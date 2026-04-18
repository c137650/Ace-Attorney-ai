"""
配置文件
"""

# 窗口配置（与前端保持一致）
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# 辩手配置
DEBATERS = {
    "player": {
        0: {"name": "一辩", "role": "affirmative"},
        1: {"name": "二辩", "role": "rebuttal"},
        2: {"name": "三辩", "role": "questioner"},
    },
    "opponent": {
        0: {"name": "一辩", "role": "affirmative"},
        1: {"name": "二辩", "role": "rebuttal"},
        2: {"name": "三辩", "role": "questioner"},
    }
}

# 发言字数限制
WORD_LIMITS = {
    "opening": {"min": 50, "max": 100},      # 开篇立论
    "rebuttal": {"min": 50, "max": 100},     # 驳论
    "question": {"min": 50, "max": 100},     # 质询
    "free_debate": {"min": 50, "max": 100}, # 自由辩论
    "closing": {"min": 50, "max": 100},      # 总结陈词
}

# 环节配置
DEBATE_PHASES = [
    {"id": "opening", "name": "开篇立论", "order": 1},
    {"id": "rebuttal", "name": "驳论", "order": 2},
    {"id": "question", "name": "质询", "order": 3},
    {"id": "free_debate", "name": "自由辩论", "order": 4},
    {"id": "closing", "name": "总结陈词", "order": 5},
]

# 教练指导字数限制
COACH_GUIDANCE_MAX_WORDS = 50

# 自由辩论轮数
FREE_DEBATE_ROUNDS = 10
