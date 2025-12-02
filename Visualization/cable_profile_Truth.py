import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 设置可用字体
plt.rcParams['font.family'] = ['DejaVu Serif']

# 数据导入
print("Loading Data...")
data = np.loadtxt('output/Data/newoutput1.csv', delimiter=',')
rows, cols = data.shape
print(f"Data Shape: {data.shape}")

# 检查列数是否为10的倍数
if cols % 10 == 0:
    Tck = np.zeros((rows, (cols // 10) * 3))
    indices = np.arange(0, cols, 10)
    for i, idx in enumerate(indices):
        Tck[:, 3 * i: 3 * i + 3] = data[:, idx:idx + 3]
else:
    Tck = data.copy()

print(f"Processed data shape of Tck: {Tck.shape}")

# 新数据矩阵初始化
data_new = np.zeros((20000, Tck.shape[1]))

# 完全向量化的积分计算
def compute_integrals_vectorized(data):
    h = 0.002
    n_rows, n_cols = data.shape
    
    # Simpson积分 (从第3个点开始)
    simpson_result = np.zeros((n_rows, n_cols))
    for col in range(n_cols):
        # 使用cumsum进行向量化Simpson积分
        weights = np.ones(n_rows)
        weights[1:-1:2] = 4  # 奇数点权重4
        weights[2:-2:2] = 2  # 偶数点权重2
        weights[0] = 1/3
        weights[-1] = 1/3
        
        simpson_result[:, col] = np.cumsum(data[:, col] * weights) * (h / 3)
    
    # 梯形积分 (第2个点)
    trapezoidal_result = np.zeros((n_rows, n_cols))
    for col in range(n_cols):
        weights = np.ones(n_rows)
        weights[0] = 0.5
        weights[-1] = 0.5
        trapezoidal_result[:, col] = np.cumsum(data[:, col] * weights) * h
    
    return simpson_result, trapezoidal_result

print("Interagting...")
simpson_result, trapezoidal_result = compute_integrals_vectorized(Tck)

# 填充data_new
data_new[2:, :] = simpson_result[2:, :]  # Simpson积分从第3点开始
data_new[1, :] = trapezoidal_result[1, :]  # 第2点用梯形积分
data_new[0, :] = 0  # 第1点为0

print("Intergate done!!")

# 修改 data_new 的第二列值 - 修复索引问题
n_points = data_new.shape[1] // 3  # 实际点数
K = np.arange(0, -0.2 * n_points, -0.2)[:n_points]  # 根据实际点数生成K，纵向节点间距为0.2m

for j in range(n_points):
    if 3 * j + 2 < data_new.shape[1]:
        data_new[:, 3 * j + 0] += K[j]

# 定义点的集合 - 修复索引边界问题
time_indices = np.arange(0, min(20000, data_new.shape[0]), 100)  ##################################### 确保不超出时间范围(时间范围值)
point_indices = np.arange(n_points)  # 使用实际点数

# 预分配数组
Xr, Yr, Zr = [], [], []

print(f"Processing {len(time_indices)} time points...")

for time_idx in time_indices:
    if time_idx < data_new.shape[0]:
        # 确保索引不超出边界
        valid_points = []
        x_vals, y_vals, z_vals = [], [], []
        
        for j in point_indices:
            x_idx = 3 * j + 0
            y_idx = 3 * j + 1
            z_idx = 3 * j + 2
            
            # 检查所有索引是否有效
            if (x_idx < data_new.shape[1] and 
                y_idx < data_new.shape[1] and 
                z_idx < data_new.shape[1]):
                x_vals.append(data_new[time_idx, x_idx])
                y_vals.append(data_new[time_idx, y_idx])
                z_vals.append(data_new[time_idx, z_idx])
                valid_points.append(j)
        
        if len(x_vals) > 1:  # 至少需要2个点才能画线
            Xr.append(np.array(x_vals))
            Yr.append(np.array(y_vals))
            Zr.append(np.array(z_vals))

print(f"Successfully processed {len(Xr)} valid time series")


# def rot_y_neg90(x, y, z):
    # 绕 y 轴旋转 -90°：X'=-Z, Y'=Y, Z'=X
#   return -z, y, x

# 批量旋转所有时间曲线
# Xr2, Yr2, Zr2 = [], [], []
# for x, y, z in zip(Xr, Yr, Zr):
#     xr, yr, zr = rot_y_neg90(x, y, z)
#     Xr2.append(xr); Yr2.append(yr); Zr2.append(zr)


# 定义中心点数据 - 修复索引
valid_center_points = min(20000, data_new.shape[0]) #####################################################(红线的时间范围值)
if data_new.shape[1] >= 4:  # 确保有足够的列
    Xc = data_new[:valid_center_points, 0]
    Yc = data_new[:valid_center_points, 1] 
    Zc = data_new[:valid_center_points, 2]
else:
    Xc, Yc, Zc = np.array([]), np.array([]), np.array([])
    print("Warning: Not enough columns for center point data")

# 旋转中心轨迹
# Xc2, Yc2, Zc2 = rot_y_neg90(Xc, Yc, Zc)


# 绘制3D图
if len(Xr) > 0:
    print("Generating 3D plot...")
    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection='3d')

    # 绘制各时间点的曲线
    colors = plt.cm.viridis(np.linspace(0, 1, len(Xr)))
    for i, (x, y, z, color) in enumerate(zip(Xr, Yr, Zr, colors)):
        if len(x) > 1:  # 确保有足够的数据点
            # 只为开始、中间、结束的时间点添加标签
            if i == 0 or i == len(Xr)//2 or i == len(Xr)-1:
                label = f't={time_indices[i]*0.002:.1f}s'
            else:
                label = None
            ax.plot(x, y, z, color=color, alpha=0.8, linewidth=1.2, label=label)

    # 绘制中心点轨迹
    if len(Xc) > 1:
        ax.plot(Xc, Yc, Zc, linestyle="--", color="#B3112F", linewidth=2.5, label='Center Point Trajectory')

        ax.set_xlim(-25.00, 5.00)     # X 轴范围
        ax.set_ylim(-15.00, 15.00)   # Y 轴范围
        ax.set_zlim(-15.00, 15.00)     # Z 轴范围
        
        ax.set_xticks(np.arange(-25.0, 7.00, 2.00))
        ax.set_yticks(np.arange(-15.00, 17.00,  2.00))
        ax.set_zticks(np.arange(-15.00, 17.00,  2.00))
       
        # 如需自定义刻度标签格式，手动给字符串
        ax.set_xticklabels([f"{v:.1f}" for v in ax.get_xticks()])
        ax.set_yticklabels([f"{v:.2f}" for v in ax.get_yticks()])
        ax.set_zticklabels([f"{v:.2f}" for v in ax.get_zticks()])
        
        
        #spacing = 0.2
        #L = (n_points - 1) * spacing
        #ax.set_xlim(-L - 0.2, 0.2)   # 例：给定固定边界
        #ax.set_xticks(np.arange(-L, 0.001, spacing))  # 每 0.2m 一个刻度
       
        
        # 改进的刻度标签格式化
        def format_tick_labels(ticks):
            """根据数值范围智能格式化刻度标签"""
            if len(ticks) == 0:
                return []
            
            # 确定数值范围
            tick_range = np.max(ticks) - np.min(ticks)
            
            # 根据范围选择格式
            if tick_range < 0.01:
                return [f'{tick:.4f}' for tick in ticks]
            elif tick_range < 0.1:
                return [f'{tick:.3f}' for tick in ticks]
            elif tick_range < 1:
                return [f'{tick:.2f}' for tick in ticks]
            elif tick_range < 10:
                return [f'{tick:.1f}' for tick in ticks]
            else:
                return [f'{tick:.0f}' for tick in ticks]
        
    # 设置坐标轴标签
    ax.set_xlabel('X Coordinate (m)', fontsize=14, fontweight='bold', labelpad=15)
    ax.set_ylabel('Y Coordinate (m)', fontsize=14, fontweight='bold', labelpad=15)
    ax.set_zlabel('Z Coordinate (m)', fontsize=14, fontweight='bold', labelpad=15)

    # 修改刻度样式
    ax.tick_params(axis='x', which='major', labelsize=12, pad=8)
    ax.tick_params(axis='y', which='major', labelsize=12, pad=8)
    ax.tick_params(axis='z', which='major', labelsize=12, pad=8)

    # 增强网格可见性
    ax.xaxis.pane.set_alpha(0.1)
    ax.yaxis.pane.set_alpha(0.1)
    ax.zaxis.pane.set_alpha(0.1)
    ax.grid(True, alpha=0.4, linestyle='-', linewidth=0.5)
    
    # 设置视角
    ax.view_init(elev=30, azim=45)
    #ax.view_init(elev=22, azim=128)   # 俯仰≈22°，方位≈128°
    ax.set_box_aspect((1, 1, 0.35))
    # 如果仍感觉左右相反，可再反转 Z 轴方向（视具体数据决定是否需要）：
    # ax.invert_xaxis()
    # ax.invert_yaxis()
    # ax.invert_zaxis()
    
    # 添加颜色条
    sm = plt.cm.ScalarMappable(cmap='viridis', 
                              norm=plt.Normalize(0, time_indices[-1]*0.002))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, shrink=0.7, pad=0.1)
    cbar.set_label('Time (s)', rotation=270, labelpad=20, fontsize=13)
    cbar.ax.tick_params(labelsize=11)
    
    # 添加图例
    legend = ax.legend(
        loc='upper left',
        bbox_to_anchor=(0, 1),
        fontsize=11,
        ncol=1,
        fancybox=True,
        shadow=True,
        framealpha=0.9,
        title='Time Points',
        title_fontsize=12
    )
    legend.get_title().set_fontweight('bold')

    plt.tight_layout()

    # 保存图像
    plt.savefig('output/Figures/3D_cable_Truth.png', dpi=600, bbox_inches='tight', facecolor='white')
    print("3D plot generated and saved as 3D_cable.png ")

else:
    print("Error: No valid data to plot")

# 输出统计信息
print(f"\n=== Data Statistics ===")
print(f"Total time points processed: {len(time_indices)}")
print(f"Valid time series: {len(Xr)}")
print(f"Center trajectory points: {len(Xc)}")
print(f"Data new shape: {data_new.shape}")
print(f"Number of physical points: {n_points}")