# controller.py
import numpy as np
import yaml
from scipy.interpolate import interp1d

class ConfigLoader:
    """加载并解析 YAML 配置文件"""
    @staticmethod
    def load(filepath='rov_config.yaml'):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"警告: 找不到配置文件 {filepath}，将使用默认参数。")
            return None

class ROVConfig:
    """Tether Vehicle 物理与几何配置参数"""
    def __init__(self, config_dict=None):
        cfg = config_dict.get('robot', {}) if config_dict else {}
        
        # 质量与尺寸参数
        self.mass_air = cfg.get('mass_air', 50.0)
        self.mass_submerged = cfg.get('mass_submerged', 1.642)
        dims = cfg.get('dimensions', [0.660, 0.524, 0.410])
        self.length, self.width, self.height = dims
        self.CG = np.array(cfg.get('cg', [0.000, 0.000, 0.000]))
        
        # 推进器基础配置
        thruster_cfg = cfg.get('thrusters', {})
        self.max_rpm = thruster_cfg.get('max_rpm', 2000)
        self.max_rpm_acceleration = thruster_cfg.get('max_rpm_acceleration', 15000.0)
        self.thruster_deflection_angle = np.deg2rad(thruster_cfg.get('deflection_angle_deg', 30))
        self.n_thrusters = 6
        self.thruster_radius = 0.060
        
        # 动态读取推进器安装位置偏移量 (相对于 CG)
        offsets = thruster_cfg.get('offsets', {})
        self.Bbp = offsets.get('Bbp', 0.150)  
        self.Bfp = offsets.get('Bfp', 0.150)  
        self.Btp = offsets.get('Btp', 0.165)  
        self.Lbp = offsets.get('Lbp', 0.200)  
        self.Lfp = offsets.get('Lfp', 0.200)  
        self.Htp = offsets.get('Htp', 0.037)  
        self.H0  = offsets.get('H0', 0.100)
        
        # 【修改】硬件符号映射表 (Actuator Sign Map) 前桨前进需反转(-1)，后桨前进需正转(+1)，顶桨up需+转(1)
        self.rpm_sign_map = np.array([-1.0, -1.0, 1.0, 1.0, 1.0, 1.0])
        
        # 初始化计算
        self._calculate_thruster_positions()
        self._calculate_thrust_allocation_matrix()
        self._init_thruster_curves()
        

    def _calculate_thruster_positions(self):
        """计算每个 thruster 的空间位置和推力方向 (基于 NED: X=前, Y=右, Z=下)"""
        self.thruster_positions = np.zeros((6, 3))
        
        # 【核心修正】严格对齐 CFD 通道 -> 0:右前, 1:左前, 2:右后, 3:左后, 4:右顶, 5:左顶
        # NED坐标系 -> 前为+X, 后为-X | 右为+Y, 左为-Y | 下为+Z, 上为-Z
        self.thruster_positions[0] = [ self.Lfp,  self.Bfp, 0]         # 0: 右前 (Y为正)
        self.thruster_positions[1] = [ self.Lfp, -self.Bfp, 0]         # 1: 左前 (Y为负)
        self.thruster_positions[2] = [-self.Lbp,  self.Bbp, 0]         # 2: 右后 (Y为正)
        self.thruster_positions[3] = [-self.Lbp, -self.Bbp, 0]         # 3: 左后 (Y为负)
        self.thruster_positions[4] = [0,  self.Btp, -self.Htp-self.H0]         # 4: 右顶 (Y为正)
        self.thruster_positions[5] = [0, -self.Btp, -self.Htp-self.H0]         # 5: 左顶 (Y为负)
        
        # 推力方向向量 (当产生正向推力时，力量在 X, Y, Z 轴上的投影分量)
        self.thruster_directions = np.zeros((6, 3))
        angle = self.thruster_deflection_angle
        
        # 0: 右前 -> 向前(+X)，向右(+Y)
        self.thruster_directions[0] = [np.cos(angle),  np.sin(angle), 0] 
        # 1: 左前 -> 向前(+X)，向左(-Y)
        self.thruster_directions[1] = [np.cos(angle), -np.sin(angle), 0] 
        # 2: 右后 -> 向前(+X)，向左(-Y) (通常与对角线的左前平行)
        self.thruster_directions[2] = [np.cos(angle), -np.sin(angle), 0] 
        # 3: 左后 -> 向前(+X)，向右(+Y) (通常与对角线的右前平行)
        self.thruster_directions[3] = [np.cos(angle),  np.sin(angle), 0] 
        
        # 垂向推进器 (4-5) - up (-Z方向)
        self.thruster_directions[4] = [0, 0, -1]  
        self.thruster_directions[5] = [0, 0, -1]
        
    def _calculate_thrust_allocation_matrix(self):
        """生成推力分配矩阵 A_matrix (6x6)"""
        self.A_matrix = np.zeros((6, 6))
        for i in range(6):
            # 前三行: 力分量 (X, Y, Z)
            self.A_matrix[0:3, i] = self.thruster_directions[i]
            # 后三行: 力矩分量 (K, M, N) = r × F
            r = self.thruster_positions[i]
            F = self.thruster_directions[i]
            moment = np.cross(r, F)
            self.A_matrix[3:6, i] = moment
            
    def _init_thruster_curves(self):
        """初始化 KA 4-70 敞水曲线的插值模型"""
        self.rho_water = 1000  # kg/m³
        self.D_prop = 2 * self.thruster_radius
        # 进速比 J 与 推力系数 KT 的关系
        self.J_points = np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
        self.KT_points = np.array([0.38, 0.35, 0.32, 0.28, 0.24, 0.19, 0.14, 0.08, 0.02])
        self.KT_interp = interp1d(self.J_points, self.KT_points, kind='cubic', fill_value='extrapolate')
        
    def thrust_to_rpm(self, T_desired, Va, thruster_index):
        """逆螺旋桨模型：结合硬件安装方向解算最终指令转速"""
        if abs(T_desired) < 1e-6:
            return 0.0
        
        # 获取推力方向
        sign = np.sign(T_desired)
        T_abs = abs(T_desired)
        
        # 根据 J=0 时的静态推力系数做初始转速猜测
        n_rps = np.sqrt(T_abs / (self.rho_water * self.D_prop**4 * self.KT_points[0]))
        if n_rps < 0.1:
            n_rps = 5.0  
            
        # 松弛迭代法逼近真实转速
        for _ in range(5):
            J = Va / (n_rps * self.D_prop) if n_rps > 0.1 else 0
            J = np.clip(J, 0, 0.8) 
            KT = self.KT_interp(J) 
            n_rps_new = np.sqrt(T_abs / (self.rho_water * self.D_prop**4 * KT)) 
            n_rps = 0.5 * n_rps + 0.5 * n_rps_new 
            
        # 【核心修改】最终转速 = 绝对转速 * 期望推力方向 * 硬件安装映射符号
        final_rpm = n_rps * 60 * sign * self.rpm_sign_map[thruster_index]
        return final_rpm

