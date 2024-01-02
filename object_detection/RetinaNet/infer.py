import torchvision.transforms as transforms
import os
from preprocess_image.binarize import binarize_image
from PIL import ImageDraw, ImageFont, Image
import time

from object_detection.RetinaNet.load_model import load_model
from object_detection.RetinaNet.utils import filter_res, draw

model = load_model().cuda()

model.eval()


def infer_retina(folder_path, result_path=""):
    for file in os.listdir(folder_path):
        print(f"processing {file}")
        img_path = os.path.join(folder_path, file)
        img = binarize_image(img_path)
        transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])
        input_image = transform(img).unsqueeze(0).cuda()
        output = model(input_image)[0]
        boxes = output['boxes'].tolist()
        scores = output['scores'].tolist()
        labels = output['labels'].tolist()
        # orig_img = Image.open(os.path.join(folder_path, file))
        # img.show()
        # draw(orig_img, boxes, labels, scores)
        orig_img = Image.open(os.path.join(folder_path, file))
        filtred_boxes, filtred_labels, filtred_scores, sorted_lines = filter_res(boxes, labels, scores)
        res_image = draw(orig_img, filtred_boxes, filtred_labels, filtred_scores)
        if result_path:
            res_image.save(os.path.join(result_path + file))
