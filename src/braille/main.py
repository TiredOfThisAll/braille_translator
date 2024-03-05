from object_detection.RetinaNet.infer import infer_retina_local
from object_detection.RetinaNet.train import train
from object_detection.RetinaNet.validate import validate

if __name__ == "__main__":
    infer_retina_local(input("Path to images folder"))