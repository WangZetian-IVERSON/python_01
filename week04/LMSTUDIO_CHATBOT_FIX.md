# LM Studio 聊天机器人修复说明

## 问题描述
原始的 `lmstudio_chatbot.py` 文件在 Streamlit Cloud 上部署时出现 `APIConnectionError` 错误，因为代码试图连接到 `localhost:1234` 的本地 LM Studio 服务器，但在云环境中无法访问本地服务器。

## 解决方案

### 1. 自适应客户端初始化
添加了智能客户端选择机制：
```python
@st.cache_resource
def get_openai_client():
    """获取OpenAI客户端 - 支持本地和云端"""
    try:
        # 尝试从 Streamlit secrets 获取 DeepSeek API 配置
        api_key = st.secrets.get("DEEPSEEK_API_KEY", None)
        if api_key:
            # 使用 DeepSeek API (云端版本)
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
            return client, "DeepSeek API", "deepseek-chat"
        else:
            # 使用本地 LM Studio (本地版本)
            client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")
            return client, "LM Studio", "deepseek/deepseek-r1-0528-qwen3-8b"
    except Exception as e:
        st.error(f"客户端初始化错误: {e}")
        return None, "错误", ""
```

### 2. 动态模型选择
- **云端模式**：使用 `deepseek-chat` 模型
- **本地模式**：使用 `deepseek/deepseek-r1-0528-qwen3-8b` 模型

### 3. 增强的错误处理
添加了comprehensive error handling：
```python
try:
    response = client.chat.completions.create(
        model=model_name,
        messages=st.session_state.messages,
        stream=True,
    )
except Exception as e:
    st.error(f"API调用失败: {e}")
    if "insufficient" in str(e).lower() or "balance" in str(e).lower():
        st.warning("⚠️ API余额不足，请充值后再试")
    elif "connection" in str(e).lower():
        st.warning("⚠️ 网络连接问题，请检查网络设置")
    else:
        st.info("请检查以下配置：")
        st.info("- 如果使用云端版本，请确保配置了 DEEPSEEK_API_KEY")
        st.info("- 如果使用本地版本，请确保 LM Studio 正在运行")
```

### 4. 状态指示器
添加了连接状态显示：
- ✅ 已连接到 DeepSeek 云端API
- ✅ 已连接到本地 LM Studio
- ❌ 连接失败

## 部署配置

### 本地运行
无需额外配置，自动使用本地 LM Studio 服务器。

### Streamlit Cloud 部署
需要在 Streamlit Cloud 的 App settings 中配置 Secrets：

```toml
DEEPSEEK_API_KEY = "sk-4483325f3b24494ea26de5b89b3bd98f"
APP_PASSWORD = "20040311"  # 如果需要密码保护
```

## 功能特性

### 双模式支持
1. **本地模式**：连接到 LM Studio 本地服务器
2. **云端模式**：连接到 DeepSeek API

### 智能降级
- 优先尝试云端 API
- 如果没有配置 API 密钥，则回退到本地模式

### 详细错误提示
- API 余额不足提醒
- 网络连接问题诊断
- 配置检查指导

## 使用说明

### 本地使用
1. 确保 LM Studio 正在运行并监听 1234 端口
2. 运行 streamlit 应用
3. 开始聊天

### 云端使用
1. 配置 DeepSeek API 密钥
2. 部署到 Streamlit Cloud
3. 访问应用URL开始聊天

## 文件位置
- 修复后的文件：`week04/lmstudio_chatbot.py`
- GitHub 仓库：`WangZetian-IVERSON/python_01`
- 提交ID：`5848a6a`

## 更新日期
2025-09-26