class FuzzyTuner:
    """二维模糊规则查表器,用于动态调整 PID"""
    def __init__(self, e_max, ec_max, kp_max, ki_max, kd_max):
        # 论域极值 (用于将实际物理量映射到 [-3, 3] 的模糊论域)
        self.Ke = 3.0 / e_max    # 误差量化因子
        self.Kec = 3.0 / ec_max  # 误差变化率量化因子
        # 输出比例因子 (将模糊输出 [-3, 3] 映射回真实的增量物理范围)
        self.Ku_p = kp_max / 3.0
        self.Ku_i = ki_max / 3.0
        self.Ku_d = kd_max / 3.0
        # 定义经典 7x7 模糊规则表 (NB=-3, NM=-2, NS=-1, ZO=0, PS=1, PM=2, PB=3)
        # 行: 误差 e (-3 到 3) | 列: 误差变化率 ec (-3 到 3)
        self.rule_kp = np.array([
            [ 3,  3,  2,  2,  1,  0,  0],
            [ 3,  3,  2,  1,  1,  0, -1],
            [ 2,  2,  2,  1,  0, -1, -1],
            [ 2,  2,  1,  0, -1, -2, -2],
            [ 1,  1,  0, -1, -1, -2, -2],
            [ 1,  0, -1, -2, -2, -2, -3],
            [ 0,  0, -2, -2, -2, -3, -3]
        ])
        
        self.rule_ki = np.array([
            [-3, -3, -2, -2, -1,  0,  0],
            [-3, -3, -2, -1, -1,  0,  0],
            [-3, -2, -1, -1,  0,  1,  1],
            [-2, -2, -1,  0,  1,  2,  2],
            [-2, -1,  0,  1,  1,  2,  3],
            [ 0,  0,  1,  1,  2,  3,  3],
            [ 0,  0,  1,  2,  2,  3,  3]
        ])
        
        self.rule_kd = np.array([
            [ 1, -1, -3, -3, -3, -2,  1],
            [ 1, -1, -3, -2, -2, -1,  0],
            [ 0, -1, -2, -2, -1, -1,  0],
            [ 0, -1, -1, -1, -1, -1,  0],
            [ 0,  0,  0,  0,  0,  0,  0],
            [ 3, -1,  1,  1,  1,  1,  3],
            [ 3,  2,  2,  2,  1,  1,  3]
        ])

    def compute_delta(self, error, error_rate):
        """输入真实误差和变化率，返回 ΔKp, ΔKi, ΔKd"""
        # 1. 模糊化映射：物理论域映射到 [-3, 3]
        e_fuzz = np.clip(error * self.Ke, -3, 3)
        ec_fuzz = np.clip(error_rate * self.Kec, -3, 3)
        # 2. 简化的双线性插值查表 (比纯粹的重心法解模糊快 10 倍以上)
        e_idx = e_fuzz + 3  # 映射到 0~6 的索引
        ec_idx = ec_fuzz + 3
        # 找到相邻的四个点进行二维插值 (这里为保证极速，可用最近邻，或直接四舍五入)
        # 为保持极高频响应，这里采用四舍五入的快速查表法
        row = int(np.round(e_idx))
        col = int(np.round(ec_idx))
        # 3. 提取规则并解模糊映射回真实增量
        delta_kp = self.rule_kp[row, col] * self.Ku_p
        delta_ki = self.rule_ki[row, col] * self.Ku_i
        delta_kd = self.rule_kd[row, col] * self.Ku_d
        return delta_kp, delta_ki, delta_kd

