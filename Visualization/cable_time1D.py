import csv
import os

start = 0
end = 20
step = 0.001

os.makedirs('Timestep_axis', exist_ok=True)
data = [round(i * step, 3) for i in range(int(start / step), int(end / step) + 1)]

with open('Timestep_axis/timestep.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    
    for value in data:
        writer.writerow([value])

print("CSV geted!!")
 
