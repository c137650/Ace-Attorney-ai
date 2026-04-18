"""
Soul编辑页面（Tkinter版）
玩家可以在游戏开始前编辑己方辩手的Soul。
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext

# 添加backend路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

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
- 常用\"我方认为\"、\"综上所述\"
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
- 常用\"对方辩友\"、\"请对方注意\"
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
- 常用\"请问对方\"、\"我方再问\"
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
    """Soul编辑器（Tkinter界面）"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI辩论赛 - Soul编辑")
        self.root.geometry("1280x720")
        self.root.minsize(1080, 640)

        # 与开始菜单一致的深色蓝系风格
        self.bg_color = "#191923"
        self.panel_color = "#1e2332"
        self.card_color = "#282c3d"
        self.text_color = "#e6eaf2"
        self.muted_text = "#9aa3b5"
        self.accent = "#4285f4"
        self.accent_hover = "#5b98ff"
        self.border = "#5b6f97"
        self.success = "#34a853"

        self.root.configure(bg=self.bg_color)

        # 数据状态
        self.current_debater = 0
        self.contents = {d["id"]: DEFAULT_SOULS[d["id"]] for d in DEBATERS}
        self.result = "menu"

        self.load_from_files()
        self._build_ui()
        self._load_current_content_to_editor()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.bind("<Escape>", lambda _e: self._return_menu())
        self.root.bind("<Control-Return>", lambda _e: self._save_only(show_message=True))
        self.root.bind("<Tab>", self._switch_next_debater)

    def _build_ui(self):
        title_bar = tk.Frame(self.root, bg=self.bg_color)
        title_bar.pack(fill="x", padx=40, pady=(24, 10))

        title = tk.Label(
            title_bar,
            text="Soul编辑",
            bg=self.bg_color,
            fg=self.text_color,
            font=("Microsoft YaHei UI", 30, "bold"),
        )
        title.pack(side="left")

        hint = tk.Label(
            title_bar,
            text="Tab: 切换辩手   Ctrl+Enter: 保存   ESC: 返回",
            bg=self.bg_color,
            fg=self.muted_text,
            font=("Microsoft YaHei UI", 12),
        )
        hint.pack(side="right", pady=(8, 0))

        mode_line = tk.Frame(self.root, bg="#323a4d", height=1)
        mode_line.pack(fill="x", padx=40, pady=(0, 14))

        # 辩手切换Tab
        self.tab_frame = tk.Frame(self.root, bg=self.bg_color)
        self.tab_frame.pack(fill="x", padx=40)
        self.tab_buttons = []
        for idx, d in enumerate(DEBATERS):
            btn = tk.Button(
                self.tab_frame,
                text=d["name"],
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Microsoft YaHei UI", 14, "bold"),
                command=lambda i=idx: self._switch_debater(i),
            )
            btn.pack(side="left", padx=(0, 18), ipadx=24, ipady=8)
            self.tab_buttons.append(btn)

        self.info_label = tk.Label(
            self.root,
            text="",
            bg=self.bg_color,
            fg=self.accent,
            font=("Microsoft YaHei UI", 14, "bold"),
            anchor="w",
        )
        self.info_label.pack(fill="x", padx=40, pady=(14, 10))

        editor_wrap = tk.Frame(self.root, bg=self.panel_color, highlightthickness=1, highlightbackground=self.border)
        editor_wrap.pack(fill="both", expand=True, padx=40, pady=(0, 14))

        self.editor = scrolledtext.ScrolledText(
            editor_wrap,
            wrap="word",
            undo=True,
            bg=self.card_color,
            fg=self.text_color,
            insertbackground=self.text_color,
            relief="flat",
            bd=0,
            padx=16,
            pady=14,
            font=("Microsoft YaHei UI", 12),
            selectbackground="#3f5f96",
            selectforeground="#ffffff",
        )
        self.editor.pack(fill="both", expand=True, padx=12, pady=12)
        self.editor.bind("<KeyRelease>", lambda _e: self._sync_editor_to_current())

        bottom = tk.Frame(self.root, bg=self.bg_color)
        bottom.pack(fill="x", padx=40, pady=(0, 22))

        self.status_label = tk.Label(
            bottom,
            text="",
            bg=self.bg_color,
            fg=self.success,
            font=("Microsoft YaHei UI", 12),
        )
        self.status_label.pack(side="left")

        right = tk.Frame(bottom, bg=self.bg_color)
        right.pack(side="right")

        self._make_action_button(bottom, "重置模板", self._reset_current, variant="secondary").pack(side="left", padx=(0, 10))
        self._make_action_button(bottom, "保存修改", lambda: self._save_only(show_message=True), variant="secondary").pack(side="left", padx=(0, 10))

        self._make_action_button(right, "开始游戏 ->", self._start_game, variant="primary").pack(side="right", padx=(10, 0))
        self._make_action_button(right, "<- 返回", self._return_menu, variant="secondary").pack(side="right")

        self._refresh_tabs()
        self._refresh_info_label()

    def _make_action_button(self, parent, text, command, variant="secondary"):
        if variant == "primary":
            bg = self.accent
            hover = self.accent_hover
            fg = "#ffffff"
        else:
            bg = "#2a2f42"
            hover = "#343c52"
            fg = self.text_color

        button = tk.Button(
            parent,
            text=text,
            command=command,
            cursor="hand2",
            relief="flat",
            bd=0,
            bg=bg,
            fg=fg,
            activebackground=hover,
            activeforeground="#ffffff",
            highlightthickness=1,
            highlightbackground=self.border,
            highlightcolor=self.border,
            font=("Microsoft YaHei UI", 12, "bold"),
            padx=18,
            pady=8,
        )

        button.bind("<Enter>", lambda _e, b=button, c=hover: b.configure(bg=c))
        button.bind("<Leave>", lambda _e, b=button, c=bg: b.configure(bg=c))
        return button

    def _refresh_tabs(self):
        for idx, btn in enumerate(self.tab_buttons):
            if idx == self.current_debater:
                btn.configure(bg=self.accent, fg="#ffffff", activebackground=self.accent_hover, activeforeground="#ffffff")
            else:
                btn.configure(bg="#23283a", fg="#cdd5e5", activebackground="#313a52", activeforeground="#ffffff")

    def _refresh_info_label(self):
        d = DEBATERS[self.current_debater]
        self.info_label.configure(text=f"当前编辑：{d['name']}「{d['title']}」- {d['position']}")

    def _sync_editor_to_current(self):
        debater_id = DEBATERS[self.current_debater]["id"]
        self.contents[debater_id] = self.editor.get("1.0", "end-1c")

    def _load_current_content_to_editor(self):
        self._refresh_tabs()
        self._refresh_info_label()
        debater_id = DEBATERS[self.current_debater]["id"]
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", self.contents[debater_id])
        self.editor.focus_set()

    def _switch_debater(self, index):
        if index == self.current_debater:
            return
        self._sync_editor_to_current()
        self.current_debater = index
        self._load_current_content_to_editor()

    def _switch_next_debater(self, _event=None):
        self._sync_editor_to_current()
        self.current_debater = (self.current_debater + 1) % len(DEBATERS)
        self._load_current_content_to_editor()
        return "break"

    def _set_status(self, text, color=None):
        self.status_label.configure(text=text, fg=(color or self.success))
        if text:
            self.root.after(1800, lambda: self.status_label.configure(text=""))

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

    def _reset_current(self):
        debater_id = DEBATERS[self.current_debater]["id"]
        self.contents[debater_id] = DEFAULT_SOULS[debater_id]
        self._load_current_content_to_editor()
        self._set_status("已重置为默认模板")

    def _save_only(self, show_message=False):
        self._sync_editor_to_current()
        ok = self.save_to_files()
        if ok and show_message:
            self._set_status("保存成功")
        elif not ok and show_message:
            self._set_status("保存失败", color="#ea4335")
        return ok

    def _return_menu(self):
        self.result = "menu"
        self.root.destroy()

    def _start_game(self):
        if not self._save_only(show_message=False):
            messagebox.showerror("保存失败", "文件保存失败，请检查文件权限。")
            return
        self.result = "start"
        self.root.destroy()

    def _on_close(self):
        self.result = "menu"
        self.root.destroy()

    def run(self):
        """运行编辑器"""
        self.root.mainloop()
        return self.result


# 独立运行测试
if __name__ == "__main__":
    editor = SoulEditor()
    result = editor.run()
    print(f"退出: {result}")