class ROVPIDController:
    """6自由度位姿 PID 控制器"""
    def __init__(self, rov_config, config_dict=None):
        self.config = rov_config
        
        pid_cfg = config_dict.get('pid', {}) if config_dict else {}
        pos_cfg = pid_cfg.get('position', {})
        att_cfg = pid_cfg.get('attitude', {})
        limits_cfg = pid_cfg.get('limits', {})
        fuzzy_z_cfg = pid_cfg.get('fuzzy_z', {})
        fuzzy_pitch_cfg = pid_cfg.get('fuzzy_pitch', {})
        
        # 提取增益参数
        self.Kp_pos = np.array(pos_cfg.get('kp', [35.0, 35.0, 50.0]))
        self.Ki_pos = np.array(pos_cfg.get('ki', [5.0, 5.0, 5.0]))
        self.Kd_pos = np.array(pos_cfg.get('kd', [15.0, 15.0, 20.0]))
        self.Kp_att = np.array(att_cfg.get('kp', [10.0, 10.0, 20.0]))
        self.Ki_att = np.array(att_cfg.get('ki', [2.0, 2.0, 0.0]))
        self.Kd_att = np.array(att_cfg.get('kd', [15.0, 15.0, 20.0]))
        
        # 动态读取模糊 PID 配置
        self.fuzzy_z = FuzzyTuner(
            e_max=fuzzy_z_cfg.get('e_max', 0.5),
            ec_max=fuzzy_z_cfg.get('ec_max', 0.25),
            kp_max=fuzzy_z_cfg.get('kp_max', 15.0),
            ki_max=fuzzy_z_cfg.get('ki_max', 5.0),
            kd_max=fuzzy_z_cfg.get('kd_max', 2.0)
        )
        
        #self.fuzzy_pitch = FuzzyTuner(
        #    e_max=fuzzy_pitch_cfg.get('e_max', 0.174),
        #    ec_max=fuzzy_pitch_cfg.get('ec_max', 0.100),
        #    kp_max=fuzzy_pitch_cfg.get('kp_max', 5.0),
        #    ki_max=fuzzy_pitch_cfg.get('ki_max', 0.5),
        #    kd_max=fuzzy_pitch_cfg.get('kd_max', 1.0)
        #)
        
        fuzzy_x_cfg = pid_cfg.get('fuzzy_x', {})
        self.fuzzy_x = FuzzyTuner(
            e_max=fuzzy_x_cfg.get('e_max', 0.3),
            ec_max=fuzzy_x_cfg.get('ec_max', 0.2),
            kp_max=fuzzy_x_cfg.get('kp_max', 20.0),
            ki_max=fuzzy_x_cfg.get('ki_max', 5.0),
            kd_max=fuzzy_x_cfg.get('kd_max', 10.0)
        )
        
        # 积分限幅器
        pos_int = pos_cfg.get('max_integral', [100.0, 100.0, 200.0])
        att_int = att_cfg.get('max_integral', [50.0, 50.0, 100.0])
        self.max_integral = np.array(pos_int + att_int)
        
        # 广义力输出限制
        self.max_force = limits_cfg.get('max_force', 200.0)
        self.max_moment = limits_cfg.get('max_moment', 50.0)
        self.static_comp_z = limits_cfg.get('static_compensation_z', -5.1)
        
        self.integral_pos = np.zeros(3)
        self.integral_att = np.zeros(3)
        self.last_error_pos = None
        self.last_time = None
        
    def compute_control(self, current_state, desired_state):
        """计算期望广义力 tau = [X, Y, Z, K, M, N]"""
        current_time = current_state['timestamp']
        
        current_pos = np.array([current_state['x'], current_state['y'], current_state['z']])
        current_att = np.array([current_state['roll'], current_state['pitch'], current_state['yaw']])
        current_vel = np.array([current_state['u'], current_state['v'], current_state['w']])
        current_omega = np.array([current_state['p'], current_state['q'], current_state['r']])
        
        desired_pos = np.array([desired_state['x'], desired_state['y'], desired_state['z']])
        desired_att = np.array([desired_state['roll'], desired_state['pitch'], desired_state['yaw']])
        
        # 位置与姿态误差计算
        error_pos = desired_pos - current_pos
        error_att = self._normalize_angle(desired_att - current_att)
        
        # 采用微分先行(速度反馈)策略避免阶跃冲击
        if self.last_error_pos is not None and self.last_time is not None:
            dt = current_time - self.last_time
            if dt > 0:
                deriv_pos = -current_vel  
                deriv_att = -current_omega
            else:
                deriv_pos = np.zeros(3)
                deriv_att = np.zeros(3)
        else:
            deriv_pos = np.zeros(3)
            deriv_att = np.zeros(3)
            
        # 积分累加与抗饱和 (Anti-windup)
        if self.last_time is not None:
            dt = current_time - self.last_time
            if dt > 0:
                self.integral_pos += error_pos * dt
                self.integral_att += error_att * dt
                self.integral_pos = np.clip(self.integral_pos, -self.max_integral[:3], self.max_integral[:3])
                self.integral_att = np.clip(self.integral_att, -self.max_integral[3:], self.max_integral[3:])
        
        # 模糊 PID 动态调参应用
        # 1. 提取 Z 轴(深度)的模糊增量
        dkp_z, dki_z, dkd_z = self.fuzzy_z.compute_delta(error_pos[2], deriv_pos[2])
        #dkp_p, dki_p, dkd_p = self.fuzzy_pitch.compute_delta(error_att[1], deriv_att[1])
        dkp_x, dki_x, dkd_x = self.fuzzy_x.compute_delta(error_pos[0], deriv_pos[0])
        current_Kp_pos = self.Kp_pos.copy()
        current_Ki_pos = self.Ki_pos.copy()
        current_Kd_pos = self.Kd_pos.copy()
        current_Kp_att = self.Kp_att.copy()
        current_Ki_att = self.Ki_att.copy()
        current_Kd_att = self.Kd_att.copy()
        
        current_Kp_pos[2] += dkp_z
        current_Ki_pos[2] += dki_z
        current_Kd_pos[2] += dkd_z
        #current_Kp_att[2] += dkp_p
        #current_Ki_att[2] += dki_p
        #current_Kd_att[2] += dkd_p
        current_Kp_pos[0] += dkp_x
        current_Ki_pos[0] += dki_x
        current_Kd_pos[0] += dkd_x
        
        force = (current_Kp_pos * error_pos + current_Ki_pos * self.integral_pos + current_Kd_pos * deriv_pos)
        moment = (current_Kp_att * error_att + current_Ki_att * self.integral_att + current_Kd_att * deriv_att)
        #垂向静态补偿
        force[2] += self.static_comp_z

        # 输出限幅
        force = np.clip(force, -self.max_force, self.max_force)
        moment = np.clip(moment, -self.max_moment, self.max_moment)
        tau = np.concatenate([force, moment])
        
        self.last_error_pos = error_pos
        self.last_time = current_time
        
        # 收集当前真正使用的 PID 参数 (包含模糊增量)
        pid_status = {
            'kp_pos': current_Kp_pos,
            'ki_pos': current_Ki_pos,
            'kd_pos': current_Kd_pos
        }
        
        return tau, pid_status
    
    def _normalize_angle(self, angle):
        """将角度规范到 [-pi, pi] 范围内"""
        return (angle + np.pi) % (2 * np.pi) - np.pi

