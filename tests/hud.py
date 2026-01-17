import pygame
from dronekit import connect
import math
import time

# Araca bağlan
vehicle = connect('COM6',baud=57600 ,wait_ready=False, timeout=120, heartbeat_timeout=120)

# Pygame başlat
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("F-16 Style HUD")
font = pygame.font.SysFont("Consolas", 18)
clock = pygame.time.Clock()

def draw_text(text, x, y, color=(0, 255, 0)):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def draw_scale_bar(center_value, min_value, max_value, step, x_pos, y_center, width=60, height=300):
    # Şerit çizimi (örneğin hız ya da irtifa için)
    scale_range = list(range(int(center_value) - 5 * step, int(center_value) + 6 * step, step))
    top = y_center - height // 2
    pygame.draw.rect(screen, (0, 100, 0), (x_pos, top, width, height), 1)

    for i, val in enumerate(scale_range):
        y = y_center + (val - center_value) * -20
        if top < y < top + height:
            draw_text(str(val), x_pos + 5, int(y - 10))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    # Telemetri verileri
    altitude = vehicle.location.global_relative_frame.alt or 0
    groundspeed = vehicle.groundspeed or 0
    heading = vehicle.heading or 0
    battery = vehicle.battery.level or 0
    pitch = math.degrees(vehicle.attitude.pitch or 0)
    roll = math.degrees(vehicle.attitude.roll or 0)

    center_x, center_y = 400, 300

    # HUD Ortasında hedef çarprazı
    pygame.draw.line(screen, (0,255,0), (center_x - 10, center_y), (center_x + 10, center_y), 1)
    pygame.draw.line(screen, (0,255,0), (center_x, center_y - 10), (center_x, center_y + 10), 1)

    # Sol: Hız Şeridi
    draw_scale_bar(groundspeed, 0, 100, 5, 50, center_y)

    # Sağ: İrtifa Şeridi
    draw_scale_bar(altitude, 0, 1000, 10, 690, center_y)

    # Heading üstte
    draw_text(f"HDG: {heading:.0f}°", center_x - 40, 20)
    draw_text(f"BATT: {battery:.0f}%", center_x + 200, 20)

    # Yapay ufuk çizgisi (basit yatay çizgi)
    pitch_offset = pitch * 5
    pygame.draw.line(screen, (0,255,0),
                     (center_x - 100, center_y + pitch_offset),
                     (center_x + 100, center_y + pitch_offset), 2)

    pygame.display.flip()
    clock.tick(30)

vehicle.close()
pygame.quit()
