import time
import win32gui
import cv2
from utils_table import *
from CNN_utils import *
from Card import Card
from Strategy import *
from logger import custom_print
from tesseract import optimized_read
print = custom_print


class AOFTable:
    def __init__(self, name, hwnd, dealer_model, blinds_model, action_model, value_model, suit_model, tess_models, device, crusher):
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
        self.curr_location_name_mapping = {}
        for location in Location:
            self.curr_location_position_mapping[location] = Position.SittingOut
            self.curr_location_name_mapping[location] = None

        self.left_card = None
        self.right_card = None

        self.curr_state = None

        self.valid = False
        self.crusher = crusher

        self.hands_counter = 0
        self.innner_counter = 0

        # FIXME: use as a static variables
        self.dealer_model = dealer_model
        self.blinds_model = blinds_model
        self.action_model = action_model
        self.value_model = value_model
        self.suit_model = suit_model

        self.opt_study = tess_models
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
        self.innner_counter = 0

    def screen_shot(self):
        self.fg_table()
        #raw_screenshot_str = "./pictures/Running/" + self.short_name + "_" + str(self.hands_counter) + "_raw.png"
        raw_screenshot_str = f"./pictures/Running/{self.short_name}_{self.hands_counter}_raw.png"
        #clear_screenshot_str = "./pictures/Running/" + self.short_name + "_" + str(self.hands_counter) + ".png"
        clear_screenshot_str = f"./pictures/Running/{self.short_name}_{self.hands_counter}_{self.innner_counter}.png"
        self.innner_counter += 1
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

        wrong_flag = False
        self.valid = not wrong_flag

        self.curr_location_position_mapping[self.curr_dealer_location] = Position.Dealer
        self.curr_location_position_mapping[self.curr_bb_location] = Position.BigBlind

        if (self.curr_dealer_location.value == (self.curr_bb_location.value - 2) % 4) and ((self.curr_sb_location is None and Location((self.curr_bb_location.value - 1) % 4) in self.curr_all_ins) or (
                self.curr_sb_location is not None and self.curr_sb_location.value == (self.curr_bb_location.value - 1) % 4)):
            self.curr_location_position_mapping[Location((self.curr_bb_location.value - 1) % 4)] = Position.SmallBlind
            self.curr_location_position_mapping[Location((self.curr_bb_location.value - 3) % 4)] = Position.CutOff

        # one sitting out in the middle, not cutoff
        elif self.curr_dealer_location.value == (self.curr_bb_location.value - 3) % 4 and (
                (self.curr_sb_location is not None and self.curr_sb_location != self.curr_dealer_location) or any(ai_loc != self.curr_dealer_location for ai_loc in self.curr_all_ins)):
            if self.curr_sb_location is None:
                if Location((self.curr_bb_location.value - 1) % 4) in self.curr_all_ins:
                    self.curr_location_position_mapping[Location((self.curr_bb_location.value - 1) % 4)] = Position.SmallBlind
                    self.curr_location_position_mapping[Location((self.curr_bb_location.value - 2) % 4)] = Position.SittingOut

                elif Location((self.curr_bb_location.value - 2) % 4) in self.curr_all_ins:
                    self.curr_location_position_mapping[Location((self.curr_bb_location.value - 1) % 4)] = Position.SittingOut
                    self.curr_location_position_mapping[Location((self.curr_bb_location.value - 2) % 4)] = Position.SmallBlind

                else:
                    wrong_flag = True

            else:
                remaining_loc = TOTAL_SUM_OF_LOCATIONS - self.curr_sb_location.value - self.curr_bb_location.value - self.curr_dealer_location.value
                remaining_loc = Location(remaining_loc)
                self.curr_location_position_mapping[remaining_loc] = Position.SittingOut
                self.curr_location_position_mapping[self.curr_sb_location] = Position.SmallBlind

        # two players sitting out

        elif self.curr_sb_location is not None and self.curr_sb_location == self.curr_dealer_location:
            for location in Location:
                if location not in [self.curr_bb_location, self.curr_dealer_location]:
                    self.curr_location_position_mapping[location] = Position.SittingOut
            self.curr_location_position_mapping[self.curr_dealer_location] = Position.SmallBlind

        elif self.curr_sb_location is None and self.curr_dealer_location in self.curr_all_ins:
            for location in Location:
                if location not in [self.curr_bb_location, self.curr_dealer_location]:
                    if location in self.curr_all_ins:
                        wrong_flag = True
            self.curr_location_position_mapping[self.curr_dealer_location] = Position.SmallBlind
        else:
            wrong_flag = True

        self.valid = not wrong_flag
        if not self.valid:
            if self.crusher:
                assert False, "-E- Impossible table structure"
            print(f"-E- {self.name} Incompatible table structure")
            self.curr_location_position_mapping[Location.Bottom] = Position.SittingOut
            self.curr_location_position_mapping[Location.Left] = Position.SittingOut
            self.curr_location_position_mapping[Location.Right] = Position.SittingOut
            self.curr_location_position_mapping[Location.Top] = Position.SittingOut

    def _figure_state(self):
        if not self.valid:
            if self.curr_bb_location == Location.Bottom:
                fake_state = State.BB_CO
            elif self.curr_dealer_location == Location.Bottom:
                fake_state = State.DE
            elif len(self.curr_all_ins) > 0:
                fake_state = State.SB_CO
            else:
                fake_state = State.CO
            print(f"-E- {self.name} Incompatible table structure, Guessing {fake_state}")
            self.valid = True
            return fake_state

        if self.curr_location_position_mapping[Location.Bottom] == Position.CutOff:
            if not len(self.curr_all_ins) == 0:
                print(f"-E- {self.name} position CO, with allin")
                self.valid = False
            return State.CO

        if self.curr_location_position_mapping[Location.Bottom] == Position.Dealer:
            if not len(self.curr_all_ins) <= 1:
                print(f"-E- {self.name} position DE more than 1 allin")
                self.valid = False
                return State.DE_CO
            if len(self.curr_all_ins) == 1:
                if not self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.CutOff:
                    print(f"-E- {self.name} position DE one all in not in CO")
                    self.valid = False
                return State.DE_CO
            else:
                return State.DE

        if self.curr_location_position_mapping[Location.Bottom] == Position.SmallBlind:
            if not len(self.curr_all_ins) <= 2:
                print(f"-E- {self.name} position SB more than 2 allin")
                self.valid = False
                return State.SB_CO_DE
            if len(self.curr_all_ins) == 0:
                return State.SB
            if len(self.curr_all_ins) == 1:
                if self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.CutOff:
                    return State.SB_CO
                if self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.Dealer:
                    return State.SB_DE
                print(f"-E- {self.name} position SB 1 allin not in CO or DE")
                self.valid = False
                return State.SB_DE
            if len(self.curr_all_ins) == 2:
                if not (self.curr_location_position_mapping[self.curr_all_ins[0]] in [Position.CutOff, Position.Dealer]
                        and self.curr_location_position_mapping[self.curr_all_ins[1]] in [Position.CutOff, Position.Dealer]):
                    print(f"-E- {self.name} position SB 2 allin, not in CO and DE")
                    self.valid = False
                return State.SB_CO_DE

        if self.curr_location_position_mapping[Location.Bottom] == Position.BigBlind:
            if not len(self.curr_all_ins) >= 1:
                print(f"-E- {self.name} position BB no allin")
                self.valid = False
                return State.BB_CO
            if len(self.curr_all_ins) == 1:
                if self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.CutOff:
                    return State.BB_CO
                if self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.Dealer:
                    return State.BB_DE
                if self.curr_location_position_mapping[self.curr_all_ins[0]] == Position.SmallBlind:
                    return State.BB_SB
                print(f"-E- {self.name} position BB 1 allin not in CO or DE or SB")
                self.valid = False
                return State.BB_CO
            if len(self.curr_all_ins) == 3:
                if not (Location.Top in self.curr_all_ins and Location.Left in self.curr_all_ins and Location.Right in self.curr_all_ins):
                    print(f"-E- {self.name} position BB 3 allin not in all the Locations")
                    self.valid = False
                return State.BB_CO_DE_SB
            if len(self.curr_all_ins) == 2:
                if Position.CutOff not in [self.curr_location_position_mapping[self.curr_all_ins[0]], self.curr_location_position_mapping[self.curr_all_ins[1]]]:
                    return State.BB_DE_SB
                if Position.Dealer not in [self.curr_location_position_mapping[self.curr_all_ins[0]], self.curr_location_position_mapping[self.curr_all_ins[1]]]:
                    return State.BB_CO_SB
                if Position.SmallBlind not in [self.curr_location_position_mapping[self.curr_all_ins[0]], self.curr_location_position_mapping[self.curr_all_ins[1]]]:
                    return State.BB_CO_DE
                print(f"-E- {self.name} position BB 2 allin don't fit DE_SB or CO_SB or CD_DE")
                self.valid = False
                return State.BB_CO_DE
            print(f"-E- {self.name} position BB not {1,2,3} allin")
            self.valid = False
            return State.BB_CO
        print(f"-E- {self.name} position not BB or SB or DE or CO")
        self.valid = False
        return State.CO

    def figure_state(self):
        self.curr_state = self._figure_state()

    def is_my_turn(self, save=False):
        self.screen_shot()
        action = self.zoom_in(name='action', cor_x=int(self.x_size * action_x_cor_rel),
                              cor_y=int(self.y_size * action_y_cor_rel),
                              size_y=int(self.y_size * action_y_size_rel),
                              size_x=int(self.x_size * action_x_size_rel), save=save)

        return classify_image(model=self.action_model, im=action, device=self.device, resize=action_resize)

    def read_hud(self, save=False):
        def read_hud_loc(loc):
            name = "hud_"
            if loc == Location.Left:
                player_x_cor_rel = left_player_x_cor_rel
                player_y_cor_rel = left_player_y_cor_rel
                hud_x_cor_rel = hud_left_x_cor_rel
                hud_y_cor_rel = hud_left_y_cor_rel
                name += 'left'
            elif loc == Location.Right:
                player_x_cor_rel = right_player_x_cor_rel
                player_y_cor_rel = right_player_y_cor_rel
                hud_x_cor_rel = hud_right_x_cor_rel
                hud_y_cor_rel = hud_right_y_cor_rel
                name += 'right'
            elif loc == Location.Top:
                player_x_cor_rel = top_player_x_cor_rel
                player_y_cor_rel = top_player_y_cor_rel
                hud_x_cor_rel = hud_top_x_cor_rel
                hud_y_cor_rel = hud_top_y_cor_rel
                name += 'top'
            else:
                assert False

            pyautogui.moveTo(self.cor_x_high + int(self.x_size * player_x_cor_rel),
                             self.cor_y_high + int(self.y_size * player_y_cor_rel), duration=0.1)
            # TODO: pyautogui.moveTo(500, 500, duration=1, tween=pyautogui.easeInOutQuad)
            if loc == Location.Top:
                time.sleep(0.5)
            self.screen_shot()
            if loc == Location.Top:
                plt.imshow(self.curr_screen_shot)
                plt.show()
            hud = self.zoom_in(name=name,
                               cor_x=int(self.x_size * hud_x_cor_rel),
                               cor_y=int(self.y_size * hud_y_cor_rel),
                               size_y=int(self.y_size * hud_y_size_rel),
                               size_x=int(self.x_size * hud_x_size_rel), save=save)
            time.sleep(0.1)

        locations = [Location.Top, Location.Left, Location.Right]
        time.sleep(0.1)
        for loc in locations:
            read_hud_loc(loc=loc)

        pyautogui.moveTo(self.cor_x_high + int(self.x_size * 0.5),
                         self.cor_y_high + int(self.y_size * 0.5), duration=0.1)

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

    def read_names(self, save=False):
        left_name = self.zoom_in(name='left_name',
                                 cor_x=int(self.x_size * left_name_x_cor_rel),
                                 cor_y=int(self.y_size * left_name_y_cor_rel),
                                 size_y=int(self.y_size * name_y_size_rel),
                                 size_x=int(self.x_size * name_x_size_rel), save=save)

        right_name = self.zoom_in(name='right_name',
                                 cor_x=int(self.x_size * right_name_x_cor_rel),
                                 cor_y=int(self.y_size * right_name_y_cor_rel),
                                 size_y=int(self.y_size * name_y_size_rel),
                                 size_x=int(self.x_size * name_x_size_rel), save=save)

        top_name = self.zoom_in(name='top_name',
                                  cor_x=int(self.x_size * top_name_x_cor_rel),
                                  cor_y=int(self.y_size * top_name_y_cor_rel),
                                  size_y=int(self.y_size * name_y_size_rel),
                                  size_x=int(self.x_size * name_x_size_rel), save=save)

        left_name = optimized_read(im=left_name, num=1, study=self.opt_study)
        top_name = optimized_read(im=top_name, num=1, study=self.opt_study)
        right_name = optimized_read(im=right_name, num=1, study=self.opt_study)

        self.curr_location_name_mapping[Location.Left] = left_name.split("\n")[0]
        self.curr_location_name_mapping[Location.Top] = top_name.split("\n")[0]
        self.curr_location_name_mapping[Location.Right] = right_name.split("\n")[0]

    def _all_in(self):
        x = int(self.cor_x_high + self.x_size * act_allin_x_rel + np.random.randn() * 15 * self.x_size / 1280)
        y = int(self.cor_y_high + self.y_size * act_allin_y_rel + np.random.randn() * 5 * self.y_size / 911)
        print(f"-I- Allin: {x, y}")
        pyautogui.moveTo(x, y, duration=0.1 + np.random.randn() * 0.01)
        pyautogui.click(x, y, tween=pyautogui.easeInOutQuad)

    def _fold(self):
        x = int(self.cor_x_high + self.x_size * act_fold_x_rel + np.random.randn() * 15 * self.x_size / 1280)
        y = int(self.cor_y_high + self.y_size * act_fold_y_rel + np.random.randn() * 5 * self.y_size / 911)
        print(f"-I- Fold: {x, y}")
        pyautogui.moveTo(x, y, duration=0.1 + np.random.randn() * 0.01)
        pyautogui.click(x, y, tween=pyautogui.easeInOutQuad)

    def act(self):
        action = decide_action(c1=self.left_card, c2=self.right_card, state=self.curr_state, all_in=2.0, bb=0.25, sb=0.1, jp=130)
        if action == Action.AllIn:
            self._all_in()
        else:
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

        top_in = int(Location.Top in self.curr_all_ins)
        left_in = int(Location.Left in self.curr_all_ins)
        right_in = int(Location.Right in self.curr_all_ins)
        bottom_in = int(Location.Bottom in self.curr_all_ins)

        top_dealer = int(Location.Top == self.curr_dealer_location)
        left_dealer = int(Location.Left == self.curr_dealer_location)
        right_dealer = int(Location.Right == self.curr_dealer_location)
        bottom_dealer = int(Location.Bottom == self.curr_dealer_location)

        top_bb = int(Location.Top == self.curr_bb_location)
        left_bb = int(Location.Left == self.curr_bb_location)
        right_bb = int(Location.Right == self.curr_bb_location)
        bottom_bb = int(Location.Bottom == self.curr_bb_location)

        top_sb = int(Location.Top == self.curr_sb_location)
        left_sb = int(Location.Left == self.curr_sb_location)
        right_sb = int(Location.Right == self.curr_sb_location)
        bottom_sb = int(Location.Bottom == self.curr_sb_location)

        dealer_str = Color.GREEN + 'o ' + Color.END
        bb_str = Color.YELLOW + 'bb ' + Color.END
        sb_str = Color.YELLOW + 'sb ' + Color.END

        top_blinds_str = top_bb * bb_str + top_sb * sb_str
        left_blinds_str = left_bb * bb_str + left_sb * sb_str
        right_blinds_str = right_bb * bb_str + right_sb * sb_str
        bottom_blinds_str = bottom_bb * bb_str + bottom_sb * sb_str

        top_name_str = f"{top_in * (Color.BOLD+Color.UNDERLINE)}{self.curr_location_name_mapping[Location.Top]}-{self.curr_location_position_mapping[Location.Top]}{top_in * Color.END}"
        left_name_str = f"{left_in * (Color.BOLD + Color.UNDERLINE)}{self.curr_location_name_mapping[Location.Left]}-{self.curr_location_position_mapping[Location.Left]}{left_in * Color.END} "
        right_name_str = f"{right_in * (Color.BOLD+Color.UNDERLINE)}{self.curr_location_name_mapping[Location.Right]}-{self.curr_location_position_mapping[Location.Right]}{right_in * Color.END}"
        bottom_name_str = f"{bottom_in * (Color.BOLD+Color.UNDERLINE)}{self.curr_location_position_mapping[Location.Bottom]}{bottom_in * Color.END}"

        left_name_len = len(self.curr_location_name_mapping[Location.Left])
        top_spaces = 15 + left_name_len
        left_spaces = 5
        right_spaces = 5 + left_name_len
        bottom_spaces = 17 + left_name_len

        table_str += f"{' ' * top_spaces}{top_name_str}\n"
        table_str += f"{' ' * (top_spaces+3)}{top_blinds_str}{top_dealer * dealer_str}\n"
        table_str += f"{' ' * left_spaces}{left_name_str} {left_blinds_str + left_dealer * dealer_str} {' ' * 20} {right_blinds_str + right_dealer * dealer_str} {right_name_str}\n"
        table_str += f"{' ' * bottom_spaces}{bottom_blinds_str + bottom_dealer * dealer_str}\n"
        table_str += f"{' ' * bottom_spaces} {bottom_name_str} \n"

        table_str += f"{self.left_card} {self.right_card} \n"

        table_str += f"{self.curr_state} \n"
        table_str += f"{self.curr_all_ins} "

        return table_str

