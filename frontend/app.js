/**
 * AI辩论游戏 - 前端逻辑
 */

const API_BASE = 'http://127.0.0.1:5000/api';

// ==================== 音频管理 ====================
const audio = {
    menuBgm: new Audio('/musics/startmenu.wav'),
    gameBgm: new Audio('/musics/background.wav'),
    button: new Audio('/musics/button.wav'),
    horse: new Audio('/musics/horse.wav'),
    donkey: new Audio('/musics/donkey.wav')
};

Object.values(audio).forEach((item) => {
    item.preload = 'auto';
});

audio.menuBgm.loop = true;
audio.gameBgm.loop = true;
audio.menuBgm.volume = 1.0;
audio.gameBgm.volume = 1.0;
audio.button.volume = 1.0;
audio.horse.volume = 1.0;
audio.donkey.volume = 1.0;

let audioUnlocked = false;
let activeBgmKey = null;
let audioContext = null;
let audioMasterGain = null;
const audioGainNodes = new Map();

function getBoostGain(name) {
    const gainMap = {
        menuBgm: 2.0,
        gameBgm: 2.0,
        button: 1.0,
        horse: 1.0,
        donkey: 1.0
    };
    return gainMap[name] || 1.0;
}

function initAudioBoost() {
    if (audioContext) return;

    const Ctx = window.AudioContext || window.webkitAudioContext;
    if (!Ctx) return;

    audioContext = new Ctx();
    audioMasterGain = audioContext.createGain();
    audioMasterGain.gain.value = 1.0;
    audioMasterGain.connect(audioContext.destination);

    Object.entries(audio).forEach(([name, element]) => {
        const source = audioContext.createMediaElementSource(element);
        const gainNode = audioContext.createGain();
        gainNode.gain.value = getBoostGain(name);
        source.connect(gainNode);
        gainNode.connect(audioMasterGain);
        audioGainNodes.set(name, gainNode);
    });
}

function safePlay(audioObj) {
    if (!audioObj) return;
    const promise = audioObj.play();
    if (promise && typeof promise.catch === 'function') {
        promise.catch(() => {});
    }
}

function stopAudio(audioObj) {
    if (!audioObj) return;
    audioObj.pause();
    audioObj.currentTime = 0;
}

function getBgmByKey(key) {
    if (key === 'menu') return audio.menuBgm;
    if (key === 'game') return audio.gameBgm;
    return null;
}

function ensureBgmLoop(audioObj) {
    if (!audioObj) return;
    audioObj.loop = true;
    audioObj.addEventListener('ended', () => {
        if (!audioUnlocked) return;
        if (getBgmByKey(activeBgmKey) !== audioObj) return;
        audioObj.currentTime = 0;
        safePlay(audioObj);
    });
}

ensureBgmLoop(audio.menuBgm);
ensureBgmLoop(audio.gameBgm);

function playBgmByPage(pageId) {
    if (!audioUnlocked) return;

    const isMenu = pageId === 'menu-page';
    activeBgmKey = isMenu ? 'menu' : 'game';
    const target = isMenu ? audio.menuBgm : audio.gameBgm;
    const other = isMenu ? audio.gameBgm : audio.menuBgm;

    if (!target.paused) {
        return;
    }

    stopAudio(other);
    safePlay(target);
}

function unlockAudio() {
    if (audioUnlocked) return;

    initAudioBoost();
    if (audioContext && audioContext.state === 'suspended') {
        audioContext.resume().catch(() => {});
    }

    audioUnlocked = true;
    const pageId = `${state.currentPage || 'menu'}-page`;
    playBgmByPage(pageId);
}

function playSfx(audioObj) {
    if (!audioUnlocked) return;
    audioObj.currentTime = 0;
    safePlay(audioObj);
}

function playSpeechSfx(side) {
    if (side === 'player') {
        playSfx(audio.horse);
    } else if (side === 'opponent') {
        playSfx(audio.donkey);
    }
}

