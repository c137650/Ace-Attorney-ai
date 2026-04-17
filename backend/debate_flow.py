"""
辩论流程控制
管理辩论的各个环节和回合
"""

from typing import Optional, Callable
from dataclasses import dataclass

from game_state import GameState, GamePhase, TurnType, DebateRound, Topic
from agents.debater import DebaterAgent, SimpleDebaterAgent
from agents.coach import CoachAgent, SimpleCoachAgent


@dataclass
class TurnResult:
    """回合结果"""
    turn_type: TurnType
    speaker_side: str
    speaker_name: str
    content: str  # 发言内容或教练指导
    is_complete: bool  # 回合是否完成


class DebateFlow:
    """辩论流程控制器"""

    def __init__(self, state: GameState, use_simple_agents: bool = True, use_llm: bool = False):
        """
        初始化辩论流程

        Args:
            state: 游戏状态
            use_simple_agents: 是否使用简化Agent（不调用LLM，用于测试）
            use_llm: 是否使用LLM生成内容（需要配置API）
        """
        self.state = state
        self.use_simple_agents = use_simple_agents
        self.use_llm = use_llm and not use_simple_agents  # 启用LLM时不能同时用简化Agent

        # 初始化辩手
        if use_simple_agents:
            self.debaters = {
                "player": {
                    0: SimpleDebaterAgent("一辩", "player", 0),
                    1: SimpleDebaterAgent("二辩", "player", 1),
                    2: SimpleDebaterAgent("三辩", "player", 2),
                },
                "opponent": {
                    0: SimpleDebaterAgent("一辩", "opponent", 0),
                    1: SimpleDebaterAgent("二辩", "opponent", 1),
                    2: SimpleDebaterAgent("三辩", "opponent", 2),
                }
            }
            self.coaches = {
                "player": SimpleCoachAgent("player"),
                "opponent": SimpleCoachAgent("opponent"),
            }
        else:
            # 使用完整Agent（支持LLM）
            self.debaters = {
                "player": {
                    0: DebaterAgent("一辩", "player", 0, use_llm=use_llm),
                    1: DebaterAgent("二辩", "player", 1, use_llm=use_llm),
                    2: DebaterAgent("三辩", "player", 2, use_llm=use_llm),
                },
                "opponent": {
                    0: DebaterAgent("一辩", "opponent", 0, use_llm=use_llm),
                    1: DebaterAgent("二辩", "opponent", 1, use_llm=use_llm),
                    2: DebaterAgent("三辩", "opponent", 2, use_llm=use_llm),
                }
            }
            self.coaches = {
                "player": CoachAgent("player", use_llm=use_llm),
                "opponent": CoachAgent("opponent", use_llm=use_llm),
            }

        # 对方上一轮发言（用于教练分析和反驳）
        self.last_opponent_speech: Optional[str] = None

        # 质询环节：对方的提问
        self.last_question: Optional[str] = None

    def process_player_input(self, player_input: str) -> TurnResult:
        """
        处理玩家输入

        Args:
            player_input: 玩家教练的指导指令

        Returns:
            回合结果
        """
        speaker = self.state.get_current_speaker()

        if self.state.current_turn == TurnType.PLAYER_SPEAK:
            # 玩家方辩手发言
            return self._execute_player_speak(player_input, speaker)
        elif self.state.current_turn == TurnType.PLAYER_COACH_GUIDANCE:
            # 玩家教练指导（用于对手方发言前）
            return self._execute_player_coach_guidance(player_input, speaker)
        elif self.state.current_turn == TurnType.PLAYER_QUESTION:
            # 玩家方三辩提问（质询）
            return self._execute_player_question(player_input, speaker)
        elif self.state.current_turn == TurnType.PLAYER_ANSWER:
            # 玩家方三辩回答（被质询）
            return self._execute_player_answer(player_input, speaker)
        else:
            raise ValueError(f"当前不是玩家回合: {self.state.current_turn}")

    def advance_turn(self) -> TurnResult:
        """
        推进回合（用于AI自动执行或跳过玩家输入）

        Returns:
            回合结果
        """
        speaker = self.state.get_current_speaker()

        if self.state.current_turn == TurnType.OPPONENT_SPEAK:
            # 对手方发言
            return self._execute_opponent_speak(speaker)
        elif self.state.current_turn == TurnType.OPPONENT_COACH_GUIDANCE:
            # 对手方教练指导
            return self._execute_opponent_coach_guidance(speaker)
        elif self.state.current_turn == TurnType.OPPONENT_QUESTION:
            # 对手方三辩提问（质询）
            return self._execute_opponent_question(speaker)
        elif self.state.current_turn == TurnType.OPPONENT_ANSWER:
            # 对手方三辩回答（被质询）
            return self._execute_opponent_answer(speaker)
        else:
            raise ValueError(f"当前不是AI回合: {self.state.current_turn}")

    def skip_player_turn(self) -> TurnResult:
        """
        跳过玩家回合（使用默认策略）

        Returns:
            回合结果
        """
        # 使用默认指导
        default_guidance = "保持原有策略，坚持己方立场。"
        return self.process_player_input(default_guidance)

    def _execute_player_speak(self, coach_guidance: str, speaker: dict) -> TurnResult:
        """执行玩家方辩手发言"""
        side = speaker["side"]
        index = speaker["index"]

        # 获取辩手
        debater = self.debaters[side][index]

        # 获取立场
        stance = self.state.player_stance if side == "player" else ("B" if self.state.player_stance == "A" else "A")

        # 生成发言
        speech = debater.generate_speech(
            coach_guidance=coach_guidance,
            topic=self.state.topic,
            stance=stance,
            phase=self.state.current_phase,
            context=self.last_opponent_speech
        )

        # 记录回合
        round_record = DebateRound(
            round_num=len(self.state.rounds) + 1,
            phase=self.state.current_phase,
            speaker_side=side,
            speaker_index=index,
            turn_type=TurnType.PLAYER_SPEAK,
            content=speech
        )
        self.state.rounds.append(round_record)

        # 自由辩论：玩家发言后不增加轮次，只切换到对手
        if self.state.current_phase == "free_debate":
            self.state.current_turn = TurnType.OPPONENT_SPEAK
        else:
            # 其他环节正常推进
            self._advance_to_next_turn()

        return TurnResult(
            turn_type=TurnType.PLAYER_SPEAK,
            speaker_side=side,
            speaker_name=f"{'玩家方' if side == 'player' else '对手方'}{speaker['name']}",
            content=speech,
            is_complete=True
        )

    def _execute_player_coach_guidance(self, guidance: str, speaker: dict) -> TurnResult:
        """执行玩家教练指导（对手方发言前）"""
        # 记录玩家教练的指导（用于后续分析）
        # 玩家输入的guidance会被传递给对手方辩手

        # 直接进入对手方发言
        opponent_speaker = {"side": "opponent", "index": speaker["index"], "name": speaker["name"]}
        return self._execute_opponent_speak(opponent_speaker, player_guidance=guidance)

    # ==================== 质询环节 ====================

    def _execute_player_question(self, coach_guidance: str, speaker: dict) -> TurnResult:
        """执行玩家方三辩提问（质询环节）"""
        side = "player"
        index = 2  # 三辩

        # 获取辩手
        debater = self.debaters[side][index]

        # 获取立场
        stance = self.state.player_stance

        # 生成提问
        speech = debater.generate_speech(
            coach_guidance=coach_guidance,
            topic=self.state.topic,
            stance=stance,
            phase=self.state.current_phase,
            context=self.last_opponent_speech,
            is_question_asker=True  # 提问方
        )

        # 保存提问（用于对手回答）
        self.last_question = speech

        # 记录回合
        round_record = DebateRound(
            round_num=len(self.state.rounds) + 1,
            phase=self.state.current_phase,
            speaker_side=side,
            speaker_index=index,
            turn_type=TurnType.PLAYER_QUESTION,
            content=speech
        )
        self.state.rounds.append(round_record)

        # 更新状态：进入对手方回答（round=2 表示对手回答阶段）
        self.state.current_round = 2
        self.state.current_turn = TurnType.OPPONENT_ANSWER

        return TurnResult(
            turn_type=TurnType.PLAYER_QUESTION,
            speaker_side=side,
            speaker_name=f"玩家方三辩",
            content=speech,
            is_complete=True
        )

    def _execute_player_answer(self, coach_guidance: str, speaker: dict) -> TurnResult:
        """执行玩家方三辩回答（被质询）"""
        side = "player"
        index = 2  # 三辩

        # 获取辩手
        debater = self.debaters[side][index]

        # 获取立场
        stance = self.state.player_stance

        # 生成回答
        speech = debater.generate_speech(
            coach_guidance=coach_guidance,
            topic=self.state.topic,
            stance=stance,
            phase=self.state.current_phase,
            context=self.last_question,  # 对手的提问
            is_question_asker=False  # 回答方
        )

        # 记录回合
        round_record = DebateRound(
            round_num=len(self.state.rounds) + 1,
            phase=self.state.current_phase,
            speaker_side=side,
            speaker_index=index,
            turn_type=TurnType.PLAYER_ANSWER,
            content=speech
        )
        self.state.rounds.append(round_record)

        # 质询环节：如果 round=3，玩家回答后进入自由辩论
        if self.state.current_phase == "question":
            if self.state.current_round == 3:
                self._advance_to_next_phase()
            else:
                self._advance_to_next_turn()
        else:
            self._advance_to_next_turn()

        return TurnResult(
            turn_type=TurnType.PLAYER_ANSWER,
            speaker_side=side,
            speaker_name=f"玩家方三辩",
            content=speech,
            is_complete=True
        )

    def _execute_opponent_question(self, speaker: dict) -> TurnResult:
        """执行对手方三辩提问（质询环节）"""
        side = "opponent"
        index = 2  # 三辩

        # 获取辩手
        debater = self.debaters[side][index]

        # 获取立场
        opponent_stance = "B" if self.state.player_stance == "A" else "A"

        # AI教练生成指导
        coach = self.coaches[side]
        coach_guidance = coach.generate_guidance(
            opponent_speech=self.last_question,
            topic=self.state.topic,
            stance=opponent_stance,
            phase=self.state.current_phase,
            debate_history=self.state.rounds
        )

        # 生成提问
        speech = debater.generate_speech(
            coach_guidance=coach_guidance,
            topic=self.state.topic,
            stance=opponent_stance,
            phase=self.state.current_phase,
            context=self.last_question,
            is_question_asker=True  # 提问方
        )

        # 保存提问
        self.last_question = speech

        # 记录回合
        round_record = DebateRound(
            round_num=len(self.state.rounds) + 1,
            phase=self.state.current_phase,
            speaker_side=side,
            speaker_index=index,
            turn_type=TurnType.OPPONENT_QUESTION,
            content=speech
        )
        self.state.rounds.append(round_record)

        # 更新状态：进入玩家方回答
        self.state.current_turn = TurnType.PLAYER_ANSWER

        return TurnResult(
            turn_type=TurnType.OPPONENT_QUESTION,
            speaker_side=side,
            speaker_name=f"对手方三辩",
            content=speech,
            is_complete=True
        )

    def _execute_opponent_answer(self, speaker: dict) -> TurnResult:
        """执行对手方三辩回答（被质询）"""
        side = "opponent"
        index = 2  # 三辩

        # 获取辩手
        debater = self.debaters[side][index]

        # 获取立场
        opponent_stance = "B" if self.state.player_stance == "A" else "A"

        # AI教练生成指导
        coach = self.coaches[side]
        coach_guidance = coach.generate_guidance(
            opponent_speech=self.last_question,
            topic=self.state.topic,
            stance=opponent_stance,
            phase=self.state.current_phase,
            debate_history=self.state.rounds
        )

        # 生成回答
        speech = debater.generate_speech(
            coach_guidance=coach_guidance,
            topic=self.state.topic,
            stance=opponent_stance,
            phase=self.state.current_phase,
            context=self.last_question,
            is_question_asker=False  # 回答方
        )

        # 记录回合
        round_record = DebateRound(
            round_num=len(self.state.rounds) + 1,
            phase=self.state.current_phase,
            speaker_side=side,
            speaker_index=index,
            turn_type=TurnType.OPPONENT_ANSWER,
            content=speech
        )
        self.state.rounds.append(round_record)

        # 质询环节：对手回答后进入对手提问，然后推进轮次
        self.state.current_turn = TurnType.OPPONENT_QUESTION
        self._advance_to_next_turn()

        return TurnResult(
            turn_type=TurnType.OPPONENT_ANSWER,
            speaker_side=side,
            speaker_name=f"对手方三辩",
            content=speech,
            is_complete=True
        )

    def _execute_opponent_speak(self, speaker: dict, player_guidance: Optional[str] = None) -> TurnResult:
        """执行对手方辩手发言"""
        side = speaker["side"]  # "opponent"
        index = speaker["index"]

        # 获取辩手
        debater = self.debaters[side][index]

        # 获取立场
        opponent_stance = "B" if self.state.player_stance == "A" else "A"

        # 获取教练指导
        coach = self.coaches[side]

        # 生成教练指导
        coach_guidance = coach.generate_guidance(
            opponent_speech=self.last_opponent_speech,
            topic=self.state.topic,
            stance=opponent_stance,
            phase=self.state.current_phase,
            debate_history=self.state.rounds
        )

        # 生成发言
        speech = debater.generate_speech(
            coach_guidance=coach_guidance,
            topic=self.state.topic,
            stance=opponent_stance,
            phase=self.state.current_phase,
            context=self.last_opponent_speech
        )

        # 记录回合
        round_record = DebateRound(
            round_num=len(self.state.rounds) + 1,
            phase=self.state.current_phase,
            speaker_side=side,
            speaker_index=index,
            turn_type=TurnType.OPPONENT_SPEAK,
            content=speech
        )
        self.state.rounds.append(round_record)

        # 保存对手发言（供下一轮使用）
        self.last_opponent_speech = speech

        # 开篇立论对手方发言后，进入驳论
        if self.state.current_phase == "opening":
            self._advance_to_next_phase()
        # 自由辩论：对手发言后增加轮次
        elif self.state.current_phase == "free_debate":
            self.state.free_debate_round += 1
            if self.state.free_debate_round >= 8:
                # 自由辩论结束，进入总结陈词
                self._advance_to_next_phase()
            else:
                # 切换到玩家发言
                self.state.current_turn = TurnType.PLAYER_SPEAK
        else:
            # 其他环节正常推进
            self._advance_to_next_turn()

        return TurnResult(
            turn_type=TurnType.OPPONENT_SPEAK,
            speaker_side=side,
            speaker_name=f"{'对手方'}{speaker['name']}",
            content=speech,
            is_complete=True
        )

    def _execute_opponent_coach_guidance(self, speaker: dict) -> TurnResult:
        """执行对手方教练指导"""
        side = "opponent"

        # 对手方教练分析并给出指导，然后直接发言
        opponent_speaker = {"side": "opponent", "index": speaker["index"], "name": speaker["name"]}
        return self._execute_opponent_speak(opponent_speaker)

    def _advance_to_next_turn(self):
        """推进到下一回合"""
        phase = self.state.current_phase

        if phase == "opening":
            # 开篇立论：2轮（玩家方→对手方）
            if self.state.current_round == 1:
                # 第一轮完成，进入第二轮（对手方发言）
                self.state.current_round = 2
                self.state.current_turn = TurnType.OPPONENT_SPEAK
            else:
                # 开篇立论结束，进入驳论
                self._advance_to_next_phase()
                # 继续处理新环节的状态（更新phase变量）
                phase = self.state.current_phase
                self._advance_to_next_turn()
        elif phase == "rebuttal":
            # 驳论：2轮（对手方→玩家方）
            if self.state.current_round == 1:
                self.state.current_round = 2
                self.state.current_turn = TurnType.PLAYER_SPEAK
            else:
                self._advance_to_next_phase()
        elif phase == "question":
            # 质询：对手发言后增加轮次
            # 注意：turn 已经在 execute 方法中设置了，这里只增加 round
            self.state.current_round += 1
            if self.state.current_round >= 4:
                # 质询结束（4个步骤完成）
                self._advance_to_next_phase()
        elif phase == "free_debate":
            # 自由辩论轮次由 _execute_opponent_speak 处理
            # 这里不需要额外的处理
            pass
        elif phase == "closing":
            # 总结陈词：2轮（对手方→玩家方）
            if self.state.current_round == 1:
                self.state.current_round = 2
                self.state.current_turn = TurnType.PLAYER_SPEAK
            else:
                self._advance_to_next_phase()

    def _advance_to_next_phase(self):
        """推进到下一环节"""
        phases = ["opening", "rebuttal", "question", "free_debate", "closing"]
        current_index = phases.index(self.state.current_phase)

        if current_index < len(phases) - 1:
            # 进入下一环节
            self.state.current_phase = phases[current_index + 1]
            self.state.current_round = 1

            # 确定第一轮的发言方
            if self.state.current_phase == "opening":
                self.state.current_turn = TurnType.PLAYER_SPEAK
            elif self.state.current_phase == "rebuttal":
                # 驳论第一轮：对手方先发言
                self.state.current_turn = TurnType.OPPONENT_SPEAK
            elif self.state.current_phase == "question":
                self.state.current_turn = TurnType.PLAYER_QUESTION
            elif self.state.current_phase == "free_debate":
                self.state.current_turn = TurnType.PLAYER_SPEAK
                self.state.free_debate_round = 0
            elif self.state.current_phase == "closing":
                self.state.current_turn = TurnType.OPPONENT_SPEAK
        else:
            # 所有环节结束，进入裁判判决
            self.state.phase = GamePhase.JUDGMENT

    def is_phase_complete(self) -> bool:
        """检查当前环节是否完成"""
        phase = self.state.current_phase
        round_num = self.state.current_round

        if phase == "free_debate":
            return self.state.free_debate_round >= 16

        # 其他环节都是2轮
        return round_num > 2

    def get_game_status(self) -> dict:
        """获取游戏状态"""
        return {
            "phase": self.state.phase.value,
            "current_phase": self.state.current_phase,
            "current_round": self.state.current_round,
            "current_turn": self.state.current_turn.value,
            "is_player_turn": self.state.is_player_turn(),
            "turn_description": self.state.get_turn_description(),
            "speaker": self.state.get_current_speaker(),
            "topic": {
                "title": self.state.topic.title,
                "description": self.state.topic.description,
                "player_stance": self.state.player_stance,
                "player_stance_text": self.state.topic.stance_a if self.state.player_stance == "A" else self.state.topic.stance_b,
            }
        }
