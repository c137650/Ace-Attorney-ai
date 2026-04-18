# 🤖 AI 辩论赛

一个人工智能辩论游戏，玩家作为教练指导己方辩手，与AI辩手进行辩论对决。

## 🎮 游戏特色

- **Web 端**：开始界面、辩论界面和 Soul 编辑器都在浏览器中完成
- **Soul系统**：为每个辩手定制独特的性格和说话风格
- **Memory系统**：记录辩手的所有发言，供裁判评判
- **LLM支持**：可选接入GPT-4等大语言模型，生成更智能的辩论内容
- **多种辩题**：包含5个热门社会议题

## 📁 项目结构

```
ai-debate-game/
├── backend/              # 后端辩论逻辑
│   ├── agents/          # AI辩手和教练
│   ├── souls/            # 辩手灵魂配置
│   ├── memories/         # 辩手发言记忆
│   ├── topics/           # 辩题库
│   ├── debate_flow.py   # 辩论流程
│   ├── game_state.py    # 游戏状态
│   ├── llm_client.py    # LLM调用
│   └── soul_manager.py   # Soul管理
├── hackathon_game/       # Web 前端入口
│   ├── main.py          # Web 启动器
│   ├── web_server.py    # 兼容入口
│   ├── web_http.py      # 本地 HTTP 服务
│   ├── web_app.py       # Web 业务状态
│   ├── web_frontend.py  # 页面 HTML
│   └── web_data.py      # Soul/辩手数据
└── README.md
```

## 🚀 快速开始

### 1. 运行游戏

```bash
cd hackathon_game
python main.py
```

启动后会自动打开浏览器页面。

### 2. 页面说明

- 开始界面：选择辩题、立场和 LLM 模式
- 辩论界面：输入教练指导并查看发言记录
- Soul 编辑：直接在网页中编辑并保存模板

### 3. 页面操作

| 页面 | 功能 |
|------|------|
| **菜单** | 选择辩题、立场和模式 |
| **辩论** | 输入教练指导、推进 AI 回合 |
| **Soul 编辑** | 编辑并保存辩手模板 |

## ⚙️ LLM配置（可选）

1. 编辑 `backend/config.json`
2. 配置API Key：

```json
{
    "api": {
        "provider": "openai",
        "base_url": "https://api.openai.com/v1",
        "api_key": "你的API_KEY",
        "model": "gpt-4o-mini"
    }
}
```

## 🎯 游戏流程

1. **选择立场** - 随机辩题，选择正方或反方
2. **Soul编辑** - （可选）定制己方辩手性格
3. **辩论对决** - 作为教练给辩手下达战术指导
4. **裁判评判** - 基于Memory记录评定胜负

## 🛠️ 技术栈

- **前端**：浏览器 + HTML/CSS/JavaScript
- **后端**：Python 辩论逻辑
- **AI**：OpenAI GPT / Ollama（可选）

## 📄 许可证

MIT License

---

> *"逻辑是武器，语言是盾牌，辩论是战场。"*
