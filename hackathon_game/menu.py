"""
AI 辩论游戏 - 首页菜单

设计规格：
- 标题居中显示
- 两个按钮：开始游戏、读取存档
- 背景可自定义
"""

import pygame
import os

# ==================== 配置 ====================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# 颜色配置
COLORS = {
    "background": (25, 25, 35),       # 深蓝灰背景
    "title": (255, 255, 255),         # 标题白色
    "title_glow": (66, 133, 244),     # 标题发光色（蓝色）
    "button_normal": (50, 50, 70),     # 按钮默认
    "button_hover": (70, 90, 140),     # 按钮悬停
    "button_text": (255, 255, 255),    # 按钮文字
    "button_border": (100, 130, 200),  # 按钮边框
    "hint": (120, 120, 140),           # 提示文字
}


class MenuButton:
    """菜单按钮"""

    def __init__(self, x, y, width, height, text, icon=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.icon = icon
        self.is_hovered = False

        # 按钮效果
        self.hover_scale = 1.05
        self.current_scale = 1.0
        self.target_scale = 1.0

    def update(self):
        """更新按钮动画"""
        self.target_scale = 1.05 if self.is_hovered else 1.0
        self.current_scale += (self.target_scale - self.current_scale) * 0.15

    def draw(self, screen, font_large, font_medium):
        """绘制按钮"""
        # 计算缩放后的尺寸
        scaled_width = int(self.rect.width * self.current_scale)
        scaled_height = int(self.rect.height * self.current_scale)
        scaled_x = self.rect.centerx - scaled_width // 2
        scaled_y = self.rect.centery - scaled_height // 2
        scaled_rect = pygame.Rect(scaled_x, scaled_y, scaled_width, scaled_height)

        # 按钮颜色
        if self.is_hovered:
            btn_color = COLORS["button_hover"]
            border_color = COLORS["title_glow"]
            border_width = 3
        else:
            btn_color = COLORS["button_normal"]
            border_color = COLORS["button_border"]
            border_width = 2

        # 绘制按钮背景
        pygame.draw.rect(screen, btn_color, scaled_rect, border_radius=15)

        # 绘制按钮边框
        pygame.draw.rect(screen, border_color, scaled_rect, border_width, border_radius=15)

        # 绘制文字
        full_text = f"{self.icon} {self.text}" if self.icon else self.text
        text_surface = font_large.render(full_text, True, COLORS["button_text"])
        text_rect = text_surface.get_rect(center=scaled_rect.center)
        screen.blit(text_surface, text_rect)

    def check_hover(self, pos):
        """检查鼠标是否悬停"""
        self.is_hovered = self.rect.collidepoint(pos)


class Menu:
    """首页菜单"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI 辩论赛")
        self.clock = pygame.time.Clock()

        # 加载中文字体
        self.fonts = self._load_chinese_fonts()

        # 创建按钮
        button_width = 280
        button_height = 60
        button_y = 360

        self.buttons = [
            MenuButton(
                SCREEN_WIDTH // 2 - button_width // 2,
                button_y,
                button_width,
                button_height,
                "开始游戏",
                "▶"
            ),
            MenuButton(
                SCREEN_WIDTH // 2 - button_width // 2,
                button_y + 75,
                button_width,
                button_height,
                "Soul编辑",
                "✎"
            ),
            MenuButton(
                SCREEN_WIDTH // 2 - button_width // 2,
                button_y + 150,
                button_width,
                button_height,
                "读取存档",
                "📁"
            ),
        ]

        # 当前选中的按钮索引
        self.selected_index = -1

        # 背景装饰动画
        self.decorations = self._create_decorations()

        # 标题动画
        self.title_y = 180
        self.title_target_y = 180
        self.title_alpha = 0
        self.title_target_alpha = 255

        # 运行状态
        self.running = True
        self.choice = None  # "start" 或 "load"
        self.use_llm = False  # 是否使用LLM

        # 加载背景
        self.background = None
        self._load_background()

        # 检查配置文件
        self._check_llm_config()

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
                    fonts['title'] = pygame.font.Font(path, 72)
                    fonts['large'] = pygame.font.Font(path, 36)
                    fonts['medium'] = pygame.font.Font(path, 28)
                    fonts['small'] = pygame.font.Font(path, 20)
                    print(f"✓ 加载字体: {path}")
                    return fonts
                except:
                    continue

        # 默认字体
        fonts['title'] = pygame.font.Font(None, 80)
        fonts['large'] = pygame.font.Font(None, 40)
        fonts['medium'] = pygame.font.Font(None, 30)
        fonts['small'] = pygame.font.Font(None, 22)
        return fonts

    def _create_decorations(self):
        """创建背景装饰"""
        decorations = []
        # 添加一些装饰性圆形
        for _ in range(8):
            decorations.append({
                'x': 0,
                'y': 0,
                'radius': 30,
                'color': (40, 50, 80),
                'speed': 0.2,
                'angle': 0,
            })
        return decorations

    def _load_background(self):
        """加载背景"""
        bg_path = os.path.join(os.path.dirname(__file__), "assets", "menu_bg.png")
        if os.path.exists(bg_path):
            self.background = pygame.image.load(bg_path)
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            print(f"✓ 加载菜单背景: {bg_path}")

    def _check_llm_config(self):
        """检查LLM配置"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "backend", "config.json")
        if os.path.exists(config_path):
            try:
                import json
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                api_key = config.get("api", {}).get("api_key", "")
                if api_key and api_key != "YOUR_API_KEY_HERE":
                    self.use_llm = True
                    print(f"✓ 检测到LLM配置已设置")
                else:
                    self.use_llm = False
                    print(f"⚠ LLM未配置API Key，将使用演示模式")
            except:
                self.use_llm = False

    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.choice = None
            elif event.type == pygame.MOUSEMOTION:
                for i, btn in enumerate(self.buttons):
                    btn.check_hover(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左键
                    for i, btn in enumerate(self.buttons):
                        if btn.is_hovered:
                            if i == 0:
                                self.choice = "start"
                                self.running = False
                            elif i == 1:
                                self.choice = "soul_edit"
                                self.running = False
                            elif i == 2:
                                self.choice = "load"
                                self.running = False
                    # 点击模式切换区域
                    mode_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 270, 300, 50)
                    if mode_rect.collidepoint(event.pos):
                        self.use_llm = not self.use_llm
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.choice = None
                elif event.key == pygame.K_1 or event.key == pygame.K_RETURN:
                    if len(self.buttons) > 0:
                        self.choice = "start"
                        self.running = False
                elif event.key == pygame.K_2:
                    if len(self.buttons) > 1:
                        self.choice = "soul_edit"
                        self.running = False
                elif event.key == pygame.K_3:
                    if len(self.buttons) > 2:
                        self.choice = "load"
                        self.running = False
                elif event.key == pygame.K_m or event.key == pygame.KMOD_SHIFT:
                    # M键切换模式
                    self.use_llm = not self.use_llm

    def update(self):
        """更新"""
        # 更新按钮
        for btn in self.buttons:
            btn.update()

        # 更新标题动画
        if self.title_alpha < self.title_target_alpha:
            self.title_alpha += 5

        # 更新装饰
        for dec in self.decorations:
            dec['angle'] += dec['speed']

    def draw(self):
        """绘制"""
        # 背景
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(COLORS["background"])

        # 绘制装饰背景
        self._draw_decorations()

        # 绘制标题
        self._draw_title()

        # 绘制模式选择
        self._draw_mode_selector()

        # 绘制按钮
        for btn in self.buttons:
            btn.draw(self.screen, self.fonts['large'], self.fonts['medium'])

        # 绘制底部提示
        self._draw_hints()

        pygame.display.flip()

    def _draw_mode_selector(self):
        """绘制模式选择器"""
        # 模式背景
        mode_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 270, 300, 50)
        pygame.draw.rect(self.screen, (40, 40, 60), mode_rect, border_radius=10)

        if self.use_llm:
            border_color = (100, 200, 100)
            mode_text = "🤖 AI模式 - 已启用"
        else:
            border_color = (150, 150, 150)
            mode_text = "📝 演示模式"

        pygame.draw.rect(self.screen, border_color, mode_rect, 2, border_radius=10)
        mode_surface = self.fonts['medium'].render(mode_text, True, COLORS["title"])
        mode_rect_text = mode_surface.get_rect(center=mode_rect.center)
        self.screen.blit(mode_surface, mode_rect_text)

        # 提示
        tip = self.fonts['small'].render("按 M 键切换模式", True, (100, 100, 120))
        self.screen.blit(tip, (SCREEN_WIDTH // 2 - tip.get_width() // 2, 375))

    def _draw_decorations(self):
        """绘制装饰元素"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2

        for i, dec in enumerate(self.decorations):
            # 计算装饰位置（围绕中心旋转）
            angle = dec['angle'] + (i * 0.5)
            distance = 200 + (i % 3) * 100
            x = center_x + int(distance * pygame.math.Vector2(1, 0).rotate(-angle).x)
            y = center_y + int(distance * 0.5 * pygame.math.Vector2(1, 0).rotate(-angle).y)

            # 绘制装饰圆
            alpha = 30 + (i % 5) * 10
            color = (*dec['color'][:3], alpha)
            surface = pygame.Surface((dec['radius'] * 2, dec['radius'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, color, (dec['radius'], dec['radius']), dec['radius'])
            self.screen.blit(surface, (x - dec['radius'], y - dec['radius']))

    def _draw_title(self):
        """绘制标题"""
        # 标题文字
        title_text = "AI 辩 论 赛"

        # 创建半透明背景
        title_bg = pygame.Surface((600, 120), pygame.SRCALPHA)
        title_bg.fill((0, 0, 0, 100))
        title_rect = title_bg.get_rect(center=(SCREEN_WIDTH // 2, self.title_y))
        self.screen.blit(title_bg, title_rect)

        # 主标题（带描边效果）
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            shadow = self.fonts['title'].render(title_text, True, (30, 30, 50))
            shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + offset[0], self.title_y + offset[1]))
            self.screen.blit(shadow, shadow_rect)

        # 标题
        title_surface = self.fonts['title'].render(title_text, True, COLORS["title"])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, self.title_y))
        self.screen.blit(title_surface, title_rect)

        # 副标题
        subtitle = "人工智能辩论挑战"
        subtitle_surface = self.fonts['medium'].render(subtitle, True, COLORS["hint"])
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, self.title_y + 50))
        self.screen.blit(subtitle_surface, subtitle_rect)

    def _draw_hints(self):
        """绘制提示"""
        hints = [
            "按 1 开始  |  2 Soul编辑  |  3 存档",
            "按 M 切换 AI/演示模式",
            "按 ESC 退出"
        ]

        y = SCREEN_HEIGHT - 40
        for i, hint in enumerate(hints):
            text = self.fonts['small'].render(hint, True, COLORS["hint"])
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y - i * 25))
            self.screen.blit(text, text_rect)

    def run(self):
        """运行菜单"""
        print("=" * 50)
        print("AI 辩论游戏 - 首页")
        print("=" * 50)
        print("选项:")
        print("  1 / 回车: 开始游戏")
        print("  2: 读取存档")
        print("  ESC: 退出")
        print("=" * 50)

        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        return self.choice


# ==================== 入口 ====================

if __name__ == "__main__":
    menu = Menu()
    choice = menu.run()
    use_llm = menu.use_llm
    if choice == "start":
        print(f">>> 启动游戏... (LLM={'启用' if use_llm else '禁用'})")
        # 直接启动游戏，传递LLM模式
        from main import Game
        game = Game()
        game.load_backend(use_llm=use_llm)
        if game.debate_game:
            game.run()
    elif choice == "load":
        print(">>> 加载存档...")
    else:
        print(">>> 退出游戏...")
