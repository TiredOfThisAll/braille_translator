import matplotlib.pyplot as plt

with open("results_resnet.txt") as file:
    res = file.read().split("\n")

points_x = []
points_y = []
value = 0

for label in res:
    points_y.append(float(label.split()[5]))
    points_x.append(value)
    value += 1

plt.figure((46000))
plt.plot(points_x, points_y, color='blue')  # Построение точек
plt.xlabel('Epoch / 8')  # Название оси X
plt.ylabel('Loss')  # Название оси Y
plt.title('Процес навчання')  # Заголовок графика
plt.grid(True)  # Добавление сетки на график (по желанию)
plt.show()  # Показать график