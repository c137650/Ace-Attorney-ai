"""
Soul编辑页面
玩家可以在游戏开始前编辑己方辩手的Soul
"""

import pygame
import os
import sys

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# 中文字体加载
def load_font(size=24):
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/STKAITI.TTF",
    ]
    for path in font_paths:
        if os.path.exists(path):
            return pygame.font.Font(path, size)
    return pygame.font.SysFont("microsoftyahei", size)

# 辩手配置
DEBATERS = [
    {"id": "player_debater_1", "name": "正方一辩", "title": "张明", "position": "一辩（开篇立论）"},
    {"id": "player_debater_2", "name": "正方二辩", "title": "李华", "position": "二辩（驳论）"},
    {"id": "player_debater_3", "name": "正方三辩", "title": "王强", "position": "三辩（质询/自由辩/总结）"},
]

# 默认Soul模板
DEFAULT_SOULS = {
    "player_debater_1": """# 正方一辩 - 灵魂配置

## 基础信息
- **名字**: 张明
- **学校**: XX大学
- **辩位**: 一辩（开篇立论）

## 性格特征
- 逻辑严谨
- 表达清晰
- 稳重沉着
- 善于归纳总结

## 说话风格
- 开场气势足
- 论点清晰有条理
- 常用"我方认为"、"综上所述"
- 语言正式但不刻板

## 专长
- 开篇立论
- 概念定义
- 框架建构

## 系统提示词
你扮演正方一辩张明，XX大学辩论队成员。你擅长开篇立论，逻辑严密，表达清晰。你的发言风格稳重沉着，善于归纳总结。""",

    "player_debater_2": """# 正方二辩 - 灵魂配置

## 基础信息
- **名字**: 李华
- **学校**: XX大学
- **辩位**: 二辩（驳论）

## 性格特征
- 反应敏捷
- 攻击性强
- 善于抓漏洞
- 逻辑思维能力强

## 说话风格
- 反驳犀利
- 追问直接
- 常用"对方辩友"、"请对方注意"
- 善于抓住对方逻辑漏洞

## 专长
- 驳论
- 逻辑攻击
- 数据反驳

## 系统提示词
你扮演正方二辩李华，XX大学辩论队成员。你擅长驳论，反应敏捷，攻击性强，善于抓住对方论点中的漏洞进行反驳。""",

    "player_debater_3": """# 正方三辩 - 灵魂配置

## 基础信息
- **名字**: 王强
- **学校**: XX大学
- **辩位**: 三辩（质询、自由辩、总结）

## 性格特征
- 临场应变能力强
- 攻击犀利
- 善于临场发挥
- 气场强大

## 说话风格
- 质询尖锐
- 自由辩灵活
- 总结有力
- 常用"请问对方"、"我方再问"
- 善于打乱对方节奏

## 专长
- 质询
- 自由辩论
- 总结陈词
- 临场反应

## 系统提示词
你扮演正方三辩王强，XX大学辩论队成员。你擅长质询和自由辩论，临场应变能力强，攻击犀利，气场强大。""",
}


