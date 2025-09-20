"""
音频分析模块 - 检测音乐的鼓点和节拍
"""
import librosa
import numpy as np
from scipy.signal import find_peaks
import soundfile as sf

class AudioAnalyzer:
    def __init__(self, audio_file):
        """
        初始化音频分析器
        :param audio_file: 音频文件路径
        """
        self.audio_file = audio_file
        self.y = None  # 音频数据
        self.sr = None  # 采样率
        self.tempo = None  # BPM
        self.beats = None  # 节拍时间点
        self.onset_times = None  # 音符开始时间点
        
    def load_audio(self):
        """加载音频文件"""
        try:
            self.y, self.sr = librosa.load(self.audio_file, sr=22050)
            print(f"音频加载成功: {self.audio_file}")
            print(f"采样率: {self.sr}, 时长: {len(self.y)/self.sr:.2f}秒")
            return True
        except Exception as e:
            print(f"音频加载失败: {e}")
            return False
    
    def analyze_beats(self):
        """分析节拍"""
        if self.y is None:
            raise ValueError("请先加载音频文件")
        
        # 检测BPM和节拍
        self.tempo, beats = librosa.beat.beat_track(y=self.y, sr=self.sr)
        self.beats = librosa.frames_to_time(beats, sr=self.sr)
        
        print(f"检测到BPM: {self.tempo:.1f}")
        print(f"节拍数量: {len(self.beats)}")
        
        return self.beats
    
    def detect_onsets(self):
        """检测音符开始点（鼓点等）"""
        if self.y is None:
            raise ValueError("请先加载音频文件")
        
        # 使用onset detection检测鼓点
        onset_frames = librosa.onset.onset_detect(
            y=self.y, 
            sr=self.sr,
            units='time',
            hop_length=512,
            backtrack=True
        )
        
        self.onset_times = onset_frames
        print(f"检测到音符开始点: {len(self.onset_times)}个")
        
        return self.onset_times
    
    def get_spectral_features(self, frame_time):
        """获取指定时间点的频谱特征"""
        if self.y is None:
            raise ValueError("请先加载音频文件")
        
        # 将时间转换为样本索引
        frame_idx = int(frame_time * self.sr)
        
        # 获取一小段音频用于分析
        window_size = 1024
        start_idx = max(0, frame_idx - window_size // 2)
        end_idx = min(len(self.y), frame_idx + window_size // 2)
        
        audio_segment = self.y[start_idx:end_idx]
        
        if len(audio_segment) == 0:
            return {'rms': 0, 'spectral_centroid': 0, 'zero_crossing_rate': 0}
        
        # 计算特征
        rms = librosa.feature.rms(y=audio_segment)[0][0]
        spectral_centroid = librosa.feature.spectral_centroid(y=audio_segment, sr=self.sr)[0][0]
        zero_crossing_rate = librosa.feature.zero_crossing_rate(audio_segment)[0][0]
        
        return {
            'rms': float(rms),
            'spectral_centroid': float(spectral_centroid),
            'zero_crossing_rate': float(zero_crossing_rate)
        }
    
    def create_dummy_audio(self, duration=10, bpm=120):
        """创建模拟音频数据用于测试"""
        print("创建模拟音频数据...")
        
        # 生成测试音频
        self.sr = 22050
        self.tempo = bpm
        
        # 生成基础节拍
        beat_interval = 60.0 / bpm  # 节拍间隔（秒）
        num_beats = int(duration / beat_interval)
        
        # 创建节拍时间点
        self.beats = np.arange(0, duration, beat_interval)[:num_beats]
        
        # 创建音符开始时间点（更密集）
        onset_interval = beat_interval / 2  # 每个节拍有2个onset
        self.onset_times = np.arange(0, duration, onset_interval)
        
        # 生成简单的音频信号
        t = np.linspace(0, duration, int(duration * self.sr))
        self.y = np.zeros_like(t)
        
        # 在每个节拍点添加鼓声
        for beat_time in self.beats:
            beat_sample = int(beat_time * self.sr)
            if beat_sample < len(self.y):
                # 添加低频鼓声
                drum_duration = int(0.1 * self.sr)  # 0.1秒鼓声
                end_sample = min(beat_sample + drum_duration, len(self.y))
                drum_samples = np.arange(end_sample - beat_sample)
                drum_sound = np.sin(2 * np.pi * 60 * drum_samples / self.sr) * np.exp(-drum_samples / (0.05 * self.sr))
                self.y[beat_sample:end_sample] += drum_sound * 0.5
        
        print(f"生成模拟音频: BPM={bpm}, 时长={duration}秒, 节拍={len(self.beats)}个")
        return True

if __name__ == "__main__":
    # 测试代码
    analyzer = AudioAnalyzer("test.wav")
    
    # 创建模拟音频进行测试
    if analyzer.create_dummy_audio(duration=10, bpm=120):
        beats = analyzer.analyze_beats()
        onsets = analyzer.detect_onsets()
        
        print("前5个节拍时间点:", beats[:5])
        print("前5个音符开始点:", onsets[:5])