class ThrustAllocator:
    """推力分配器"""
    def __init__(self, rov_config):
        self.config = rov_config
        self.A_matrix = rov_config.A_matrix
        # 计算广义逆矩阵 (Moore-Penrose pseudo-inverse)
        self.A_pinv = np.linalg.pinv(self.A_matrix)
        # 单个推进器物理推力极值
        self.max_thrust_per_prop = 50.0  
        self.min_thrust_per_prop = -30.0  
        
    def allocate(self, tau):
        """通过伪逆法将六自由度广义力分配至六个推进器"""
        thrusts = self.A_pinv @ tau
        thrusts = np.clip(thrusts, self.min_thrust_per_prop, self.max_thrust_per_prop)
        return thrusts


class MotorController:
    """电机动态响应控制器 (线性恒定速率爬坡版)"""
    def __init__(self, rov_config):
        self.config = rov_config
        # 设定的转速最大变化率: 15000 rpm/s (即 0.1秒内提速 1500 rpm)
        self.max_rpm_acceleration = self.config.max_rpm_acceleration 
        self.last_rpm = np.zeros(6)
        self.last_time = None
        
    def thrust_to_rpm(self, thrusts, Va_array):
        """包装调用配置中的推力转 RPM 功能"""
        rpm = np.zeros(6)
        for i in range(6):
            # 【修改】将当前的索引 i 传给配置类，以便提取对应的符号映射
            rpm[i] = self.config.thrust_to_rpm(thrusts[i], Va_array[i], thruster_index=i)
        
        rpm = np.clip(rpm, -self.config.max_rpm, self.config.max_rpm)
        return rpm
    
    def apply_motor_dynamics(self, desired_rpm, current_sim_time):
        """引入线性速率限制器 (Rate Limiter) 以模拟恒定爬坡"""
        if self.last_time is None:
            self.last_time = current_sim_time
            self.last_rpm = desired_rpm
            return desired_rpm
        
        dt = current_sim_time - self.last_time
        if dt <= 0: return self.last_rpm

        # 1. 计算当前时间步长 (dt) 内允许的最大转速变化量绝对值
        max_delta = self.max_rpm_acceleration * dt
        
        # 2. 计算期望转速与当前真实转速的差值
        diff = desired_rpm - self.last_rpm
        
        # 3. 将差值强制截断在允许的最大变化量范围内
        # 如果差值很大，本步只增加 max_delta；如果差值很小，就直接补齐差值达到目标
        actual_delta = np.clip(diff, -max_delta, max_delta)
        
        # 4. 获得真实的瞬间转速
        actual_rpm = self.last_rpm + actual_delta
        
        self.last_rpm = actual_rpm
        self.last_time = current_sim_time
        return actual_rpm


