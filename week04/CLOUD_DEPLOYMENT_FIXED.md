# 云端聊天机器人部署指南 - 修复版

## 问题解决

### 原始问题
- **ModuleNotFoundError**: `from bs4 import BeautifulSoup` 导入失败
- **依赖项配置错误**: Streamlit Cloud 无法正确识别和安装依赖包

### 解决方案

1. **更新了依赖项配置**：
   - 使用标准的 `requirements.txt` 文件名
   - 简化依赖项版本要求
   - 确保所有必需包都正确列出

2. **改进了错误处理**：
   - 添加了导入检查机制
   - 提供清晰的错误信息
   - 实现了优雅的降级功能

## 部署步骤

### 在 Streamlit Cloud 上部署

1. **登录 Streamlit Cloud**
   - 访问：https://share.streamlit.io/
   - 使用你的 GitHub 账户登录

2. **创建新应用**
   - 点击 "New app"
   - 选择仓库：`WangZetian-IVERSON/python_01`
   - 分支：`main`
   - 主文件路径：`week04/enhanced_cloud_app.py`

3. **配置 Secrets**
   ```toml
   DEEPSEEK_API_KEY = "sk-4483325f3b24494ea26de5b89b3bd98f"
   APP_PASSWORD = "20040311"
   ```

4. **部署设置**
   - Python 版本：3.9+
   - Requirements 文件：`week04/requirements.txt`

## 依赖项说明

### requirements.txt
```
streamlit>=1.28.0
openai>=1.0.0
requests>=2.25.0
beautifulsoup4>=4.10.0
```

### 功能说明

1. **Web 抓取功能**：
   - 使用 BeautifulSoup4 解析网页内容
   - 智能提取文本，过滤样式和脚本
   - 支持常见网页格式

2. **PDF 处理功能**：
   - 云端版本显示警告信息
   - 提供替代方案指引
   - 建议使用本地版本进行完整PDF处理

3. **AI 对话功能**：
   - 集成 DeepSeek API
   - 支持思考过程显示
   - 智能响应格式化

## 错误处理

### 导入错误处理
- 检查每个关键库的可用性
- 显示清晰的错误消息
- 提供解决方案指引

### API 错误处理
- 检查 API 密钥配置
- 处理余额不足错误
- 提供配置指南

## 使用说明

1. **访问应用**：部署成功后，Streamlit 会提供一个公开URL

2. **登录认证**：输入密码 `20040311`

3. **使用功能**：
   - **网页分析**：输入URL获取网页内容摘要
   - **文档输入**：直接粘贴文本进行分析
   - **AI对话**：与DeepSeek模型进行智能对话

## 故障排除

### 常见问题

1. **ModuleNotFoundError**
   - 确认 requirements.txt 文件路径正确
   - 检查依赖项拼写
   - 重新构建应用

2. **API 错误**
   - 检查 Secrets 配置
   - 确认 API 密钥有效性
   - 检查账户余额

3. **网页抓取失败**
   - 某些网站可能有反爬虫机制
   - 尝试使用不同的URL
   - 检查网络连接

### 联系支持
如果遇到问题，请：
1. 检查 Streamlit Cloud 日志
2. 确认所有配置正确
3. 查看应用状态页面

## 版本信息
- 应用版本：v2.1 (修复版)
- 更新日期：2025-09-25
- GitHub 提交：9b37268