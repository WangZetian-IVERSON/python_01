import streamlit as st
from openai import OpenAI
import re
from datetime import datetime
import hashlib
import socket

# 页面配置
st.set_page_config(
    page_title="DeepSeek Chatbot - 安全版",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 密码保护功能
def check_password():
    """密码验证函数"""
    
    # 设置密码（可以修改这里的密码）
    correct_password = "deepseek2025"  # 你可以改成任何密码
    
    def password_entered():
        """检查输入的密码是否正确"""
        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # 删除密码避免内存泄露
        else:
            st.session_state["password_correct"] = False

    # 如果密码未验证或验证失败
    if "password_correct" not in st.session_state:
        # 首次访问
        st.title("🔒 DeepSeek Chatbot - 安全访问")
        st.markdown("### 请输入访问密码")
        st.text_input(
            "密码", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.info("💡 提示：请联系管理员获取访问密码")
        return False
    elif not st.session_state["password_correct"]:
        # 密码错误
        st.title("🔒 DeepSeek Chatbot - 安全访问")
        st.markdown("### 请输入访问密码")
        st.text_input(
            "密码", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("❌ 密码错误，请重新输入")
        return False
    else:
        # 密码正确
        return True

# 验证密码
if not check_password():
    st.stop()

# UI样式
st.markdown("""
<style>
.stApp {
    background-color: #f8f9fa !important;
    color: #000000 !important;
}

/* 确保所有文本为黑色 */
* {
    color: #000000 !important;
}

/* 主内容区域文本 */
.main * {
    color: #000000 !important;
}

/* 聊天消息文本 */
[data-testid="chat-message"] * {
    color: #000000 !important;
}

/* 确保markdown内容为黑色 */
.stMarkdown {
    color: #000000 !important;
}

.css-1d391kg {
    background-color: #2c3e50 !important;
    padding: 1rem !important;
}

/* 侧边栏文本保持白色 */
.css-1d391kg * {
    color: #ecf0f1 !important;
}

.css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
    color: #ecf0f1 !important;
}

.main {
    background-color: #ffffff !important;
    padding: 2rem !important;
}

h1 {
    color: #2c3e50 !important;
    font-weight: 700 !important;
    background-color: #ecf0f1 !important;
    padding: 1rem !important;
    border-radius: 10px !important;
    text-align: center !important;
}

[data-testid="chat-message"] {
    background-color: #f8f9fa !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin: 1rem 0 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}

[data-testid*="user"] {
    background-color: #e3f2fd !important;
    border-left: 4px solid #2196f3 !important;
}

[data-testid*="assistant"] {
    background-color: #e8f5e8 !important;
    border-left: 4px solid #4caf50 !important;
}

.logout-btn {
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 999;
}
</style>
""", unsafe_allow_html=True)

# 配置 OpenAI 客户端
api_base = st.secrets.get("OPENAI_API_BASE", "http://localhost:1234/v1")
api_key = st.secrets.get("OPENAI_API_KEY", "lm-studio")
model_name = st.secrets.get("MODEL_NAME", "deepseek/deepseek-r1-0528-qwen3-8b")

try:
    client = OpenAI(base_url=api_base, api_key=api_key)
except Exception as e:
    st.error(f"无法连接到 API 服务器: {e}")
    st.stop()

# 顶部标题和注销按钮
col1, col2 = st.columns([4, 1])
with col1:
    st.title("🔒 DeepSeek Chatbot - 安全版")
    st.caption("🚀 基于 DeepSeek R1 模型的安全聊天助手")

with col2:
    if st.button("🚪 注销", key="logout", help="注销当前会话"):
        # 清除所有会话状态
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# 安全提醒
st.info("🛡️ 此应用受密码保护，请勿与未授权人员分享密码")

# 侧边栏 - 历史对话管理
with st.sidebar:
    st.header("📚 对话历史")
    
    # 显示当前用户信息
    st.success("✅ 已通过安全验证")
    
    # 初始化会话状态
    if "conversations" not in st.session_state:
        st.session_state.conversations = {}
    
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = None
        
    if "conversation_counter" not in st.session_state:
        st.session_state.conversation_counter = 0
    
    # 新建对话按钮
    if st.button("🆕 新建对话", use_container_width=True):
        st.session_state.conversation_counter += 1
        new_id = f"conversation_{st.session_state.conversation_counter}"
        current_time = datetime.now().strftime("%H:%M")
        st.session_state.conversations[new_id] = {
            "title": f"对话 {st.session_state.conversation_counter}",
            "time": current_time,
            "messages": [{"role": "assistant", "content": "你好！我是 DeepSeek 助手，有什么可以帮助你的吗？"}]
        }
        st.session_state.current_conversation_id = new_id
        st.session_state.messages = st.session_state.conversations[new_id]["messages"].copy()
        st.rerun()
    
    # 显示历史对话列表
    st.subheader("历史对话")
    
    if st.session_state.conversations:
        conversations_list = list(st.session_state.conversations.items())
        conversations_list.reverse()
        
        for conv_id, conv_data in conversations_list:
            button_text = f"💬 {conv_data['title']} ({conv_data['time']})"
            is_current = conv_id == st.session_state.current_conversation_id
            
            if st.button(
                button_text, 
                key=f"load_{conv_id}",
                use_container_width=True,
                type="primary" if is_current else "secondary"
            ):
                st.session_state.current_conversation_id = conv_id
                st.session_state.messages = st.session_state.conversations[conv_id]["messages"].copy()
                st.rerun()
            
            if st.button(f"🗑️ 删除", key=f"delete_{conv_id}"):
                if len(st.session_state.conversations) > 1:
                    del st.session_state.conversations[conv_id]
                    if conv_id == st.session_state.current_conversation_id:
                        remaining_convs = list(st.session_state.conversations.keys())
                        if remaining_convs:
                            st.session_state.current_conversation_id = remaining_convs[0]
                            st.session_state.messages = st.session_state.conversations[remaining_convs[0]]["messages"].copy()
                        else:
                            st.session_state.current_conversation_id = None
                            st.session_state.messages = [{"role": "assistant", "content": "你好！我是 DeepSeek 助手，有什么可以帮助你的吗？"}]
                    st.rerun()
                else:
                    st.warning("至少需要保留一个对话！")
            
            st.divider()
    else:
        st.info("暂无历史对话，点击上方按钮开始新对话")
    
    # 清空所有对话
    if st.button("🧹 清空所有对话", use_container_width=True):
        if st.session_state.conversations:
            st.session_state.conversations = {}
            st.session_state.current_conversation_id = None
            st.session_state.messages = [{"role": "assistant", "content": "你好！我是 DeepSeek 助手，有什么可以帮助你的吗？"}]
            st.session_state.conversation_counter = 0
            st.rerun()

def format_deepseek_response(content):
    """格式化 DeepSeek 响应，分离思考和回答部分"""
    patterns = [
        r'<think>(.*?)</think>',
        r'<thinking>(.*?)</thinking>',
        r'思考：(.*?)(?=\n\n|\Z)',
        r'Thinking:(.*?)(?=\n\n|\Z)',
    ]
    
    thinking_parts = []
    cleaned_content = content
    
    for pattern in patterns:
        matches = re.findall(pattern, cleaned_content, re.DOTALL | re.IGNORECASE)
        thinking_parts.extend(matches)
        cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.DOTALL | re.IGNORECASE)
    
    incomplete_think_pattern = r'<think>(.*?)(?!</think>)'
    if '<think>' in content and '</think>' not in content:
        incomplete_match = re.search(incomplete_think_pattern, content, re.DOTALL)
        if incomplete_match:
            thinking_parts.append(incomplete_match.group(1))
            cleaned_content = re.sub(incomplete_think_pattern, '', cleaned_content, flags=re.DOTALL)
    
    response_content = cleaned_content.strip()
    return thinking_parts, response_content

def display_formatted_message(content):
    """显示格式化的消息"""
    thinking_parts, response_content = format_deepseek_response(content)
    
    if thinking_parts:
        for i, thinking in enumerate(thinking_parts):
            thinking_text = thinking.strip()
            if thinking_text:
                thinking_html = thinking_text.replace('\n', '<br>')
                st.markdown(f'''
                <div style="
                    font-size:12px; 
                    color:#666666; 
                    font-style:italic; 
                    margin-bottom:10px; 
                    padding:8px; 
                    background-color:#f8f9fa; 
                    border-left:3px solid #dee2e6;
                    border-radius:4px;">
                    🤔 <strong>思考过程 {i+1}:</strong><br>
                    {thinking_html}
                </div>
                ''', unsafe_allow_html=True)
    
    if response_content:
        if '<think>' in response_content or '思考：' in response_content or 'Thinking:' in response_content:
            st.warning("⚠️ 检测到未完全分离的思考内容")
            st.code(response_content, language="text")
        else:
            st.markdown(response_content)
    elif not thinking_parts:
        st.markdown(content)

# 初始化消息
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "你好！我是 DeepSeek 助手，有什么可以帮助你的吗？"}]

