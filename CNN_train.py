import cv2

from CNN_data import get_data_loader
from CNN_utils import plot_images, train_epoch, eval_epoch, train_and_eval, classify_image, blinds_resize, dealer_resize
import torch
import torch.nn as nn
from CNN_mdel import CnnClassifier, get_model


if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    criterion = nn.CrossEntropyLoss()

    button_dir = "pictures\Data\Button"
    blinds_dir = "pictures\Data\Blinds"

    dealer_data_train, dealer_data_validation = get_data_loader(data_dir=button_dir, batch_size=4, height=dealer_resize[0], width=dealer_resize[1])

    #dealer_model = CnnClassifier(width=dealer_resize[1], height=dealer_resize[0], channels=3, output=2).to(device)
    dealer_model = get_model(width=dealer_resize[1], height=dealer_resize[0], channels=3, output=2, conv=0, fc=2).to(device)
    dealer_optimizer = torch.optim.Adam(dealer_model.parameters())

    train_and_eval(model=dealer_model, optimizer=dealer_optimizer, loss_func=criterion,
                   dataset=dealer_data_train, testset=dealer_data_validation,
                   epochs=10, task='Dealer', device=device)

    blinds_data_train, blinds_data_validation = get_data_loader(data_dir=blinds_dir, batch_size=4, height=blinds_resize[0], width=blinds_resize[1])

    #blinds_model = CnnClassifier(width=blinds_resize[1], height=blinds_resize[0], channels=3, output=3).to(device)
    blinds_model = get_model(width=blinds_resize[1], height=blinds_resize[0], channels=3, output=3, conv=1, fc=2).to(device)
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