// ==================== 状态管理 ====================
const state = {
    currentPage: 'menu',
    topics: [],
    selectedTopicIndex: 0,
    selectedTopic: null,
    playerStance: 'A', // A=正方, B=反方
    gameStatus: null,
    history: [],
    useLLM: false,
    soulAgents: [],
    soulCurrentIndex: 0,
    isTyping: false,
    typingTimeout: null,
    judgeResult: null,
    judgeClashRound: 0,
    judgeClashMaxRounds: 2,
    judgeClashHistory: [],
    judgeClashSubmitting: false
};

// ==================== 页面控制 ====================
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
    document.getElementById(pageId).classList.remove('hidden');
    state.currentPage = pageId.replace('-page', '');
    playBgmByPage(pageId);
}

// ==================== API调用 ====================
async function api(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: { 'Content-Type': 'application/json' },
        ...options
    };
    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }
    const response = await fetch(url, config);
    return response.json();
}

function normalizeHistoryItem(item) {
    if (Array.isArray(item)) {
        const [side, index, content] = item;
        return [side, Number(index), String(content || '')];
    }

    if (item && typeof item === 'object') {
        const side = item.side || item.speaker_side || '';
        const index = item.index ?? item.speaker_index ?? 0;
        const content = item.content || item.speech || '';
        return [side, Number(index), String(content)];
    }

    return null;
}

async function syncHistoryFromServer() {
    const result = await api('/game/history');
    if (result.success && Array.isArray(result.history)) {
        state.history = result.history
            .map(normalizeHistoryItem)
            .filter(Boolean);
    }
}

// ==================== 菜单页面 ====================
document.getElementById('btn-start').addEventListener('click', async () => {
    state.useLLM = document.getElementById('llm-mode').checked;
    
    // 直接获取随机辩题并进入立场选择
    const result = await api('/topics/random');
    if (result.success && result.topic) {
        state.selectedTopic = result.topic;
        showStancePage();
    }
});

document.getElementById('btn-soul-editor').addEventListener('click', () => {
    window.location.href = '/soul-editor';
});

// LLM模式切换
document.getElementById('llm-mode').addEventListener('change', (e) => {
    state.useLLM = e.target.checked;
    const text = e.target.nextElementSibling.nextElementSibling;
    text.textContent = e.target.checked ? '🤖 AI模式' : '📝 演示模式';
});

// ==================== 立场选择页面 ====================
document.getElementById('btn-change-topic').addEventListener('click', async () => {
    // 重新获取随机辩题
    const result = await api('/topics/random');
    if (result.success && result.topic) {
        state.selectedTopic = result.topic;
        showStancePage();
    }
});

function showStancePage() {
    const topic = state.selectedTopic;
    document.getElementById('selected-topic').textContent = topic.title;
    document.getElementById('stance-a-text').textContent = topic.stance_a;
    document.getElementById('stance-b-text').textContent = topic.stance_b;

    state.playerStance = 'A';
    updateStanceSelection();

    showPage('stance-page');
}

function updateStanceSelection() {
    const positive = document.getElementById('stance-positive');
    const negative = document.getElementById('stance-negative');

    positive.classList.toggle('selected', state.playerStance === 'A');
    negative.classList.toggle('selected', state.playerStance === 'B');
}

function sideToStanceLabel(side) {
    if (!state.gameStatus) {
        return side === 'player' ? '我方' : '对方';
    }

    if (state.gameStatus.player_stance === 'A') {
        return side === 'player' ? '正方' : '反方';
    }

    return side === 'player' ? '反方' : '正方';
}

function selectStance(stance) {
    state.playerStance = stance;
    updateStanceSelection();
}

document.getElementById('stance-positive').addEventListener('click', () => selectStance('A'));
document.getElementById('stance-negative').addEventListener('click', () => selectStance('B'));

document.getElementById('btn-confirm-stance').addEventListener('click', startGame);

// ==================== 游戏逻辑 ====================
async function startGame() {
    const result = await api('/game/start', {
        method: 'POST',
        body: {
            topic: state.selectedTopic,
            player_stance: state.playerStance,
            use_llm: state.useLLM
        }
    });

    if (result.success) {
        state.gameStatus = result.status;
        state.history = [];
        state.judgeResult = null;
        await syncHistoryFromServer();
        updateGameUI();
        showPage('game-page');
        initSoulAgents();

        // 如果是AI回合，自动推进
        if (!state.gameStatus.is_player_turn) {
            setTimeout(doAITurn, 1000);
        }
    }
}

