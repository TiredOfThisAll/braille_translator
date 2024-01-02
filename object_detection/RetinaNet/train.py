import torch

from object_detection.RetinaNet.utils import load_data
from object_detection.RetinaNet.model import create_retinanet


epochs = 100


def train():
    torch.cuda.empty_cache()

    trainloader, testloader = load_data()

    model = create_retinanet(num_classes=64, trainable_backbone_layers=5, detections_per_img=800, topk_candidates=1600).cuda()

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    model.train()


    for epoch in range(epochs):
        i = 0
        train_loader_len = len(trainloader)
        for i, data in enumerate(trainloader, 0):

            images, targets = data

            optimizer.zero_grad()
            
            images = [x.cuda() for x in images]
            for target in targets:
                target['boxes'] = target['boxes'].cuda()
                target['labels'] = target['labels'].cuda()

            loss = model(images, targets)

            loss = sum(loss for loss in loss.values())
            loss.backward()
            optimizer.step()

            if i % 10 == 0:
                print(f"Epoch {epoch + 1}/100, Batch {i}/{train_loader_len}, Loss: {loss.item()}")
                with open("results.txt", "+w") as file:
                    file.write(f"Epoch {epoch + 1}/100, Batch {i}/{train_loader_len}, Loss: {loss.item()}")

    torch.save(model, f"model_{epoch}.pth")
