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
data_new = np.zeros((20000, 300))

# 完全向量化的Simpson积分函数
def v_int_Sim_fully_vectorized(data):
    h = 0.001  # TimeStep
    n_points = data.shape[0]
    n_columns = data.shape[1]
    
    # 预分配结果数组
    result = np.zeros((n_points, n_columns))
    
    # 使用cumsum进行向量化积分计算
    for col in range(n_columns):
        # Simpson积分公式的向量化实现
        simpson_weights = np.ones(n_points)
        simpson_weights[1:-1:2] = 4  # 奇数索引点权重为4
        simpson_weights[2:-2:2] = 2  # 偶数索引点权重为2
        
        # 累积积分
        cumulative_integral = np.cumsum(data[:, col] * simpson_weights) * (h / 3)
        result[:, col] = cumulative_integral
    
    return result

# 完全向量化的梯形积分函数
def v_int_tra_fully_vectorized(data):
    h = 0.001  # TimeStep
    n_points = data.shape[0]
    n_columns = data.shape[1]
    
    # 预分配结果数组
    result = np.zeros((n_points, n_columns))
    
    for col in range(n_columns):
        # 梯形积分公式的向量化实现
        trapezoidal_weights = np.ones(n_points)
        trapezoidal_weights[0] = 0.5
        trapezoidal_weights[-1] = 0.5
        
        # 累积积分
        cumulative_integral = np.cumsum(data[:, col] * trapezoidal_weights) * h
        result[:, col] = cumulative_integral
    
    return result

print("Integraling...")

# 使用向量化函数计算所有列的积分
simpson_result = v_int_Sim_fully_vectorized(Tck)
trapezoidal_result = v_int_tra_fully_vectorized(Tck)

# 组合结果
data_new[2:, :] = simpson_result[2:, :]  # Simpson积分从第3个点开始
data_new[1, :] = trapezoidal_result[1, :]  # 第二个点用梯形积分
data_new[0, :] = 0  # 第一个点为0

print("Integral Over!")

# 时间轴生成
t = np.arange(0.001, 20.001, 0.001)  # TimeStep

# 提取数据绘图
X1, X100 = data_new[:, 0], data_new[:, 297]
Y1, Y100 = data_new[:, 1], data_new[:, 298]
Z1, Z100 = data_new[:, 2], data_new[:, 299]

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
    plt.plot(t, data, '-', linewidth=1.6, color = color)
    plt.xlim([0, 4])
    plt.ylim([-0.2, 0.2])
    plt.xticks(np.arange(0, 4.5, 0.5))
    plt.yticks(np.arange(-0.2, 0.25, 0.05))
    plt.title(title, fontsize=12)
    plt.xlabel("Time(s)")
    plt.ylabel("Displacement(m)")
    plt.grid(True, alpha=0.3)

# 绘图
plt.figure(figsize=(15, 8))

plot_displacement(t, Y1,    "Point01's  Displacement at in Y-direction", 2, colors['Y1'])
plot_displacement(t, Y100,  "Point100's Displacement at in Y-direction", 5, colors['Y100'])
plot_displacement(t, X1,    "Point01's  Displacement at in X-direction", 1, colors['X1'])
plot_displacement(t, X100,  "Point100's Displacement at in X-direction", 4, colors['X100'])
plot_displacement(t, Z1,    "Point01's  Displacement at in Z-direction", 3, colors['Z1'])
plot_displacement(t, Z100,  "Point100's Displacement at in Z-direction", 6, colors['Z100'])

plt.tight_layout()

output_filename = "Profile_in_XYZ"
plt.savefig(f'output/Figures/{output_filename}.png', dpi=600, bbox_inches='tight', facecolor='white')
# plt.show()

print(f"Plot done! the Figures are saved as {output_filename}.png")