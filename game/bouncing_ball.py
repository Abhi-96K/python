import pygame
import sys
import math
import random
import os

pygame.init()
WIDTH, HEIGHT =1200,1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

try:
    bounce_sound = pygame.mixer.Sound("bounce.wav")
except:
    bounce_sound = None
    print("⚠️ 'bounce.wav' not found — sound disabled.")

WHITE = (255, 255, 255)

circle_center = (WIDTH // 2, HEIGHT // 2)
circle_radius = 200
rotation_angle = 0
escape_width_deg = 90

class Ball:
    def __init__(self):
        angle = random.uniform(0, 2 * math.pi)
        r = random.uniform(0, circle_radius - 20)
        self.x = circle_center[0] + r * math.cos(angle)
        self.y = circle_center[1] + r * math.sin(angle)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.radius = 10
        self.color = [random.randint(50, 255) for _ in range(3)]

    def update(self):
        self.x += self.vx
        self.y += self.vy
        dx = self.x - circle_center[0]
        dy = self.y - circle_center[1]
        dist = math.hypot(dx, dy)

        if dist + self.radius > circle_radius:
            angle = math.atan2(dy, dx)
            speed = math.hypot(self.vx, self.vy)
            incoming_angle = math.atan2(self.vy, self.vx)
            reflect_angle = 2 * angle - incoming_angle
            self.vx = -speed * math.cos(reflect_angle)
            self.vy = -speed * math.sin(reflect_angle)

            new_speed = math.hypot(self.vx, self.vy)
            if new_speed != 0:
                scale = speed / new_speed
                self.vx *= scale
                self.vy *= scale

            if bounce_sound:
                bounce_sound.play()

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

    def check_escape(self, rot_angle_deg):
        dx = self.x - circle_center[0]
        dy = self.y - circle_center[1]
        dist = math.hypot(dx, dy)

        if dist + self.radius >= circle_radius:
            ball_angle = (math.degrees(math.atan2(dy, dx)) - rot_angle_deg) % 360
            if ball_angle < escape_width_deg or ball_angle > 360 - escape_width_deg:
                return True
        return False

def check_ball_collisions(ball_list):
    for i in range(len(ball_list)):
        for j in range(i + 1, len(ball_list)):
            b1 = ball_list[i]
            b2 = ball_list[j]
            dx = b2.x - b1.x
            dy = b2.y - b1.y
            dist = math.hypot(dx, dy)
            if dist < b1.radius + b2.radius and dist != 0:

                nx = dx / dist
                ny = dy / dist


                tx = -ny
                ty = nx

                dpTan1 = b1.vx * tx + b1.vy * ty
                dpTan2 = b2.vx * tx + b2.vy * ty

                dpNorm1 = b1.vx * nx + b1.vy * ny
                dpNorm2 = b2.vx * nx + b2.vy * ny

                b1_vn = dpNorm2
                b2_vn = dpNorm1

                b1.vx = tx * dpTan1 + nx * b1_vn
                b1.vy = ty * dpTan1 + ny * b1_vn
                b2.vx = tx * dpTan2 + nx * b2_vn
                b2.vy = ty * dpTan2 + ny * b2_vn

                overlap = 0.5 * (b1.radius + b2.radius - dist + 1)
                b1.x -= overlap * nx
                b1.y -= overlap * ny
                b2.x += overlap * nx
                b2.y += overlap * ny

                if bounce_sound:
                    bounce_sound.play()

balls = [Ball()]

while True:
    screen.fill((0, 0, 0))
    dt = clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    rotation_angle = (rotation_angle + 1) % 360

    pygame.draw.circle(screen, WHITE, circle_center, circle_radius, 2)

    gap_angle_start = math.radians(rotation_angle - escape_width_deg / 2)
    gap_angle_end = math.radians(rotation_angle + escape_width_deg / 2)
    pygame.draw.arc(screen, (0, 0, 0),
        [circle_center[0] - circle_radius, circle_center[1] - circle_radius, 2 * circle_radius, 2 * circle_radius],
        gap_angle_start, gap_angle_end, 6)

    new_balls = []
    for ball in balls[:]:
        ball.update()
        if ball.check_escape(rotation_angle):
            balls.remove(ball)
            new_balls.extend([Ball(), Ball(),Ball(),Ball()])
        else:
            ball.draw()

    check_ball_collisions(balls)

    balls.extend(new_balls)

    pygame.display.flip()