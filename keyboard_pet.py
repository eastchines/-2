import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap, QMouseEvent
from PyQt5.QtCore import Qt, QTimer
from pynput import keyboard


def get_resource_path(relative_path):
    # 1. 优先读取 exe / 脚本旁边的外部 images 文件夹（用户可自由替换图片）
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，以 exe 所在目录为基准
        external_base = os.path.dirname(sys.executable)
    else:
        # 开发环境，以脚本所在目录为基准
        external_base = os.path.dirname(os.path.abspath(__file__))

    external_path = os.path.join(external_base, relative_path)
    if os.path.exists(external_path):
        return external_path

    # 2. 兜底：使用打包进 exe 内部的内置图片（外部没放图时用默认素材）
    if hasattr(sys, '_MEIPASS'):
        bundled_path = os.path.join(sys._MEIPASS, relative_path)
        if os.path.exists(bundled_path):
            return bundled_path

    # 3. 都没有，返回外部路径并打印警告
    if not os.path.exists(external_path):
        print(f"[Warning] Missing image: {external_path}")
    return external_path


# ==================== 图片资源 ====================
GIRL_IDLE = get_resource_path("images/girl_idle.png")
GIRL_FRAMES = [
    get_resource_path("images/girl_type_01.png"),
    get_resource_path("images/girl_type_02.png"),
    get_resource_path("images/girl_type_03.png"),
    get_resource_path("images/girl_type_04.png"),
]

ANIMAL_IDLE = get_resource_path("images/animal_idle.png")
ANIMAL_FRAMES = [
    get_resource_path("images/animal_type_01.png"),
    get_resource_path("images/animal_type_02.png"),
    get_resource_path("images/animal_type_03.png"),
    get_resource_path("images/animal_type_04.png"),
]

SWITCH_FRAMES = [
    get_resource_path("images/switch_01.png"),
    get_resource_path("images/switch_02.png"),
    get_resource_path("images/switch_03.png"),
    get_resource_path("images/switch_04.png"),
]

GIRL_WALK_FRAMES = [
    get_resource_path("images/girl_walk_01.png"),
    get_resource_path("images/girl_walk_02.png"),
    get_resource_path("images/girl_walk_03.png"),
    get_resource_path("images/girl_walk_04.png"),
]

# ==================== 参数 ====================
IDLE_DELAY = 2000
SWITCH_FRAME_DELAY = 120
WALK_FRAME_DELAY = 180
TYPE_FRAME_DELAY = 90      # 按一次键后，4帧敲击动画每帧间隔（毫秒）
WALK_SPEED = 4
IDLE_TO_WALK_MS = 60000
PET_W = 360
PET_H = 360


