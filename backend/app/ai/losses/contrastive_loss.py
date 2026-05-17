import torch
import torch.nn.functional as F

class ContrastiveLoss(torch.nn.Module):
    def __init__(self, margin=1.0):
        super().__init__()
        self.margin = margin

    def forward(self, out1, out2, label):
        dist = F.pairwise_distance(out1, out2)
        return torch.mean(
            (1 - label) * dist**2 + label * torch.clamp(self.margin - dist, min=0) ** 2
        )
