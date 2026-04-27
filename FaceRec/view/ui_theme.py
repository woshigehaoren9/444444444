from PyQt5.QtWidgets import QLabel, QPushButton, QTableWidget, QWidget


PRIMARY = "#1F6FEB"
PRIMARY_HOVER = "#3B82F6"
SUCCESS = "#16A34A"
WARNING = "#D97706"
DANGER = "#DC2626"
BORDER = "#CBD5E1"
CARD_BG = "#FFFFFF"
SURFACE_BG = "#F8FAFC"


def apply_page_theme(widget: QWidget) -> None:
    widget.setStyleSheet(
        f"""
        QWidget {{
            background-color: {SURFACE_BG};
            color: #0F172A;
            font-family: "Microsoft YaHei";
            font-size: 13px;
        }}
        QGroupBox {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER};
            border-radius: 10px;
            margin-top: 10px;
            font-weight: 700;
            padding-top: 10px;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 14px;
            color: #1E293B;
            padding: 0 4px;
        }}
        QLineEdit, QComboBox, QDateEdit, QTimeEdit, QSpinBox {{
            background-color: #FFFFFF;
            border: 1px solid {BORDER};
            border-radius: 6px;
            min-height: 30px;
            padding: 0 10px;
        }}
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus, QSpinBox:focus {{
            border: 1px solid {PRIMARY};
        }}
        QTableWidget {{
            background-color: #FFFFFF;
            border: 1px solid {BORDER};
            border-radius: 8px;
            gridline-color: #E2E8F0;
            alternate-background-color: #F8FAFC;
        }}
        QHeaderView::section {{
            background-color: #E2E8F0;
            color: #0F172A;
            border: 0;
            border-right: 1px solid #CBD5E1;
            padding: 8px 6px;
            font-weight: 700;
        }}
        QProgressBar {{
            border: 1px solid {BORDER};
            border-radius: 6px;
            text-align: center;
            background-color: #EEF2FF;
        }}
        QProgressBar::chunk {{
            background-color: {PRIMARY};
            border-radius: 5px;
        }}
        """
    )


def style_nav_button(button: QPushButton, active: bool = False) -> None:
    if active:
        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {PRIMARY};
                color: #FFFFFF;
                border: 0;
                border-radius: 8px;
                text-align: left;
                padding-left: 20px;
                min-height: 46px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {PRIMARY_HOVER};
            }}
            """
        )
    else:
        button.setStyleSheet(
            """
            QPushButton {
                background-color: #334155;
                color: #E2E8F0;
                border: 0;
                border-radius: 8px;
                text-align: left;
                padding-left: 20px;
                min-height: 46px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #475569;
            }
            """
        )


def set_nav_active(buttons, active_btn: QPushButton) -> None:
    for btn in buttons:
        style_nav_button(btn, btn is active_btn)


def style_button(button: QPushButton, kind: str = "default") -> None:
    palette = {
        "primary": (PRIMARY, PRIMARY_HOVER),
        "success": (SUCCESS, "#22C55E"),
        "warning": (WARNING, "#F59E0B"),
        "danger": (DANGER, "#EF4444"),
        "default": ("#475569", "#64748B"),
    }
    normal, hover = palette.get(kind, palette["default"])
    button.setStyleSheet(
        f"""
        QPushButton {{
            background-color: {normal};
            color: #FFFFFF;
            border: 0;
            border-radius: 8px;
            min-height: 34px;
            padding: 0 14px;
            font-weight: 700;
        }}
        QPushButton:hover {{
            background-color: {hover};
        }}
        QPushButton:pressed {{
            padding-top: 1px;
        }}
        """
    )


def style_table(table: QTableWidget) -> None:
    table.setAlternatingRowColors(True)
    table.setStyleSheet(
        f"""
        QTableWidget {{
            background-color: #FFFFFF;
            border: 1px solid {BORDER};
            border-radius: 8px;
            gridline-color: #E2E8F0;
            alternate-background-color: #F8FAFC;
            selection-background-color: #DBEAFE;
            selection-color: #0F172A;
        }}
        QHeaderView::section {{
            background-color: #E2E8F0;
            color: #0F172A;
            border: 0;
            border-right: 1px solid #CBD5E1;
            padding: 8px 6px;
            font-weight: 700;
        }}
        """
    )


def style_hint_label(label: QLabel, kind: str = "info") -> None:
    color_map = {
        "info": ("#EFF6FF", "#1D4ED8"),
        "success": ("#ECFDF5", "#15803D"),
        "warning": ("#FFFBEB", "#B45309"),
        "danger": ("#FEF2F2", "#B91C1C"),
    }
    bg, fg = color_map.get(kind, color_map["info"])
    label.setStyleSheet(
        f"background:{bg}; color:{fg}; border:1px solid {BORDER}; border-radius:8px; padding:6px 10px;"
    )


def style_status_badge(label: QLabel, status: str) -> None:
    text = (status or "").strip()
    if text in ("已到", "补签", "签到成功"):
        style_hint_label(label, "success")
    elif text in ("迟到", "早退", "重复识别(冷却中)", "已签退"):
        style_hint_label(label, "warning")
    elif text in ("缺勤", "未识别", "识别失败", "班级未设置", "不在签到时段"):
        style_hint_label(label, "danger")
    else:
        style_hint_label(label, "info")
    label.setText(text or "未识别")
