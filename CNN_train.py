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

    """
    suit_data_train, suit_data_validation = get_data_loader(data_dir=suit_dir, batch_size=4, height=suit_resize[0], width=suit_resize[1])
    suit_model = get_model(width=suit_resize[1], height=suit_resize[0], channels=3, output=4, conv=0, fc=1).to(device)
    suit_optimizer = torch.optim.Adam(suit_model.parameters())
    train_and_eval(model=suit_model, optimizer=suit_optimizer, loss_func=criterion,
                   dataset=suit_data_train, testset=suit_data_validation,
                   epochs=10, task='Suit', device=device)
    print('Suit Test')
    print(classify_image(model=suit_model, im=cv2.imread('./pictures/Data/Suit/Spade/Suit_Spade_0.png'), device=device, resize=suit_resize))
    print(classify_image(model=suit_model, im=cv2.imread('./pictures/Data/Suit/Spade/Suit_Spade_10.png'), device=device, resize=suit_resize))
    print(classify_image(model=suit_model, im=cv2.imread('./pictures/Data/Suit/Heart/Suit_Heart_0.png'), device=device, resize=suit_resize))
    print(classify_image(model=suit_model, im=cv2.imread('./pictures/Data/Suit/Heart/Suit_Heart_10.png'), device=device, resize=suit_resize))
    print(classify_image(model=suit_model, im=cv2.imread('./pictures/Data/Suit/Club/Suit_Club_0.png'), device=device, resize=suit_resize))
    print(classify_image(model=suit_model, im=cv2.imread('./pictures/Data/Suit/Club/Suit_Club_10.png'), device=device, resize=suit_resize))
    print(classify_image(model=suit_model, im=cv2.imread('./pictures/Data/Suit/Diamond/Suit_Diamond_0.png'), device=device, resize=suit_resize))
    print(classify_image(model=suit_model, im=cv2.imread('./pictures/Data/Suit/Diamond/Suit_Diamond_10.png'), device=device, resize=suit_resize))
    """

    value_data_train, value_data_validation = get_data_loader(data_dir=value_dir, batch_size=4, height=value_resize[0], width=value_resize[1])
    value_model = get_model(width=value_resize[1], height=value_resize[0], channels=3, output=13, conv=1, fc=2).to(device)
    value_optimizer = torch.optim.Adam(value_model.parameters())
    train_and_eval(model=value_model, optimizer=value_optimizer, loss_func=criterion,
                   dataset=value_data_train, testset=value_data_validation,
                   epochs=50, task='Value', device=device)


    """ 
    action_data_train, action_data_validation = get_data_loader(data_dir=action_dir, batch_size=4, height=action_resize[0], width=action_resize[1])
    action_model = get_model(width=action_resize[1], height=action_resize[0], channels=3, output=2, conv=0, fc=2).to(device)
    action_optimizer = torch.optim.Adam(action_model.parameters())
    train_and_eval(model=action_model, optimizer=action_optimizer, loss_func=criterion,
                   dataset=action_data_train, testset=action_data_validation,
                   epochs=10, task='Action', device=device)


    dealer_data_train, dealer_data_validation = get_data_loader(data_dir=button_dir, batch_size=4, height=dealer_resize[0], width=dealer_resize[1])
    dealer_model = get_model(width=dealer_resize[1], height=dealer_resize[0], channels=3, output=2, conv=0, fc=2).to(device)
    dealer_optimizer = torch.optim.Adam(dealer_model.parameters())
    train_and_eval(model=dealer_model, optimizer=dealer_optimizer, loss_func=criterion,
                   dataset=dealer_data_train, testset=dealer_data_validation,
                   epochs=10, task='Dealer', device=device)
    """
    """
    blinds_data_train, blinds_data_validation = get_data_loader(data_dir=blinds_dir, batch_size=4, height=blinds_resize[0], width=blinds_resize[1])
    blinds_model = get_model(width=blinds_resize[1], height=blinds_resize[0], channels=3, output=3, conv=1, fc=1).to(device)
    blinds_optimizer = torch.optim.Adam(blinds_model.parameters())
    train_and_eval(model=blinds_model, optimizer=blinds_optimizer, loss_func=criterion,
                   dataset=blinds_data_train, testset=blinds_data_validation,
                   epochs=10, task='Blinds', device=device)

    print('Dealer Test')
    print(classify_image(model=dealer_model, im=cv2.imread('./pictures/Data/Button/Yes/Button_Yes_0.png'), device=device, resize=dealer_resize))
    print(classify_image(model=dealer_model, im=cv2.imread('./pictures/Data/Button/Yes/Button_Yes_10.png'), device=device, resize=dealer_resize))
    print(classify_image(model=dealer_model, im=cv2.imread('./pictures/Data/Button/No/Button_No_0.png'), device=device, resize=dealer_resize))
    print(classify_image(model=dealer_model, im=cv2.imread('./pictures/Data/Button/No/Button_No_10.png'), device=device, resize=dealer_resize))

    print('Blinds Test')
    print(classify_image(model=blinds_model, im=cv2.imread('./pictures/Data/Blinds/Nothing/Blinds_Nothing_0.png'), device=device, resize=blinds_resize))
    print(classify_image(model=blinds_model, im=cv2.imread('./pictures/Data/Blinds/Nothing/Blinds_Nothing_10.png'), device=device, resize=blinds_resize))
    print(classify_image(model=blinds_model, im=cv2.imread('./pictures/Data/Blinds/BB/Blinds_BB_0.png'), device=device, resize=blinds_resize))
    print(classify_image(model=blinds_model, im=cv2.imread('./pictures/Data/Blinds/BB/Blinds_BB_10.png'), device=device, resize=blinds_resize))
    print(classify_image(model=blinds_model, im=cv2.imread('./pictures/Data/Blinds/SB/Blinds_SB_0.png'), device=device, resize=blinds_resize))
    print(classify_image(model=blinds_model, im=cv2.imread('./pictures/Data/Blinds/SB/Blinds_SB_10.png'), device=device, resize=blinds_resize))
    """







