"""
LLM 调用模块
统一管理API调用，支持Soul个性化
"""

import json
import os
from typing import Optional
import urllib.request
import urllib.error

# 延迟导入Soul管理器
_soul_manager = None


def _get_soul_manager():
    """获取Soul管理器"""
    global _soul_manager
    if _soul_manager is None:
        from soul_manager import SoulManager
        _soul_manager = SoulManager()
    return _soul_manager


class LLMClient:
    """LLM API调用客户端"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.json")

        self.config = self._load_config(config_path)
        self.api_config = self.config.get("api", {})
        self.prompts = self.config.get("prompts", {})
        self.fallback_enabled = self.config.get("fallback", {}).get("enabled", True)
        self.soul_manager = _get_soul_manager()

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        fallback: Optional[str] = None,
        max_retries: int = 2
    ) -> str:
        """调用LLM API"""
        provider = self.api_config.get("provider", "openai")

        for attempt in range(max_retries):
            try:
                if provider == "openai":
                    return self._call_openai(system_prompt, user_prompt)
                elif provider == "anthropic":
                    return self._call_anthropic(system_prompt, user_prompt)
                elif provider == "ollama":
                    return self._call_ollama(system_prompt, user_prompt)
                else:
                    raise ValueError(f"不支持的provider: {provider}")
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠ LLM调用失败(重试{attempt+1}/{max_retries}): {e}")
                    import time
                    time.sleep(1)
                else:
                    print(f"⚠ LLM调用失败: {e}")
                    if fallback:
                        print(f"   使用备用文本")
                        return fallback
                    return fallback or "（无法生成内容）"

    def _call_openai(self, system_prompt: str, user_prompt: str) -> str:
        """调用OpenAI兼容API"""
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context

        api_key = self.api_config.get("api_key", "")
        base_url = self.api_config.get("base_url", "https://api.openai.com/v1")
        model = self.api_config.get("model", "gpt-4o-mini")
        temperature = self.api_config.get("temperature", 0.3)
        max_tokens = self.api_config.get("max_tokens", 500)
        timeout = self.api_config.get("timeout", 60)

        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError("API Key未配置")

        url = f"{base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}'
            },
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=timeout) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content'].strip()
            return self._clean_think_content(content)

    def _call_anthropic(self, system_prompt: str, user_prompt: str) -> str:
        """调用Anthropic API"""
        api_key = self.api_config.get("api_key", "")
        model = self.api_config.get("model", "claude-3-haiku")

        if not api_key or api_key == "YOUR_API_KEY_HERE":
            raise ValueError("API Key未配置")

        url = "https://api.anthropic.com/v1/messages"

        payload = {
            "model": model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": 500
        }

        data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01'
            },
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['content'][0]['text'].strip()
            return self._clean_think_content(content)

    def _call_ollama(self, system_prompt: str, user_prompt: str) -> str:
        """调用Ollama本地API"""
        base_url = self.api_config.get("base_url", "http://localhost:11434")
        model = self.api_config.get("model", "llama3.2")

        url = f"{base_url}/api/generate"

        payload = {
            "model": model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False
        }

        data = json.dumps(payload).encode('utf-8')

        req = urllib.request.Request(
            url,
            data=data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['response'].strip()
            return self._clean_think_content(content)

    def generate_debater_speech(
        self,
        coach_guidance: str,
        topic_title: str,
        stance: str,
        stance_text: str,
        phase: str,
        context: Optional[str] = None,
        agent_id: str = "player_debater_1",
        agent_name: str = "辩手"
    ) -> str:
        """生成辩手发言"""
        # 获取Soul
        soul = self.soul_manager.get_soul(agent_id)

        # 从Soul中提取系统提示词
        if soul:
            system = self._extract_system_prompt(soul)
        else:
            system = self.prompts.get("debater_system", "你是辩论赛辩手。")

        # 构建上下文
        context_str = f"\n\n对方刚才的发言：{context}" if context else ""

        # 根据阶段构建不同的提示
        phase_instruction = self._get_phase_instruction(phase)

        user_prompt = f"""辩题：{topic_title}
你的立场：{stance_text}
当前环节：{self._get_phase_name(phase)}

{phase_instruction}

教练指导：{coach_guidance if coach_guidance else '请自行发挥'}
{context_str}

请生成一段符合你角色特点的发言（50-100字）："""

        # 生成备用文本
        fallback = self._get_fallback_speech(agent_name, topic_title, stance_text, phase, coach_guidance)

        return self.call_llm(system, user_prompt, fallback)

    def generate_coach_guidance(
        self,
        opponent_speech: Optional[str],
        topic_title: str,
        stance: str,
        stance_text: str,
        phase: str,
        debate_history: list,
        agent_id: str = "player_coach",
        agent_name: str = "教练"
    ) -> str:
        """生成教练指导"""
        # 获取Soul
        soul = self.soul_manager.get_soul(agent_id)

        # 从Soul中提取系统提示词
        if soul:
            system = self._extract_system_prompt(soul)
        else:
            system = self.prompts.get("coach_system", "你是辩论赛教练。")

        # 构建历史
        history_items = []
        for h in debate_history[-5:]:
            if hasattr(h, '__dict__'):
                d = vars(h) if not hasattr(h, '__slots__') else {k: getattr(h, k) for k in h.__slots__ if hasattr(h, k)}
                speaker = d.get('speaker', d.get('speaker_name', '未知'))
                content = d.get('content', '')[:80]
            else:
                speaker = h.get('speaker', h.get('speaker_name', '未知'))
                content = h.get('content', '')[:80]
            history_items.append(f"{speaker}：{content}")

        history_str = "\n".join(history_items) if history_items else "暂无历史记录"
        opponent_str = opponent_speech[:150] if opponent_speech else "暂无"

        # 根据阶段构建不同的指导要求
        phase_guidance = self._get_coach_phase_guidance(phase)

        user_prompt = f"""辩题：{topic_title}
