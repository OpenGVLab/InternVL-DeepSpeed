# --------------------------------------------------------
# InternVL
# Copyright (c) 2024 OpenGVLab
# Licensed under The MIT License [see LICENSE for details]
# --------------------------------------------------------

_base_ = [
    '../../_base_/models/upernet_r50.py',
    '../../_base_/datasets/coco-stuff164k_504x504.py',
    '../../_base_/default_runtime.py',
    '../../_base_/schedules/schedule_80k.py'
]
deepspeed = True
deepspeed_config = 'zero_configs/adam_zero1_bf16.json'
pretrained = './pretrained/intern_vit_6b_448px_v1_5.pth'
model = dict(
    pretrained=None,
    backbone=dict(
        _delete_=True,
        type='InternViT6B',
        pretrain_size=448,
        img_size=504,
        patch_size=14,
        embed_dim=3200,
        depth=45,
        num_heads=25,
        mlp_ratio=4.,
        qkv_bias=False,
        drop_path_rate=0.4,
        init_values=0.1,
        with_cp=True,
        use_flash_attn=True,
        qk_normalization=True,
        layerscale_force_fp32=False,
        with_fpn=True,
        freeze_vit=False,
        out_indices=[11, 22, 33, 44],
        pretrained=pretrained),
    decode_head=dict(num_classes=171,
                     channels=1536,
                     in_channels=[3200, 3200, 3200, 3200]),
    auxiliary_head=dict(num_classes=171,
                        channels=1536,
                        in_channels=3200),
    test_cfg=dict(mode='slide', crop_size=(504, 504), stride=(322, 322))
)
optimizer = dict(_delete_=True, type='AdamW', lr=4e-5, betas=(0.9, 0.999), weight_decay=0.05,
                 constructor='CustomLayerDecayOptimizerConstructor',
                 paramwise_cfg=dict(num_layers=45, layer_decay_rate=0.95))
lr_config = dict(_delete_=True, policy='poly',
                 warmup='linear',
                 warmup_iters=1500,
                 warmup_ratio=1e-6,
                 power=1.0, min_lr=0.0, by_epoch=False)
# By default, models are trained on 8 GPUs with 2 images per GPU
data = dict(samples_per_gpu=2)
runner = dict(type='IterBasedRunner')
if deepspeed:
    checkpoint_config = dict(deepspeed=deepspeed, by_epoch=False, interval=1000, max_keep_ckpts=2)
else:
    checkpoint_config = dict(by_epoch=False, interval=1000, max_keep_ckpts=2)
evaluation = dict(interval=1000, metric='mIoU', save_best='auto')
custom_hooks = [
    dict(
        type='ToBFloat16Hook',
        priority=49),
]
