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
        # get screen dimension
        self.screen_l = GetSystemMetrics(win32con.SM_CXSCREEN)
        self.screen_h = GetSystemMetrics(win32con.SM_CYSCREEN)
        # start keyboard monitoring
        mkey = MonitorKey()
        mkey.start()
        mkey.send_key.connect(self.get_key)
        # load UI and config UI
        self.ui = Ui_AutoFish()
        self.ui.setupUi(self)
        qp = QPalette()
        qp.setColor(QPalette.WindowText, Qt.red)
        self.ui.lcd_counter.setPalette(qp)
        self.ui.statusbar.showMessage(self.tr('Ready'))
        # get color values and original corner values
        self.red1 = self.ui.spinBox_R1.value()
        self.red2 = self.ui.spinBox_R2.value()
        self.green1 = self.ui.spinBox_G1.value()
        self.green2 = self.ui.spinBox_G2.value()
        self.blue1 = self.ui.spinBox_B1.value()
        self.blue2 = self.ui.spinBox_B2.value()
        self.height = self.ui.verticalSlider.value()
        self.width = self.ui.horizontalSlider.value()
        # initiate color set value
        self.set_color()
        # initiate snapshot rectangle coordinate
        self.set_bbox()
        # initiate fishing times counter
        self.counter = 0
        self.intl = 0
        # add 2 buttons for activating fishing and quit program
        self.button_start = self.ui.buttonBox.addButton(self.tr('Start'),
                                                        QDialogButtonBox.ActionRole)
        self.button_close = self.ui.buttonBox.addButton(QDialogButtonBox.Close)
        self.button_close.setText(self.tr('Close'))
        # get current color value and original snapshot coordinate value
        self.ui.spinBox_R1.valueChanged.connect(self.set_red1)
        self.ui.spinBox_R2.valueChanged.connect(self.set_red2)
        self.ui.spinBox_B1.valueChanged.connect(self.set_blue1)
        self.ui.spinBox_B2.valueChanged.connect(self.set_blue2)
        self.ui.spinBox_G1.valueChanged.connect(self.set_green1)
        self.ui.spinBox_G2.valueChanged.connect(self.set_green2)
        self.ui.horizontalSlider.valueChanged.connect(self.set_width)
        self.ui.verticalSlider.valueChanged.connect(self.set_height)
        # menu actions signal
        self.ui.menuHelp.triggered[QAction].connect(self.show_help)
        # buttons signal
        self.button_start.clicked.connect(self.start_fishing)
        self.button_close.clicked.connect(self.close)

    def get_key(self, key):
        # capture certain key
        # print(key)
        if key == 'Key.alt_l' or key == 'Key.alt_r':
            self.start_fishing()

    def show_help(self, action):
        # show about and help information
        if action == self.ui.actionAbout:
            QMessageBox.information(self, self.tr('About'),
                                    self.tr('Auto fishing for Minecraft\n'
                                            'made by imloafer@163.com'),
                                    QMessageBox.Close)
        else:
            pass

    def start_fishing(self):
        # activate fishing thread
        # terminate fishing thread
        txt = self.button_start.text()
        handle = win32gui.FindWindow(None, 'Minecraft')
        if handle:
            if txt == self.tr('Start'):
                self.autofish = AutoFish(self.color_set, self.bbox)
                self.autofish.start()
                self.button_start.setText(self.tr('Stop'))
                self.autofish.message.connect(self.show_message)
                self.autofish.times.connect(self.show_times)

            else:
                self.autofish.terminate()
                self.button_start.setText(self.tr('Start'))
                self.ui.statusbar.showMessage(self.tr('Stop'))
                self.intl = self.counter
        else:
            QMessageBox.warning(self, self.tr('warning'),
                                self.tr('Minecraft does not run'),
                                QMessageBox.Cancel)

    def show_message(self, message):
        # show program on-process information
        self.ui.statusbar.showMessage(message)

    def show_times(self, times):
        # show fishing times
        times += self.intl
        self.ui.lcd_counter.display(times)
        self.counter = times

    def set_width(self):
        # set new snapshot width original X
        self.width = self.ui.horizontalSlider.value()
        self.set_bbox()

    def set_height(self):
        # set new snapshot height original Y
        self.height = self.ui.verticalSlider.value()
        self.set_bbox()

    def set_red1(self):
        # set new red lower value
        self.red1 = self.ui.spinBox_R1.value()
        self.set_color()

    def set_red2(self):
        # set new red upper value
        self.red2 = self.ui.spinBox_R2.value()
        self.set_color()

    def set_blue1(self):
        # set new blue lower value
        self.blue1 = self.ui.spinBox_B1.value()
        self.set_color()

    def set_blue2(self):
        # set new blue upper value
        self.blue2 = self.ui.spinBox_B2.value()
        self.set_color()

    def set_green1(self):
        # set new green lower value
        self.green1 = self.ui.spinBox_G1.value()
        self.set_color()

    def set_green2(self):
        # set new green upper value
        self.green2 = self.ui.spinBox_G2.value()
        self.set_color()

    def set_color(self):
        # generate a color set depends on given colors
        self.color_set = {(x, y, z) for x in range(self.red1, self.red2)
                          for y in range(self.green1, self.green2)
                          for z in range(self.blue1, self.blue2)}

    def set_bbox(self):
        # get snapshot rectangle coordinate
        # grab a snapshot by giving box
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
    # fishing threading
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
            time.sleep(0.2)
            im = ImageGrab.grab(bbox=self.bbox)

            im = im.resize((128, 128))
            data_set = set(im.getdata())

            if self.color_set.intersection(data_set) == set():
                pyautogui.click(button='right')
                i += 1
                self.times.emit(i)
                self.message.emit(self.tr('fishing'))
                time.sleep(0.2)
                pyautogui.click(button='right')


class MonitorKey(QThread):
    # monitoring keyboard event threading, using pynput module to
    # capture keyboard input.
    send_key = pyqtSignal(str)

    def __init__(self):
        super(MonitorKey, self).__init__()

    def on_release(self, key):
        # capture when key released
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







