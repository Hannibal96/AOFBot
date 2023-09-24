from AOFTable import AOFTable, win32gui
import time
from utils_player import find_running_tables_window, set_running_tables
import torch
from torch.multiprocessing import Process, Queue
import time


def run_table_iter(table, saver):
    if table.is_table_visible():
        table.fg_table()

        if table.find_button_location(save=saver):
            table.update_hand_counter()

        if table.is_my_turn(save=saver):
            table.find_blinds_location(save=saver)
            table.figure_table_structure()
            table.figure_state()
            table.read_holding_cards(save=saver)

            print(table)
            table.act()
            #table.read_hud(save=True)


def run_table(table, saver, lock):
    while True:
        run_table_iter(table=table, saver=saver)


if __name__ == "__main__":
    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = "cpu"
    MP = True
    saver = False
    crusher = False

    print('Device:', device)
    dealer_model = torch.load("./trained_Button_model.torch").to(device)
    blinds_model = torch.load("./trained_Blinds_model.torch").to(device)
    action_model = torch.load("./trained_Action_model.torch").to(device)
    suit_model = torch.load("./trained_Suit_model.torch").to(device)
    value_model = torch.load("./trained_Value_model.torch").to(device)

    print('Models Loaded')

    aof_tables_list = find_running_tables_window()
    running_tables = set_running_tables(tables_list=aof_tables_list,
                                        dealer_model=dealer_model, blinds_model=blinds_model, action_model=action_model, value_model=value_model, suit_model=suit_model,
                                        device=device, crusher=crusher)
    if MP:
        torch.multiprocessing.set_start_method('spawn')
        processes = []

        for table in running_tables:
            process = Process(target=run_table, args=(table, None, saver))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()

    else:
        while True:
            for table in running_tables:
                run_table_iter(table, saver=saver)
                #table.read_community_cards(save=False)
                #table.read_villains_holding_cards(save=False)
