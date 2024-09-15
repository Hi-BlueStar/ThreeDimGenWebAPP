import sys
from PySide6.QtCore import Qt, QRect, Property, QPropertyAnimation
from PySide6.QtWidgets import QApplication, QPushButton, QGraphicsDropShadowEffect, QMainWindow
from PySide6.QtGui import QColor, QPainter, QBrush, QPen, QFont


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
        self.shadow_effect.setXOffset(5)
        self.shadow_effect.setYOffset(5)
        self.shadow_effect.setColor(QColor("#b0bec5"))
        self.setGraphicsEffect(self.shadow_effect)
        
        # 設置動畫
        self.color_animation = QPropertyAnimation(self, b"button_color")
        self.color_animation.setDuration(200)
        
        self.scale_animation = QPropertyAnimation(self, b"geometry")
        self.scale_animation.setDuration(100)
  
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # 開啟抗鋸齒
        rect = self.rect()

        # 使用當前顏色繪製按鈕背景
        painter.setBrush(QBrush(self.current_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 20, 20)  # 設置圓角

        super().paintEvent(event)

    def enterEvent(self, event):
        self.color_animation.setStartValue(self.current_color)
        self.color_animation.setEndValue(self.hover_color)
        self.color_animation.start()

        # 放大動畫
        self.scale_animation.setStartValue(self.geometry())
        self.scale_animation.setEndValue(self.geometry().adjusted(-5, -5, 5, 5))  # 放大
        self.scale_animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):
        self.color_animation.setStartValue(self.current_color)
        self.color_animation.setEndValue(self.normal_color)
        self.color_animation.start()

        # 縮小動畫
        self.scale_animation.setStartValue(self.geometry())
        self.scale_animation.setEndValue(self.geometry().adjusted(5, 5, -5, -5))  # 恢復
        self.scale_animation.start()

        super().leaveEvent(event)

    def mousePressEvent(self, event):
        # 點擊按鈕時的縮小動畫
        self.scale_animation.setStartValue(self.geometry())
        self.scale_animation.setEndValue(self.geometry().adjusted(5, 5, -5, -5))  # 按下時縮小
        self.scale_animation.start()

        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        # 釋放按鈕時的回彈動畫
        self.scale_animation.setStartValue(self.geometry())
        self.scale_animation.setEndValue(self.geometry().adjusted(-5, -5, 5, 5))  # 回彈
        self.scale_animation.start()

        super().mouseReleaseEvent(event)

    # 使用 Property 來設置動畫顏色
    def get_button_color(self):
        return self.current_color

    def set_button_color(self, color):
        self.current_color = color
        self.update()

    button_color = Property(QColor, get_button_color, set_button_color)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modern Animated Button")
        self.setGeometry(100, 100, 400, 300)

        # 創建按鈕
        self.button = AnimatedButton("Click Me", self)
        self.button.setGeometry(120, 120, 160, 60)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
