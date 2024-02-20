import numpy as np
import matplotlib.pyplot as plt
import torch
from PIL import Image
from torchvision import transforms
from CNN_data import get_data_loader
from CNN_mdel import get_model
import os
from Enums import *
import copy


blinds_resize = (48, 48)
dealer_resize = (24, 24)
action_resize = (16, 64)
suit_resize = (32, 64)
value_resize = (32, 64)

blinds_label_converter = {0: Action.AllIn,
                          1: Position.BigBlind,
                          2: Position.SittingOut,
                          3: Position.SmallBlind}

suit_label_converter = {0: Suits.Club,
                        1: Suits.Diamond,
                        2: Suits.Heart,
                        3: Suits.Spade}

value_label_converter = {0: Number.Ten,
                         1: Number.Duce,
                         2: Number.Three,
                         3: Number.Four,
                         4: Number.Five,
                         5: Number.Six,
                         6: Number.Seven,
                         7: Number.Eight,
                         8: Number.Nine,
                         9: Number.Ace,
                         10: Number.Jack,
                         11: Number.King,
                         12: Number.Queen}


def plot_images(images, classification=''):
    for image in images:
        image = np.swapaxes(image, 0, 1)
        image = np.swapaxes(image, 1, 2)
        plt.imshow(image)
        plt.title('Sample'+str(classification))
        plt.show()


