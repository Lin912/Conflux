# main.py
import time
import numpy as np
import csv
import datetime  # 用于生成带有时间戳的文件名

# 从我们拆分好的文件中导入类
from SofinLoop import CoSimInterface
from controller import ROVControlSystem
from Traj import TrajectoryPlanner

def main():
    print("StarCCM+ -> coupling -> ROVCTRL (BASED_ON Linux MMF)")
    
    # 1. 实例化内存接口 
    cosim_interface = CoSimInterface(
        use_dummy=False,
        filename="../HydroSimulation/ControlDirect_SharedMemory")
    
    # 2. 实例化控制器，并注入内存接口***************************************>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
    cs = ROVControlSystem(cosim_interface=cosim_interface)
    
    # ---------------- 轨迹规划初始化 (工作船伴随模式) ----------------
    csv_path = './Ship_Starting_Profiles/displacement_profiles.csv'
    rov_offsets = {
        'y': 0.0, 
        'z': 0.0,
        'roll': 0.0, 'pitch': 0.0, 'yaw': 0.0
    }
    
    planner = TrajectoryPlanner(
        csv_filepath=csv_path, 
        profile_type='Poly5', 
        relative_offsets=rov_offsets
    )
    # ------------------------------------------------

    print("\n Wating for StarCCM+ simulating...")
    
    last_display_time = -1.0    # 初始刷新时间
    display_interval = 0.01     # 数据记录与屏幕刷新间隔 (0.01s = 100Hz 记录频率)

    # 缓存函数属性，提升高频循环性能
    set_pos = cs.set_desired_position
    set_att = cs.set_desired_attitude
    get_target = planner.get_desired_state
    # 自动生成带时间戳的日志文件名，防止覆盖旧数据
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"rov_control_log_{timestamp_str}.csv"
    
    # 定义 CSV 表头 (将原本复合的字符串拆解为独立的纯数字列，方便后续绘图)
    headers = [
        "Time_s", 
        "Pos_X", "Pos_Y", "Pos_Z", 
        "Target_X", "Target_Y", "Target_Z", 
        "Roll_deg", "Pitch_deg", "Yaw_deg",
        "Force_X", "Force_Y", "Force_Z", 
        "Moment_K", "Moment_M", "Moment_N",
        "TgtRPM_0", "TgtRPM_1", "TgtRPM_2", "TgtRPM_3", "TgtRPM_4", "TgtRPM_5",
        "RealRPM_0", "RealRPM_1", "RealRPM_2", "RealRPM_3", "RealRPM_4", "RealRPM_5",
        "Kp_Z", "Ki_Z", "Kd_Z"
        "Kp_X", "Ki_X", "Kd_X",            
        "Kp_Pitch", "Ki_Pitch", "Kd_Pitch"
    ]

    print(f"\n[INFO] 控制数据将实时写入: {log_filename}")

    # ================= 打印控制台表头 =================
    print("=" * 210)
    print(f"{'Time(s)':^8} | {'Position (X,Y,Z)':^20} | {'Attitude (R,P,Y)°':^20} | {'Force (Fx,Fy,Fz)':^22} | {'Moment (Mx,My,Mz)':^22} | {'Target RPM (T0~T5)':^32} | {'Real RPM (T0~T5)':^32} | {'PID_Z (P, I, D)':^22} | {'PID_X (P, I, D)':^22} | {'PID_Pitch (P, I, D)':^22}")
    print("=" * 210)

    try:
        # 使用 context manager (with) 打开文件，确保异常退出时文件也能安全保存
        with open(log_filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers) # 写入表头

            while True:
                # 单步执行联合仿真
                sim_time, current_state, tau, target_rpm, actual_rpm, pid_status = cs.step()

                # 获取期望目标并送入控制器
                dtgt = get_target(sim_time)
                set_pos(dtgt['x'], dtgt['y'], dtgt['z'])
                set_att(dtgt['roll'], dtgt['pitch'], dtgt['yaw'])
                
                # 按照指定的间隔记录数据
                if sim_time - last_display_time >= (display_interval - 1e-6):
                    
                    r_deg = np.degrees(current_state['roll'])
                    p_deg = np.degrees(current_state['pitch'])
                    y_deg = np.degrees(current_state['yaw'])
                    
                    kp_z = pid_status['kp_pos'][2]
                    ki_z = pid_status['ki_pos'][2]
                    kd_z = pid_status['kd_pos'][2]
                    
                    kp_x = pid_status['kp_pos'][0]
                    ki_x = pid_status['ki_pos'][0]
                    kd_x = pid_status['kd_pos'][0]
                    
                    
                    kp_p = pid_status['kp_att'][1]
                    ki_p = pid_status['ki_att'][1]
                    kd_p = pid_status['kd_att'][1]
                    
                    # 组装当前行的数据列表 (保留合适的小数位数以缩减文件体积)
                    row_data = [
                        round(sim_time, 4),
                        round(current_state['x'], 4), round(current_state['y'], 4), round(current_state['z'], 4),
                        round(dtgt['x'], 4), round(dtgt['y'], 4), round(dtgt['z'], 4),
                        round(r_deg, 3), round(p_deg, 3), round(y_deg, 3),
                        round(tau[0], 2), round(tau[1], 2), round(tau[2], 2),
                        round(tau[3], 2), round(tau[4], 2), round(tau[5], 2),
                        round(target_rpm[0], 1), round(target_rpm[1], 1), round(target_rpm[2], 1), round(target_rpm[3], 1), round(target_rpm[4], 1), round(target_rpm[5], 1),
                        round(actual_rpm[0], 1), round(actual_rpm[1], 1), round(actual_rpm[2], 1), round(actual_rpm[3], 1), round(actual_rpm[4], 1), round(actual_rpm[5], 1),
                        round(kp_z, 3), round(ki_z, 3), round(kd_z, 3),
                        round(kp_x, 3), round(ki_x, 3), round(kd_x, 3),
                        round(kp_p, 3), round(ki_p, 3), round(kd_p, 3)
                    ]
                    
                    writer.writerow(row_data)
                    f.flush() 

                    # ---- 打印到控制台 (恢复你原本的滚屏格式) ----
                    pos_str = f"({current_state['x']:>5.2f}, {current_state['y']:>5.2f}, {current_state['z']:>5.2f})"
                    att_str = f"({r_deg:>5.1f}, {p_deg:>5.1f}, {y_deg:>5.1f})"
                    force_str = f"({tau[0]:>5.1f}, {tau[1]:>5.1f}, {tau[2]:>5.1f})"
                    moment_str = f"({tau[3]:>5.1f}, {tau[4]:>5.1f}, {tau[5]:>5.1f})"
                    target_str = f"[{target_rpm[0]:>5.0f} {target_rpm[1]:>5.0f} {target_rpm[2]:>5.0f} {target_rpm[3]:>5.0f} {target_rpm[4]:>5.0f} {target_rpm[5]:>5.0f}]"
                    actual_str = f"[{actual_rpm[0]:>5.0f} {actual_rpm[1]:>5.0f} {actual_rpm[2]:>5.0f} {actual_rpm[3]:>5.0f} {actual_rpm[4]:>5.0f} {actual_rpm[5]:>5.0f}]"
                    
                    pid_z_str = f"({kp_z:>4.1f},{ki_z:>4.1f},{kd_z:>4.1f})" 
                    pid_x_str = f"({kp_x:>4.1f},{ki_x:>4.1f},{kd_x:>4.1f})"
                    pid_p_str = f"({kp_p:>4.1f},{ki_p:>4.1f},{kd_p:>4.1f})"
                    
                    print(f" {sim_time:>7.3f}s | {pos_str:^20} | {att_str:^20} | {force_str:^22} | {moment_str:^22} | {target_str:^32} | {actual_str:^32} | {pid_z_str:^22} | {pid_x_str:^22} | {pid_p_str:^22}")
                    last_display_time = sim_time
                
    except KeyboardInterrupt:
        print("\n\n Stoping...")
        
    finally:
        # 确保安全关闭内存映射文件，释放 Linux 系统资源
        cosim_interface.close()
        print("Memory mapping released, program exits safely.")

if __name__ == "__main__":
    main()