# 如果没有当前对话，创建第一个对话
if st.session_state.current_conversation_id is None and not st.session_state.conversations:
    st.session_state.conversation_counter += 1
    new_id = f"conversation_{st.session_state.conversation_counter}"
    current_time = datetime.now().strftime("%H:%M")
    st.session_state.conversations[new_id] = {
        "title": f"对话 {st.session_state.conversation_counter}",
        "time": current_time,
        "messages": st.session_state.messages.copy()
    }
    st.session_state.current_conversation_id = new_id

# 显示对话历史
for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        with st.chat_message("assistant"):
            display_formatted_message(msg["content"])
    else:
        st.chat_message(msg["role"]).write(msg["content"])

# 处理用户输入
if prompt := st.chat_input("请输入您的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=st.session_state.messages,
            stream=True,
        )

        msg = ""
        assistant_message = st.chat_message("assistant")
        message_placeholder = assistant_message.empty()

        for chunk in response:
            if chunk.choices[0].delta.content:
                msg += chunk.choices[0].delta.content
                
                with message_placeholder.container():
                    display_formatted_message(msg)
        
        st.session_state.messages.append({"role": "assistant", "content": msg})
        
        # 保存到当前对话
        if st.session_state.current_conversation_id:
            st.session_state.conversations[st.session_state.current_conversation_id]["messages"] = st.session_state.messages.copy()
            
            # 用第一条用户消息命名对话
            user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
            if len(user_messages) == 1:
                title = prompt[:20] + "..." if len(prompt) > 20 else prompt
                st.session_state.conversations[st.session_state.current_conversation_id]["title"] = title
                
    except Exception as e:
        st.error(f"连接错误: {e}")
        st.info("请确保 LM Studio 正在运行并启动了服务器")