from PIL import Image, ImageDraw
import numpy as np
import random

# 画布尺寸
CANVAS_WIDTH, CANVAS_HEIGHT = 960, 540
# GIF帧率
FPS = 12  # 降低帧率从60到12
# 动画持续时间（秒）
DURATION = 10
# 总帧数
TOTAL_FRAMES = FPS * DURATION
# 山峦层数
MOUNTAIN_LAYERS = 340
# 颜色映射，模拟水墨渐变，从深到浅
INK_COLOR_MAP = [(i, i, i) for i in range(50, 255, 8)]  # 从更亮的颜色开始

# 模拟心率数据，简单的周期性变化模拟
heart_rate_data = []
base_heart_rates = [60, 70, 80]
for _ in range(TOTAL_FRAMES):
    heart_rate = random.choice(base_heart_rates)
    heart_rate_data.append(heart_rate)

# 定义波形参数映射函数，控制山峦起伏幅度和频率
def map_amplitude(heart_rate):
    return np.interp(heart_rate, [60, 80], [20, 40])  # 修正心率范围并增加振幅
def map_frequency(heart_rate):
    return np.interp(heart_rate, [60, 80], [0.01, 0.03])  # 修正心率范围

# 生成随机的山峦基础高度，从下到上逐渐降低
base_heights = []
bottom_height = CANVAS_HEIGHT * 0.6  # 从更低的位置开始，确保山峦可见
for _ in range(MOUNTAIN_LAYERS):
    height = bottom_height - random.uniform(0, CANVAS_HEIGHT * 0.02)  # 减小高度差
    base_heights.append(max(height, CANVAS_HEIGHT * 0.1))  # 确保不超出画布上边界
    bottom_height = height

# 生成每一帧的函数
def generate_frame(frame_index):
    img = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    heart_rate = heart_rate_data[frame_index]
    amplitude = map_amplitude(heart_rate)
    frequency = map_frequency(heart_rate)

    for layer in range(MOUNTAIN_LAYERS):
        base_y = base_heights[layer]
        x_coords = np.arange(CANVAS_WIDTH)
        # 增加更多随机扰动，让山峦形态更自然
        offset = random.uniform(-5, 5)  # 减小偏移范围
        phase = frame_index * 0.02 + layer * 0.1 + offset  # 恢复合适的相位变化速度
        y_coords = base_y + amplitude * np.sin(frequency * x_coords + phase)
        y_coords = np.clip(y_coords, 0, CANVAS_HEIGHT)
        color_index = min(layer * (len(INK_COLOR_MAP) // MOUNTAIN_LAYERS), len(INK_COLOR_MAP) - 1)  # 防止索引越界
        color = INK_COLOR_MAP[color_index]
        # 使用更多控制点绘制曲线，让线条更平滑
        num_control_points = 30
        control_x = np.linspace(0, CANVAS_WIDTH, num_control_points)
        control_y = np.interp(control_x, x_coords, y_coords)
        smooth_x = np.linspace(0, CANVAS_WIDTH, CANVAS_WIDTH)
        smooth_y = np.interp(smooth_x, control_x, control_y)
        for i in range(len(smooth_x) - 1):
            draw.line([(smooth_x[i], smooth_y[i]), (smooth_x[i + 1], smooth_y[i + 1])], fill=color, width=2)

    return img

# 生成所有帧
frames = [generate_frame(i) for i in range(TOTAL_FRAMES)]
# 保存为GIF
frames[0].save('adjusted_water_ink_mountain_animation.gif', save_all=True, append_images=frames[1:], loop=0, duration=1000 // FPS * 20)  # 增加duration，让每帧停留更久
