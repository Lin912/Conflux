import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.ticker as ticker
from mpl_toolkits.mplot3d import Axes3D
import os

# ==========================================
# 0. 基础设置
# ==========================================
def set_pub_style():
    plt.rcParams['font.family'] = 'serif'
    plt.rcParams['font.serif'] = ['Times New Roman']
    plt.rcParams['mathtext.fontset'] = 'stix'
    plt.rcParams['font.size'] = 10
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['lines.linewidth'] = 1.2
    plt.rcParams['pdf.fonttype'] = 42
    plt.rcParams['svg.fonttype'] = 'none'

set_pub_style()

# ==========================================
# 1. 配置参数
# ==========================================
data_folder = 'output/DataCompara' 

# 定义三个算例，分配不同的主色调 (Hue)
# 建议：蓝色(Blue), 红色(Red), 绿色(Green) 或 紫色(Purple)
files = [
    {'name': 'newoutputT2A0.16.csv', 'label': 'Amp 0.16', 'color': "#020085", 'ls': '-'}, # 蓝色
    {'name': 'newoutputT2A0.35.csv', 'label': 'Amp 0.35', 'color': "#6d0202", 'ls': '--'}, # 橙色
    {'name': 'newoutputT2A0.50.csv', 'label': 'Amp 0.50', 'color': "#135000", 'ls': '-.'}  # 绿色
]

dt = 0.002
# 为了防止画面过乱，建议减少时间步的数量，只选关键帧
# 例如：只画 5-6 个关键时刻
representative_steps = [0, 1000, 2000, 3000, 4000] 

# 坐标轴范围
ENABLE_MANUAL_LIMITS = True
X_LIMITS = [-5.0, 5.0]   # 稍微扩大一点范围以容纳大振幅
Y_LIMITS = [-2.0, 6.0]
Z_LIMITS = [-22.0, 2.0]

output_dir = os.path.join(data_folder, 'Figures_Compare_All')
os.makedirs(output_dir, exist_ok=True)

# ==========================================
# 2. 数据读取与处理 (保持不变)
# ==========================================
def load_and_integrate_data(filename):
    filepath = os.path.join(data_folder, filename)
    print(f"Reading: {filepath} ...")
    try:
        data = np.loadtxt(filepath, delimiter=',')
    except OSError:
        return None

    rows, cols = data.shape
    if cols % 10 == 0:
        n_nodes = cols // 10
        Tck = np.zeros((rows, n_nodes * 3))
        for i in range(n_nodes):
            idx = 10 * i
            Tck[:, 3*i : 3*i+3] = data[:, idx : idx+3]
    else:
        Tck = data.copy()

    h = dt
    n_rows_data, n_cols_data = Tck.shape
    weights_simpson = np.ones(n_rows_data)
    weights_simpson[1:-1:2] = 4; weights_simpson[2:-2:2] = 2
    weights_simpson[0] = 1/3; weights_simpson[-1] = 1/3
    weights_trap = np.ones(n_rows_data)
    weights_trap[0] = 0.5; weights_trap[-1] = 0.5
    
    simpson_result = np.zeros_like(Tck)
    trapezoidal_result = np.zeros_like(Tck)
    for col in range(n_cols_data):
        simpson_result[:, col] = np.cumsum(Tck[:, col] * weights_simpson) * (h / 3)
        trapezoidal_result[:, col] = np.cumsum(Tck[:, col] * weights_trap) * h
        
    data_new = np.zeros_like(Tck)
    data_new[2:, :] = simpson_result[2:, :]
    data_new[1, :] = trapezoidal_result[1, :]
    data_new[0, :] = 0

    n_points = data_new.shape[1] // 3
    K = np.arange(0, -0.2 * n_points, -0.2)[:n_points]
    for j in range(n_points):
        data_new[:, 3 * j] = -data_new[:, 3 * j] + K[j]
        
    return data_new

# ==========================================
# 3. 颜色生成工具
# ==========================================
def get_gradient_color(base_color_name, t_norm):
    """
    根据时间进度 (0~1) 生成对应色系的颜色。
    t_norm = 0.0 -> 非常淡
    t_norm = 1.0 -> 纯色 (base_color)
    """
    base_rgb = mcolors.to_rgb(base_color_name)
    # 混合白色：color = base * t + white * (1-t)
    # 但我们希望t=0时也是可见的淡色，不是纯白
    # 调整权重：t_eff 从 0.3 到 1.0
    t_eff = 0.3 + 0.7 * t_norm 
    
    r = base_rgb[0] * t_eff + 1.0 * (1 - t_eff)
    g = base_rgb[1] * t_eff + 1.0 * (1 - t_eff)
    b = base_rgb[2] * t_eff + 1.0 * (1 - t_eff)
    return (r, g, b)

# ==========================================
# 4. 主程序：绘制综合对比图
# ==========================================
# 4.1 加载数据
datasets = []
for file_info in files:
    processed_data = load_and_integrate_data(file_info['name'])
    if processed_data is not None:
        datasets.append({
            'data': processed_data,
            'info': file_info
        })

if not datasets: exit()

# 4.2 初始化画布 (只画一张大图)
fig = plt.figure(figsize=(14, 10))

