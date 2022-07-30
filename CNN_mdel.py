import torch
import torch.nn as nn


class CnnClassifier(nn.Module):
    def __init__(self, width, height, channels, output):
        super(CnnClassifier, self).__init__()

        self.height = height
        self.width = width

        self.conv_1 = nn.Conv2d(in_channels=channels, out_channels=16, kernel_size=(7, 7), padding=3)
        self.conv_2 = nn.Conv2d(in_channels=16, out_channels=32, kernel_size=(5, 5), padding=2)
        self.conv_3 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=(3, 3), padding=1)

        self.fc1 = nn.Linear(in_features=height*width*64, out_features=256)
        self.fc2 = nn.Linear(in_features=256, out_features=16)
        self.fc3 = nn.Linear(in_features=16, out_features=output)

        self.relu = nn.LeakyReLU(negative_slope=0.05)
        self.dropout = torch.nn.Dropout(p=0.3)
        self.pre_conv_norm = nn.BatchNorm2d(3)
        self.post_conv_norm = nn.BatchNorm2d(64)

    def forward(self, x):
        x = self.conv_1(x)
        x = self.conv_2(x)
        x = self.conv_3(x)

        x = x.view(-1, self.height * self.width * 64)

        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        x = self.relu(x)
        x = self.fc3(x)

        return x


class Flatten(torch.nn.Module):
    def forward(self, x):
        batch_size = x.shape[0]
        return x.view(batch_size, -1)


def get_model(width, height, channels, output, conv=0, fc=1):
    modules = []

    prev_channel = channels
    for i in range(conv):
        kernel_size = 2 * (conv-i) + 1
        kernel_size = (kernel_size, kernel_size)
        out_channels = 16 * (2**i)

        modules.append(nn.Conv2d(in_channels=prev_channel, out_channels=out_channels, kernel_size=kernel_size, padding=conv-i))

        prev_channel = out_channels

    modules.append(nn.Flatten())

    input = width * height * prev_channel
    lin_factor = int((input / output) ** (1/fc))

    for i in range(fc-1):
        modules.append(nn.Linear(in_features=input, out_features=int(input/lin_factor) ))
        input = int(input/lin_factor)

    modules.append(nn.Linear(in_features=input, out_features=output))

    return nn.Sequential(*modules)



