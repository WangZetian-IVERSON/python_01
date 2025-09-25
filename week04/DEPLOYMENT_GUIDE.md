# DeepSeek Chatbot 部署指南

## 🌐 分享你的 AI 聊天机器人

### 方案一：Streamlit Cloud（免费，推荐）

1. **准备 GitHub 仓库**
   - 将 `chatbot_deploy.py` 推送到 GitHub
   - 确保 `requirements.txt` 包含所需依赖
   - 添加 `.streamlit/config.toml` 配置文件

2. **部署到 Streamlit Cloud**
   - 访问 [share.streamlit.io](https://share.streamlit.io)
   - 登录 GitHub 账号
   - 选择仓库和 `chatbot_deploy.py` 文件
   - 点击 Deploy

3. **配置 API**
   - 在 Streamlit Cloud 的 Secrets 中配置 API 信息
   - 或修改代码连接到公开的 API 服务

**优点**: 完全免费，自动部署，支持自定义域名
**缺点**: 需要连接外部 API（因为无法运行本地 LM Studio）

---

### 方案二：本地网络分享

1. **启动应用**
   ```bash
   streamlit run chatbot_deploy.py --server.port 8501 --server.address 0.0.0.0
   ```

2. **获取本机 IP**
   - Windows: `ipconfig`
   - 找到你的局域网 IP（如：192.168.1.100）

3. **分享链接**
   - 其他人可以通过 `http://你的IP:8501` 访问
   - 例如：`http://192.168.1.100:8501`

**优点**: 保持本地 LM Studio，完全控制
**缺点**: 仅限局域网访问，需要保持电脑开启

---

### 方案三：Docker 部署

1. **构建镜像**
   ```bash
   cd week04
   docker build -t deepseek-chatbot .
   ```

2. **运行容器**
   ```bash
   docker run -p 8501:8501 deepseek-chatbot
   ```

3. **访问应用**
   - 本地: `http://localhost:8501`
   - 网络: `http://你的服务器IP:8501`

**优点**: 容易迁移，环境一致
**缺点**: 需要服务器或云平台

---

### 方案四：云服务器部署

#### 使用腾讯云/阿里云/AWS

1. **创建云服务器**
   - 选择 Ubuntu 20.04
   - 开放 8501 端口

2. **安装环境**
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip3 install streamlit openai
   ```

3. **上传文件**
   ```bash
   scp chatbot_deploy.py user@服务器IP:/home/user/
   ```

4. **运行应用**
   ```bash
   nohup streamlit run chatbot_deploy.py --server.port 8501 --server.address 0.0.0.0 &
   ```

5. **访问**
   - 通过 `http://服务器IP:8501` 访问

**优点**: 公网可访问，24小时在线
**缺点**: 需要付费，需要配置外部 API

---

### 方案五：移动端 App

#### 使用 Streamlit 转换为 PWA

1. **修改配置**
   在 `.streamlit/config.toml` 添加：
   ```toml
   [client]
   showSidebarNavigation = false
   
   [ui]
   hideTopBar = true
   ```

2. **添加 PWA 支持**
   用户可以在手机浏览器中"添加到主屏幕"

#### 使用 BeeWare（Python → 原生 App）

1. **安装 BeeWare**
   ```bash
   pip install briefcase
   ```

2. **创建 App 项目**
   ```bash
   briefcase new
   ```

3. **适配聊天界面**
   需要重写界面为原生控件

**优点**: 真正的手机 App
**缺点**: 开发复杂度高

---

## 🔧 部署文件说明

### `chatbot_deploy.py`
- 优化的部署版本
- 支持环境变量配置
- 错误处理更完善
- 中文界面优化

### `.streamlit/config.toml`
- Streamlit 应用配置
- 服务器端口和地址设置

### `.streamlit/secrets.toml`
- API 密钥和端点配置
- 生产环境敏感信息

### `Dockerfile`
- Docker 容器化配置
- 适合云平台部署

### `requirements.txt`
- Python 依赖包列表
- 确保部署环境一致

---

## 📱 推荐部署方案

**个人使用**: 方案二（本地网络分享）
**团队使用**: 方案三（Docker + 内网服务器）
**公开分享**: 方案一（Streamlit Cloud + 外部 API）
**商业用途**: 方案四（云服务器 + 自建 API）

---

## 🚀 快速开始

1. **测试部署版本**
   ```bash
   streamlit run chatbot_deploy.py --server.port 8510
   ```

2. **访问测试**
   打开 `http://localhost:8510`

3. **选择部署方案**
   根据需求选择上述方案之一

4. **分享给朋友**
   提供访问链接即可！

---

现在你可以轻松地将 AI 聊天机器人分享给任何人使用了！🎉