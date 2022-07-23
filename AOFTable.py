import win32gui, pyautogui, os, cv2
from utils_table import squeeze_name
from utils_table import button_top_x_cor_rel, button_top_y_cor_rel, button_right_y_cor_rel, button_right_x_cor_rel, button_left_x_cor_rel, button_left_y_cor_rel, \
    button_x_size_rel, button_y_size_rel, button_bottom_x_cor_rel, button_bottom_y_cor_rel


class AOFTable:
    def __init__(self, name, hwnd):
        self.name = name
        self.short_name = squeeze_name(name)
        self.hwnd = hwnd
        self.coordinates = win32gui.GetWindowRect(hwnd)
        self.cor_x_high, self.cor_y_high, self.cor_x_low, self.cor_y_low = self.coordinates
        self.x_size = self.cor_x_low - self.cor_x_high
        self.y_size = self.cor_y_low - self.cor_y_high
        self.curr_screen_shot = None
        self.curr_hand_num = 0

    def get_name(self):
        return self.name

    def get_hwnd(self):
        return self.hwnd

    def fg_table(self):
        win32gui.SetForegroundWindow(self.hwnd)

    def is_table_visible(self):
        return win32gui.IsWindowVisible(self.hwnd)

    def zoom_in(self, name, cor_x, size_x, cor_y, size_y, save=False):

        im = self.curr_screen_shot[cor_y:cor_y + size_y, cor_x:cor_x + size_x]
        if save:
            path = "./pictures/Running/" + self.short_name + "_" + name + "_" + str(self.curr_hand_num) + ".png"
            cv2.imwrite(path, im)

        return im

    def screen_shot(self):
        self.fg_table()
        raw_screenshot_str = "./pictures/Running/" + self.short_name + "_" + str(self.curr_hand_num) + "_raw.png"
        clear_screenshot_str = "./pictures/Running/" + self.short_name + "_" + str(self.curr_hand_num) + ".png"
        pyautogui.screenshot(raw_screenshot_str)
        im = cv2.imread(raw_screenshot_str, 0)
        im = im[self.cor_y_high:self.cor_y_low, self.cor_x_high:self.cor_x_low]
        os.remove(raw_screenshot_str)

        cv2.imwrite(clear_screenshot_str, im)

        self.curr_screen_shot = im[:]
        self.curr_hand_num += 1

    def find_button_location(self):
        self.zoom_in(name='dealer_top', cor_x=int(self.x_size * button_top_x_cor_rel),
                     cor_y=int(self.y_size * button_top_y_cor_rel),
                     size_y=int(self.y_size * button_y_size_rel),
                     size_x=int(self.x_size * button_x_size_rel), save=True)

        self.zoom_in(name='dealer_right', cor_x=int(self.x_size * button_right_x_cor_rel),
                     cor_y=int(self.y_size * button_right_y_cor_rel),
                     size_y=int(self.y_size * button_y_size_rel),
                     size_x=int(self.x_size * button_x_size_rel), save=True)

        self.zoom_in(name='dealer_left', cor_x=int(self.x_size * button_left_x_cor_rel),
                     cor_y=int(self.y_size * button_left_y_cor_rel),
                     size_y=int(self.y_size * button_y_size_rel),
                     size_x=int(self.x_size * button_x_size_rel), save=True)

        self.zoom_in(name='dealer_bottom', cor_x=int(self.x_size * button_bottom_x_cor_rel),
                     cor_y=int(self.y_size * button_bottom_y_cor_rel),
                     size_y=int(self.y_size * button_y_size_rel),
                     size_x=int(self.x_size * button_x_size_rel), save=True)

    def __str__(self):
        table_str = "*"*10 + " " + self.name + " " + "*"*10 + "\n"
        table_str += "*"*5 + " Coordinates: " + str(self.coordinates) + "\n"
        return table_str

