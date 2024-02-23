from utils_player import *
import torch
from torch.multiprocessing import Process, Lock
import optuna
import glob

if __name__ == "__main__":

    # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    device = "cpu"
    MP = True
    saver = False
    crusher = False
    tess_models = 1

    print('Device:', device)

    #nn_dir = "./NN_models/1.001"
    nn_dir = "./NN_models/3.1"

    dealer_model_path = glob.glob(f"{nn_dir}/*Button*.torch")[0]
    blinds_model_path = glob.glob(f"{nn_dir}/*Blinds*.torch")[0]
    action_model_path = glob.glob(f"{nn_dir}/*Action*.torch")[0]
    suit_model_path = glob.glob(f"{nn_dir}/*Suit*.torch")[0]
    value_model_path = glob.glob(f"{nn_dir}/*Value*.torch")[0]

    dealer_model = torch.load(dealer_model_path).to(device)
    blinds_model = torch.load(blinds_model_path).to(device)
    action_model = torch.load(action_model_path).to(device)
    suit_model = torch.load(suit_model_path).to(device)
    value_model = torch.load(value_model_path).to(device)

    optuna_name = f"tess_opt_{tess_models}"
    opt_study = optuna.create_study(study_name=f'{optuna_name}',
                                         storage=f'sqlite:///./Optuna/{optuna_name}.db ',
                                         direction='maximize', load_if_exists=True)
    tess_models = opt_study

    print('Models Loaded')

    aof_tables_list = find_running_tables_window()
    running_tables = set_running_tables(tables_list=aof_tables_list,
                                        dealer_model=dealer_model, blinds_model=blinds_model, action_model=action_model, value_model=value_model, suit_model=suit_model,
                                        device=device, crusher=crusher, tess_models=tess_models)
    if MP:
        #torch.multiprocessing.set_start_method('spawn')
        lock = Lock()
        processes = []

        for table in running_tables:
            process = Process(target=run_table, args=(table, saver, lock))
            process.start()
            processes.append(process)

        for process in processes:
            process.join()

    else:
        while True:
            for table in running_tables:
                run_table_iter(table, saver=saver, lock=None)
                #table.read_community_cards(save=False)
                #table.read_villains_holding_cards(save=False)
