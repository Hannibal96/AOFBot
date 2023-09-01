import torchvision
from torchvision import transforms
import torch


def get_data_loader(data_dir, width=16, height=24, batch_size=128, train=False, split=0.8):
    transform = {
        'train': transforms.Compose([
            transforms.Resize([height, width]),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2),
            transforms.RandomAffine(degrees=(-10, 10), translate=(0.1, 0.3), scale=(0.5, 0.8)),
            #transforms.GaussianBlur(kernel_size=1),
            transforms.ToTensor(),
        ]),
        'test': transforms.Compose([
            transforms.Resize([height, width]),
            transforms.ToTensor(),
        ])
    }

    dataset = torchvision.datasets.ImageFolder(root=data_dir, transform=transform['train'] if train else transform['test'])
    lengths = [int(split * len(dataset)), len(dataset) - int(split * len(dataset))]
    train_dataset, validation_dataset = torch.utils.data.random_split(dataset, lengths)

    train_data_loader = torch.utils.data.DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    validation_data_loader = torch.utils.data.DataLoader(dataset=validation_dataset, batch_size=batch_size, shuffle=True, num_workers=0)

    return train_data_loader, validation_data_loader