function updateGameUI() {
    const status = state.gameStatus;
    if (!status) return;

    // 辩题
    document.getElementById('game-topic').textContent = status.topic;

    // 立场
    const stanceName = status.player_stance === 'A' ? '正方' : '反方';
    const stanceText = status.player_stance === 'A' ?
        state.selectedTopic?.stance_a : state.selectedTopic?.stance_b;
    document.getElementById('game-stance').textContent = `${stanceName}：${stanceText}`;

    // 环节
    document.getElementById('game-phase').textContent = status.phase_name;
    document.getElementById('phase-step').textContent = status.phase_info?.step || 1;
    document.getElementById('phase-total').textContent = status.phase_info?.total_steps || 1;

    // 当前发言者
    const speaker = status.phase_info?.current_speaker_name || '等待中...';
    document.getElementById('game-speaker').textContent = speaker;

    // 回合指示器
    const indicator = document.getElementById('turn-indicator');
    const indicatorText = document.getElementById('indicator-text');
    if (status.current_phase === 'free_debate' && status.current_turn === 'player_question') {
        indicator.className = 'panel-section turn-indicator player-turn';
        indicatorText.textContent = '>>> 你的回合：系统已随机匹配双方成员，输入指导发起质询 <<<';
    } else if (status.current_phase === 'free_debate' && status.current_turn === 'player_answer') {
        indicator.className = 'panel-section turn-indicator player-turn';
        indicatorText.textContent = '>>> 你的回合：被质询成员回答 <<<';
    } else if (status.is_player_turn) {
        indicator.className = 'panel-section turn-indicator player-turn';
        indicatorText.textContent = '>>> 等待你的指导 <<<';
    } else {
        indicator.className = 'panel-section turn-indicator opponent-turn';
        indicatorText.textContent = '>>> AI正在发言 <<<';
    }

    // 教练指导区域始终显示，AI回合仅禁用输入避免“消失”体验
    const guidanceSection = document.getElementById('guidance-section');
    const guidanceInput = document.getElementById('guidance-input');
    const submitBtn = document.getElementById('btn-submit-guidance');
    const skipBtn = document.getElementById('btn-skip-guidance');

    guidanceSection.style.display = 'block';
    guidanceInput.disabled = !status.is_player_turn;
    submitBtn.disabled = !status.is_player_turn;
    skipBtn.disabled = !status.is_player_turn;

    if (!status.is_player_turn) {
        guidanceInput.placeholder = 'AI回合进行中，等待下一轮可输入';
    } else if (status.current_phase === 'free_debate' && status.current_turn === 'player_answer') {
        guidanceInput.placeholder = '输入指导，让被质询成员作答...';
    } else if (status.current_phase === 'free_debate' && status.current_turn === 'player_question') {
        guidanceInput.placeholder = '输入指导并选择双方成员发起质询...';
    } else {
        guidanceInput.placeholder = '输入你的战术指导...';
    }

    const demoTools = document.getElementById('demo-tools');
    demoTools.classList.toggle('hidden', state.useLLM);

    // 更新辩手发言状态
    updateDebaterSeats();

    // 渲染历史记录
    renderHistory();
}

function updateDebaterSeats() {
    const status = state.gameStatus;
    if (!status) return;

    // 清除所有发言状态
    document.querySelectorAll('.person').forEach(p => {
        p.classList.remove('speaking');
    });

    // 设置当前发言者
    const speakerSide = status.phase_info?.current_speaker_side;
    const speakerIndex = status.phase_info?.current_speaker_index;

    if (speakerSide && speakerIndex !== undefined) {
        let seatId;
        if (speakerSide === 'player') {
            seatId = `player-${speakerIndex}`;
        } else {
            seatId = `opponent-${speakerIndex}`;
        }
        const seat = document.getElementById(seatId);
        if (seat) {
            seat.classList.add('speaking');
        }
    }
}

