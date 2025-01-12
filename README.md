# VME: A Satellite Imagery Dataset and Benchmark for Detecting Vehicles in the Middle East and Beyond

## VME Dataset
VME is a satellite imagery dataset built for vehicle detection in the Middle East. VME images and their associated annotations can be used for academic purposes only.  satellite_images folder is under CC BY-NC-ND 4.0 license, whereas the rest of folders (annotations_HBB, annotations_OBB, CDSI_construction_scripts) are under CC BY 4.0 license.

You can find 
VME_CDSI_datasets.zip has four components:

1- annotations_OBB: It holds TXT files in YOLO format with Oriented Bounding Box (OBB) annotations. Each annotation file is named after the corresponding image name
2- annotations_HBB: This component contains HBB annotation files in JSON file formatted in MS-COCO format defined by four values in pixels (x_min, y_min, width, height) of training, validation, and test splits 
3- satellite_images: This folder consists of VME images of size 512x512 in PNG format
4- CDSI_construction_scripts: This directory comprises all instructions needed to build the CDSI dataset, in detail: a) instructions for downloading each dataset from its repository, b) The conversion to MS-COCO format script for each dataset is under the dataset name folder, c) The combination instructions. The training, validation, and test splits are available under "CDSI_construction_scripts/data_utils" folder.

Components 1,2,4 can be found in this repository. The VME images are available in the Zenodo repository with the other components.

## Environment Setup for data preparation and preprocessing

```bash
pip install -r requirements.txt
```

## CDSI Dataset preparation
For using the VME dataset, both OBB (YOLO) and HBB (MS-COCO) formats are available with the desired splits. VME images and annotations are available at XXX.

In order to build the CDSI dataset, you need to follow the steps below:

1- Download each dataset from its repository:
- xView (https://challenge.xviewdataset.org/)
- DOTA-v2.0 (https://captain-whu.github.io/DOTA/index.html)
- VEDAI (https://downloads.greyc.fr/vedai/)
- DIOR (https://gcheng-nwpu.github.io/)
- FAIR1M-2.0 (http://gaofen-challenge.com/benchmark)

2- Convert each dataset to MS-COCO (JSON) format with original/ car-related + other small objects(car-other)/ car-related (car) setup, utilizing each dataset scripts under main directory:

### Instructions before starting:

a- After installing some datasets, it's recommended to put all images under one directory and all annotations under one directory, to ease the MS-COCO conversion

b- To generate SPLIT_FILE.txt for each setup (original|CDSI_other|CDSI), run this command under each dataset directory (example for car setup):

```bash
grep 'xview' CDSI_train.txt > xview_car_train.txt

SPLIT_FILE == xview_car_train.txt
```

** For DOTA-v2.0: please check ``dota2`` directory


### Converting each dataset to COCO format

Under each dataset directory, DATANAME_to_coco.py script is available to convert the specified dataset
```bash
python DATANAME_to_coco.py IMG_DIR SPLIT_FILE.txt OUT_DIR MODE
```

### Combining train-val-test splits

To combine the train-val-test splits from each dataset to construct CDSI splits, please use the following command/package. The command takes 3 arguments:File1.json File2.json OutputFile.json. This step needs to be repeated to complete CDSI specific split.
```bash
pyodi coco merge SPLIT_A.json SPLIT_B.json SPLIT_A_B.json
```

>[!NOTE]
__The benchmark scripts will be released soon! Stay Tuned!__
