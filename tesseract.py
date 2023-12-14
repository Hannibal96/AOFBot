import numpy as np
import pytesseract
import cv2
import glob
import os
import matplotlib
import pandas as pd
import optuna
matplotlib.get_backend()


def preprocess_stats(image, threshold):
    dim = len(image.shape)
    assert dim == 2 or dim == 3
    if dim == 3:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image[image > threshold] = 254
    image[image <= threshold] = 0
    return image


def read(im, threshold, config, alpha, beta, scale):
    im = cv2.resize(im, (int(im.shape[1] * scale), int(im.shape[0] * scale)))
    im = cv2.convertScaleAbs(im, alpha=alpha, beta=beta)
    rand_im = preprocess_stats(image=im, threshold=threshold)
    return pytesseract.image_to_string(rand_im, config=config)


def evaluate(labels_csv, only_lighten,
             configs, thresholds, scales, alphas, betas,
             printer=False, dir_path="./pictures/Tes test/"):

    correct = 0
    total = 0
    l_res = []

    for file in glob.glob(os.path.join(dir_path, "*.png")):
        name = file.split('\\')[1].split('.')[0]
        real_text = labels_csv[labels_csv['Name'] == name]['Text'].iloc[0]
        lighten = labels_csv[labels_csv['Name'] == name]['Lighten'].iloc[0]

        if only_lighten and not lighten:
            continue
        d_res = {}

        im = cv2.imread(file)
        for i in range(len(configs)):
            tes_txt = read(im=im, config=configs[i], threshold=thresholds[i], scale=scales[i], beta=betas[i], alpha=alphas[i]).split('\n')[0]
            if tes_txt not in d_res:
                d_res[tes_txt] = 1
            else:
                d_res[tes_txt] += 1

        tes_txt = max(d_res, key=d_res.get)

        if tes_txt == real_text:
            if printer:
                print("V", end=" ")
            l_res.append(1)
        else:
            if printer:
                print("X", end=" ")
            l_res.append(0)

        correct += tes_txt == real_text
        total += 1

    return round(100 * correct / total, 2), np.array(l_res)


def optuna_optimization(trial):
    th_list = []
    scale_list = []
    alpha_list = []
    beta_list = []
    config_list = []

    for i in range(models_num):
        psm = trial.suggest_categorical(f"psm_{i}", [1, 3, 4, 6, 7, 10, 11, 12])
        oem = trial.suggest_categorical(f"oem_{i}", [1, 3])
        threshold = trial.suggest_int(f'threshold_{i}', 0, 255)
        scale = trial.suggest_float(f'scale_{i}', 0.1, 10.0)
        alpha = trial.suggest_float(f"alpha_{i}", 0.0, 5.0)
        beta = trial.suggest_float(f"beta_{i}", -5.0, 5.0)
        config = f'--psm {psm} --oem {oem}'

        th_list.append(threshold)
        scale_list.append(scale)
        alpha_list.append(alpha)
        beta_list.append(beta)
        config_list.append(config)

    acc, res = evaluate(labels_csv=labels_csv,
                        configs=config_list, thresholds=th_list, scales=scale_list, alphas=alpha_list, betas=beta_list,
                        only_lighten=only_lighten, printer=printer, dir_path="./pictures/Tes test/")

    return acc


def optimized_read(im, num, study):

    th_list = []
    scale_list = []
    alpha_list = []
    beta_list = []
    config_list = []

    for i in range(num):
        psm = study.best_params[f"psm_{i}"]
        oem = study.best_params[f"oem_{i}"]
        threshold = study.best_params[f'threshold_{i}']
        scale = study.best_params[f'scale_{i}']
        alpha = study.best_params[f'alpha_{i}']
        beta = study.best_params[f'beta_{i}']
        config = f'--psm {psm} --oem {oem}'

        th_list.append(threshold)
        scale_list.append(scale)
        alpha_list.append(alpha)
        beta_list.append(beta)
        config_list.append(config)

    d_res = {}
    for i in range(len(config_list)):
        tes_txt = read(im=im, config=config_list[i], threshold=th_list[i], scale=scale_list[i], beta=beta_list[i], alpha=alpha_list[i]).split('\n')[0]
        if tes_txt not in d_res:
            d_res[tes_txt] = 1
        else:
            d_res[tes_txt] += 1

    tes_txt = max(d_res, key=d_res.get)
    return tes_txt


if __name__ == "__main__":

    labels_csv = pd.read_csv('./pictures/Tes test/labels.csv')
    only_lighten = False
    printer = False
    models_num = 3

    name = f"tess_opt_{models_num}{int(only_lighten) * '_lighten'}"
    study = optuna.create_study(study_name=f'{name}',
                                storage=f'sqlite:///./Optuna/{name}.db ',
                                direction='maximize', load_if_exists=True)
    study.optimize(optuna_optimization, n_trials=10_000)



