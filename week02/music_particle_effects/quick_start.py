"""
快速启动版本 - 音乐粒子特效
不使用librosa，直接使用简单的节拍生成
"""
import pygame
import sys
import time
import math
import random

# 简化的粒子类
class QuickParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # 朝右上角移动，增加初始速度
        angle = random.uniform(-0.6, 0.3) - math.pi/4  # 增加角度变化范围
        speed = random.uniform(2.5, 6)  # 增加初始速度
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        self.size = random.uniform(2, 10)
        self.original_size = self.size
        self.color = random.choice([
            (255, 100, 100),  # 红
            (100, 255, 100),  # 绿
            (100, 150, 255),  # 蓝
            (255, 255, 100),  # 黄
            (255, 100, 255),  # 紫
            (100, 255, 255),  # 青
            (255, 255, 255),  # 白
        ])
        self.life = 3.0  # 增加生存时间
        self.pulse = 1.0
        
    def update(self, dt):
        self.x += self.vx * dt * 60
        self.y += self.vy * dt * 60
        self.vy += 0.02  # 减少重力，让粒子飞得更远
        self.vx *= 0.9995  # 减少阻力
        self.vy *= 0.9995
        
        self.life -= dt * 0.4  # 减慢生命消耗
        self.pulse = 1.0 + 0.3 * math.sin(time.time() * 8)
        self.size = self.original_size * self.pulse * max(0, self.life)
        
    def beat_pulse(self, intensity=1.5):
        self.pulse *= intensity
        self.size = self.original_size * self.pulse * self.life
        # 添加随机扰动
        self.vx += random.uniform(-1, 1) * intensity
        self.vy += random.uniform(-1, 1) * intensity
        
    def draw(self, screen):
        if self.life > 0 and self.size > 0:
            x, y = int(self.x), int(self.y)
            size = max(1, int(self.size))
            alpha = max(0, min(255, int(255 * self.life)))
            
            # 简单发光效果
            for i in range(2):
                glow_size = size + i * 2
                if glow_size > 0:
                    # 直接使用颜色，不使用alpha通道
                    pygame.draw.circle(screen, self.color, (x, y), glow_size)
            
            # 核心
            pygame.draw.circle(screen, self.color, (x, y), size)

class QuickParticleSystem:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.max_particles = 300
        
    def spawn_particles(self, intensity=1.0):
        """生成粒子"""
        count = int(12 * intensity)  # 增加粒子数量
        for _ in range(count):
            # 扩大生成区域，不只是左下角
            start_x = random.uniform(0, self.width * 0.25)  # 扩大X范围
            start_y = random.uniform(self.height * 0.6, self.height)  # 扩大Y范围
            self.particles.append(QuickParticle(start_x, start_y))
        
        # 限制粒子数量
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]
    
    def beat_response(self, intensity=1.5):
        """节拍响应"""
        # 让现有粒子脉冲
        for particle in self.particles:
            if particle.life > 0:
                particle.beat_pulse(intensity)
        
        # 生成新粒子
        self.spawn_particles(intensity)
    
    def update(self, dt):
        """更新粒子"""
        # 更宽松的边界条件，让粒子飞到屏幕中间再清理
        self.particles = [p for p in self.particles if 
                         p.life > 0 and 
                         p.x > -100 and p.x < self.width + 100 and
                         p.y > -100 and p.y < self.height + 100]
        
        for particle in self.particles:
            particle.update(dt)
    
    def draw(self, screen):
        """绘制所有粒子"""
        for particle in self.particles:
            particle.draw(screen)
    
    def clear(self):
        """清空粒子"""
        self.particles.clear()
    
    def get_count(self):
        """获取活跃粒子数"""
        return len([p for p in self.particles if p.life > 0])

def main():
    """主函数"""
    print("快速启动音乐粒子特效...")
    
    # 初始化Pygame
    pygame.init()
    width, height = 1000, 700
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("音乐粒子特效 - 快速版")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # 创建粒子系统
    particle_system = QuickParticleSystem(width, height)
    
    # 自动节拍参数
    last_beat = 0
    beat_interval = 0.6  # 节拍间隔
    beat_intensity_cycle = 0
    
    print("启动成功!")
    print("控制:")
    print("- SPACE: 手动节拍")
    print("- C: 清空粒子")
    print("- ESC: 退出")
    
    running = True
    start_time = time.time()
    
    while running:
        dt = clock.tick(60) / 1000.0
        current_time = time.time() - start_time
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    particle_system.beat_response(2.0)
                    print("手动节拍触发!")
                elif event.key == pygame.K_c:
                    particle_system.clear()
                    print("粒子已清空")
        
        # 自动节拍
        if current_time - last_beat > beat_interval:
            beat_intensity_cycle += 1
            intensity = 1.0 + 0.5 * math.sin(beat_intensity_cycle * 0.3)
            particle_system.beat_response(intensity)
            last_beat = current_time
            
            # 变化节拍间隔
            beat_interval = random.uniform(0.4, 0.8)
        
        # 更新
        particle_system.update(dt)
        
        # 绘制
        screen.fill((5, 5, 15))  # 深色背景
        
        # 绘制粒子
        particle_system.draw(screen)
        
        # UI信息
        info_text = f"粒子: {particle_system.get_count()} | 时间: {current_time:.1f}s | SPACE:节拍 ESC:退出"
        text_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(text_surface, (10, 10))
        
        # 显示FPS
        fps_text = f"FPS: {int(clock.get_fps())}"
        fps_surface = font.render(fps_text, True, (100, 255, 100))
        screen.blit(fps_surface, (10, 50))
        
        pygame.display.flip()
    
    pygame.quit()
    print("程序结束")

if __name__ == "__main__":
    main()