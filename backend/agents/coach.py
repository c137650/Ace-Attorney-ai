"""
AI教练模块
分析对方发言，给出指导性意见，支持Soul个性化
"""

from typing import Optional

# 延迟导入
_llm_client = None


def _get_llm():
    """获取LLM客户端"""
    global _llm_client
    if _llm_client is None:
        from llm_client import get_llm_client
        _llm_client = get_llm_client()
    return _llm_client


class CoachAgent:
    """AI教练"""

    def __init__(self, side: str, use_llm: bool = False, agent_id: str = None):
        self.side = side  # "player" 或 "opponent"
        self.use_llm = use_llm  # 是否使用LLM

        # Agent ID用于Soul
        if agent_id is None:
            prefix = "player" if side == "player" else "opponent"
            self.agent_id = f"{prefix}_coach"
        else:
            self.agent_id = agent_id

    def generate_guidance(
        self,
        opponent_speech: Optional[str],
        topic,
        stance: str,
        phase: str,
        debate_history: list
    ) -> str:
        """生成教练指导"""
        # 如果启用LLM，使用Soul生成
        if self.use_llm:
            try:
                llm = _get_llm()
                stance_text = topic.stance_a if stance == "A" else topic.stance_b
                agent_name = "正方教练" if self.side == "player" else "反方教练"
                guidance = llm.generate_coach_guidance(
                    opponent_speech=opponent_speech,
                    topic_title=topic.title,
                    stance=stance,
                    stance_text=stance_text,
                    phase=phase,
                    debate_history=debate_history,
                    agent_id=self.agent_id,
                    agent_name=agent_name
                )
                print(f"  [LLM] {agent_name}指导生成成功")
                return guidance
            except Exception as e:
                print(f"  [LLM] 调用失败: {e}")

        # 备用生成
        if phase == "opening":
            return self._guidance_opening(topic, stance)
        elif phase == "rebuttal":
            return self._guidance_rebuttal(opponent_speech, topic, stance)
        elif phase == "question":
            return self._guidance_question(opponent_speech, topic, stance)
        elif phase == "free_debate":
            return self._guidance_free_debate(opponent_speech, debate_history)
        elif phase == "closing":
            return self._guidance_closing(opponent_speech, debate_history)
        else:
            return "坚持己方立场，逻辑清晰。"

    def _guidance_opening(self, topic, stance: str) -> str:
        """开篇立论的教练指导"""
        stance_text = topic.stance_a if stance == "A" else topic.stance_b

        # 根据立场提供不同的指导模板
        templates = [
            f"一辩立论（50-100字）：\n论点1：{topic.title}具有重要意义\n论点2：{stance_text[:40]}\n论点3：强调社会价值",
            f"一辩立论（50-100字）：\n核心论点：{stance_text[:50]}\n用数据支撑观点\n简洁有力收尾",
            f"一辩立论（50-100字）：\n立论要清晰\n论据要充分\n价值要升华",
        ]

        return self._limit_guidance(templates[hash(topic.id) % len(templates)])

    def _guidance_rebuttal(self, opponent_speech: Optional[str], topic, stance: str) -> str:
        """驳论的教练指导"""
        if opponent_speech:
            return self._limit_guidance(
                f"二辩驳论（50-100字）：\n攻击对方核心弱点\n用逻辑反驳\n数据反击"
            )
        return self._limit_guidance("二辩驳论（50-100字）：坚持己方论点，攻击对方漏洞。")

    def _guidance_question(self, opponent_speech: Optional[str], topic, stance: str) -> str:
        """质询的教练指导"""
        return self._limit_guidance(
            f"三辩质询（50-100字）：\n问题1：针对对方论点提出质疑\n问题2：追问逻辑漏洞\n保持进攻态势"
        )

    def _guidance_free_debate(self, opponent_speech: Optional[str], debate_history: list) -> str:
        """自由辩论的教练指导"""
        return self._limit_guidance(
            "自由辩论（50-100字）：\n保持攻势\n专注攻击\n简洁有力"
        )

    def _guidance_closing(self, opponent_speech: Optional[str], debate_history: list) -> str:
        """总结陈词的教练指导"""
        return self._limit_guidance(
            "三辩总结（50-100字）：\n回应对方攻击\n强化己方论点\n升华价值"
        )

    def _limit_guidance(self, text: str, max_chars: int = 50) -> str:
        """限制指导字数"""
        # 计算中文字符
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        other_chars = len(text) - chinese_chars
        # 粗略估算：中文占1字符，英文/符号占0.5
        estimated = chinese_chars + other_chars // 2

        if estimated <= max_chars:
            return text

        # 截断到合理长度
        result = []
        count = 0
        for c in text:
            if '\u4e00' <= c <= '\u9fff':
                count += 1
            else:
                count += 0.5
            if count <= max_chars:
                result.append(c)
            else:
                break

        return ''.join(result) + "..."


class SimpleCoachAgent(CoachAgent):
    """简化版教练（用于测试）"""

    def generate_guidance(self, opponent_speech: Optional[str], topic, stance: str, phase: str, debate_history: list) -> str:
        """生成简化的测试指导"""
        phase_names = {
            "opening": "开篇立论",
            "rebuttal": "驳论",
            "question": "质询",
            "free_debate": "自由辩论",
            "closing": "总结陈词"
        }

        return f"{phase_names.get(phase, '发言')}指导：坚持立场，逻辑清晰。"


class SimpleCoachAgent(CoachAgent):
    """简化版教练（用于测试）"""

    def generate_guidance(self, opponent_speech: Optional[str], topic, stance: str, phase: str, debate_history: list) -> str:
        """生成简化的测试指导"""
        phase_names = {
            "opening": "开篇立论",
            "rebuttal": "驳论",
            "question": "质询",
            "free_debate": "自由辩论",
            "closing": "总结陈词"
        }

        return f"{phase_names.get(phase, '发言')}指导：坚持立场，逻辑清晰。"
