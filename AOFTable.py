import win32gui, pyautogui
from utils_table import squeeze_name
import cv2

class AOFTable:
    def __init__(self, name, hwnd):
        self.name = name
        self.short_name = squeeze_name(name)
        self.hwnd = hwnd
        self.coordinates = win32gui.GetWindowRect(hwnd)
        self.cor_x_high, self.cor_y_high, self.cor_x_low, self.cor_y_low = self.coordinates
        self.x_size = self.cor_x_low - self.cor_x_high
        self.y_size = self.cor_y_low - self.cor_y_high

    def get_name(self):
        return self.name

    def get_hwnd(self):
        return self.hwnd

    def fg_table(self):
        win32gui.SetForegroundWindow(self.hwnd)

    def is_table_visible(self):
        return win32gui.IsWindowVisible(self.hwnd)

    def screen_shot(self):
        self.fg_table()
        raw_screenshot_str = "./pictures/Running/" + self.short_name + "_" + "_raw.png"
        pyautogui.screenshot(raw_screenshot_str)
        im = cv2.imread(raw_screenshot_str, 0)
        #im = im[self.cor_y_high:self.cor_y_low, self.cor_x_high:self.cor_x_low]
        #os.remove(raw_screenshot_str)
        #self.screen_shot = im[:]



    def __str__(self):
        table_str = "*"*10 + " " + self.name + " " + "*"*10 + "\n"
        table_str += "*"*5 + " Coordinates: " + str(self.coordinates) + "\n"
        return table_str

