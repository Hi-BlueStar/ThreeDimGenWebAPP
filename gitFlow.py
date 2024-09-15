# 匯入所需的 PySide6 和其他模組
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
    """
    一個自定義的按鈕類，支持顏色和縮放動畫效果。

    參數:
    text (str): 按鈕上顯示的文字。
    parent (QWidget, optional): 按鈕的父級窗口，默認為 None。
    """
    
    def __init__(self, text, parent=None):
        """
        AnimatedButton 類的建構函數，設置按鈕的初始狀態和動畫效果。

        參數:
        text (str): 按鈕上顯示的文字。
        parent (QWidget, optional): 按鈕的父級窗口，默認為 None。
        """
        super().__init__(text, parent)

        # 設置按鈕大小
        self.setFixedSize(160, 60)
        # 按鈕的正常顏色
        self.normal_color = QColor("#4ade80")
        # 當滑鼠懸停時的顏色
        self.hover_color = QColor("#67e8a9")
        # 當前顏色初始為正常顏色
        self.current_color = self.normal_color

        # 設置圓角按鈕樣式，並且文字顯示為白色
        self.setStyleSheet("border-radius: 20px; font-size: 14px; color: white;")

        # 為按鈕添加陰影效果
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setBlurRadius(20)  # 陰影的模糊半徑
        self.shadow_effect.setXOffset(0)      # X 軸方向的陰影偏移
        self.shadow_effect.setYOffset(5)      # Y 軸方向的陰影偏移
        self.shadow_effect.setColor(QColor("#b0bec5"))  # 陰影的顏色
        self.setGraphicsEffect(self.shadow_effect)  # 將陰影效果應用到按鈕上

        # 設置顏色動畫，該動畫將改變按鈕顏色
        self.color_animation = QPropertyAnimation(self, b"button_color")
        self.color_animation.setDuration(200)  # 動畫持續時間為 200 毫秒

        # 設置縮放動畫，當按鈕互動時會有縮放效果
        self.scale_animation = QPropertyAnimation(self, b"scale_factor")
        self.scale_animation.setDuration(100)  # 縮放動畫持續時間 100 毫秒
        self.scale_animation.setEasingCurve(QEasingCurve.OutBack)  # 使用 OutBack 緩動曲線

        self._scale_factor = 1.0  # 初始縮放因子設為 1.0 (無縮放)

    def paintEvent(self, event):
        """
        覆寫 paintEvent 方法，自定義按鈕的繪製行為，包括背景顏色和圓角效果。

        參數:
        event (QPaintEvent): 繪製事件對象。
        """
        # 創建 QPainter 用來繪製按鈕
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 開啟抗鋸齒以提高繪製質量
        rect = self.rect()  # 獲取按鈕的矩形邊界

        # 保存當前繪製狀態
        painter.save()
        # 進行縮放變換，根據 _scale_factor 對按鈕進行縮放
        painter.scale(self._scale_factor, self._scale_factor)
        # 調整按鈕的位置以使其在縮放後仍保持居中
        painter.translate(
            rect.width() * (1 - self._scale_factor) / (2 * self._scale_factor),
            rect.height() * (1 - self._scale_factor) / (2 * self._scale_factor)
        )
        # 設置按鈕背景顏色並繪製圓角矩形
        painter.setBrush(QBrush(self.current_color))
        painter.setPen(Qt.NoPen)  # 取消邊框線條
        painter.drawRoundedRect(rect, 20, 20)  # 繪製圓角矩形，圓角半徑為 20
        painter.restore()  # 恢復之前保存的狀態

        # 繼續使用 QPushButton 的預設文字繪製
        super().paintEvent(event)

    def enterEvent(self, event):
        """
        當滑鼠進入按鈕時觸發，開始顏色和縮放動畫。

        參數:
        event (QEvent): 進入事件。
        """
        # 停止之前的動畫
        self.color_animation.stop()
        # 設置動畫的開始和結束顏色
        self.color_animation.setStartValue(self.current_color)
        self.color_animation.setEndValue(self.hover_color)
        # 開始顏色動畫
        self.color_animation.start()

        # 同樣為縮放動畫設置開始和結束值
        self.scale_animation.stop()
        self.scale_animation.setStartValue(self._scale_factor)
        self.scale_animation.setEndValue(1.05)  # 進入按鈕時稍微放大
        # 開始縮放動畫
        self.scale_animation.start()

        super().enterEvent(event)  # 呼叫父類的 enterEvent 方法

    def leaveEvent(self, event):
        """
        當滑鼠離開按鈕時觸發，將按鈕顏色和縮放恢復到原狀。

        參數:
        event (QEvent): 離開事件。
        """
        # 顏色動畫恢復到正常顏色
        self.color_animation.stop()
        self.color_animation.setStartValue(self.current_color)
        self.color_animation.setEndValue(self.normal_color)
        self.color_animation.start()

        # 縮放動畫恢復到原始大小
        self.scale_animation.stop()
        self.scale_animation.setStartValue(self._scale_factor)
        self.scale_animation.setEndValue(1.0)
        self.scale_animation.start()

        super().leaveEvent(event)  # 呼叫父類的 leaveEvent 方法

    def mousePressEvent(self, event):
        """
        當按下按鈕時觸發，按鈕縮小的動畫效果。

        參數:
        event (QMouseEvent): 滑鼠按下事件。
        """
        # 按下按鈕時縮小按鈕
        self.scale_animation.stop()
        self.scale_animation.setStartValue(self._scale_factor)
        self.scale_animation.setEndValue(0.95)  # 按下時縮小到 95% 大小
        self.scale_animation.start()

        super().mousePressEvent(event)  # 呼叫父類的 mousePressEvent 方法

    def mouseReleaseEvent(self, event):
        """
        當釋放按鈕時觸發，按鈕恢復縮放效果。

        參數:
        event (QMouseEvent): 滑鼠釋放事件。
        """
        # 釋放按鈕後恢復縮放效果
        self.scale_animation.stop()
        self.scale_animation.setStartValue(self._scale_factor)
        self.scale_animation.setEndValue(1.05)  # 回到按鈕的 hover 狀態大小
        self.scale_animation.start()

        super().mouseReleaseEvent(event)  # 呼叫父類的 mouseReleaseEvent 方法

    # 使用 Property 來設置動畫顏色
    def get_button_color(self):
        """
        獲取按鈕的當前顏色。

        返回:
        return (QColor): 按鈕的當前顏色。
        """
        return self.current_color

    def set_button_color(self, color):
        """
        設置按鈕的顏色並刷新按鈕顯示。

        參數:
        color (QColor): 新的按鈕顏色。
        """
        self.current_color = color
        self.update()  # 刷新按鈕顯示

    button_color = Property(QColor, get_button_color, set_button_color)

    # 添加縮放因子屬性
    def get_scale_factor(self):
        """
        獲取當前的縮放因子。

        返回:
        return (float): 當前的縮放因子。
        """
        return self._scale_factor

    def set_scale_factor(self, factor):
        """
        設置縮放因子並更新按鈕顯示。

        參數:
        factor (float): 新的縮放因子。
        """
        self._scale_factor = factor
        self.update()  # 刷新按鈕顯示

    _scale_factor = 1.0
    scale_factor = Property(float, get_scale_factor, set_scale_factor)

