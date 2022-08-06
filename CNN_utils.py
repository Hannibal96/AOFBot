import numpy as np
import matplotlib.pyplot as plt
import torch
from PIL import Image
from torchvision import transforms
from CNN_data import get_data_loader
from CNN_mdel import get_model


blinds_resize = (48, 48)
dealer_resize = (24, 24)
action_resize = (16, 64)
suit_resize = (32, 64)
value_resize = (32, 64)


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


def train_and_eval(model, optimizer, loss_func, dataset, testset, epochs, task, model_str, device):

    tl = [] ; ta = [] ; el = [] ; ea = []

    eval_loss, eval_acc = eval_epoch(model=model, loss_func=loss_func, test_set=testset, device=device)
    print("*" * 25)
    print("*" * 10, task, "*" * 10)
    print("*" * 25)
    print(model)
    print("#Epoch {} - Eval Loss: {:.3f}, Eval Accuracy: {:.3f}".format(0, eval_loss, eval_acc*100))

    for epoch in range(1, epochs+1):
        train_loss, train_acc = train_epoch(model=model, optimizer=optimizer, loss_func=loss_func, train_dataset=dataset, device=device)
        eval_loss, eval_acc = eval_epoch(model=model, loss_func=loss_func, test_set=testset, device=device)
        print("#Epoch {} - Train Loss: {:.5f}, Train Accuracy: {:.2f}, Eval Loss: {:.5f}, Eval Accuracy: {:.2f}"
              .format(epoch, train_loss, 100*train_acc, eval_loss, 100*eval_acc))
        tl.append(train_loss) ; ta.append(train_acc * 100) ; el.append(eval_loss) ; ea.append(eval_acc * 100)
        if (train_acc == 1.0 and eval_acc == 1.0) or train_loss < 1e-4:
            break

    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    axes[0].plot(tl, label="Train")
    axes[0].plot(el, label="Eval")
    axes[0].set_title(task + " " + model_str+" -Loss")
    axes[0].legend()
    axes[1].plot(ta, label="Train")
    axes[1].plot(ea, label="Eval")
    axes[1].set_title(task + " " + model_str + " -Accuracy")
    axes[1].legend()
    plt.show()

    torch.save(model, "./trained_"+task+"_model.torch")

    return train_acc, eval_acc


def classify_image(model, im, resize, device):
    im = Image.fromarray(np.uint8(im)).convert('RGB')
    transfer = transforms.Compose([transforms.Resize(resize), transforms.ToTensor()])
    im = torch.unsqueeze(transfer(im), dim=0).to(device)
    model.eval()
    _, predicted = torch.max(model(im).data, 1)
    return predicted.item()


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