function renderHistory() {
    const list = document.getElementById('history-list');
    list.innerHTML = '';

    if (state.history.length === 0) {
        list.innerHTML = '<div class="history-item"><div class="history-content"><div class="line">暂无发言记录</div></div></div>';
        return;
    }

    state.history.forEach(item => {
        const [side, index, content] = item;
        const div = document.createElement('div');
        div.className = `history-item ${side}`;

        const sideName = sideToStanceLabel(side).replace('方', '');
        const debaterNames = ['一', '二', '三'];
        const name = debaterNames[index] || '';

        // 分行显示内容
        const lines = wrapText(content, 22);
        const linesHtml = lines.slice(0, 3).map(line =>
            `<div class="line">${line}</div>`
        ).join('');

        div.innerHTML = `
            <div class="history-header">
                <span class="history-side">[${sideName}${name}]</span>
            </div>
            <div class="history-content">${linesHtml}</div>
        `;
        list.appendChild(div);
    });

    list.scrollTop = list.scrollHeight;
}

function wrapText(text, maxChars) {
    const lines = [];
    let current = '';
    for (const char of text) {
        current += char;
        if (current.length >= maxChars) {
            lines.push(current);
            current = '';
        }
    }
    if (current) lines.push(current);
    return lines.length ? lines : [''];
}

// ==================== 玩家输入 ====================
document.getElementById('btn-submit-guidance').addEventListener('click', submitGuidance);
document.getElementById('btn-skip-guidance').addEventListener('click', skipGuidance);

document.getElementById('guidance-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        submitGuidance();
    }
});

async function submitGuidance() {
    const input = document.getElementById('guidance-input');
    const guidance = input.value.trim() || '坚持己方立场，简短有力回应。';

    const body = { guidance };

    const result = await api('/game/guidance', {
        method: 'POST',
        body
    });

    if (result.success) {
        input.value = '';

        await syncHistoryFromServer();

        const { speaker_side, speech } = result.result;

        playSpeechSfx(speaker_side);

        // 显示发言
        showSpeech(speech, sideToStanceLabel(speaker_side));

        // 更新状态
        state.gameStatus = result.status;
        updateGameUI();

        // 检查游戏是否结束
        if (await checkGameOver()) return;

        // AI回合
        if (!state.gameStatus.is_player_turn) {
            setTimeout(doAITurn, 1500);
        }
    }
}

async function skipGuidance() {
    await submitGuidance();
}

async function doAITurn() {
    if (state.isTyping) {
        // 打字机动画期间延迟重试，避免AI推进被中断后卡住
        setTimeout(doAITurn, 600);
        return;
    }

    const result = await api('/game/ai_turn', {
        method: 'POST'
    });

    if (result.success) {
        await syncHistoryFromServer();

        const { speaker_side, speech } = result.result;

        playSpeechSfx(speaker_side);

        // 显示发言
        showSpeech(speech, sideToStanceLabel(speaker_side));

        // 更新状态
        state.gameStatus = result.status;
        updateGameUI();

        // 检查游戏是否结束
        if (await checkGameOver()) return;

        // 处理连续AI回合，直到轮到玩家
        if (!state.gameStatus.is_player_turn) {
            setTimeout(doAITurn, 1200);
        }
    }
}

function showSpeech(text, speaker) {
    const bubble = document.getElementById('speech-bubble');
    const content = document.getElementById('speech-content');

    content.textContent = '';
    bubble.classList.add('visible');

    // 打字机效果
    state.isTyping = true;
    let index = 0;
    const speed = 30; // 毫秒每字符

    function typeChar() {
        if (index < text.length) {
            content.textContent += text[index];
            index++;
            state.typingTimeout = setTimeout(typeChar, speed);
        } else {
            state.isTyping = false;
            // 3秒后隐藏
            setTimeout(() => {
                bubble.classList.remove('visible');
            }, 3000);
        }
    }

    typeChar();
}

async function checkGameOver() {
    const result = await api('/game/is_over');
    if (result.success && result.is_over) {
        await showGameOver();
        return true;
    }
    return false;
}

// ==================== 游戏结束 ====================
async function fetchJudgement() {
    const result = await api('/game/judgement');
    if (result.success) {
        state.judgeResult = result.judgement;
    }
}

