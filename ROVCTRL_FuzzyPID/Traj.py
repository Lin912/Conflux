
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
import os

class TrajectoryPlanner:
    """基于离线 CSV 轨迹数据的高频轨迹生成器"""
    
    def __init__(self, csv_filepath, profile_type='Poly5', relative_offsets=None):
        """
        :param csv_filepath: 工作船位移数据文件路径 (例如: './Ship_Starting_Profiles/displacement_profiles.csv')
        :param profile_type: 选择跟随的曲线类型 ('Linear', 'Sine', 'Exp', 'Poly5')
        :param relative_offsets: ROV 相对于工作船的固定偏移量字典，例如 {'y': 0.0, 'z': 2.0} 表示在船下方2米
        """
        if not os.path.exists(csv_filepath):
            raise FileNotFoundError(f"找不到轨迹文件: {csv_filepath}。请先运行 ShipFORWARDCreator.py。")
            
        # 1. 加载工作船数据
        df = pd.read_csv(csv_filepath)
        time_data = df['Time_s'].values
        
        # 构建对应的列名
        target_col = f'Displacement_{profile_type}_m'
        if target_col not in df.columns:
            raise ValueError(f"CSV 文件中没有找到列: {target_col}")
            
        disp_data = df[target_col].values
        
        # 2. 构建 1D 插值器 (即使控制环频率与 CSV 采样率不一致，也能平滑过渡)
        # bounds_error=False 和 fill_value 确保超出仿真时间后，ROV 会停在最后的位置
        self.x_interp = interp1d(
            time_data, disp_data, 
            kind='cubic', # 使用三次样条插值保证速度和加速度的连续性
            bounds_error=False, 
            fill_value=(disp_data[0], disp_data[-1])
        )
        
        # 3. 设置固定的相对偏移量和姿态
        self.offsets = relative_offsets if relative_offsets else {}
        self.y_offset = self.offsets.get('y', 0.0)
        self.z_offset = self.offsets.get('z', 0.0)  # 比如设为正数代表在水下一定深度
        self.roll = self.offsets.get('roll', 0.0)
        self.pitch = self.offsets.get('pitch', 0.0)
        self.yaw = self.offsets.get('yaw', 0.0)

    def get_desired_state(self, current_time):
        """高频调用接口：根据当前时间返回目标位姿"""
        # 计算当前时刻工作船的 X 轴位移
        target_x = float(self.x_interp(current_time))
        
        return {
            'x': target_x,
            'y': self.y_offset,
            'z': self.z_offset,
            'roll': self.roll,
            'pitch': self.pitch,
            'yaw': self.yaw
        }