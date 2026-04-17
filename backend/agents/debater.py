"""
AI辩手模块
根据教练指令生成辩论发言
"""

import re
from typing import Optional

# 延迟导入，避免循环依赖
_llm_client = None


def _get_llm():
    """获取LLM客户端"""
    global _llm_client
    if _llm_client is None:
        from llm_client import get_llm_client
        _llm_client = get_llm_client()
    return _llm_client


class DebaterAgent:
    """AI辩手"""

    def __init__(self, name: str, side: str, index: int, use_llm: bool = False, agent_id: str = None):
        self.name = name  # "一辩"、"二辩"、"三辩"
        self.side = side  # "player" 或 "opponent"
        self.index = index  # 0, 1, 2
        self.use_llm = use_llm  # 是否使用LLM

        # Agent ID用于Soul和Memory
        if agent_id is None:
            prefix = "player" if side == "player" else "opponent"
            self.agent_id = f"{prefix}_debater_{index + 1}"
        else:
            self.agent_id = agent_id

    def generate_speech(
        self,
        coach_guidance: str,
        topic,
        stance: str,
        phase: str,
        context: Optional[str] = None,
        is_question_asker: bool = True
    ) -> str:
        """根据教练指导生成发言"""
        stance_text = topic.stance_a if stance == "A" else topic.stance_b

        # 如果启用LLM，使用Soul生成
        if self.use_llm:
            try:
                llm = _get_llm()
                agent_name = "正方" + self.name if self.side == "player" else "反方" + self.name
                speech = llm.generate_debater_speech(
                    coach_guidance=coach_guidance,
                    topic_title=topic.title,
                    stance=stance,
                    stance_text=stance_text,
                    phase=phase,
                    context=context,
                    agent_id=self.agent_id,
                    agent_name=agent_name
                )
                print(f"  [LLM] {agent_name}发言生成成功")
                # 记录到Memory
                self._record_memory(phase, speech)
                return speech
            except Exception as e:
                print(f"  [LLM] 调用失败: {e}")

        # 备用生成
        if phase == "question":
            if is_question_asker:
                speech = self._generate_question_ask(coach_guidance, context)
            else:
                speech = self._generate_question_answer(coach_guidance, context)
        elif phase == "opening":
            speech = self._generate_opening(coach_guidance, topic, stance_text)
        elif phase == "rebuttal":
            speech = self._generate_rebuttal(coach_guidance, context)
        elif phase == "free_debate":
            speech = self._generate_free_debate(coach_guidance, context)
        elif phase == "closing":
            speech = self._generate_closing(coach_guidance, context)
        else:
            speech = coach_guidance

        # 记录到Memory
        self._record_memory(phase, speech)
        return speech

    def _record_memory(self, phase: str, content: str):
        """记录到Memory"""
        try:
            from soul_manager import get_soul_manager
            manager = get_soul_manager()
            phase_name = {
                "opening": "开篇立论",
                "rebuttal": "驳论",
                "question": "质询",
                "free_debate": "自由辩论",
                "closing": "总结陈词"
            }.get(phase, phase)
            manager.add_memory(self.agent_id, phase_name, content)
        except Exception as e:
            print(f"  记录Memory失败: {e}")

    def _generate_opening(self, guidance: str, topic, stance_text: str) -> str:
        """生成开篇立论"""
        # 提取指导中的关键论点
        key_points = self._extract_key_points(guidance)

        speech = f"谢谢主席。\n\n"

        if key_points:
            for point in key_points:
                speech += f"{point}\n"
        else:
            # 默认模板
            speech += f"我方认为{topic.title}，理由如下：\n\n"
            speech += f"第一，{stance_text[:40]}...\n"
            speech += f"第二，{stance_text[40:80] if len(stance_text) > 40 else '从社会发展角度看，此议题至关重要'}...\n"
            speech += f"第三，综上所述，我方立场明确。\n"

        speech += "\n谢谢。"
        return self._limit_words(speech, 100)

    def _generate_rebuttal(self, guidance: str, opponent_speech: Optional[str]) -> str:
        """生成驳论"""
        key_points = self._extract_key_points(guidance)

        speech = f"谢谢。针对对方的立论，我方提出以下反驳：\n\n"

        if key_points:
            for point in key_points:
                speech += f"{point}\n"
        else:
            speech += "对方的论点存在逻辑漏洞，我方将在以下方面进行反驳...\n"

        speech += "\n谢谢。"
        return self._limit_words(speech, 100)

    def _generate_question(self, guidance: str, opponent_speech: Optional[str], is_question_asker: bool = True) -> str:
        """
        生成质询

        Args:
            guidance: 教练指导
            opponent_speech: 对方发言（包含对方的问题或回答）
            is_question_asker: 是否是提问方（True=提问，False=回答）
        """
        if is_question_asker:
            # 提问方：提出尖锐问题
            return self._generate_question_ask(guidance, opponent_speech)
        else:
            # 回答方：简短回答
            return self._generate_question_answer(guidance, opponent_speech)

    def _generate_question_ask(self, guidance: str, opponent_speech: Optional[str]) -> str:
        """生成质询提问"""
        questions = self._extract_questions(guidance)

        speech = "谢谢。我方想向对方请教几个问题：\n\n"

        if questions:
            for q in questions:
                speech += f"{q}\n"
        else:
            # 默认问题
            speech += "问题一：请问对方如何解释其中的核心矛盾？\n"
            speech += "问题二：对方是否承认这一事实？\n"
            speech += "问题三：请对方正面回应我方质疑。\n"

        speech += "\n请对方正面回答。"
        return self._limit_words(speech, 100)

    def _generate_question_answer(self, guidance: str, opponent_questions: Optional[str]) -> str:
        """生成质询回答"""
        key_points = self._extract_key_points(guidance)

        speech = "谢谢。针对对方的问题，我方回答如下：\n\n"

        if key_points:
            for point in key_points:
                speech += f"{point}\n"
        else:
            speech += "对方的提问存在前提错误，我方不予承认。\n"
            speech += "我方始终坚持原有立场。\n"

        speech += "\n谢谢。"
        return self._limit_words(speech, 100)

    def _generate_free_debate(self, guidance: str, context: Optional[str]) -> str:
        """生成自由辩论发言"""
        key_points = self._extract_key_points(guidance)

        if key_points:
            speech = "\n".join(key_points)
        else:
            speech = guidance if guidance else "我方坚持原有立场，请对方正面回应..."

        return self._limit_words(speech, 100)

    def _generate_closing(self, guidance: str, context: Optional[str]) -> str:
        """生成总结陈词"""
        key_points = self._extract_key_points(guidance)

        speech = "谢谢。最后总结我方观点：\n\n"

        if key_points:
            for point in key_points:
                speech += f"{point}\n"
        else:
            speech += "综上所述，我方的立场是坚定且有据可依的。\n"
            speech += "对方虽然在某些方面有所论述，但未能从根本上动摇我方论点。\n"

        speech += "\n感谢各位的聆听。"
        return self._limit_words(speech, 100)

    def _extract_key_points(self, text: str) -> list:
        """从文本中提取关键论点"""
        points = []

        # 匹配常见的论点格式
        patterns = [
            r'[一二三四五六七八九十][、.]\s*(.+?)(?=\n|$)',
            r'第一[、:：]\s*(.+?)(?=\n|$)',
            r'论点\d*[：:]\s*(.+?)(?=\n|$)',
            r'核心\d*[：:]\s*(.+?)(?=\n|$)',
            r'攻击[对方]*\d*[：:]\s*(.+?)(?=\n|$)',
            r'反驳[对方]*\d*[：:]\s*(.+?)(?=\n|$)',
            r'主[攻|要][点|张]*[：:]\s*(.+?)(?=\n|$)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            points.extend(matches)

        # 去重
        seen = set()
        unique_points = []
        for p in points:
            if p.strip() not in seen and len(p.strip()) > 5:
                seen.add(p.strip())
                unique_points.append(p.strip())

        return unique_points

    def _extract_questions(self, text: str) -> list:
        """从文本中提取问题"""
        questions = []

        # 匹配问题格式
        patterns = [
            r'问题\d*[：:]\s*(.+?)(?=\n|$)',
            r'请问[对方]*[：:]\s*(.+?)(?=\n|$)',
            r'对方.*[？?]\s*(.+?)(?=\n|$)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text)
            questions.extend(matches)

        # 去重
        seen = set()
        unique_questions = []
        for q in questions:
            if q.strip() not in seen and len(q.strip()) > 5:
                seen.add(q.strip())
                unique_questions.append(q.strip())

        return unique_questions

    def _limit_words(self, text: str, max_words: int) -> str:
        """限制字数"""
        # 简单估算：中文字符约等于字数
        if len(text) <= max_words:
            return text

        # 找到最后一个完整句子
        for i in range(min(len(text), max_words), 0, -1):
            if text[i] in '。！？\n':
                return text[:i+1]

        return text[:max_words] + "..."


class SimpleDebaterAgent(DebaterAgent):
    """简化版辩手（用于测试，不调用真实LLM）"""

    def generate_speech(self, coach_guidance: str, topic, stance: str, phase: str, context: Optional[str] = None, is_question_asker: bool = True) -> str:
        """生成简化的测试发言"""
        side_name = "正方" if self.side == "player" else "反方"
        stance_text = topic.stance_a if stance == "A" else topic.stance_b

        if phase == "question":
            if is_question_asker:
                speech = f"{side_name}三辩质询：请问对方如何解释{topic.title}中的核心矛盾？请问对方是否承认这一事实？请对方正面回答。"
            else:
                speech = f"{side_name}三辩回答：对方的提问存在前提错误。我方不予承认。我方始终坚持原有立场。谢谢。"
        else:
            speeches = {
                "opening": f"{side_name}一辩开篇立论：我方认为{topic.title}。{stance_text[:50]}。谢谢。",
                "rebuttal": f"{side_name}二辩驳论：针对对方的观点，我方认为{stance_text[20:60]}。谢谢。",
                "free_debate": f"{side_name}辩手自由辩论：{coach_guidance[:50] if coach_guidance else '我方坚持原有立场'}。谢谢。",
                "closing": f"{side_name}三辩总结：综上所述，{stance_text[:30]}，感谢各位聆听。",
            }
            speech = speeches.get(phase, coach_guidance or "发言内容")

        # 记录到Memory
        self._record_memory(phase, speech)
        return speech
