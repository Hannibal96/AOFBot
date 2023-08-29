from AOFTable import AOFTable, win32gui


def find_running_tables_window():
    def tables_collector(hwnd, tables_list, sub_string="AFH", not_sub_string="Chat"):
        if sub_string in win32gui.GetWindowText(hwnd) and not_sub_string not in win32gui.GetWindowText(hwnd):
            tables_list.append(hwnd)

    aof_tables_list = []
    win32gui.EnumWindows(tables_collector, aof_tables_list)

    return aof_tables_list


def set_running_tables(tables_list, dealer_model, blinds_model, action_model, value_model, suit_model, device):
    running_tables_list = []
    for table in tables_list:
        new_table = AOFTable(name=win32gui.GetWindowText(table), hwnd=table, device=device,
                             dealer_model=dealer_model, blinds_model=blinds_model, action_model=action_model,
                             value_model=value_model, suit_model=suit_model)
        running_tables_list.append(new_table)
    return running_tables_list
