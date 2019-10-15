import sys
from PIL import ImageGrab
import time
from win32api import GetSystemMetrics
import win32con
import pyautogui
import win32gui
from pynput import keyboard
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDialogButtonBox,
                             QAction, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal, QTranslator, QLocale, Qt
from PyQt5.QtGui import QPalette
from minecraft import Ui_AutoFish
import minecraft_rc


class UI(QMainWindow):
    def __init__(self):

        super(UI, self).__init__()
        self.screen_l = GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_h = GetSystemMetrics(win32con.SM_CYSCREEN)
        mkey = MonitorKey()
        mkey.start()
        mkey.send_key.connect(self.get_key)
        self.ui = Ui_AutoFish()
        self.ui.setupUi(self)
        qp = QPalette()
        qp.setColor(QPalette.WindowText, Qt.red)
        self.ui.lcd_counter.setPalette(qp)
        self.ui.statusbar.showMessage(self.tr('Ready'))
        self.red1 = self.ui.spinBox_R1.value()
        self.red2 = self.ui.spinBox_R2.value()
        self.green1 = self.ui.spinBox_G1.value()
        self.green2 = self.ui.spinBox_G2.value()
        self.blue1 = self.ui.spinBox_B1.value()
        self.blue2 = self.ui.spinBox_B2.value()
        self.height = self.ui.verticalSlider.value()
        self.width = self.ui.horizontalSlider.value()
        self.set_color()
        self.set_bbox()
        self.counter = 0
        self.intl = 0

        self.button_start = self.ui.buttonBox.addButton(self.tr('Start'),
                                                        QDialogButtonBox.ActionRole)
        self.button_close = self.ui.buttonBox.addButton(QDialogButtonBox.Close)
        self.button_close.setText(self.tr('Close'))
        self.ui.spinBox_R1.valueChanged.connect(self.set_red1)
        self.ui.spinBox_R2.valueChanged.connect(self.set_red2)
        self.ui.spinBox_B1.valueChanged.connect(self.set_blue1)
        self.ui.spinBox_B2.valueChanged.connect(self.set_blue2)
        self.ui.spinBox_G1.valueChanged.connect(self.set_green1)
        self.ui.spinBox_G2.valueChanged.connect(self.set_green2)
        self.ui.horizontalSlider.valueChanged.connect(self.set_width)
        self.ui.verticalSlider.valueChanged.connect(self.set_height)
        self.ui.menuHelp.triggered[QAction].connect(self.show_help)
        self.button_start.clicked.connect(self.start_fishing)
        self.button_close.clicked.connect(self.close)

    def get_key(self, key):
        # print(key)
        if key == 'Key.alt_l' or key == 'Key.alt_r':
            self.start_fishing()

    def show_help(self, action):
        if action == self.ui.actionAbout:
            QMessageBox.information(self, self.tr('About'),
                                    self.tr('Auto fishing for Minecraft\n'
                                            'made by imloafer@163.com'),
                                    QMessageBox.Close)
        else:
            pass

    def start_fishing(self):
        txt = self.button_start.text()
        handle = win32gui.FindWindow(None, 'Minecraft')
        if handle:
            if txt == self.tr('Start'):
                self.autofish = AutoFish(self.color_set, self.bbox)
                self.button_start.setText(self.tr('Stop'))
                self.autofish.start()
                self.autofish.message.connect(self.show_message)
                self.autofish.times.connect(self.show_times)
            else:
                self.autofish.stop()
                self.button_start.setText(self.tr('Start'))
                self.autofish.message.connect(self.show_message)
                self.intl = self.counter
                self.counter = 0
        else:
            QMessageBox.warning(self, self.tr('warning'),
                                self.tr('Minecraft does not run'),
                                QMessageBox.Cancel)

    def show_message(self, message):
        self.ui.statusbar.showMessage(message)

    def show_times(self, times):
        self.counter = times + self.intl
        self.ui.lcd_counter.display(self.counter)

    def set_width(self):
        self.width = self.ui.horizontalSlider.value()
        self.set_bbox()

    def set_height(self):
        self.height = self.ui.verticalSlider.value()
        self.set_bbox()

    def set_red1(self):
        self.red1 = self.ui.spinBox_R1.value()
        self.set_color()

    def set_red2(self):
        self.red2 = self.ui.spinBox_R2.value()
        self.set_color()

    def set_blue1(self):
        self.blue1 = self.ui.spinBox_B1.value()
        self.set_color()

    def set_blue2(self):
        self.blue2 = self.ui.spinBox_B2.value()
        self.set_color()

    def set_green1(self):
        self.green1 = self.ui.spinBox_G1.value()
        self.set_color()

    def set_green2(self):
        self.green2 = self.ui.spinBox_G2.value()
        self.set_color()

    def set_color(self):
        self.color_set = {(x, y, z) for x in range(self.red1, self.red2)
                          for y in range(self.green1, self.green2)
                          for z in range(self.blue1, self.blue2)}

    def set_bbox(self):
        x_lu = int((self.screen_l - 256) * self.width/100)
        y_lu = int((self.screen_h-128) * self.height/100)
        x_rl = x_lu + 256
        y_rl = y_lu + 128
        self.bbox = (x_lu, y_lu, x_rl, y_rl)
        screen = QApplication.primaryScreen()
        screen_shot = screen.grabWindow(QApplication.desktop().winId(),
                                        x_lu, y_lu, 256, 128)
        self.ui.label_picture.setPixmap(screen_shot)


class AutoFish(QThread):
    message = pyqtSignal(str)
    times = pyqtSignal(int)

    def __init__(self, color_set, bbox):
        super(AutoFish, self).__init__()
        self.color_set = color_set
        self.bbox = bbox
        self.flag = True

    def run(self):
        i = 0
        while self.flag:
            self.message.emit(self.tr('waiting'))
            time.sleep(0.5)
            im1 = ImageGrab.grab(bbox=self.bbox)

            im1 = im1.resize((128, 128))
            data_set = set(im1.getdata())

            if self.color_set.intersection(data_set) == set():
                pyautogui.click(button='right')
                i += 1
                self.message.emit(self.tr('fishing'))
                self.times.emit(i)
                time.sleep(0.5)
                pyautogui.click(button='right')

    def stop(self):
        self.flag = False
        self.message.emit(self.tr('Stop'))


class MonitorKey(QThread):
    # monitoring keyboard event threading, using pynput module to
    # capture keyboard input.
    send_key = pyqtSignal(str)

    def __init__(self):
        super(MonitorKey, self).__init__()

    def on_release(self, key):
        try:
            self.send_key.emit(key.char)
        except AttributeError:
            self.send_key.emit(str(key))

    def run(self):

        listener = keyboard.Listener(on_press=self.on_release)
        listener.start()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    TRANSLATOR = QTranslator(app)
    TRANSLATOR.load(QLocale.system().name())
    app.installTranslator(TRANSLATOR)
    window = UI()
    window.show()
    sys.exit(app.exec_())