class KeyboardPet(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint
            | Qt.FramelessWindowHint
            | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(PET_W, PET_H)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.resize(self.size())

        self.mode = "chinese"
        self.frame_idx = 0
        self.drag_pos = None
        self.is_playing_switch = False
        self.is_walking = False
        self.switch_frame_idx = 0
        self.walk_frame_idx = 0
        self.type_frame_idx = 0

        # 缩放参数
        self.scale = 1.0
        self.min_scale = 0.3
        self.max_scale = 1.3
        self.scale_step = 0.1

        # 图片加载
        self.girl_idle_img = QPixmap(GIRL_IDLE)
        self.girl_anim = [QPixmap(p) for p in GIRL_FRAMES]
        self.animal_idle_img = QPixmap(ANIMAL_IDLE)
        self.animal_anim = [QPixmap(p) for p in ANIMAL_FRAMES]
        self.switch_anim = [QPixmap(p) for p in SWITCH_FRAMES]
        self.girl_walk_anim = [QPixmap(p) for p in GIRL_WALK_FRAMES]

        # 定时器
        self.return_idle_timer = QTimer()
        self.return_idle_timer.setSingleShot(True)
        self.return_idle_timer.timeout.connect(self.set_idle)

        self.switch_timer = QTimer()
        self.switch_timer.timeout.connect(self.play_switch_frame)

        self.type_timer = QTimer()
        self.type_timer.timeout.connect(self.play_type_frame)

        self.walk_timer = QTimer()
        self.walk_timer.timeout.connect(self.update_walk)

        self.idle_to_walk_timer = QTimer()
        self.idle_to_walk_timer.setSingleShot(True)
        self.idle_to_walk_timer.timeout.connect(self.start_girl_walk)

        self.set_idle()
        self.reset_idle_to_walk_timer()
        self.show()

        self.keyboard_listener = keyboard.Listener(on_press=self.on_global_key_press)
        self.keyboard_listener.daemon = True
        self.keyboard_listener.start()

    def scale_pixmap(self, pixmap):
        base_w = self.label.width()
        base_h = self.label.height()
        scaled_w = max(1, int(base_w * self.scale))
        scaled_h = max(1, int(base_h * self.scale))
        return pixmap.scaled(scaled_w, scaled_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def set_pix(self, pixmap):
        self.label.setPixmap(self.scale_pixmap(pixmap))

    def set_idle(self):
        if self.mode == "chinese":
            self.set_pix(self.girl_idle_img)
        else:
            self.set_pix(self.animal_idle_img)
        self.frame_idx = 0

    def play_type_anim(self):
        # 按一次键盘，自动快速播完整套4帧敲击动画，再回待机
        if self.is_playing_switch:
            return
        if self.is_walking:
            self.stop_girl_walk()
        # 每次按键都从头播（打断正在播放的动画，重新开始一套完整敲击）
        self.type_frame_idx = 0
        self.type_timer.start(TYPE_FRAME_DELAY)
        self.reset_idle_to_walk_timer()

    def play_type_frame(self):
        frame_list = self.girl_anim if self.mode == "chinese" else self.animal_anim
        if self.type_frame_idx < len(frame_list):
            self.set_pix(frame_list[self.type_frame_idx])
            self.type_frame_idx += 1
        else:
            # 4帧播完，停止动画，回到待机姿势
            self.type_timer.stop()
            self.set_idle()

    def start_switch_anim(self):
        self.is_playing_switch = True
        self.switch_frame_idx = 0
        self.switch_timer.start(SWITCH_FRAME_DELAY)

    def play_switch_frame(self):
        self.set_pix(self.switch_anim[self.switch_frame_idx])
        self.switch_frame_idx += 1
        if self.switch_frame_idx >= len(self.switch_anim):
            self.switch_timer.stop()
            self.is_playing_switch = False
            self.set_idle()
            self.reset_idle_to_walk_timer()

    def switch_mode(self):
        self.mode = "english" if self.mode == "chinese" else "chinese"
        self.start_switch_anim()

    def reset_idle_to_walk_timer(self):
        self.idle_to_walk_timer.stop()
        self.idle_to_walk_timer.start(IDLE_TO_WALK_MS)

    def start_girl_walk(self):
        self.mode = "chinese"
        self.is_walking = True
        self.walk_direction = 1
        self.walk_frame_idx = 0
        screen = QApplication.primaryScreen()
        screen_geo = screen.availableGeometry()
        self.min_x = screen_geo.left()
        self.max_x = screen_geo.right() - self.width()
        self.walk_timer.start(WALK_FRAME_DELAY)

    def stop_girl_walk(self):
        self.is_walking = False
        self.walk_timer.stop()
        self.set_idle()

    def update_walk(self):
        if not self.is_walking:
            return
        self.set_pix(self.girl_walk_anim[self.walk_frame_idx])
        self.walk_frame_idx = (self.walk_frame_idx + 1) % len(self.girl_walk_anim)
        new_x = self.x() + WALK_SPEED * self.walk_direction
        if new_x <= self.min_x:
            new_x = self.min_x
            self.walk_direction = 1
        elif new_x >= self.max_x:
            new_x = self.max_x
            self.walk_direction = -1
        self.move(new_x, self.y())

    def on_global_key_press(self, key):
        try:
            if key == keyboard.Key.shift:
                self.switch_mode()
            else:
                self.play_type_anim()
        except Exception:
            pass

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale = min(self.max_scale, self.scale + self.scale_step)
        else:
            self.scale = max(self.min_scale, self.scale - self.scale_step)
        if self.is_playing_switch:
            self.set_pix(self.switch_anim[self.switch_frame_idx])
        elif self.is_walking:
            self.set_pix(self.girl_walk_anim[self.walk_frame_idx])
        else:
            self.set_idle()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            if self.is_walking:
                self.stop_girl_walk()
            self.reset_idle_to_walk_timer()
        elif event.button() == Qt.RightButton:
            self.close()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drag_pos:
            self.move(event.globalPos() - self.drag_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_pos = None
            self.reset_idle_to_walk_timer()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = KeyboardPet()
    sys.exit(app.exec_())
