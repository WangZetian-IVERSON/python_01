# Python Learning Projects--WangZetian 🐍

欢迎来到我的 Python 学习项目仓库！这里包含了我在学习 Python 过程中完成的各种项目和练习。(welcome come to my repository)

1:![Music Particle Effects](music_particle_effects.gif)

## 🎵 特色项目

### 音乐粒子特效系统
一个基于音频驱动的实时粒子特效可视化项目，展示了音乐与视觉艺术的结合。(music&art)

**主要特性：**
- 🎵 Real-time audio analysis and beat detection
- 🎨 Particle system
- ⚡ 60FPS Smooth rendering
- 🎮 Interactive control
- 📱 You can press any key on the keyboard to create a beat

**PJ location：** `week02/music_particle_effects/`

**quick start：**
```bash
cd week02/music_particle_effects
pip install pygame
python quick_start.py
```
**Main language：** Python 3.8+

**Main repo：**
- `pygame` - Game development and real-time rendering
- `matplotlib` - Data visualization
- `librosa` - Audio analysis
- `numpy` - Numerical analysis
- `requests` - Network requests
- `BeautifulSoup` - Web page parsing
- `FastAPI` - Web API  exploitation
- `Docker` - Containerized deployment

## 🚀 How

1. **clone**
   ```bash
   git clone https://github.com/WangZetian-IVERSON/python_01.git
   cd python_01
   ```

2. **set environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 或
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run**
   ```bash
   # 例如运行音乐粒子特效
   cd week02/music_particle_effects
   python quick_start.py
   ```

## devote🤝 
Suggestions and improvements are welcome! If you have any ideas or find an issue, please create an issue or submit a pull request.

## 📝licence

Only study。

---

# 2： LM Studio DeepSeek Chatbot
<img width="2550" height="1397" alt="image" src="https://github.com/user-attachments/assets/1165508b-def5-4244-82f7-025c4d1ca82f" />

一个功能完善的AI聊天机器人，基于Streamlit构建，支持本地和云端双模式。

## ✨ 特性

- 🤖 **双模式支持**: 自动切换本地LM Studio或DeepSeek云端API （Automatically switch between local LM Studio or DeepSeek cloud APIs）
- 💬 **智能对话**: 支持流式响应和思考过程显示 （Support streaming response and thought process display）
- 📚 **历史管理**: 侧边栏对话历史，支持新建、删除、切换对话 （Sidebar conversation history, which supports creating, deleting, and switching conversations）
- 🎨 **美观界面**: 深色侧边栏+白色文字，主内容区黑色文字 （Dark sidebar + white text, black text in the main content area）
- 🔄 **实时更新**: 流式显示AI回答过程 （Streaming the AI answering process）

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 启动应用
```bash
streamlit run lmstudio_chatbot.py

*持续学习，不断进步！* 🌟
## 📧 about

- GitHub: [@WangZetian-IVERSON](https://github.com/WangZetian-IVERSON)
- 项目仓库: [python_01](https://github.com/WangZetian-IVERSON/python_01)

---

## unsloth — qwen2.5 7B Fine-Tuning

This section documents a LoRA micro-finetuning run performed locally on a Qwen2.5-7B-Instruct base model. It was included here so collaborators can reproduce training and inference steps.

## 概述（Overview）
本次训练以 Qwen2.5-7B-Instruct 为基础模型，采用 LoRA（低秩适配）进行指令微调（SFT），数据源为 Hugging Face 的 FreedomIntelligence/medical-o1-reasoning-SFT（已清洗并导出为本地 JSON）。目标是在有限显存下得到可用的 LoRA 适配器，便于后续推理动态加载或离线合并。（This run fine-tuned Qwen2.5-7B-Instruct using LoRA for SFT on the FreedomIntelligence/medical-o1-reasoning-SFT dataset, which was preprocessed and saved as local JSON.）

## 环境与文件（Environment & Files）
- GPU: NVIDIA GeForce RTX 4090（约 24GB VRAM，单卡）。(GPU: NVIDIA GeForce RTX 4090 (~24GB VRAM, single card).)
- Conda 环境前缀: `/root/autdl-tmp/conda-envs/unsloth`。（Conda env prefix: `/root/autdl-tmp/conda-envs/unsloth`）
- 基础模型（Base model）: `/root/autdl-tmp/modelscope/Qwen-Qwen2.5-7B-Instruct/...`。（Base model path.）
- LoRA 适配器与 tokenizer（LoRA adapter & tokenizer）: `/root/autdl-tmp/unsloth/lora_model`。（LoRA adapter & tokenizer path.）
- 本地训练数据（Local dataset）: `filtered_medical_o1_sft_Chinese.json`。（Local training data JSON.）

## 关键配置（Key Configs）
- LoRA: r=16, alpha=16；target modules 以 q/k/v/o/gate/up/down 为主。（LoRA params: r=16, alpha=16; target modules include q/k/v/o/gate/up/down.）
- 最大序列长度: 8196。（Seq length: 8196.）
- 训练设置: per-device batch=2，gradient_accumulation=4，epochs=1，learning_rate=1e-5。（Training: per-device batch=2, grad_accum=4, epochs=1, lr=1e-5.）
- 使用 TRL 的 SFTTrainer 驱动训练，尽量采用 4-bit 加载（bitsandbytes）以节省显存。（Training used TRL's SFTTrainer and attempted 4-bit loading via bitsandbytes to save memory.）

## 结果速记（Results）
- 单轮训练完成，训练日志末期 train_loss ≈ 1.26。（Single-epoch finished; final train_loss ≈ 1.26.）
- LoRA 适配器已保存于 `lora_model/`，可在线加载或离线合并为完整权重以加速推理启动。（LoRA adapter saved to `lora_model/`; it can be loaded at runtime or merged offline into full weights to speed up startup.）

## 关键代码片段（示意 / Key snippets）
以下代码为示意摘录，完整实现见 `FineTuning.py`。（The following snippets are illustrative extracts; see `FineTuning.py` for full implementation.）

加载基础模型（示意 / Load base model）：（Chinese first, then English）
```python
from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name='/root/autdl-tmp/modelscope/Qwen-Qwen2.5-7B-Instruct/...',
    load_in_4bit=True,
    device_map='cuda:0',
    local_files_only=True,
    trust_remote_code=True,
)
```

应用 LoRA（示意 / Apply LoRA）：
```python
model = FastLanguageModel.get_peft_model(
    model,
    r=16,
    target_modules=["q_proj","k_proj","v_proj","o_proj","gate_proj","up_proj","down_proj"],
    lora_alpha=16,
)
```

保存适配器（示意 / Save adapter）：
```python
model.save_pretrained('lora_model')
tokenizer.save_pretrained('lora_model')
```

推理时加载 LoRA（示意 / Load LoRA for inference）：
```python
from transformers import AutoModelForCausalLM
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained(base_path, local_files_only=True, trust_remote_code=True)
model = PeftModel.from_pretrained(base, '/root/autdl-tmp/unsloth/lora_model', local_files_only=True)
```

## 备注（Notes）
完整实现与训练细节位于 `FineTuning.py`；如需我添加 LoRA 合并脚本、Dockerfile、或把 README 推送到远程仓库，我可以继续协助。（Full implementation and details are in `FineTuning.py`. ）
