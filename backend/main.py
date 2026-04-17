"""
AI辩论游戏 - 后端主程序
开题立论环节演示
"""

import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from game_state import GameState, GamePhase, create_initial_state
from debate_flow import DebateFlow
from topic_loader import load_topics, get_random_topic


def print_game_status(flow: DebateFlow):
    """打印游戏状态"""
    status = flow.get_game_status()
    print("\n" + "=" * 60)
    print(f"【当前环节】{status['current_phase']}")
    print(f"【当前轮次】第 {status['current_round']} 轮")
    print(f"【当前回合】{status['turn_description']}")
    print(f"【是否玩家回合】{'是' if status['is_player_turn'] else '否'}")
    print("=" * 60)


def print_speaker_result(result):
    """打印发言结果"""
    print(f"\n【{result.speaker_name}】")
    print("-" * 40)
    print(result.content)
    print("-" * 40)


def demo_opening_phase():
    """演示开篇立论环节"""
    print("\n" + "=" * 60)
    print("🎯 AI 辩论游戏 - 开篇立论环节演示")
    print("=" * 60)

    # 加载辩题
    topic = get_random_topic()
    if not topic:
        print("错误：未找到辩题！")
        return

    print(f"\n📋 辩题：{topic.title}")
    print(f"📝 描述：{topic.description}")

    # 创建游戏状态
    state = create_initial_state(topic)
    print(f"\n🎲 随机分配：玩家方为【{state.player_stance}】方")
    print(f"   {topic.stance_a if state.player_stance == 'A' else topic.stance_b}")

    # 创建辩论流程
    flow = DebateFlow(state, use_simple_agents=True)

    print("\n" + "=" * 60)
    print("📖 开篇立论环节规则")
    print("=" * 60)
    print("1. 玩家方一辩先发言（50-100字）")
    print("2. 对手方一辩发言（50-100字）")
    print("3. 环节结束，进入驳论")
    print("=" * 60)

    # ========== 环节1：开篇立论 ==========
    print("\n\n" + "🏆 " + "=" * 54 + "🏆")
    print("                    环节1：开篇立论")
    print("🏆 " + "=" * 54 + "🏆\n")

    # ----- 玩家方一辩发言 -----
    print("【步骤1】玩家方一辩开篇立论")
    print("请输入你的教练指导（直接回车使用默认策略）：")

    player_guidance = input("> ").strip()
    if not player_guidance:
        player_guidance = "一辩立论（50-100字）：核心论点要清晰有力，举例说明，升华价值。"

    print_game_status(flow)

    result = flow.process_player_input(player_guidance)
    print_speaker_result(result)

    # ----- 对手方一辩发言 -----
    print("\n【步骤2】对手方一辩发言...")
    result = flow.advance_turn()  # 对手方一辩发言
    print_speaker_result(result)

    print("\n✅ 开篇立论环节完成！")

    # 打印辩论记录
    print("\n" + "=" * 60)
    print("📜 当前辩论记录")
    print("=" * 60)
    for i, round_record in enumerate(state.rounds, 1):
        speaker_label = f"{'玩家' if round_record.speaker_side == 'player' else '对手'}"
        print(f"\n[第{i}轮] {speaker_label}方发言：")
        print(f"  {round_record.content[:80]}...")

    print("\n" + "=" * 60)
    print("✅ 开篇立论环节演示完成！")
    print("💡 提示：选择模式3可查看完整流程（包含驳论+质询）")
    print("=" * 60)

    return flow


