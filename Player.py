from AOFTable import AOFTable, win32gui
import time
from utils_player import find_running_tables_window, set_running_tables


aof_tables_list = find_running_tables_window()
running_tables = set_running_tables(aof_tables_list)

while True:
    for table in running_tables:
        if table.is_table_visible():
            table.fg_table()
            print(table)
            table.screen_shot()
            table.find_button_location()
            time.sleep(0.5)
