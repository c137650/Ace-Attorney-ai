"""
立场选择页面
辩题随机，玩家选择正方或反方
"""

import pygame
import os
import sys
import random

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

# 辩题列表（用于随机抽取）
TOPICS = [
    {
        "id": "t001",
        "title": "AI是否应该取代教师",
        "description": "随着人工智能技术的发展，AI在教育领域的应用越来越广泛。",
        "stance_a": "AI应该取代教师",
        "stance_b": "教师不可替代",
        "stance_a_detail": "AI可以个性化教学、提供24小时服务、数据驱动精准教学。",
        "stance_b_detail": "教师能提供情感关怀、道德引导、创造力培养。",
    },
    {
        "id": "t002",
        "title": "电子游戏对青少年的利弊",
        "description": "电子游戏已经成为青少年最流行的娱乐方式之一。",
        "stance_a": "电子游戏对青少年利大于弊",
        "stance_b": "电子游戏对青少年弊大于利",
        "stance_a_detail": "游戏可以锻炼反应能力，培养团队协作、释放压力。",
        "stance_b_detail": "容易沉迷、影响学业、可能接触暴力内容。",
    },
    {
        "id": "t003",
        "title": "996工作制应该被禁止",
        "description": "996工作制（早9点上班、晚9点下班、每周6天）在互联网行业普遍存在。",
        "stance_a": "996工作制应该被禁止",
        "stance_b": "996工作制不应被禁止",
        "stance_a_detail": "它严重损害员工健康、破坏家庭生活、违反劳动法。",
        "stance_b_detail": "市场经济自由选择、年轻人需要奋斗、某些行业确实需要。",
    },
    {
        "id": "t004",
        "title": "大学生应该先就业还是先择业",
        "description": "面对就业压力，有人主张先找到工作再说，有人认为应该坚持理想。",
        "stance_a": "大学生应该先就业再择业",
        "stance_b": "大学生应该先择业再就业",
        "stance_a_detail": "先积累经验、减轻家庭负担、在实践中明确方向。",
        "stance_b_detail": "选择喜欢的领域更容易坚持、起点决定高度、不将就是负责。",
    },
    {
        "id": "t005",
        "title": "网络舆论对司法公正的影响",
        "description": "网络时代，舆论监督成为重要力量。",
        "stance_a": "网络舆论对司法公正影响正面",
        "stance_b": "网络舆论对司法公正影响负面",
        "stance_a_detail": "它监督权力、防止腐败、让正义可见。",
        "stance_b_detail": "它可能干扰独立审判、网络暴力伤害无辜。",
    },
]


