from AOFTable import AOFTable, win32gui
from logger import custom_print
print = custom_print


def find_running_tables_window():
    def tables_collector(hwnd, tables_list, sub_string="AFH", not_sub_string="Chat"):
        if sub_string in win32gui.GetWindowText(hwnd) and not_sub_string not in win32gui.GetWindowText(hwnd):
            tables_list.append(hwnd)

    aof_tables_list = []
    win32gui.EnumWindows(tables_collector, aof_tables_list)

    return aof_tables_list


def set_running_tables(tables_list, dealer_model, blinds_model, action_model, value_model, suit_model, device, tess_models, crusher):
    running_tables_list = []
    for table in tables_list:
        new_table = AOFTable(name=win32gui.GetWindowText(table), hwnd=table, device=device,
                             dealer_model=dealer_model, blinds_model=blinds_model, action_model=action_model,
                             value_model=value_model, suit_model=suit_model, crusher=crusher, tess_models=tess_models)
        running_tables_list.append(new_table)
    return running_tables_list


def run_table_iter(table, saver, lock):
    if table.is_table_visible():
        table.fg_table()

        if table.find_button_location(save=saver):
            table.update_hand_counter()

        if table.is_my_turn(save=saver):
            table.find_blinds_location(save=saver)
            table.figure_table_structure()
            table.figure_state()
            table.read_holding_cards(save=saver)
            table.read_names(save=saver)

            if lock:
                lock.acquire()
                print(table)
                table.act()
                lock.release()

            #table.read_hud(save=True)


def run_table(table, saver, lock):
    while True:
        run_table_iter(table=table, saver=saver, lock=lock)
