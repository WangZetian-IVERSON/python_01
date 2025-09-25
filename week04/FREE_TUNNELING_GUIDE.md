# 完全免费的公网分享方案

## 🆓 免费内网穿透方案对比

### 方案1：Serveo（推荐 - 完全免费）

**优点**：
- ✅ 完全免费
- ✅ 无需注册
- ✅ 一行命令搞定
- ✅ 支持自定义子域名

**使用方法**：
```bash
# 启动聊天机器人
streamlit run chatbot_deploy.py --server.port 8501

# 新开终端，运行 serveo
ssh -R 80:localhost:8501 serveo.net
```

会获得类似：`https://randomname.serveo.net` 的链接

**自定义域名**：
```bash
ssh -R yourname:80:localhost:8501 serveo.net
```
获得：`https://yourname.serveo.net`

---

### 方案2：localhost.run（完全免费）

**使用方法**：
```bash
ssh -R 80:localhost:8501 ssh.localhost.run
```

获得类似：`https://abc-123-456-789.lhr.life` 的链接

---

### 方案3：bore.pub（免费）

**安装**：
```bash
npm install -g @boringcodes/bore-cli
```

**使用**：
```bash
bore 8501 bore.pub
```

---

### 方案4：Cloudflare Tunnel（免费，稳定）

**安装 cloudflared**：
1. 下载：https://github.com/cloudflare/cloudflared/releases
2. 解压到文件夹

**使用**：
```bash
cloudflared tunnel --url http://localhost:8501
```

获得 `https://xxx.trycloudflare.com` 链接

**优点**：
- ✅ Cloudflare 提供，稳定可靠
- ✅ 完全免费
- ✅ 无需注册
- ✅ 高速 CDN

---

## 🎯 我的推荐排序：

### 1. **Cloudflare Tunnel**（最稳定）
- 大公司背景，最可靠
- 全球 CDN，速度快

### 2. **Serveo**（最简单）
- 无需安装任何软件
- SSH 命令直接使用

### 3. **ngrok 免费版**（功能最全）
- 界面友好，功能丰富
- 但有流量限制

## 🚀 快速测试 Cloudflare Tunnel：

1. **下载 cloudflared**：
   - 访问：https://github.com/cloudflare/cloudflare/releases
   - 下载 Windows 版本
   - 解压到 `C:/cloudflared/`

2. **启动聊天机器人**：
   ```bash
   cd C:/Users/30502/pfad/week04
   streamlit run chatbot_deploy.py --server.port 8501
   ```

3. **运行 Cloudflare Tunnel**：
   ```bash
   C:/cloudflared/cloudflared.exe tunnel --url http://localhost:8501
   ```

4. **获得公网链接**：
   终端会显示类似：
   ```
   https://abc-def-ghi.trycloudflare.com
   ```

**这个链接可以分享给全世界任何人！完全免费！**

---

## 💡 总结：

**如果你想要**：
- **最简单** → Serveo (SSH 命令)
- **最稳定** → Cloudflare Tunnel
- **最功能全** → ngrok 免费版
- **完全零成本** → 任何一个都是免费的！

你想试试哪个方案？我可以帮你详细设置！