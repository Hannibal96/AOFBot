import win32gui
import pyautogui
import os
import cv2
from utils_table import *
from Enums import Location, Position
from CNN_utils import classify_image, blinds_resize, dealer_resize


class AOFTable:
    def __init__(self, name, hwnd, dealer_model, blinds_model, device):
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

        self.curr_location_position_mapping = {}
        for location in Location:
            self.curr_location_position_mapping[location] = Position.SittingOut

        self.valid = False

        self.hands_counter = 0

        self.dealer_model = dealer_model
        self.blinds_model = blinds_model
        self.device = device

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

    def find_blinds_location(self, save=False):
        blinds_top = blinds_right = blinds_left = blinds_bottom = 0
        s = set([blinds_right, blinds_top, blinds_left, blinds_bottom])

        counter = 0
        while not (0 in s and 1 in s and 2 in s):
            self.screen_shot()

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

            blinds_top = classify_image(model=self.blinds_model, im=blinds_top, device=self.device, resize=blinds_resize)
            blinds_right = classify_image(model=self.blinds_model, im=blinds_right, device=self.device, resize=blinds_resize)
            blinds_left = classify_image(model=self.blinds_model, im=blinds_left, device=self.device, resize=blinds_resize)
            blinds_bottom = classify_image(model=self.blinds_model, im=blinds_bottom, device=self.device, resize=blinds_resize)

            s = set([blinds_right, blinds_top, blinds_left, blinds_bottom])

            counter += 1
            if counter == 2:
                self.valid = False
                break

            self.valid = True

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

    def find_button_location(self, save=False):
        prev = self.curr_dealer_location
        dealer_top = dealer_right = dealer_left = dealer_bottom = 0

        while dealer_top+dealer_left+dealer_bottom+dealer_right != 1:
            self.screen_shot()

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

            dealer_top = classify_image(model=self.dealer_model, im=dealer_top, device=self.device, resize=dealer_resize)
            dealer_right = classify_image(model=self.dealer_model, im=dealer_right, device=self.device, resize=dealer_resize)
            dealer_left = classify_image(model=self.dealer_model, im=dealer_left, device=self.device, resize=dealer_resize)
            dealer_bottom = classify_image(model=self.dealer_model, im=dealer_bottom, device=self.device, resize=dealer_resize)

            if dealer_top:
                self.curr_dealer_location = Location.Top

            if dealer_right:
                self.curr_dealer_location = Location.Right

            if dealer_left:
                self.curr_dealer_location = Location.Left

            if dealer_bottom:
                self.curr_dealer_location = Location.Bottom

        if prev != self.curr_dealer_location:
            return True
        return False

    def figure_table_structure(self):
        if not self.valid:
            return

        self.curr_location_position_mapping[self.curr_dealer_location] = Position.Dealer
        self.curr_location_position_mapping[self.curr_sb_location] = Position.SmallBlind
        self.curr_location_position_mapping[self.curr_bb_location] = Position.BigBlind

        # classic case no jumps in the order of blinds and button
        if self.curr_dealer_location.value == (self.curr_sb_location.value - 1) % 4 == \
                (self.curr_bb_location.value - 2) % 4:
            remain_location = Location(TOTAL_SUM_OF_LOCATIONS - self.curr_bb_location.value -
                                       self.curr_sb_location.value - self.curr_dealer_location.value)
            self.curr_location_position_mapping[remain_location] = Position.CutOff

        # one sitting out in the middle, not cutoff
        elif (self.curr_dealer_location.value == (self.curr_sb_location.value - 1) % 4 ==
                (self.curr_bb_location.value - 3) % 4) or \
                (self.curr_dealer_location.value == (self.curr_sb_location.value - 2) % 4 ==
                 (self.curr_bb_location.value - 3) % 4):
            remain_location = Location(TOTAL_SUM_OF_LOCATIONS - self.curr_bb_location.value -
                                       self.curr_sb_location.value - self.curr_dealer_location.value)
            self.curr_location_position_mapping[remain_location] = Position.SittingOut

        # two players sitting out
        elif self.curr_dealer_location == self.curr_sb_location:

            if (self.curr_bb_location.value - 1) % 4 == self.curr_dealer_location.value:
                self.curr_location_position_mapping[Location((self.curr_bb_location.value + 1) % 4)] = Position.SittingOut
                self.curr_location_position_mapping[Location((self.curr_bb_location.value + 2) % 4)] = Position.SittingOut

            elif (self.curr_bb_location.value - 2) % 4 == self.curr_dealer_location.value:
                self.curr_location_position_mapping[Location((self.curr_bb_location.value + 1) % 4)] = Position.SittingOut
                self.curr_location_position_mapping[Location((self.curr_bb_location.value - 1) % 4)] = Position.SittingOut

            elif (self.curr_bb_location.value + 1) % 4 == self.curr_dealer_location.value:
                self.curr_location_position_mapping[Location((self.curr_bb_location.value + 2) % 4)] = Position.SittingOut
                self.curr_location_position_mapping[Location((self.curr_bb_location.value - 1) % 4)] = Position.SittingOut

            else:
                assert False, "-E- impossible table structure"

    def __str__(self):
        table_str = "*"*10 + " " + self.name + " " + "*"*10 + "\n"
        table_str += "*"*5 + " Coordinates: " + str(self.coordinates) + "\n"
        table_str += "*" * 5 + " # Hand: " + str(self.hands_counter) + "\n"
        table_str += "*"*5 + " Dealer Location: " + str(self.curr_dealer_location) + "\n"
        table_str += "*" * 5 + " SB Location: " + str(self.curr_sb_location) + "\n"
        table_str += "*" * 5 + " BB Location: " + str(self.curr_bb_location) + "\n"

        for location in Location:
            table_str += "*" * 5 + " " + str(location) + ': ' + str(self.curr_location_position_mapping[location]) + "\n"

        return table_str

