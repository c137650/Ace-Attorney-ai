"""
AI 辩论游戏 - Pygame 界面（对接后端版）

运行方式：
    pip install pygame
    cd ..\hackathon_game
    python main.py
"""

import pygame
import os
import sys
import json
import subprocess
import ctypes
from ctypes import wintypes

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# ==================== 配置 ====================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# 颜色配置
COLORS = {
    "background": (25, 25, 35),
    "player_side": (66, 133, 244),
    "opponent_side": (234, 67, 53),
    "judge": (251, 188, 5),
    "table": (139, 90, 43),
    "coach_seat": (100, 100, 120),
    "text": (255, 255, 255),
    "highlight": (255, 215, 0),
    "panel_bg": (40, 40, 55),
    "input_bg": (60, 60, 80),
}

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
BACKGROUND_PATH = os.path.join(ASSETS_DIR, "background.png")

# ==================== 布局配置 ====================

class LayoutConfig:
    """布局配置"""
    player_zone = {
        "coach_y": 80,
        "debater_y": 185,
        "table_y": 290,
        "table_height": 15,
    }
    opponent_zone = {
        "coach_y": 620,
        "debater_y": 450,
        "table_y": 360,
        "table_height": 15,
    }
    middle_zone = {"y": 340, "height": 80}
    judge_zone = {"x": 720, "y": 480, "width": 120, "height": 150}  # 移到辩论桌下方左侧
    seat = {"width": 80, "height": 100}
    table = {"player_width": 380, "opponent_width": 380, "height": 15}
    coach_seat = {"width": 150, "height": 85}
    debater_spacing = 110
    info_panel = {"x": 850, "y": 50, "width": 400, "height": 620}

    @staticmethod
    def get_debater_x_positions(center_x):
        spacing = LayoutConfig.debater_spacing
        return [center_x - spacing, center_x, center_x + spacing]

    @staticmethod
    def get_judge_pos():
        return (LayoutConfig.judge_zone["x"], LayoutConfig.judge_zone["y"],
                LayoutConfig.judge_zone["width"], LayoutConfig.judge_zone["height"])


# ==================== 游戏类 ====================

