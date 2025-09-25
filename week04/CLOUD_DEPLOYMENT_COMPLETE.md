# 🚀 Streamlit Cloud 部署完整指南

## 📋 部署步骤

### 1. 访问 Streamlit Cloud
打开：https://share.streamlit.io/

### 2. 登录GitHub
点击 "Sign in with GitHub"

### 3. 创建新应用
- 点击 **"New app"**
- Repository: `WangZetian-IVERSON/python_01`
- Branch: `main`
- Main file path: `week04/streamlit_cloud_app.py` ⭐
- **Advanced settings**:
  - Requirements file: `week04/requirements_streamlit.txt`
  - Python version: 3.9

### 4. 部署
点击 **"Deploy!"**

---

## 🔑 配置 API 密钥（必需）

### 获取 DeepSeek API 密钥：
1. 访问：https://platform.deepseek.com/
2. 注册账号
3. 获取 API 密钥

### 在 Streamlit Cloud 中配置：
1. 部署完成后，点击 **"Settings"**
2. 找到 **"Secrets"** 部分
3. 添加以下配置：

```toml
DEEPSEEK_API_KEY = "sk-xxxxxxxxxx"  # 你的DeepSeek API密钥
APP_PASSWORD = "deepseek2025"       # 访问密码（可选）
```

4. 点击 **"Save"**
5. 应用会自动重启

---

## 🎯 完成后你将获得：

### 永久固定链接：
```
https://yourappname-yourname.streamlit.app
```

### 特点：
- ✅ 24/7 可访问
- ✅ 全球访问
- ✅ HTTPS 加密
- ✅ 自动更新
- ✅ 免费托管

---

## 📁 文件说明：

### `streamlit_cloud_app.py` - 云端专用版本
- ✅ 使用 DeepSeek 官方 API
- ✅ 密码保护
- ✅ 思考过程显示
- ✅ 对话历史
- ✅ 完整 CSS 样式

### `requirements_streamlit.txt` - 依赖包
```
streamlit>=1.28.0
openai>=1.0.0
```

---

## ⚠️ 注意事项：

### API 费用：
- DeepSeek API 是按使用量收费的
- 新用户通常有免费额度
- 费用很低，大约每1000次对话几美元

### 替代方案：
如果不想使用付费API，可以：
1. 使用免费的 Hugging Face API
2. 使用 Ollama Cloud（如果有的话）
3. 或其他免费AI API服务

---

## � 故障排除

### 问题1：ModuleNotFoundError: openai
**解决方案**：
1. 确保在 Advanced settings 中指定：`week04/requirements_streamlit.txt`
2. 或者直接在应用目录创建 `requirements.txt`

### 问题2：应用无法启动
**检查步骤**：
1. 点击右下角 "Manage app"
2. 查看 Logs 获得详细错误信息
3. 确保所有文件路径正确

### 问题3：API连接失败
**解决方案**：
1. 检查 Secrets 配置是否正确
2. 确保 DeepSeek API 密钥有效
3. 检查 API 余额是否充足

---

## �🚀 快速部署链接：

**直接部署**: https://share.streamlit.io/deploy?repository=WangZetian-IVERSON/python_01&branch=main&mainModule=week04/streamlit_cloud_app.py

需要帮助配置API密钥吗？