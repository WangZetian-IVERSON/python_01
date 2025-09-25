import streamlit as st
import re
from datetime import datetime
import hashlib
import requests
import io
import tempfile
import os
from urllib.parse import urljoin, urlparse

# 尝试导入可选依赖项
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    st.error("OpenAI package not found. Please install it: pip install openai")
    OPENAI_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    st.error("BeautifulSoup4 package not found. Please install it: pip install beautifulsoup4")
    BS4_AVAILABLE = False

# 页面配置
st.set_page_config(
    page_title="DeepSeek Chatbot - 云端增强版",
    page_icon="📚",
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
        st.markdown("# 🔒 DeepSeek Chatbot - 云端增强版")
        st.markdown("请输入访问密码：")
        st.text_input("密码", type="password", on_change=password_entered, key="password")
        st.info("💡 提示：这是一个支持PDF和网页读取的云端AI聊天机器人")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("# 🔒 DeepSeek Chatbot - 云端增强版")
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
    
    /* 文档信息样式 */
    .document-info {
        background-color: #f0f4f8;
        border-left: 4px solid #00acc1;
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

# PDF读取功能（云端简化版）
def extract_pdf_text(uploaded_file):
    """从上传的PDF文件中提取文本（云端版本）"""
    try:
        st.warning("⚠️ PDF读取功能在云端版本中受限。如需处理PDF文件，请：")
        st.info("""
        **替代方案：**
        1. 手动复制PDF中的文本并粘贴到下方的文本输入框
        2. 使用在线PDF转文本工具
        3. 使用本地版本的增强聊天机器人
        """)
        
        return None
        
    except Exception as e:
        st.error(f"PDF处理出错: {e}")
        return None

# 网页内容读取功能
def extract_webpage_text(url):
    """从网页URL中提取文本内容"""
    if not BS4_AVAILABLE:
        st.error("BeautifulSoup4 不可用，无法解析网页内容。")
        return None
        
    try:
        # 设置请求头，模拟浏览器访问
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 发送GET请求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查HTTP错误
        
        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 移除脚本和样式元素
        for script in soup(["script", "style"]):
            script.extract()
        
        # 提取文本内容
        text = soup.get_text()
        
        # 清理文本：移除多余的空白字符
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:5000]  # 限制长度，避免过长
        
    except requests.exceptions.RequestException as e:
        return f"网页访问错误：{str(e)}"
    except Exception as e:
        return f"网页解析错误：{str(e)}"

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
    if not OPENAI_AVAILABLE:
        return None, "OpenAI库不可用"
        
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
            - 充值余额以使用API服务
            """)
            return None, "未配置API"
            
        # 使用 DeepSeek API
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )
        return client, "DeepSeek API"
    except Exception as e:
        return None, f"连接错误：{str(e)}"

def main():
    # 检查密码
    if not check_password():
        return
    
    # 加载自定义样式
    load_custom_css()
    
    # 获取OpenAI客户端
    client, client_info = get_openai_client()
    
    # 主标题
    st.title("📚 DeepSeek Chatbot - 云端增强版")
    st.markdown("支持PDF和网页内容读取的云端智能对话助手")
    
    # 显示客户端状态
    if client:
        st.success(f"✅ AI服务已连接：{client_info}")
    else:
        st.error(f"❌ AI服务连接失败：{client_info}")
        return
    
    # 侧边栏
    with st.sidebar:
        st.header("📁 文档处理")
        
        # PDF上传
        st.subheader("📄 PDF文件读取")
        uploaded_pdf = st.file_uploader("上传PDF文件", type=['pdf'])
        
        if uploaded_pdf:
            if st.button("📖 读取PDF内容"):
                with st.spinner("正在读取PDF..."):
                    pdf_text = extract_pdf_text(uploaded_pdf)
                    if pdf_text and not pdf_text.startswith("PDF读取错误") and not pdf_text.startswith("PDF读取功能暂不可用"):
                        st.session_state.pdf_content = pdf_text
                        st.success(f"✅ PDF读取成功！共{len(pdf_text)}个字符")
                        st.text_area("PDF内容预览", pdf_text[:500] + "..." if len(pdf_text) > 500 else pdf_text, height=150)
                    else:
                        st.error(pdf_text)
                        if "暂不可用" in pdf_text:
                            st.info("💡 PDF功能需要管理员安装额外的依赖包")
        
        st.markdown("---")
        
        # 网页URL读取
        st.subheader("🌐 网页内容读取")
        webpage_url = st.text_input("输入网页URL", placeholder="https://example.com")
        
        if webpage_url and st.button("🔍 读取网页内容"):
            with st.spinner("正在读取网页..."):
                webpage_text = extract_webpage_text(webpage_url)
                if webpage_text and not webpage_text.startswith("网页"):
                    st.session_state.webpage_content = webpage_text
                    st.success(f"✅ 网页读取成功！共{len(webpage_text)}个字符")
                    st.text_area("网页内容预览", webpage_text[:500] + "..." if len(webpage_text) > 500 else webpage_text, height=150)
                else:
                    st.error(webpage_text)
        
        st.markdown("---")
        
        # 文本输入功能
        st.subheader("📝 直接输入文本")
        direct_text = st.text_area("直接输入或粘贴文本内容", height=150, placeholder="在这里粘贴任何文本内容...")
        
        if direct_text and st.button("💾 保存文本内容"):
            st.session_state.direct_text_content = direct_text
            st.success(f"✅ 文本保存成功！共{len(direct_text)}个字符")
        
        st.markdown("---")
        
        # 对话历史管理
        st.header("💬 对话管理")
        
        # 清除历史按钮
        if st.button("🗑️ 清除对话历史", type="secondary"):
            st.session_state.messages = []
            st.rerun()
        
        # 清除文档内容
        if st.button("📄 清除所有内容", type="secondary"):
            for key in ['pdf_content', 'webpage_content', 'direct_text_content']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
        
        # 显示对话统计
        if "messages" in st.session_state:
            total_messages = len(st.session_state.messages)
            user_messages = len([msg for msg in st.session_state.messages if msg["role"] == "user"])
            st.metric("总消息数", total_messages)
            st.metric("用户消息", user_messages)
        
        st.markdown("---")
        st.markdown("### 📝 功能说明")
        st.markdown("""
        **🔍 主要功能：**
        - 📄 PDF文件读取和分析
        - 🌐 网页内容抓取和解析
        - 📝 直接文本输入和分析
        - 💬 基于文档内容的智能对话
        
        **💡 使用方法：**
        - 上传PDF、输入网页URL或直接粘贴文本
        - 读取内容后直接提问相关问题
        - AI会基于文档内容回答
        """)
        
        st.markdown("---")
        st.markdown("### ⚡ AI模型")
        st.markdown(f"**当前连接**: {client_info}")
        st.markdown("🌐 **云端版本** - 永久可访问")
    
    # 初始化对话历史
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # 显示文档状态
    doc_status = []
    if 'pdf_content' in st.session_state:
        doc_status.append("📄 PDF文档")
    if 'webpage_content' in st.session_state:
        doc_status.append("🌐 网页内容")
    if 'direct_text_content' in st.session_state:
        doc_status.append("📝 文本内容")
    
    if doc_status:
        st.info(f"📚 当前已加载：{' + '.join(doc_status)}")
    
    # 显示对话历史
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                # 显示思考过程（如果有）
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
    if prompt := st.chat_input("输入你的问题（可以询问已上传的文档内容）..."):
        # 添加用户消息到历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
        
        # 构建上下文信息
        context_info = ""
        
        # 添加PDF内容
        if 'pdf_content' in st.session_state:
            context_info += f"\n\n**PDF文档内容：**\n{st.session_state.pdf_content[:2000]}..."
        
        # 添加网页内容
        if 'webpage_content' in st.session_state:
            context_info += f"\n\n**网页内容：**\n{st.session_state.webpage_content[:2000]}..."
        
        # 添加直接输入的文本内容
        if 'direct_text_content' in st.session_state:
            context_info += f"\n\n**用户提供的文本内容：**\n{st.session_state.direct_text_content[:2000]}..."
        
        # 构建完整的prompt
        full_prompt = prompt
        if context_info:
            full_prompt = f"""用户问题：{prompt}

参考文档内容：{context_info}

请基于上述文档内容回答用户的问题。如果文档内容与问题无关，请正常回答问题并说明未找到相关文档内容。"""
        
        # 生成AI回复
        with st.chat_message("assistant"):
            with st.spinner("DeepSeek正在分析文档并思考中..."):
                try:
                    # 调用DeepSeek API
                    response = client.chat.completions.create(
                        model="deepseek-reasoner",
                        messages=[
                            {"role": "system", "content": "你是DeepSeek R1，一个有用、无害、诚实的AI助手。你可以阅读和分析PDF文档、网页内容和文本内容，并基于这些内容回答用户的问题。请用中文回答。"},
                            {"role": "user", "content": full_prompt}
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
                    if "402" in str(e) or "Insufficient Balance" in str(e):
                        st.error("💰 DeepSeek API余额不足，请充值后继续使用")
                        st.info("💡 访问 https://platform.deepseek.com/ 进行充值")
                    else:
                        st.info("💡 请检查API密钥配置是否正确")

if __name__ == "__main__":
    main()