def demo_question_phase():
    """演示质询环节"""
    print("\n" + "=" * 60)
    print("🎯 AI 辩论游戏 - 质询环节演示")
    print("=" * 60)

    # 加载辩题
    topic = get_random_topic()
    if not topic:
        print("错误：未找到辩题！")
        return

    print(f"\n📋 辩题：{topic.title}")

    # 创建游戏状态
    state = create_initial_state(topic)
    print(f"\n🎲 随机分配：玩家方为【{state.player_stance}】方")

    # 创建辩论流程
    flow = DebateFlow(state, use_simple_agents=True)

    # 直接跳到质询环节
    from game_state import TurnType
    state.current_phase = "question"
    state.current_round = 1
    state.current_turn = TurnType.PLAYER_QUESTION

    print("\n" + "=" * 60)
    print("📖 质询环节规则")
    print("=" * 60)
    print("质询流程：")
    print("  1. 玩家方三辩提问（玩家教练指导）")
    print("  2. 对手方三辩回答")
    print("  3. 对手方三辩提问")
    print("  4. 玩家方三辩回答（玩家教练指导）")
    print("=" * 60)

    # ========== 环节3：质询 ==========
    print("\n\n" + "🏆 " + "=" * 54 + "🏆")
    print("                    环节3：质询")
    print("🏆 " + "=" * 54 + "🏆\n")

    # ----- 玩家方三辩提问 -----
    print("【步骤1】玩家方三辩提问")
    print("请输入你的教练指导（直接回车使用默认策略）：")

    player_guidance = input("> ").strip()
    if not player_guidance:
        player_guidance = "质询（50-100字）：问题1：请问对方如何解释核心矛盾？问题2：对方是否承认这个事实？问题3：请正面回答。"

    result = flow.process_player_input(player_guidance)
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    # ----- 对手方三辩回答 -----
    print("\n【步骤2】对手方三辩回答...")
    result = flow.advance_turn()
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    # ----- 对手方三辩提问 -----
    print("\n【步骤3】对手方三辩提问...")
    result = flow.advance_turn()
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    # ----- 玩家方三辩回答 -----
    print("\n【步骤4】玩家方三辩回答")
    print("请输入你的教练指导（直接回车使用默认策略）：")

    player_guidance = input("> ").strip()
    if not player_guidance:
        player_guidance = "回答：对方的提问存在前提错误，我方不予承认。坚持己方立场。"

    result = flow.process_player_input(player_guidance)
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    # 打印辩论记录
    print("\n" + "=" * 60)
    print("📜 质询环节辩论记录")
    print("=" * 60)
    for i, round_record in enumerate(state.rounds, 1):
        speaker_label = f"{'玩家' if round_record.speaker_side == 'player' else '对手'}"
        role_label = round_record.turn_type.value.replace("_", " ")
        print(f"\n[第{i}轮] {speaker_label}方 - {role_label}：")
        print(f"  {round_record.content[:80]}...")

    print("\n" + "=" * 60)
    print("✅ 质询环节演示完成！")
    print("=" * 60)

    return flow


