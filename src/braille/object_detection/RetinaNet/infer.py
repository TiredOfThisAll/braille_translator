import torchvision.transforms as transforms
import os
from braille.preprocess_image.binarize import binarize_image
from PIL import Image

from braille.object_detection.RetinaNet.load_model import load_model
from braille.object_detection.RetinaNet.utils import filter_res, draw, get_text_from_predictions


model = load_model().cuda()

model.eval()
transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5,), (0.5,))])


def infer_retina_local(folder_path, result_path=""):
    for file in os.listdir(folder_path):
        print(f"processing {file}")

        img_path = os.path.join(folder_path, file)
        img = binarize_image(img_path)

        input_image = transform(img).unsqueeze(0).cuda()
        output = model(input_image)[0]

        boxes = output['boxes'].tolist()
        scores = output['scores'].tolist()
        labels = output['labels'].tolist()

        orig_img = Image.open(os.path.join(folder_path, file))
        filtered_boxes, filtered_labels, filtered_scores, sorted_lines = filter_res(boxes, labels, scores)
        res_image = draw(orig_img, filtered_boxes, filtered_labels, filtered_scores)

        if result_path:
            res_image.save(os.path.join(result_path + file))


def infer_retina_web(data, filename, status, upload_id, recognition_options):
    result = []
    images_amount = len(data)
    for num, file in enumerate(data):
        bin_image = binarize_image(file[0])
        status[upload_id] = ((0.2 + num) / images_amount) * 100

        input_image = transform(bin_image).unsqueeze(0).cuda()
        status[upload_id] = ((0.3 + num) / images_amount) * 100

        output = model(input_image)[0]
        status[upload_id] = ((0.7 + num) / images_amount) * 100

        boxes = output['boxes'].tolist()
        scores = output['scores'].tolist()
        labels = output['labels'].tolist()
        status[upload_id] = ((0.8 + num) / images_amount) * 100

        result_dict = {}

        filtered_boxes, filtered_labels, filtered_scores, sorted_lines = filter_res(boxes, labels, scores)
        if recognition_options["translation_required"] == "true" or recognition_options["braille_required"] == "true":
            translated_text, braille_text = get_text_from_predictions(sorted_lines, recognition_options["language"])
            if recognition_options["braille_required"] == "true":
                result_dict["braille_text"] = braille_text
            if recognition_options["translation_required"] == "true":
                result_dict["translated_text"] = translated_text
        if recognition_options["image_required"] == "true":
            result_dict["image"] = draw(file[0], filtered_boxes, filtered_labels, filtered_scores)
        status[upload_id] = ((1 + num) / images_amount) * 100
        result_dict["name"] = file[1]

        result.append(result_dict)

    return result
