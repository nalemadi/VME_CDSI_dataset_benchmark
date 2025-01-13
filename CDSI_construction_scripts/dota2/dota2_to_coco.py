import os
from pathlib import Path
import fire
from PIL import Image
from sahi.utils.coco import Coco, CocoAnnotation, CocoCategory, CocoImage
from sahi.utils.file import save_json
from tqdm import tqdm
import sys


CATEGORY_ID_REMAPPING = {
    "plane": "0",
    "baseball-diamond": "1",
    "bridge": "2",
    "ground-track-field": "3",
    "small-vehicle": "4",
    "large-vehicle": "5",
    "ship": "6",
    "tennis-court": "7",
    "basketball-court": "8",
    "storage-tank": "9",
    "soccer-ball-field": "10",
    "roundabout": "11",
    "harbor": "12",
    "swimming-pool": "13",
    "helicopter": "14",
    "container-crane": "15", 
    "airport": "16", 
    "helipad": "17"
}

def dota2_to_coco(
    data_folder_dir,
    split_images_path,
    output_file_path,
    mode,
    category_id_remapping=None,
):
    """
    Converts dota2 annotations into coco annotation.

    Args:
        data_folder_dir: str
            'fair1m' folder directory
        output_file_path: str
            Output file path
        category_id_remapping: dict
            Used for selecting desired category ids and mapping them.
            If not provided, vedai mapping will be used.
            format: str(id) to str(id)
    """

    # init paths/folders
    input_image_folder = str(Path(data_folder_dir) / "images")
    input_ann_folder = str(Path(data_folder_dir) / "labelTxt")

    image_filepath_list = os.listdir(input_image_folder)
    
    if category_id_remapping is None:
        category_id_remapping = CATEGORY_ID_REMAPPING
    
    # init coco object
    coco = Coco()
    
    if mode == 'original':
        # append categories
        categories = ["plane", "baseball-diamond", "bridge", "ground-track-field", "small-vehicle", "large-vehicle", "ship", "tennis-court", "basketball-court", "storage-tank", "soccer-ball-field", "roundabout", "harbor", "swimming-pool", "helicopter", "container-crane", "airport", "helipad"]
        for i, cat in enumerate(categories):
            coco.add_category(CocoCategory(id=i, name=cat))
    elif mode == 'car_other':
        print('"car_other" mode categories')
        coco.add_category(CocoCategory(id=0, name='Other'))
        coco.add_category(CocoCategory(id=1, name='Car'))
        for k,v in category_id_remapping.items():
            if k in 'small-vehicle':
                category_id_remapping[k] =1
            else:
                category_id_remapping[k]=0
    elif mode == 'car':
        # car related categories: car, pickup, van
        print('"car" mode categories')
        coco.add_category(CocoCategory(id=0, name='Car'))
        category_id_remapping = {'small-vehicle': '0'}
    else:
        print('pick a defined mode: [original/car_other/car]')
        sys.exit()
    
    split_images_lst = []
    with open(split_images_path, 'r') as f:
        for line in f:
            broken = line.strip().split('/')
            if len(broken) > 1:
                split_images_lst.append(broken[1])
            else:
                split_images_lst.append(broken[0])
    
    cnt=0
    broken_set = set()
    # convert fair1m annotations to coco
    for image_filename in tqdm(image_filepath_list):
        if image_filename in split_images_lst:
            cnt+=1
            # get image properties
            image_filepath = str(Path(input_image_folder) / image_filename)
            annotation_filename = image_filename.split(".png")[0] + ".txt"
            annotation_filepath = str(Path(input_ann_folder) / annotation_filename)
            image = Image.open(image_filepath)
            cocoimage_filename = str(Path(image_filepath)).split(str(Path(data_folder_dir)))[1]
            if cocoimage_filename[0] == os.sep:
                cocoimage_filename = cocoimage_filename[1:]
            # create coco image object
            coco_image = CocoImage(file_name=cocoimage_filename, height=image.size[1], width=image.size[0])
            # parse annotation file
            ###
            file = open(annotation_filepath, "r")
            lines = file.readlines()
            for line in lines:
                # x1 y1 x2 y2 x3 y3 x4 y4 category difficult
                broken = line.strip().split(' ')
                broken_set.add(len(broken))
                if len(broken) > 1:
                    x_corners = []
                    y_corners = []
                
                    x_corners.append(int(float(broken[0])))
                    x_corners.append(int(float(broken[2])))
                    x_corners.append(int(float(broken[4])))
                    x_corners.append(int(float(broken[6])))
                    #
                    y_corners.append(int(float(broken[1])))
                    y_corners.append(int(float(broken[3])))
                    y_corners.append(int(float(broken[5])))
                    y_corners.append(int(float(broken[7])))

                    minx = min(x_corners)
                    miny = min(y_corners)
                    maxx = max(x_corners)
                    maxy = max(y_corners)

                    tbox = [minx, miny, maxx, maxy]
                    # width = maxx-minx, height = maxy-miny
                    width = tbox[2] - tbox[0]
                    height = tbox[3] - tbox[1]

                    bbox = [minx,
                            miny,
                            width,
                            height]
                    obj_area = width * height

                    category_name = broken[8]
                    if category_name in category_id_remapping.keys():
                        remapped_category_id = category_id_remapping[category_name]
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
                        if 0 < coco_annotation.area < 400:
                            coco_image.add_annotation(coco_annotation)
                    elif mode == 'car':
                        if 0 < coco_annotation.area < 400:
#                         if 0 < obj_area < 400:
                            coco_image.add_annotation(coco_annotation)
                else:
                    continue
            
            coco.add_image(coco_image)
    
    print('cnt', cnt, 'broken_set', broken_set)
    save_path = output_file_path
    all_json_path = Path(save_path) / "{}.json".format(split_images_path.split('.')[0])
    save_json(data=coco.json, save_path=all_json_path)


if __name__ == "__main__":
    fire.Fire(dota2_to_coco)
