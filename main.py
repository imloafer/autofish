import sys
from PIL import ImageGrab
import json
import time
import re
from win32api import GetSystemMetrics
import win32con
import pyautogui
from pynput import keyboard
from PyQt5.QtWidgets import (QMainWindow, QApplication, QDialogButtonBox,
                             QMessageBox, QSpinBox)
from PyQt5.QtCore import (QThread, pyqtSignal, QTranslator,
                          QLocale, Qt, QTimer, QTime)
from PyQt5.QtGui import QPalette
from minecraft import Ui_AutoFish
from get_window import GetWindow
import minecraft_rc

__version__ = '0.0.6'


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

        with open('color.json', 'r') as f:
            self.color = json.load(f)
        # load UI
        self.ui = Ui_AutoFish()
        self.ui.setupUi(self)

        # set 'Minecraft' switch
        self.handle = False

        # add a timer and a time clock
        self.timer = QTimer()
        self.timeClock = QTime()
        self.timeClock.setHMS(0, 0, 0)
        self.timer.timeout.connect(self.display_time)
        qp = QPalette()
        qp.setColor(QPalette.WindowText, Qt.blue)
        self.ui.lcd_counter.setPalette(qp)
        self.ui.lcd_time.setPalette(qp)
        self.ui.statusbar.showMessage(self.tr('Ready'))

        # get color values and original corner values
        self.ui.spinBox_R1.setValue(self.color['red1'])
        self.ui.spinBox_R2.setValue(self.color['red2'])
        self.ui.spinBox_G1.setValue(self.color['green1'])
        self.ui.spinBox_G2.setValue(self.color['green2'])
        self.ui.spinBox_B1.setValue(self.color['blue1'])
        self.ui.spinBox_B2.setValue(self.color['blue2'])
        self.height = self.ui.verticalSlider.value()
        self.width = self.ui.horizontalSlider.value()

        # initiate color set value
        self.set_color()

        # initiate snapshot rectangle coordinate
        self.set_bbox()

        # initiate fishing times counter
        self.counter = 0

        # add 2 buttons for activating fishing and quit program
        self.button_start = self.ui.buttonBox.addButton(self.tr('Start'),
                                                        QDialogButtonBox.ActionRole)
        self.button_close = self.ui.buttonBox.addButton(QDialogButtonBox.Close)
        self.button_close.setText(self.tr('Close'))

        # get current color value and original snapshot coordinate value
        for child in self.ui.gBox_color.children():
            if isinstance(child, QSpinBox):
                child.valueChanged.connect(self.set_color_value)

        # get current point X, Y coordinate
        self.ui.horizontalSlider.valueChanged.connect(self.set_width)
        self.ui.verticalSlider.valueChanged.connect(self.set_height)

        # menu actions signal
        self.ui.menuHelp.triggered.connect(self.show_help)
        # buttons signal

        self.button_start.clicked.connect(self.start_fishing)
        self.button_close.clicked.connect(self.close)

    def set_color_value(self):
        self.color['red1'] = self.ui.spinBox_R1.value()
        self.color['red2'] = self.ui.spinBox_R2.value()
        self.color['green1'] = self.ui.spinBox_G1.value()
        self.color['green2'] = self.ui.spinBox_G2.value()
        self.color['blue1'] = self.ui.spinBox_B1.value()
        self.color['blue2'] = self.ui.spinBox_B2.value()
        self.set_color()
        with open('color.json', 'w+') as f:
            json.dump(self.color, f)

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
                                            + 'made by imloafer@163.com\n'
                                            + 'V: %s' % __version__),
                                    QMessageBox.Close)
        elif action == self.ui.actionHow:
            if self.ui.actionHow.isChecked():
                self.setWindowFlags(Qt.WindowStaysOnTopHint)
            else:
                self.setWindowFlags(Qt.WindowShadeButtonHint)
            self.show()

    def start_fishing(self):
        # activate fishing thread
        # terminate fishing thread
        txt = self.button_start.text()
        gw = GetWindow()
        for title in gw.title_list:
            if re.match('Minecraft', title):
                self.handle = True
        if self.handle:
            if txt == self.tr('Start'):
                self.autofish = AutoFish(self.color_set, self.bbox)
                self.autofish.start()
                self.timer.start(1000)
                self.button_start.setText(self.tr('Stop'))
                self.autofish.message.connect(self.show_message)
                self.autofish.times.connect(self.show_times)
            else:
                self.autofish.terminate()
                self.timer.stop()
                self.button_start.setText(self.tr('Start'))
                self.ui.statusbar.showMessage(self.tr('Stop'))
        else:
            QMessageBox.warning(self, self.tr('warning'),
                                self.tr('Minecraft does not run'),
                                QMessageBox.Cancel)

    def display_time(self):
        self.timeClock = self.timeClock.addMSecs(1000)
        self.ui.lcd_time.display(self.timeClock.toString("hh:mm:ss"))

    def show_message(self, message):
        # show program on-process information
        self.ui.statusbar.showMessage(message)

    def show_times(self):
        # show fishing times
        self.counter += 1
        self.ui.lcd_counter.display(self.counter)

    def set_width(self):
        # set new snapshot width original X
        self.width = self.ui.horizontalSlider.value()
        self.set_bbox()

    def set_height(self):
        # set new snapshot height original Y
        self.height = self.ui.verticalSlider.value()
        self.set_bbox()

    def set_color(self):
        # generate a color set depends on given colors
        self.color_set = {(x, y, z) for x in range(self.color['red1'],
                                                   self.color['red2'])
                          for y in range(self.color['green1'],
                                         self.color['green2'])
                          for z in range(self.color['blue1'],
                                         self.color['blue2'])}

    def set_bbox(self):
        # get snapshot rectangle coordinate
        # grab a snapshot by given box
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
    times = pyqtSignal()

    def __init__(self, color_set, bbox):
        super(AutoFish, self).__init__()
        self.color_set = color_set
        self.bbox = bbox
        self.flag = True

    def run(self):
        while self.flag:
            self.message.emit(self.tr('waiting'))
            time.sleep(0.5)
            data_set = self._grab_window()
            if self.color_set.intersection(data_set) == set():
                pyautogui.click(button='right')
                time.sleep(0.5)
                data_set1 = self._grab_window()
                if self.color_set.intersection(data_set1) == set():
                    self.times.emit()
                    self.message.emit(self.tr('fishing'))
                    pyautogui.click(button='right')

    def _grab_window(self):
        im = ImageGrab.grab(bbox=self.bbox)
        im = im.resize((128, 128))
        return set(im.getdata())


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
        # listener.join()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    TRANSLATOR = QTranslator(app)
    TRANSLATOR.load(QLocale.system().name())
    app.installTranslator(TRANSLATOR)
    window = UI()
    window.show()
    sys.exit(app.exec_())







