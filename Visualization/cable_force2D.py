import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import os

# 设置字体 - 使用可用字体替代Times New Roman
plt.rcParams['font.family'] = ['DejaVu Serif', 'Liberation Serif', 'serif']
plt.rcParams['font.serif'] = ['DejaVu Serif', 'Liberation Serif', 'serif']
plt.rcParams['pdf.fonttype'] = 42  # 嵌入字体，而不是转换为路径
plt.rcParams['ps.fonttype'] = 42

# 加载数据 - 使用numpy直接加载更快
print("正在加载数据...")
data = np.loadtxt('output/newoutput2.csv', delimiter=',')
print(f"数据加载完成，形状: {data.shape}")

# 初始化 Fx, Fy, Fz 矩阵 - 完全向量化处理
num_rows, num_cols = data.shape
n_points = num_cols // 10

if num_cols % 10 == 0:
    # 向量化提取所有力数据
    print("正在提取力数据...")
    
    # 创建索引数组来一次性提取所有力数据
    force_indices = np.arange(3, num_cols, 10)
    
    # 使用高级索引一次性提取所有Fx, Fy, Fz
    Fx = data[:, force_indices].copy()
    Fy = data[:, force_indices + 1].copy()
    Fz = data[:, force_indices + 2].copy()
    
    print(f"力数据提取完成,Fx形状: {Fx.shape}")
else:
    print("警告: 数据列数不是10的倍数,无法正确提取力数据")
    Fx = Fy = Fz = np.zeros((num_rows, n_points))

# 时间数组
t = np.linspace(0.001, 20.001, num_rows, endpoint=False)

# 选择要绘制的点
points_to_plot = [0, 24, 49]  # 点1, 25, 50
point_names = ['Point1', 'Point25', 'Point50']
colors = ['#320A72', '#500F04', '#274400']

# 创建图形
fig, axs = plt.subplots(3, 3, figsize=(15, 10))
#fig.suptitle('Force Analysis at Different Points', fontsize=18, fontweight='bold')

# 定义优化的绘图函数
def plot_subplot(ax, x, y, title, xlabel, ylabel, xlim, ylim, color='b'):
    ax.plot(x, y, '-', linewidth=1.2, color=color, alpha=0.8)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.tick_params(axis='both', which='major', labelsize=10)

# 批量绘制所有子图
print("Saveing plots...")
for col_idx, (point_idx, point_name, color) in enumerate(zip(points_to_plot, point_names, colors)):
    # 第一行: Fx (张力)
    plot_subplot(axs[0, col_idx], t, Fx[:, point_idx], 
                f"Tension at {point_name}", "Time(s)", "Force(N)", 
                [0, 10], [-8, 8], color)
    
    # 第二行: Fy
    plot_subplot(axs[1, col_idx], t, Fy[:, point_idx], 
                f"Fy at {point_name}", "Time(s)", "Force(N)", 
                [0, 10], [-1.5, 1.5], color)
    
    # 第三行: Fz
    plot_subplot(axs[2, col_idx], t, Fz[:, point_idx], 
                f"Fz at {point_name}", "Time(s)", "Force(N)", 
                [0, 10], [-1.5, 1.5], color)

# 调整布局
plt.tight_layout()
plt.subplots_adjust(top=0.93)

# 保存图像
output_filename = "force_analysis_plot"
plt.savefig(f"{output_filename}.png", dpi=600, bbox_inches='tight', facecolor='white')
#plt.savefig(f"{output_filename}.pdf", bbox_inches='tight', facecolor='white')
print(f"Plots are saved as {output_filename}.png 和 {output_filename}.pdf")


# 输出统计信息
#print("\n=== 数据统计 ===")
#for point_idx, point_name in zip(points_to_plot, point_names):
#    print(f"\n{point_name}:")
#    print(f"  Fx: 均值={Fx[:, point_idx].mean():.3f}, 标准差={Fx[:, point_idx].std():.3f}, 范围=[{Fx[:, point_idx].min():.3f}, {Fx[:, point_idx].max():.3f}]")
#    print(f"  Fy: 均值={Fy[:, point_idx].mean():.3f}, 标准差={Fy[:, point_idx].std():.3f}, 范围=[{Fy[:, point_idx].min():.3f}, {Fy[:, point_idx].max():.3f}]")
#    print(f"  Fz: 均值={Fz[:, point_idx].mean():.3f}, 标准差={Fz[:, point_idx].std():.3f}, 范围=[{Fz[:, point_idx].min():.3f}, {Fz[:, point_idx].max():.3f}]")
