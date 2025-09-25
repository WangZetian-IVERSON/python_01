import streamlit as st
from openai import OpenAI
import re
from datetime import datetime
import hashlib

# 页面配置
st.set_page_config(
    page_title="DeepSeek Chatbot - Cloud版",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 密码保护功能
def check_password():
    """密码验证函数"""
    
    # 设置密码
    correct_password = st.secrets.get("APP_PASSWORD", "deepseek2025")
    
    def password_entered():
        """检查输入的密码是否正确"""
        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # 如果密码未验证或验证失败
    if "password_correct" not in st.session_state:
        st.markdown("# 🔒 DeepSeek Chatbot")
        st.markdown("请输入访问密码：")
        st.text_input("密码", type="password", on_change=password_entered, key="password")
        st.info("💡 提示：这是一个基于DeepSeek R1模型的AI聊天机器人")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("# 🔒 DeepSeek Chatbot")
        st.markdown("请输入访问密码：")
        st.text_input("密码", type="password", on_change=password_entered, key="password")
        st.error("❌ 密码错误，请重试")
        return False
    else:
        return True

# 自定义CSS样式
def load_custom_css():
    st.markdown("""
    <style>
    /* 确保所有文本都是黑色 */
    .stApp, .stApp * {
        color: #000000 !important;
    }
    
    /* 主容器背景 */
    .stApp {
        background-color: #ffffff;
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background-color: #f0f2f6;
    }
    
    /* 聊天消息样式 */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    
    /* 思考过程样式 */
    .thinking-section {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        font-style: italic;
        color: #000000 !important;
    }
    
    /* 响应部分样式 */
    .response-section {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        color: #000000 !important;
    }
    
    /* 标题样式 */
    h1, h2, h3 {
        color: #000000 !important;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background-color: #2196f3;
        color: white !important;
        border: none;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #1976d2;
        color: white !important;
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* 确保代码块文本可见 */
    code {
        color: #000000 !important;
        background-color: #f5f5f5 !important;
    }
    
    pre {
        background-color: #f5f5f5 !important;
    }
    
    pre code {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# DeepSeek响应解析
def parse_deepseek_response(response):
    """解析DeepSeek模型的响应，分离思考过程和最终回答"""
    
    # 使用正则表达式匹配<think>标签
    think_pattern = r'<think>(.*?)</think>'
    think_matches = re.findall(think_pattern, response, re.DOTALL)
    
    # 移除<think>标签获得最终回答
    final_response = re.sub(think_pattern, '', response, flags=re.DOTALL).strip()
    
    return think_matches, final_response

# 初始化OpenAI客户端
@st.cache_resource
def get_openai_client():
    """获取OpenAI客户端"""
    try:
        # 从 Streamlit secrets 获取配置
        api_key = st.secrets.get("DEEPSEEK_API_KEY", None)
        if not api_key:
            st.error("❌ 请配置 DeepSeek API 密钥")
            st.info("""
            **配置说明：**
            1. 在 Streamlit Cloud 的 App settings 中
            2. 添加 secrets：
            ```toml
            DEEPSEEK_API_KEY = "your_api_key_here"
            APP_PASSWORD = "your_password_here"  # 可选
            ```
            
            **获取 DeepSeek API 密钥：**
            - 访问：https://platform.deepseek.com/
            - 注册并获取 API 密钥
            """)
            return None
            
        # 使用 DeepSeek API
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        return client
    except Exception as e:
        st.error(f"❌ 无法连接到DeepSeek API：{str(e)}")
        return None

def main():
    # 检查密码
    if not check_password():
        return
    
    # 加载自定义样式
    load_custom_css()
    
    # 获取OpenAI客户端
    client = get_openai_client()
    if not client:
        return
    
    # 主标题
    st.title("🤖 DeepSeek R1 Chatbot - Cloud版")
    st.markdown("基于DeepSeek R1模型的云端智能对话助手")
    
    # 侧边栏
    with st.sidebar:
        st.header("💬 对话历史")
        
        # 清除历史按钮
        if st.button("🗑️ 清除历史", type="secondary"):
            st.session_state.messages = []
            st.rerun()
        
        # 显示对话统计
        if "messages" in st.session_state:
            total_messages = len(st.session_state.messages)
            user_messages = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
            st.metric("总消息数", total_messages)
            st.metric("用户消息", user_messages)
        
        st.markdown("---")
        st.markdown("### 📝 使用说明")
        st.markdown("""
        - 直接输入问题开始对话
        - 支持中英文对话
        - 显示AI的思考过程
        - 自动保存对话历史
        """)
        
        st.markdown("---")
        st.markdown("### ⚡ 模型信息")
        st.markdown("**DeepSeek R1** - 推理增强模型")
        st.markdown("🌐 **云端版本** - 永久可访问")
    
    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "thinking" in message:
                # 显示思考过程
                if message.get("thinking"):
                    with st.expander("🤔 AI思考过程", expanded=False):
                        st.markdown(f'<div class="thinking-section">{message["thinking"]}</div>', 
                                  unsafe_allow_html=True)
                
                # 显示最终回答
                st.markdown(f'<div class="response-section">{message["content"]}</div>', 
                          unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="user-message">{message["content"]}</div>', 
                          unsafe_allow_html=True)
    
    # 用户输入
    if prompt := st.chat_input("输入你的问题..."):
        # 添加用户消息到历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
        
        # 生成AI回复
        with st.chat_message("assistant"):
            with st.spinner("DeepSeek正在思考中..."):
                try:
                    # 调用DeepSeek API
                    response = client.chat.completions.create(
                        model="deepseek-reasoner",
                        messages=[
                            {"role": "system", "content": "你是DeepSeek R1，一个有用、无害、诚实的AI助手。请用中文回答，并在回答时展示你的思考过程。"},
                            *st.session_state.messages
                        ],
                        temperature=0.7,
                        max_tokens=2000
                    )
                    
                    # 获取响应内容
                    full_response = response.choices[0].message.content
                    
                    # 解析响应
                    thinking_parts, final_response = parse_deepseek_response(full_response)
                    
                    # 合并思考部分
                    thinking_text = "\n\n".join(thinking_parts) if thinking_parts else ""
                    
                    # 显示思考过程（如果有）
                    if thinking_text:
                        with st.expander("🤔 AI思考过程", expanded=False):
                            st.markdown(f'<div class="thinking-section">{thinking_text}</div>', 
                                      unsafe_allow_html=True)
                    
                    # 显示最终回答
                    if final_response:
                        st.markdown(f'<div class="response-section">{final_response}</div>', 
                                  unsafe_allow_html=True)
                        
                        # 添加到对话历史
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": final_response,
                            "thinking": thinking_text
                        })
                    else:
                        st.error("❌ 未能获得有效回答")
                        
                except Exception as e:
                    st.error(f"❌ API调用失败：{str(e)}")
                    st.info("💡 请检查API密钥配置是否正确")

if __name__ == "__main__":
    main()