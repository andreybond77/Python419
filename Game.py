import pygame
import random

# Инициализация Pygame
pygame.init()

# Параметры экрана
screen_width = 640
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))

# Цвета
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
black = (0, 0, 0)
yellow = (255, 255, 0)

# Шрифт для отображения счетчика
font = pygame.font.Font(None, 36)

# Параметры шара
circle_radius = 20
circle_speed = 1
initial_collision_counter = 9  # Начальное значение счетчика столкновений

# Список для хаотически движущихся шаров
moving_circles = []
for _ in range(10):  # Создаем 10 хаотически движущихся шаров
    color = random.choice([red, green, blue])
    pos = [random.randint(circle_radius, screen_width - circle_radius),
           random.randint(circle_radius, screen_height - circle_radius)]
    speed = [random.choice([-1, 1]) * circle_speed,
             random.choice([-1, 1]) * circle_speed]
    moving_circles.append({
        "pos": pos,
        "speed": speed,
        "color": color,
        "counter": initial_collision_counter,  # Счетчик столкновений
        "last_distance": float("inf")  # Расстояние до последнего сближения
    })

# Параметры желтого шара, управляемого игроком
player_circle_pos = [random.randint(circle_radius, screen_width - circle_radius),
                     random.randint(circle_radius, screen_height - circle_radius)]
player_circle_color = yellow

# Основной игровой цикл
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Управление желтым шаром
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_circle_pos[0] - circle_radius > 0:
        player_circle_pos[0] -= circle_speed
    if keys[pygame.K_RIGHT] and player_circle_pos[0] + circle_radius < screen_width:
        player_circle_pos[0] += circle_speed
    if keys[pygame.K_UP] and player_circle_pos[1] - circle_radius > 0:
        player_circle_pos[1] -= circle_speed
    if keys[pygame.K_DOWN] and player_circle_pos[1] + circle_radius < screen_height:
        player_circle_pos[1] += circle_speed

    # Движение хаотически движущихся шаров
    for circle in moving_circles:
        circle["pos"][0] += circle["speed"][0]
        circle["pos"][1] += circle["speed"][1]

        # Проверка на столкновение с границами экрана
        if circle["pos"][0] <= circle_radius or circle["pos"][0] >= screen_width - circle_radius:
            circle["speed"][0] *= -1
        if circle["pos"][1] <= circle_radius or circle["pos"][1] >= screen_height - circle_radius:
            circle["speed"][1] *= -1

    # Проверка столкновений между шарами
    to_remove = set()  # Множество для хранения индексов шаров, которые нужно удалить

    # Сначала проверяем столкновения
    for i in range(len(moving_circles)):
        for j in range(i + 1, len(moving_circles)):
            circle1 = moving_circles[i]
            circle2 = moving_circles[j]

            # Вычисляем текущее расстояние между шарами
            dx = circle2["pos"][0] - circle1["pos"][0]
            dy = circle2["pos"][1] - circle1["pos"][1]
            current_distance = (dx ** 2 + dy ** 2) ** 0.5

            # Если шары столкнулись
            if current_distance <= 2 * circle_radius:
                # Сохраняем текущее расстояние как "последнее сближение"
                circle1["last_distance"] = current_distance
                circle2["last_distance"] = current_distance

                # Изменяем скорость шаров при столкновении
                if abs(dx) > abs(dy):
                    circle1["speed"][0] *= -1
                    circle2["speed"][0] *= -1
                else:
                    circle1["speed"][1] *= -1
                    circle2["speed"][1] *= -1

            # Если шары расходятся после столкновения
            elif circle1["last_distance"] <= 2 * circle_radius and current_distance > 2 * circle_radius:
                color1, color2 = circle1["color"], circle2["color"]

                # Красный vs Зеленый: Уменьшаем счетчик зеленого, красный меняет скорость
                if color1 == red and color2 == green:
                    if circle2["counter"] > 0:
                        circle2["counter"] -= 1
                    if circle2["counter"] == 0:
                        to_remove.add(j)  # Удаляем зеленый шар, если его счетчик достиг 0

                # Зеленый vs Синий: Уменьшаем счетчик синего, зеленый меняет скорость
                elif color1 == green and color2 == blue:
                    if circle2["counter"] > 0:
                        circle2["counter"] -= 1
                    if circle2["counter"] == 0:
                        to_remove.add(j)  # Удаляем синий шар, если его счетчик достиг 0

                # Синий vs Красный: Уменьшаем счетчик красного, синий меняет скорость
                elif color1 == blue and color2 == red:
                    if circle1["counter"] > 0:
                        circle1["counter"] -= 1
                    if circle1["counter"] == 0:
                        to_remove.add(i)  # Удаляем красный шар, если его счетчик достиг 0

                # Обратные случаи (цвета поменяны местами)
                elif color1 == green and color2 == red:
                    if circle1["counter"] > 0:
                        circle1["counter"] -= 1
                    if circle1["counter"] == 0:
                        to_remove.add(i)  # Удаляем зеленый шар, если его счетчик достиг 0

                elif color1 == blue and color2 == green:
                    if circle1["counter"] > 0:
                        circle1["counter"] -= 1
                    if circle1["counter"] == 0:
                        to_remove.add(i)  # Удаляем синий шар, если его счетчик достиг 0

                elif color1 == red and color2 == blue:
                    if circle1["counter"] > 0:
                        circle1["counter"] -= 1
                    if circle1["counter"] == 0:
                        to_remove.add(i)  # Удаляем красный шар, если его счетчик достиг 0

                # Шары одного цвета: оба меняют скорость, но счетчики не уменьшаются
                elif color1 == color2:
                    pass  # Счетчики не изменяются

                # Сбрасываем последнее сохраненное расстояние
                circle1["last_distance"] = float("inf")
                circle2["last_distance"] = float("inf")

    # Удаляем шары после завершения проверки
    to_remove = sorted(to_remove, reverse=True)  # Сортируем индексы в обратном порядке
    for index in to_remove:
        if 0 <= index < len(moving_circles):
            moving_circles.pop(index)

    # Рисуем шары
    screen.fill(black)

    # Отрисовка всех шаров и их счетчиков
    for circle in moving_circles:
        pygame.draw.circle(screen, circle["color"], circle["pos"], circle_radius)

        # Отображение счетчика внутри шара
        text = font.render(str(circle["counter"]), True, white)
        text_rect = text.get_rect(center=(circle["pos"][0], circle["pos"][1]))
        screen.blit(text, text_rect)

    # Отрисовка игрока
    pygame.draw.circle(screen, player_circle_color, player_circle_pos, circle_radius)

    pygame.display.update()
    pygame.time.Clock().tick(60)

# Завершение игры
pygame.quit()







