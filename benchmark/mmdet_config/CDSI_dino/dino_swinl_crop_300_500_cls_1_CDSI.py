_base_ = ["../dino/dino-5scale_swin-l_8xb2-36e_coco.py"]


EXP_NAME = "dino_swinl_crop_300_500_cls_1_car"
DATA_ROOT = "data/CDSI_v2/"
BATCH_MULTIPLIER = 1
NUM_CLASSES = 1

# model settings
model = dict(
    bbox_head=dict(
        num_classes=NUM_CLASSES,),
)

backend_args = None
train_pipeline = [
    dict(type="LoadImageFromFile", backend_args=backend_args),
    dict(type="LoadAnnotations", with_bbox=True),
    dict(type="RandomFlip", prob=0.5),
        dict(type='RandomChoice',
         transforms=[
            [
                dict(
                    type='RandomCrop', 
                    crop_type='absolute_range', 
                    crop_size=(300, 500), 
                    allow_negative_crop=True),
                dict(
                    type="Resize", 
                    scale=(1333, 800), 
                    keep_ratio=True)
            ],
            [
                dict(
                    type='RandomCrop', 
                    crop_type='absolute_range', 
                    crop_size=(300, 500), 
                    allow_negative_crop=True),
                dict(
                    type="Resize", 
                    scale=(1333, 800), 
                    keep_ratio=True)
            ]
        ]),
    dict(type='PackDetInputs')
]

test_pipeline = [
    dict(type='LoadImageFromFile', backend_args=backend_args),
    dict(type='Resize', scale=(1333, 800), keep_ratio=True),
    # If you don't have a gt annotation, delete the pipeline
    dict(type='LoadAnnotations', with_bbox=True),
    dict(
        type='PackDetInputs',
        meta_keys=('img_id', 'img_path', 'ori_shape', 'img_shape','scale_factor'))
]


dataset_type = 'CustomDataset'
b_size=2
train_dataloader = dict(
    batch_size=b_size * BATCH_MULTIPLIER,
#     num_workers=2,
    num_workers=4,
    persistent_workers=True,
    sampler=dict(type='DefaultSampler', shuffle=True),
    batch_sampler=dict(type='AspectRatioBatchSampler'),
    dataset=dict(
        type=dataset_type,
        data_root=DATA_ROOT,
        ann_file="coco/train.json",
        data_prefix=dict(img="images/"),
        filter_cfg=dict(filter_empty_gt=True, min_size=32),
        pipeline=train_pipeline,
        backend_args=backend_args)
)

val_dataloader = dict(
#     batch_size=1,
    batch_size=2,
#     num_workers=2,
    num_workers=4,
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type='DefaultSampler', shuffle=False),
    dataset=dict(
        type=dataset_type,
        data_root=DATA_ROOT,
        ann_file="sliced/val_400_0.json",
        data_prefix=dict(img="sliced/val_images_400_0/"),
        test_mode=True,
        pipeline=test_pipeline,
        backend_args=backend_args))
test_dataloader = val_dataloader


val_evaluator = dict(
    type='CocoMetric',
    ann_file="sliced/val_400_0.json",
    metric='bbox',
    format_only=False,
    backend_args=backend_args)
test_evaluator = val_evaluator

# max_epochs = 24
# train_cfg = dict(type='EpochBasedTrainLoop', max_epochs=max_epochs, val_interval=1)
log_processor = dict(type='LogProcessor', window_size=1, by_epoch=True)
default_hooks = dict(
    logger=dict(type='LoggerHook', interval=1), 
    checkpoint=dict(type='CheckpointHook', save_best='auto')
)


# base_batch_size = (8 GPUs) x (2 samples per GPU)
auto_scale_lr=dict(base_batch_size=b_size*BATCH_MULTIPLIER, enable=True)

load_from = "https://github.com/RistoranteRist/mmlab-weights/releases/download/dino-swinl/dino-5scale_swin-l_8xb2-36e_coco-5486e051.pth"
work_dir = f"runs/CDSI/{EXP_NAME}/"
