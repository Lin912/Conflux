import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.ticker as ticker

# === 0. Adobe Illustrator 适配设置 ===
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['svg.fonttype'] = 'none' 
plt.rcParams['font.family'] = ['Arial', 'Helvetica', 'DejaVu Sans']

# === 1. 数据配置与导入 ===
print("Loading Data...")
try:
    data = np.loadtxt('output/Data/newoutput1.csv', delimiter=',')
except OSError:
    print("Warning: File not found. Generating dummy data for test.")
    rows, cols = 6501, 310
    data = np.random.normal(0, 0.05, (rows, cols))

rows, cols = data.shape
if cols % 10 == 0:
    Tck = np.zeros((rows, (cols // 10) * 3))
    indices = np.arange(0, cols, 10)
    for i, idx in enumerate(indices):
        Tck[:, 3 * i: 3 * i + 3] = data[:, idx:idx + 3]
else:
    Tck = data.copy()

# === 2. 积分计算 ===
data_new = np.zeros((20000, Tck.shape[1]))
if data_new.shape[0] < rows: data_new = np.zeros((rows, Tck.shape[1]))

def compute_integrals_vectorized(data):
    h = 0.002
    n_rows, n_cols = data.shape
    
    weights_simpson = np.ones(n_rows)
    weights_simpson[1:-1:2] = 4
    weights_simpson[2:-2:2] = 2
    weights_simpson[0] = 1/3
    weights_simpson[-1] = 1/3
    
    weights_trap = np.ones(n_rows)
    weights_trap[0] = 0.5
    weights_trap[-1] = 0.5
    
    simpson_result = np.zeros((n_rows, n_cols))
    trapezoidal_result = np.zeros((n_rows, n_cols))
    
    for col in range(n_cols):
        simpson_result[:, col] = np.cumsum(data[:, col] * weights_simpson) * (h / 3)
        trapezoidal_result[:, col] = np.cumsum(data[:, col] * weights_trap) * h
        
    return simpson_result, trapezoidal_result

simpson_result, trapezoidal_result = compute_integrals_vectorized(Tck)
max_fill_idx = min(data_new.shape[0], simpson_result.shape[0])
data_new[2:max_fill_idx, :] = simpson_result[2:max_fill_idx, :]
data_new[1, :] = trapezoidal_result[1, :]
data_new[0, :] = 0

# === 3. 几何构建 ===
n_points = data_new.shape[1] // 3
K = np.arange(0, -0.2 * n_points, -0.2)[:n_points]
for j in range(n_points):
    if 3 * j + 2 < data_new.shape[1]:
        data_new[:, 3 * j] = -data_new[:, 3 * j] + K[j]

# === 4. 时间设置 (0-12s) ===
dt = 0.002
target_duration = 12.0
interval_seconds = 1.0 

max_idx = int(target_duration / dt)
step_idx = int(interval_seconds / dt)
valid_max_idx = min(max_idx + 1, data_new.shape[0])
time_indices = np.arange(0, valid_max_idx, step_idx)

# === 5. 坐标变换 ===
plot_frames = []
for t_idx in time_indices:
    plot_frames.append({
        'x': data_new[t_idx, 1::3], 
        'y': data_new[t_idx, 2::3], 
        'z': data_new[t_idx, 0::3]
    })

# === 6. 红色虚线轨迹 ===
traj_indices = np.arange(0, valid_max_idx, 5)
node_idx = 0 
t_raw_x = data_new[traj_indices, node_idx*3 + 0]
t_raw_y = data_new[traj_indices, node_idx*3 + 1]
t_raw_z = data_new[traj_indices, node_idx*3 + 2]

traj_plot_x = t_raw_y
traj_plot_y = t_raw_z
traj_plot_z = t_raw_x

# === 7. 绘图参数设置 ===
xlim_fixed = [-0.5, 0.5]
ylim_fixed = [-1, 6]
zlim_fixed = [-22, 2]

colors = plt.cm.Blues(np.linspace(0.4, 1, len(plot_frames)))

def save_vector_figure(filename_base):
    plt.savefig(f'output/Figures/{filename_base}.svg', format='svg', bbox_inches='tight', dpi=600)
    plt.savefig(f'output/Figures/{filename_base}.pdf', format='pdf', bbox_inches='tight')
    print(f"Saved {filename_base}")

# ==========================================
# 图 1: 3D 主视图 (Y轴视觉拉长)
# ==========================================
fig_3d = plt.figure(figsize=(14, 12)) 
ax = fig_3d.add_subplot(111, projection='3d')

for frame, color in zip(plot_frames, colors):
    ax.plot(frame['x'], frame['y'], frame['z'], color=color, alpha=0.9, linewidth=1.5)

ax.plot(traj_plot_x, traj_plot_y, traj_plot_z, color='#660000', linestyle='--', linewidth=2.5, label='Top Node Trajectory')

# 坐标轴范围
ax.set_xlim(xlim_fixed)
ax.set_ylim(ylim_fixed)
ax.set_zlim(zlim_fixed)

# Y轴刻度间隔 0.5m
ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))

# === 关键修改：Box Aspect ===
# 原物理比例约为 (1, 0.8, 2.4)。
# 为了"视觉拉长Y轴"，我们将Y的分量显著增加到 1.8。
# 现在 Y轴(8m范围) 在屏幕上的长度将是 X轴(10m范围) 的 1.8倍。
ax.set_box_aspect((1, 2.0, 2.4)) 

ax.view_init(elev=20, azim=45)
ax.set_xlabel('X (m)')
ax.set_ylabel('Y (m)')
ax.set_zlabel('Depth (m)')

# 时间轴 Colorbar
sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(0, target_duration))
sm.set_array([])