function renderJudgement() {
    const winnerEl = document.getElementById('judge-winner');
    const summaryEl = document.getElementById('judge-summary');

    if (!state.judgeResult) {
        winnerEl.textContent = '裁判未给出结果';
        summaryEl.textContent = '请稍后重试。';
        return;
    }

    winnerEl.textContent = state.judgeResult.winner_label || '未判定';
    summaryEl.textContent = state.judgeResult.summary || '无裁决说明';
}

function renderJudgeClashHistory() {
    const historyEl = document.getElementById('judge-clash-history');
    historyEl.innerHTML = '';

    if (state.judgeClashHistory.length === 0) {
        historyEl.innerHTML = '<div class="judge-clash-line judge-msg">裁判：不服判决？你可以发起2轮对轰。</div>';
        return;
    }

    state.judgeClashHistory.forEach((item) => {
        const line = document.createElement('div');
        const roleClass = item.role === 'judge' ? 'judge-msg' : item.role;
        line.className = `judge-clash-line ${roleClass}`;
        line.textContent = `${item.role === 'player' ? '你' : '裁判'}：${item.text}`;
        historyEl.appendChild(line);
    });

    historyEl.scrollTop = historyEl.scrollHeight;
}

function setupJudgeClashPanel() {
    const card = document.getElementById('judge-clash-card');
    const btn = document.getElementById('btn-judge-clash');
    const input = document.getElementById('judge-clash-input');

    const playerLose = state.judgeResult?.winner === 'opponent';
    card.classList.toggle('hidden', !playerLose);

    if (!playerLose) {
        return;
    }

    renderJudgeClashHistory();
    const leftRounds = state.judgeClashMaxRounds - state.judgeClashRound;
    btn.textContent = leftRounds > 0 ? `和裁判对轰（剩余${leftRounds}轮）` : '对轰结束';
    btn.disabled = leftRounds <= 0 || state.judgeClashSubmitting;
    input.disabled = leftRounds <= 0 || state.judgeClashSubmitting;
    input.placeholder = leftRounds > 0
        ? `第${state.judgeClashRound + 1}轮：输入你的反击观点...`
        : '两轮对轰已结束';
}

async function submitJudgeClash() {
    const input = document.getElementById('judge-clash-input');
    const btn = document.getElementById('btn-judge-clash');
    const text = input.value.trim();
    if (!text) return;

    if (state.judgeClashRound >= state.judgeClashMaxRounds || state.judgeClashSubmitting) {
        return;
    }

    state.judgeClashSubmitting = true;
    btn.disabled = true;

    const nextRound = state.judgeClashRound + 1;
    const result = await api('/game/judge_clash', {
        method: 'POST',
        body: {
            message: text,
            round: nextRound
        }
    });

    if (!result.success) {
        alert(result.error || '对轰失败');
        state.judgeClashSubmitting = false;
        setupJudgeClashPanel();
        return;
    }

    state.judgeClashHistory.push({ role: 'player', text });
    state.judgeClashHistory.push({ role: 'judge', text: result.judge_reply || '裁判沉默了。' });
    state.judgeClashRound = nextRound;
    input.value = '';
    state.judgeClashSubmitting = false;

    setupJudgeClashPanel();
}

async function showGameOver() {
    await syncHistoryFromServer();
    await fetchJudgement();

    state.judgeClashRound = 0;
    state.judgeClashHistory = [];
    state.judgeClashSubmitting = false;

    document.getElementById('result-topic').textContent = state.gameStatus?.topic || '';
    document.getElementById('result-stance').textContent =
        state.gameStatus?.player_stance === 'A' ? '正方' : '反方';
    document.getElementById('result-rounds').textContent = state.history.length + ' 轮';

    renderJudgement();
    setupJudgeClashPanel();

    showPage('gameover-page');
}

async function forceDemoOpponentWin() {
    if (state.useLLM) {
        alert('仅演示模式支持此功能');
        return;
    }

    const result = await api('/game/demo/force_opponent_win', {
        method: 'POST'
    });

    if (!result.success) {
        alert(result.error || '跳转结局失败');
        return;
    }

    state.gameStatus = result.status || state.gameStatus;
    state.judgeResult = result.judgement || null;
    await showGameOver();
}

