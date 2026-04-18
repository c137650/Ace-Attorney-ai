"""
裁判判决模块
根据辩论双方的发言记录进行评分和判决
"""

from typing import Dict, List, Tuple
import re


class JudgeResult:
    """判决结果"""
    def __init__(self):
        self.player_score: float = 0.0
        self.opponent_score: float = 0.0
        self.winner: str = ""  # "player" / "opponent" / "draw"
        self.reasons: List[str] = []
        self.analysis: Dict[str, str] = {}
    
    def to_dict(self) -> dict:
        return {
            "player_score": self.player_score,
            "opponent_score": self.opponent_score,
            "winner": self.winner,
            "reasons": self.reasons,
            "analysis": self.analysis
        }


class Judge:
    """辩论裁判"""
    
    def __init__(self):
        self.phase_names = {
            "opening": "开篇立论",
            "rebuttal": "驳论",
            "question": "质询",
            "free_debate": "自由辩论",
            "closing": "总结陈词"
        }
    
    def judge(self, game_state, speech_history: List[Tuple]) -> JudgeResult:
        """
        进行判决
        
        Args:
            game_state: 游戏状态（包含辩题、立场等信息）
            speech_history: 发言历史 [(side, index, content), ...]
            
        Returns:
            判决结果
        """
        result = JudgeResult()
        
        # 分离双方发言
        player_speeches = [(idx, content) for side, idx, content in speech_history if side == "player"]
        opponent_speeches = [(idx, content) for side, idx, content in speech_history if side == "opponent"]
        
        # 读取 Memory 文件获取更详细的分析
        memories = self._load_memories()
        
        # 评分维度
        scores = {
            "player": {"logic": 0, "evidence": 0, "response": 0, "style": 0},
            "opponent": {"logic": 0, "evidence": 0, "response": 0, "style": 0}
        }
        
        # 1. 评分：逻辑性（基于发言长度和结构）
        scores["player"]["logic"] = self._score_logic(player_speeches)
        scores["opponent"]["logic"] = self._score_logic(opponent_speeches)
        
        # 2. 评分：论点数量
        scores["player"]["evidence"] = self._score_evidence(player_speeches)
        scores["opponent"]["evidence"] = self._score_evidence(opponent_speeches)
        
        # 3. 评分：回应对方论点
        scores["player"]["response"] = self._score_response(player_speeches, opponent_speeches)
        scores["opponent"]["response"] = self._score_response(opponent_speeches, player_speeches)
        
        # 4. 评分：表达风格
        scores["player"]["style"] = self._score_style(player_speeches)
        scores["opponent"]["style"] = self._score_style(opponent_speeches)
        
        # 计算总分（满分100）
        total_player = sum(scores["player"].values())
        total_opponent = sum(scores["opponent"].values())
        
        # 归一化到100分
        max_possible = 40  # 每个维度最高10分
        result.player_score = min(100, (total_player / max_possible) * 100)
        result.opponent_score = min(100, (total_opponent / max_possible) * 100)
        
        # 判定胜负
        diff = abs(result.player_score - result.opponent_score)
        if diff < 5:
            result.winner = "draw"
            result.reasons.append("双方表现势均力敌，难分伯仲")
        elif result.player_score > result.opponent_score:
            result.winner = "player"
            result.reasons.append("正方整体表现更为出色")
        else:
            result.winner = "opponent"
            result.reasons.append("反方整体表现更为出色")
        
        # 生成分析理由
        result.analysis = self._generate_analysis(scores, game_state)
        
        # 逐项对比
        self._add_comparison_reasons(result, scores)
        
        return result
    
    def _load_memories(self) -> Dict[str, str]:
        """加载所有 Memory 文件"""
        memories = {}
        try:
            from soul_manager import get_soul_manager
            manager = get_soul_manager()
            for agent_id in ["player_debater_1", "player_debater_2", "player_debater_3",
                           "opponent_debater_1", "opponent_debater_2", "opponent_debater_3"]:
                memories[agent_id] = manager.get_memory(agent_id)
        except Exception as e:
            print(f"加载Memory失败: {e}")
        return memories
    
    def _score_logic(self, speeches: List[Tuple[int, str]]) -> float:
        """评分：逻辑性"""
        if not speeches:
            return 0
        
        score = 0
        for _, content in speeches:
            # 基础分：发言长度
            if len(content) > 50:
                score += 2
            
            # 加分：有明确的论点结构（首先、其次、第一、第二等）
            structure_markers = ['第一', '第二', '第三', '首先', '其次', '最后', '综上所述']
            for marker in structure_markers:
                if marker in content:
                    score += 1
                    break
            
            # 加分：有因果关系表述（因为、所以、因此、导致）
            if any(word in content for word in ['因为', '所以', '因此', '导致']):
                score += 1
        
        return min(10, score)
    
    def _score_evidence(self, speeches: List[Tuple[int, str]]) -> float:
        """评分：论点数量"""
        if not speeches:
            return 0
        
        score = 0
        for _, content in speeches:
            # 统计论点数（通过特定模式）
            evidence_markers = ['证明', '显示', '表明', '根据', '数据', '研究', '事实', '案例']
            for marker in evidence_markers:
                if marker in content:
                    score += 1
                    break
            
            # 检查是否有具体论述（超过100字）
            if len(content) > 100:
                score += 1
        
        return min(10, score)
    
    def _score_response(self, own_speeches: List[Tuple[int, str]], 
                       opponent_speeches: List[Tuple[int, str]]) -> float:
        """评分：回应对方论点"""
        if not opponent_speeches:
            return 5  # 没有对方发言，中立分
        
        score = 0
        opponent_content = " ".join([c for _, c in opponent_speeches])
        
        for _, content in own_speeches:
            # 检查是否提及对方观点（反驳）
            if any(word in content for word in ['对方', '对方观点', '对手']):
                score += 2
            # 检查是否有针对性回应（针对、回应、反驳）
            if any(word in content for word in ['针对', '回应', '反驳', '质疑']):
                score += 1
            # 检查是否提到对方一辩/二辩/三辩
            if any(word in opponent_content for word in ['一辩', '二辩', '三辩']):
                if any(word in content for word in ['一辩', '二辩', '三辩']):
                    score += 1
        
        return min(10, score)
    
    def _score_style(self, speeches: List[Tuple[int, str]]) -> float:
        """评分：表达风格"""
        if not speeches:
            return 0
        
        score = 0
        for _, content in speeches:
            # 加分：有礼貌用语
            polite_markers = ['谢谢', '感谢', '请', '各位']
            for marker in polite_markers:
                if marker in content:
                    score += 1
                    break
            
            # 加分：有总结收尾
            if '谢谢' in content or '总结' in content:
                score += 1
            
            # 扣分：过于简短（少于30字）
            if len(content) < 30:
                score -= 1
        
        return max(0, min(10, score + 5))  # 基础分5分
    
    def _generate_analysis(self, scores: Dict, game_state) -> Dict[str, str]:
        """生成分析说明"""
        analysis = {}
        
        analysis["player_logic"] = self._get_logic_desc(scores["player"]["logic"])
        analysis["opponent_logic"] = self._get_logic_desc(scores["opponent"]["logic"])
        analysis["player_evidence"] = self._get_evidence_desc(scores["player"]["evidence"])
        analysis["opponent_evidence"] = self._get_evidence_desc(scores["opponent"]["evidence"])
        analysis["player_response"] = self._get_response_desc(scores["player"]["response"])
        analysis["opponent_response"] = self._get_response_desc(scores["opponent"]["response"])
        
        return analysis
    
    def _get_logic_desc(self, score: float) -> str:
        if score >= 8:
            return "逻辑严密，论证充分"
        elif score >= 5:
            return "逻辑清晰，有一定论证"
        else:
            return "逻辑较弱，论证不足"
    
    def _get_evidence_desc(self, score: float) -> str:
        if score >= 8:
            return "论据丰富，有理有据"
        elif score >= 5:
            return "论据适中"
        else:
            return "论据较少"
    
    def _get_response_desc(self, score: float) -> str:
        if score >= 8:
            return "积极回应对方，有效反驳"
        elif score >= 5:
            return "有回应对方观点"
        else:
            return "较少回应对方"
    
    def _add_comparison_reasons(self, result: JudgeResult, scores: Dict):
        """添加对比理由"""
        # 逻辑对比
        if scores["player"]["logic"] > scores["opponent"]["logic"] + 2:
            result.reasons.append("正方在论证逻辑上更为严密")
        elif scores["opponent"]["logic"] > scores["player"]["logic"] + 2:
            result.reasons.append("反方在论证逻辑上更为严密")
        
        # 论据对比
        if scores["player"]["evidence"] > scores["opponent"]["evidence"] + 2:
            result.reasons.append("正方论据更加充分有力")
        elif scores["opponent"]["evidence"] > scores["player"]["evidence"] + 2:
            result.reasons.append("反方论据更加充分有力")
        
        # 反驳对比
        if scores["player"]["response"] > scores["opponent"]["response"] + 2:
            result.reasons.append("正方对对方观点的回应更为到位")
        elif scores["opponent"]["response"] > scores["player"]["response"] + 2:
            result.reasons.append("反方对对方观点的回应更为到位")
        
        # 限制理由数量
        result.reasons = result.reasons[:5]


def judge_debate(game_state, speech_history: List[Tuple]) -> Dict:
    """
    快捷函数：进行辩论判决
    
    Args:
        game_state: 游戏状态
        speech_history: 发言历史 [(side, index, content), ...]
        
    Returns:
        判决结果字典
    """
    judge = Judge()
    result = judge.judge(game_state, speech_history)
    return result.to_dict()
