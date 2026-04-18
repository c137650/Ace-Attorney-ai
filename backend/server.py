"""
辩论游戏 HTTP API 服务
Flask后端，提供REST API给前端调用
"""

import os
import sys

# 设置编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 前端目录
frontend_dir = os.path.join(os.path.dirname(current_dir), 'frontend')

app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
CORS(app)

# 游戏实例
_game_instance = None
_forced_judgement = None


# ==================== 游戏控制 ====================

@app.route('/api/game/start', methods=['POST'])
def start_game():
    """开始新游戏"""
    global _game_instance, _forced_judgement

    data = request.get_json() or {}

    # 获取参数
    topic_dict = data.get('topic')
    player_stance = data.get('player_stance', 'A')
    use_llm = data.get('use_llm', False)

    # 构建辩题对象
    topic = None
    if topic_dict:
        from game_state import Topic
        topic = Topic(
            id=topic_dict.get('id'),
            title=topic_dict.get('title'),
            description=topic_dict.get('description'),
            stance_a=topic_dict.get('stance_a'),
            stance_b=topic_dict.get('stance_b')
        )

    # 创建游戏实例
    from game_integration import DebateGame
    _game_instance = DebateGame(
        topic=topic,
        use_simple_agents=not use_llm,
        use_llm=use_llm,
        player_stance=player_stance
    )
    _forced_judgement = None

    return jsonify({
        'success': True,
        'status': _game_instance.get_game_status()
    })


@app.route('/api/game/demo/force_opponent_win', methods=['POST'])
def force_demo_opponent_win():
    """演示模式：一键跳到结局并判定对手方获胜"""
    global _forced_judgement

    if _game_instance is None:
        return jsonify({'success': False, 'error': '游戏未开始'})

    if _game_instance.use_llm:
        return jsonify({'success': False, 'error': '仅演示模式支持此功能'})

    from game_state import GamePhase

    winner_label = '反方胜' if _game_instance.player_stance == 'A' else '正方胜'
    _forced_judgement = {
        'winner': 'opponent',
        'winner_label': winner_label,
        'summary': '演示模式已触发：直接跳转至结局并判定对手方获胜。你可继续进行两轮“和裁判对轰”加赛。',
        'scores': {
            'player': {'score': 48},
            'opponent': {'score': 72}
        }
    }

    _game_instance.state.phase = GamePhase.FINISHED
    _game_instance.state.current_phase = ''

    return jsonify({
        'success': True,
        'status': _game_instance.get_game_status(),
        'judgement': _forced_judgement
    })


@app.route('/api/game/status', methods=['GET'])
def get_status():
    """获取游戏状态"""
    if _game_instance is None:
        return jsonify({'success': False, 'error': '游戏未开始'})

    return jsonify({
        'success': True,
        'status': _game_instance.get_game_status()
    })