己方立场：{stance_text}
当前环节：{self._get_phase_name(phase)}

{phase_guidance}

对方的发言：
{opponent_str}

辩论历史（最近几轮）：
{history_str}

请给出50字左右的战术指导："""

        # 生成备用文本
        fallback = self._get_fallback_guidance(agent_name, phase)

        return self.call_llm(system, user_prompt, fallback)

    def _extract_system_prompt(self, soul: str) -> str:
        """从Soul中提取系统提示词"""
        lines = soul.split('\n')
        system_lines = []
        in_system_section = False

        for line in lines:
            if '## 系统提示词' in line or '##system' in line.lower():
                in_system_section = True
                continue
            elif in_system_section and line.startswith('## '):
                break
            elif in_system_section:
                system_lines.append(line)

        if system_lines:
            return '\n'.join(system_lines).strip()
        return soul

    def _clean_think_content(self, content: str) -> str:
        """清理think标签内容，只保留最终结果"""
        import re

        # 模式1: <think>...</think> 标签（提取标签外的内容）
        # 如果有think标签，返回think之后的内容
        think_match = re.search(r'</think>\s*(.*)$', content, re.DOTALL | re.IGNORECASE)
        if think_match:
            result = think_match.group(1).strip()
            if result:
                return result

        # 模式2: <think>...</think> 包裹整个内容
        think_only = re.search(r'<think>\s*(.*?)\s*</think>', content, re.DOTALL | re.IGNORECASE)
        if think_only and not think_match:
            # think标签里是完整内容，说明LLM把思考过程当输出了
            # 返回空或者提示
            return "[思考中...]"

        # 没有think标签，直接返回原内容
        return content

    def _get_phase_name(self, phase: str) -> str:
        """获取环节名称"""
        names = {
            "opening": "开篇立论",
            "rebuttal": "驳论",
            "question": "质询",
            "free_debate": "自由辩论",
            "closing": "总结陈词"
        }
        return names.get(phase, phase)

    def _get_phase_instruction(self, phase: str) -> str:
        """获取环节指令"""
        instructions = {
            "opening": "这是开篇立论环节。请清晰阐述己方核心论点，奠定整场辩论的基调。开场要有气势，论点要有逻辑性。",
            "rebuttal": "这是驳论环节。请针对对方的立论进行反驳，攻击对方论点的薄弱之处。",
            "question": "这是质询环节。请提出尖锐的问题追问对方，或针对对方的问题给出有力回答。",
            "free_debate": "这是自由辩论环节。请与对方展开激烈交锋，攻击对方的论点。",
            "closing": "这是总结陈词环节。请总结己方观点，回应对方的攻击，升华价值。",
        }
        return instructions.get(phase, "")

    def _get_coach_phase_guidance(self, phase: str) -> str:
        """获取教练环节指导"""
        instructions = {
            "opening": "这是开篇立论环节。指导辩手如何清晰有力地阐述核心论点。",
            "rebuttal": "这是驳论环节。指出对方立论的关键漏洞，指导如何有效反驳。",
            "question": "这是质询环节。设计尖锐的问题，追问对方无法回避的关键点。",
            "free_debate": "这是自由辩论环节。分析对方的薄弱环节，提供攻击方向。",
            "closing": "这是总结陈词环节。指导如何强化己方论点，回应质疑，升华价值。",
        }
        return instructions.get(phase, "")

    def _get_fallback_speech(
        self,
        agent_name: str,
        topic_title: str,
        stance_text: str,
        phase: str,
        guidance: str
    ) -> str:
        """获取备用发言（演示用）"""
        side = "正方" if "正方" in agent_name else "反方"

        fallbacks = {
            "opening": f"{side}一辩开篇立论：我方认为{topic_title}。{stance_text[:50]}。谢谢。",
            "rebuttal": f"{side}二辩驳论：针对对方的观点，我方认为{stance_text[20:60]}。谢谢。",
            "question": f"{side}三辩质询：请问对方如何解释{topic_title}中的核心矛盾？请问对方是否承认这一事实？请对方正面回答。",
            "free_debate": f"{side}自由辩论：{guidance[:50] if guidance else '我方坚持原有立场'}。谢谢。",
            "closing": f"{side}三辩总结：综上所述，{stance_text[:30]}，感谢各位聆听。"
        }

        return fallbacks.get(phase, guidance or f"{side}发言：坚持己方立场。")

    def _get_fallback_guidance(self, agent_name: str, phase: str) -> str:
        """获取备用指导（演示用）"""
        side = "正方" if "正方" in agent_name else "反方"

        fallbacks = {
            "opening": f"{side}一辩立论（50-100字）：论点清晰，论据充分，逻辑严密。",
            "rebuttal": f"{side}二辩驳论（50-100字）：攻击对方核心弱点，用逻辑反驳。",
            "question": f"{side}三辩质询（50-100字）：问题尖锐，追问逻辑漏洞。",
            "free_debate": f"{side}自由辩论（50-100字）：保持攻势，专注攻击，简洁有力。",
            "closing": f"{side}三辩总结（50-100字）：回应对方攻击，强化己方论点。"
        }

        return fallbacks.get(phase, "坚持己方立场，逻辑清晰。")


# 全局单例
_llm_client = None


def get_llm_client(config_path: str = None) -> LLMClient:
    """获取LLM客户端单例"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient(config_path)
    return _llm_client


def reset_llm_client():
    """重置LLM客户端"""
    global _llm_client
    _llm_client = None
