import streamlit as st
from openai import OpenAI
import re
import json
from datetime import datetime

# 改进的UI样式，包含侧边栏
st.markdown("""
<style>
/* 主应用背景 */
.stApp {
    background-color: #f8f9fa !important;
}

/* 侧边栏样式 */
.css-1d391kg {
    background-color: #2c3e50 !important;
    padding: 1rem !important;
}

/* 侧边栏标题 */
.css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
    color: #ecf0f1 !important;
}

/* 侧边栏文本 */
.css-1d391kg .stMarkdown {
    color: #bdc3c7 !important;
}

/* 侧边栏按钮 */
.css-1d391kg .stButton > button {
    background-color: #3498db !important;
    color: white !important;
    border-radius: 6px !important;
    border: none !important;
    width: 100% !important;
    margin-bottom: 0.5rem !important;
}

.css-1d391kg .stButton > button:hover {
    background-color: #2980b9 !important;
}

/* 主内容区域 */
.main {
    background-color: #ffffff !important;
    padding: 2rem !important;
}

/* 标题样式 */
h1 {
    color: #2c3e50 !important;
    font-weight: 700 !important;
    background-color: #ecf0f1 !important;
    padding: 1rem !important;
    border-radius: 10px !important;
    text-align: center !important;
}

/* 聊天消息容器 */
[data-testid="chat-message"] {
    background-color: #f8f9fa !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    margin: 1rem 0 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}

/* 用户消息样式 */
[data-testid*="user"] {
    background-color: #e3f2fd !important;
    border-left: 4px solid #2196f3 !important;
}

/* 助手消息样式 */
[data-testid*="assistant"] {
    background-color: #e8f5e8 !important;
    border-left: 4px solid #4caf50 !important;
}

/* 聊天输入框 */
[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border: 2px solid #e0e0e0 !important;
    border-radius: 25px !important;
    padding: 0.5rem !important;
}

/* 发送按钮 */
[data-testid="stChatInput"] button {
    background-color: #2196f3 !important;
    border-radius: 50% !important;
    width: 40px !important;
    height: 40px !important;
}

[data-testid="stChatInput"] button:hover {
    background-color: #1976d2 !important;
    transform: scale(1.05) !important;
}
</style>
""", unsafe_allow_html=True)

# 添加黑色字体样式
st.markdown("""
<style>
/* 确保所有文本都是黑色 */
.stApp, .main, .block-container, .element-container {
    color: #212529 !important;
}

/* Streamlit默认文本颜色 */
p, div, span, h2, h3, h4, h5, h6 {
    color: #212529 !important;
}

/* 聊天消息文本颜色 */
[data-testid="chat-message"] {
    color: #212529 !important;
}

[data-testid="chat-message"] p, 
[data-testid="chat-message"] div, 
[data-testid="chat-message"] span {
    color: #212529 !important;
}

/* 聊天输入框文本 */
[data-testid="stChatInput"] input {
    color: #212529 !important;
}

/* 思考过程显示 */
.thinking-process {
    background-color: #fff3cd !important;
    border: 1px solid #ffeaa7 !important;
    border-radius: 8px !important;
    padding: 1rem !important;
    margin: 1rem 0 !important;
    color: #212529 !important;
}

.thinking-process h4 {
    color: #856404 !important;
    margin-bottom: 0.5rem !important;
}

.thinking-process p {
    color: #212529 !important;
    margin: 0.5rem 0 !important;
}

/* 强制覆盖Streamlit默认样式 */
.stMarkdown, .stText, .stCaption {
    color: #212529 !important;
}

/* 强制所有markdown内容为黑色 */
.stMarkdown * {
    color: #212529 !important;
}
</style>
""", unsafe_allow_html=True)

# Point to the local server or DeepSeek API
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

# 获取客户端和模型信息
client, client_type, model_name = get_openai_client()

if not client:
    st.stop()

