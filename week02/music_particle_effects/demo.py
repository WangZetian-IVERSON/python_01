"""
演示版本 - 音乐粒子特效
使用预设音频文件进行分析和可视化
"""
import pygame
import sys
import os
from audio_analyzer import AudioAnalyzer
from particle_system import ParticleSystem

def find_audio_file():
    """查找音频文件"""
    audio_dir = "audio"
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
        print(f"已创建 {audio_dir} 文件夹，请放入音频文件")
        return None
    
    # 支持的音频格式
    supported_formats = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
    
    audio_files = []
    for file in os.listdir(audio_dir):
        if any(file.lower().endswith(fmt) for fmt in supported_formats):
            audio_files.append(os.path.join(audio_dir, file))
    
    if not audio_files:
        print(f"在 {audio_dir} 文件夹中未找到音频文件")
        print(f"支持的格式: {', '.join(supported_formats)}")
        return None
    
    print(f"找到音频文件: {audio_files[0]}")
    return audio_files[0]

def main():
    """主函数"""
    print("音乐粒子特效演示版启动...")
    
    # 查找音频文件
    audio_file = find_audio_file()
    if not audio_file:
        print("请在 audio/ 文件夹中放入音频文件后重试")
        return
    
    # 初始化Pygame
    pygame.init()
    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("音乐粒子特效 - 演示版")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # 初始化音频分析器
    print("正在分析音频...")
    audio_analyzer = AudioAnalyzer(audio_file)
    if audio_analyzer.y is None:
        print("音频分析失败")
        return
    
    # 初始化粒子系统
    particle_system = ParticleSystem(width, height)
    particle_system.set_background_spawn(False)  # 关闭背景生成
    
    print("演示准备完成!")
    print("控制:")
    print("- SPACE: 开始/暂停播放")
    print("- R: 重新开始")
    print("- C: 清空粒子")
    print("- ESC: 退出")
    
    # 播放状态
    is_playing = False
    show_info = True
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        
        # 事件处理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    if is_playing:
                        audio_analyzer.stop_playback()
                        is_playing = False
                        print("暂停播放")
                    else:
                        audio_analyzer.start_playback()
                        is_playing = True
                        print("开始播放")
                elif event.key == pygame.K_r:
                    audio_analyzer.stop_playback()
                    audio_analyzer.start_playback()
                    particle_system.clear()
                    is_playing = True
                    print("重新开始")
                elif event.key == pygame.K_c:
                    particle_system.clear()
                elif event.key == pygame.K_i:
                    show_info = not show_info
        
        # 音频分析和粒子响应
        if is_playing:
            # 检查节拍
            is_beat, beat_intensity = audio_analyzer.is_beat()
            if is_beat:
                particle_system.beat_response(beat_intensity)
            
            # 检查音符开始
            is_onset, onset_intensity = audio_analyzer.is_onset()
            if is_onset:
                particle_system.onset_response(onset_intensity)
            
            # 根据能量调整重力
            energy = audio_analyzer.get_energy()
            particle_system.set_gravity(30 - energy * 20)  # 能量高时重力小
        
        # 更新粒子系统
        particle_system.update(dt)
        
        # 绘制
        screen.fill((8, 8, 20))  # 深蓝色背景
        
        # 绘制粒子
        particle_system.draw(screen)
        
        # UI信息
        if show_info:
            y_offset = 10
            
            # 播放状态
            status = "播放中" if is_playing else "暂停"
            status_color = (100, 255, 100) if is_playing else (255, 100, 100)
            status_text = font.render(f"状态: {status}", True, status_color)
            screen.blit(status_text, (10, y_offset))
            y_offset += 40
            
            # 播放进度
            if audio_analyzer.get_duration() > 0:
                progress = audio_analyzer.get_progress()
                duration = audio_analyzer.get_duration()
                current_time = audio_analyzer.current_time
                
                progress_text = f"进度: {current_time:.1f}s / {duration:.1f}s ({progress*100:.1f}%)"
                text_surface = font.render(progress_text, True, (255, 255, 255))
                screen.blit(text_surface, (10, y_offset))
                y_offset += 30
                
                # 进度条
                bar_width = 300
                bar_height = 8
                bar_x = 10
                bar_y = y_offset
                
                # 背景
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                # 进度
                pygame.draw.rect(screen, (100, 150, 255), (bar_x, bar_y, int(bar_width * progress), bar_height))
                y_offset += 30
            
            # 粒子信息
            stats = particle_system.get_stats()
            particle_text = f"粒子: {stats['alive_particles']}"
            text_surface = font.render(particle_text, True, (255, 255, 255))
            screen.blit(text_surface, (10, y_offset))
            y_offset += 30
            
            # BPM信息
            if audio_analyzer.tempo:
                bpm_text = f"BPM: {audio_analyzer.tempo:.1f}"
                text_surface = font.render(bpm_text, True, (255, 255, 100))
                screen.blit(text_surface, (10, y_offset))
                y_offset += 30
            
            # 音频特征
            if is_playing:
                energy = audio_analyzer.get_energy()
                centroid = audio_analyzer.get_spectral_centroid()
                
                features_text = f"能量: {energy:.2f} | 频谱: {centroid:.2f}"
                text_surface = font.render(features_text, True, (200, 200, 200))
                screen.blit(text_surface, (10, y_offset))
                y_offset += 30
            
            # 控制说明
            if not is_playing:
                help_text = "SPACE:播放 R:重启 C:清空 ESC:退出"
                text_surface = font.render(help_text, True, (150, 150, 150))
                screen.blit(text_surface, (10, height - 40))
        
        # 显示FPS
        fps_text = f"FPS: {int(clock.get_fps())}"
        fps_surface = font.render(fps_text, True, (100, 255, 100))
        screen.blit(fps_surface, (width - 120, 10))
        
        pygame.display.flip()
    
    pygame.quit()
    print("演示结束")

if __name__ == "__main__":
    main()