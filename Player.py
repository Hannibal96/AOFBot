from AOFTable import AOFTable, win32gui
import time
from utils_player import find_running_tables_window, set_running_tables
import torch

if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print('Device:', device)
    dealer_model = torch.load("./trained_Button_model.torch")
    blinds_model = torch.load("./trained_Blinds_model.torch")
    action_model = torch.load("./trained_Action_model.torch")
    suit_model = torch.load("./trained_Suit_model.torch")
    value_model = torch.load("./trained_Value_model.torch")

    print('Models Loaded')

    aof_tables_list = find_running_tables_window()
    running_tables = set_running_tables(tables_list=aof_tables_list,
                                        dealer_model=dealer_model, blinds_model=blinds_model, action_model=action_model, value_model=value_model, suit_model=suit_model,
                                        device=device)

    while True:
        for table in running_tables:
            if table.is_table_visible():
                table.fg_table()
                if table.find_button_location(save=False):
                    table.update_hand_counter()

                if table.is_my_turn(save=False):
                    table.find_blinds_location(save=True)
                    #table.figure_table_structure()
                    table.read_holding_cards(save=True)
                    print("="*10)
                    print(table.name)
                    print("=" * 10)
                    print(f" * Dealer: {table.curr_dealer_location}")
                    print(f" * SB: {table.curr_sb_location}")
                    print(f" * BB: {table.curr_bb_location}")
                    print(f" * #Hands: {table.hands_counter}")
                    print(table.left_card, table.right_card)

                #table.read_community_cards(save=False)
                #table.read_villains_holding_cards(save=False)
