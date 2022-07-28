import win32gui
import pyautogui
import os
import cv2
from utils_table import *
from Enums import Location
from CNN_utils import classify_image


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
        self.curr_dealer_location = None
        self.curr_sb_location = None
        self.curr_bb_location = None

        self.hands_counter = 0

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
            path = "./pictures/Running/" + self.short_name + "_" + name + "_" + str(self.hands_counter) + ".png"
            cv2.imwrite(path, im)

        return im

    def update_hand_counter(self):
        self.hands_counter += 1

    def screen_shot(self):
        self.fg_table()
        raw_screenshot_str = "./pictures/Running/" + self.short_name + "_" + str(self.hands_counter) + "_raw.png"
        clear_screenshot_str = "./pictures/Running/" + self.short_name + "_" + str(self.hands_counter) + ".png"
        pyautogui.screenshot(raw_screenshot_str)
        im = cv2.imread(raw_screenshot_str, 0)
        im = im[self.cor_y_high:self.cor_y_low, self.cor_x_high:self.cor_x_low]
        os.remove(raw_screenshot_str)

        cv2.imwrite(clear_screenshot_str, im)

        self.curr_screen_shot = im[:]

    def find_blinds_location(self, blinds_model, device, save=False):
        blinds_top = blinds_right = blinds_left = blinds_bottom = 0

        while blinds_top + blinds_right + blinds_left + blinds_bottom != 4:
            blinds_top = self.zoom_in(name='blinds_top', cor_x=int(self.x_size * blinds_top_x_cor_rel),
                                      cor_y=int(self.y_size * blinds_top_y_cor_rel),
                                      size_y=int(self.y_size * blinds_y_size_rel),
                                      size_x=int(self.x_size * blinds_x_size_rel), save=save)

            blinds_right = self.zoom_in(name='blinds_right', cor_x=int(self.x_size * blinds_right_x_cor_rel),
                                        cor_y=int(self.y_size * blinds_right_y_cor_rel),
                                        size_y=int(self.y_size * blinds_y_size_rel),
                                        size_x=int(self.x_size * blinds_x_size_rel), save=save)

            blinds_left = self.zoom_in(name='blinds_left', cor_x=int(self.x_size * blinds_left_x_cor_rel),
                                       cor_y=int(self.y_size * blinds_left_y_cor_rel),
                                       size_y=int(self.y_size * blinds_y_size_rel),
                                       size_x=int(self.x_size * blinds_x_size_rel), save=save)

            blinds_bottom = self.zoom_in(name='blinds_bottom', cor_x=int(self.x_size * blinds_bottom_x_cor_rel),
                                         cor_y=int(self.y_size * blinds_bottom_y_cor_rel),
                                         size_y=int(self.y_size * blinds_y_size_rel),
                                         size_x=int(self.x_size * blinds_x_size_rel), save=save)

            # BB = 0, SB = 2
            blinds_top = classify_image(model=blinds_model, im=blinds_top, device=device, resize=(16, 16))
            blinds_right = classify_image(model=blinds_model, im=blinds_right, device=device, resize=(16, 16))
            blinds_left = classify_image(model=blinds_model, im=blinds_left, device=device, resize=(16, 16))
            blinds_bottom = classify_image(model=blinds_model, im=blinds_bottom, device=device, resize=(16, 16))
            print(blinds_top, blinds_left, blinds_right, blinds_bottom)


        if blinds_top == 0:
            self.curr_bb_location = Location.Top
        if blinds_top == 2:
            self.curr_sb_location = Location.Top

        if blinds_right == 0:
            self.curr_bb_location = Location.Right
        if blinds_right == 2:
            self.curr_sb_location = Location.Right

        if blinds_left == 0:
            self.curr_bb_location = Location.Left
        if blinds_left == 2:
            self.curr_sb_location = Location.Left

        if blinds_bottom == 0:
            self.curr_bb_location = Location.Bottom
        if blinds_bottom == 2:
            self.curr_sb_location = Location.Bottom

    def find_button_location(self, dealer_model, device, save=False):
        dealer_top = self.zoom_in(name='dealer_top', cor_x=int(self.x_size * button_top_x_cor_rel),
                     cor_y=int(self.y_size * button_top_y_cor_rel),
                     size_y=int(self.y_size * button_y_size_rel),
                     size_x=int(self.x_size * button_x_size_rel), save=save)

        dealer_right = self.zoom_in(name='dealer_right', cor_x=int(self.x_size * button_right_x_cor_rel),
                     cor_y=int(self.y_size * button_right_y_cor_rel),
                     size_y=int(self.y_size * button_y_size_rel),
                     size_x=int(self.x_size * button_x_size_rel), save=save)

        dealer_left = self.zoom_in(name='dealer_left', cor_x=int(self.x_size * button_left_x_cor_rel),
                     cor_y=int(self.y_size * button_left_y_cor_rel),
                     size_y=int(self.y_size * button_y_size_rel),
                     size_x=int(self.x_size * button_x_size_rel), save=save)

        dealer_bottom = self.zoom_in(name='dealer_bottom', cor_x=int(self.x_size * button_bottom_x_cor_rel),
                     cor_y=int(self.y_size * button_bottom_y_cor_rel),
                     size_y=int(self.y_size * button_y_size_rel),
                     size_x=int(self.x_size * button_x_size_rel), save=save)

        prev = self.curr_dealer_location

        if classify_image(model=dealer_model, im=dealer_top, device=device, resize=(16, 16)):
            self.curr_dealer_location = Location.Top

        if classify_image(model=dealer_model, im=dealer_right, device=device, resize=(16, 16)):
            self.curr_dealer_location = Location.Right

        if classify_image(model=dealer_model, im=dealer_left, device=device, resize=(16, 16)):
            self.curr_dealer_location = Location.Left

        if classify_image(model=dealer_model, im=dealer_bottom, device=device, resize=(16, 16)):
            self.curr_dealer_location = Location.Bottom

        if prev != self.curr_dealer_location:
            return True
        return False

    def __str__(self):
        table_str = "*"*10 + " " + self.name + " " + "*"*10 + "\n"
        table_str += "*"*5 + " Coordinates: " + str(self.coordinates) + "\n"
        table_str += "*" * 5 + " # Hand: " + str(self.hands_counter) + "\n"
        table_str += "*"*5 + " Dealer Location: " + str(self.curr_dealer_location) + "\n"
        table_str += "*" * 5 + " SB Location: " + str(self.curr_sb_location) + "\n"
        table_str += "*" * 5 + " BB Location: " + str(self.curr_bb_location) + "\n"
        return table_str

