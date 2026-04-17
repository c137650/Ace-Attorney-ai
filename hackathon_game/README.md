# AI 辩论游戏 - Pygame 原型

> 用矩形表示各部分，方便后期替换素材

---

## 📁 文件结构

```
hackathon_game/
├── main.py              ← 主程序
├── README.md            ← 本文档
└── assets/              ← 素材目录
    └── background.png   ← 背景图（可选）
```

---

## 🚀 运行方法

```bash
# 1. 安装 pygame
pip install pygame

# 2. 运行
cd E:\hackson\game\hackathon_game
python main.py
```

---

## 🎮 操作说明

| 按键 | 功能 |
|------|------|
| **1** | 玩家方一辩发言 |
| **2** | 玩家方二辩发言 |
| **3** | 玩家方三辩发言 |
| **7** | 对手方一辩发言 |
| **8** | 对手方二辩发言 |
| **9** | 对手方三辩发言 |
| **空格** | 清除发言状态 |
| **ESC** | 退出游戏 |

---

## 🎨 界面布局

```
┌────────────────────────────────────────────────────────────┬──────────┐
│                       玩 家 方 (蓝色)                     │          │
│                     ┌──────────────┐                      │          │
│                     │    教练      │ ← 2号辩手后方       │  👨‍⚖️  │
│                     └──────────────┘                      │  裁 判  │
│        ┌─────┐   ┌─────┐   ┌─────┐                       │          │
│        │ 一辩│   │ 二辩│   │ 三辩│                       │          │
│ ═══════════════════════════════════════════════════════════╪══════════│
│ ═══════════════════════════════════════════════════════════╪══════════│
│        │ 一辩│   │ 二辩│   │ 三辩│                       │          │
│        └─────┘   └─────┘   └─────┘                       │          │
│                     ┌──────────────┐                      │          │
│                     │  AI教练      │ ← 2号辩手后方       │          │
│                     └──────────────┘                      │          │
│                       对 手 方 (红色)                     │          │
└──────────────────────────────────────────────────────────┴──────────┘

【布局参数】
玩家方：教练(80) → 辩手(185) → 桌子(290)
对手方：教练(620) → 辩手(450) → 桌子(360)

教练始终在2号辩手的后方（对齐2号X位置）
```

---

## 🔧 配置说明

### 颜色配置 (main.py 第21行)

```python
COLORS = {
    "background": (25, 25, 35),        # 背景色
    "player_side": (66, 133, 244),     # 玩家方蓝色
    "opponent_side": (234, 67, 53),   # 对手方红色
    "judge": (251, 188, 5),            # 裁判黄色
    "table": (139, 90, 43),            # 桌子棕色
    "coach_seat": (100, 100, 120),    # 教练席灰蓝
    "highlight": (255, 215, 0),        # 发言高亮金色
}
```

### 布局配置 (LayoutConfig 类)

```python
class LayoutConfig:
    # 玩家方区域位置
    player_zone = {
        "y": 80,           # 区域顶部Y坐标
        "coach_y": 90,     # 教练席Y坐标
        "debater_y": 180,  # 辩手席Y坐标
        "table_y": 250,    # 桌子Y坐标
    }

    # 对手方区域位置
    opponent_zone = {
        "coach_y": 530,    # 教练席Y坐标
        "debater_y": 460,  # 辩手席Y坐标
        "table_y": 420,    # 桌子Y坐标
    }

    # 裁判区域
    judge_zone = {
        "x": 1100,         # X坐标
        "width": 160,      # 宽度
    }
```

---

## 🖼️ 替换素材

### 方法1：替换背景图

在 `assets/` 目录下放置 `background.png` 图片即可。

```bash
# 例如：
E:\hackson\game\hackathon_game\assets\background.png
```

### 方法2：修改代码使用图片

在 `draw_debaters()` 等方法中，用 `pygame.image.load()` 加载图片替换矩形。

```python
def draw_debaters(self):
    """绘制辩手 - 未来可替换为图片"""
    for debater in self.debaters:
        # 如果有对应图片，加载图片
        img_path = f"assets/{debater.side}_{debater.name}.png"
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
            self.screen.blit(img, debater.rect)
        else:
            # 使用矩形作为占位符
            pygame.draw.rect(self.screen, debater.get_color(), debater.rect)
```

---

## 📝 辩手数据结构

```python
class Debater:
    name: str       # "一辩" / "二辩" / "三辩"
    side: str       # "player" / "opponent"
    index: int      # 0, 1, 2
    is_speaking: bool  # 是否正在发言
    rect: pygame.Rect  # 位置矩形
```

---

## 🔌 后续开发接口

当需要接入后端AI时，可以添加：

```python
class Game:
    def submit_instruction(self, text: str):
        """玩家提交教练指令"""
        # 调用AI生成辩手发言
        # 更新对话记录
        pass

    def get_current_state(self) -> dict:
        """获取当前游戏状态"""
        return {
            "phase": "opening",
            "current_side": "player",
            "current_debater": "一辩",
            "is_speaking": True,
            "record": [...]
        }
```

---

## 📋 待办事项

- [ ] 添加角色立绘图片
- [ ] 添加裁判立绘图片
- [ ] 添加桌子背景图
- [ ] 添加发言气泡UI
- [ ] 添加输入框组件
- [ ] 接入后端AI
- [ ] 添加存档/读档功能

---

*文档：布洛妮娅 | Hackathon 游戏原型*