def train_epoch(model, optimizer, loss_func, train_dataset, device):
    model.train()
    total_loss = 0
    total_correct = 0
    total_samples = 0
    for idx, data in enumerate(train_dataset):
        images, labels = data
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)

        loss = loss_func(outputs, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_samples += labels.size(0)
        total_loss += loss.data.item()
        _, predicted = torch.max(outputs.data, 1)
        total_correct += (predicted == labels).sum().item()

    return total_loss / total_samples, total_correct / total_samples


def eval_epoch(model, loss_func, test_set, device):
    model.eval()
    total_loss = 0
    total_correct = 0
    total_samples = 0
    for idx, data in enumerate(test_set):
        images, labels = data
        images = images.to(device)
        labels = labels.to(device)

        outputs = model(images)

        loss = loss_func(outputs, labels)

        total_samples += labels.size(0)
        total_loss += loss.data.item()
        _, predicted = torch.max(outputs.data, 1)
        total_correct += (predicted == labels).sum().item()

    return total_loss / total_samples, total_correct / total_samples


def train_and_eval(model, optimizer, loss_func, dataset, testset, epochs, task, device):

    train_loss_list, train_acc_list, eval_loss_list, eval_acc_list = [], [], [], []
    best_eval_acc = 0
    best_train_acc = 0
    best_epoch_idx = -1
    best_model_weights = None

    eval_loss, eval_acc = eval_epoch(model=model, loss_func=loss_func, test_set=testset, device=device)
    print("*" * 25)
    print("*" * 10, task, "*" * 3, 'LR=', str(optimizer.param_groups[0]['lr']), "*" * 3, 'BS=', str(dataset.batch_size))
    print("*" * 25)
    print(model)
    print("#Epoch {} - Eval Loss: {:.3f}, Eval Accuracy: {:.3f}".format(0, eval_loss, eval_acc*100))

    for epoch in range(1, epochs+1):
        train_loss, train_acc = train_epoch(model=model, optimizer=optimizer, loss_func=loss_func, train_dataset=dataset, device=device)
        eval_loss, eval_acc = eval_epoch(model=model, loss_func=loss_func, test_set=testset, device=device)
        print("#Epoch {} - Train Loss: {:.5f}, Train Accuracy: {:.2f}, Eval Loss: {:.5f}, Eval Accuracy: {:.2f}"
              .format(epoch, train_loss, 100*train_acc, eval_loss, 100*eval_acc))
        train_loss_list.append(train_loss)
        train_acc_list.append(train_acc * 100)
        eval_loss_list.append(eval_loss)
        eval_acc_list.append(eval_acc * 100)
        if eval_acc > best_eval_acc or (eval_acc == best_eval_acc and train_acc > best_train_acc):
            best_eval_acc = eval_acc
            best_train_acc = train_acc
            best_epoch_idx = epoch
            best_model_weights = copy.deepcopy(model.state_dict())

        if (train_acc == 1.0 and eval_acc == 1.0) or train_loss < 1e-6:
            break

    model.load_state_dict(best_model_weights)
    return train_loss_list, train_acc_list, eval_loss_list, eval_acc_list, best_epoch_idx


def classify_image(model, im, resize, device):
    im = Image.fromarray(np.uint8(im)).convert('RGB')
    transfer = transforms.Compose([transforms.Resize(resize), transforms.ToTensor()])
    im = torch.unsqueeze(transfer(im), dim=0).to(device)
    model.eval()
    _, predicted = torch.max(model(im).data, 1)
    return predicted.item()


def hpo(data_dir, resize, criterion, device, epochs=100, path=None):

    task = data_dir.split('/')[-1]
    output = len(os.listdir(data_dir))

    params_list = [
        (0, 1),
        (0, 2),
        (0, 3),
        (1, 1),
        (1, 2),
        (1, 3),
        (1, 2),
        (2, 2),
        (2, 3),
        (3, 1),
        (3, 2),
        (3, 3),
        (4, 1),
        (4, 2),
        (4, 3),
        (4, 4),
    ]
    batch_list = [4, 16, 64, 128, 256]
    lr_list = [1e-2, 5e-2, 1e-3, 5e-3, 1e-4, 5e-4]

    for params in params_list:
        with open(f"./NN_models/{task}_results.log", "a") as file:
            file.write("="*25+"\n")
            file.write(f"Starting CV={params[0]} FC={params[1]}\n")
        best_acc_eval_params = 0
        best_acc_train_params = 0
        for batch_size in batch_list:
            for lr in lr_list:
                data_train, data_validation = get_data_loader(data_dir=data_dir, batch_size=batch_size, height=resize[0], width=resize[1])

                conv, fc = params
                model_str = 'CV='+str(conv)+' FC='+str(fc)+' BS='+str(batch_size)+' lr='+str(lr)

                model = get_model(width=resize[1], height=resize[0], channels=3, output=output, conv=conv, fc=fc).to(device)
                optimizer = torch.optim.Adam(model.parameters(), lr=lr)
                train_loss_list, train_acc_list, eval_loss_list, eval_acc_list, best_epoch_idx = train_and_eval(model=model, optimizer=optimizer, loss_func=criterion,
                                                                                                                dataset=data_train, testset=data_validation,
                                                                                                                epochs=epochs, task=task, device=device)

                last_eval_acc = eval_acc_list[best_epoch_idx-1]         # its not last, its best but for compatibiility left with misleading name
                last_train_acc = train_acc_list[best_epoch_idx-1]
                print(f"{model_str}: best epoch-{best_epoch_idx} with train={last_train_acc}, eval={last_eval_acc}")
                with open(f"./NN_models/{task}_results.log", "a") as file:
                    file.write(f"{model_str}: train={last_train_acc}, eval={last_eval_acc}\n")

                if (last_eval_acc > best_acc_eval_params) or (last_eval_acc == best_acc_eval_params and last_train_acc > best_acc_train_params):
                    print(f"-I- Saved {task} with {model_str}")
                    torch.save(model, f"./NN_models/last_run/{task}_CV={params[0]}_FC={params[1]}.torch")
                    best_acc_eval_params = last_eval_acc
                    best_acc_train_params = last_train_acc

                    if path is None:
                        continue

                    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
                    axes[0].plot(train_loss_list, label="Train")
                    axes[0].plot(eval_loss_list, label="Eval")
                    axes[0].set_title(task + " " + model_str + " -Loss")
                    axes[0].legend()
                    axes[0].grid()
                    axes[1].plot(train_acc_list, label="Train")
                    axes[1].plot(eval_acc_list, label="Eval")
                    axes[1].set_title(task + " " + model_str + " -Accuracy")
                    axes[1].legend()
                    axes[1].grid()
                    plt.savefig(f"{path}/{task}_{model_str}_{round(last_eval_acc, 1)}%.png")
                    plt.clf()

                if last_eval_acc == 100.0 and last_train_acc == 100.0:
                    return

        with open(f"./NN_models/{task}_results.log", "a") as file:
            file.write("\n\n")