# 刻度也改为从 0 到 target_duration
cbar_ticks = np.arange(0, target_duration + 0.1, 1.0)

cbar = plt.colorbar(sm, ax=ax, shrink=0.85, pad=0.1, ticks=cbar_ticks)

cbar.set_label('Time (s)', rotation=270, labelpad=20, fontsize=12)
cbar.ax.tick_params(labelsize=8)

save_vector_figure('1_Cable_3D_View_Elongated')
plt.close(fig_3d)

# ==========================================
# 图 2: XY 平面投影
# ==========================================
fig_xy, ax_xy = plt.subplots(figsize=(8, 8))
for frame, color in zip(plot_frames, colors):
    ax_xy.plot(frame['x'], frame['y'], color=color, alpha=0.8, linewidth=1.2)
ax_xy.plot(traj_plot_x, traj_plot_y, color='#660000', linestyle='--', linewidth=2)

ax_xy.set_xlim(xlim_fixed)
ax_xy.set_ylim(ylim_fixed)
# 这里保持 equal 比例，真实反映物理形状
ax_xy.set_aspect('equal')
ax_xy.grid(True, linestyle=':', alpha=0.6)
ax_xy.set_xlabel('X (m)')
ax_xy.set_ylabel('Y (m)')

# === 新增：控制坐标轴刻度间距 ===
# 设置 X 轴主刻度间距 (例如 1.0m)
ax_xy.xaxis.set_major_locator(ticker.MultipleLocator(0.2)) 

# 设置 Y 轴主刻度间距 (例如 0.5m)
ax_xy.yaxis.set_major_locator(ticker.MultipleLocator(0.5))

save_vector_figure('2_Projection_XY_Top')
plt.close(fig_xy)

# ==========================================
# 图 3: XZ 平面投影
# ==========================================
fig_xz, ax_xz = plt.subplots(figsize=(6, 10))
for frame, color in zip(plot_frames, colors):
    ax_xz.plot(frame['x'], frame['z'], color=color, alpha=0.8, linewidth=1.2)
ax_xz.plot(traj_plot_x, traj_plot_z, color='#660000', linestyle='--', linewidth=2)

ax_xz.set_xlim(xlim_fixed)
ax_xz.set_ylim(zlim_fixed)
ax_xz.set_xlabel('X (m)')
ax_xz.set_ylabel('Z (Depth)')
ax_xz.grid(True, linestyle=':', alpha=0.6)

# === 新增：控制坐标轴刻度间距 ===
# 设置 X 轴主刻度间距 (例如 1.0m)
ax_xz.xaxis.set_major_locator(ticker.MultipleLocator(0.2)) 
# 设置 Z 轴主刻度间距 (例如 2.0m)
ax_xz.yaxis.set_major_locator(ticker.MultipleLocator(2.0))

save_vector_figure('3_Projection_XZ_Front')
plt.close(fig_xz)

# ==========================================
# 图 4: YZ 平面投影 (视觉加宽)
# ==========================================
# 为了配合3D图中凸显YZ平面的意图，这里将 figsize 的宽度增加
fig_yz, ax_yz = plt.subplots(figsize=(8, 10)) # 宽度从6增加到8
for frame, color in zip(plot_frames, colors):
    ax_yz.plot(frame['y'], frame['z'], color=color, alpha=0.8, linewidth=1.2)
ax_yz.plot(traj_plot_y, traj_plot_z, color='#660000', linestyle='--', linewidth=2)

ax_yz.set_xlim(ylim_fixed) 
ax_yz.set_ylim(zlim_fixed)
ax_yz.set_xlabel('Y (m)')
ax_yz.set_ylabel('Z (Depth)')
ax_yz.grid(True, linestyle=':', alpha=0.6)

# === 新增：控制坐标轴刻度间距 ===
# 设置 Y 轴主刻度间距 (例如 0.5m)
ax_yz.xaxis.set_major_locator(ticker.MultipleLocator(0.5)) 
# 设置 Z 轴主刻度间距 (例如 2.0m)
ax_yz.yaxis.set_major_locator(ticker.MultipleLocator(2.0))

save_vector_figure('4_Projection_YZ_Side')
plt.close(fig_yz)

print("\nProcessing complete. Y-axis visually elongated in 3D plot.")