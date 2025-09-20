"""
简化测试版本 - 音乐粒子特效
"""
import pygame
import sys
import random
import math
import time

# 初始化Pygame
pygame.init()

# 设置窗口
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("音乐粒子特效 - 演示版")
clock = pygame.time.Clock()

class SimpleParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # 朝右上角移动
        angle = random.uniform(-0.3, 0.3) - math.pi/4  # -45度 ± 偏移
        speed = random.uniform(1, 3)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.size = random.uniform(2, 8)
        self.original_size = self.size
        self.color = [random.randint(100, 255) for _ in range(3)]
        self.life = 1.0
        self.pulse = 1.0
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.02  # 轻微重力
        self.life -= 0.005
        self.pulse = 1.0 + 0.2 * math.sin(time.time() * 10)
        self.size = self.original_size * self.pulse * self.life
        
    def beat_pulse(self):
        self.pulse *= 2
        self.vx += random.uniform(-0.5, 0.5)
        self.vy += random.uniform(-0.5, 0.5)
        
    def draw(self, screen):
        if self.life > 0 and self.size > 0:
            alpha = int(255 * self.life)
            color = (*self.color, alpha)
            
            # 绘制发光效果
            for i in range(3):
                glow_size = int(self.size + i * 2)
                if glow_size > 0:
                    glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                    glow_alpha = alpha // (i + 2)
                    pygame.draw.circle(glow_surface, (*self.color, glow_alpha), 
                                     (glow_size, glow_size), glow_size)
                    screen.blit(glow_surface, (self.x - glow_size, self.y - glow_size))

def main():
    particles = []
    last_beat = 0
    beat_interval = 0.5  # 每0.5秒一个节拍
    
    print("音乐粒子特效演示")
    print("按SPACE手动触发节拍效果")
    print("按ESC退出")
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time()
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 手动触发节拍
                    last_beat = current_time
                    
                    # 生成粒子
                    for _ in range(10):
                        start_x = random.uniform(0, WIDTH * 0.1)
                        start_y = random.uniform(HEIGHT * 0.8, HEIGHT)
                        particles.append(SimpleParticle(start_x, start_y))
                    
                    # 触发现有粒子的脉冲
                    for particle in particles:
                        particle.beat_pulse()
        
        # 自动节拍
        if current_time - last_beat > beat_interval:
            last_beat = current_time
            
            # 生成粒子
            for _ in range(5):
                start_x = random.uniform(0, WIDTH * 0.1)
                start_y = random.uniform(HEIGHT * 0.8, HEIGHT)
                particles.append(SimpleParticle(start_x, start_y))
        
        # 更新粒子
        particles = [p for p in particles if p.life > 0 and 
                    p.x > -50 and p.x < WIDTH + 50 and 
                    p.y > -50 and p.y < HEIGHT + 50]
        
        for particle in particles:
            particle.update()
        
        # 绘制
        screen.fill((5, 5, 15))  # 深色背景
        
        # 绘制轨迹淡化
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.set_alpha(20)
        fade_surface.fill((5, 5, 15))
        screen.blit(fade_surface, (0, 0))
        
        # 绘制粒子
        for particle in particles:
            particle.draw(screen)
        
        # 绘制信息
        font = pygame.font.Font(None, 36)
        info_text = f"粒子数量: {len(particles)} | 按SPACE触发节拍 | ESC退出"
        text_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()