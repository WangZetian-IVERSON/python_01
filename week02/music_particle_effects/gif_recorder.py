"""
GIF录制版本 - 自动录制粒子特效动画
"""
import pygame
import sys
import time
import math
import random
import os

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
            
            # 简单发光效果
            for i in range(2):
                glow_size = size + i * 2
                if glow_size > 0:
                    pygame.draw.circle(screen, self.color, (x, y), glow_size)
            
            # 核心
            pygame.draw.circle(screen, self.color, (x, y), size)

class QuickParticleSystem:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particles = []
        self.max_particles = 200  # 减少粒子数量以便录制
        
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
    
    def get_count(self):
        """获取活跃粒子数"""
        return len([p for p in self.particles if p.life > 0])

def main():
    """主函数 - GIF录制版本"""
    print("开始录制粒子特效 GIF...")
    
    # 初始化Pygame
    pygame.init()
    width, height = 800, 600  # 较小的尺寸便于制作GIF
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("音乐粒子特效 - GIF录制")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # 创建粒子系统
    particle_system = QuickParticleSystem(width, height)
    
    # 录制参数
    frames = []
    recording_duration = 6  # 录制6秒
    frame_count = 0
    max_frames = recording_duration * 30  # 30 FPS
    
    # 自动节拍参数
    last_beat = 0
    beat_interval = 0.8  # 节拍间隔
    beat_intensity_cycle = 0
    
    start_time = time.time()
    
    while frame_count < max_frames:
        dt = clock.tick(30) / 1000.0  # 30 FPS
        current_time = time.time() - start_time
        
        # 自动节拍
        if current_time - last_beat > beat_interval:
            beat_intensity_cycle += 1
            intensity = 1.2 + 0.8 * math.sin(beat_intensity_cycle * 0.3)
            particle_system.beat_response(intensity)
            last_beat = current_time
            
            # 变化节拍间隔
            beat_interval = random.uniform(0.6, 1.2)
        
        # 更新
        particle_system.update(dt)
        
        # 绘制
        screen.fill((8, 8, 25))  # 深色背景
        
        # 绘制粒子
        particle_system.draw(screen)
        
        # 添加标题
        title_text = "Music Particle Effects"
        title_surface = font.render(title_text, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(width//2, 30))
        screen.blit(title_surface, title_rect)
        
        # 添加副标题
        subtitle_text = "Beat-Responsive Particle Visualization"
        subtitle_surface = font.render(subtitle_text, True, (200, 200, 200))
        subtitle_rect = subtitle_surface.get_rect(center=(width//2, 55))
        screen.blit(subtitle_surface, subtitle_rect)
        
        pygame.display.flip()
        
        # 保存帧
        if frame_count % 2 == 0:  # 每隔一帧保存，减少文件大小
            frame_surface = screen.copy()
            frames.append(pygame.surfarray.array3d(frame_surface))
        
        frame_count += 1
        
        # 显示进度
        progress = frame_count / max_frames
        if frame_count % 30 == 0:  # 每秒显示一次进度
            print(f"录制进度: {progress*100:.1f}%")
    
    pygame.quit()
    
    # 保存为GIF
    print("正在生成 GIF...")
    try:
        from PIL import Image
        import numpy as np
        
        # 转换帧格式
        pil_frames = []
        for frame in frames:
            # pygame的数组是(width, height, 3)，需要转置为(height, width, 3)
            frame_transposed = np.transpose(frame, (1, 0, 2))
            pil_frame = Image.fromarray(frame_transposed.astype('uint8'))
            pil_frames.append(pil_frame)
        
        # 保存GIF
        gif_path = "music_particle_effects.gif"
        pil_frames[0].save(
            gif_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=66,  # 约15 FPS
            loop=0,
            optimize=True
        )
        
        print(f"GIF 已保存到: {gif_path}")
        print(f"总帧数: {len(pil_frames)}")
        
    except ImportError:
        print("需要安装 Pillow 库来生成 GIF")
        print("请运行: pip install Pillow")
        
        # 保存帧为PNG文件
        print("保存帧为 PNG 文件...")
        for i, frame in enumerate(frames):
            frame_transposed = np.transpose(frame, (1, 0, 2))
            pygame.image.save(pygame.surfarray.make_surface(frame), f"frame_{i:03d}.png")
        print(f"已保存 {len(frames)} 个 PNG 帧")

if __name__ == "__main__":
    main()