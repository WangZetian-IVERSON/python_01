# 使用内网穿透实现公网访问指南

## 🌐 内网穿透：让本地应用全球可访问

### 方案1：ngrok（推荐）

1. **下载安装 ngrok**
   - 访问 https://ngrok.com
   - 注册账号并下载

2. **启动你的聊天机器人**
   ```bash
   streamlit run chatbot_deploy.py --server.port 8501
   ```

3. **使用 ngrok 暴露端口**
   ```bash
   ngrok http 8501
   ```

4. **获取公网链接**
   ngrok 会提供类似这样的链接：
   ```
   https://abc123.ngrok.io
   ```
   任何人通过这个链接都能访问你的聊天机器人！

**优点**：
- ✅ 免费版可用
- ✅ 支持 HTTPS
- ✅ 全球访问
- ✅ 保持本地 LM Studio

**缺点**：
- ❌ 免费版链接会变化
- ❌ 需要保持电脑开启

---

### 方案2：花生壳（国内）

1. **注册花生壳账号**
   - 访问 https://hsk.oray.com

2. **下载客户端**
   - 安装花生壳内网穿透工具

3. **配置端口映射**
   - 本地端口：8501
   - 协议：HTTP

4. **获取访问域名**
   - 花生壳会分配一个域名
   - 例如：`http://yourname.gicp.net`

---

### 方案3：frp（免费，需要自己搭建）

需要有一台公网服务器作为中转。

---

## 🚀 最简单的公网分享方法

如果你想要最简单的公网分享，我推荐使用 **ngrok**：

### 快速步骤：

1. **启动聊天机器人**
   ```bash
   cd C:/Users/30502/pfad/week04
   streamlit run chatbot_deploy.py --server.port 8501
   ```

2. **下载 ngrok**
   - 去 https://ngrok.com 注册并下载
   - 解压到任意文件夹

3. **运行 ngrok**
   ```bash
   # 在 ngrok 文件夹中运行
   ngrok http 8501
   ```

4. **分享链接**
   - ngrok 显示的 https 链接可以发给任何人
   - 他们无需连接你的 WiFi 即可使用

### 示例效果：
```
ngrok by @inconshreveable

Session Status    online
Account           your-email@example.com
Version           2.3.40
Region            United States (us)
Web Interface     http://127.0.0.1:4040
Forwarding        http://abc123.ngrok.io -> http://localhost:8501
Forwarding        https://abc123.ngrok.io -> http://localhost:8501
```

**分享这个链接：** `https://abc123.ngrok.io`

---

## 📱 网络访问对比总结：

| 方案 | 网络要求 | 费用 | 难度 | 推荐度 |
|------|----------|------|------|--------|
| 本地网络 | 同一WiFi | 免费 | 极简 | ⭐⭐⭐ |
| ngrok | 任何网络 | 免费/付费 | 简单 | ⭐⭐⭐⭐⭐ |
| Streamlit Cloud | 任何网络 | 免费 | 中等 | ⭐⭐⭐⭐ |
| 云服务器 | 任何网络 | 付费 | 复杂 | ⭐⭐⭐⭐ |

---

## 🎯 我的推荐：

**如果朋友在同一个地方**（家/办公室）→ 本地网络分享
**如果朋友在不同地方** → 使用 ngrok 内网穿透
**如果要长期稳定分享** → Streamlit Cloud 或云服务器

你想尝试哪种方案？我可以帮你具体设置！