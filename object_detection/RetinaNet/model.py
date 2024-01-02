import torch
from torchvision.models.detection.retinanet import RetinaNet, RetinaNetClassificationHead, RetinaNetRegressionHead, LastLevelP6P7
from torchvision.models.resnet import Bottleneck, ResNet
from torchvision.models.detection.backbone_utils import BackboneWithFPN, LastLevelMaxPool
from torchvision.models.detection.anchor_utils import AnchorGenerator
from functools import partial


class RetinaNetHead(torch.nn.Module):
    def __init__(self, in_channels, num_anchors, num_classes, norm_layer = None):
        super().__init__()
        self.classification_head = RetinaNetClassificationHead(
            in_channels, num_anchors, num_classes, norm_layer=norm_layer
        )
        self.regression_head = RetinaNetRegressionHead(in_channels, num_anchors, norm_layer=norm_layer)

    def compute_loss(self, targets, head_outputs, anchors, matched_idxs):
        return {
            "classification": self.classification_head.compute_loss(targets, head_outputs, matched_idxs),
            "bbox_regression": self.regression_head.compute_loss(targets, head_outputs, anchors, matched_idxs),
        }

    def forward(self, x):
        return {"cls_logits": self.classification_head(x), "bbox_regression": self.regression_head(x)}


def anchorgen():
    anchor_sizes = tuple((x, int(x * 2 ** (1.0 / 3)), int(x * 2 ** (2.0 / 3))) for x in [32, 64, 128, 256, 512])
    aspect_ratios = ((0.5, 1.0, 2.0),) * len(anchor_sizes)
    anchor_generator = AnchorGenerator(anchor_sizes, aspect_ratios)
    return anchor_generator


def resnet_fpn_extractor(
    backbone, trainable_layers: int, returned_layers = None, extra_blocks = None, norm_layer = None,
) -> BackboneWithFPN:

    layers_to_train = ["layer4", "layer3", "layer2", "layer1", "conv1"][:trainable_layers]
    if trainable_layers == 5:
        layers_to_train.append("bn1")
    for name, parameter in backbone.named_parameters():
        if all([not name.startswith(layer) for layer in layers_to_train]):
            parameter.requires_grad_(False)

    if extra_blocks is None:
        extra_blocks = LastLevelMaxPool()

    if returned_layers is None:
        returned_layers = [1, 2, 3, 4]

    return_layers = {f"layer{k}": str(v) for v, k in enumerate(returned_layers)}

    in_channels_stage2 = backbone.inplanes // 8
    in_channels_list = [in_channels_stage2 * 2 ** (i - 1) for i in returned_layers]
    out_channels = 256
    return BackboneWithFPN(
        backbone, return_layers, in_channels_list, out_channels, extra_blocks=extra_blocks, norm_layer=norm_layer
    )


def create_retinanet(
    *,
    num_classes = 64,
    trainable_backbone_layers = 5,
    **kwargs,
) -> RetinaNet:

    backbone = ResNet(Bottleneck, [3, 4, 6, 3])
    backbone = resnet_fpn_extractor(
        backbone, trainable_backbone_layers, returned_layers=[2, 3, 4], extra_blocks=LastLevelP6P7(2048, 256)
    )
    anchor_generator = anchorgen()
    head = RetinaNetHead(
        backbone.out_channels,
        anchor_generator.num_anchors_per_location()[0],
        num_classes,
        norm_layer=partial(torch.nn.GroupNorm, 32),
    )
    head.regression_head._loss_type = "giou"
    model = RetinaNet(backbone, num_classes, anchor_generator=anchor_generator, head=head, detections_per_img=800, topk_candidates=1600, **kwargs)

    return model