class StanceSelect:
    """立场选择器"""

    def __init__(self, screen_width=1280, screen_height=720):
        self.MARGIN = 50
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("AI辩论赛 - 选择立场")
        self.clock = pygame.time.Clock()

        self.width = screen_width
        self.height = screen_height

        # 字体
        self.font_large = load_font(40)
        self.font_medium = load_font(28)
        self.font_small = load_font(22)
        self.font_hint = load_font(18)

        # 颜色
        self.bg_color = (20, 25, 35)
        self.panel_color = (30, 35, 50)
        self.player_color = (66, 133, 244)  # 蓝色-正方
        self.opponent_color = (234, 67, 53)  # 红色-反方
        self.text_color = (220, 225, 235)
        self.hint_color = (120, 125, 140)
        self.accent_color = (66, 133, 244)

        # 随机抽取辩题
        self.current_topic = random.choice(TOPICS)

        # 立场选择状态: None, "A"(正方), "B"(反方)
        self.selected_stance = None
        self.player_stance = "A"  # 最终选择

        # 辩题卡片区域
        self.topic_rect = pygame.Rect(self.MARGIN, 150, screen_width - self.MARGIN * 2, 400)

        # 立场选择区域
        self.stance_a_rect = pygame.Rect(self.MARGIN, 580, 500, 100)
        self.stance_b_rect = pygame.Rect(screen_width - self.MARGIN - 500, 580, 500, 100)

    def run(self):
        """运行立场选择"""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a or event.key == pygame.K_1:
                        self.selected_stance = "A"
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d or event.key == pygame.K_2:
                        self.selected_stance = "B"
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        if self.selected_stance:
                            self.player_stance = self.selected_stance
                            return {
                                "topic": self.current_topic,
                                "player_stance": self.player_stance
                            }

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos

                    if self.stance_a_rect.collidepoint(mx, my):
                        self.selected_stance = "A"
                    elif self.stance_b_rect.collidepoint(mx, my):
                        self.selected_stance = "B"

                    # 确认按钮
                    if self.selected_stance:
                        confirm_rect = pygame.Rect(
                            self.width // 2 - 100,
                            self.height - 50,
                            200, 45
                        )
                        if confirm_rect.collidepoint(mx, my):
                            self.player_stance = self.selected_stance
                            return {
                                "topic": self.current_topic,
                                "player_stance": self.player_stance
                            }

                    # 返回按钮
                    back_rect = pygame.Rect(self.MARGIN, self.height - 50, 100, 40)
                    if back_rect.collidepoint(mx, my):
                        return None

                    # 换题按钮
                    refresh_rect = pygame.Rect(self.width - self.MARGIN - 100, self.height - 50, 100, 40)
                    if refresh_rect.collidepoint(mx, my):
                        self.current_topic = random.choice(TOPICS)
                        self.selected_stance = None

            # 绘制
            self._draw()
            pygame.display.flip()
            self.clock.tick(60)

        return None

    def _draw(self):
        """绘制界面"""
        self.screen.fill(self.bg_color)

        # 标题
        title = self.font_large.render("选择你的立场", True, self.text_color)
        self.screen.blit(title, (self.MARGIN, 40))

        # 副标题
        subtitle = self.font_small.render(
            "辩题已随机抽取，请选择你要支持的立场",
            True, self.hint_color
        )
        self.screen.blit(subtitle, (self.MARGIN, 95))

        # 辩题卡片
        pygame.draw.rect(self.screen, self.panel_color, self.topic_rect, border_radius=15)

        # 辩题标题
        topic_title = self.font_large.render(f"辩题：{self.current_topic['title']}", True, (255, 255, 255))
        topic_title_rect = topic_title.get_rect(centerx=self.topic_rect.centerx, top=self.topic_rect.top + 30)
        self.screen.blit(topic_title, topic_title_rect)

        # 辩题描述
        desc = self.font_small.render(self.current_topic['description'], True, self.hint_color)
        desc_rect = desc.get_rect(centerx=self.topic_rect.centerx, top=self.topic_rect.top + 85)
        self.screen.blit(desc, desc_rect)

        # 分隔线
        line_y = self.topic_rect.top + 130
        pygame.draw.line(self.screen, (60, 65, 85),
                        (self.topic_rect.left + 40, line_y),
                        (self.topic_rect.right - 40, line_y), 2)

        # 正方立场框
        self._draw_stance_box(
            self.topic_rect.left + 50,
            line_y + 30,
            self.topic_rect.width // 2 - 70,
            200,
            "A",
            "正方",
            self.current_topic['stance_a'],
            self.current_topic['stance_a_detail'],
            self.player_color,
            "按 ← 或 1 选择"
        )

        # 反方立场框
        self._draw_stance_box(
            self.topic_rect.left + self.topic_rect.width // 2 + 20,
            line_y + 30,
            self.topic_rect.width // 2 - 70,
            200,
            "B",
            "反方",
            self.current_topic['stance_b'],
            self.current_topic['stance_b_detail'],
            self.opponent_color,
            "按 → 或 2 选择"
        )

        # VS
        vs_text = self.font_large.render("VS", True, (100, 100, 100))
        vs_rect = vs_text.get_rect(center=(self.topic_rect.centerx, line_y + 130))
        self.screen.blit(vs_text, vs_rect)

        # 底部按钮
        # 返回
        back_rect = pygame.Rect(self.MARGIN, self.height - 50, 100, 40)
        pygame.draw.rect(self.screen, (40, 45, 60), back_rect, border_radius=8)
        back_text = self.font_small.render("← 返回", True, self.text_color)
        self.screen.blit(back_text, back_text.get_rect(center=back_rect.center))

        # 换题
        refresh_rect = pygame.Rect(self.width - self.MARGIN - 100, self.height - 50, 100, 40)
        pygame.draw.rect(self.screen, (40, 45, 60), refresh_rect, border_radius=8)
        refresh_text = self.font_small.render("换一道", True, self.text_color)
        self.screen.blit(refresh_text, refresh_text.get_rect(center=refresh_rect.center))

        # 确认按钮（只有选择了立场才显示）
        if self.selected_stance:
            confirm_rect = pygame.Rect(self.width // 2 - 100, self.height - 50, 200, 45)
            pygame.draw.rect(self.screen, self.accent_color, confirm_rect, border_radius=10)

            stance_text = "正方" if self.selected_stance == "A" else "反方"
            confirm_text = self.font_medium.render(f"确认选择 {stance_text} →", True, (255, 255, 255))
            self.screen.blit(confirm_text, confirm_text.get_rect(center=confirm_rect.center))

        # 底部提示
        hint = self.font_hint.render("← / A / 1 选择正方    → / D / 2 选择反方    Enter 确认", True, self.hint_color)
        self.screen.blit(hint, hint.get_rect(centerx=self.width // 2, bottom=self.height - 10))

    def _draw_stance_box(self, x, y, width, height, stance_key, stance_name, stance_title, stance_detail, color, hint):
        """绘制立场选择框"""
        is_selected = self.selected_stance == stance_key

        # 背景
        bg_color = (color[0] // 3, color[1] // 3, color[2] // 3) if is_selected else (35, 40, 55)
        pygame.draw.rect(self.screen, bg_color, (x, y, width, height), border_radius=12)

        # 边框
        border_color = color if is_selected else (60, 65, 80)
        border_width = 3 if is_selected else 2
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), border_width, border_radius=12)

        # 立场标签
        label = self.font_medium.render(stance_name, True, color)
        self.screen.blit(label, (x + 20, y + 15))

        # 立场标题
        title = self.font_small.render(stance_title, True, (255, 255, 255))
        self.screen.blit(title, (x + 20, y + 50))

        # 立场说明
        detail = self.font_hint.render(stance_detail[:30] + "..." if len(stance_detail) > 30 else stance_detail, True, self.hint_color)
        self.screen.blit(detail, (x + 20, y + 90))

        # 提示
        if is_selected:
            hint_text = self.font_hint.render("✓ 已选择", True, color)
        else:
            hint_text = self.font_hint.render(hint, True, self.hint_color)
        self.screen.blit(hint_text, (x + 20, y + height - 30))


# 独立运行测试
if __name__ == "__main__":
    selector = StanceSelect()
    result = selector.run()
    if result:
        print(f"选择: {result['topic']['title']} - {'正方' if result['player_stance'] == 'A' else '反方'}")
    else:
        print("取消选择")
    pygame.quit()
