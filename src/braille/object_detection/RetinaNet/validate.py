from object_detection.RetinaNet.train import load_data
from object_detection.RetinaNet.load_model import load_model
from object_detection.RetinaNet.utils import filter_res, draw, targets_to_lines
import torch


def calculate_precision(predictions, targets):
    correct_detections = 0
    correct_classifications = 0
    for key_p, key_t in zip(predictions.keys(), targets.keys()):
        for num_p, box_p in enumerate(predictions[key_p]):
            min_distance = [10000, 0]
            for num_t, box_t in enumerate(targets[key_t]):
                distance = abs(box_p['box'][0] - box_t['box'][0])
                if distance < min_distance[0]:
                    min_distance = [distance, num_t]
            iou_value = calculate_iou(box_p['box'], targets[key_t][min_distance[1]]['box'])
            if iou_value > 0.5:
                correct_detections += 1
                if box_p['label'] == targets[key_t][min_distance[1]]['label']:
                    correct_classifications += 1

    return correct_detections, correct_classifications


def calculate_iou(targets, predictions):
    xA = max(targets[0], predictions[0])
    yA = max(targets[1], predictions[1])
    xB = min(targets[2], predictions[2])
    yB = min(targets[3], predictions[3])

    inter_area = max(0, xB - xA + 1) * max(0, yB - yA + 1)

    boxA_area = (targets[2] - targets[0] + 1) * (targets[3] - targets[1] + 1)
    boxB_area = (predictions[2] - predictions[0] + 1) * (predictions[3] - predictions[1] + 1)

    return inter_area / float(boxA_area + boxB_area - inter_area)


def validate():
    model = load_model().eval().cuda()

    total_detections = 0
    total_classifications = 0
    total_correct_detections = 0
    total_correct_classifications = 0


    trainloader, testloader = load_data()

    with torch.no_grad():  # Отключение вычисления градиентов
        for images_dict, targets in testloader:
            images = [x['image'].cuda() for x in images_dict]
            for target in targets:
                target['boxes'] = target['boxes'].cuda()
                target['labels'] = target['labels'].cuda()
            
            print(f"Processing {images_dict[0]['path']}")
                
            outputs = model(images)[0]
            boxes = outputs['boxes'].tolist()
            labels = outputs['labels'].tolist()
            scores = outputs['scores'].tolist()
            boxes, labels, scores, lines = filter_res(boxes, labels, scores)
            draw(images_dict[0]["path"], boxes, labels, scores)
            
            targets_lines = targets_to_lines(targets[0]['boxes'].tolist(), targets[0]['labels'].tolist(), [1.0 for x in range(len(targets[0]["boxes"]))])

            total_detections += len(targets[0]["boxes"])
            correct_predictions, correct_classifications = calculate_precision(lines, targets_lines)
            total_classifications += correct_predictions
            total_correct_detections += correct_predictions
            total_correct_classifications += correct_classifications
    
    print(f"total detections: {total_detections}, correct: {total_correct_detections}, accuracy: {total_correct_detections / total_detections}")
    print(f"total classifications: {total_classifications}, correct: {total_correct_classifications}, accuracy: {total_correct_classifications / total_classifications}")
