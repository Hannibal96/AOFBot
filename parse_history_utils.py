from Enums import *
import os
import glob
import os
import cv2
from utils_table import *
import torch
from CNN_utils import *
import pytesseract
import pickle


pot_top_x_cor_rel = 400 / 968
pot_top_y_cor_rel = 245 / 696
pot_x_size_rel = 165 / 968
pot_y_size_rel = 40 / 696


class History(Enum):
    CO = 0
    DE = 1
    SB = 2
    BB = 3

    CO_DE = 4
    CO_SB = 5
    CO_BB = 6
    DE_SB = 7
    DE_BB = 8
    SB_BB = 9

    CO_DE_SB = 10
    CO_DE_BB = 11
    CO_SB_BB = 12
    DE_SB_BB = 13

    CO_DE_SB_BB = 14


def extract_order(file_name):
    base_name = os.path.basename(file_name)
    color, table_number, hand_counter, inner_counter = base_name.split(".")[0].split("_")
    res = int(table_number) * 1e6 + int(hand_counter) * 1e3 + int(inner_counter)
    return int(res)


def find_dealer_location(im, save=False):
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

    top = im[top_y:top_y+y_size, top_x:top_x+x_size]
    left = im[left_y:left_y + y_size, left_x:left_x + x_size]
    right = im[right_y:right_y + y_size, right_x:right_x + x_size]
    bottom = im[bottom_y:bottom_y + y_size, bottom_x:bottom_x + x_size]

    nn_dir = "./NN/1.001"
    device = "cpu"
    dealer_model = torch.load(f"{nn_dir}/trained_Button_model.torch").to(device)
    top = classify_image(model=dealer_model, im=top, resize=dealer_resize, device=device)
    left = classify_image(model=dealer_model, im=left, resize=dealer_resize, device=device)
    right = classify_image(model=dealer_model, im=right, resize=dealer_resize, device=device)
    bottom = classify_image(model=dealer_model, im=bottom, resize=dealer_resize, device=device)

    if top == 1:
        return Location.Top
    if left == 1:
        return Location.Left
    if right == 1:
        return Location.Right
    if bottom == 1:
        return Location.Bottom

    return None