def interactive_demo():
    """交互式演示"""
    print("\n" + "=" * 60)
    print("🎮 AI 辩论游戏 - 完整流程演示（简化版）")
    print("=" * 60)

    # 加载辩题
    topic = get_random_topic()
    if not topic:
        print("错误：未找到辩题！")
        return

    print(f"\n📋 辩题：{topic.title}")
    print(f"📝 描述：{topic.description}")

    # 创建游戏状态
    state = create_initial_state(topic)
    print(f"\n🎲 随机分配：玩家方为【{state.player_stance}】方")
    stance_text = topic.stance_a if state.player_stance == "A" else topic.stance_b
    print(f"   你的立场：{stance_text[:60]}...")

    # 创建辩论流程
    flow = DebateFlow(state, use_simple_agents=True)

    # ===== 环节1：开篇立论 =====
    print("\n\n" + "🏆 " + "=" * 54 + "🏆")
    print("                    环节1：开篇立论")
    print("🏆 " + "=" * 54 + "🏆\n")

    # 玩家方一辩
    print("【玩家方一辩发言】请输入教练指导（直接回车跳过）：")
    guidance = input("> ").strip() or "立论要清晰有力，用数据和案例支撑观点。"
    result = flow.process_player_input(guidance)
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    # 对手方一辩
    print("\n【对手方一辩发言】")
    result = flow.advance_turn()  # 对手方一辩发言
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    print("\n✅ 开篇立论完成！")
    print(f"\n当前状态：{flow.state.current_phase} - 第{flow.state.current_round}轮 - {flow.state.current_turn.value}")
    print(f"下一环节：驳论")

    # ===== 环节2：驳论 =====
    print("\n\n" + "🏆 " + "=" * 54 + "🏆")
    print("                    环节2：驳论")
    print("🏆 " + "=" * 54 + "🏆\n")

    # 对手方二辩驳论
    print("【对手方二辩驳论】")
    result = flow.advance_turn()
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    # 玩家方二辩驳论
    print("\n【玩家方二辩驳论】请输入教练指导（直接回车跳过）：")
    guidance = input("> ").strip() or "攻击对方逻辑漏洞，用事实反驳。"
    result = flow.process_player_input(guidance)
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    print("\n✅ 驳论完成！")

    # ===== 环节3：质询 =====
    print("\n\n" + "🏆 " + "=" * 54 + "🏆")
    print("                    环节3：质询")
    print("🏆 " + "=" * 54 + "🏆\n")

    print("📖 质询规则：")
    print("   1. 提问方提出2-3个尖锐问题")
    print("   2. 回答方需简短正面回应")
    print("   3. 提问方追问（可选）")
    print()

    # 玩家方三辩提问
    print("【玩家方三辩提问】请输入教练指导（直接回车跳过）：")
    guidance = input("> ").strip() or "质询指导：提出3个尖锐问题，攻击对方逻辑漏洞。"
    result = flow.process_player_input(guidance)
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    # 对手方三辩回答
    print("\n【对手方三辩回答】")
    result = flow.advance_turn()
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    # 对手方三辩提问
    print("\n【对手方三辩提问】")
    result = flow.advance_turn()
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    # 玩家方三辩回答
    print("\n【玩家方三辩回答】请输入教练指导（直接回车跳过）：")
    guidance = input("> ").strip() or "回答指导：坚持立场，简短有力回应，不纠缠陷阱。"
    result = flow.process_player_input(guidance)
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    print("\n✅ 质询完成！")

    # ===== 环节4：自由辩论 =====
    print("\n\n" + "🏆 " + "=" * 54 + "🏆")
    print("                    环节4：自由辩论")
    print("🏆 " + "=" * 54 + "🏆\n")

    print("📖 自由辩论规则：")
    print("   - 每方8轮，共16轮")
    print("   - 玩家方/对手方交替发言")
    print("   - 每轮50-100字")
    print("   - 教练每轮给指令")
    print("=" * 60)

    # 自由辩论：16轮
    free_debate_rounds = 8  # 每方8轮

    for i in range(free_debate_rounds):
        # ----- 玩家方发言 -----
        player_round = i + 1
        print(f"\n【第{player_round}轮 - 玩家方发言】")
        print("请输入教练指导（直接回车跳过）：")
        guidance = input("> ").strip() or f"自由辩论第{player_round}轮：攻击对方弱点，坚持己方立场。"
        result = flow.process_player_input(guidance)
        print(f"\n>>> {result.speaker_name}：")
        print(result.content)

        # ----- 对手方发言 -----
        print(f"\n【第{player_round}轮 - 对手方发言】")
        result = flow.advance_turn()
        print(f"\n>>> {result.speaker_name}：")
        print(result.content)

    print("\n✅ 自由辩论完成！")

    # ===== 环节5：总结陈词 =====
    print("\n\n" + "🏆 " + "=" * 54 + "🏆")
    print("                    环节5：总结陈词")
    print("🏆 " + "=" * 54 + "🏆\n")

    # 对手方三辩总结
    print("【对手方三辩总结陈词】")
    result = flow.advance_turn()
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    # 玩家方三辩总结
    print("\n【玩家方三辩总结陈词】请输入教练指导（直接回车跳过）：")
    guidance = input("> ").strip() or "总结陈词：回应对手攻击，强化己方论点，升华价值。"
    result = flow.process_player_input(guidance)
    print(f"\n>>> {result.speaker_name}：")
    print(result.content)

    print("\n" + "=" * 60)
    print("✅ 辩论赛结束！")
    print("=" * 60)

    # 打印辩论记录摘要
    print("\n📜 辩论记录摘要")
    print("=" * 60)
    for i, round_record in enumerate(state.rounds, 1):
        speaker_label = f"{'玩家' if round_record.speaker_side == 'player' else '对手'}"
        turn_label = round_record.turn_type.value.replace("_", " ")
        print(f"[{i}] {speaker_label}方 - {turn_label}")
    print("=" * 60)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎮 AI 辩论游戏 - 后端演示")
    print("=" * 60)
    print("\n选择模式：")
    print("1. 开篇立论环节详细演示（仅立论）")
    print("2. 质询环节详细演示（仅质询）")
    print("3. 【推荐】完整流程演示（立论+驳论+质询+自由辩论+总结）")
    print("4. 仅测试辩题加载")

    choice = input("\n请选择 (1/2/3/4): ").strip()

    if choice == "1":
        demo_opening_phase()
    elif choice == "2":
        demo_question_phase()
    elif choice == "3":
        interactive_demo()
    elif choice == "4":
        topics = load_topics()
        print(f"\n加载到 {len(topics)} 个辩题：")
        for t in topics:
            print(f"  - {t.id}: {t.title}")
    else:
        print("无效选择，运行简化演示...")
        demo_opening_phase()