document.getElementById('btn-play-again').addEventListener('click', async () => {
    // 直接获取随机辩题并进入立场选择
    const result = await api('/topics/random');
    if (result.success && result.topic) {
        state.selectedTopic = result.topic;
        showStancePage();
    }
});

document.getElementById('btn-back-menu').addEventListener('click', () => {
    showPage('menu-page');
});

document.getElementById('btn-judge-clash').addEventListener('click', () => {
    submitJudgeClash().catch((err) => alert(err.message || '对轰失败'));
});

document.getElementById('btn-demo-end-lose').addEventListener('click', () => {
    forceDemoOpponentWin().catch((err) => alert(err.message || '跳转结局失败'));
});

document.getElementById('judge-clash-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        submitJudgeClash().catch((err) => alert(err.message || '对轰失败'));
    }
});

// ==================== Soul查看器 ====================
async function initSoulAgents() {
    const result = await api('/souls');
    if (result.success) {
        state.soulAgents = Object.values(result.souls);
        state.soulCurrentIndex = 0;
    }
}

function showSoulViewer() {
    if (state.soulAgents.length === 0) {
        initSoulAgents().then(showSoulViewerPage);
    } else {
        showSoulViewerPage();
    }
}

function showSoulViewerPage() {
    updateSoulViewer();
    showPage('soul-viewer-page');
}

function updateSoulViewer() {
    const agent = state.soulAgents[state.soulCurrentIndex];
    if (!agent) return;

    document.getElementById('soul-current').textContent = state.soulCurrentIndex + 1;
    document.getElementById('soul-total').textContent = state.soulAgents.length;
    document.getElementById('soul-name').textContent = agent.name;

    const badge = document.getElementById('soul-badge');
    badge.textContent = agent.editable ? '玩家' : 'AI';
    badge.className = `soul-badge ${agent.editable ? 'player' : 'opponent'}`;

    document.getElementById('soul-content').textContent = agent.content;
}

document.getElementById('btn-prev-soul').addEventListener('click', () => {
    state.soulCurrentIndex = (state.soulCurrentIndex - 1 + state.soulAgents.length) % state.soulAgents.length;
    updateSoulViewer();
});

document.getElementById('btn-next-soul').addEventListener('click', () => {
    state.soulCurrentIndex = (state.soulCurrentIndex + 1) % state.soulAgents.length;
    updateSoulViewer();
});

// ==================== 键盘控制 ====================
document.addEventListener('keydown', (e) => {
    // 立场选择页面
    if (state.currentPage === 'stance') {
        if (e.key === 'ArrowLeft' || e.key === '1') selectStance('A');
        if (e.key === 'ArrowRight' || e.key === '2') selectStance('B');
        if (e.key === 'Enter') startGame();
        if (e.key === 'Escape') showPage('menu-page');
    }

    // Soul查看器
    if (state.currentPage === 'soul-viewer') {
        if (e.key === 'ArrowLeft' || e.key === 'a' || e.key === 'A') {
            document.getElementById('btn-prev-soul').click();
        }
        if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
            document.getElementById('btn-next-soul').click();
        }
        if (e.key === 'Escape' || e.key === 'v' || e.key === 'V') {
            showPage('game-page');
        }
    }

    // 游戏页面
    if (state.currentPage === 'game') {
        if (e.key === 'v' || e.key === 'V') {
            showSoulViewer();
        }
    }
});

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', () => {
    // 浏览器通常需要用户手势后才允许播放音频
    document.addEventListener('pointerdown', unlockAudio, { once: true });
    document.addEventListener('touchstart', unlockAudio, { once: true });
    document.addEventListener('mousedown', unlockAudio, { once: true });
    document.addEventListener('keydown', unlockAudio, { once: true });

    // 任意按钮点击单次播放 button 音效
    document.addEventListener('click', (event) => {
        const button = event.target.closest('button');
        if (!button || button.disabled) return;
        unlockAudio();
        playSfx(audio.button);
    });

    showPage('menu-page');
});
