from AOFTable import AOFTable, win32gui
import time
from utils_player import find_running_tables_window, set_running_tables
import torch

if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print('Device:', device)
    dealer_model = torch.load("./trained_Dealer_model.torch")
    blinds_model = torch.load("./trained_Blinds_model.torch")
    action_model = torch.load("./trained_Action_model.torch")
    print('Models Loaded')

    aof_tables_list = find_running_tables_window()
    running_tables = set_running_tables(tables_list=aof_tables_list,
                                        dealer_model=dealer_model, blinds_model=blinds_model, action_model=action_model,
                                        device=device)

    while True:
        for table in running_tables:
            if table.is_table_visible():
                table.fg_table()
                table.screen_shot()

                if table.find_button_location(save=False):
                    table.find_blinds_location(save=False)
                    table.figure_table_structure()
                    table.update_hand_counter()
                    print(table)
                if table.is_my_turn():
                    print('play')

                table.read_holding_cards(save=True)
                table.read_community_cards(save=True)
                table.read_villains_holding_cards(save=True)
