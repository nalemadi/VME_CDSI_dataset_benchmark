import os
from pathlib import Path
import fire
from PIL import Image
from sahi.utils.coco import Coco, CocoAnnotation, CocoCategory, CocoImage
from sahi.utils.file import save_json
from tqdm import tqdm
import sys


CATEGORY_ID_TO_NAME = {
"1": "car",
"2":"truck",
"3": "pickup",
"4": "tractor",
"5": "camping",
"6": "boat",
"7": "motorcycle",
"9": "bus",
"10": "van",
"11": "other",
"12": "small car",
"13": "large car",
"31": "plane",
"23": "board"
}

CATEGORY_ID_REMAPPING = {
    "1": "0",
    "2": "1",
    "4": "2",
    "5": "3",
    "7": "4",
    "9": "5",
    "10": "6",
    "11": "7",
    "31": "8",
    "23": "9"
}

NAME_TO_COCO_CATEGORY = {
    "car": {"name": "car", "supercategory": "car"},
    "truck": {"name": "truck", "supercategory": "truck"},
    "tractor": {"name": "tractor", "supercategory": "tractor"},
    "camping": {"name": "camping", "supercategory": "camping"},
    "motorcycle": {"name": "motorcycle", "supercategory": "motorcycle"},
    "bus": {"name": "bus", "supercategory": "bus"},
    "van": {"name": "van", "supercategory": "van"},
    "other": {"name": "other", "supercategory": "other"},
    "plane": {"name": "plane", "supercategory": "plane"},
    "board": {"name": "board", "supercategory": "board"}
}


def vedai_to_coco(
    data_folder_dir,
    split_images_path,
    output_dir,
    mode,
    category_id_remapping=None,
):
    """
    Converts vedai annotations into coco annotation.

    Args:
        data_folder_dir: str
            'vedai' folder directory
        split_images_path: str
            split_images_path txt file
        output_file_path: str
            Output file path
        mode: str
            mode original|car_other|car
        category_id_remapping: dict
            Used for selecting desired category ids and mapping them.
            If not provided, vedai mapping will be used.
            format: str(id) to str(id)
    """

    # init paths/folders
    input_image_folder = str(Path(data_folder_dir) / "Vehicules512")
    input_ann_folder = str(Path(data_folder_dir) / "Annotations512")

    image_filepath_list = os.listdir(input_image_folder)

#     Path(output_dir).parents[0].mkdir(parents=True, exist_ok=True)

    if category_id_remapping is None:
        category_id_remapping = CATEGORY_ID_REMAPPING

    # init coco object
    coco = Coco()

    # append categories
    if mode == 'original':
        for category_id, category_name in CATEGORY_ID_TO_NAME.items():
            if category_id in category_id_remapping.keys():
                remapped_category_id = category_id_remapping[category_id]
                coco_category = NAME_TO_COCO_CATEGORY[category_name]
                coco.add_category(
                    CocoCategory(
                        id=int(remapped_category_id),
                        name=coco_category["name"],
                        supercategory=coco_category["supercategory"],
                    )
                )
    elif mode == 'car_other':
        print('"car_other" mode categories')
        coco.add_category(CocoCategory(id=0, name='Other'))
        coco.add_category(CocoCategory(id=1, name='Car'))
        for k,v in category_id_remapping.items():
            if k in ['1','10']:
                category_id_remapping[k] =1
            else:
                category_id_remapping[k]=0
    elif mode == 'car':
        # car related categories: car, pickup, van
        print('"car" mode categories')
        coco.add_category(CocoCategory(id=0, name='Car'))
        category_id_remapping = {'1': '0','10': '0'}
    else:
        print('pick a defined mode: [original/car_other/car]')
        sys.exit()
    
    split_images_lst = []
    with open(split_images_path, 'r') as f:
        for line in f:
            split_images_lst.append(line.strip().split('/')[1])
    
    # convert vedai annotations to coco
    for image_name in tqdm(image_filepath_list):
        # get image properties
        if image_name in split_images_lst:
            image_filepath = str(Path(input_image_folder) / image_name)
            annotation_filename = image_name.split("_co.png")[0] + ".txt"
            annotation_filepath = str(Path(input_ann_folder) / annotation_filename)
            image = Image.open(image_filepath)
            cocoimage_filename = str(Path(image_filepath)).split(str(Path(data_folder_dir)))[1]
            if cocoimage_filename[0] == os.sep:
                cocoimage_filename = cocoimage_filename[1:]
            # create coco image object
            coco_image = CocoImage(file_name=cocoimage_filename, height=image.size[1], width=image.size[0])
            # parse annotation file
            file = open(annotation_filepath, "r")
            lines = file.readlines()
            for line in lines:
                # parse annotation bboxes
                new_line = line.strip("\n").split(" ")
                y_corners = [int(x) for x in new_line[-4:]]
                x_corners = [int(x) for x in new_line[-8:-4]]
                minx_miny = (min(x_corners), min(y_corners))
                maxx_maxy = (max(x_corners), max(y_corners))
                #
                i_bbox = [minx_miny[0], minx_miny[1], maxx_maxy[0], maxx_maxy[1]]
                # width = maxx-minx, height = maxy-miny
                width = i_bbox[2] - i_bbox[0]
                height = i_bbox[3] - i_bbox[1]

                #top left point
                minx = min(x_corners)
                miny = min(y_corners)

                bbox = [minx,
                        miny,
                        width,
                        height]
                # parse category id and name
                category_id = new_line[3]
                if category_id in category_id_remapping.keys():
                    category_name = CATEGORY_ID_TO_NAME[category_id]
                    remapped_category_id = category_id_remapping[category_id]
                else:
                    continue

                # create coco annotation and append it to coco image
                coco_annotation = CocoAnnotation.from_coco_bbox(
                    bbox=bbox,
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

    save_path = output_dir
    all_json_path = Path(save_path) / "{}.json".format(split_images_path.split('.')[0])
    save_json(data=coco.json, save_path=all_json_path)
    


if __name__ == "__main__":
    fire.Fire(vedai_to_coco)