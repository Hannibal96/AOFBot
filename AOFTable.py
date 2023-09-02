import win32gui
import pyautogui
import os
import cv2
from utils_table import *
from Enums import *
from CNN_utils import *
from Card import Card
from Strategy import  *


class AOFTable:
    def __init__(self, name, hwnd, dealer_model, blinds_model, action_model, value_model, suit_model, device):
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
        self.curr_all_ins = []

        self.curr_location_position_mapping = {}
        for location in Location:
            self.curr_location_position_mapping[location] = Position.SittingOut

        self.left_card = None
        self.right_card = None

        self.curr_state = None

        self.valid = False

        self.hands_counter = 0

        self.dealer_model = dealer_model
        self.blinds_model = blinds_model
        self.action_model = action_model
        self.value_model = value_model
        self.suit_model = suit_model

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
        res = [blinds_top, blinds_right, blinds_bottom, blinds_left]

        self.curr_sb_location = None
        self.curr_bb_location = None
        self.curr_all_ins = []

        while True:
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

            if res == [blinds_top, blinds_right, blinds_bottom, blinds_left]:
                break
            else:
                res = [blinds_top, blinds_right, blinds_bottom, blinds_left]

        blinds_top = blinds_label_converter[blinds_top]
        blinds_right = blinds_label_converter[blinds_right]
        blinds_left = blinds_label_converter[blinds_left]
        blinds_bottom = blinds_label_converter[blinds_bottom]

        if blinds_top == Position.BigBlind:
            self.curr_bb_location = Location.Top
        elif blinds_right == Position.BigBlind:
            self.curr_bb_location = Location.Right
        elif blinds_left == Position.BigBlind:
            self.curr_bb_location = Location.Left
        elif blinds_bottom == Position.BigBlind:
            self.curr_bb_location = Location.Bottom
        else:
            assert False, "-E- Didn't recognize BB"

        if blinds_top == Position.SmallBlind:
            self.curr_sb_location = Location.Top
        elif blinds_right == Position.SmallBlind:
            self.curr_sb_location = Location.Right
        elif blinds_left == Position.SmallBlind:
            self.curr_sb_location = Location.Left
        elif blinds_bottom == Position.SmallBlind:
            self.curr_sb_location = Location.Bottom

        if blinds_top == Action.AllIn:
            self.curr_all_ins.append(Location.Top)
        if blinds_right == Action.AllIn:
            self.curr_all_ins.append(Location.Right)
        if blinds_left == Action.AllIn:
            self.curr_all_ins.append(Location.Left)
        if blinds_bottom == Action.AllIn:
            self.curr_all_ins.append(Location.Bottom)

        if self.curr_bb_location in self.curr_all_ins:
            assert False, "-E- Allin in BB"

    def find_button_location(self, save=False):
        prev = self.curr_dealer_location
        dealer_top = dealer_right = dealer_left = dealer_bottom = 0

        while True:
            res = [dealer_top, dealer_right, dealer_bottom, dealer_left]
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
            if res == [dealer_top, dealer_right, dealer_bottom, dealer_left]:
                break

        if dealer_top:
            self.curr_dealer_location = Location.Top

        elif dealer_right:
            self.curr_dealer_location = Location.Right

        elif dealer_left:
            self.curr_dealer_location = Location.Left

        elif dealer_bottom:
            self.curr_dealer_location = Location.Bottom

        #else:
        #    assert False, "-E- Didn't recognize Button"

        if prev != self.curr_dealer_location:
            return True
        return False

    def figure_table_structure(self):

        print("*" * 10)
        print("*" * 10)
        print("*" * 10)
        print(f"DE: {self.curr_dealer_location.value}")
        print(f"SB: {self.curr_sb_location.value if self.curr_sb_location is not None else self.curr_sb_location}")
        print(f"BB: {self.curr_bb_location.value}")
        print(f"{self.curr_all_ins}")
        print("*" * 10)
        print("*" * 10)
        print("*" * 10)

        self.curr_location_position_mapping[self.curr_dealer_location] = Position.Dealer
        self.curr_location_position_mapping[self.curr_bb_location] = Position.BigBlind

        if (self.curr_dealer_location.value == (self.curr_bb_location.value - 2) % 4) and ((self.curr_sb_location is None and Location((self.curr_bb_location.value - 1) % 4) in self.curr_all_ins) or (
                self.curr_sb_location is not None and self.curr_sb_location.value == (self.curr_bb_location.value - 1) % 4)):
            print(" 4 Players case")
            self.curr_location_position_mapping[Location((self.curr_bb_location.value - 1) % 4)] = Position.SmallBlind
            self.curr_location_position_mapping[Location((self.curr_bb_location.value - 3) % 4)] = Position.CutOff

        # one sitting out in the middle, not cutoff
        elif self.curr_dealer_location.value == (self.curr_bb_location.value - 3) % 4 and (
                (self.curr_sb_location is not None and self.curr_sb_location != self.curr_dealer_location) or any(ai_loc != self.curr_dealer_location for ai_loc in self.curr_all_ins)):
            print(" 3 Players case")
            if self.curr_sb_location is None:
                if Location((self.curr_bb_location.value - 1) % 4) in self.curr_all_ins:
                    self.curr_location_position_mapping[Location((self.curr_bb_location.value - 1) % 4)] = Position.SmallBlind
                    self.curr_location_position_mapping[Location((self.curr_bb_location.value - 2) % 4)] = Position.SittingOut

                elif Location((self.curr_bb_location.value - 2) % 4) in self.curr_all_ins:
                    self.curr_location_position_mapping[Location((self.curr_bb_location.value - 1) % 4)] = Position.SittingOut
                    self.curr_location_position_mapping[Location((self.curr_bb_location.value - 2) % 4)] = Position.SmallBlind

                else:
                    assert False, "-E- impossible table structure"

            else:
                remaining_loc = TOTAL_SUM_OF_LOCATIONS - self.curr_sb_location.value - self.curr_bb_location.value - self.curr_dealer_location.value
                remaining_loc = Location(remaining_loc)
                self.curr_location_position_mapping[remaining_loc] = Position.SittingOut
                self.curr_location_position_mapping[self.curr_sb_location] = Position.SmallBlind

        # two players sitting out

        elif self.curr_sb_location is not None and self.curr_sb_location == self.curr_dealer_location:
            print(" 2 Players case I")
            for location in Location:
                if location not in [self.curr_bb_location, self.curr_dealer_location]:
                    self.curr_location_position_mapping[location] = Position.SittingOut

        elif self.curr_sb_location is None and self.curr_dealer_location in self.curr_all_ins:
            print(" 2 Players case II")
            for location in Location:
                if location not in [self.curr_bb_location, self.curr_dealer_location]:
                    assert location not in self.curr_all_ins, "-E- impossible table structure"

        else:
            assert False, "-E- impossible table structure"

    def _figure_state(self):

        if self.curr_location_position_mapping[Location.Bottom] == Position.CutOff:
            assert len(self.curr_all_ins) == 0
            return State.CO

        if self.curr_location_position_mapping[Location.Bottom] == Position.Dealer:
            assert len(self.curr_all_ins) <= 1
            if len(self.curr_all_ins) == 1:
                assert self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.CutOff
                return State.DE_CO
            else:
                return State.DE

        if self.curr_location_position_mapping[Location.Bottom] == Position.SmallBlind:
            assert len(self.curr_all_ins) <= 2
            if len(self.curr_all_ins) == 0:
                return State.SB
            if len(self.curr_all_ins) == 1:
                if self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.CutOff:
                    return State.SB_CO
                if self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.Dealer:
                    return State.SB_CO
            if len(self.curr_all_ins) == 2:
                assert self.curr_location_position_mapping[self.curr_all_ins[0]] in [Position.CutOff, Position.Dealer]
                assert self.curr_location_position_mapping[self.curr_all_ins[1]] in [Position.CutOff, Position.Dealer]
                return State.SB_CO_DE

        if self.curr_location_position_mapping[Location.Bottom] == Position.BigBlind:
            assert len(self.curr_all_ins) >= 1
            if len(self.curr_all_ins) == 1:
                if self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.CutOff:
                    return State.BB_CO
                if self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.Dealer:
                    return State.BB_DE
                if self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.SmallBlind:
                    return State.BB_SB
            if len(self.curr_all_ins) == 3:
                return State.BB_CO_DE_SB
            if len(self.curr_all_ins) == 2:
                if not Position.CutOff in [self.curr_location_position_mapping[self.curr_all_ins[0]], self.curr_location_position_mapping[self.curr_all_ins[1]]]:
                    return State.BB_DE_SB
                if not Position.Dealer in [self.curr_location_position_mapping[self.curr_all_ins[0]], self.curr_location_position_mapping[self.curr_all_ins[1]]]:
                    return State.BB_CO_SB
                if not Position.SmallBlind in [self.curr_location_position_mapping[self.curr_all_ins[0]], self.curr_location_position_mapping[self.curr_all_ins[1]]]:
                    return State.BB_CO_DE
            assert False

        assert False

    def figure_state(self):
        self.curr_state = self._figure_state()

    def is_my_turn(self, save=False):
        self.screen_shot()
        action = self.zoom_in(name='action', cor_x=int(self.x_size * action_x_cor_rel),
                              cor_y=int(self.y_size * action_y_cor_rel),
                              size_y=int(self.y_size * action_y_size_rel),
                              size_x=int(self.x_size * action_x_size_rel), save=save)

        return classify_image(model=self.action_model, im=action, device=self.device, resize=action_resize)

    def read_holding_cards(self, save=False):
        left_card = self.zoom_in(name='bottom_left_card',
                                 cor_x=int(self.x_size * holding_cards_bottom_left_x_cor_rel),
                                 cor_y=int(self.y_size * holding_cards_bottom_left_y_cor_rel),
                                 size_y=int(self.y_size * card_y_size_rel),
                                 size_x=int(self.x_size * card_x_size_rel), save=save)

        right_card = self.zoom_in(name='bottom_right_card',
                                 cor_x=int(self.x_size * holding_cards_bottom_right_x_cor_rel),
                                 cor_y=int(self.y_size * holding_cards_bottom_right_y_cor_rel),
                                 size_y=int(self.y_size * card_y_size_rel),
                                 size_x=int(self.x_size * card_x_size_rel), save=save)

        left_suit = classify_image(model=self.suit_model, im=left_card, device=self.device, resize=suit_resize)
        left_value = classify_image(model=self.value_model, im=left_card, device=self.device, resize=value_resize)
        left_suit = suit_label_converter[left_suit]
        left_value = value_label_converter[left_value]

        right_suit = classify_image(model=self.suit_model, im=right_card, device=self.device, resize=suit_resize)
        right_value = classify_image(model=self.value_model, im=right_card, device=self.device, resize=value_resize)
        right_suit = suit_label_converter[right_suit]
        right_value = value_label_converter[right_value]

        self.left_card = Card(number=left_value, suit=left_suit)
        self.right_card = Card(number=right_value, suit=right_suit)

    def _all_in(self):
        x = int(self.cor_x_high + self.x_size * act_allin_x_rel + np.random.randint(low=-50, high=50))
        y = int(self.cor_y_high + self.y_size * act_allin_y_rel + np.random.randint(low=-20, high=20))
        print(f"Allin: {x, y}")
        pyautogui.doubleClick(x, y)

    def _fold(self):
        x = int(self.cor_x_high + self.x_size * act_fold_x_rel + np.random.randint(low=-50, high=50))
        y = int(self.cor_y_high + self.y_size * act_fold_y_rel + np.random.randint(low=-20, high=20))
        print(f"Fold: {x, y}")
        pyautogui.doubleClick(x, y)

    def act(self):
        action = decide_action(c1=self.left_card, c2=self.right_card, state=self.curr_state)
        if action == Action.AllIn:
            print("-I- Action: Allin")
            self._all_in()
        else:
            print("-I- Action: Fold")
            self._fold()

    def read_villains_holding_cards(self, save=False):
        top_left_card = self.zoom_in(name='top_left_card',
                                 cor_x=int(self.x_size * holding_cards_top_left_x_cor_rel),
                                 cor_y=int(self.y_size * holding_cards_top_left_y_cor_rel),
                                 size_y=int(self.y_size * card_y_size_rel),
                                 size_x=int(self.x_size * card_x_size_rel), save=save)

        top_right_card = self.zoom_in(name='top_right_card',
                                  cor_x=int(self.x_size * holding_cards_top_right_x_cor_rel),
                                  cor_y=int(self.y_size * holding_cards_top_right_y_cor_rel),
                                  size_y=int(self.y_size * card_y_size_rel),
                                  size_x=int(self.x_size * card_x_size_rel), save=save)

        right_left_card = self.zoom_in(name='right_left_card',
                                     cor_x=int(self.x_size * holding_cards_right_left_x_cor_rel),
                                     cor_y=int(self.y_size * holding_cards_right_left_y_cor_rel),
                                     size_y=int(self.y_size * card_y_size_rel),
                                     size_x=int(self.x_size * card_x_size_rel), save=save)

        right_right_card = self.zoom_in(name='right_right_card',
                                      cor_x=int(self.x_size * holding_cards_right_right_x_cor_rel),
                                      cor_y=int(self.y_size * holding_cards_right_right_y_cor_rel),
                                      size_y=int(self.y_size * card_y_size_rel),
                                      size_x=int(self.x_size * card_x_size_rel), save=save)

        left_left_card = self.zoom_in(name='left_left_card',
                                       cor_x=int(self.x_size * holding_cards_left_left_x_cor_rel),
                                       cor_y=int(self.y_size * holding_cards_left_left_y_cor_rel),
                                       size_y=int(self.y_size * card_y_size_rel),
                                       size_x=int(self.x_size * card_x_size_rel), save=save)

        left_right_card = self.zoom_in(name='left_right_card',
                                        cor_x=int(self.x_size * holding_cards_left_right_x_cor_rel),
                                        cor_y=int(self.y_size * holding_cards_left_right_y_cor_rel),
                                        size_y=int(self.y_size * card_y_size_rel),
                                        size_x=int(self.x_size * card_x_size_rel), save=save)

    def read_community_cards(self, save=False):
        community_card_1 = self.zoom_in(name='community_card_1',
                                        cor_x=int(self.x_size * community_cards_1_x_cor_rel),
                                        cor_y=int(self.y_size * community_cards_1_y_cor_rel),
                                        size_y=int(self.y_size * card_y_size_rel),
                                        size_x=int(self.x_size * card_x_size_rel), save=save)
        community_card_2 = self.zoom_in(name='community_card_2',
                                        cor_x=int(self.x_size * community_cards_2_x_cor_rel),
                                        cor_y=int(self.y_size * community_cards_2_y_cor_rel),
                                        size_y=int(self.y_size * card_y_size_rel),
                                        size_x=int(self.x_size * card_x_size_rel), save=save)
        community_card_3 = self.zoom_in(name='community_card_3',
                                        cor_x=int(self.x_size * community_cards_3_x_cor_rel),
                                        cor_y=int(self.y_size * community_cards_3_y_cor_rel),
                                        size_y=int(self.y_size * card_y_size_rel),
                                        size_x=int(self.x_size * card_x_size_rel), save=save)
        community_card_4 = self.zoom_in(name='community_card_4',
                                        cor_x=int(self.x_size * community_cards_4_x_cor_rel),
                                        cor_y=int(self.y_size * community_cards_4_y_cor_rel),
                                        size_y=int(self.y_size * card_y_size_rel),
                                        size_x=int(self.x_size * card_x_size_rel), save=save)
        community_card_5 = self.zoom_in(name='community_card_5',
                                        cor_x=int(self.x_size * community_cards_5_x_cor_rel),
                                        cor_y=int(self.y_size * community_cards_5_y_cor_rel),
                                        size_y=int(self.y_size * card_y_size_rel),
                                        size_x=int(self.x_size * card_x_size_rel), save=save)

    def __str__(self):
        table_str = "*"*10 + " " + self.name + " " + "*"*10 + "\n"
        table_str += "*" * 5 + " # Hand: " + str(self.hands_counter) + "\n"
        #table_str += "*"*5 + " Dealer Location: " + str(self.curr_dealer_location) + "\n"
        #table_str += "*" * 5 + " SB Location: " + str(self.curr_sb_location) + "\n"
        #table_str += "*" * 5 + " BB Location: " + str(self.curr_bb_location) + "\n"

        top_in = int(Location.Top in self.curr_all_ins)
        left_in = int(Location.Left in self.curr_all_ins)
        right_in = int(Location.Right in self.curr_all_ins)
        bottom_in = int(Location.Bottom in self.curr_all_ins)

        table_str += f"{' ' * 13}{top_in * '**' + (1-top_in) * '  '}{self.curr_location_position_mapping[Location.Top]}{top_in * '**' + (1-top_in) * '  '}\n"
        table_str += "\n"
        table_str += f"{' ' * 3}{left_in * '**' + (1-left_in) * '  '}{self.curr_location_position_mapping[Location.Left]} {left_in * '**' + (1-left_in) * '  '} " \
                     f"{' ' * 11} {right_in * '**' + (1-right_in) * '  '}{self.curr_location_position_mapping[Location.Right]}{right_in * '**' + (1-right_in) * '  '} \n"
        table_str += "\n"
        table_str += f"{' ' * 13}{bottom_in * '**' + (1-bottom_in) * '  '}{self.curr_location_position_mapping[Location.Bottom]} {bottom_in * '**' + (1-bottom_in) * '  '} \n"
        table_str += "\n"
        table_str += f"{self.left_card} {self.right_card} \n"

        table_str += f"{self.curr_all_ins}"
        table_str += f"{self.curr_state}"

        return table_str