@app.route('/api/game/guidance', methods=['POST'])
def submit_guidance():
    """提交教练指导"""
    if _game_instance is None:
        return jsonify({'success': False, 'error': '游戏未开始'})

    data = request.get_json() or {}
    guidance = data.get('guidance', '')
    target_index = data.get('target_index')
    asker_index = data.get('asker_index')

    if target_index is not None:
        try:
            target_index = int(target_index)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'target_index 必须是 0-2 的整数'})

        if target_index not in (0, 1, 2):
            return jsonify({'success': False, 'error': 'target_index 必须在 0-2 之间'})

    if asker_index is not None:
        try:
            asker_index = int(asker_index)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'asker_index 必须是 0-2 的整数'})

        if asker_index not in (0, 1, 2):
            return jsonify({'success': False, 'error': 'asker_index 必须在 0-2 之间'})

    try:
        result = _game_instance.process_player_guidance(
            guidance,
            free_debate_target_index=target_index,
            free_debate_asker_index=asker_index,
        )
        return jsonify({
            'success': True,
            'result': result,
            'status': _game_instance.get_game_status()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/game/ai_turn', methods=['POST'])
def ai_turn():
    """AI回合"""
    if _game_instance is None:
        return jsonify({'success': False, 'error': '游戏未开始'})

    try:
        result = _game_instance.advance_turn()
        return jsonify({
            'success': True,
            'result': result,
            'status': _game_instance.get_game_status()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/game/history', methods=['GET'])
def get_history():
    """获取发言历史"""
    if _game_instance is None:
        return jsonify({'success': False, 'error': '游戏未开始'})

    return jsonify({
        'success': True,
        'history': _game_instance.speech_history,
        'status': _game_instance.get_game_status()
    })


@app.route('/api/game/is_over', methods=['GET'])
def is_game_over():
    """检查游戏是否结束"""
    if _game_instance is None:
        return jsonify({'success': False, 'error': '游戏未开始'})

    return jsonify({
        'success': True,
        'is_over': _game_instance.is_game_over()
    })


@app.route('/api/game/judgement', methods=['GET'])
def get_game_judgement():
    """比赛结束后给出裁判裁决（基于双方历史发言）"""
    global _forced_judgement

    if _game_instance is None:
        return jsonify({'success': False, 'error': '游戏未开始'})

    if _forced_judgement is not None:
        return jsonify({'success': True, 'judgement': _forced_judgement})

    if not _game_instance.is_game_over():
        return jsonify({'success': False, 'error': '比赛尚未结束'})

    judgement = _build_judgement_payload(_game_instance)
    return jsonify({'success': True, 'judgement': judgement})


def _build_judgement_payload(game_instance):
    """基于历史发言构建裁判裁决"""
    global _forced_judgement

    if _forced_judgement is not None:
        return _forced_judgement

    history = list(game_instance.speech_history or [])

    if not history:
        winner = 'opponent'
        winner_label = '反方胜' if game_instance.player_stance == 'A' else '正方胜'
        return {
            'winner': winner,
            'winner_label': winner_label,
            'summary': '未检测到有效发言记录，按规则判定对手方获胜。'
        }

    # 规范化历史结构，确保后续评分稳定
    normalized_history = []
    for item in history:
        if not isinstance(item, (list, tuple)) or len(item) < 3:
            continue
        side = str(item[0])
        try:
            index = int(item[1])
        except (TypeError, ValueError):
            index = 0
        content = str(item[2] or '')
        normalized_history.append((side, index, content))

    if not normalized_history:
        winner = 'opponent'
        winner_label = '反方胜' if game_instance.player_stance == 'A' else '正方胜'
        return {
            'winner': winner,
            'winner_label': winner_label,
            'summary': '历史记录格式异常，无法有效评审，按规则判定对手方获胜。'
        }

    from judge import judge_debate

    judge_result = judge_debate(game_instance.state, normalized_history)
    winner = judge_result.get('winner') or 'draw'

    player_texts = [content.strip() for side, _index, content in normalized_history if side == 'player']
    opponent_texts = [content.strip() for side, _index, content in normalized_history if side == 'opponent']
    player_rounds = len(player_texts)
    opponent_rounds = len(opponent_texts)
    player_chars = sum(len(text) for text in player_texts)
    opponent_chars = sum(len(text) for text in opponent_texts)

    # 平局时基于历史完整度做决胜，避免没有明确输赢
    if winner == 'draw':
        if player_chars != opponent_chars:
            winner = 'player' if player_chars > opponent_chars else 'opponent'
        elif player_rounds != opponent_rounds:
            winner = 'player' if player_rounds > opponent_rounds else 'opponent'
        else:
            winner = 'opponent'

    if winner == 'player':
        winner_label = '正方胜' if game_instance.player_stance == 'A' else '反方胜'
    else:
        winner_label = '反方胜' if game_instance.player_stance == 'A' else '正方胜'

    phase_counter = {}
    for round_item in getattr(game_instance.state, 'rounds', []):
        phase = getattr(round_item, 'phase', '') or 'unknown'
        phase_counter[phase] = phase_counter.get(phase, 0) + 1

    phase_desc = '、'.join([f"{k}:{v}" for k, v in phase_counter.items()]) if phase_counter else '无'
    reasons = [str(r).strip() for r in (judge_result.get('reasons') or []) if str(r).strip()]
    if not reasons:
        reasons = ['裁判未返回细分理由，依据历史发言完整度判定。']

    summary_lines = [
        f"历史记录统计：玩家方{player_rounds}轮，共{player_chars}字；对手方{opponent_rounds}轮，共{opponent_chars}字。",
        f"按环节记录：{phase_desc}",
        '裁判理由：' + '；'.join(reasons),
        f"最终判定：{winner_label}。"
    ]

    return {
        'winner': winner,
        'winner_label': winner_label,
        'summary': '\n'.join(summary_lines),
        'scores': {
            'player': {
                'score': round(float(judge_result.get('player_score', 0.0)), 2),
                'rounds': player_rounds,
                'total_chars': player_chars
            },
            'opponent': {
                'score': round(float(judge_result.get('opponent_score', 0.0)), 2),
                'rounds': opponent_rounds,
                'total_chars': opponent_chars
            }
        },
        'reasons': reasons,
        'analysis': judge_result.get('analysis', {})
    }


@app.route('/api/game/judge_clash', methods=['POST'])
def judge_clash():
    """玩家败诉后与裁判对轰（最多2轮来回）"""
    if _game_instance is None:
        return jsonify({'success': False, 'error': '游戏未开始'})

    if not _game_instance.is_game_over():
        return jsonify({'success': False, 'error': '比赛尚未结束'})

    judgement = _build_judgement_payload(_game_instance)
    if judgement.get('winner') != 'opponent':
        return jsonify({'success': False, 'error': '仅当人类玩家败诉时可与裁判对轰'})

    data = request.get_json() or {}
    message = str(data.get('message', '')).strip()
    round_index = data.get('round')

    if not message:
        return jsonify({'success': False, 'error': '请输入对轰内容'})

    try:
        round_index = int(round_index)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'round 参数无效'})

    if round_index not in (1, 2):
        return jsonify({'success': False, 'error': '对轰仅支持2轮'})

    opening = [
        '裁判回应：你有斗志，但请回到论证结构。',
        '裁判回应：气势不错，不过胜负仍看论据和反驳质量。'
    ]

    closing = [
        '裁判终裁：情绪可以加分观感，但不会改变证据权重。',
        '裁判终裁：你这两轮反击很精彩，建议下局把证据链做得更完整。'
    ]

    if round_index == 1:
        judge_reply = f"{opening[0]} 你刚才说「{message[:24]}」这点，我记录了。"
    else:
        judge_reply = f"{closing[1]} 本场最终判定保持：{judgement.get('winner_label', '未判定')}。"

    return jsonify({
        'success': True,
        'round': round_index,
        'max_rounds': 2,
        'judge_reply': judge_reply
    })


# ==================== 辩题 ====================

@app.route('/api/topics', methods=['GET'])
def get_topics():
    """获取所有辩题"""
    try:
        from topic_loader import get_all_topics
        topics = get_all_topics()
        return jsonify({
            'success': True,
            'topics': [t.__dict__ for t in topics]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/topics/random', methods=['GET'])
def get_random_topic():
    """获取随机辩题"""
    try:
        from topic_loader import get_random_topic as _get_random_topic
        topic = _get_random_topic()
        return jsonify({
            'success': True,
            'topic': topic.__dict__ if topic else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== Soul管理 ====================

@app.route('/api/souls', methods=['GET'])
def get_souls():
    """获取所有Soul"""
    try:
        from soul_manager import get_soul_manager
        manager = get_soul_manager()

        souls = {}
        for agent_id in manager.get_all_agent_ids():
            souls[agent_id] = {
                'id': agent_id,
                'name': manager.get_agent_name(agent_id),
                'content': manager.get_soul(agent_id),
                'editable': manager.is_player_editable(agent_id)
            }

        return jsonify({'success': True, 'souls': souls})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/souls/<agent_id>', methods=['GET'])
def get_soul(agent_id):
    """获取指定Soul"""
    try:
        from soul_manager import get_soul_manager
        manager = get_soul_manager()

        content = manager.get_soul(agent_id)
        return jsonify({
            'success': True,
            'soul': {
                'id': agent_id,
                'name': manager.get_agent_name(agent_id),
                'content': content,
                'editable': manager.is_player_editable(agent_id)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/souls/<agent_id>', methods=['PUT'])
def update_soul(agent_id):
    """更新Soul"""
    try:
        from soul_manager import get_soul_manager
        manager = get_soul_manager()

        if not manager.is_player_editable(agent_id):
            return jsonify({'success': False, 'error': '该Soul不可编辑'})

        data = request.get_json() or {}
        content = data.get('content', '')

        success = manager.save_soul(agent_id, content)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/souls/<agent_id>/reset', methods=['POST'])
def reset_soul(agent_id):
    """重置Soul到模板"""
    try:
        from soul_manager import get_soul_manager
        manager = get_soul_manager()

        success = manager.reset_to_template(agent_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


# ==================== 前端页面 ====================

@app.route('/')
def index():
    """主页"""
    return send_from_directory(frontend_dir, 'index.html')


@app.route('/soul-editor')
def soul_editor_page():
    """Soul编辑器页面"""
    return send_from_directory(frontend_dir, 'soul_editor.html')


@app.route('/<path:filename>')
def serve_static(filename):
    """提供静态文件"""
    import os
    # 确保路径安全
    safe_path = os.path.normpath(filename)
    target_path = os.path.join(frontend_dir, safe_path)
    
    # 检查文件是否存在
    if os.path.isfile(target_path):
        return send_from_directory(frontend_dir, safe_path)
    else:
        # 文件不存在
        print(f"[404] 文件未找到: {target_path}")
        return f"File not found: {filename}", 404


if __name__ == '__main__':
    print("=" * 50)
    print("AI 辩论游戏 - Web服务")
    print("=" * 50)
    print("访问 http://127.0.0.1:5000 开始游戏")
    print("=" * 50)

    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)
