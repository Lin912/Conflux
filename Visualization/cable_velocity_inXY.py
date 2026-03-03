import numpy as np
import matplotlib.pyplot as plt
import matplotlib

# 设置使用可用字体替代Times New Roman
plt.rcParams['font.family'] = ['DejaVu Serif']
plt.rcParams['font.serif'] = ['DejaVu Serif']
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42

# 数据导入
print("Loading Data...")
data = np.loadtxt('output/Data/newoutput1.csv', delimiter=',')
rows, cols = data.shape
print(f"Loaded the Data, which is: {data.shape}")

# 处理数据的矩阵重组
if cols % 10 == 0:
    Tck = np.zeros((rows, (cols // 10) * 3))
    indices = np.arange(0, cols, 10)
    for i, idx in enumerate(indices):
        Tck[:, 3 * i: 3 * i + 3] = data[:, idx: idx + 3]
else:
    Tck = np.zeros((rows, cols))

# 初始化结果矩阵
data_Vel = np.zeros((20000, 300))

# 组合结果
data_Vel[2:, :] = Tck[2:, :]
data_Vel[1, :] = Tck[1, :]
data_Vel[0, :] = 0  

print("No need to integrate...")

# 时间轴生成
t = np.arange(0.002, 40.002, 0.002)  # TimeStep

# 提取数据绘图
X1, X100 = data_Vel[:, 0], data_Vel[:, 297]
Y1, Y100 = data_Vel[:, 1], data_Vel[:, 298]
Z1, Z100 = data_Vel[:, 2], data_Vel[:, 299]

# 图线颜色
colors = {
    'X1': '#320a72',    
    'X100': '#320a72',   
    'Y1': '#500f04',     
    'Y100': '#500f04',   
    'Z1': '#274400',     
    'Z100': '#274400'    
}

# 统一绘图参数
def plot_displacement(t, data, title, subplot_pos, color):
    plt.subplot(2, 3, subplot_pos)
    plt.plot(t, data, '-', linewidth=2.0, color = color)
    plt.xlim([0, 20])
    plt.ylim([-2.0, 2.0])
    plt.xticks(np.arange(0, 22.0, 2.0))
    plt.yticks(np.arange(-2.0, 2.50, 0.50))
    plt.title(title, fontsize=12)
    plt.xlabel("Time(s)")
    plt.ylabel("Velocity(m)")
    plt.grid(True, alpha=0.3)

# 绘图
plt.figure(figsize=(15, 8))

plot_displacement(t, Y1,    "Point01's  Velocity at in Y-direction", 2, colors['Y1'])
plot_displacement(t, Y100,  "Point100's Velocity at in Y-direction", 5, colors['Y100'])
plot_displacement(t, X1,    "Point01's  Velocity at in X-direction", 1, colors['X1'])
plot_displacement(t, X100,  "Point100's Velocity at in X-direction", 4, colors['X100'])
plot_displacement(t, Z1,    "Point01's  Velocity at in Z-direction", 3, colors['Z1'])
plot_displacement(t, Z100,  "Point100's Velocity at in Z-direction", 6, colors['Z100'])

plt.tight_layout()

output_filename = "Velocity_in_XYZ"
plt.savefig(f'output/Figures/{output_filename}.png', dpi=600, bbox_inches='tight', facecolor='white')
# plt.show()

print(f"Plot done! the Figures are saved as {output_filename}.png")