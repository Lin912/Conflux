import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from mpl_toolkits.mplot3d import Axes3D
import os

# ==========================================
# 0. 绘图风格设置 (学术期刊风格)
# ==========================================
def set_pub_style():
    # 设置字体为 Times New Roman (或 Arial)
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.rcParams['mathtext.fontset'] = 'stix' # 数学公式字体类似 Times
    
    # 字号设置
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    
    # 线条与刻度
    plt.rcParams['axes.linewidth'] = 1.0 # 边框加粗
    plt.rcParams['lines.linewidth'] = 1.5 # 线条加粗
    plt.rcParams['xtick.direction'] = 'in' # 刻度朝内
    plt.rcParams['ytick.direction'] = 'in'
    
    # 矢量图设置
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['ps.fonttype'] = 42
    plt.rcParams['svg.fonttype'] = 'none'

set_pub_style()

# ==========================================
# 1. 配置参数
# ==========================================

# [修改这里] 请输入您CSV文件所在的文件夹路径
# 如果文件和脚本在同一目录下，保持为 '.' 即可
# Windows路径示例: r'D:\Project\CableData'
data_folder = 'output/DataCompara' 

# 定义三个算例文件名
files = [
    {'name': 'newoutputT2A0.16.csv', 'label': 'Amp 0.16', 'color': "#020085", 'ls': '-'}, # 蓝色
    {'name': 'newoutputT2A0.35.csv', 'label': 'Amp 0.35', 'color': "#6d0202", 'ls': '--'}, # 橙色
    {'name': 'newoutputT2A0.50.csv', 'label': 'Amp 0.50', 'color': "#135000", 'ls': '-.'}  # 绿色
]

# 时间步长 (dt)
dt = 0.002
representative_steps = [0, 250, 500, 750, 1000, 1250, 1500, 1750, 2000, 2250, 2500, 2750, 3000, 3250, 3500, 3750, 4000] # 对应 6.0s, 6.5s, 7.0s, 7.5s

# -----------------------------------------------------------
# [新增] 手动调整坐标轴范围
# -----------------------------------------------------------
ENABLE_MANUAL_LIMITS = True  # 开关：True为手动固定范围，False为自动适应

# 请根据您的缆绳实际尺寸调整以下数值
# 格式: [最小值, 最大值]
X_LIMITS = [-5.0, 5.0]    # 水平 X 方向范围 (米)
Y_LIMITS = [-5.0, 15.0]    # 水平 Y 方向范围 (米)
Z_LIMITS = [-22.0, 2.0]   # 深度 Z 方向范围 (米)
# -----------------------------------------------------------

# [输出设置]
output_dir = os.path.join(data_folder, 'Figures_3D_Manual')
os.makedirs(output_dir, exist_ok=True)

# [绘图样式]
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['svg.fonttype'] = 'none' 
plt.rcParams['font.family'] = ['Arial', 'Helvetica', 'DejaVu Sans']

# ==========================================
# 2. 数据处理函数 (速度 -> 位移)
# ==========================================
def load_and_integrate_data(filename):
    filepath = os.path.join(data_folder, filename)
    print(f"正在读取文件: {filepath} ...")
    
    try:
        data = np.loadtxt(filepath, delimiter=',')
    except OSError:
        print(f"错误: 无法找到文件 {filepath}")
        return None

    rows, cols = data.shape
    
    # --- 提取每隔10个节点的列 ---
    if cols % 10 == 0:
        n_nodes = cols // 10
        Tck = np.zeros((rows, n_nodes * 3))
        for i in range(n_nodes):
            idx = 10 * i
            Tck[:, 3*i : 3*i+3] = data[:, idx : idx+3]
    else:
        Tck = data.copy()

    # --- 积分计算 (Simpson积分) ---
    h = dt
    n_rows_data, n_cols_data = Tck.shape
    
    weights_simpson = np.ones(n_rows_data)
    weights_simpson[1:-1:2] = 4
    weights_simpson[2:-2:2] = 2
    weights_simpson[0] = 1/3
    weights_simpson[-1] = 1/3
    
    weights_trap = np.ones(n_rows_data)
    weights_trap[0] = 0.5
    weights_trap[-1] = 0.5
    
    simpson_result = np.zeros_like(Tck)
    trapezoidal_result = np.zeros_like(Tck)
    
    for col in range(n_cols_data):
        simpson_result[:, col] = np.cumsum(Tck[:, col] * weights_simpson) * (h / 3)
        trapezoidal_result[:, col] = np.cumsum(Tck[:, col] * weights_trap) * h
        
    data_new = np.zeros_like(Tck)
    data_new[2:, :] = simpson_result[2:, :]
    data_new[1, :] = trapezoidal_result[1, :]
    data_new[0, :] = 0

    # --- 初始几何形态叠加 ---
    n_points = data_new.shape[1] // 3
    K = np.arange(0, -0.2 * n_points, -0.2)[:n_points]
    
    for j in range(n_points):
        data_new[:, 3 * j] = -data_new[:, 3 * j] + K[j]
        
    return data_new

# ==========================================
# 3. 主程序：绘图
# ==========================================

datasets = []
for file_info in files:
    processed_data = load_and_integrate_data(file_info['name'])
    if processed_data is not None:
        datasets.append({
            'data': processed_data,
            'label': file_info['label'],
            'color': file_info['color'],
            'ls': file_info['ls']
        })

if not datasets:
    print("程序终止：无数据。")
    exit()

