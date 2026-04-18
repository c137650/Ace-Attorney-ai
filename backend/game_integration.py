"""
辩论游戏对接层
连接前端（Pygame）和后端（辩论逻辑）
"""

import os
import sys

# 设置编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from typing import Optional, Tuple
from debate_flow import DebateFlow
from game_state import create_initial_state, TurnType, Topic, GamePhase
from topic_loader import get_random_topic
from config import FREE_DEBATE_ROUNDS


class DebateGame:
    """辩论游戏控制器 - 前端调用的接口"""

    def __init__(self, topic: Optional[Topic] = None, use_simple_agents: bool = True, use_llm: bool = False, player_stance: str = None):
        """
        初始化辩论游戏

        Args:
            topic: 辩题（如果不提供则随机选择）
            use_simple_agents: 是否使用简化AI（不调用真实LLM）
            use_llm: 是否使用LLM生成内容
            player_stance: 玩家立场 ("A" 或 "B")
        """
        # 加载或随机选择辩题
        if topic is None:
            topic = get_random_topic()

        # 创建游戏状态（指定玩家立场）
        self.state = create_initial_state(topic, player_stance=player_stance)

        # 创建辩论流程
        self.flow = DebateFlow(self.state, use_simple_agents=use_simple_agents, use_llm=use_llm)

        # 记录是否使用LLM
        self.use_llm = use_llm and not use_simple_agents

        if self.use_llm:
            print(f"✓ LLM模式已启用")

        # 初始化Memory
        self._init_memories()

        # 辩手状态缓存（用于前端显示）
        self.speaker_states = {
            "player": {0: False, 1: False, 2: False},
            "opponent": {0: False, 1: False, 2: False}
        }

        # 当前环节信息
        self.phase_info = {
            "name": "开篇立论",
            "step": 1,
            "total_steps": 2,
            "is_player_turn": True,
            "current_speaker_name": "玩家方一辩",
            "current_speaker_side": "player",
            "current_speaker_index": 0
        }

        # 发言内容缓存（用于前端显示）
        self.current_speech = ""
        self.speech_history = []

        # 根据立场和环节同步初始发言信息
        self.update_phase_info()

    def _init_memories(self):
        """初始化Memory文件"""
        try:
            from soul_manager import get_soul_manager
            manager = get_soul_manager()

            # 辩手名称映射
            debater_names = {
                "player_debater_1": "马嘶克",
                "player_debater_2": "赵高",
                "player_debater_3": "赛马娘",
                "opponent_debater_1": "驴嘶克",
                "opponent_debater_2": "赵高",
                "opponent_debater_3": "赛驴娘",
            }

            # 初始化每个辩手的Memory
            for agent_id, name in debater_names.items():
                stance = "正方" if "player" in agent_id else "反方"
                manager.init_memory(agent_id, name, stance)

            print("✓ Memory文件已初始化")
        except Exception as e:
            print(f"⚠ Memory初始化失败: {e}")

    def get_memories(self) -> dict:
        """获取所有辩手的Memory"""
        try:
            from soul_manager import get_soul_manager
            manager = get_soul_manager()

            memories = {}
            for agent_id in ["player_debater_1", "player_debater_2", "player_debater_3",
                           "opponent_debater_1", "opponent_debater_2", "opponent_debater_3"]:
                memories[agent_id] = manager.get_memory(agent_id)
            return memories
        except Exception as e:
            print(f"获取Memory失败: {e}")
            return {}

    @property
    def topic(self) -> Topic:
        """获取当前辩题"""
        return self.state.topic

    @property
    def player_stance(self) -> str:
        """获取玩家方立场 (A 或 B)"""
        return self.state.player_stance

    @property
    def player_stance_text(self) -> str:
        """获取玩家方立场文字"""
        if self.player_stance == "A":
            return self.state.topic.stance_a
        else:
            return self.state.topic.stance_b

    def get_current_phase(self) -> str:
        """获取当前环节"""
        return self.state.current_phase

    def get_phase_name(self) -> str:
        """获取当前环节名称"""
        phase_names = {
            "opening": "开篇立论",
            "rebuttal": "驳论",
            "question": "质询",
            "free_debate": "自由辩论",
            "closing": "总结陈词"
        }
        return phase_names.get(self.state.current_phase, "未知环节")

    def is_player_turn(self) -> bool:
        """是否是玩家回合"""
        return self.state.current_turn in [
            TurnType.PLAYER_SPEAK,
            TurnType.PLAYER_QUESTION,
            TurnType.PLAYER_ANSWER,
            TurnType.PLAYER_COACH_GUIDANCE
        ]

    def get_current_speaker(self) -> Tuple[str, int, str]:
        """
        获取当前发言者信息

        Returns:
            (side, index, name) - 阵营、辩手索引、辩手名称
        """
        speaker = self.state.get_current_speaker()
        return (speaker["side"], speaker["index"], speaker["name"])

    def update_phase_info(self):
        """更新环节信息"""
        speaker = self.state.get_current_speaker()
        positive_side = self.state.get_positive_side()

        # 更新当前发言者
        side_name = "正方" if speaker["side"] == positive_side else "反方"
        self.phase_info["current_speaker_name"] = f"{side_name}{speaker['name']}"
        self.phase_info["current_speaker_side"] = speaker["side"]
        self.phase_info["current_speaker_index"] = speaker["index"]
        self.phase_info["name"] = self.get_phase_name()
        self.phase_info["is_player_turn"] = self.is_player_turn()

        # 计算步骤
        if self.state.current_phase == "opening":
            self.phase_info["step"] = self.state.current_round
            self.phase_info["total_steps"] = 2
        elif self.state.current_phase == "rebuttal":
            self.phase_info["step"] = self.state.current_round
            self.phase_info["total_steps"] = 2
        elif self.state.current_phase == "question":
            self.phase_info["step"] = self.state.current_round
            self.phase_info["total_steps"] = 4
        elif self.state.current_phase == "free_debate":
            self.phase_info["step"] = self.state.free_debate_round + 1
            self.phase_info["total_steps"] = FREE_DEBATE_ROUNDS
        elif self.state.current_phase == "closing":
            self.phase_info["step"] = self.state.current_round
            self.phase_info["total_steps"] = 2

    def process_player_guidance(
        self,
        guidance: str,
        free_debate_target_index: Optional[int] = None,
        free_debate_asker_index: Optional[int] = None,
    ) -> dict:
        """
        处理玩家教练指导

        Args:
            guidance: 玩家输入的教练指导

        Returns:
            {
                "success": bool,
                "speech": str,  # 辩手发言内容
                "speaker_name": str,  # 发言辩手名称
                "speaker_side": str,  # 发言辩手阵营
                "speaker_index": int,  # 发言辩手索引
                "is_complete": bool,  # 环节是否完成
                "next_phase": str  # 下一环节（如果完成）
            }
        """
        # 重置发言状态
        self._reset_speaker_states()

        # 获取当前发言者
        speaker = self.state.get_current_speaker()
        side, index, name = speaker["side"], speaker["index"], speaker["name"]

        # 执行玩家输入
        result = self.flow.process_player_input(
            guidance,
            free_debate_target_index=free_debate_target_index,
            free_debate_asker_index=free_debate_asker_index,
        )

        # 更新发言状态
        self.speaker_states[side][index] = True
        self.current_speech = result.content

        # 记录到历史
        self.speech_history.append((side, index, result.content))

        # 更新环节信息
        self.update_phase_info()

        return {
            "success": True,
            "speech": result.content,
            "speaker_name": result.speaker_name,
            "speaker_side": side,
            "speaker_index": index,
            "is_complete": self.state.current_phase != self.get_current_phase(),
            "next_phase": self.get_phase_name()
        }

    def advance_turn(self) -> dict:
        """
        推进AI回合

        Returns:
            {
                "success": bool,
                "speech": str,  # 辩手发言内容
                "speaker_name": str,  # 发言辩手名称
                "speaker_side": str,  # 发言辩手阵营
                "speaker_index": int,  # 发言辩手索引
                "is_complete": bool,  # 环节是否完成
                "next_phase": str  # 下一环节（如果完成）
            }
        """
        # 重置发言状态
        self._reset_speaker_states()

        # 获取当前发言者
        speaker = self.state.get_current_speaker()
        side, index, name = speaker["side"], speaker["index"], speaker["name"]

        # 执行AI回合
        result = self.flow.advance_turn()

        # 更新发言状态
        self.speaker_states[side][index] = True
        self.current_speech = result.content

        # 记录到历史
        self.speech_history.append((side, index, result.content))

        # 更新环节信息
        self.update_phase_info()

        return {
            "success": True,
            "speech": result.content,
            "speaker_name": result.speaker_name,
            "speaker_side": side,
            "speaker_index": index,
            "is_complete": False,  # AI回合后不一定完成环节
            "next_phase": self.get_phase_name()
        }

    def get_game_status(self) -> dict:
        """获取游戏状态（用于前端显示）"""
        return {
            "topic": self.topic.title,
            "topic_description": self.topic.description,
            "player_stance": self.player_stance,
            "player_stance_text": self.player_stance_text,
            "current_phase": self.state.current_phase,
            "current_turn": self.state.current_turn.value,
            "phase_name": self.get_phase_name(),
            "current_round": self.state.current_round,
            "is_player_turn": self.is_player_turn(),
            "current_speaker": self.get_current_speaker(),
            "speaker_states": self.speaker_states,
            "phase_info": self.phase_info,
            "current_speech": self.current_speech,
            "speech_history_count": len(self.speech_history)
        }

    def _reset_speaker_states(self):
        """重置发言状态"""
        for side in self.speaker_states:
            for index in self.speaker_states[side]:
                self.speaker_states[side][index] = False

    def is_game_over(self) -> bool:
        """检查游戏是否结束"""
        return self.state.phase in [GamePhase.JUDGMENT, GamePhase.FINISHED] or self.state.current_phase == ""


# 导出
__all__ = ['DebateGame']
