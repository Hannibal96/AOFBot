from CNN_utils import classify_image, blinds_resize, suit_resize, value_resize, dealer_resize, action_resize
import cv2
import torch
import glob
import matplotlib.pyplot as plt

if __name__ == "__main__":
    device = "cpu"
    #nn_dir = "./NN_models/1.001"
    nn_dir = "./NN_models/3.6"

    dealer_model_path = glob.glob(f"{nn_dir}/*Button*.torch")[0]
    blinds_model_path = glob.glob(f"{nn_dir}/*Blinds*.torch")[0]
    action_model_path = glob.glob(f"{nn_dir}/*Action*.torch")[0]
    suit_model_path = glob.glob(f"{nn_dir}/*Suit*.torch")[0]
    value_model_path = glob.glob(f"{nn_dir}/*Value*.torch")[0]

    dealer_model = torch.load(dealer_model_path, map_location='cuda:0').to(device)
    blinds_model = torch.load(blinds_model_path, map_location='cuda:0').to(device)
    action_model = torch.load(action_model_path, map_location='cuda:0').to(device)
    suit_model = torch.load(suit_model_path, map_location='cuda:0').to(device)
    value_model = torch.load(value_model_path, map_location='cuda:0').to(device)

    model_dict = {#"dealer": (dealer_model, "./pictures/Data/Button/", dealer_resize),
                  #"blinds": (blinds_model, "./pictures/Data/Blinds/", blinds_resize),
                  #"action": (action_model, "./pictures/Data/Action/", action_resize),
                  #"suit": (suit_model, "./pictures/Data/Suit/", suit_resize),
                  "value": (value_model, "./pictures/Data/Value/", value_resize)
    }

    for task, params in model_dict.items():
        print("*"*20)
        print(task)
        model, path, resize = params
        for idx, category in enumerate(glob.glob(f'{path}/*')):
            print(category)
            for item in glob.glob(f'{category}/*'):
                res = classify_image(model=model, im=cv2.imread(item), resize=resize, device=device)
                if res == idx:
                    continue
                print(f"{task}-{category}-{item} Expected {idx}, got {res}")
                plt.imshow(cv2.imread(item))
                plt.title(f"Expected {idx}, got {res}")
                plt.show()

