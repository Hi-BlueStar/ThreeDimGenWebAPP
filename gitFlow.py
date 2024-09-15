from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit,
                               QMessageBox, QInputDialog, QComboBox, QDialog, QTextEdit, QGridLayout)
from PySide6.QtCore import Qt, QRect, Property, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QApplication, QPushButton, QGraphicsDropShadowEffect, QMainWindow
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont, QIcon
import subprocess
import sys
import matplotlib.pyplot as plt
import networkx as nx
import tempfile
import os

class AnimatedButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
        self.setFixedSize(160, 60)
        self.normal_color = QColor("#4ade80")  # 正常狀態的顏色
        self.hover_color = QColor("#67e8a9")   # 懸停狀態的顏色
        self.current_color = self.normal_color

        # 設置圓角按鈕
        self.setStyleSheet("border-radius: 20px; font-size: 14px; color: white;")

        # 添加陰影效果
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(20)
        self.shadow_effect.setXOffset(0)
        self.shadow_effect.setYOffset(5)
        self.shadow_effect.setColor(QColor("#b0bec5"))
        self.setGraphicsEffect(self.shadow_effect)

        # 設置動畫
        self.color_animation = QPropertyAnimation(self, b"button_color")
        self.color_animation.setDuration(200)

        self.scale_animation = QPropertyAnimation(self, b"scale_factor")
        self.scale_animation.setDuration(100)
        self.scale_animation.setEasingCurve(QEasingCurve.OutBack)

        self._scale_factor = 1.0

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 開啟抗鋸齒
        rect = self.rect()

        # 繪製按鈕背景
        painter.save()
        painter.scale(self._scale_factor, self._scale_factor)
        painter.translate(
            rect.width() * (1 - self._scale_factor) / (2 * self._scale_factor),
            rect.height() * (1 - self._scale_factor) / (2 * self._scale_factor)
        )
        painter.setBrush(QBrush(self.current_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 20, 20)  # 設置圓角
        painter.restore()

        # 繪製文字
        super().paintEvent(event)

    def enterEvent(self, event):
        self.color_animation.stop()
        self.color_animation.setStartValue(self.current_color)
        self.color_animation.setEndValue(self.hover_color)
        self.color_animation.start()

        self.scale_animation.stop()
        self.scale_animation.setStartValue(self._scale_factor)
        self.scale_animation.setEndValue(1.05)
        self.scale_animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        self.color_animation.stop()
        self.color_animation.setStartValue(self.current_color)
        self.color_animation.setEndValue(self.normal_color)
        self.color_animation.start()

        self.scale_animation.stop()
        self.scale_animation.setStartValue(self._scale_factor)
        self.scale_animation.setEndValue(1.0)
        self.scale_animation.start()

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        self.scale_animation.stop()
        self.scale_animation.setStartValue(self._scale_factor)
        self.scale_animation.setEndValue(0.95)
        self.scale_animation.start()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.scale_animation.stop()
        self.scale_animation.setStartValue(self._scale_factor)
        self.scale_animation.setEndValue(1.05)
        self.scale_animation.start()

        super().mouseReleaseEvent(event)

    # 使用 Property 來設置動畫顏色
    def get_button_color(self):
        return self.current_color

    def set_button_color(self, color):
        self.current_color = color
        self.update()

    button_color = Property(QColor, get_button_color, set_button_color)

    # 添加縮放因子屬性
    def get_scale_factor(self):
        return self._scale_factor

    def set_scale_factor(self, factor):
        self._scale_factor = factor
        self.update()

    _scale_factor = 1.0
    scale_factor = Property(float, get_scale_factor, set_scale_factor)

class GitManagerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Git 流程管理工具")
        self.setWindowIcon(QIcon("git_icon.png"))  # 添加應用程式圖示
        self.setStyleSheet("background-color: #E0F7E0; border-radius: 20px; font-size: 14px; color: black;")
        self.setGeometry(100, 100, 600, 600)  # 調整視窗大小

        self.os_type = "Windows"  # 預設為 Windows
        self.remote_repo = "https://github.com/Hi-BlueStar/ThreeDimGenWebAPP.git"  # 遠端倉庫地址
        self.commit_message = "提交變更"  # 預設提交訊息

        # 標題
        self.label = QLabel("Git 流程管理", self)
        self.label.setStyleSheet("font-size: 24px; color: #2C662D; font-weight: bold;")
        self.label.setAlignment(Qt.AlignCenter)

        # 導覽說明
        self.guide_label = QLabel("請依照步驟完成 Git 的基本操作：", self)
        self.guide_label.setStyleSheet("color: #2C662D;")
        self.guide_label.setAlignment(Qt.AlignCenter)

        self.guide_text = QLabel("1. 初始化倉庫\n2. 創建分支或直接提交變更\n3. 推送到遠端倉庫\n4. 合併分支並解決衝突", self)
        self.guide_text.setStyleSheet("color: #2C662D;")
        self.guide_text.setAlignment(Qt.AlignCenter)

        # 操作系統選擇
        self.os_label = QLabel("選擇操作系統:", self)
        self.os_label.setStyleSheet("color: #2C662D;")

        self.os_menu = QComboBox(self)
        self.os_menu.addItems(["Windows", "Mac", "Linux (Ubuntu)"])
        self.os_menu.setStyleSheet("background-color: #A4DDA4; color: #2C662D;")
        self.os_menu.currentTextChanged.connect(self.update_os_type)

        # 遠端倉庫地址輸入框
        self.repo_label = QLabel("遠端倉庫地址:", self)
        self.repo_label.setStyleSheet("color: #2C662D;")
        self.repo_entry = QLineEdit(self)
        self.repo_entry.setText(self.remote_repo)
        self.repo_entry.setStyleSheet("background-color: #A4DDA4; color: #2C662D;")

        # 提交訊息輸入框
        self.commit_label = QLabel("提交訊息:", self)
        self.commit_label.setStyleSheet("color: #2C662D;")
        self.commit_entry = QLineEdit(self)
        self.commit_entry.setText(self.commit_message)
        self.commit_entry.setStyleSheet("background-color: #A4DDA4; color: #2C662D;")

        # 布局
        layout = QGridLayout()
        layout.addWidget(self.label, 0, 0, 1, 3)
        layout.addWidget(self.guide_label, 1, 0, 1, 3)
        layout.addWidget(self.guide_text, 2, 0, 1, 3)

        layout.addWidget(self.os_label, 3, 0)
        layout.addWidget(self.os_menu, 3, 1, 1, 2)

        layout.addWidget(self.repo_label, 4, 0)
        layout.addWidget(self.repo_entry, 4, 1, 1, 2)

        layout.addWidget(self.commit_label, 5, 0)
        layout.addWidget(self.commit_entry, 5, 1, 1, 2)

        # 功能按鈕
        button_style = "background-color: #A4DDA4; color: #2C662D; padding: 10px;"
        self.init_btn = AnimatedButton("初始化倉庫", self)
        self.init_btn.setStyleSheet(button_style)
        self.init_btn.clicked.connect(self.init_repository)
        layout.addWidget(self.init_btn, 6, 0)

        self.commit_btn = AnimatedButton("提交變更", self)
        self.commit_btn.setStyleSheet(button_style)
        self.commit_btn.clicked.connect(self.commit_changes)
        layout.addWidget(self.commit_btn, 6, 1)

        self.push_btn = AnimatedButton("推送至遠端", self)
        self.push_btn.setStyleSheet(button_style)
        self.push_btn.clicked.connect(self.push_changes)
        layout.addWidget(self.push_btn, 6, 2)

        self.branch_btn = AnimatedButton("顯示分支", self)
        self.branch_btn.setStyleSheet(button_style)
        self.branch_btn.clicked.connect(self.show_branches)
        layout.addWidget(self.branch_btn, 7, 0)

        self.create_branch_btn = AnimatedButton("創建新分支", self)
        self.create_branch_btn.setStyleSheet(button_style)
        self.create_branch_btn.clicked.connect(self.create_branch)
        layout.addWidget(self.create_branch_btn, 7, 1)

        self.switch_branch_btn = AnimatedButton("切換分支", self)
        self.switch_branch_btn.setStyleSheet(button_style)
        self.switch_branch_btn.clicked.connect(self.switch_branch)
        layout.addWidget(self.switch_branch_btn, 7, 2)

        self.merge_branch_btn = AnimatedButton("合併分支", self)
        self.merge_branch_btn.setStyleSheet(button_style)
        self.merge_branch_btn.clicked.connect(self.merge_branch)
        layout.addWidget(self.merge_branch_btn, 8, 0)

        self.rename_branch_btn = AnimatedButton("重命名分支", self)
        self.rename_branch_btn.setStyleSheet(button_style)
        self.rename_branch_btn.clicked.connect(self.rename_branch)
        layout.addWidget(self.rename_branch_btn, 8, 1)

        self.delete_branch_btn = AnimatedButton("刪除分支", self)
        self.delete_branch_btn.setStyleSheet(button_style)
        self.delete_branch_btn.clicked.connect(self.delete_branch)
        layout.addWidget(self.delete_branch_btn, 8, 2)

        self.show_branch_graph_btn = AnimatedButton("顯示分支圖表", self)
        self.show_branch_graph_btn.setStyleSheet(button_style)
        self.show_branch_graph_btn.clicked.connect(self.show_branch_graph)
        layout.addWidget(self.show_branch_graph_btn, 9, 0, 1, 3)

        # 設置間距和邊距
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        self.setLayout(layout)

    def update_os_type(self, os_type):
        self.os_type = os_type

    def run_git_command(self, command):
        """執行 Git 命令，根據操作系統選擇適當的 shell"""
        try:
            if self.os_type == "Windows":
                # Windows 上使用雙引號
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
            else:
                result = subprocess.run(command, shell=True, executable='/bin/bash', capture_output=True, text=True)

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise Exception(result.stderr.strip())
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"Git 命令失敗：\n{e}")
            return None

    def init_repository(self):
        """初始化 Git 倉庫"""
        output = self.run_git_command("git init")
        if output:
            QMessageBox.information(self, "初始化倉庫", f"成功初始化倉庫：\n{output}")

    def commit_changes(self):
        """提交變更"""
        output = self.run_git_command(f"git add . && git commit -m '{str(self.commit_entry.text())}'")
        if output:
            QMessageBox.information(self, "提交變更", f"提交成功：\n{output}")

    def push_changes(self):
        """推送至遠端倉庫"""
        repo = self.repo_entry.text() if self.repo_entry.text() else "origin"
        output = self.run_git_command(f"git push {repo} master")
        if output:
            QMessageBox.information(self, "推送至遠端", f"推送成功：\n{output}")

    def show_branches(self):
        """顯示分支"""
        output = self.run_git_command("git branch")
        if output:
            QMessageBox.information(self, "顯示分支", f"目前分支：\n{output}")

    def create_branch(self):
        """創建新分支"""
        branch_name, ok = QInputDialog.getText(self, "新分支名稱", "請輸入新分支名稱:")
        if ok and branch_name:
            output = self.run_git_command(f"git checkout -b {branch_name}")
            if output:
                QMessageBox.information(self, "創建新分支", f"成功創建並切換到新分支：\n{output}")

    def switch_branch(self):
        """切換到其他分支"""
        branch_name, ok = QInputDialog.getText(self, "切換分支", "請輸入要切換的分支名稱:")
        if ok and branch_name:
            output = self.run_git_command(f"git checkout {branch_name}")
            if output:
                QMessageBox.information(self, "切換分支", f"成功切換到分支：\n{output}")

    def merge_branch(self):
        """合併分支"""
        branch_name, ok = QInputDialog.getText(self, "合併分支", "請輸入要合併的分支名稱:")
        if ok and branch_name:
            output = self.run_git_command(f"git merge {branch_name}")
            if output:
                QMessageBox.information(self, "合併分支", f"成功合併分支：\n{output}")
            else:
                self.handle_merge_conflict()

    def rename_branch(self):
        """重命名分支"""
        new_branch_name, ok = QInputDialog.getText(self, "重命名分支", "請輸入新的分支名稱:")
        if ok and new_branch_name:
            output = self.run_git_command(f"git branch -m {new_branch_name}")
            if output is not None:
                QMessageBox.information(self, "重命名分支", f"成功重命名當前分支為：{new_branch_name}")

    def delete_branch(self):
        """刪除分支"""
        branch_name, ok = QInputDialog.getText(self, "刪除分支", "請輸入要刪除的分支名稱:")
        if ok and branch_name:
            confirm = QMessageBox.question(self, "刪除確認", f"確定要刪除分支 {branch_name} 嗎？")
            if confirm == QMessageBox.Yes:
                output = self.run_git_command(f"git branch -d {branch_name}")
                if output:
                    QMessageBox.information(self, "刪除分支", f"成功刪除分支：\n{output}")

    def handle_merge_conflict(self):
        """處理合併衝突"""
        resolve = QMessageBox.question(self, "合併衝突", "發生衝突，是否已解決並提交？")
        if resolve == QMessageBox.Yes:
            self.run_git_command("git add . && git commit -m '解決合併衝突'")
            QMessageBox.information(self, "合併衝突", "已解決並提交衝突。")

    def show_branch_graph(self):
        """顯示分支圖表"""
        # 取得 Git 日誌資料
        if self.os_type == "Windows":
            git_command = 'git log --all --pretty=format:"%h %p"'
        else:
            git_command = "git log --all --pretty=format:'%h %p'"
        
        output = self.run_git_command(git_command)
        if output:
            edges = []
            for line in output.split('\n'):
                parts = line.strip().split()
                if len(parts) > 1:
                    parent_hashes = parts[1:]
                    for parent in parent_hashes:
                        edges.append((parent, parts[0]))

            # 創建有向圖
            G = nx.DiGraph()
            G.add_edges_from(edges)

            pos = nx.spring_layout(G)
            plt.figure(figsize=(12, 8))
            nx.draw(G, pos, with_labels=True, node_size=800, node_color='#A4DDA4', arrowsize=20)
            plt.title("Git 分支圖表", fontsize=16)

            # 將圖表顯示在 Qt 視窗中
            graph_window = QDialog(self)
            graph_window.setWindowTitle("分支圖表")
            graph_layout = QVBoxLayout(graph_window)

            # 將 matplotlib 圖表嵌入到 Qt
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            canvas = FigureCanvas(plt.gcf())
            graph_layout.addWidget(canvas)
            graph_window.exec()

            # 清理圖表，避免重複繪製
            plt.clf()
        else:
            QMessageBox.information(self, "分支圖表", "無法取得分支圖表資料。")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitManagerApp()
    window.show()
    sys.exit(app.exec())
