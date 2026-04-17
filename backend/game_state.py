"""
游戏状态管理
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import random

from config import DEBATERS, DEBATE_PHASES, FREE_DEBATE_ROUNDS


class GamePhase(Enum):
    """游戏阶段"""
    WAITING = "waiting"           # 等待开始
    TOPIC_REVEAL = "topic_reveal" # 辩题公布
    OPENING = "opening"           # 开篇立论
    REBUTTAL = "rebuttal"         # 驳论
    QUESTION = "question"         # 质询
    FREE_DEBATE = "free_debate"   # 自由辩论
    CLOSING = "closing"           # 总结陈词
    JUDGMENT = "judgment"         # 裁判判决
    FINISHED = "finished"         # 结束


class TurnType(Enum):
    """回合类型"""
    PLAYER_SPEAK = "player_speak"         # 玩家方发言
    PLAYER_COACH_GUIDANCE = "player_coach_guidance"  # 玩家方教练指导
    OPPONENT_SPEAK = "opponent_speak"     # 对手方发言
    OPPONENT_COACH_GUIDANCE = "opponent_coach_guidance"  # 对手方教练指导
    # 质询环节专用
    PLAYER_QUESTION = "player_question"   # 玩家方提问（质询）
    PLAYER_ANSWER = "player_answer"       # 玩家方回答（被质询）
    OPPONENT_QUESTION = "opponent_question"  # 对手方提问（质询）
    OPPONENT_ANSWER = "opponent_answer"   # 对手方回答（被质询）
    PHASE_END = "phase_end"              # 环节结束


@dataclass
class Topic:
    """辩题"""
    id: str
    title: str
    description: str
    stance_a: str  # 甲方立场描述
    stance_b: str  # 乙方立场描述


@dataclass
class DebateRound:
    """辩论回合"""
    round_num: int
    phase: str
    speaker_side: str  # "player" or "opponent"
    speaker_index: int  # 0, 1, 2
    turn_type: TurnType
    content: str = ""  # 发言内容或教练指导
    timestamp: Optional[str] = None


@dataclass
class GameState:
    """游戏状态"""
    phase: GamePhase = GamePhase.WAITING
    topic: Optional[Topic] = None

    # 立场分配（随机）
    player_stance: str = "A"  # "A" 或 "B"

    # 当前环节
    current_phase: str = ""
    current_round: int = 0
    current_turn: TurnType = TurnType.PLAYER_SPEAK

    # 自由辩论轮次
    free_debate_round: int = 0

    # 辩论记录
    rounds: list = field(default_factory=list)

    # 玩家教练待指导
    pending_player_guidance: bool = False
    pending_opponent_guidance: bool = False

    def get_current_speaker(self) -> dict:
        """获取当前发言的辩手信息"""
        if self.current_phase == "opening":
            if self.current_round == 1:
                return {"side": "player", "index": 0, "name": "一辩", "role": "立论"}
            else:
                return {"side": "opponent", "index": 0, "name": "一辩", "role": "立论"}
        elif self.current_phase == "rebuttal":
            if self.current_round == 1:
                return {"side": "opponent", "index": 1, "name": "二辩", "role": "驳论"}
            else:
                return {"side": "player", "index": 1, "name": "二辩", "role": "驳论"}
        elif self.current_phase == "question":
            # 质询环节：4个步骤
            # round=1: 玩家方提问, round=2: 对手方回答
            # round=3: 对手方提问, round=4: 玩家方回答
            if self.current_round == 1:
                return {"side": "player", "index": 2, "name": "三辩", "role": "提问"}
            elif self.current_round == 2:
                return {"side": "opponent", "index": 2, "name": "三辩", "role": "回答"}
            elif self.current_round == 3:
                return {"side": "opponent", "index": 2, "name": "三辩", "role": "提问"}
            else:
                return {"side": "player", "index": 2, "name": "三辩", "role": "回答"}
        elif self.current_phase == "free_debate":
            # 自由辩论使用当前轮次来确定辩手（轮次由 free_debate_round 控制）
            # 但这里 current_round 固定为 1，所以用 free_debate_round 来判断
            # 玩家方和对手方交替发言
            if self.free_debate_round == 0 or self.free_debate_round % 2 == 0:
                side = "player"
            else:
                side = "opponent"
            # 自由辩论时随机选择辩手（0-2）
            index = (self.free_debate_round + (0 if side == "player" else 1)) % 3
            return {"side": side, "index": index, "name": "辩手", "role": "自由辩论"}
        elif self.current_phase == "closing":
            if self.current_round == 1:
                return {"side": "opponent", "index": 2, "name": "三辩", "role": "总结"}
            else:
                return {"side": "player", "index": 2, "name": "三辩", "role": "总结"}
        return {"side": "", "index": -1, "name": "", "role": ""}

    def is_player_turn(self) -> bool:
        """是否是玩家回合（需要玩家输入）"""
        return self.current_turn in [
            TurnType.PLAYER_SPEAK,
            TurnType.PLAYER_COACH_GUIDANCE
        ]

    def get_phase_name(self) -> str:
        """获取当前环节名称"""
        for p in DEBATE_PHASES:
            if p["id"] == self.current_phase:
                return p["name"]
        return ""

    def get_turn_description(self) -> str:
        """获取当前回合描述"""
        speaker = self.get_current_speaker()
        speaker_name = f"{'玩家方' if speaker['side'] == 'player' else '对手方'}{speaker['name']}"

        turn_descriptions = {
            TurnType.PLAYER_SPEAK: f"{speaker_name}发言",
            TurnType.PLAYER_COACH_GUIDANCE: f"{speaker_name}教练指导",
            TurnType.OPPONENT_SPEAK: f"{speaker_name}发言",
            TurnType.OPPONENT_COACH_GUIDANCE: f"{speaker_name}教练指导",
            TurnType.PHASE_END: "环节结束",
        }
        return turn_descriptions.get(self.current_turn, "")


def create_initial_state(topic: Topic, player_stance: str = None) -> GameState:
    """创建初始游戏状态

    Args:
        topic: 辩题
        player_stance: 玩家立场 ("A" 或 "B")，如果为None则随机
    """
    state = GameState()
    state.topic = topic
    state.phase = GamePhase.TOPIC_REVEAL
    state.current_phase = "opening"
    state.current_round = 1
    state.current_turn = TurnType.PLAYER_SPEAK

    # 如果没有指定立场，则随机
    if player_stance is None:
        player_stance = random.choice(["A", "B"])
    state.player_stance = player_stance

    return state