class SoulEditor:
    """Soul编辑器"""

    # 布局常量
    MARGIN_LEFT = 40
    MARGIN_RIGHT = 40
    CONTENT_WIDTH = 1200

    # Y轴布局
    Y_TITLE = 30
    Y_HINT = 70
    Y_TAB = 105
    Y_CURRENT_INFO = 150
    Y_TEXTBOX = 185
    Y_TEXTBOX_BOTTOM = 635
    Y_BUTTONS = 655

    def __init__(self, screen_width=1280, screen_height=720):
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("AI辩论赛 - Soul编辑")
        self.clock = pygame.time.Clock()

        self.width = screen_width
        self.height = screen_height

        # 字体
        self.font_large = load_font(36)
        self.font_medium = load_font(24)
        self.font_small = load_font(20)
        self.font_hint = load_font(16)

        # 颜色
        self.bg_color = (20, 25, 35)
        self.panel_color = (30, 35, 50)
        self.text_color = (220, 225, 235)
        self.accent_color = (66, 133, 244)
        self.warning_color = (234, 67, 53)
        self.success_color = (52, 168, 83)
        self.input_bg = (40, 45, 60)
        self.input_border = (80, 90, 110)
        self.input_focus = (66, 133, 244)
        self.hint_color = (120, 125, 140)

        # 状态
        self.current_debater = 0
        self.contents = {d["id"]: DEFAULT_SOULS[d["id"]] for d in DEBATERS}
        self.load_from_files()

        # 文本框
        textbox_height = self.Y_TEXTBOX_BOTTOM - self.Y_TEXTBOX
        self.text_box_rect = pygame.Rect(self.MARGIN_LEFT, self.Y_TEXTBOX,
                                        self.CONTENT_WIDTH, textbox_height)
        self.input_active = True
        self.scroll_offset = 0
        self.max_scroll = 0

        # 按钮
        self.buttons = self._create_buttons()
        self._update_text_surface()

        # 初始化IME
        pygame.key.start_text_input()
        self.ime_rect = pygame.Rect(self.MARGIN_LEFT, self.height - 50,
                                   self.CONTENT_WIDTH, 40)

    def _create_buttons(self):
        """创建按钮"""
        buttons = []

        # 辩手切换标签
        tab_width = 350
        tab_gap = 30
        start_x = self.MARGIN_LEFT
        for i, debater in enumerate(DEBATERS):
            x = start_x + i * (tab_width + tab_gap)
            buttons.append({
                "rect": pygame.Rect(x, self.Y_TAB, tab_width, 38),
                "text": debater["name"],
                "action": "tab",
                "index": i
            })

        # 底部按钮
        btn_y = self.Y_BUTTONS
        btn_width = 140
        btn_height = 40

        buttons.append({
            "rect": pygame.Rect(self.MARGIN_LEFT, btn_y, btn_width, btn_height),
            "text": "重置模板",
            "action": "reset"
        })
        buttons.append({
            "rect": pygame.Rect(self.MARGIN_LEFT + 160, btn_y, btn_width, btn_height),
            "text": "保存修改",
            "action": "save"
        })
        buttons.append({
            "rect": pygame.Rect(self.width - self.MARGIN_LEFT - btn_width, btn_y, btn_width, btn_height),
            "text": "← 返回",
            "action": "back"
        })
        buttons.append({
            "rect": pygame.Rect(self.width - self.MARGIN_LEFT - btn_width - 160, btn_y, 150, btn_height),
            "text": "开始游戏 →",
            "action": "start",
            "highlight": True
        })

        return buttons

    def load_from_files(self):
        """从文件加载Soul"""
        try:
            for debater in DEBATERS:
                file_path = os.path.join(
                    os.path.dirname(__file__), '..', 'backend', 'souls',
                    f"{debater['id']}.md"
                )
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self.contents[debater["id"]] = f.read()
        except Exception as e:
            print(f"加载Soul失败: {e}")

    def save_to_files(self):
        """保存Soul到文件"""
        try:
            for debater in DEBATERS:
                file_path = os.path.join(
                    os.path.dirname(__file__), '..', 'backend', 'souls',
                    f"{debater['id']}.md"
                )
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.contents[debater["id"]])
            return True
        except Exception as e:
            print(f"保存Soul失败: {e}")
            return False

    def _update_text_surface(self):
        """更新文本表面"""
        current_id = DEBATERS[self.current_debater]["id"]
        content = self.contents[current_id]

        # 渲染文本
        lines = content.split('\n')
        self.text_lines = []
        for line in lines:
            text_surface = self.font_small.render(line, True, self.text_color)
            self.text_lines.append({
                "surface": text_surface,
                "text": line
            })

        # 计算最大滚动
        line_height = 28
        total_height = len(self.text_lines) * line_height
        available_height = self.Y_TEXTBOX_BOTTOM - self.Y_TEXTBOX - 20
        self.max_scroll = max(0, total_height - available_height)

    def run(self):
        """运行编辑器"""
        running = True
        cursor_timer = 0
        show_cursor = True
        message = None
        message_timer = 0

        while running:
            cursor_timer += self.clock.get_time()
            if cursor_timer > 500:
                cursor_timer = 0
                show_cursor = not show_cursor

            # 消息倒计时
            if message:
                message_timer += self.clock.get_time()
                if message_timer > 2000:
                    message = None
                    message_timer = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    # 检查按钮点击
                    for btn in self.buttons:
                        if btn["rect"].collidepoint(mx, my):
                            if btn["action"] == "tab":
                                self.current_debater = btn["index"]
                                self._update_text_surface()
                            elif btn["action"] == "reset":
                                debater_id = DEBATERS[self.current_debater]["id"]
                                self.contents[debater_id] = DEFAULT_SOULS[debater_id]
                                self._update_text_surface()
                            elif btn["action"] == "save":
                                if self.save_to_files():
                                    message = ("✓ 保存成功!", self.success_color)
                                else:
                                    message = ("✗ 保存失败!", self.warning_color)
                            elif btn["action"] == "back":
                                return "menu"
                            elif btn["action"] == "start":
                                self.save_to_files()
                                return "start"
                            break

                    # 检查文本框点击
                    if self.text_box_rect.collidepoint(mx, my):
                        self.input_active = True
                        pygame.key.start_text_input()
                        pygame.key.set_text_input_rect(self.ime_rect)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 4:  # 滚轮上
                        self.scroll_offset = max(0, self.scroll_offset - 50)
                    elif event.button == 5:  # 滚轮下
                        self.scroll_offset = min(self.max_scroll, self.scroll_offset + 50)

                elif event.type == pygame.TEXTINPUT:
                    if self.input_active:
                        debater_id = DEBATERS[self.current_debater]["id"]
                        self.contents[debater_id] += event.text
                        self._update_text_surface()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"
                    elif event.key == pygame.K_RETURN and pygame.key.get_mods() & pygame.KMOD_LCTRL:
                        if self.save_to_files():
                            message = ("✓ 保存成功!", self.success_color)
                    elif event.key == pygame.K_UP:
                        self.scroll_offset = max(0, self.scroll_offset - 50)
                    elif event.key == pygame.K_DOWN:
                        self.scroll_offset = min(self.max_scroll, self.scroll_offset + 50)
                    elif event.key == pygame.K_TAB:
                        self.current_debater = (self.current_debater + 1) % len(DEBATERS)
                        self._update_text_surface()
                    elif event.key == pygame.K_BACKSPACE and self.input_active:
                        debater_id = DEBATERS[self.current_debater]["id"]
                        if self.contents[debater_id]:
                            self.contents[debater_id] = self.contents[debater_id][:-1]
                            self._update_text_surface()

            # 绘制
            self._draw(show_cursor, message)
            pygame.display.flip()
            self.clock.tick(60)

        return "quit"

    def _draw(self, show_cursor, message=None):
        """绘制界面"""
        self.screen.fill(self.bg_color)

        # 标题
        title = self.font_large.render("Soul编辑", True, self.text_color)
        self.screen.blit(title, (self.MARGIN_LEFT, self.Y_TITLE))

        # 操作提示（和标题同一行右边）
        hint_texts = [
            "Tab: 切换辩手",
            "滚轮: 滚动",
            "Ctrl+Enter: 保存",
            "ESC: 返回"
        ]
        hint_x = self.width - self.MARGIN_LEFT - 500
        for i, hint in enumerate(hint_texts):
            text = self.font_hint.render(hint, True, self.hint_color)
            self.screen.blit(text, (hint_x + i * 125, self.Y_TITLE + 5))

        # 分隔线
        pygame.draw.line(self.screen, (50, 55, 70),
                        (self.MARGIN_LEFT, self.Y_HINT + 15),
                        (self.width - self.MARGIN_LEFT, self.Y_HINT + 15), 1)

        # 辩手标签按钮
        for btn in self.buttons:
            if btn["action"] == "tab":
                is_hover = btn["rect"].collidepoint(pygame.mouse.get_pos())
                is_active = DEBATERS[self.current_debater]["name"] == btn["text"]

                if is_active:
                    bg_color = self.accent_color
                    text_color = (255, 255, 255)
                elif is_hover:
                    bg_color = (60, 70, 90)
                    text_color = self.text_color
                else:
                    bg_color = self.panel_color
                    text_color = (180, 185, 200)

                pygame.draw.rect(self.screen, bg_color, btn["rect"], border_radius=8)
                text = self.font_medium.render(btn["text"], True, text_color)
                text_rect = text.get_rect(center=btn["rect"].center)
                self.screen.blit(text, text_rect)

        # 当前辩手信息
        debater = DEBATERS[self.current_debater]
        info = self.font_medium.render(
            f"当前编辑：{debater['name']}「{debater['title']}」- {debater['position']}",
            True, self.accent_color
        )
        self.screen.blit(info, (self.MARGIN_LEFT, self.Y_CURRENT_INFO))

        # 文本框背景
        pygame.draw.rect(self.screen, self.panel_color, self.text_box_rect, border_radius=10)
        border_color = self.input_focus if self.input_active else self.input_border
        pygame.draw.rect(self.screen, border_color, self.text_box_rect, 2, border_radius=10)

        # 绘制文本
        line_height = 28
        y = self.text_box_rect.y + 15 - self.scroll_offset

        # 计算可见行
        visible_start = self.scroll_offset // line_height
        visible_count = (self.text_box_rect.height - 30) // line_height + 2

        for idx, line_data in enumerate(self.text_lines):
            if idx < visible_start:
                continue
            if idx >= visible_start + visible_count:
                break

            current_y = self.text_box_rect.y + 15 + (idx - visible_start) * line_height
            if self.text_box_rect.top < current_y < self.text_box_rect.bottom - 20:
                self.screen.blit(line_data["surface"], (self.text_box_rect.x + 20, current_y))

        # 底部按钮
        for btn in self.buttons:
            if btn["action"] != "tab":
                is_hover = btn["rect"].collidepoint(pygame.mouse.get_pos())
                if btn.get("highlight"):
                    color = self.accent_color if is_hover else (50, 60, 80)
                    text_color = (255, 255, 255) if is_hover else self.text_color
                else:
                    color = (50, 55, 70) if is_hover else (40, 45, 60)
                    text_color = self.text_color

                pygame.draw.rect(self.screen, color, btn["rect"], border_radius=6)
                text = self.font_small.render(btn["text"], True, text_color)
                text_rect = text.get_rect(center=btn["rect"].center)
                self.screen.blit(text, text_rect)

        # 消息提示
        if message:
            msg_text, msg_color = message
            surface = self.font_medium.render(msg_text, True, msg_color)
            rect = surface.get_rect(center=(self.width // 2, 50))
            pygame.draw.rect(self.screen, self.panel_color, rect.inflate(40, 20), border_radius=8)
            self.screen.blit(surface, rect)


# 独立运行测试
if __name__ == "__main__":
    editor = SoulEditor()
    result = editor.run()
    print(f"退出: {result}")
    pygame.quit()
