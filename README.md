<p align="center"><img width="200" height="240" alt="logo-color-small" src="https://github.com/user-attachments/assets/feffd7e6-d55e-4f15-9f35-eb5f04f73f23"/></p>

# VME: A Satellite Imagery Dataset and Benchmark for Detecting Vehicles in the Middle East and Beyond
This is the official repository for the paper *"VME: A Satellite Imagery Dataset and Benchmark for Detecting Vehicles in the Middle East and Beyond"*, Which is accepted in Nature Scientific Data, January 2025.

#### Authors
[Noora Al-Emadi](https://orcid.org/0000-0003-4137-6082), Qatar Computing Research Institute, Hamad Bin Khalifa University

[Ingmar Weber](https://orcid.org/0000-0003-4169-2579), Saarland Informatics Campus, Saarland University

[Yin Yang](https://orcid.org/0000-0002-0549-3882), College of Science and Engineering, Hamad Bin Khalifa University

[Ferda Ofli](https://orcid.org/0000-0003-3918-3230), Qatar Computing Research Institute, Hamad Bin Khalifa University

## Abstract
Detecting vehicles in satellite images is crucial for traffic management, urban planning, and disaster response. However, current models struggle with real-world diversity, particularly across different regions. This challenge is amplified by geographic bias in existing datasets, which often focus on specific areas and overlook regions like the Middle East. To address this gap, we present the Vehicles in the Middle East (VME) dataset, designed explicitly for vehicle detection in high-resolution satellite images from Middle Eastern countries. Sourced from Maxar, the VME dataset spans 54 cities across 12 countries, comprising over 4,000 image tiles and more than 100,000 vehicles, annotated using both manual and semi-automated methods. Additionally, we introduce the largest benchmark dataset for Car Detection in Satellite Imagery (CDSI), combining images from multiple sources to enhance global car detection. Our experiments demonstrate that models trained on existing datasets perform poorly on Middle Eastern images, while the VME dataset significantly improves detection accuracy in this region. Moreover, state-of-the-art models trained on CDSI achieve substantial improvements in global car detection.


<img width="1144" alt="figure1" src="https://github.com/user-attachments/assets/95060606-4209-4757-a3f6-73eab271a5bf" />
<h6> The distinct visual context of cars on the road in the Middle Eastern cities: a) Abu Kamal, Syria, and b) Alexandria, Egypt & other cities around the world: c) Sydney, Australia, and d) Mexico City, Mexico.</h6>

## VME Dataset

Vehicles in the Middle East (VME) is a satellite imagery dataset built for vehicle detection in the Middle East. 

[comment]: # "VME images and their associated annotations can be used for **academic purposes only**." 

VME images (**satellite_images** folder) are under [**CC BY-NC-ND 4.0 license**](https://creativecommons.org/licenses/by-nc-nd/4.0/) and available for download on [**Zenodo repository**](https://zenodo.org/records/14185684), we also release VME ground-truth annotations and the scripts associated for constructing CDSI **(annotations_HBB, annotations_OBB, CDSI_construction_scripts)** under [**CC BY 4.0 license**](https://creativecommons.org/licenses/by/4.0/) which are available on [**Zenodo repository**](https://zenodo.org/records/14185684) and here.

This repository consists of:
1. VME_annotations, which has:
   * annotations_OBB: It holds TXT files in YOLO format with Oriented Bounding Box (OBB) annotations. Each annotation file is named after the corresponding image name.
   * annotations_HBB: This component contains HBB annotation files in JSON file formatted in MS-COCO format defined by four values in pixels (x_min, y_min, width, height) of training, validation, and test splits.
   * satellite_images: This folder consists of VME images of size 512x512 in PNG format. (**The VME images are available in the [**Zenodo repository**](https://zenodo.org/records/14185684)**)
2. CDSI_construction_scripts: This directory comprises all instructions needed to build the CDSI dataset, in detail: a) instructions for downloading each dataset from its repository, b) The conversion to MS-COCO format script for each dataset is under the dataset name folder, c) The combination instructions. The training, validation, and test splits are available under "CDSI_construction_scripts/data_utils" folder.


## Environment Setup for data preparation and preprocessing

```bash
pip install -r requirements.txt
```

## CDSI Dataset preparation
For using the VME dataset, both OBB (YOLO) and HBB (MS-COCO) formats are available with the desired splits.

In order to build the CDSI dataset, you need to follow the steps below:

1. Download each dataset from its repository:
    * xView (https://challenge.xviewdataset.org/)
    * DOTA-v2.0 (https://captain-whu.github.io/DOTA/index.html)
    * VEDAI (https://downloads.greyc.fr/vedai/)
    * DIOR (https://gcheng-nwpu.github.io/)
    * FAIR1M-2.0 (http://gaofen-challenge.com/benchmark)

2. Convert each dataset to MS-COCO (JSON) format with original/ car-related + other small objects(car-other)/ car-related (car) setup, utilizing each dataset scripts under main directory:

### Instructions before starting:

a. After installing some datasets, it's recommended to put all images under one directory and all annotations under one directory, to ease the MS-COCO conversion

b. To generate SPLIT_FILE.txt for each setup (original | CDSI_other | CDSI), run this command under each dataset directory (example for car setup):

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

## Citation
```bash
@article{alemadi2025vme,
  title={{VME: A Satellite Imagery Dataset and Benchmark for Detecting Vehicles in the Middle East and Beyond}},
  author={Alemadi, Noora and Weber, Ingmar and Yang, Yin and Ofli, Ferda},
  journal={Scientific Data},
  volume={},
  number={1},
  pages={},
  year={2025},
  publisher={Spring Nature},
  note={to appear}
}
```
[comment]: # "## Result"


[comment]: # "## Citation"
[comment]: # "If you found our project helpful, please cite our paper:"
[comment]: # "```bash"


