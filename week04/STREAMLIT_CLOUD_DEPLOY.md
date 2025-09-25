# 🚀 Streamlit Cloud 部署指南

## 步骤1：准备文件
已为你创建：
- `streamlit_app.py` - Streamlit Cloud专用版本
- `requirements_cloud.txt` - 云端依赖

## 步骤2：创建GitHub仓库

### 方法A：使用现有仓库
1. 打开 https://github.com/WangZetian-IVERSON/python_01
2. 确保这些文件存在：
   - `week04/streamlit_app.py`
   - `week04/requirements_cloud.txt`

### 方法B：创建新仓库
1. 访问 https://github.com/new
2. 仓库名：`deepseek-chatbot`
3. 设为Public
4. 上传文件：
   ```
   streamlit_app.py
   requirements.txt (重命名 requirements_cloud.txt)
   ```

## 步骤3：部署到Streamlit Cloud

1. **访问** https://share.streamlit.io/

2. **登录GitHub账号**

3. **New app**
   - Repository: `WangZetian-IVERSON/python_01`
   - Branch: `main`
   - Main file path: `week04/streamlit_app.py`
   
   或如果创建新仓库：
   - Repository: `WangZetian-IVERSON/deepseek-chatbot`
   - Branch: `main`  
   - Main file path: `streamlit_app.py`

4. **Advanced settings**
   - Python version: 3.9
   - Requirements file: `week04/requirements_cloud.txt`

5. **点击Deploy**

## 步骤4：配置secrets（可选）

如果需要自定义密码：
1. 在Streamlit Cloud的app设置中
2. 添加secrets：
   ```toml
   APP_PASSWORD = "your_password_here"
   ```

## 🎯 完成后你将获得：

**固定URL**: `https://yourapp.streamlit.app`

**特点**：
- ✅ 永久可用
- ✅ 全球访问
- ✅ HTTPS加密
- ✅ 自动更新
- ✅ 免费托管

## ⚠️ 注意事项：

**本地模型限制**：
- Streamlit Cloud无法连接到你本地的LM Studio
- 需要使用在线API服务（如OpenAI、DeepSeek API等）

**解决方案**：
1. 申请DeepSeek官方API密钥
2. 或使用其他在线AI服务
3. 在Streamlit Cloud secrets中配置API密钥

需要我帮你设置在线API吗？