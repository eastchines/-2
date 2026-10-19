import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
from pynput import keyboard

# ===================== 配置参数 =====================
TYPE_FRAME_DELAY = 90  # 动画帧间隔(ms)，数值越大动画越慢
IDLE_IMG = "girl_idle.png"
TYPE_FRAMES = [
    "girl_type_01.png",
    "girl_type_02.png",
    "girl_type_03.png",
    "girl_type_04.png"
]
PET_WIDTH = 360
PET_HEIGHT = 360
# ====================================================

def get_img_path(filename):
    """仅读取exe外部images文件夹，无内置兜底图片"""
    if hasattr(sys, 'executable') and os.path.basename(sys.executable).lower() != "python.exe":
        # 打包exe运行模式
        base_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        # 本地python调试运行模式
        base_dir = os.path.dirname(os.path.abspath(__file__))

    img_full_path = os.path.join(base_dir, "images", filename)
    if not os.path.exists(img_full_path):
        QMessageBox.critical(None, "素材缺失",
            f"找不到图片：\n{img_full_path}\n\n请将images文件夹放在exe同目录！")
        sys.exit(1)
    return img_full_path

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        # 动画状态
        self.is_animating = False
        self.anim_index = 0
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.next_anim_frame)
        self.anim_timer.setInterval(TYPE_FRAME_DELAY)

        # 全局键盘监听
        self.key_listener = keyboard.Listener(on_press=self.on_key_press)
        self.key_listener.start()

    def initUI(self):
        # 无边框、置顶、透明背景
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(PET_WIDTH, PET_HEIGHT)

        self.label = QLabel(self)
        self.label.resize(PET_WIDTH, PET_HEIGHT)
        # 加载待机图
        self.set_image(get_img_path(IDLE_IMG))

        # 拖动变量
        self.drag_flag = False
        self.drag_pos = None

    def set_image(self, path):
        pix = QPixmap(path)
        self.label.setPixmap(pix)
        self.label.setScaledContents(True)

    def on_key_press(self, key):
        # 按键触发动画，如果动画正在播放则忽略新按键
        if not self.is_animating:
            self.start_type_animation()

    def start_type_animation(self):
        self.is_animating = True
        self.anim_index = 0
        self.anim_timer.start()

    def next_anim_frame(self):
        if self.anim_index < len(TYPE_FRAMES):
            img_path = get_img_path(TYPE_FRAMES[self.anim_index])
            self.set_image(img_path)
            self.anim_index += 1
        else:
            # 动画播放完毕，切回待机图
            self.anim_timer.stop()
            self.is_animating = False
            self.set_image(get_img_path(IDLE_IMG))

    # 拖动窗口
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_flag = True
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            # 右键关闭宠物
            self.close()

    def mouseMoveEvent(self, event):
        if self.drag_flag:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_flag = False

    def closeEvent(self, event):
        # 关闭时停止键盘监听
        self.key_listener.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec_())