class Game:
    """游戏主类"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI 辩论赛")
        self.clock = pygame.time.Clock()

        self.fonts = self._load_chinese_fonts()
        self._init_game()

    def _load_chinese_fonts(self) -> dict:
        """加载中文字体"""
        font_paths = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/simkai.ttf",
        ]
        fonts = {}
        for path in font_paths:
            if os.path.exists(path):
                try:
                    fonts['small'] = pygame.font.Font(path, 18)
                    fonts['medium'] = pygame.font.Font(path, 22)
                    fonts['large'] = pygame.font.Font(path, 28)
                    return fonts
                except:
                    continue
        fonts['small'] = pygame.font.Font(None, 20)
        fonts['medium'] = pygame.font.Font(None, 24)
        fonts['large'] = pygame.font.Font(None, 30)
        return fonts

    def _init_game(self):
        """初始化游戏对象"""
        self.background = None
        self.load_background()
        self.debate_game = None
        self.load_backend()

        self.debater_rects = {"player": [None, None, None], "opponent": [None, None, None]}
        self.typing_text = ""
        self.typing_index = 0
        self.typing_speed = 5
        self.is_typing = False
        self.player_input = ""
        self.input_active = False
        self.input_rect = pygame.Rect(865, 505, 360, 45)
        self.running = True
        self.waiting_ai = False
        self._ime_text = ""  # IME正在编辑的拼音
        # 仅在Windows默认启用Tk覆盖输入；失败时会自动降级到Pygame输入
        self.tk_overlay_enabled = (sys.platform == "win32")

        # Soul查看器状态
        self.soul_viewer = False  # 是否显示Soul查看器
        self.soul_current_index = 0  # 当前查看的AI索引
        self._v_pressed = False  # V键按下状态
        # 所有AI列表（己方3个 + 对方3个 + 己方教练 + 对方教练）
        self.soul_agents = [
            {"id": "player_debater_1", "name": "正方一辩「张明」", "side": "player"},
            {"id": "player_debater_2", "name": "正方二辩「李华」", "side": "player"},
            {"id": "player_debater_3", "name": "正方三辩「王强」", "side": "player"},
            {"id": "opponent_debater_1", "name": "反方一辩「陈思」", "side": "opponent"},
            {"id": "opponent_debater_2", "name": "反方二辩「赵敏」", "side": "opponent"},
            {"id": "opponent_debater_3", "name": "反方三辩「刘洋」", "side": "opponent"},
            {"id": "player_coach", "name": "正方教练「陈指导」", "side": "player"},
            {"id": "opponent_coach", "name": "反方教练「王指导」", "side": "opponent"},
        ]

    def load_background(self):
        if os.path.exists(BACKGROUND_PATH):
            self.background = pygame.image.load(BACKGROUND_PATH)
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def load_backend(self, use_llm: bool = False, topic_dict: dict = None, player_stance: str = None):
        try:
            from game_integration import DebateGame
            from topic_loader import create_topic_from_dict

            # 如果提供了辩题字典，转换为Topic对象
            topic = None
            if topic_dict:
                topic = create_topic_from_dict(topic_dict)

            # use_simple_agents=False时use_llm才生效
            self.debate_game = DebateGame(
                topic=topic,
                use_simple_agents=not use_llm,
                use_llm=use_llm,
                player_stance=player_stance
            )
            stance = "正方" if self.debate_game.player_stance == "A" else "反方"
            if use_llm:
                print(f"✓ 加载后端成功 (LLM模式): {self.debate_game.topic.title} [{stance}]")
            else:
                print(f"✓ 加载后端成功 (演示模式): {self.debate_game.topic.title} [{stance}]")
        except Exception as e:
            print(f"✗ 加载后端失败: {e}")
            self.debate_game = None

    def _get_window_screen_position(self):
        """获取Pygame客户区左上角屏幕坐标。"""
        if sys.platform != "win32":
            return None
        try:
            wm_info = pygame.display.get_wm_info()
            hwnd = wm_info.get("window")
            if not hwnd:
                return None

            point = wintypes.POINT(0, 0)
            ok = ctypes.windll.user32.ClientToScreen(int(hwnd), ctypes.byref(point))
            if not ok:
                return None
            return point.x, point.y
        except Exception:
            return None

    def _start_pygame_text_input(self):
        """启用Pygame原生输入作为跨平台兜底。"""
        self.input_active = True
        pygame.key.start_text_input()
        pygame.key.set_text_input_rect(self.input_rect)

    def _open_input_editor(self):
        """优先使用Tk覆盖输入，失败时自动回退到Pygame输入。"""
        if not self.tk_overlay_enabled:
            self._start_pygame_text_input()
            return

        pygame.key.stop_text_input()
        window_pos = self._get_window_screen_position()
        if window_pos is not None:
            win_x, win_y = window_pos
            dialog_x = win_x + self.input_rect.x
            dialog_y = win_y + self.input_rect.y
        else:
            dialog_x = self.input_rect.x
            dialog_y = self.input_rect.y

        dialog_text = self.open_tk_input_dialog(
            screen_x=dialog_x,
            screen_y=dialog_y,
            width=self.input_rect.width,
            height=self.input_rect.height,
        )

        if dialog_text is not None:
            self.player_input = dialog_text
            self._ime_text = ""
            self.input_active = False
            return

        # Tk启动失败或用户取消：降级到Pygame输入，避免无法输入
        print("Tk输入不可用，已切换为Pygame原生输入")
        self.tk_overlay_enabled = False
        self._start_pygame_text_input()

    def open_tk_input_dialog(self, screen_x: int, screen_y: int, width: int, height: int):
        """打开附着在input_area上的无边框Tk输入框，Enter提交。"""
        dialog_script = (
            "import json,sys,tkinter as tk\n"
            "root=tk.Tk()\n"
            "x=int(sys.argv[1]); y=int(sys.argv[2]); w=int(sys.argv[3]); h=int(sys.argv[4])\n"
            "initial = sys.argv[5] if len(sys.argv) > 5 else ''\n"
            "root.overrideredirect(True)\n"
            "root.attributes('-topmost', True)\n"
            "root.geometry(f'{w}x{h}+{x}+{y}')\n"
            "root.configure(bg='#1f2330')\n"
            "entry_var = tk.StringVar(value=initial)\n"
            "entry = tk.Entry(root, textvariable=entry_var, bd=0, highlightthickness=0, font=('Microsoft YaHei UI', 11), insertbackground='#ffffff', fg='#ffffff', bg='#2f3444')\n"
            "entry.place(x=6, y=6, width=max(10, w-12), height=max(10, h-12))\n"
            "def submit(_event=None):\n"
            "    print(json.dumps({'text': entry_var.get()}, ensure_ascii=False), flush=True)\n"
            "    root.destroy()\n"
            "def cancel(_event=None):\n"
            "    print(json.dumps({'text': None}, ensure_ascii=False), flush=True)\n"
            "    root.destroy()\n"
            "entry.bind('<Return>', submit)\n"
            "entry.bind('<Escape>', cancel)\n"
            "root.bind('<FocusOut>', cancel)\n"
            "entry.focus_force()\n"
            "root.mainloop()\n"
        )

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    dialog_script,
                    str(screen_x),
                    str(screen_y),
                    str(width),
                    str(height),
                    self.player_input,
                ],
                capture_output=True,
                text=False,
                timeout=300,
            )

            def _safe_decode(raw):
                if raw is None:
                    return ""
                if isinstance(raw, str):
                    return raw
                try:
                    return raw.decode("utf-8")
                except UnicodeDecodeError:
                    return raw.decode("gbk", errors="replace")

            stdout_text = _safe_decode(result.stdout)
            stderr_text = _safe_decode(result.stderr)

            if result.returncode != 0:
                err = stderr_text.strip() if stderr_text else "未知错误"
                print(f"Tk输入框启动失败: {err}")
                return None

            output = stdout_text.strip().splitlines()
            if not output:
                return None

            payload = json.loads(output[-1])
            return payload.get("text")
        except subprocess.TimeoutExpired:
            print("Tk输入框超时关闭")
            return None
        except Exception as e:
            print(f"Tk输入框异常: {e}")
            return None

    def handle_events(self):
        # 先处理KEYDOWN事件中的V键（在Soul查看器中先处理ESC和V）
        v_key_handled = False
        esc_key_handled = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            # Soul查看器模式
            if self.soul_viewer:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE and not esc_key_handled:
                        esc_key_handled = True
                        self.soul_viewer = False
                        pygame.key.stop_text_input()
                    elif event.key == pygame.K_v and not v_key_handled:
                        v_key_handled = True
                        self.soul_viewer = False
                        pygame.key.stop_text_input()
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.soul_current_index = (self.soul_current_index - 1) % len(self.soul_agents)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.soul_current_index = (self.soul_current_index + 1) % len(self.soul_agents)
                continue

            # 游戏模式
            if event.type == pygame.KEYDOWN:
                # ESC和V键优先处理
                if event.key == pygame.K_ESCAPE and not esc_key_handled:
                    esc_key_handled = True
                    self.running = False
                elif event.key == pygame.K_v and not v_key_handled:
                    v_key_handled = True
                    self.soul_viewer = True
                    self.input_active = False
                    pygame.key.stop_text_input()
                elif event.key == pygame.K_TAB:
                    self.input_active = not self.input_active
                    if self.input_active:
                        pygame.key.start_text_input()
                    else:
                        pygame.key.stop_text_input()
                elif event.key == pygame.K_RETURN:
                    if self.input_active:
                        self.submit_player_input()
                elif event.key == pygame.K_BACKSPACE:
                    if self.input_active and self.player_input:
                        self.player_input = self.player_input[:-1]
                elif event.key == pygame.K_SPACE:
                    if not self.input_active:
                        self.submit_player_input()
                    elif self.player_input:
                        self.player_input += " "
            elif event.type == pygame.TEXTINPUT:
                if self.input_active:
                    self.player_input += event.text
                    self._ime_text = ""
            elif event.type == pygame.TEXTEDITING:
                if self.input_active:
                    self._ime_text = event.text
                else:
                    self._ime_text = ""
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.input_rect.collidepoint(event.pos):
                    self._open_input_editor()
                else:
                    if self.input_active:
                        pygame.key.stop_text_input()
                    self.input_active = False

    def submit_player_input(self):
        if self.debate_game is None:
            return
        if self.debate_game.is_player_turn():
            guidance = self.player_input.strip() if self.player_input.strip() else "坚持己方立场，简短有力回应。"
            try:
                result = self.debate_game.process_player_guidance(guidance)
                self.display_speech(result["speech"])
                self.player_input = ""
                self.input_active = False
                self.waiting_ai = not self.debate_game.is_player_turn()
            except Exception as e:
                print(f"处理失败: {e}")

    def display_speech(self, speech: str):
        self.typing_text = speech
        self.typing_index = 0
        self.is_typing = True

    def update(self):
        if self.debate_game is None:
            return
        if self.is_typing and self.typing_index < len(self.typing_text):
            self.typing_index += self.typing_speed
            if self.typing_index >= len(self.typing_text):
                self.typing_index = len(self.typing_text)
                self.is_typing = False
        if self.waiting_ai and not self.is_typing:
            try:
                result = self.debate_game.advance_turn()
                self.display_speech(result["speech"])
                self.waiting_ai = False
            except Exception as e:
                print(f"AI失败: {e}")
                self.waiting_ai = False
        if not self.waiting_ai and not self.is_typing:
            self.waiting_ai = not self.debate_game.is_player_turn()

    def draw(self):
        if self.soul_viewer:
            # 绘制Soul查看器
            self.draw_soul_viewer()
        else:
            # 绘制游戏界面
            if self.background:
                self.screen.blit(self.background, (0, 0))
            else:
                self.screen.fill(COLORS["background"])
            self.draw_tables()
            self.draw_debaters()
            self.draw_coach_seats()
            self.draw_judge()
            self.draw_info_panel()
            self.draw_input_area()
            self.draw_current_speech()
            # 绘制提示
            self.draw_viewer_hint()

    def draw_viewer_hint(self):
        """绘制Soul查看器提示"""
        hint = self.fonts['small'].render("按 V 查看AI灵魂", True, (100, 100, 100))
        self.screen.blit(hint, (50, 10))

    def draw_tables(self):
        center_x = 400
        table_x = center_x - LayoutConfig.table["player_width"] // 2
        rect = pygame.Rect(table_x, LayoutConfig.layout["player_zone"]["table_y"],
                           LayoutConfig.table["player_width"], LayoutConfig.layout["player_zone"]["table_height"])
        pygame.draw.rect(self.screen, COLORS["table"], rect, border_radius=5)
        table_x = center_x - LayoutConfig.table["opponent_width"] // 2
        rect = pygame.Rect(table_x, LayoutConfig.layout["opponent_zone"]["table_y"],
                           LayoutConfig.table["opponent_width"], LayoutConfig.layout["opponent_zone"]["table_height"])
        pygame.draw.rect(self.screen, COLORS["table"], rect, border_radius=5)

    def draw_debaters(self):
        center_x = 400
        x_positions = LayoutConfig.get_debater_x_positions(center_x)
        for i in range(3):
            y = LayoutConfig.layout["player_zone"]["debater_y"]
            rect = pygame.Rect(x_positions[i] - LayoutConfig.seat["width"] // 2, y,
                              LayoutConfig.seat["width"], LayoutConfig.seat["height"])
            self.debater_rects["player"][i] = rect
            is_speaking = self.debate_game and self.debate_game.speaker_states["player"][i]
            if is_speaking:
                glow_rect = rect.inflate(15, 15)
                pygame.draw.rect(self.screen, COLORS["highlight"], glow_rect, 3, border_radius=12)
            pygame.draw.rect(self.screen, COLORS["player_side"], rect, border_radius=10)
            text = self.fonts['medium'].render(["一辩", "二辩", "三辩"][i], True, COLORS["text"])
            self.screen.blit(text, text.get_rect(center=rect.center))
        for i in range(3):
            y = LayoutConfig.layout["opponent_zone"]["debater_y"]
            rect = pygame.Rect(x_positions[i] - LayoutConfig.seat["width"] // 2, y,
                              LayoutConfig.seat["width"], LayoutConfig.seat["height"])
            self.debater_rects["opponent"][i] = rect
            is_speaking = self.debate_game and self.debate_game.speaker_states["opponent"][i]
            if is_speaking:
                glow_rect = rect.inflate(15, 15)
                pygame.draw.rect(self.screen, COLORS["highlight"], glow_rect, 3, border_radius=12)
            pygame.draw.rect(self.screen, COLORS["opponent_side"], rect, border_radius=10)
            text = self.fonts['medium'].render(["一辩", "二辩", "三辩"][i], True, COLORS["text"])
            self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_coach_seats(self):
        center_x = 400
        coach_width = LayoutConfig.coach_seat["width"]
        coach_height = LayoutConfig.coach_seat["height"]
        for y, label in [(LayoutConfig.layout["player_zone"]["coach_y"], "教练"),
                         (LayoutConfig.layout["opponent_zone"]["coach_y"], "AI教练")]:
            rect = pygame.Rect(center_x - coach_width // 2, y, coach_width, coach_height)
            pygame.draw.rect(self.screen, COLORS["coach_seat"], rect, border_radius=10)
            text = self.fonts['large'].render(label, True, COLORS["text"])
            self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_judge(self):
        jx, jy, jw, jh = LayoutConfig.get_judge_pos()
        rect = pygame.Rect(jx, jy, jw, jh)
        pygame.draw.rect(self.screen, COLORS["judge"], rect, border_radius=12)
        text = self.fonts['medium'].render("裁判", True, (50, 40, 0))
        self.screen.blit(text, text.get_rect(center=(jx + jw//2, jy + jh//2 - 20)))
        sub = self.fonts['small'].render("评审席", True, (80, 70, 50))
        self.screen.blit(sub, sub.get_rect(center=(jx + jw//2, jy + jh//2 + 15)))

    def draw_info_panel(self):
        if self.debate_game is None:
            return
        px, py, pw, ph = LayoutConfig.info_panel["x"], LayoutConfig.info_panel["y"], \
                         LayoutConfig.info_panel["width"], LayoutConfig.info_panel["height"]
        pygame.draw.rect(self.screen, COLORS["panel_bg"], pygame.Rect(px, py, pw, ph), border_radius=10)

        # 辩题
        self.screen.blit(self.fonts['medium'].render("辩题", True, COLORS["highlight"]), (px + 15, py + 15))
        self.screen.blit(self.fonts['small'].render(self.debate_game.topic.title, True, COLORS["text"]), (px + 15, py + 40))

        # 立场
        stance = "正方" if self.debate_game.player_stance == "A" else "反方"
        self.screen.blit(self.fonts['medium'].render(f"你的立场: {stance}", True, COLORS["player_side"]), (px + 15, py + 85))

        # 当前环节
        self.screen.blit(self.fonts['medium'].render("当前环节", True, COLORS["highlight"]), (px + 15, py + 130))
        self.screen.blit(self.fonts['small'].render(self.debate_game.get_phase_name(), True, COLORS["text"]), (px + 15, py + 155))

        # 当前发言者
        self.screen.blit(self.fonts['medium'].render("当前发言", True, COLORS["highlight"]), (px + 15, py + 200))
        info = self.debate_game.phase_info
        color = COLORS["player_side"] if info["is_player_turn"] else COLORS["opponent_side"]
        self.screen.blit(self.fonts['small'].render(info["current_speaker_name"], True, color), (px + 15, py + 225))

        # 提示
        tip = ">>> 等待你的指导 <<<" if info["is_player_turn"] else ">>> AI正在发言 <<<"
        tip_color = COLORS["highlight"] if info["is_player_turn"] else (150, 150, 150)
        self.screen.blit(self.fonts['small'].render(tip, True, tip_color), (px + 15, py + 260))

        # 发言历史
        self.screen.blit(self.fonts['medium'].render("发言历史", True, COLORS["highlight"]), (px + 15, py + 310))
        history = self.debate_game.speech_history[-3:] if self.debate_game.speech_history else []
        for i, (side, idx, content) in enumerate(history):
            y = py + 340 + i * 40
            if y > py + ph - 60:
                break
            mark = "P" if side == "player" else "O"
            name = ["一", "二", "三"][idx]
            text = f"[{mark}{name}] {content[:25]}..."
            color = COLORS["player_side"] if side == "player" else COLORS["opponent_side"]
            self.screen.blit(self.fonts['small'].render(text, True, color), (px + 15, y))

    def draw_input_area(self):
        if self.debate_game is None or not self.debate_game.is_player_turn():
            return
        px = LayoutConfig.info_panel["x"]
        input_y = 505

        self.screen.blit(self.fonts['medium'].render("教练指导:", True, COLORS["highlight"]), (px + 15, 480))

        # 更新输入框位置
        input_rect = pygame.Rect(px + 15, input_y, 360, 45)
        pygame.draw.rect(self.screen, (50, 50, 70), input_rect, border_radius=8)
        border_color = (100, 130, 180) if not self.input_active else (150, 180, 230)
        pygame.draw.rect(self.screen, border_color, input_rect, 2, border_radius=8)

        import time

        if self._ime_text:
            # 显示正在输入的拼音
            pygame.draw.rect(self.screen, (30, 30, 50), (input_rect.x + 5, input_rect.y + 5, 350, 35), border_radius=5)
            self.screen.blit(self.fonts['medium'].render(self._ime_text, True, (255, 220, 100)),
                           (input_rect.x + 10, input_rect.y + 10))
            # 光标闪烁
            if int(time.time() * 2) % 2 == 0:
                x = input_rect.x + 10 + self.fonts['medium'].size(self._ime_text)[0] + 5
                pygame.draw.rect(self.screen, (255, 220, 100), (x, input_rect.y + 10, 2, 24))
        elif self.player_input:
            self.screen.blit(self.fonts['small'].render(self.player_input, True, COLORS["text"]),
                           (input_rect.x + 10, input_rect.y + 12))
            # 光标闪烁
            if self.input_active and int(time.time() * 2) % 2 == 0:
                x = input_rect.x + 10 + self.fonts['small'].size(self.player_input)[0] + 5
                pygame.draw.rect(self.screen, COLORS["text"], (x, input_rect.y + 8, 2, 25))
        else:
            if self.input_active:
                # 输入模式但无内容 - 显示闪烁光标
                self.screen.blit(self.fonts['small'].render("", True, COLORS["text"]),
                               (input_rect.x + 10, input_rect.y + 12))
                if int(time.time() * 2) % 2 == 0:
                    pygame.draw.rect(self.screen, COLORS["text"], (input_rect.x + 10, input_rect.y + 8, 2, 25))
            else:
                self.screen.blit(self.fonts['small'].render("点击此处输入，或按空格", True, (100, 100, 100)),
                               (input_rect.x + 10, input_rect.y + 12))

    def draw_current_speech(self):
        if not self.typing_text:
            return
        speech = self.typing_text[:self.typing_index]
        speech_bg = pygame.Surface((SCREEN_WIDTH - 50, 80), pygame.SRCALPHA)
        speech_bg.fill((0, 0, 0, 180))
        self.screen.blit(speech_bg, (25, SCREEN_HEIGHT - 100))

        lines = []
        current_line = ""
        max_width = SCREEN_WIDTH - 100
        for char in speech:
            test_line = current_line + char
            if self.fonts['medium'].size(test_line)[0] > max_width:
                lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
        for i, line in enumerate(lines[:3]):
            self.screen.blit(self.fonts['medium'].render(line, True, COLORS["text"]),
                           (40, SCREEN_HEIGHT - 90 + i * 25))

    def draw_soul_viewer(self):
        """绘制Soul查看器（只读）"""
        # 背景
        self.screen.fill((20, 25, 35))

        # 标题
        title = self.fonts['large'].render("AI灵魂查看器", True, (255, 255, 255))
        self.screen.blit(title, (50, 30))

        # 返回提示
        back_hint = self.fonts['small'].render("按 ESC 或 V 返回游戏", True, (100, 100, 100))
        self.screen.blit(back_hint, (1050, 35))

        # 获取当前AI信息
        agent = self.soul_agents[self.soul_current_index]

        # 获取Soul内容
        soul_content = ""
        try:
            from soul_manager import get_soul_manager
            manager = get_soul_manager()
            soul_content = manager.get_soul(agent["id"])
        except Exception as e:
            soul_content = f"加载失败: {e}"

        # AI名称和位置
        name_y = 80
        name_text = agent["name"]
        if "coach" in agent["id"]:
            name_text += "（教练）"

        name_color = COLORS["player_side"] if agent["side"] == "player" else COLORS["opponent_side"]
        name = self.fonts['medium'].render(name_text, True, name_color)
        self.screen.blit(name, (50, name_y))

        # 左右切换提示
        nav_text = f"← {self.soul_current_index + 1}/{len(self.soul_agents)} →"
        nav_hint = self.fonts['small'].render(nav_text, True, (150, 150, 170))
        self.screen.blit(nav_hint, (50, name_y + 35))

        # 切换按钮区域（不可点击，仅显示）
        btn_y = 80
        if self.soul_current_index > 0:
            left_hint = self.fonts['small'].render("◀ 左翻", True, (100, 120, 160))
            self.screen.blit(left_hint, (200, btn_y))
        if self.soul_current_index < len(self.soul_agents) - 1:
            right_hint = self.fonts['small'].render("右翻 ▶", True, (100, 120, 160))
            self.screen.blit(right_hint, (270, btn_y))

        # 文本框背景
        box_rect = pygame.Rect(50, 140, SCREEN_WIDTH - 100, 520)
        pygame.draw.rect(self.screen, (30, 35, 50), box_rect, border_radius=10)
        pygame.draw.rect(self.screen, (80, 90, 110), box_rect, 2, border_radius=10)

        # 绘制Soul内容
        lines = soul_content.split('\n')
        line_y = 160
        line_height = 26
        max_lines = 18

        for i, line in enumerate(lines[:max_lines]):
            text_color = (200, 205, 220)
            # 标题行高亮
            if line.startswith('#'):
                text_color = (66, 133, 244)
                line_text = line.replace('#', '').strip()
            elif line.startswith('##'):
                text_color = (100, 180, 100)
                line_text = line.replace('##', '').strip()
            elif line.startswith('- **') or line.startswith('-'):
                line_text = line
            else:
                line_text = line

            text = self.fonts['small'].render(line_text, True, text_color)
            self.screen.blit(text, (70, line_y))
            line_y += line_height

        # 只读提示
        readonly_hint = self.fonts['small'].render("（只读模式 - 仅供查看）", True, (80, 85, 100))
        self.screen.blit(readonly_hint, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 55))

        # 底部操作提示
        bottom_hints = [
            "← / A: 上一页",
            "→ / D: 下一页",
            "V / ESC: 返回",
        ]
        hint_y = SCREEN_HEIGHT - 30
        for i, hint in enumerate(bottom_hints):
            text = self.fonts['small'].render(hint, True, (100, 105, 120))
            self.screen.blit(text, (50 + i * 200, hint_y))

    def run(self):
        print("AI 辩论游戏启动...")
        while self.running:
            self.handle_events()
            # Soul查看器中不更新游戏逻辑
            if not self.soul_viewer:
                self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()


# 修正布局引用
LayoutConfig.layout = {
    "player_zone": LayoutConfig.player_zone,
    "opponent_zone": LayoutConfig.opponent_zone,
    "middle_zone": LayoutConfig.middle_zone,
}


# ==================== 入口 ====================

if __name__ == "__main__":
    import menu as menu_module

    while True:
        menu = menu_module.Menu()
        choice = menu.run()
        use_llm = menu.use_llm

        if choice == "start" or choice == "soul_edit":
            # 先打开Soul编辑器
            if choice == "soul_edit":
                print(">>> 打开Soul编辑器...")
                import soul_editor
                editor = soul_editor.SoulEditor()
                editor_result = editor.run()
                if editor_result != "start":
                    continue  # 返回菜单

            # 选择立场（辩题随机抽取）
            print(">>> 打开立场选择...")
            import topic_select
            selector = topic_select.StanceSelect()
            result = selector.run()

            if result is None:
                continue  # 返回菜单

            selected_topic = result["topic"]
            player_stance = result["player_stance"]

            stance_name = "正方" if player_stance == "A" else "反方"
            print(f">>> 辩题: {selected_topic['title']} | 玩家选择: {stance_name} (LLM={'启用' if use_llm else '禁用'})")

            game = Game()
            game.load_backend(use_llm=use_llm, topic_dict=selected_topic, player_stance=player_stance)
            if game.debate_game:
                game.run()
        else:
            print("退出游戏...")
            break