class GitManagerApp(QWidget):
    """
    一個基於 Qt 的 Git 管理工具 GUI 應用程式，提供了基本的 Git 操作，如初始化倉庫、提交變更、推送到遠端、顯示分支等功能。

    參數:
    無

    返回:
    return (None): 無返回值
    """
    
    def __init__(self):
        """
        GitManagerApp 類的建構函數，初始化應用程式的 GUI 佈局及相關元件。

        參數:
        無
        """
        super().__init__()
        # 設定應用程式窗口的標題
        self.setWindowTitle("Git 流程管理工具")
        # 設定應用程式的圖標
        self.setWindowIcon(QIcon("git_icon.png"))
        # 設定窗口的背景顏色和樣式
        self.setStyleSheet("background-color: #E0F7E0; border-radius: 20px; font-size: 14px; color: black;")
        # 設定窗口的大小和位置
        self.setGeometry(100, 100, 600, 600)

        # 預設的操作系統類型，默認設置為 Windows
        self.os_type = "Windows"
        # 遠端 Git 倉庫的 URL 預設為特定的 GitHub 倉庫
        self.remote_repo = "https://github.com/Hi-BlueStar/ThreeDimGenWebAPP.git"
        # 預設的提交訊息
        self.commit_message = "提交變更"

        # 創建標題標籤，顯示應用程式的標題
        self.label = QLabel("Git 流程管理", self)
        # 設置標題標籤的樣式和字體
        self.label.setStyleSheet("font-size: 24px; color: #2C662D; font-weight: bold;")
        # 將標題標籤置於視窗中間
        self.label.setAlignment(Qt.AlignCenter)

        # 導覽說明，向用戶展示基本 Git 操作的步驟
        self.guide_label = QLabel("請依照步驟完成 Git 的基本操作：", self)
        self.guide_label.setStyleSheet("color: #2C662D;")
        self.guide_label.setAlignment(Qt.AlignCenter)

        # 顯示具體的 Git 操作步驟
        self.guide_text = QLabel("1. 初始化倉庫\n2. 創建分支或直接提交變更\n3. 推送到遠端倉庫\n4. 合併分支並解決衝突", self)
        self.guide_text.setStyleSheet("color: #2C662D;")
        self.guide_text.setAlignment(Qt.AlignCenter)

        # 操作系統選擇標籤
        self.os_label = QLabel("選擇操作系統:", self)
        self.os_label.setStyleSheet("color: #2C662D;")

        # 下拉選單供用戶選擇操作系統
        self.os_menu = QComboBox(self)
        # 將常見的操作系統選項添加到下拉選單中
        self.os_menu.addItems(["Windows", "Mac", "Linux (Ubuntu)"])
        self.os_menu.setStyleSheet("background-color: #A4DDA4; color: #2C662D;")
        # 當用戶更改選擇的操作系統時，觸發 update_os_type 方法來更新內部狀態
        self.os_menu.currentTextChanged.connect(self.update_os_type)

        # 遠端倉庫地址標籤
        self.repo_label = QLabel("遠端倉庫地址:", self)
        self.repo_label.setStyleSheet("color: #2C662D;")
        # 用於輸入或顯示遠端倉庫地址的文本框
        self.repo_entry = QLineEdit(self)
        self.repo_entry.setText(self.remote_repo)  # 預設的遠端倉庫地址
        self.repo_entry.setStyleSheet("background-color: #A4DDA4; color: #2C662D;")

        # 提交訊息標籤
        self.commit_label = QLabel("提交訊息:", self)
        self.commit_label.setStyleSheet("color: #2C662D;")
        # 用於輸入提交訊息的文本框
        self.commit_entry = QLineEdit(self)
        self.commit_entry.setText(self.commit_message)  # 預設提交訊息
        self.commit_entry.setStyleSheet("background-color: #A4DDA4; color: #2C662D;")
        
        # 創建 Grid 佈局管理器，用於排列視窗中的控件
        layout = QGridLayout()
        # 將標題和說明文本添加到佈局中，並調整它們的位置和跨度
        layout.addWidget(self.label, 0, 0, 1, 3)
        layout.addWidget(self.guide_label, 1, 0, 1, 3)
        layout.addWidget(self.guide_text, 2, 0, 1, 3)

        # 將操作系統選擇的相關控件添加到佈局中
        layout.addWidget(self.os_label, 3, 0)
        layout.addWidget(self.os_menu, 3, 1, 1, 2)

        # 將遠端倉庫地址的控件添加到佈局中
        layout.addWidget(self.repo_label, 4, 0)
        layout.addWidget(self.repo_entry, 4, 1, 1, 2)

        # 將提交訊息的控件添加到佈局中
        layout.addWidget(self.commit_label, 5, 0)
        layout.addWidget(self.commit_entry, 5, 1, 1, 2)

                # 設置功能按鈕樣式
        button_style = "background-color: #A4DDA4; color: #2C662D; padding: 10px;"

        # 初始化倉庫按鈕
        self.init_btn = AnimatedButton("初始化倉庫", self)
        self.init_btn.setStyleSheet(button_style)
        # 點擊按鈕時調用 init_repository 方法
        self.init_btn.clicked.connect(self.init_repository)
        layout.addWidget(self.init_btn, 6, 0)

        # 提交變更按鈕
        self.commit_btn = AnimatedButton("提交變更", self)
        self.commit_btn.setStyleSheet(button_style)
        # 點擊按鈕時調用 commit_changes 方法
        self.commit_btn.clicked.connect(self.commit_changes)
        layout.addWidget(self.commit_btn, 6, 1)

        # 推送至遠端按鈕
        self.push_btn = AnimatedButton("推送至遠端", self)
        self.push_btn.setStyleSheet(button_style)
        # 點擊按鈕時調用 push_changes 方法
        self.push_btn.clicked.connect(self.push_changes)
        layout.addWidget(self.push_btn, 6, 2)

        # 顯示分支按鈕
        self.branch_btn = AnimatedButton("顯示分支", self)
        self.branch_btn.setStyleSheet(button_style)
        # 點擊按鈕時調用 show_branches 方法
        self.branch_btn.clicked.connect(self.show_branches)
        layout.addWidget(self.branch_btn, 7, 0)

        # 創建新分支按鈕
        self.create_branch_btn = AnimatedButton("創建新分支", self)
        self.create_branch_btn.setStyleSheet(button_style)
        # 點擊按鈕時調用 create_branch 方法
        self.create_branch_btn.clicked.connect(self.create_branch)
        layout.addWidget(self.create_branch_btn, 7, 1)

        # 切換分支按鈕
        self.switch_branch_btn = AnimatedButton("切換分支", self)
        self.switch_branch_btn.setStyleSheet(button_style)
        # 點擊按鈕時調用 switch_branch 方法
        self.switch_branch_btn.clicked.connect(self.switch_branch)
        layout.addWidget(self.switch_branch_btn, 7, 2)

        # 合併分支按鈕
        self.merge_branch_btn = AnimatedButton("合併分支", self)
        self.merge_branch_btn.setStyleSheet(button_style)
        # 點擊按鈕時調用 merge_branch 方法
        self.merge_branch_btn.clicked.connect(self.merge_branch)
        layout.addWidget(self.merge_branch_btn, 8, 0)

        # 重命名分支按鈕
        self.rename_branch_btn = AnimatedButton("重命名分支", self)
        self.rename_branch_btn.setStyleSheet(button_style)
        # 點擊按鈕時調用 rename_branch 方法
        self.rename_branch_btn.clicked.connect(self.rename_branch)
        layout.addWidget(self.rename_branch_btn, 8, 1)

        # 刪除分支按鈕
        self.delete_branch_btn = AnimatedButton("刪除分支", self)
        self.delete_branch_btn.setStyleSheet(button_style)
        # 點擊按鈕時調用 delete_branch 方法
        self.delete_branch_btn.clicked.connect(self.delete_branch)
        layout.addWidget(self.delete_branch_btn, 8, 2)

        # 顯示分支圖表按鈕
        self.show_branch_graph_btn = AnimatedButton("顯示分支圖表", self)
        self.show_branch_graph_btn.setStyleSheet(button_style)
        # 點擊按鈕時調用 show_branch_graph 方法
        self.show_branch_graph_btn.clicked.connect(self.show_branch_graph)
        layout.addWidget(self.show_branch_graph_btn, 9, 0, 1, 3)

        # 設置佈局中的間距和邊距
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # 將設置好的佈局應用到窗口
        self.setLayout(layout)

    def update_os_type(self, os_type):
        """
        根據用戶的選擇，更新操作系統的類型。

        參數:
        os_type (str): 用戶選擇的操作系統類型。
        """
        self.os_type = os_type

    def run_git_command(self, command):
        """
        執行指定的 Git 命令，根據當前選擇的操作系統，選擇適合的 Shell。

        參數:
        command (str): 要執行的 Git 命令。

        返回:
        return (str or None): 如果命令成功執行，返回命令的輸出結果。否則，返回 None 並顯示錯誤訊息。
        """
        try:
            if self.os_type == "Windows":
                # 在 Windows 上執行命令，使用 shell=True
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
            else:
                # 在 Linux 或 MacOS 上使用 Bash 執行命令
                result = subprocess.run(command, shell=True, executable='/bin/bash', capture_output=True, text=True)

            if result.returncode == 0:
                # 如果命令執行成功，返回標準輸出
                return result.stdout.strip()
            else:
                # 如果命令失敗，拋出錯誤並顯示標準錯誤輸出
                raise Exception(result.stderr.strip())
        except Exception as e:
            # 顯示錯誤訊息
            QMessageBox.critical(self, "錯誤", f"Git 命令失敗：\n{e}")
            return None

    def init_repository(self):
        """
        初始化一個新的 Git 倉庫。

        返回:
        return (None): 無返回值，成功時顯示倉庫初始化訊息，失敗時顯示錯誤訊息。
        """
        output = self.run_git_command("git init")
        if output:
            # 如果初始化成功，顯示成功訊息
            QMessageBox.information(self, "初始化倉庫", f"成功初始化倉庫：\n{output}")

    def commit_changes(self):
        """
        提交當前工作目錄的變更，使用用戶指定的提交訊息。

        返回:
        return (None): 無返回值，成功時顯示提交訊息，失敗時顯示錯誤訊息。
        """
        output = self.run_git_command(f"git add . && git commit -m '{str(self.commit_entry.text())}'")
        if output:
            # 如果提交成功，顯示成功訊息
            QMessageBox.information(self, "提交變更", f"提交成功：\n{output}")

    def push_changes(self):
        """
        將當前分支的變更推送到遠端倉庫。

        返回:
        return (None): 無返回值，成功時顯示推送成功訊息，失敗時顯示錯誤訊息。
        """
        repo = self.repo_entry.text() if self.repo_entry.text() else "origin"
        output = self.run_git_command(f"git push {repo} master")
        if output:
            # 如果推送成功，顯示成功訊息
            QMessageBox.information(self, "推送至遠端", f"推送成功：\n{output}")

    def show_branches(self):
        """
        顯示所有本地分支。

        返回:
        return (None): 無返回值，成功時顯示分支列表，失敗時顯示錯誤訊息。
        """
        output = self.run_git_command("git branch")
        if output:
            # 顯示目前的所有分支
            QMessageBox.information(self, "顯示分支", f"目前分支：\n{output}")

    def create_branch(self):
        """
        創建一個新的 Git 分支，並自動切換到該分支。

        返回:
        return (None): 無返回值，成功時顯示新分支的訊息，失敗時顯示錯誤訊息。
        """
        # 顯示輸入對話框，讓使用者輸入新分支名稱
        branch_name, ok = QInputDialog.getText(self, "新分支名稱", "請輸入新分支名稱:")
        if ok and branch_name:
            # 執行 Git 創建新分支的命令
            output = self.run_git_command(f"git checkout -b {branch_name}")
            if output:
                # 如果成功，顯示訊息告知用戶已成功創建並切換到新分支
                QMessageBox.information(self, "創建新分支", f"成功創建並切換到新分支：\n{output}")

    def switch_branch(self):
        """
        切換到其他指定的 Git 分支。

        返回:
        return (None): 無返回值，成功時顯示切換成功訊息，失敗時顯示錯誤訊息。
        """
        # 顯示輸入對話框，讓使用者輸入要切換的分支名稱
        branch_name, ok = QInputDialog.getText(self, "切換分支", "請輸入要切換的分支名稱:")
        if ok and branch_name:
            # 執行 Git 切換分支的命令
            output = self.run_git_command(f"git checkout {branch_name}")
            if output:
                # 如果成功，顯示切換成功的訊息
                QMessageBox.information(self, "切換分支", f"成功切換到分支：\n{output}")

    def merge_branch(self):
        """
        合併指定的分支到當前所在分支。

        返回:
        return (None): 無返回值，成功時顯示合併成功訊息，遇到衝突則進行處理。
        """
        # 顯示輸入對話框，讓使用者輸入要合併的分支名稱
        branch_name, ok = QInputDialog.getText(self, "合併分支", "請輸入要合併的分支名稱:")
        if ok and branch_name:
            # 執行 Git 合併分支的命令
            output = self.run_git_command(f"git merge {branch_name}")
            if output:
                # 如果合併成功，顯示成功訊息
                QMessageBox.information(self, "合併分支", f"成功合併分支：\n{output}")
            else:
                # 如果合併發生衝突，調用處理衝突的方法
                self.handle_merge_conflict()

    def rename_branch(self):
        """
        重命名當前 Git 分支。

        返回:
        return (None): 無返回值，成功時顯示分支重命名成功訊息。
        """
        # 顯示輸入對話框，讓使用者輸入新的分支名稱
        new_branch_name, ok = QInputDialog.getText(self, "重命名分支", "請輸入新的分支名稱:")
        if ok and new_branch_name:
            # 執行 Git 分支重命名命令
            output = self.run_git_command(f"git branch -m {new_branch_name}")
            if output is not None:
                # 如果成功，顯示成功重命名訊息
                QMessageBox.information(self, "重命名分支", f"成功重命名當前分支為：{new_branch_name}")

    def delete_branch(self):
        """
        刪除指定的 Git 分支。

        返回:
        return (None): 無返回值，成功時顯示刪除成功訊息。
        """
        # 顯示輸入對話框，讓使用者輸入要刪除的分支名稱
        branch_name, ok = QInputDialog.getText(self, "刪除分支", "請輸入要刪除的分支名稱:")
        if ok and branch_name:
            # 顯示確認對話框，確保用戶確認要刪除分支
            confirm = QMessageBox.question(self, "刪除確認", f"確定要刪除分支 {branch_name} 嗎？")
            if confirm == QMessageBox.Yes:
                # 執行 Git 刪除分支的命令
                output = self.run_git_command(f"git branch -d {branch_name}")
                if output:
                    # 如果成功，顯示刪除成功的訊息
                    QMessageBox.information(self, "刪除分支", f"成功刪除分支：\n{output}")

    def handle_merge_conflict(self):
        """
        處理 Git 分支合併衝突，提示用戶手動解決衝突並提交解決。

        返回:
        return (None): 無返回值，當衝突解決後會提交衝突解決訊息。
        """
        # 顯示確認對話框，詢問用戶是否已經解決合併衝突
        resolve = QMessageBox.question(self, "合併衝突", "發生衝突，是否已解決並提交？")
        if resolve == QMessageBox.Yes:
            # 如果用戶已解決，執行提交命令
            self.run_git_command("git add . && git commit -m '解決合併衝突'")
            QMessageBox.information(self, "合併衝突", "已解決並提交衝突。")

    def show_branch_graph(self):
        """
        顯示 Git 分支的圖表，通過 NetworkX 生成分支結構圖並在視窗中顯示。

        返回:
        return (None): 無返回值，成功時顯示分支圖表，失敗時顯示錯誤訊息。
        """
        # 根據操作系統設置相應的 Git 日誌命令來取得分支圖表的數據
        if self.os_type == "Windows":
            git_command = 'git log --all --pretty=format:"%h %p"'
        else:
            git_command = "git log --all --pretty=format:'%h %p'"

        # 執行 Git 命令來獲取日誌數據
        output = self.run_git_command(git_command)
        if output:
            edges = []
            # 解析 Git 日誌的輸出，提取提交之間的關聯（邊）
            for line in output.split('\n'):
                parts = line.strip().split()
                if len(parts) > 1:
                    parent_hashes = parts[1:]
                    for parent in parent_hashes:
                        edges.append((parent, parts[0]))

            # 創建有向圖來顯示分支結構
            G = nx.DiGraph()
            G.add_edges_from(edges)

            # 使用 spring 布局來安排節點的位置
            pos = nx.spring_layout(G)
            plt.figure(figsize=(12, 8))
            # 繪製圖表，節點顯示提交哈希
            nx.draw(G, pos, with_labels=True, node_size=800, node_color='#A4DDA4', arrowsize=20)
            plt.title("Git 分支圖表", fontsize=16)

            # 創建一個新的視窗來顯示圖表
            graph_window = QDialog(self)
            graph_window.setWindowTitle("分支圖表")
            graph_layout = QVBoxLayout(graph_window)

            # 將 matplotlib 圖表嵌入到 Qt 視窗中
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            canvas = FigureCanvas(plt.gcf())
            graph_layout.addWidget(canvas)
            graph_window.exec()

            # 清理圖表，避免重複繪製
            plt.clf()
        else:
            # 如果無法獲取分支圖表數據，顯示錯誤訊息
            QMessageBox.information(self, "分支圖表", "無法取得分支圖表資料。")

if __name__ == "__main__":
    """
    主函數，應用程式的入口點。

    此部分負責創建 QApplication 實例，初始化主窗口，並啟動應用程式的事件循環。

    返回:
    return (None): 無返回值。
    """
    # 創建 QApplication 實例，該實例負責管理應用程式的控制流程
    app = QApplication(sys.argv)
    
    # 創建 GitManagerApp 主窗口實例
    window = GitManagerApp()
    # 顯示主窗口
    window.show()
    
    # 啟動應用程式的事件循環，等待用戶的互動
    sys.exit(app.exec())

