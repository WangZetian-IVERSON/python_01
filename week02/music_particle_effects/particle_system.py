"""
粒子系统 - 实现粒子的生成、更新和管理
"""
import numpy as np
import random
import math

class Particle:
    def __init__(self, x, y, vx=0, vy=0, size=2, color=(255, 255, 255), life=1.0):
        """
        初始化粒子
        :param x, y: 初始位置
        :param vx, vy: 初始速度
        :param size: 粒子大小
        :param color: 粒子颜色 (R, G, B)
        :param life: 粒子生命值 (0-1)
        """
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.original_size = size
        self.color = color
        self.life = life
        self.max_life = life
        self.age = 0
        self.is_alive = True
        
        # 粒子效果属性
        self.pulse_scale = 1.0  # 脉冲缩放
        self.pulse_speed = 0.1  # 脉冲速度
        self.gravity = 0.1  # 重力
        self.friction = 0.98  # 摩擦力
        
    def update(self, dt=1.0):
        """更新粒子状态"""
        if not self.is_alive:
            return
        
        # 更新位置
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # 应用重力和摩擦
        self.vy += self.gravity * dt
        self.vx *= self.friction
        self.vy *= self.friction
        
        # 更新生命值
        self.age += dt
        self.life = max(0, self.max_life - self.age * 0.01)
        
        # 更新脉冲效果
        self.pulse_scale = 1.0 + 0.3 * math.sin(self.age * self.pulse_speed)
        
        # 更新大小（随生命值衰减）
        self.size = self.original_size * self.pulse_scale * (self.life ** 0.5)
        
        # 检查是否死亡
        if self.life <= 0 or self.size <= 0.1:
            self.is_alive = False
    
    def beat_pulse(self, intensity=2.0):
        """节拍脉冲效果"""
        self.pulse_scale *= intensity
        self.size = self.original_size * self.pulse_scale * (self.life ** 0.5)
        
        # 添加随机速度扰动
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 2.0) * intensity
        self.vx += math.cos(angle) * speed
        self.vy += math.sin(angle) * speed

class ParticleSystem:
    def __init__(self, width=800, height=600):
        """
        初始化粒子系统
        :param width, height: 画布尺寸
        """
        self.width = width
        self.height = height
        self.particles = []
        self.max_particles = 1000
        
        # 粒子生成参数
        self.spawn_rate = 5  # 每次生成的粒子数
        self.base_speed = 2.0
        self.color_palette = [
            (255, 100, 100),  # 红色
            (100, 255, 100),  # 绿色
            (100, 100, 255),  # 蓝色
            (255, 255, 100),  # 黄色
            (255, 100, 255),  # 紫色
            (100, 255, 255),  # 青色
            (255, 255, 255),  # 白色
        ]
        
    def add_particle(self, x, y, vx=0, vy=0, size=None, color=None):
        """添加单个粒子"""
        if len(self.particles) >= self.max_particles:
            return
        
        if size is None:
            size = random.uniform(2, 8)
        if color is None:
            color = random.choice(self.color_palette)
        
        particle = Particle(x, y, vx, vy, size, color, life=random.uniform(0.8, 1.0))
        self.particles.append(particle)
    
    def spawn_particles_at_beat(self, beat_intensity=1.0):
        """在节拍点生成粒子"""
        # 从左下角开始生成粒子
        start_x = random.uniform(0, self.width * 0.1)
        start_y = random.uniform(self.height * 0.8, self.height)
        
        # 计算朝向右上角的方向
        target_x = random.uniform(self.width * 0.8, self.width)
        target_y = random.uniform(0, self.height * 0.2)
        
        # 计算方向向量
        dx = target_x - start_x
        dy = target_y - start_y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # 生成多个粒子
        num_particles = int(self.spawn_rate * beat_intensity)
        for _ in range(num_particles):
            # 添加一些随机偏移
            offset_x = random.uniform(-50, 50)
            offset_y = random.uniform(-50, 50)
            
            # 计算速度
            speed = self.base_speed * random.uniform(0.5, 1.5) * beat_intensity
            angle_offset = random.uniform(-0.3, 0.3)  # 添加角度偏移
            
            final_dx = dx * math.cos(angle_offset) - dy * math.sin(angle_offset)
            final_dy = dx * math.sin(angle_offset) + dy * math.cos(angle_offset)
            
            vx = final_dx * speed
            vy = final_dy * speed
            
            # 根据节拍强度选择颜色和大小
            color_intensity = min(255, int(128 + 127 * beat_intensity))
            color = (color_intensity, 
                    random.randint(100, color_intensity), 
                    random.randint(100, color_intensity))
            
            size = random.uniform(3, 8) * beat_intensity
            
            self.add_particle(
                start_x + offset_x, 
                start_y + offset_y, 
                vx, vy, 
                size, 
                color
            )
    
    def update(self, dt=1.0):
        """更新所有粒子"""
        # 更新现有粒子
        for particle in self.particles[:]:  # 创建副本以安全删除
            particle.update(dt)
            
            # 移除死亡或超出边界的粒子
            if (not particle.is_alive or 
                particle.x < -50 or particle.x > self.width + 50 or
                particle.y < -50 or particle.y > self.height + 50):
                self.particles.remove(particle)
    
    def beat_response(self, beat_intensity=1.0):
        """节拍响应 - 让现有粒子产生脉冲"""
        for particle in self.particles:
            if particle.is_alive:
                particle.beat_pulse(beat_intensity)
        
        # 生成新粒子
        self.spawn_particles_at_beat(beat_intensity)
    
    def get_particles(self):
        """获取所有活跃粒子"""
        return [p for p in self.particles if p.is_alive]
    
    def clear(self):
        """清空所有粒子"""
        self.particles.clear()
    
    def get_particle_count(self):
        """获取活跃粒子数量"""
        return len([p for p in self.particles if p.is_alive])

if __name__ == "__main__":
    # 测试代码
    import time
    
    particle_system = ParticleSystem(800, 600)
    
    print("测试粒子系统...")
    
    # 模拟几个节拍
    for i in range(5):
        print(f"节拍 {i+1}")
        particle_system.beat_response(random.uniform(0.5, 2.0))
        
        # 模拟几帧更新
        for j in range(10):
            particle_system.update()
            time.sleep(0.01)
        
        print(f"当前粒子数: {particle_system.get_particle_count()}")
    
    print("测试完成!")