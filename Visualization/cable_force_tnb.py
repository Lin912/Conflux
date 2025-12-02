import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import os

# 设置字体 - 使用可用字体替代Times New Roman
plt.rcParams['font.family'] = ['DejaVu Serif']
plt.rcParams['font.serif'] = ['DejaVu Serif']

plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

# 加载数据
print("Loading Data...")
data = np.loadtxt('output/Data/output.csv', delimiter=',')
print(f"Loaded the Data, which is: {data.shape}")

# 初始化 Tension, Force_in_normal, Force_in_bi-normal 矩阵
num_rows, num_cols = data.shape
n_points = num_cols // 10

if num_cols % 10 == 0:
    print("Catching the Force value...")
    
    force_indices = np.arange(3, num_cols, 10)
    
    Tension = data[:, force_indices].copy()
    Fn = data[:, force_indices + 1].copy()
    Fb = data[:, force_indices + 2].copy()
    
    print(f"Catched done! Tension's shape is: {Tension.shape}")
else:
    print("Warrning: can not catch the values of Force")
    Tension = Fn = Fb = np.zeros((num_rows, n_points))

# 时间数组
t = np.linspace(0.002, 40.002, num_rows, endpoint=False)

# 选择要绘制的点
points_to_plot = [0, 49, 99]  # point: 1, 50, 100
point_names = ['Point1', 'Point50', 'Point100']
colors = ['#320A72', '#500F04', '#274400']

# 创建图形
fig, axs = plt.subplots(3, 3, figsize=(15, 10))
#fig.suptitle('Force Analysis at Different Points', fontsize=18, fontweight='bold')

# 定义优化的绘图函数
def plot_subplot(ax, x, y, title, xlabel, ylabel, xlim, ylim, color='b'):
    ax.plot(x, y, '-', linewidth=2.0, color=color, alpha=0.8)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.tick_params(axis='both', which='major', labelsize=10)

# 批量绘制所有子图
print("Saveing plots...")
for col_idx, (point_idx, point_name, color) in enumerate(zip(points_to_plot, point_names, colors)):
    # 第一行: Fx (张力)
    plot_subplot(axs[0, col_idx], t, Tension[:, point_idx], 
                f"Tension at {point_name}", "Time(s)", "Tension(N)", 
                [0, 8], [-200, 200], color)
    
    # 第二行: Fy
    plot_subplot(axs[1, col_idx], t, Fn[:, point_idx], 
                f"Force_in_normal at {point_name}", "Time(s)", "Fn(N)", 
                [0, 8], [-20.0, 20.0], color)
    
    # 第三行: Fz
    plot_subplot(axs[2, col_idx], t, Fb[:, point_idx], 
                f"Force_in_bi-normal at {point_name}", "Time(s)", "Fb(N)", 
                [0, 8], [-20.0, 20.0], color)

# 调整布局
plt.tight_layout()
plt.subplots_adjust(top=0.93)

# 保存图像
output_filename = "Forces_tnb"
plt.savefig(f'output/Figures/{output_filename}.png', dpi=600, bbox_inches='tight', facecolor='white')
#plt.savefig(f"{output_filename}.pdf", bbox_inches='tight', facecolor='white')
print(f"Plots are saved as {output_filename}.png :)")


# 输出统计信息
#print("\n=== 数据统计 ===")
#for point_idx, point_name in zip(points_to_plot, point_names):
#    print(f"\n{point_name}:")
#    print(f"  Fx: 均值={Fx[:, point_idx].mean():.3f}, 标准差={Fx[:, point_idx].std():.3f}, 范围=[{Fx[:, point_idx].min():.3f}, {Fx[:, point_idx].max():.3f}]")
#    print(f"  Fy: 均值={Fy[:, point_idx].mean():.3f}, 标准差={Fy[:, point_idx].std():.3f}, 范围=[{Fy[:, point_idx].min():.3f}, {Fy[:, point_idx].max():.3f}]")
#    print(f"  Fz: 均值={Fz[:, point_idx].mean():.3f}, 标准差={Fz[:, point_idx].std():.3f}, 范围=[{Fz[:, point_idx].min():.3f}, {Fz[:, point_idx].max():.3f}]")
