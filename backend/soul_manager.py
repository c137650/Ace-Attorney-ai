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


# 全局单例
_soul_manager = None


def get_soul_manager() -> SoulManager:
    """获取Soul管理器单例"""
    global _soul_manager
    if _soul_manager is None:
        _soul_manager = SoulManager()
    return _soul_manager