# 配置页面
st.set_page_config(
    page_title="DeepSeek Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("💬 DeepSeek Chatbot")
st.caption(f"🚀 A Streamlit chatbot powered by DeepSeek R1 model via {client_type}")

# 显示连接状态
if client_type == "DeepSeek API":
    st.success("✅ 已连接到 DeepSeek 云端API")
elif client_type == "LM Studio":
    st.success("✅ 已连接到本地 LM Studio")
else:
    st.error("❌ 连接失败")

# 侧边栏 - 历史对话管理
with st.sidebar:
    st.header("📚 对话历史")
    
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
            "messages": [{"role": "assistant", "content": "How can I help you?"}]
        }
        st.session_state.current_conversation_id = new_id
        st.session_state.messages = st.session_state.conversations[new_id]["messages"].copy()
        st.rerun()
    
    # 显示历史对话列表
    st.subheader("历史对话")
    
    if st.session_state.conversations:
        # 按时间倒序显示对话
        conversations_list = list(st.session_state.conversations.items())
        conversations_list.reverse()
        
        for conv_id, conv_data in conversations_list:
            # 创建对话按钮
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
            
            # 删除对话按钮
            if st.button(f"🗑️ 删除", key=f"delete_{conv_id}"):
                if len(st.session_state.conversations) > 1:
                    del st.session_state.conversations[conv_id]
                    if conv_id == st.session_state.current_conversation_id:
                        # 切换到第一个可用对话
                        remaining_convs = list(st.session_state.conversations.keys())
                        if remaining_convs:
                            st.session_state.current_conversation_id = remaining_convs[0]
                            st.session_state.messages = st.session_state.conversations[remaining_convs[0]]["messages"].copy()
                        else:
                            st.session_state.current_conversation_id = None
                            st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
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
            st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
            st.session_state.conversation_counter = 0
            st.rerun()

def format_deepseek_response(content):
    """Format DeepSeek response to separate thinking and response parts"""
    # Multiple patterns to match different thinking formats
    patterns = [
        r'<think>(.*?)</think>',  # Standard <think> tags
        r'<thinking>(.*?)</thinking>',  # Alternative thinking tags
        r'思考：(.*?)(?=\n\n|\Z)',  # Chinese thinking pattern
        r'Thinking:(.*?)(?=\n\n|\Z)',  # English thinking pattern
    ]
    
    thinking_parts = []
    cleaned_content = content
    
    # Try each pattern
    for pattern in patterns:
        matches = re.findall(pattern, cleaned_content, re.DOTALL | re.IGNORECASE)
        thinking_parts.extend(matches)
        # Remove matched parts from content
        cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.DOTALL | re.IGNORECASE)
    
    # Additional check for incomplete thinking tags (streaming scenario)
    incomplete_think_pattern = r'<think>(.*?)(?!</think>)'
    if '<think>' in content and '</think>' not in content:
        # This is likely an incomplete streaming response
        incomplete_match = re.search(incomplete_think_pattern, content, re.DOTALL)
        if incomplete_match:
            thinking_parts.append(incomplete_match.group(1))
            cleaned_content = re.sub(incomplete_think_pattern, '', cleaned_content, flags=re.DOTALL)
    
    response_content = cleaned_content.strip()
    
    return thinking_parts, response_content

def display_formatted_message(content):
    """Display message with formatted thinking and response parts"""
    # Debug: show raw content structure
    # st.text(f"Raw content: {content[:200]}...")
    
    thinking_parts, response_content = format_deepseek_response(content)
    
    # Display thinking parts in small gray text
    if thinking_parts:
        for i, thinking in enumerate(thinking_parts):
            thinking_text = thinking.strip()
            if thinking_text:
                # Escape HTML characters in thinking content
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
    
    # Display response content normally, but check if there's any remaining thinking content
    if response_content:
        # Final check: if response still contains thinking patterns, highlight them
        if '<think>' in response_content or '思考：' in response_content or 'Thinking:' in response_content:
            st.warning("⚠️ 检测到未完全分离的思考内容，请检查格式")
            st.code(response_content, language="text")
        else:
            st.markdown(response_content)
    elif not thinking_parts:
        # If no thinking parts and no response, show raw content
        st.markdown(content)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

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

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        with st.chat_message("assistant"):
            display_formatted_message(msg["content"])
    else:
        st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():

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
                
                # Update display with formatted content
                with message_placeholder.container():
                    display_formatted_message(msg)
        
        st.session_state.messages.append({"role": "assistant", "content": msg})
        
        # 保存到当前对话
        if st.session_state.current_conversation_id:
            st.session_state.conversations[st.session_state.current_conversation_id]["messages"] = st.session_state.messages.copy()
            
            # 如果是第一条用户消息，用它来命名对话
            user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
            if len(user_messages) == 1:
                # 截取前20个字符作为标题
                title = prompt[:20] + "..." if len(prompt) > 20 else prompt
                st.session_state.conversations[st.session_state.current_conversation_id]["title"] = title
                
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
