# 🤖 AI 辩论赛

一个人工智能辩论游戏，玩家作为教练指导己方辩手，与AI辩手进行辩论对决。

## 🎮 游戏特色

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
├── hackathon_game/       # Pygame前端
│   ├── main.py          # 游戏主程序
│   ├── menu.py          # 菜单界面
│   ├── soul_editor.py   # Soul编辑器
│   └── topic_select.py   # 立场选择
└── README.md
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pygame
```

### 2. 运行游戏

```bash
cd hackathon_game
python main.py
```

### 3. 游戏操作

| 按键 | 功能 |
|------|------|
| **1** | 开始游戏 |
| **2** | Soul编辑 |
| **M** | 切换AI/演示模式 |
| **Tab** | 激活/关闭输入 |
| **Enter** | 发送指导 |
| **空格** | 使用默认指导 |
| **V** | 查看AI灵魂 |
| **ESC** | 退出 |

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

## 📋 辩题列表

| # | 辩题 |
|---|------|
| 1 | AI是否应该取代教师 |
| 2 | 电子游戏对青少年的利弊 |
| 3 | 996工作制应该被禁止 |
| 4 | 大学生先就业还是先择业 |
| 5 | 网络舆论对司法公正的影响 |

## 🛠️ 技术栈

- **前端**：Python + Pygame
- **后端**：Python 辩论逻辑
- **AI**：OpenAI GPT / Ollama（可选）

## 📄 许可证

MIT License

---

> *"逻辑是武器，语言是盾牌，辩论是战场。"*
