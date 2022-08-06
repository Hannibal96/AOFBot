import cv2

from CNN_data import get_data_loader
from CNN_utils import *
import torch
import torch.nn as nn
from CNN_mdel import CnnClassifier, get_model

if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    criterion = nn.CrossEntropyLoss()

    button_dir = "pictures\Data\Button"
    blinds_dir = "pictures\Data\Blinds"
    action_dir = "pictures\Data\Action"
    suit_dir = "pictures\Data\Suit"
    value_dir = "pictures\Data\Value"

    hpo(data_dir=button_dir, resize=dealer_resize, criterion=criterion, device=device)
    hpo(data_dir=blinds_dir, resize=blinds_resize, criterion=criterion, device=device)
    hpo(data_dir=action_dir, resize=action_resize, criterion=criterion, device=device)
    hpo(data_dir=suit_dir, resize=suit_resize, criterion=criterion, device=device)
    hpo(data_dir=value_dir, resize=value_resize, criterion=criterion, device=device)

    #print(classify_image(model=blinds_model, im=cv2.imread('./pictures/Data/Blinds/Nothing/Blinds_Nothing_0.png'), device=device, resize=blinds_resize))
