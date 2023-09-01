import cv2

from CNN_data import get_data_loader
from CNN_utils import *
import torch
import torch.nn as nn
from CNN_mdel import CnnClassifier, get_model
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--task", type=str, required=True, nargs='+', choices=["blinds", "dealer", "action", "suit", "value"])
    parser.add_argument("-e", "--epoch", type=int, required=False, default=100)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    criterion = nn.CrossEntropyLoss()

    if "blinds" in args.task:
        blinds_dir = "pictures/Data/Blinds"
        hpo(data_dir=blinds_dir, resize=blinds_resize, criterion=criterion, device=device, path="./train_logs", epochs=args.epoch)

    if "dealer" in args.task:
        button_dir = "pictures/Data/Button"
        hpo(data_dir=button_dir, resize=dealer_resize, criterion=criterion, device=device, path="./train_logs", epochs=args.epoch)

    if "action" in args.task:
        action_dir = "pictures/Data/Action"
        hpo(data_dir=action_dir, resize=action_resize, criterion=criterion, device=device, path="./train_logs", epochs=args.epoch)

    if "suit" in args.task:
        suit_dir = "pictures/Data/Suit"
        hpo(data_dir=suit_dir, resize=suit_resize, criterion=criterion, device=device, path="./train_logs", epochs=args.epoch)

    if "value" in args.task:
        value_dir = "pictures/Data/Value"
        hpo(data_dir=value_dir, resize=value_resize, criterion=criterion, device=device, path="./train_logs", epochs=args.epoch)



