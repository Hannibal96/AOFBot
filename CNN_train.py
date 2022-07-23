import cv2

from CNN_data import get_data_loader
from CNN_utils import plot_images, train_epoch, eval_epoch, train_and_eval, classify_image
import torch
import torch.nn as nn
from CNN_mdel import CnnClassifier


if __name__ == "__main__":

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    criterion = nn.CrossEntropyLoss()

    dir = "pictures\Data\Button"
    dealer_data_train, dealer_data_validation = get_data_loader(data_dir=dir, batch_size=4, height=16, width=16, )

    dealer_model = CnnClassifier(width=16, height=16, channels=3, output=2).to(device)
    dealer_optimizer = torch.optim.Adam(dealer_model.parameters())

    train_and_eval(model=dealer_model, optimizer=dealer_optimizer, loss_func=criterion,
                   dataset=dealer_data_train, testset=dealer_data_validation,
                   epochs=10, task='Dealer', device=device)

    print(classify_image(model=dealer_model, im=cv2.imread('./pictures/Data/Button/Yes/Button_Yes_0.png'), device=device, resize=(16,16)))
    print(classify_image(model=dealer_model, im=cv2.imread('./pictures/Data/Button/Yes/Button_Yes_10.png'), device=device, resize=(16, 16)))
    print(classify_image(model=dealer_model, im=cv2.imread('./pictures/Data/Button/Yes/Button_Yes_20.png'), device=device, resize=(16, 16)))
    print(classify_image(model=dealer_model, im=cv2.imread('./pictures/Data/Button/No/Button_No_0.png'), device=device, resize=(16, 16)))
    print(classify_image(model=dealer_model, im=cv2.imread('./pictures/Data/Button/No/Button_No_10.png'), device=device, resize=(16, 16)))
    print(classify_image(model=dealer_model, im=cv2.imread('./pictures/Data/Button/No/Button_No_5.png'), device=device, resize=(16, 16)))



