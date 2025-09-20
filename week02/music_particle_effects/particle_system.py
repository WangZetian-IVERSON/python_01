"""
粒子系统模块
物理驱动的粒子效果和渲染
"""
import pygame
import math
import random
import time
from typing import List, Tuple

class Particle:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        
        # 运动参数
        angle = random.uniform(-math.pi/3, math.pi/6) - math.pi/4  # 大致朝右上角
        speed = random.uniform(50, 150)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        # 外观参数
        self.size = random.uniform(2, 8)
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
        
        # 生命周期
        self.life = 1.0
        self.max_life = 1.0
        self.decay_rate = random.uniform(0.3, 0.7)
        
        # 特效参数
        self.pulse = 1.0
        self.pulse_phase = random.uniform(0, 2 * math.pi)
        self.trail_positions = []
        
    def update(self, dt: float, gravity: float = 30, friction: float = 0.98):
        """更新粒子状态"""
        # 物理运动
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # 重力和阻力
        self.vy += gravity * dt
        self.vx *= friction
        self.vy *= friction
        
        # 生命周期
        self.life -= self.decay_rate * dt
        
        # 脉冲效果
        self.pulse = 1.0 + 0.2 * math.sin(time.time() * 8 + self.pulse_phase)
        
        # 尺寸随生命周期变化
        life_factor = max(0, self.life / self.max_life)
        self.size = self.original_size * self.pulse * life_factor
        
        # 轨迹记录
        self.trail_positions.append((self.x, self.y))
        if len(self.trail_positions) > 10:
            self.trail_positions.pop(0)
    
    def beat_pulse(self, intensity: float = 2.0):
        """节拍脉冲效果"""
        self.pulse *= intensity
        self.size = self.original_size * self.pulse * (self.life / self.max_life)
        
        # 添加随机扰动
        impulse = intensity * 20
        self.vx += random.uniform(-impulse, impulse)
        self.vy += random.uniform(-impulse, impulse)
        
        # 延长生命
        self.life = min(self.max_life, self.life + 0.1 * intensity)
    
    def draw(self, screen: pygame.Surface, draw_trail: bool = True):
        """绘制粒子"""
        if self.life <= 0:
            return
        
        # 绘制轨迹
        if draw_trail and len(self.trail_positions) > 1:
            for i, (tx, ty) in enumerate(self.trail_positions[:-1]):
                alpha = (i / len(self.trail_positions)) * (self.life / self.max_life) * 0.5
                trail_size = max(1, int(self.size * alpha))
                if trail_size > 0:
                    trail_color = tuple(int(c * alpha) for c in self.color)
                    pygame.draw.circle(screen, trail_color, (int(tx), int(ty)), trail_size)
        
        # 绘制主体
        if self.size > 0:
            x, y = int(self.x), int(self.y)
            size = max(1, int(self.size))
            
            # 发光效果
            alpha = self.life / self.max_life
            for i in range(3):
                glow_size = size + i * 2
                if glow_size > 0:
                    glow_alpha = alpha / (i + 1)
                    glow_color = tuple(int(c * glow_alpha) for c in self.color)
                    pygame.draw.circle(screen, glow_color, (x, y), glow_size)
            
            # 核心
            pygame.draw.circle(screen, self.color, (x, y), size)
    
    def is_alive(self) -> bool:
        """检查粒子是否存活"""
        return self.life > 0

class ParticleSystem:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.particles: List[Particle] = []
        self.max_particles = 500
        
        # 物理参数
        self.gravity = 30
        self.friction = 0.98
        
        # 生成参数
        self.spawn_rate = 5  # 每秒生成的粒子数
        self.spawn_accumulator = 0.0
        
        # 效果参数
        self.beat_response_time = 0.0
        self.background_spawn = True
        
    def update(self, dt: float):
        """更新粒子系统"""
        # 背景粒子生成
        if self.background_spawn:
            self.spawn_accumulator += dt
            if self.spawn_accumulator >= 1.0 / self.spawn_rate:
                self.spawn_particle()
                self.spawn_accumulator = 0.0
        
        # 更新所有粒子
        for particle in self.particles:
            particle.update(dt, self.gravity, self.friction)
        
        # 移除死亡和越界的粒子
        self.particles = [p for p in self.particles if 
                         p.is_alive() and 
                         p.x > -50 and p.x < self.width + 50 and
                         p.y > -50 and p.y < self.height + 50]
        
        # 限制粒子数量
        if len(self.particles) > self.max_particles:
            self.particles = self.particles[-self.max_particles:]
        
        # 更新节拍响应时间
        self.beat_response_time = max(0, self.beat_response_time - dt)
    
    def spawn_particle(self, x: float = None, y: float = None) -> Particle:
        """生成单个粒子"""
        if x is None:
            x = random.uniform(0, self.width * 0.2)
        if y is None:
            y = random.uniform(self.height * 0.7, self.height)
        
        particle = Particle(x, y)
        self.particles.append(particle)
        return particle
    
    def spawn_particles(self, count: int, x: float = None, y: float = None):
        """生成多个粒子"""
        for _ in range(count):
            spawn_x = x if x is not None else random.uniform(0, self.width * 0.3)
            spawn_y = y if y is not None else random.uniform(self.height * 0.6, self.height)
            self.spawn_particle(spawn_x, spawn_y)
    
    def beat_response(self, intensity: float = 1.5):
        """节拍响应"""
        self.beat_response_time = 0.5  # 响应持续时间
        
        # 对现有粒子施加脉冲
        for particle in self.particles:
            if particle.is_alive():
                particle.beat_pulse(intensity)
        
        # 生成新粒子
        count = int(10 * intensity)
        self.spawn_particles(count)
        
        print(f"节拍响应: 强度 {intensity:.2f}, 生成 {count} 个粒子")
    
    def onset_response(self, intensity: float = 1.2):
        """音符开始响应"""
        # 生成少量粒子
        count = int(5 * intensity)
        self.spawn_particles(count)
    
    def draw(self, screen: pygame.Surface, draw_trails: bool = True):
        """绘制所有粒子"""
        for particle in self.particles:
            particle.draw(screen, draw_trails)
    
    def clear(self):
        """清空所有粒子"""
        self.particles.clear()
        print("粒子系统已清空")
    
    def get_particle_count(self) -> int:
        """获取活跃粒子数量"""
        return len([p for p in self.particles if p.is_alive()])
    
    def set_gravity(self, gravity: float):
        """设置重力"""
        self.gravity = gravity
    
    def set_spawn_rate(self, rate: float):
        """设置生成速率"""
        self.spawn_rate = max(0, rate)
    
    def set_background_spawn(self, enabled: bool):
        """设置是否背景生成粒子"""
        self.background_spawn = enabled
    
    def get_stats(self) -> dict:
        """获取统计信息"""
        alive_particles = [p for p in self.particles if p.is_alive()]
        return {
            'total_particles': len(self.particles),
            'alive_particles': len(alive_particles),
            'average_life': sum(p.life for p in alive_particles) / len(alive_particles) if alive_particles else 0,
            'beat_response_active': self.beat_response_time > 0
        }