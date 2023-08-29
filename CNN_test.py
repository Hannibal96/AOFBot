from CNN_utils import classify_image, blinds_resize, suit_resize, value_resize, dealer_resize, action_resize
import cv2
import torch
import glob


if __name__ == "__main__":
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    blinds_model = torch.load("./trained_Blinds_model.torch")
    action_model = torch.load("./trained_Action_model.torch")
    button_model = torch.load("./trained_Button_model.torch")
    suit_model = torch.load("./trained_Suit_model.torch")
    value_model = torch.load("./trained_Value_model.torch")

    model_dict = {}
    resize_dict = {}

    model_dict["Action"] = action_model
    model_dict["Blinds"] = blinds_model
    model_dict["Button"] = button_model
    model_dict["Suit"] = suit_model
    model_dict["Value"] = value_model

    resize_dict["Action"] = action_resize
    resize_dict["Blinds"] = blinds_resize
    resize_dict["Button"] = dealer_resize
    resize_dict["Suit"] = suit_resize
    resize_dict["Value"] = value_resize

    data_path = "./pictures/Data/"

    for task_path in glob.glob(f'{data_path}/*/'):
        task = task_path.split("\\")[-2]
        model = model_dict[task]
        resize = resize_dict[task]
        for category in glob.glob(f'{task_path}/*'):
            counter = 0
            print(category)
            for item in glob.glob(f'{category}/*'):
                counter += 1
                print(classify_image(model=model, im=cv2.imread(item), resize=resize, device=device), end=", ")
                if counter > 5:
                    print()
                    break
        print()




"""
    for

    for i in range(3):
        print(classify_image(model=blinds_model, im=cv2.imread(f'./pictures/Data/Blinds/Nothing/Blinds_Nothing_{i}.png'), resize=blinds_resize, device=device))

    for i in range(3):
        print(classify_image(model=action_model, im=cv2.imread('./pictures/Data/Action/Yes/Action_Yes_0.png'), resize=action_resize, device=device))

    print(classify_image(model=button_model, im=cv2.imread('./pictures/Data/Button/Yes/Button_Yes_0.png'), resize=dealer_resize, device=device))

    print(classify_image(model=suit_model, im=cv2.imread('./pictures/Data/Suit/Club/Suit_Club_10.png'), resize=suit_resize, device=device))

    print(classify_image(model=value_model, im=cv2.imread('./pictures/Data/Value/10/Value_10_0.png'), resize=value_resize, device=device))

"""