import torch
import torch.nn as nn
import torchvision.models as models

class SiameseNetwork(nn.Module):
    def __init__(self):
        super(SiameseNetwork, self).__init__()
        # Use ResNet18 as the feature extractor
        self.resnet = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
        # Remove the final classification layer
        self.resnet = nn.Sequential(*(list(self.resnet.children())[:-1]))

        # Add a fully connected layer to project features into a common space
        self.fc = nn.Sequential(
            nn.Linear(512, 256), nn.ReLU(inplace=True), nn.Linear(256, 128)
        )

    def forward_once(self, x):
        # Extract features
        output = self.resnet(x)
        output = output.view(output.size(0), -1)
        output = self.fc(output)
        return output

    def forward(self, input1, input2):
        # Pass both images through the same network
        output1 = self.forward_once(input1)
        output2 = self.forward_once(input2)
        return output1, output2
