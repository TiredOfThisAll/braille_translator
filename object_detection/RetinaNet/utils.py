from collections import OrderedDict
from PIL import ImageDraw, ImageFont, Image
from torch.utils.data import Dataset, DataLoader
import torchvision.transforms as transforms
import os
import json
import torch

proj_path = os.getcwd()

sources_path = os.path.join(proj_path, "data", "sources")
dataset_path = os.path.join(proj_path, "data", "labels")

with open(os.path.join(proj_path, "braille_letters.txt"), encoding='utf-8') as file:
    braille = file.read()

with open(os.path.join(proj_path, "braille_to_ru.json"), encoding='utf-8') as file:
    braille_to_ru = json.loads(file.read())

with open(os.path.join(proj_path, "braille_to_eng.json"), encoding='utf-8') as file:
    braille_to_eng = json.loads(file.read())


def flatten(l):
    result = []

    for i in l:
        result += i
    
    return result


def targets_to_lines(boxes, labels, scores):
    min_height = min(map(lambda x: x[3] - x[1], boxes)) * 0.8
    predictions = []
    for i in range(len(boxes)):
        predictions.append({"box": boxes[i], "label": labels[i], "score": scores[i]})

    lines = {}
    for pred in predictions:
        y = pred["box"][1]
        key = list(filter(lambda x: abs(x - y) < min_height, lines.keys()))
        key = None if len(key) == 0 else key[0]
        if key is None:
            lines[y] = [pred]
        else:
            lines[key].append(pred)

    for key in lines:
        lines[key].sort(key=lambda x: x["box"][0])

    sorted_keys = sorted(lines.keys())
    sorted_lines = OrderedDict()
    for key in sorted_keys:
        sorted_lines[key] = lines[key]

    return sorted_lines



def filter_res(boxes, labels, scores):
    min_height = min(map(lambda x: x[3] - x[1], boxes)) * 0.8
    predictions = [{"box": box, "label": label, "score": score} for box, label, score in zip(boxes, labels, scores)]

    lines = {}

    for pred in predictions:
        y = pred["box"][1]
        key = list(filter(lambda x: abs(x - y) < min_height, lines.keys()))
        key = None if len(key) == 0 else key[0]
        if key is None:
            lines[y] = [pred]
        else:
            lines[key].append(pred)

    for key in lines:
        lines[key].sort(key=lambda x: x["box"][0])

    nms_predictions = {}

    for key, line in lines.items():
        nms_predictions[key] = []

        for i in range(0, len(line)):
            left_x1 = line[i]["box"][0]
            left_y1 = line[i]["box"][1]
            left_x2 = line[i]["box"][2]
            left_y2 = line[i]["box"][3]
            left_width = left_x2 - left_x1
            left_height = left_y2 - left_y1
            score_left = line[i]["score"]
            duplicate_i = None
            for k in range(len(nms_predictions[key])):
                right_x1 = nms_predictions[key][k]["box"][0]
                right_y1 = nms_predictions[key][k]["box"][1]
                right_x2 = nms_predictions[key][k]["box"][2]
                right_y2 = nms_predictions[key][k]["box"][3]
                right_width = right_x2 - right_x1
                right_height = right_y2 - right_y1
                if ((right_x1 - left_x1) ** 2 + (right_y1 - left_y1) ** 2) ** 1/2 < min(left_height, left_width, right_height, right_width) / 2:
                    duplicate_i = k
                    break

            if duplicate_i is not None:
                score_right = nms_predictions[key][duplicate_i]["score"]
                if score_left > score_right:
                    nms_predictions[key][duplicate_i] = line[i]
            else:
                nms_predictions[key].append(line[i])

    sorted_lines = {key: lines[key] for key in sorted(lines.keys())}

    values = flatten(OrderedDict(sorted(nms_predictions.items())).values())

    return list(map(lambda x: x['box'], values)), list(map(lambda x: x['label'], values)), list(map(lambda x: x['score'], values)), sorted_lines

def draw(img, boxes, labels, scores):
    if isinstance(img, str):
        head, tail = os.path.split(img)
        img = Image.open(os.path.join(sources_path, tail))

    draw = ImageDraw.Draw(img)

    color = (0, 255, 0)
    width = 2

    text_color = (50, 50, 255)
    braile_font = ImageFont.truetype("BlistaBraille.ttf", 15)
    font = ImageFont.truetype("arial.ttf", 15)
    

    for box, score, label in zip(boxes, scores, labels):
        if score < 0.5:
            continue
        x1, y1, x2, y2 = box
        width = x2 - x1
        height = y2 - y1
        draw.rectangle((x1, y1, x2, y2), outline=color, width=2)

        label_text = braille_to_ru.get(braille[label], braille[label])

        my_text_size_x, my_text_size_y = draw.textsize(label_text, font=font)
        braille_text_size_x, braille_text_size_y = draw.textsize(braille[label], font=braile_font)
        centred_x = x1 + width / 2 - my_text_size_x
        centred_y = y1 + height / 2 - my_text_size_y / 2
        draw.text((centred_x, centred_y), label_text, fill=text_color, font=font)
        draw.text((x1 + width / 2, y1 + height / 2 - braille_text_size_y / 2), braille[label], fill=text_color, font=braile_font)

    img.show()

    return img


def load_data():
    transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])

    labels_path = os.path.join(proj_path, "data", "labels")
    targets = []
    for label_file in os.listdir(labels_path):
        with open(os.path.join(labels_path, label_file)) as file:
            labels_dict = json.load(file)
            boxes = []
            labels = []
            for label in labels_dict["labels"]:
                boxes.append(label["box"])
                labels.append(label["class"])
            targets.append({"image": labels_dict["image"], "targets": {"boxes": boxes, "labels": labels}})


    trainset_len = round(len(targets) * 0.9)

    trainset = BrailleDataset(targets[:trainset_len], transform)
    testset = BrailleDataset(targets[trainset_len:], transform)

    trainloader = DataLoader(trainset, batch_size=1, shuffle=True, num_workers=1, collate_fn=collate_fn)
    testloader = DataLoader(testset, batch_size=1, shuffle=False, num_workers=1, collate_fn=collate_fn)

    return trainloader, testloader


def collate_fn(batch):
    images = [item[0] for item in batch]
    targets = [item[1] for item in batch]

    return images, targets


class BrailleDataset(Dataset):
    def __init__(self, data, transform=None):
        self.data = data
        self.transform = transform

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        img_path = self.data[idx]['image']
        image = {"image": Image.open(img_path), "path": img_path}
        targets = self.data[idx]['targets']
        
        if self.transform:
            image['image'] = self.transform(image['image'])
            targets['boxes'] = torch.tensor(targets['boxes'])
            targets['labels'] = torch.tensor(targets['labels'], dtype=torch.int)
        
        return image, targets
