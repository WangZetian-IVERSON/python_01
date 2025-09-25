# 🚀 Cloudflare Tunnel 快速设置

## 下载和使用 Cloudflare Tunnel

### 方法1：手动下载
1. 访问：https://github.com/cloudflare/cloudflared/releases
2. 下载：cloudflared-windows-amd64.exe
3. 重命名为：cloudflared.exe
4. 放到任意文件夹

### 方法2：PowerShell 下载
```powershell
# 创建文件夹
mkdir C:\cloudflared
cd C:\cloudflared

# 下载 cloudflared
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"
```

### 使用方法：
```bash
# 1. 确保你的聊天机器人在运行（端口8514）
cd C:/Users/30502/pfad/week04
streamlit run chatbot_secure.py --server.port 8514 --server.address 0.0.0.0

# 2. 新开终端，运行cloudflared
cd C:\cloudflared
cloudflared.exe tunnel --url http://localhost:8514
```

### 获得的链接示例：
```
https://abc-def-ghi.trycloudflare.com
```

**这个链接是临时的，但比本地IP稳定得多！**

---

## 🎯 更稳定的方案：Streamlit Cloud

如果你想要永久固定的链接，我推荐部署到 Streamlit Cloud：

1. **创建GitHub仓库**
2. **推送聊天机器人代码**
3. **在 share.streamlit.io 部署**
4. **获得固定链接**：如 `yourapp.streamlit.app`

需要我帮你设置吗？