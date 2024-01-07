from parse_history_utils import *


class HistoryDataBase:
    def __init__(self, file_name):
        self.data = {}

    def update_data(self, name: str, state: State, action:Action) -> None:
        if name == "":
            return

        if name not in self.data:
            self.data[name] = {}
        if state not in self.data[name]:
            self.data[name][state] = (0, 0)

        rate, counter = self.data[name][state]
        if action == Action.Fold:
            self.data[name][state] = (rate, counter + 1)
        elif action == Action.AllIn:
            self.data[name][state] = (rate + 1, counter + 1)
        else:
            assert False, "Action is not valid"

    def get_data(self, name: str, state: State) -> float:
        if name not in self.data:
            if state not in self.data[name]:
                return -1.0
        rate, counter = self.data[name][state]
        return rate / counter

    def save_data(self, file_name):
        with open(file_name, 'wb') as f:
            pickle.dump(self.data, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_data(self, file_name):
        with open(file_name, 'rb') as f:
            self.data = pickle.load(f)


def find_init_final_photos():
    init_photo = None
    final_photo = None
    return init_photo, final_photo


def parse_location_position(init_photo, dealer_location, allin=2.0, sb=0.1, bb=0.25):
    location_position_map = {}
    location_action_map = {}

    y_size, x_size, dim = im.shape

    top_x = round(blinds_top_x_cor_rel * x_size)
    top_y = round(blinds_top_y_cor_rel * y_size)

    right_x = round(blinds_right_x_cor_rel * x_size)
    right_y = round(blinds_right_y_cor_rel * y_size)

    left_x = round(blinds_left_x_cor_rel * x_size)
    left_y = round(blinds_left_y_cor_rel * y_size)

    bottom_x = round(blinds_bottom_x_cor_rel * x_size)
    bottom_y = round(blinds_bottom_y_cor_rel * y_size)

    x_size = round(blinds_x_size_rel * x_size)
    y_size = round(blinds_y_size_rel * y_size)

    top = init_photo[top_y:top_y + y_size, top_x:top_x + x_size]
    left = init_photo[left_y:left_y + y_size, left_x:left_x + x_size]
    right = init_photo[right_y:right_y + y_size, right_x:right_x + x_size]
    bottom = init_photo[bottom_y:bottom_y + y_size, bottom_x:bottom_x + x_size]

    # nn_dir = "./NN/1.001"
    # device = "cpu"
    # blinds_model = torch.load(f"{nn_dir}/trained_Blinds_model.torch").to(device)
    # top = classify_image(model=blinds_model, im=top, resize=blinds_resize, device=device)
    # left = classify_image(model=blinds_model, im=left, resize=blinds_resize, device=device)
    # right = classify_image(model=blinds_model, im=right, resize=blinds_resize, device=device)
    # bottom = classify_image(model=blinds_model, im=bottom, resize=blinds_resize, device=device)

    def extract_position(im):
        txt = pytesseract.image_to_string(im[25:, :], config="-c tessedit_char_whitelist=012345678.$9 user_patterns_suffix ./blind_tesseract.txt")
        try:
            money = float(txt.split("$")[1].split("\n")[0])
        except IndexError:
            money = 0

        if money == 0:
            return None
        if money == 0.25:
            return Position.BigBlind
        if money == 0.1:
            return Position.SmallBlind
        if money >= 2.0:
            return Action.AllIn

    location_action_map[Location.Right] = extract_position(im=right)
    location_action_map[Location.Left] = extract_position(im=left)
    location_action_map[Location.Top] = extract_position(im=top)
    location_action_map[Location.Bottom] = extract_position(im=bottom)

    none_counter = 0
    for loc in [Location.Right, Location.Left, Location.Top, Location.Bottom]:
        if loc is None:
            none_counter += 1

    if none_counter > 2:
        return location_position_map

    temp = {Location.Right: Location.Right,
            Location.Left: Location.Left,
            Location.Top: Location.Top,
            Location.Bottom: Location.Bottom}

    location_position_map[dealer_location] = Position.Dealer
    if temp[Location((dealer_location.value + 1) % 4)] is None:
        location_position_map[Location((dealer_location.value + 1) % 4)] = Position.SittingOut
        if temp[Location((dealer_location.value + 2) % 4)] is None:
            location_position_map[Location((dealer_location.value + 2) % 4)] = Position.SittingOut
            location_position_map[Location((dealer_location.value + 3) % 4)] = Position.SmallBlind
            location_position_map[dealer_location] = Position.BigBlind
        else:
            location_position_map[Location((dealer_location.value + 2) % 4)] = Position.SmallBlind
            if temp[Location((dealer_location.value + 3) % 4)] is None:
                location_position_map[Location((dealer_location.value + 3) % 4)] = Position.SittingOut
                location_position_map[dealer_location] = Position.BigBlind
            else:
                location_position_map[Location((dealer_location.value + 3) % 4)] = Position.BigBlind
    else:
        location_position_map[Location((dealer_location.value + 1) % 4)] = Position.SmallBlind
        if temp[Location((dealer_location.value + 2) % 4)] is None:
            location_position_map[Location((dealer_location.value + 2) % 4)] = Position.SittingOut
            if temp[Location((dealer_location.value + 3) % 4)] is None:
                location_position_map[Location((dealer_location.value + 3) % 4)] = Position.SittingOut
            else:
                location_position_map[Location((dealer_location.value + 3) % 4)] = Position.BigBlind
        else:
            location_position_map[Location((dealer_location.value + 2) % 4)] = Position.BigBlind
            location_position_map[Location((dealer_location.value + 3) % 4)] = Position.CutOff

    return location_position_map, location_action_map


def find_history(location_position_map, location_action_map):

    position_action = {Position.BigBlind: None, Position.SmallBlind: None, Position.CutOff: None, Position.Dealer: None}
    c = 0
    for loc in Location:
        if location_position_map[loc] is not None:
            c += 1
            position_action[location_position_map[loc]] = location_action_map[loc]

    if c == 0:
        return None

    if position_action[Position.CutOff] == Action.AllIn:
        if position_action[Position.Dealer] == Action.AllIn:
            if position_action[Position.SmallBlind] == Action.AllIn:
                if position_action[Position.BigBlind] == Action.AllIn:
                    return History.CO_DE_SB_BB
                else:
                    return History.CO_DE_SB
            else:
                if position_action[Position.BigBlind] == Action.AllIn:
                    return History.CO_DE_BB
                else:
                    return History.CO_DE
        else:
            if position_action[Position.SmallBlind] == Action.AllIn:
                if position_action[Position.BigBlind] == Action.AllIn:
                    return History.CO_SB_BB
                else:
                    return History.CO_SB
            else:
                if position_action[Position.BigBlind] == Action.AllIn:
                    return History.CO_BB
                else:
                    return History.CO
    else:
        if position_action[Position.Dealer] == Action.AllIn:
            if position_action[Position.SmallBlind] == Action.AllIn:
                if position_action[Position.BigBlind] == Action.AllIn:
                    return History.DE_SB_BB
                else:
                    return History.DE_SB
            else:
                if position_action[Position.BigBlind] == Action.AllIn:
                    return History.DE_BB
                else:
                    return History.DE
        else:
            if position_action[Position.SmallBlind] == Action.AllIn:
                if position_action[Position.BigBlind] == Action.AllIn:
                    return History.SB_BB
                else:
                    return History.SB
            else:
                return History.BB


def parse_total_pot(final_photo, sb, bb, allin):
    y_size, x_size, dim = final_photo.shape
    x_cor = round(x_size * pot_top_x_cor_rel)
    y_cor = round(y_size * pot_top_y_cor_rel)
    x_size = round(x_size * pot_x_size_rel)
    y_size = round(y_size * pot_y_size_rel)

    pot_photo = final_photo[y_cor:y_cor+y_size, x_cor:x_cor+x_size]
    #txt = pytesseract.image_to_string(pot_photo, config="--psm 7 -c tessedit_char_whitelist=toalp:0123456789. user_patterns_suffix ./pot_tesseract.txt")
    txt = pytesseract.image_to_string(pot_photo, config="--psm 7 user_patterns_suffix ./pot_tesseract.txt")

    try:
        total_pot = txt.split('$')[1].split("\n")[0]
        total_pot = float(total_pot)
    except:
        total_pot = 10

    if total_pot == 2 * bb + sb:
        return [History.CO, History.DE]

    if total_pot == 2 * bb:
        return [History.SB]

    if total_pot == 2 * sb:
        return [History.BB]

    if total_pot == 2 * allin + bb + sb:
        return [History.CO_DE]

    if total_pot == 2 * allin + bb:
        return [History.CO_SB, History.DE_SB]

    if total_pot == 2 * allin + sb:
        return [History.CO_BB, History.DE_BB]

    if total_pot == 2 * allin:
        return [History.SB_BB]

    if total_pot == 3 * allin + bb:
        return [History.CO_DE_SB]

    if total_pot == 3 * allin + sb:
        return [History.CO_DE_BB]

    if total_pot == 3 * allin:
        return [History.CO_SB_BB, History.DE_SB_BB]

    if total_pot == 4 * allin:
        return [History.CO_DE_SB_BB]

    # FIXME: finish for cases of additional blinds and allin that is greater than the normal
    else:
        return total_pot


def update_database(database: HistoryDataBase, history: History, co_name: str, de_name: str, sb_name: str, bb_name: str):

    if history == History.BB:
        database.update_data(name=co_name, state=State.CO, action=Action.FOLD)
        database.update_data(name=de_name, state=State.DE, action=Action.FOLD)
        database.update_data(name=sb_name, state=State.SB, action=Action.FOLD)

    elif history == History.CO:
        database.update_data(name=co_name, state=State.CO, action=Action.AllIn)
        database.update_data(name=de_name, state=State.DE_CO, action=Action.FOLD)
        database.update_data(name=sb_name, state=State.SB_CO, action=Action.FOLD)
        database.update_data(name=bb_name, state=State.BB_CO, action=Action.FOLD)

    elif history == History.DE:
        database.update_data(name=co_name, state=State.CO, action=Action.FOLD)
        database.update_data(name=de_name, state=State.DE, action=Action.AllIn)
        database.update_data(name=sb_name, state=State.SB_DE, action=Action.FOLD)
        database.update_data(name=bb_name, state=State.BB_DE, action=Action.FOLD)

    elif history == History.SB:
        database.update_data(name=co_name, state=State.CO, action=Action.FOLD)
        database.update_data(name=de_name, state=State.DE, action=Action.FOLD)
        database.update_data(name=sb_name, state=State.SB, action=Action.AllIn)
        database.update_data(name=bb_name, state=State.BB_SB, action=Action.FOLD)

    elif history == History.CO_DE:
        database.update_data(name=co_name, state=State.CO, action=Action.AllIn)
        database.update_data(name=de_name, state=State.DE_CO, action=Action.AllIn)
        database.update_data(name=sb_name, state=State.SB_CO_DE, action=Action.FOLD)
        database.update_data(name=bb_name, state=State.BB_CO_DE, action=Action.FOLD)

    elif history == History.CO_SB:
        database.update_data(name=co_name, state=State.CO, action=Action.AllIn)
        database.update_data(name=de_name, state=State.DE_CO, action=Action.FOLD)
        database.update_data(name=sb_name, state=State.SB_CO, action=Action.AllIn)
        database.update_data(name=bb_name, state=State.BB_CO_SB, action=Action.FOLD)

    elif history == History.CO_BB:
        database.update_data(name=co_name, state=State.CO, action=Action.AllIn)
        database.update_data(name=de_name, state=State.DE_CO, action=Action.FOLD)
        database.update_data(name=sb_name, state=State.SB_CO, action=Action.FOLD)
        database.update_data(name=bb_name, state=State.BB_CO, action=Action.AllIn)

    elif history == History.DE_SB:
        database.update_data(name=co_name, state=State.CO, action=Action.FOLD)
        database.update_data(name=de_name, state=State.DE, action=Action.AllIn)
        database.update_data(name=sb_name, state=State.SB_DE, action=Action.AllIn)
        database.update_data(name=bb_name, state=State.BB_DE_SB, action=Action.FOLD)

    elif history == History.DE_BB:
        database.update_data(name=co_name, state=State.CO, action=Action.FOLD)
        database.update_data(name=de_name, state=State.DE, action=Action.AllIn)
        database.update_data(name=sb_name, state=State.SB_DE, action=Action.FOLD)
        database.update_data(name=bb_name, state=State.BB_DE, action=Action.AllIn)

    elif history == History.SB_BB:
        database.update_data(name=co_name, state=State.CO, action=Action.FOLD)
        database.update_data(name=de_name, state=State.DE, action=Action.FOLD)
        database.update_data(name=sb_name, state=State.SB, action=Action.AllIn)
        database.update_data(name=bb_name, state=State.BB_SB, action=Action.AllIn)

    elif history == History.CO_DE_SB:
        database.update_data(name=co_name, state=State.CO, action=Action.AllIn)
        database.update_data(name=de_name, state=State.DE_CO, action=Action.AllIn)
        database.update_data(name=sb_name, state=State.SB_CO_DE, action=Action.AllIn)
        database.update_data(name=bb_name, state=State.BB_CO_DE_SB, action=Action.FOLD)

    elif history == History.CO_DE_BB:
        database.update_data(name=co_name, state=State.CO, action=Action.AllIn)
        database.update_data(name=de_name, state=State.DE_CO, action=Action.AllIn)
        database.update_data(name=sb_name, state=State.SB_CO_DE, action=Action.FOLD)
        database.update_data(name=bb_name, state=State.BB_CO_DE, action=Action.AllIn)

    elif history == History.CO_SB_BB:
        database.update_data(name=co_name, state=State.CO, action=Action.AllIn)
        database.update_data(name=de_name, state=State.DE_CO, action=Action.FOLD)
        database.update_data(name=sb_name, state=State.SB_CO, action=Action.AllIn)
        database.update_data(name=bb_name, state=State.BB_CO_SB, action=Action.AllIn)

    elif history == History.DE_SB_BB:
        database.update_data(name=co_name, state=State.CO, action=Action.FOLD)
        database.update_data(name=de_name, state=State.DE, action=Action.AllIn)
        database.update_data(name=sb_name, state=State.SB_DE, action=Action.AllIn)
        database.update_data(name=bb_name, state=State.BB_DE_SB, action=Action.AllIn)

    elif history == History.CO_DE_SB_BB:
        database.update_data(name=co_name, state=State.CO, action=Action.AllIn)
        database.update_data(name=de_name, state=State.DE_CO, action=Action.AllIn)
        database.update_data(name=sb_name, state=State.SB_CO_DE, action=Action.AllIn)
        database.update_data(name=bb_name, state=State.BB_CO_DE_SB, action=Action.AllIn)

    else:
        assert False, "Unknown history: {}".format(history)


def find_hands(ordered_pic_list):
    """
    :param ordered_pic_list:
    :return: list of lists of pics addresses of each hand from start to end

    TODO: need better dealer recognition

    """
    hands_list = []
    prev_button_pos = None
    prev_table_name = None

    for idx, pic in enumerate(ordered_pic_list):
        im = cv2.imread(pic)
        button_pos = find_dealer_location(im=im)
        table_name = pic.split("_")
        table_name = table_name[0]+table_name[1]
        if not button_pos == prev_button_pos:  # new hand
            if idx > 0 and table_name == prev_table_name:
                hands_list.append(hand_pics)
            hand_pics = [pic]
        else:
            hand_pics.append(pic)
        prev_button_pos = button_pos
        prev_table_name = table_name

    return hands_list


def strip_data(pic_list):

    def strip_data_dealer(im):
        y_size, x_size, dim = im.shape

        top_x = round(button_top_x_cor_rel * x_size)
        top_y = round(button_top_y_cor_rel * y_size)

        right_x = round(button_right_x_cor_rel * x_size)
        right_y = round(button_right_y_cor_rel * y_size)

        left_x = round(button_left_x_cor_rel * x_size)
        left_y = round(button_left_y_cor_rel * y_size)

        bottom_x = round(button_bottom_x_cor_rel * x_size)
        bottom_y = round(button_bottom_y_cor_rel * y_size)

        x_size = round(button_x_size_rel * x_size)
        y_size = round(button_y_size_rel * y_size)

        dealer_top = im[top_y:top_y + y_size, top_x:top_x + x_size]
        dealer_left = im[left_y:left_y + y_size, left_x:left_x + x_size]
        dealer_right = im[right_y:right_y + y_size, right_x:right_x + x_size]
        dealer_bottom = im[bottom_y:bottom_y + y_size, bottom_x:bottom_x + x_size]

        return dealer_top, dealer_left, dealer_right, dealer_bottom

    def strip_data_bottom_cards(im):
        y_size, x_size, dim = im.shape

        cards_bottom_left_x = round(holding_cards_bottom_left_x_cor_rel * x_size)
        cards_bottom_left_y = round(holding_cards_bottom_left_y_cor_rel * y_size)
        cards_bottom_right_x = round(holding_cards_bottom_right_x_cor_rel * x_size)
        cards_bottom_right_y = round(holding_cards_bottom_right_y_cor_rel * y_size)

        x_size = round(card_x_size_rel * x_size)
        y_size = round(card_y_size_rel * y_size)

        cards_bottom_left = im[cards_bottom_left_y:cards_bottom_left_y + y_size, cards_bottom_left_x:cards_bottom_left_x + x_size]
        cards_bottom_right = im[cards_bottom_right_y:cards_bottom_right_y + y_size, cards_bottom_right_x:cards_bottom_right_x + x_size]

        return cards_bottom_left, cards_bottom_right

    def strip_data_community_cards(im):
        y_size, x_size, dim = im.shape

        cards_comm_1_x = round(community_cards_1_x_cor_rel * x_size)
        cards_comm_1_y = round(community_cards_1_y_cor_rel * y_size)
        cards_comm_2_x = round(community_cards_2_x_cor_rel * x_size)
        cards_comm_2_y = round(community_cards_2_y_cor_rel * y_size)
        cards_comm_3_x = round(community_cards_3_x_cor_rel * x_size)
        cards_comm_3_y = round(community_cards_3_y_cor_rel * y_size)
        cards_comm_4_x = round(community_cards_4_x_cor_rel * x_size)
        cards_comm_4_y = round(community_cards_4_y_cor_rel * y_size)
        cards_comm_5_x = round(community_cards_5_x_cor_rel * x_size)
        cards_comm_5_y = round(community_cards_5_y_cor_rel * y_size)

        x_size = round(card_x_size_rel * x_size)
        y_size = round(card_y_size_rel * y_size)

        cards_comm_1 = im[cards_comm_1_y:cards_comm_1_y + y_size, cards_comm_1_x:cards_comm_1_x + x_size]
        cards_comm_2 = im[cards_comm_2_y:cards_comm_2_y + y_size, cards_comm_2_x:cards_comm_2_x + x_size]
        cards_comm_3 = im[cards_comm_3_y:cards_comm_3_y + y_size, cards_comm_3_x:cards_comm_3_x + x_size]
        cards_comm_4 = im[cards_comm_4_y:cards_comm_4_y + y_size, cards_comm_4_x:cards_comm_4_x + x_size]
        cards_comm_5 = im[cards_comm_5_y:cards_comm_5_y + y_size, cards_comm_5_x:cards_comm_5_x + x_size]

        return cards_comm_1, cards_comm_2, cards_comm_3, cards_comm_4, cards_comm_5

    def strip_data_villain_cards(im):
        y_size, x_size, dim = im.shape

        cards_top_left_x = round(holding_cards_top_left_x_cor_rel * x_size)
        cards_top_left_y = round(holding_cards_top_left_y_cor_rel * y_size)
        cards_top_right_x = round(holding_cards_top_right_x_cor_rel * x_size)
        cards_top_right_y = round(holding_cards_top_right_y_cor_rel * y_size)

        cards_right_left_x = round(holding_cards_right_left_x_cor_rel * x_size)
        cards_right_left_y = round(holding_cards_right_left_y_cor_rel * y_size)
        cards_right_right_x = round(holding_cards_right_right_x_cor_rel * x_size)
        cards_right_right_y = round(holding_cards_right_right_y_cor_rel * y_size)

        cards_left_left_x = round(holding_cards_left_left_x_cor_rel * x_size)
        cards_left_left_y = round(holding_cards_left_left_y_cor_rel * y_size)
        cards_left_right_x = round(holding_cards_left_right_x_cor_rel * x_size)
        cards_left_right_y = round(holding_cards_left_right_y_cor_rel * y_size)

        x_size = round(card_x_size_rel * x_size)
        y_size = round(card_y_size_rel * y_size)

        cards_top_left = im[cards_top_left_y:cards_top_left_y + y_size, cards_top_left_x:cards_top_left_x + x_size]
        cards_top_right = im[cards_top_right_y:cards_top_right_y + y_size, cards_top_right_x:cards_top_right_x + x_size]
        cards_right_left = im[cards_right_left_y:cards_right_left_y + y_size, cards_right_left_x:cards_right_left_x + x_size]
        cards_right_right = im[cards_right_right_y:cards_right_right_y + y_size, cards_right_right_x:cards_right_right_x + x_size]
        cards_left_left = im[cards_left_left_y:cards_left_left_y + y_size, cards_left_left_x:cards_left_left_x + x_size]
        cards_left_right = im[cards_left_right_y:cards_left_right_y + y_size, cards_left_right_x:cards_left_right_x + x_size]

        return cards_top_left, cards_top_right, cards_right_left, cards_right_right, cards_left_left, cards_left_right

    def strip_data_blinds(im):
        y_size, x_size, dim = im.shape

        top_x = round(blinds_top_x_cor_rel * x_size)
        top_y = round(blinds_top_y_cor_rel * y_size)

        right_x = round(blinds_right_x_cor_rel * x_size)
        right_y = round(blinds_right_y_cor_rel * y_size)

        left_x = round(blinds_left_x_cor_rel * x_size)
        left_y = round(blinds_left_y_cor_rel * y_size)

        bottom_x = round(blinds_bottom_x_cor_rel * x_size)
        bottom_y = round(blinds_bottom_y_cor_rel * y_size)

        x_size = round(blinds_x_size_rel * x_size)
        y_size = round(blinds_y_size_rel * y_size)

        top = im[top_y:top_y + y_size, top_x:top_x + x_size]
        left = im[left_y:left_y + y_size, left_x:left_x + x_size]
        right = im[right_y:right_y + y_size, right_x:right_x + x_size]
        bottom = im[bottom_y:bottom_y + y_size, bottom_x:bottom_x + x_size]

        return top, left, right, bottom

    for pic in pic_list:
        im = cv2.imread(pic)
        dealer_top, dealer_left, dealer_right, dealer_bottom = strip_data_dealer(im)
        comm_1, comm_2, comm_3, comm_4, comm_5 = strip_data_community_cards(im)
        top_left, top_right, right_left, right_right, left_left, left_right = strip_data_villain_cards(im)
        cards_bottom_left, cards_bottom_right = strip_data_bottom_cards(im)
        #blinds_top, blinds_left, blinds_right, blinds_bottom = strip_data_blinds(im)

        short_name = pic.split("\\")[-1].split('.')[0]
        cv2.imwrite("./pictures/Data/Button/"+short_name+"_dealer_top.png", dealer_top)
        cv2.imwrite("./pictures/Data/Button/"+short_name+"_dealer_left.png", dealer_left)
        cv2.imwrite("./pictures/Data/Button/"+short_name+"_dealer_right.png", dealer_right)
        cv2.imwrite("./pictures/Data/Button/"+short_name+"_dealer_bottom.png", dealer_bottom)

        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_comm_1.png", comm_1)
        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_comm_2.png", comm_2)
        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_comm_3.png", comm_3)
        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_comm_4.png", comm_4)
        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_comm_5.png", comm_5)

        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_top_left.png", top_left)
        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_top_right.png", top_right)
        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_right_left.png", right_left)
        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_right_right.png", right_right)
        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_left_left.png", left_left)
        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_left_right.png", left_right)

        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_bottom_left.png", cards_bottom_left)
        cv2.imwrite("./pictures/Data/Suit/"+short_name+"_bottom_right.png", cards_bottom_right)

        print("Done with: " + pic)


if __name__ == "__main__":
    dir_path = "./pictures/Running/*.png"
    files = glob.glob(dir_path)
    files.sort(key=extract_order)

    strip_data(pic_list=files)

    # hands_list = find_hands(ordered_pic_list=files)
    # for hand in hands_list:
    #    print(hand)

    """
    
    hand_end = True
    for idx, pic in enumerate(files):
        im = cv2.imread(pic)
        button_pos = find_dealer_location(im=im)

        dealer_location = None
        if button_pos[0] == 1:
            dealer_location = Location.Top
        if button_pos[1] == 1:
            dealer_location = Location.Left
        if button_pos[2] == 1:
            dealer_location = Location.Right
        if button_pos[3] == 1:
            dealer_location = Location.Bottom

        if dealer_location is None:
            continue

        print(pic)

        loc_pos, loc_act = parse_location_position(init_photo=im, dealer_location=dealer_location)
        hist = find_history(location_position_map=loc_pos, location_action_map=loc_act)

        c = 0
        for loc in Location:
            c += int(loc_act[loc] is None)

        if c == 4:
            loc_pos, loc_act = parse_location_position(init_photo=cv2.imread(files[idx-1]), dealer_location=dealer_location)
            hist = find_history(location_position_map=loc_pos, location_action_map=loc_act)
            print(hist)

        if not prev_button_pos == button_pos:
            hand_end = not hand_end
            if hand_end:
                total_pot_parse_res = parse_total_pot(final_photo=cv2.imread(files[idx-1]), allin=2.0, sb=0.1, bb=0.25)
                print(files[idx-1], total_pot_parse_res)
            else:
                pass

        prev_button_pos = button_pos
"""