# 布局
ax_3d = fig.add_subplot(2, 2, 1, projection='3d')
ax_xy = fig.add_subplot(2, 2, 2)
ax_xz = fig.add_subplot(2, 2, 3)
ax_yz = fig.add_subplot(2, 2, 4)

# 背景设置
ax_3d.xaxis.pane.fill = False; ax_3d.yaxis.pane.fill = False; ax_3d.zaxis.pane.fill = False
ax_3d.grid(True)
xx, yy = np.meshgrid(np.linspace(X_LIMITS[0], X_LIMITS[1], 2), np.linspace(Y_LIMITS[0], Y_LIMITS[1], 2))
ax_3d.plot_surface(xx, yy, np.zeros_like(xx), alpha=0.1, color='gray')
ax_xz.axhline(0, color='gray', ls=':', lw=0.8)
ax_yz.axhline(0, color='gray', ls=':', lw=0.8)

# 4.3 绘图循环
total_steps = len(representative_steps)

for ds in datasets:
    data = ds['data']
    info = ds['info']
    base_color = info['color']
    ls = info['ls']
    
    print(f"Plotting {info['label']} in {base_color}...")
    
    for i, step in enumerate(representative_steps):
        if step >= data.shape[0]: continue
        
        # 归一化时间进度
        t_norm = i / (total_steps - 1) if total_steps > 1 else 1.0
        
        # 获取当前步的颜色 (同色系，深浅不同)
        color = get_gradient_color(base_color, t_norm)
        
        # 线宽：最后一步加粗
        lw = 1.0 if i == total_steps - 1 else 1.0
        alpha = 0.9 if i == total_steps - 1 else 0.6 # 旧时刻稍微透明一点
        
        # 绘制
        # 3D
        ax_3d.plot(data[step, 1::3], data[step, 2::3], data[step, 0::3], 
                   color=color, ls=ls, lw=lw, alpha=alpha)
        ax_3d.set_aspect('equal')
        
        # 2D
        ax_xy.plot(data[step, 1::3], data[step, 2::3], 
                   color=color, ls=ls, lw=lw, alpha=alpha)
        ax_xz.plot(data[step, 1::3], data[step, 0::3], 
                   color=color, ls=ls, lw=lw, alpha=alpha)
        ax_yz.plot(data[step, 2::3], data[step, 0::3], 
                   color=color, ls=ls, lw=lw, alpha=alpha)
        
        ax_xy.set_aspect('equal')
        ax_xz.set_aspect('equal')
        ax_yz.set_aspect('equal')

# 4.4 装饰与图例
# 手动创建一个图例，只显示颜色代表的含义
from matplotlib.lines import Line2D
custom_lines = [Line2D([0], [0], color=d['info']['color'], lw=2, linestyle=d['info']['ls']) for d in datasets]
custom_labels = [d['info']['label'] for d in datasets]

# 在图的下方添加图例
fig.legend(custom_lines, custom_labels, loc='lower center', ncol=3, bbox_to_anchor=(0.5, 0.05), frameon=False)

def format_ax(ax, title, xl, yl):
    ax.set_title(title, pad=10)
    ax.set_xlabel(xl)
    ax.set_ylabel(yl)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    # 手动设置范围，保证所有算例都在框内
    if ENABLE_MANUAL_LIMITS:
        if 'Z' in yl: ax.set_ylim(Z_LIMITS)
        if 'Z' in xl: ax.set_xlim(Z_LIMITS) # 特殊情况
        # 一般情况
        if xl == 'X (m)': ax.set_xlim(X_LIMITS)
        if xl == 'Y (m)': ax.set_xlim(Y_LIMITS)
        if yl == 'Y (m)': ax.set_ylim(Y_LIMITS)
        if yl == 'Z (m)': ax.set_ylim(Z_LIMITS)
        
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    ax.yaxis.set_major_locator(ticker.MultipleLocator(2))

ax_3d.set_title("(a) 3D Comparison", y=1.05)
ax_3d.view_init(elev=20, azim=-50)
if ENABLE_MANUAL_LIMITS:
    ax_3d.set_xlim(X_LIMITS); ax_3d.set_ylim(Y_LIMITS); ax_3d.set_zlim(Z_LIMITS)
    
ax_3d.xaxis.set_major_locator(ticker.MultipleLocator(2))
ax_3d.yaxis.set_major_locator(ticker.MultipleLocator(2))
ax_3d.zaxis.set_major_locator(ticker.MultipleLocator(2))

format_ax(ax_xy, "(b) Plan View (X-Y)", 'X (m)', 'Y (m)')
format_ax(ax_xz, "(c) Elevation View (X-Z)", 'X (m)', 'Z (m)')
format_ax(ax_yz, "(d) Side View (Y-Z)", 'Y (m)', 'Z (m)')

plt.subplots_adjust(bottom=0.12) # 留出底部图例空间
save_name = 'Comparison_All_Cases'
plt.savefig(os.path.join(output_dir, f'{save_name}.png'), dpi=600)
plt.savefig(os.path.join(output_dir, f'{save_name}.pdf'), format='pdf')

print(f"Done. Saved to {output_dir}")
plt.show()