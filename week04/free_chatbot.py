import streamlit as st
import requests
import json
import re
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="免费AI聊天机器人",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 密码保护功能
def check_password():
    """密码验证函数"""
    
    # 设置密码
    correct_password = st.secrets.get("APP_PASSWORD", "20040311")
    
    def password_entered():
        """检查输入的密码是否正确"""
        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    # 如果密码未验证或验证失败
    if "password_correct" not in st.session_state:
        st.markdown("# 🔒 免费AI聊天机器人")
        st.markdown("请输入访问密码：")
        st.text_input("密码", type="password", on_change=password_entered, key="password")
        st.info("💡 提示：这是一个免费的AI聊天机器人")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("# 🔒 免费AI聊天机器人")
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
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0.5rem;
        color: #000000 !important;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
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
    </style>
    """, unsafe_allow_html=True)

# 免费AI API调用
def call_free_ai(message):
    """调用免费AI服务"""
    try:
        # 使用Hugging Face免费API作为示例
        # 你也可以替换为其他免费AI服务
        
        # 简单的响应生成（演示用）
        responses = [
            f"感谢你的问题：{message}",
            f"这是一个很好的问题！关于'{message}'，我建议你可以从以下几个角度考虑...",
            f"根据你提到的'{message}'，我的理解是...",
            f"对于'{message}'这个话题，让我为你分析一下..."
        ]
        
        import random
        return random.choice(responses) + "\n\n（注：这是免费版本的演示回复）"
        
    except Exception as e:
        return f"抱歉，AI服务暂时不可用：{str(e)}"

def main():
    # 检查密码
    if not check_password():
        return
    
    # 加载自定义样式
    load_custom_css()
    
    # 主标题
    st.title("🤖 免费AI聊天机器人")
    st.markdown("基于免费AI服务的智能对话助手")
    
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
        - 完全免费使用
        - 支持中英文对话
        - 自动保存对话历史
        """)
        
        st.markdown("---")
        st.markdown("### ⚡ 服务信息")
        st.markdown("**免费AI服务** - 无需API密钥")
        st.markdown("🆓 **完全免费** - 无余额限制")
        
        st.markdown("---")
        st.markdown("### 💡 升级选项")
        st.markdown("""
        **想要更强大的AI？**
        - 充值DeepSeek API获得更好体验
        - 或使用其他免费AI服务
        """)
    
    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(f'<div class="assistant-message">{message["content"]}</div>', 
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
            with st.spinner("AI正在思考中..."):
                # 调用免费AI服务
                response = call_free_ai(prompt)
                
                # 显示回答
                st.markdown(f'<div class="assistant-message">{response}</div>', 
                          unsafe_allow_html=True)
                
                # 添加到对话历史
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response
                })

if __name__ == "__main__":
    main()