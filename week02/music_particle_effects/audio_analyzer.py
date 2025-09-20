"""
音频分析模块
使用 librosa 进行音频分析和节拍检测
"""
import librosa
import numpy as np
import threading
import time
from typing import Optional, Tuple, List

class AudioAnalyzer:
    def __init__(self, audio_file: str = None):
        self.audio_file = audio_file
        self.y = None  # 音频数据
        self.sr = None  # 采样率
        self.tempo = None  # BPM
        self.beat_times = None  # 节拍时间点
        self.onset_times = None  # 音符开始时间点
        
        # 实时分析参数
        self.current_time = 0.0
        self.is_playing = False
        self.start_time = None
        
        # 分析结果缓存
        self.spectral_centroids = None
        self.chroma = None
        self.mfcc = None
        
        if audio_file:
            self.load_audio(audio_file)
    
    def load_audio(self, audio_file: str) -> bool:
        """加载音频文件"""
        try:
            print(f"正在加载音频文件: {audio_file}")
            self.y, self.sr = librosa.load(audio_file, duration=30)  # 限制30秒
            print(f"音频加载成功 - 采样率: {self.sr}, 时长: {len(self.y)/self.sr:.2f}秒")
            
            # 分析音频
            self.analyze_audio()
            return True
            
        except Exception as e:
            print(f"音频加载失败: {e}")
            return False
    
    def analyze_audio(self):
        """分析音频特征"""
        if self.y is None:
            return
        
        print("正在分析音频...")
        
        # 节拍检测
        tempo, beat_frames = librosa.beat.beat_track(y=self.y, sr=self.sr)
        self.tempo = tempo
        self.beat_times = librosa.frames_to_time(beat_frames, sr=self.sr)
        print(f"检测到 BPM: {tempo:.1f}, {len(self.beat_times)} 个节拍")
        
        # 音符开始检测
        onset_frames = librosa.onset.onset_detect(y=self.y, sr=self.sr)
        self.onset_times = librosa.frames_to_time(onset_frames, sr=self.sr)
        print(f"检测到 {len(self.onset_times)} 个音符开始点")
        
        # 频谱质心
        self.spectral_centroids = librosa.feature.spectral_centroid(y=self.y, sr=self.sr)[0]
        
        # 色度特征
        self.chroma = librosa.feature.chroma_stft(y=self.y, sr=self.sr)
        
        # MFCC特征
        self.mfcc = librosa.feature.mfcc(y=self.y, sr=self.sr, n_mfcc=13)
        
        print("音频分析完成!")
    
    def start_playback(self):
        """开始播放（模拟）"""
        self.is_playing = True
        self.start_time = time.time()
        self.current_time = 0.0
        print("开始播放模拟")
    
    def stop_playback(self):
        """停止播放"""
        self.is_playing = False
        print("停止播放")
    
    def update_time(self):
        """更新当前播放时间"""
        if self.is_playing and self.start_time:
            self.current_time = time.time() - self.start_time
    
    def is_beat(self, tolerance: float = 0.1) -> Tuple[bool, float]:
        """检查当前时间是否接近节拍点"""
        if self.beat_times is None:
            return False, 0.0
        
        self.update_time()
        
        # 检查是否有节拍在容差范围内
        for beat_time in self.beat_times:
            if abs(self.current_time - beat_time) <= tolerance:
                # 计算强度（越接近节拍点强度越高）
                intensity = 1.0 - (abs(self.current_time - beat_time) / tolerance)
                return True, intensity * 2.0  # 放大强度
        
        return False, 0.0
    
    def is_onset(self, tolerance: float = 0.05) -> Tuple[bool, float]:
        """检查当前时间是否接近音符开始点"""
        if self.onset_times is None:
            return False, 0.0
        
        self.update_time()
        
        for onset_time in self.onset_times:
            if abs(self.current_time - onset_time) <= tolerance:
                intensity = 1.0 - (abs(self.current_time - onset_time) / tolerance)
                return True, intensity * 1.5
        
        return False, 0.0
    
    def get_spectral_centroid(self) -> float:
        """获取当前频谱质心"""
        if self.spectral_centroids is None:
            return 0.0
        
        self.update_time()
        
        # 将时间转换为帧索引
        frame_idx = int(self.current_time * self.sr / 512)  # 512是默认hop_length
        frame_idx = min(frame_idx, len(self.spectral_centroids) - 1)
        
        if frame_idx >= 0:
            # 归一化到0-1范围
            return min(self.spectral_centroids[frame_idx] / 4000.0, 1.0)
        
        return 0.0
    
    def get_chroma_vector(self) -> List[float]:
        """获取当前色度向量"""
        if self.chroma is None:
            return [0.0] * 12
        
        self.update_time()
        
        frame_idx = int(self.current_time * self.sr / 512)
        frame_idx = min(frame_idx, self.chroma.shape[1] - 1)
        
        if frame_idx >= 0:
            return self.chroma[:, frame_idx].tolist()
        
        return [0.0] * 12
    
    def get_mfcc_vector(self) -> List[float]:
        """获取当前MFCC向量"""
        if self.mfcc is None:
            return [0.0] * 13
        
        self.update_time()
        
        frame_idx = int(self.current_time * self.sr / 512)
        frame_idx = min(frame_idx, self.mfcc.shape[1] - 1)
        
        if frame_idx >= 0:
            return self.mfcc[:, frame_idx].tolist()
        
        return [0.0] * 13
    
    def get_energy(self) -> float:
        """获取当前能量（音量）"""
        if self.y is None:
            return 0.0
        
        self.update_time()
        
        # 计算当前时间段的RMS能量
        sample_idx = int(self.current_time * self.sr)
        window_size = 1024
        
        start_idx = max(0, sample_idx - window_size // 2)
        end_idx = min(len(self.y), sample_idx + window_size // 2)
        
        if start_idx < end_idx:
            window = self.y[start_idx:end_idx]
            rms = np.sqrt(np.mean(window ** 2))
            return min(rms * 10.0, 1.0)  # 放大并限制到0-1
        
        return 0.0
    
    def get_duration(self) -> float:
        """获取音频总时长"""
        if self.y is None:
            return 0.0
        return len(self.y) / self.sr
    
    def get_progress(self) -> float:
        """获取播放进度(0-1)"""
        duration = self.get_duration()
        if duration > 0:
            self.update_time()
            return min(self.current_time / duration, 1.0)
        return 0.0