class ROVControlSystem:
    def __init__(self, cosim_interface, config_file='rov_config.yaml'):
        # 依赖注入：挂载外部提供的内存/通信接口
        self.cosim = cosim_interface
        
        # 初始化控制组件
        self.raw_config = ConfigLoader.load(config_file)
        self.config = ROVConfig(self.raw_config)
        self.pid = ROVPIDController(self.config, self.raw_config)
        self.allocator = ThrustAllocator(self.config)
        self.motor = MotorController(self.config)
        
        # 【安全兜底】控制器的默认目标状态 (原地悬停)
        # 实际任务目标应由上层业务逻辑 (如 main.py) 通过 set_desired_position() 动态覆写
        self.desired_state = {
            'x': 0.0, 'y': 0.0, 'z': 0.0,
            'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0
        }
        
        # --- 多速率架构配置 ---
        sys_cfg = self.raw_config.get('system', {}) if self.raw_config else {}
        self.control_rate = sys_cfg.get('control_rate', 50.0) # 真实物理控制器的运算频率 (50Hz)
        self.control_dt = 1.0 / self.control_rate # 0.02秒算一次 PID
        
        # 初始化为负数，保证在仿真启动瞬间(t=0)必须执行首次 PID 计算
        self.last_control_time = -self.control_dt 
        
        # 内部缓存信号，供高频电机环使用
        self.current_target_rpm = np.zeros(6) 
        self.current_tau = np.zeros(6)
        
        # 内部缓存当前的 PID 参数状态
        self.current_pid_status = {
            'kp_pos': np.zeros(3),
            'ki_pos': np.zeros(3),
            'kd_pos': np.zeros(3)
        }

    def set_desired_position(self, x, y, z):
        self.desired_state['x'] = x
        self.desired_state['y'] = y
        self.desired_state['z'] = z
        
    def set_desired_attitude(self, roll, pitch, yaw):
        self.desired_state['roll'] = roll
        self.desired_state['pitch'] = pitch
        self.desired_state['yaw'] = yaw

    def step(self):
        """
        执行联合仿真的核心单步步进逻辑。
        由外界的主循环(main.py)无脑高频调用即可。
        """
        # 1. 阻塞等待：直到获取到最新的高频物理流场状态
        raw_state = self.cosim.wait_for_cfd_data()
        # current_state = self.cosim.wait_for_cfd_data()

        # 杆臂效应修正：将局部坐标系原点速度平移至真实的重心 (CG)
        v_Ob = np.array([raw_state['u'], raw_state['v'], raw_state['w']])
        omega = np.array([raw_state['p'], raw_state['q'], raw_state['r']])
        
        # 从随体坐标系原点 (Ob) 指向重心 (CG) 的向量
        r_Ob_to_CG = np.array([0.00, 0.00, 0.00])
        
        # 刚体运动学速度平移公式: V_cg = V_ob + omega × r
        v_CG = v_Ob + np.cross(omega, r_Ob_to_CG)
        
        current_state = {}
        current_state['timestamp'] = raw_state['timestamp']
        
        # 位置与线速度透传映射 (坐标对应)
        current_state['x'] = raw_state['x']
        current_state['y'] = raw_state['y']
        current_state['z'] = raw_state['z']
        
        current_state['u'] = v_CG[0]
        current_state['v'] = v_CG[1]
        current_state['w'] = v_CG[2]
        
        # 姿态与角速度透传映射 (坐标对应)
        current_state['roll']  = raw_state['roll']
        current_state['pitch'] = raw_state['pitch']
        current_state['yaw']   = raw_state['yaw']
        
        current_state['p'] = raw_state['p']
        current_state['q'] = raw_state['q']
        current_state['r'] = raw_state['r']
        
        current_sim_time = current_state['timestamp']
        
        # 离散低频环 (50Hz): 真实控制算法域
        if current_sim_time - self.last_control_time >= (self.control_dt - 1e-6):
            # A. 运算 PID 误差，获得期望广义力
            self.current_tau, self.current_pid_status = self.pid.compute_control(current_state, self.desired_state)
            # B. 推力分配至 6 个执行器
            thrusts = self.allocator.allocate(self.current_tau)
            # C. 结合局部进速计算，解算期望转速
            Va_array = self._compute_advance_velocities(current_state)
            self.current_target_rpm = self.motor.thrust_to_rpm(thrusts, Va_array)
            
            self.last_control_time = current_sim_time
        # 连续高频环 (与 CFD 同频, 如1000Hz): 物理延迟域
        # 无论当前是否执行了 PID，电机都在随着时间常数拼命向 target_rpm 逼近
        actual_rpm = self.motor.apply_motor_dynamics(self.current_target_rpm, current_sim_time)
        
        # 3. 将真实产生的瞬态转速送回共享内存，触发 CFD 步进
        self.cosim.send_motor_commands(actual_rpm)
        
        # 4. 向上层返回核心数据用于日志和终端打印
        return current_sim_time, current_state, self.current_tau, self.current_target_rpm, actual_rpm, self.current_pid_status

    def _compute_advance_velocities(self, state):
        """计算各推进器盘面处的局部进速（Advance Velocity）"""
        u, v, w = state['u'], state['v'], state['w']
        p, q, r = state['p'], state['q'], state['r']
        Va_array = np.zeros(6)
        
        for i in range(6):
            # 提取安装位置和偏转方向
            pos = self.config.thruster_positions[i]
            direction = self.config.thruster_directions[i]
            
            # 计算因本体旋转而引起的盘面线速度增量 v = ω × r
            rot_vel = np.cross([p, q, r], pos)
            
            # 盘面处相对于周围水流的绝对总合速度
            total_vel = np.array([u, v, w]) + rot_vel
            
            # 将总合速度投影到推进器的主推力轴线上，得到有效进速
            Va_array[i] = np.dot(total_vel, direction)
            
        return Va_array
