import cv2

from CNN_data import get_data_loader
from CNN_utils import *
import torch
import torch.nn as nn
from CNN_mdel import CnnClassifier, get_model


def hpo(data_dir, resize, output, criterion, device):

    task = data_dir.split('\\')[-1]

    params_list = [(0, 1),
                   (0, 2),
                   (1, 1),
                   (1, 2),
                   (1, 3),
                   (2, 2)]

    batch_size = 32
    data_train, data_validation = get_data_loader(data_dir=data_dir, batch_size=batch_size, height=resize[0], width=resize[1])

    for params in params_list:
        conv, fc = params
        model_str = 'CV='+str(conv)+' FC='+str(fc)+' BS='+str(batch_size)

        model = get_model(width=resize[1], height=resize[0], channels=3, output=output, conv=conv, fc=fc).to(device)
        optimizer = torch.optim.Adam(model.parameters())
        train_acc, eval_acc = train_and_eval(model=model, optimizer=optimizer, loss_func=criterion,
                                             dataset=data_train, testset=data_validation,
                                             epochs=50, task=task, device=device, model_str=model_str)
        if train_acc == 1.0 and eval_acc == 1.0:
            break


if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    criterion = nn.CrossEntropyLoss()

    button_dir = "pictures\Data\Button"
    blinds_dir = "pictures\Data\Blinds"
    action_dir = "pictures\Data\Action"
    suit_dir = "pictures\Data\Suit"
    value_dir = "pictures\Data\Value"

    hpo(data_dir=button_dir, resize=dealer_resize, output=2, criterion=criterion, device=device)
    hpo(data_dir=blinds_dir, resize=blinds_resize, output=3, criterion=criterion, device=device)
    hpo(data_dir=action_dir, resize=action_resize, output=2, criterion=criterion, device=device)
    hpo(data_dir=suit_dir, resize=suit_resize, output=4, criterion=criterion, device=device)
    hpo(data_dir=value_dir, resize=value_resize, output=13, criterion=criterion, device=device)

    #print(classify_image(model=blinds_model, im=cv2.imread('./pictures/Data/Blinds/Nothing/Blinds_Nothing_0.png'), device=device, resize=blinds_resize))
