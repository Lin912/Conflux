import csv

start = 0
end = 20
step = 0.001

data = [round(i * step, 3) for i in range(int(start / step), int(end / step) + 1)]

with open('timestep.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    
    for value in data:
        writer.writerow([value])

print("CSV 文件生成成功！")
 
