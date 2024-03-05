import torch
import os

proj_path = os.path.join(os.getcwd(), "src", "braille")
model_path = os.path.join(proj_path, "weights", "model_299.pth")


def load_model():
    loaded_net = torch.load(model_path)

    return loaded_net
