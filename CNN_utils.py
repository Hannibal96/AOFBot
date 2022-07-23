import numpy as np
import matplotlib.pyplot as plt
import torch
from PIL import Image
from torchvision import transforms


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


def classify_image(model, im, resize, device):
    im = Image.fromarray(np.uint8(im)).convert('RGB')
    transfer = transforms.Compose([transforms.Resize(resize), transforms.ToTensor()])
    im = torch.unsqueeze(transfer(im), dim=0).to(device)
    model.eval()
    _, predicted = torch.max(model(im).data, 1)
    return predicted