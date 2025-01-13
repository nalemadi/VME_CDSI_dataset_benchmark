import random
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import fire
import numpy as np
from PIL import Image
from sahi.utils.coco import Coco, CocoAnnotation, CocoCategory, CocoImage
from sahi.utils.file import load_json, save_json
from tqdm import tqdm
import sys

# fix the seed
random.seed(13)


def xview_to_coco(
    images_dir,
    split_images_path,
    train_geojson_path,
    output_dir,
    mode,
    category_id_remapping=None
):
    """
    Converts xView annotations into coco annotation.

    Args:
        images_dir: str
            'train_images' folder directory
        split_images_path: str
            split_images_path txt file
        train_geojson_path: str
            'xView_train.geojson' file path
        output_dir: str
            Output folder directory
        mode: str
            mode original|car_other|car
        category_id_remapping: dict
            Used for selecting desired category ids and mapping them.
            If not provided, vedai mapping will be used.
            format: str(id) to str(id)
    """
    

    # init vars
    category_id_to_name = {}
    with open("xview_class_labels.txt", encoding="utf8") as f:
        lines = f.readlines()
    for line in lines:
        category_id = line.split(":")[0]
        category_name = line.split(":")[1].replace("\n", "")
        category_id_to_name[category_id] = category_name

    if category_id_remapping is None:
        category_id_remapping = load_json("category_id_mapping.json")
    category_id_remapping

    # init coco object
    coco = Coco()
    # append categories
    if mode == 'original':
        for category_id, category_name in category_id_to_name.items():
            if category_id in category_id_remapping.keys():
                remapped_category_id = category_id_remapping[category_id]
                coco.add_category(
                    CocoCategory(id=int(remapped_category_id), name=category_name)
                )
    elif mode == 'car_other':
        print('"car_other" mode categories')
        coco.add_category(CocoCategory(id=0, name='Other'))
        coco.add_category(CocoCategory(id=1, name='Car'))
        for k,v in category_id_remapping.items():
            if k == '18':
                category_id_remapping[k] =1
            else:
                category_id_remapping[k]=0
        
    elif mode == 'car':
        print('"car" mode categories')
        # xview_category_id for 'Small Car' = '18'
        coco.add_category(CocoCategory(id=0, name='Car'))
        category_id_remapping = {'18': 0}
    else:
        print('pick a defined mode: [original/car_other/car]')
        sys.exit()

    # parse xview data
    coords, chips, classes, image_name_to_annotation_ind = get_labels(
        train_geojson_path
    )
    image_name_list = get_ordered_image_name_list(image_name_to_annotation_ind)
    
    split_images_lst = []
    with open(split_images_path, 'r') as f:
        for line in f:
            split_images_lst.append(line.strip().split('/')[1])
    
    # convert xView data to COCO format
    for image_name in tqdm(image_name_list, "Converting xView data into COCO format"):
        # create coco image object
        if image_name in split_images_lst:
            width, height = Image.open(Path(images_dir) / image_name).size
            coco_image = CocoImage(file_name=image_name, height=height, width=width)

            annotation_ind_list = image_name_to_annotation_ind[image_name]

            # iterate over image annotations
            for annotation_ind in annotation_ind_list:
                bbox = coords[annotation_ind].tolist()
                category_id = str(int(classes[annotation_ind].item()))
                coco_bbox = [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]]
                if category_id in category_id_remapping.keys():
                    category_name = category_id_to_name[category_id]
                    remapped_category_id = category_id_remapping[category_id]
                else:
                    continue
                # create coco annotation and append it to coco image
                coco_annotation = CocoAnnotation(
                    bbox=coco_bbox,
                    category_id=int(remapped_category_id),
                    category_name=category_name,
                )
                if mode == 'original':
                    if coco_annotation.area > 0:
                        coco_image.add_annotation(coco_annotation)
                elif mode == 'car_other':
                    if coco_annotation.area < 400:
                        coco_image.add_annotation(coco_annotation)
                elif mode == 'car':
                    if coco_annotation.area < 400:
                        coco_image.add_annotation(coco_annotation)
            coco.add_image(coco_image)
    ###
    save_path = output_dir
    all_json_path = Path(save_path) / "{}.json".format(split_images_path.split('.')[0])
    save_json(data=coco.json, save_path=all_json_path)


def get_ordered_image_name_list(image_name_to_annotation_ind: Dict):
    image_name_list: List[str] = list(image_name_to_annotation_ind.keys())

    def get_image_ind(image_name: str):
        return int(image_name.split(".")[0])

    image_name_list.sort(key=get_image_ind)

    return image_name_list


def get_labels(fname):
    """
    Gets label data from a geojson label file
    Args:
        fname: file path to an xView geojson label file
    Output:
        Returns three arrays: coords, chips, and classes corresponding to the
            coordinates, file-names, and classes for each ground truth.
    Modified from https://github.com/DIUx-xView.
    """
    data = load_json(fname)

    coords = np.zeros((len(data["features"]), 4))
    chips = np.zeros((len(data["features"])), dtype="object")
    classes = np.zeros((len(data["features"])))
    image_name_to_annotation_ind = defaultdict(list)

    for i in tqdm(range(len(data["features"])), "Parsing xView data"):
        if data["features"][i]["properties"]["bounds_imcoords"] != []:
            b_id = data["features"][i]["properties"]["image_id"]
            # https://github.com/DIUx-xView/xView1_baseline/issues/3
            if b_id == "1395.tif":
                continue
            val = np.array(
                [
                    int(num)
                    for num in data["features"][i]["properties"][
                        "bounds_imcoords"
                    ].split(",")
                ]
            )
            chips[i] = b_id
            classes[i] = data["features"][i]["properties"]["type_id"]

            image_name_to_annotation_ind[b_id].append(i)

            if val.shape[0] != 4:
                print("Issues at %d!" % i)
            else:
                coords[i] = val
        else:
            chips[i] = "None"

    return coords, chips, classes, image_name_to_annotation_ind


if __name__ == "__main__":
    fire.Fire(xview_to_coco)
