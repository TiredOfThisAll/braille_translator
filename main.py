from object_detection.RetinaNet.infer import infer_retina
from object_detection.RetinaNet.train import train
from object_detection.RetinaNet.validate import validate

# get_results("D:/PythonProjects/braile/data/infer")

if __name__ == "__main__":
    # train()
    # validate()
    infer_retina("D:\PythonProjects\\braile\data\infer")