import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 设置可用字体
plt.rcParams['font.family'] = ['DejaVu Serif', 'Liberation Serif', 'serif']

# 数据导入
print("Loading Data...")
data = np.loadtxt('output/newoutput1.csv', delimiter=',')
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
    h = 0.001
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
K = np.arange(0, -50 * n_points, -50)[:n_points]  # 根据实际点数生成K

for j in range(n_points):
    if 3 * j + 2 < data_new.shape[1]:
        data_new[:, 3 * j + 2] += K[j]

# 定义点的集合 - 修复索引边界问题
time_indices = np.arange(0, min(2001, data_new.shape[0]), 100)  # 确保不超出时间范围
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
            x_idx = 3 * j + 2
            y_idx = 3 * j + 3
            z_idx = 3 * j + 1
            
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

# 定义中心点数据 - 修复索引
valid_center_points = min(2000, data_new.shape[0])
if data_new.shape[1] >= 4:  # 确保有足够的列
    Xc = data_new[:valid_center_points, 2]
    Yc = data_new[:valid_center_points, 3] 
    Zc = data_new[:valid_center_points, 1]
else:
    Xc, Yc, Zc = np.array([]), np.array([]), np.array([])
    print("Warning: Not enough columns for center point data")

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
                label = f't={time_indices[i]*0.001:.1f}s'
            else:
                label = None
            ax.plot(x, y, z, color=color, alpha=0.8, linewidth=1.2, label=label)

    # 绘制中心点轨迹
    if len(Xc) > 1:
        ax.plot(Xc, Yc, Zc, linestyle="--", color="#B3112F", linewidth=2.5, label='Center Point Trajectory')

    # 图形设置 - 根据数据动态调整范围和刻度
    if len(Xr) > 0:
        all_x = np.concatenate(Xr)
        all_y = np.concatenate(Yr) 
        all_z = np.concatenate(Zr)
        
        print(f"Data ranges - X: [{np.min(all_x):.2f}, {np.max(all_x):.2f}], "
              f"Y: [{np.min(all_y):.3f}, {np.max(all_y):.3f}], "
              f"Z: [{np.min(all_z):.3f}, {np.max(all_z):.3f}]")
        
        # 设置坐标轴范围（增加15%的边距）
        x_range = np.max(all_x) - np.min(all_x)
        y_range = np.max(all_y) - np.min(all_y)
        z_range = np.max(all_z) - np.min(all_z)
        
        x_margin = x_range * 0.15
        y_margin = y_range * 0.15
        z_margin = z_range * 0.15
        
        ax.set_xlim([np.min(all_x) - x_margin, np.max(all_x) + x_margin])
        ax.set_ylim([np.min(all_y) - y_margin, np.max(all_y) + y_margin])
        ax.set_zlim([np.min(all_z) - z_margin, np.max(all_z) + z_margin])
        
        # 改进的智能刻度函数
        def smart_ticks(data_min, data_max, max_ticks=6):
            """改进的智能刻度生成函数"""
            data_range = data_max - data_min
            if data_range == 0:
                return np.array([data_min])
            
            # 计算理想的刻度间隔
            ideal_step = data_range / (max_ticks - 1)
            
            # 找到最接近的理想步长的10的幂次
            exponent = np.floor(np.log10(ideal_step))
            fraction = ideal_step / (10 ** exponent)
            
            # 选择最接近的标准步长
            if fraction < 1.5:
                step = 10 ** exponent
            elif fraction < 3:
                step = 2 * 10 ** exponent
            elif fraction < 7:
                step = 5 * 10 ** exponent
            else:
                step = 10 * 10 ** exponent
            
            # 确保至少有3个刻度
            num_ticks = int(data_range / step) + 1
            if num_ticks < 3:
                step = data_range / 2
            
            # 生成刻度
            start = np.floor(data_min / step) * step
            end = np.ceil(data_max / step) * step
            ticks = np.arange(start, end + step/2, step)
            
            # 确保刻度在数据范围内
            ticks = ticks[(ticks >= data_min - step/2) & (ticks <= data_max + step/2)]
            
            return ticks
        
        # 设置各轴刻度
        x_ticks = smart_ticks(np.min(all_x), np.max(all_x))
        y_ticks = smart_ticks(np.min(all_y), np.max(all_y))
        z_ticks = smart_ticks(np.min(all_z), np.max(all_z))
        
        ax.set_xticks(x_ticks)
        ax.set_yticks(y_ticks)
        ax.set_zticks(z_ticks)
        
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
        
        ax.set_xticklabels(format_tick_labels(x_ticks))
        ax.set_yticklabels(format_tick_labels(y_ticks))
        ax.set_zticklabels(format_tick_labels(z_ticks))

    # 设置坐标轴标签
    ax.set_xlabel('Z Coordinate (m)', fontsize=14, fontweight='bold', labelpad=15)
    ax.set_ylabel('Y Coordinate (m)', fontsize=14, fontweight='bold', labelpad=15)
    ax.set_zlabel('X Coordinate (m)', fontsize=14, fontweight='bold', labelpad=15)

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
    
    # 添加颜色条
    sm = plt.cm.ScalarMappable(cmap='viridis', 
                              norm=plt.Normalize(0, time_indices[-1]*0.001))
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
    plt.savefig('3d_cable_profile.png', dpi=600, bbox_inches='tight', facecolor='white')
    #plt.savefig('3d_cable_profile.pdf', bbox_inches='tight', facecolor='white')

    print("3D plot generated and saved as 3d_cable_profile.png and 3d_cable_profile.pdf")

    # 尝试显示图形
    try:
        plt.show()
    except:
        print("Could not display plot, please check the saved image files")
else:
    print("Error: No valid data to plot")

# 输出统计信息
print(f"\n=== Data Statistics ===")
print(f"Total time points processed: {len(time_indices)}")
print(f"Valid time series: {len(Xr)}")
print(f"Center trajectory points: {len(Xc)}")
print(f"Data new shape: {data_new.shape}")
print(f"Number of physical points: {n_points}")