for step in representative_steps:
    time_sec = step * dt
    print(f"正在绘制时刻 t = {time_sec:.2f} s ...")
    
    # 创建 2x2 画布
    fig = plt.figure(figsize=(12, 10))
    
    # 子图定义
    ax_3d = fig.add_subplot(2, 2, 1, projection='3d')
    
    # 3D 背景透明化/白色化 (去除默认的灰底)
    ax_3d.xaxis.pane.fill = False
    ax_3d.yaxis.pane.fill = False
    ax_3d.zaxis.pane.fill = False
    ax_3d.xaxis.pane.set_edgecolor('w')
    ax_3d.yaxis.pane.set_edgecolor('w')
    ax_3d.zaxis.pane.set_edgecolor('w')
    ax_3d.grid(True) # 3D图通常不要网格，或者要非常淡的

    for ds in datasets:
        if step >= ds['data'].shape[0]: continue
        data = ds['data']
        ax_3d.plot(data[step, 1::3], data[step, 2::3], data[step, 0::3], 
                   color=ds['color'], linestyle=ds['ls'], label=ds['label'], alpha=0.9)
    
    # 绘制海平面 (参考面)
    xx, yy = np.meshgrid(np.linspace(X_LIMITS[0], X_LIMITS[1], 2), np.linspace(Y_LIMITS[0], Y_LIMITS[1], 2))
    ax_3d.plot_surface(xx, yy, np.zeros_like(xx), alpha=0.1, color='cyan')

    ax_3d.set_xlabel('X (m)', labelpad=5)
    ax_3d.set_ylabel('Y (m)', labelpad=5)
    ax_3d.set_zlabel('Z (m)', labelpad=5)
    ax_3d.set_title(f"(a) 3D View ($t={time_sec:.2f}$ s)", y=1.02) # 使用 (a) 编号
    ax_3d.view_init(elev=25, azim=-45)
    if ENABLE_MANUAL_LIMITS:
        ax_3d.set_xlim(X_LIMITS); ax_3d.set_ylim(Y_LIMITS); ax_3d.set_zlim(Z_LIMITS)

    # ---------------------------
    # 2D Projections (其余三个)
    # ---------------------------
    # 定义辅助函数来统一设置2D图格式
    def format_2d_ax(ax, title, xlabel, ylabel):
        ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.5) # 网格更细更淡
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        # 强制开启四周刻度
        ax.tick_params(top=True, right=True) 

    # --- XY Plane ---
    ax_xy = fig.add_subplot(2, 2, 2)
    for ds in datasets:
        if step >= ds['data'].shape[0]: continue
        data = ds['data']
        ax_xy.plot(data[step, 1::3], data[step, 2::3], 
                   color=ds['color'], linestyle=ds['ls'], label=ds['label'])
    
    format_2d_ax(ax_xy, f"(b) Plan View (X-Y)", 'X (m)', 'Y (m)')
    if ENABLE_MANUAL_LIMITS:
        ax_xy.set_xlim(X_LIMITS); ax_xy.set_ylim(Y_LIMITS)
    else: ax_xy.axis('equal')

    # --- XZ Plane ---
    ax_xz = fig.add_subplot(2, 2, 3)
    # 画一条海平面参考线
    ax_xz.axhline(0, color='gray', linestyle=':', linewidth=0.8) 
    
    for ds in datasets:
        if step >= ds['data'].shape[0]: continue
        data = ds['data']
        ax_xz.plot(data[step, 1::3], data[step, 0::3], 
                   color=ds['color'], linestyle=ds['ls'], label=ds['label'])
        
    format_2d_ax(ax_xz, f"(c) Elevation View (X-Z)", 'X (m)', 'Z (m)')
    if ENABLE_MANUAL_LIMITS:
        ax_xz.set_xlim(X_LIMITS); ax_xz.set_ylim(Z_LIMITS)

    # --- YZ Plane ---
    ax_yz = fig.add_subplot(2, 2, 4)
    ax_yz.axhline(0, color='gray', linestyle=':', linewidth=0.8)
    
    for ds in datasets:
        if step >= ds['data'].shape[0]: continue
        data = ds['data']
        ax_yz.plot(data[step, 2::3], data[step, 0::3], 
                   color=ds['color'], linestyle=ds['ls'], label=ds['label'])

    format_2d_ax(ax_yz, f"(d) Side View (Y-Z)", 'Y (m)', 'Z (m)')
    if ENABLE_MANUAL_LIMITS:
        ax_yz.set_xlim(Y_LIMITS); ax_yz.set_ylim(Z_LIMITS)


    ax_3d.set_aspect('equal')
    ax_xy.set_aspect('equal')
    ax_xz.set_aspect('equal')
    ax_yz.set_aspect('equal')
    
    # ---------------------------
    # Global Legend (统一图例)
    # ---------------------------
    # 期刊通常不喜欢每个子图都有图例，建议在底部放一个共用的
    handles, labels = ax_xy.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0.02), frameon=False)

    plt.tight_layout()
    # 留出底部空间给图例
    plt.subplots_adjust(bottom=0.08)
    
    save_name = f'Pub_Quality_t{time_sec:.2f}s'
    plt.savefig(os.path.join(output_dir, f'{save_name}.png'), dpi=600) # 提高DPI
    plt.savefig(os.path.join(output_dir, f'{save_name}.pdf'), format='pdf') # 推荐保存为PDF
    plt.savefig(os.path.join(output_dir, f'{save_name}.svg'), format='svg')
    
    print(f"Saved: {save_name}")
    plt.close(fig)

print(f"Done. Check folder: {output_dir}")