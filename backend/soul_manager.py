"""
Soul管理器
管理辩手和教练的灵魂配置
"""

import os
import shutil
from typing import Dict, Optional


class SoulManager:
    """Soul管理器"""

    def __init__(self, souls_dir: str = None, memories_dir: str = None):
        if souls_dir is None:
            souls_dir = os.path.join(os.path.dirname(__file__), "souls")
        if memories_dir is None:
            memories_dir = os.path.join(os.path.dirname(__file__), "memories")

        self.souls_dir = souls_dir
        self.memories_dir = memories_dir

        # 确保目录存在
        os.makedirs(self.souls_dir, exist_ok=True)
        os.makedirs(self.memories_dir, exist_ok=True)

        # Soul文件映射
        self.soul_files = {
            "player_debater_1": "player_debater_1.md",
            "player_debater_2": "player_debater_2.md",
            "player_debater_3": "player_debater_3.md",
            "opponent_debater_1": "opponent_debater_1.md",
            "opponent_debater_2": "opponent_debater_2.md",
            "opponent_debater_3": "opponent_debater_3.md",
            "player_coach": "player_coach.md",
            "opponent_coach": "opponent_coach.md",
        }

        # 记忆文件映射
        self.memory_files = {
            "player_debater_1": "player_debater_1.md",
            "player_debater_2": "player_debater_2.md",
            "player_debater_3": "player_debater_3.md",
            "opponent_debater_1": "opponent_debater_1.md",
            "opponent_debater_2": "opponent_debater_2.md",
            "opponent_debater_3": "opponent_debater_3.md",
        }

    def get_soul(self, agent_id: str) -> str:
        """
        获取Agent的Soul

        Args:
            agent_id: Agent标识符

        Returns:
            Soul文本内容
        """
        if agent_id not in self.soul_files:
            return ""

        file_path = os.path.join(self.souls_dir, self.soul_files[agent_id])
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def set_soul(self, agent_id: str, content: str) -> bool:
        """
        设置Agent的Soul（仅限玩家可编辑的Agent）

        Args:
            agent_id: Agent标识符
            content: Soul内容

        Returns:
            是否成功
        """
        # 检查是否是玩家可编辑的Agent
        player_editable = ["player_debater_1", "player_debater_2", "player_debater_3"]
        if agent_id not in player_editable:
            print(f"⚠ {agent_id} 不可由玩家编辑")
            return False

        if agent_id not in self.soul_files:
            return False

        file_path = os.path.join(self.souls_dir, self.soul_files[agent_id])
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"⚠ 保存Soul失败: {e}")
            return False

    def reset_soul(self, agent_id: str) -> bool:
        """
        重置Soul到初始模板

        Args:
            agent_id: Agent标识符

        Returns:
            是否成功
        """
        # 查找初始模板（如果有备份的话）
        backup_file = os.path.join(self.souls_dir, f"{agent_id}.backup.md")
        if os.path.exists(backup_file):
            file_path = os.path.join(self.souls_dir, self.soul_files[agent_id])
            shutil.copy(backup_file, file_path)
            return True
        return False

    def backup_souls(self):
        """备份所有Soul文件"""
        for agent_id, filename in self.soul_files.items():
            file_path = os.path.join(self.souls_dir, filename)
            backup_path = os.path.join(self.souls_dir, f"{agent_id}.backup.md")
            if os.path.exists(file_path):
                shutil.copy(file_path, backup_path)
        print("✓ Soul模板已备份")

    def restore_souls(self):
        """从备份恢复所有Soul文件"""
        for agent_id, filename in self.soul_files.items():
            backup_path = os.path.join(self.souls_dir, f"{agent_id}.backup.md")
            file_path = os.path.join(self.souls_dir, filename)
            if os.path.exists(backup_path):
                shutil.copy(backup_path, file_path)
        print("✓ Soul模板已恢复")

    def add_memory(self, agent_id: str, phase: str, content: str) -> bool:
        """
        添加记忆

        Args:
            agent_id: Agent标识符
            phase: 辩论阶段
            content: 发言内容

        Returns:
            是否成功
        """
        if agent_id not in self.memory_files:
            return False

        file_path = os.path.join(self.memories_dir, self.memory_files[agent_id])

        try:
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n## [{phase}] {content}\n")
            return True
        except Exception as e:
            print(f"⚠ 添加记忆失败: {e}")
            return False

    def get_memory(self, agent_id: str) -> str:
        """
        获取记忆

        Args:
            agent_id: Agent标识符

        Returns:
            记忆内容
        """
        if agent_id not in self.memory_files:
            return ""

        file_path = os.path.join(self.memories_dir, self.memory_files[agent_id])
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""

    def clear_memory(self, agent_id: str = None):
        """
        清除记忆

        Args:
            agent_id: Agent标识符（None则清除所有）
        """
        if agent_id:
            if agent_id in self.memory_files:
                file_path = os.path.join(self.memories_dir, self.memory_files[agent_id])
                if os.path.exists(file_path):
                    os.remove(file_path)
        else:
            # 清除所有记忆
            for filename in self.memory_files.values():
                file_path = os.path.join(self.memories_dir, filename)
                if os.path.exists(file_path):
                    os.remove(file_path)

    def init_memory(self, agent_id: str, agent_name: str, stance: str):
        """
        初始化记忆文件

        Args:
            agent_id: Agent标识符
            agent_name: Agent名称
            stance: 立场
        """
        if agent_id not in self.memory_files:
            return

        file_path = os.path.join(self.memories_dir, self.memory_files[agent_id])

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"# {agent_name} - 辩论记忆\n")
            f.write(f"## 基础信息\n")
            f.write(f"- 立场: {stance}\n")
            f.write(f"- 创建时间: {self._get_timestamp()}\n")
            f.write(f"\n## 发言记录\n")

    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def get_all_souls(self) -> Dict[str, str]:
        """获取所有Soul"""
        souls = {}
        for agent_id in self.soul_files:
            souls[agent_id] = self.get_soul(agent_id)
        return souls

    def get_player_editable_agents(self) -> list:
        """获取玩家可编辑的Agent列表"""
        return ["player_debater_1", "player_debater_2", "player_debater_3"]

    def get_all_agent_ids(self) -> list:
        """获取所有Agent ID列表"""
        return list(self.soul_files.keys())

    def get_agent_name(self, agent_id: str) -> str:
        """获取Agent名称"""
        names = {
            "player_debater_1": "正方一辩「张明」",
            "player_debater_2": "正方二辩「李华」",
            "player_debater_3": "正方三辩「王强」",
            "opponent_debater_1": "反方一辩「陈思」",
            "opponent_debater_2": "反方二辩「赵敏」",
            "opponent_debater_3": "反方三辩「刘洋」",
            "player_coach": "正方教练「陈指导」",
            "opponent_coach": "反方教练「王指导」",
        }
        return names.get(agent_id, agent_id)

    def is_player_editable(self, agent_id: str) -> bool:
        """检查Agent是否可由玩家编辑"""
        return agent_id in ["player_debater_1", "player_debater_2", "player_debater_3"]

    def save_soul(self, agent_id: str, content: str) -> bool:
        """保存Soul"""
        if not self.is_player_editable(agent_id):
            print(f"⚠ {agent_id} 不可编辑")
            return False

        if agent_id not in self.soul_files:
            return False

        file_path = os.path.join(self.souls_dir, self.soul_files[agent_id])
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"⚠ 保存Soul失败: {e}")
            return False

    def reset_to_template(self, agent_id: str) -> bool:
        """重置为模板"""
        if not self.is_player_editable(agent_id):
            return False

        templates = {
            "player_debater_1": """# 正方一辩 马嘶克 - 灵魂配置

## 基础信息
- **名字**: 马嘶克
- **阵营**: 马方（正方）
- **辩位**: 一辩（开篇立论）
- **技能**: 钞能力（使用后本回合内：心态+5）

## 六维数值
| 维度 | 数值 | 说明 |
|------|------|------|
| 心态 | 3 | 稳定冷静 |
| 逻辑 | 2 | 基础逻辑 |
| 技巧性 | 4 | 擅长技巧 |
| 口语性 | 3 | 表达流畅 |
| 攻击性 | 2 | 温和进攻 |
| 感染力 | 3 | 中等感染 |

## 性格特征
- 财大气粗
- 自信满满
- 简洁直接
- 偶尔嘶嘶啼叫

## 说话风格
- 表达非常简洁
- 时不时会插入"嘶嘶嘶嘶"啼叫声
- 语气傲慢自信
- 金句频出

## 专长
- 开篇立论
- 用资本逻辑碾压对手
- 简短有力的总结

## 系统提示词
你扮演正方一辩马嘶克。你是马方阵营的精英辩手，拥有钞能力。你的说话风格非常简洁，时不时会插入"嘶嘶嘶嘶"的啼叫声。语气傲慢自信，但逻辑清晰。发言要简短有力，体现资本家的强势风格。""",
            "player_debater_2": """# 正方二辩 赵高 - 灵魂配置

## 基础信息
- **名字**: 赵高
- **阵营**: 马方（正方）
- **辩位**: 二辩（驳论）
- **技能**: 指鹿为马（使用后本回合内：心态+3，逻辑+2）

## 六维数值
| 维度 | 数值 | 说明 |
|------|------|------|
| 心态 | 5 | 极其稳定 |
| 逻辑 | 4 | 较强逻辑 |
| 技巧性 | 5 | 技巧丰富 |
| 口语性 | 3 | 表达流畅 |
| 攻击性 | 4 | 强力进攻 |
| 感染力 | 5 | 极强感染 |

## 性格特征
- 阴险狡诈
- 善于偷换概念
- 情绪化表达
- 掌控全局

## 说话风格
- 说话比较情绪化
- 经常偷换概念并加以掩饰
- 擅长颠倒黑白
- 语气强势逼人

## 专长
- 驳论反驳
- 偷换概念
- 逻辑陷阱
- 情绪操控

## 系统提示词
你扮演正方二辩赵高。你是马方阵营的老谋深算辩手，擅长指鹿为马的诡辩技巧。你的说话风格比较情绪化，经常偷换概念并巧妙掩饰。善于把黑的说成白的，把死的说成活的。在辩论中要发挥你偷换概念的专长，让对手陷入你的逻辑陷阱。""",
            "player_debater_3": """# 正方三辩 塞马娘 - 灵魂配置

## 基础信息
- **名字**: 塞马娘
- **阵营**: 马方（正方）
- **辩位**: 三辩（质询/总结）
- **技能**: 曼波！（使用后本回合内：口语性+5）

## 六维数值
| 维度 | 数值 | 说明 |
|------|------|------|
| 心态 | 3 | 稳定乐观 |
| 逻辑 | 2 | 基础逻辑 |
| 技巧性 | 2 | 基础技巧 |
| 口语性 | 5 | 极其活泼 |
| 攻击性 | 3 | 中等进攻 |
| 感染力 | 5 | 极强感染 |

## 性格特征
- 活泼可爱
- 元气满满
- 充满热情
- 萌系风格

## 说话风格
- 所有的人称代词都用"哈基米"替换
- 说话活泼可爱
- 经常说"曼波！"
- 元气十足

## 专长
- 质询提问
- 情感攻势
- 感染观众
- 可爱攻势

## 系统提示词
你扮演正方三辩塞马娘。你是马方阵营元气满满的可爱辩手。你的说话风格极其独特，所有的人称代词都要用"哈基米"替换！比如"我"要说"塞马娘"或"哈基米"，"你"要说"哈基米"或"那匹哈基米"。经常说"曼波！"来表示兴奋。发言要活泼可爱，元气满满，充满感染力。""",
        }

        if agent_id in templates:
            file_path = os.path.join(self.souls_dir, self.soul_files[agent_id])
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(templates[agent_id])
                return True
            except Exception as e:
                print(f"⚠ 重置模板失败: {e}")
                return False

        return False


# 全局单例
_soul_manager = None


def get_soul_manager() -> SoulManager:
    """获取Soul管理器单例"""
    global _soul_manager
    if _soul_manager is None:
        _soul_manager = SoulManager()
    return _soul_manager
