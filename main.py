import sys
import math
import signal
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import Qt, QTimer, QPoint, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

class AnalogClock(QWidget):
    def __init__(self):
        super().__init__()
        # ウィンドウタイトルの設定（枠なしでも内部的に保持）
        self.setWindowTitle("Desktop Analog Clock")
        
        # 背景を透過させ、枠を消す設定
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # 枠なし、かつ常に最前面に表示する設定
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # サイズ変更: 幅をスリムにし、高さは維持
        self.resize(300, 400)
        
        # 閉じるボタンの領域設定 (右上)
        self.close_button_rect = QRect(self.width() - 30, 10, 20, 20)

        # ウィンドウ移動用の変数
        self.oldPos = self.pos()
        self.system_move_started = False
        
        # スムーズな動きにするため、更新間隔を短くする (約60FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 閉じるボタンの範囲内かチェック
            if self.close_button_rect.contains(event.position().toPoint()):
                self.close()
                return

            self.oldPos = event.globalPosition().toPoint()
            window = self.windowHandle()
            self.system_move_started = window is not None and window.startSystemMove()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.system_move_started:
            delta = QPoint(event.globalPosition().toPoint() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # --- 1. 背景パネルの描画 (半透明ダークグレー) ---
        bg_color = QColor(40, 40, 40, 180) # RGBA: Alpha 180で半透明
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)

        # --- 閉じるボタンの描画 (右上) ---
        # ボタンの座標を現在の幅に合わせて更新
        self.close_button_rect = QRect(self.width() - 30, 10, 20, 20)

        # ホバー判定は簡易的にせず、まずは常に表示
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        # 四角でXを囲む
        painter.drawRect(self.close_button_rect)
        # Xの線 (枠から少し内側に配置)
        painter.drawLine(self.close_button_rect.left() + 3, self.close_button_rect.top() + 3,
                         self.close_button_rect.right() - 3, self.close_button_rect.bottom() - 3)
        painter.drawLine(self.close_button_rect.left() + 3, self.close_button_rect.bottom() - 3,
                         self.close_button_rect.right() - 3, self.close_button_rect.top() + 3)

        # --- 2. 色とフォントの設定 ---
        text_color = QColor(240, 240, 240)
        painter.setPen(QPen(text_color, 1))
        
        # --- 3. 年月日の表示 (上部) ---
        now = datetime.now()
        weekday_chars = ["月", "火", "水", "木", "金", "土", "日"]
        date_str = f"{now.strftime('%Y年 %m月 %d日')}({weekday_chars[now.weekday()]})"
        font_date = QFont("Helvetica", 17, QFont.Weight.Bold)
        painter.setFont(font_date)
        painter.drawText(0, 38, self.width(), 38, Qt.AlignmentFlag.AlignCenter, date_str)

        # --- 4. アナログ時計の描画 (中央) ---
        center = QPoint(self.width() // 2, self.height() // 2 + 10)
        # 直径を抑えて真円にする (高さ400から上下の余白を引いたサイズ)
        radius = 110 
        
        # 外枠
        pen_outline = QPen(text_color, 3)
        painter.setPen(pen_outline)
        painter.drawEllipse(center, radius, radius)

        # 目盛り
        pen_tick = QPen(text_color, 2)
        painter.setPen(pen_tick)
        for i in range(60):
            angle = math.radians(i * 6)
            tick_len = 8 if i % 5 == 0 else 4
            x1 = center.x() + radius * math.sin(angle)
            y1 = center.y() - radius * math.cos(angle)
            x2 = center.x() + (radius - tick_len) * math.sin(angle)
            y2 = center.y() - (radius - tick_len) * math.cos(angle)
            painter.drawLine(QPoint(int(x1), int(y1)), QPoint(int(x2), int(y2)))

        # --- スムーズな針の角度計算 ---
        # マイクロ秒まで取得して、小数単位で時間を計算する
        msec = now.microsecond / 1000000.0
        sec = now.second + msec
        minute = now.minute + sec / 60.0
        hour = (now.hour % 12) + minute / 60.0

        # 針の描画
        # 秒針 (赤色) - 1秒を6度として計算
        self.draw_hand(painter, center, radius * 0.85, sec * 6, QColor(255, 100, 100), 2)
        # 分針 (白) - 1分を6度として計算
        self.draw_hand(painter, center, radius * 0.75, minute * 6, text_color, 4)
        # 時針 (白) - 1時間を30度として計算
        self.draw_hand(painter, center, radius * 0.5, hour * 30, text_color, 6)

        # 中心点
        painter.setBrush(text_color)
        painter.drawEllipse(center, 4, 4)

        # --- 5. デジタル時刻の表示 (下部) ---
        time_str = now.strftime("%H:%M:%S")
        font_time = QFont("Consolas", 20, QFont.Weight.Bold)
        painter.setFont(font_time)
        painter.setPen(QPen(text_color, 1))
        painter.drawText(0, 330, self.width(), 40, Qt.AlignmentFlag.AlignCenter, time_str)

    def draw_hand(self, painter, center, length, angle_deg, color, width):
        pen = QPen(color, width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        angle_rad = math.radians(angle_deg)
        end_x = center.x() + length * math.sin(angle_rad)
        end_y = center.y() - length * math.cos(angle_rad)
        
        painter.drawLine(center, QPoint(int(end_x), int(end_y)))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    clock = AnalogClock()
    clock.show()

    # Ctrl-CではQtを直接終了せず、終了要求だけ記録する
    # 直接 app.quit() を呼ぶと、描画処理(paintEvent)の最中に終了し、Qtの警告が出ることがあるため
    stop_requested = [False]

    def handle_sigint(sig, frame):
        stop_requested[0] = True

    signal.signal(signal.SIGINT, handle_sigint)

    # Qtのイベント処理が一段落したところで正常終了させるための監視タイマー
    signal_timer = QTimer()

    def check_signal():
        if stop_requested[0]:
            signal_timer.stop()
            clock.close()

    signal_timer.timeout.connect(check_signal)
    signal_timer.start(100)

    sys.exit(app.exec())

