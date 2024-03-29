import torch.nn as nn

from networks.ResidualBlocks import ResidualBlock2dTransposeConv


def res_block_gen(
    in_channels,
    out_channels,
    kernelsize,
    stride,
    padding,
    o_padding,
    dilation,
    a_val=1.0,
    b_val=1.0,
):
    upsample = None
    if (kernelsize != 1 and stride != 1) or (in_channels != out_channels):
        upsample = nn.Sequential(
            nn.ConvTranspose2d(
                in_channels,
                out_channels,
                kernel_size=kernelsize,
                stride=stride,
                padding=padding,
                dilation=dilation,
                output_padding=o_padding,
            ),
            nn.BatchNorm2d(out_channels),
        )
    layers = []
    layers.append(
        ResidualBlock2dTransposeConv(
            in_channels,
            out_channels,
            kernelsize=kernelsize,
            stride=stride,
            padding=padding,
            dilation=dilation,
            o_padding=o_padding,
            upsample=upsample,
            a=a_val,
            b=b_val,
        )
    )
    return nn.Sequential(*layers)


class DataGeneratorImg(nn.Module):
    def __init__(self, cfg, a, b):
        super(DataGeneratorImg, self).__init__()
        self.resblock1 = res_block_gen(
            5 * cfg.dataset.filter_dim_img,
            4 * cfg.dataset.filter_dim_img,
            kernelsize=4,
            stride=1,
            padding=0,
            dilation=1,
            o_padding=0,
            a_val=a,
            b_val=b,
        )
        self.resblock2 = res_block_gen(
            4 * cfg.dataset.filter_dim_img,
            3 * cfg.dataset.filter_dim_img,
            kernelsize=4,
            stride=2,
            padding=1,
            dilation=1,
            o_padding=0,
            a_val=a,
            b_val=b,
        )
        self.resblock3 = res_block_gen(
            3 * cfg.dataset.filter_dim_img,
            2 * cfg.dataset.filter_dim_img,
            kernelsize=4,
            stride=2,
            padding=1,
            dilation=1,
            o_padding=0,
            a_val=a,
            b_val=b,
        )
        self.resblock4 = res_block_gen(
            2 * cfg.dataset.filter_dim_img,
            1 * cfg.dataset.filter_dim_img,
            kernelsize=4,
            stride=2,
            padding=1,
            dilation=1,
            o_padding=0,
            a_val=a,
            b_val=b,
        )
        self.conv = nn.ConvTranspose2d(
            cfg.dataset.filter_dim_img,
            cfg.dataset.image_channels,
            kernel_size=3,
            stride=2,
            padding=1,
            dilation=1,
            output_padding=1,
        )

    def forward(self, feats):
        d = self.resblock1(feats)
        d = self.resblock2(d)
        d = self.resblock3(d)
        d = self.resblock4(d)
        d = self.conv(d)
        return d
