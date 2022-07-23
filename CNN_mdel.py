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
