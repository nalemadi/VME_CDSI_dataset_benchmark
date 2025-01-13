import os
from pathlib import Path
import fire
from PIL import Image
from sahi.utils.coco import Coco, CocoAnnotation, CocoCategory, CocoImage
from sahi.utils.file import save_json
from tqdm import tqdm
import xml.etree.ElementTree as ET
import sys;


NAME_TO_COCO_CATEGORY = {
    "stadium": {"name": "stadium", "supercategory": "stadium"},
    "Expressway-toll-station": {"name": "Expressway-toll-station", "supercategory": "Expressway-toll-station"},
    "bridge": {"name": "bridge", "supercategory": "bridge"},
    "groundtrackfield": {"name": "groundtrackfield", "supercategory": "groundtrackfield"},
    "Expressway-Service-area": {"name": "groundtrackfield", "supercategory": "groundtrackfield"},
    "dam": {"name": "dam", "supercategory": "dam"},
    "ship": {"name": "ship", "supercategory": "ship"},
    "basketballcourt": {"name": "basketballcourt", "supercategory": "basketballcourt"},
    "vehicle": {"name": "vehicle", "supercategory": "vehicle"},
    "golffield": {"name": "golffield", "supercategory": "golffield"},
    "airplane": {"name": "airplane", "supercategory": "airplane"},
    "baseballfield": {"name": "baseballfield", "supercategory": "baseballfield"},
    "airport": {"name": "airport", "supercategory": "airport"},
    "harbor": {"name": "harbor", "supercategory": "harbor"},
    "chimney": {"name": "chimney", "supercategory": "chimney"},
    "tenniscourt": {"name": "tenniscourt", "supercategory": "tenniscourt"},
    "trainstation": {"name": "trainstation", "supercategory": "trainstation"},
    "overpass": {"name": "overpass", "supercategory": "overpass"},
    "storagetank": {"name": "storagetank", "supercategory": "storagetank"},
    "windmill": {"name": "windmill", "supercategory": "windmill"}
}

CATEGORY_ID_REMAPPING = {
    "stadium": "0", 
    "Expressway-toll-station": "1", 
    "bridge": "2", 
    "groundtrackfield": "3", 
    "Expressway-Service-area": "4", 
    "dam": "5",
    "ship": "6", 
    "basketballcourt": "7",
    "vehicle": "8", 
    "golffield": "9", 
    "airplane": "10", 
    "baseballfield": "11", 
    "airport":"12", 
    "harbor":"13", 
    "chimney":"14", 
    "tenniscourt":"15", 
    "trainstation":"16", 
    "overpass":"17", 
    "storagetank":"18", 
    "windmill":"19"
}


def dior_to_coco(
    data_folder_dir,
    split_images_path,
    output_file_path,
    mode,
    category_id_remapping=None,
):
    """
    Converts DIOR annotations into coco annotation.

    Args:
        data_folder_dir: str
            'dior' folder directory
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
    input_image_folder = str(Path(data_folder_dir) / "JPEGImages-all")
    input_ann_folder = str(Path(data_folder_dir) / "Annotations/Horizontal Bounding Boxes")

    image_filepath_list = os.listdir(input_image_folder)
    
    if category_id_remapping is None:
        category_id_remapping = CATEGORY_ID_REMAPPING
    
    # init coco object
    coco = Coco()
    
    if mode == 'original':
        # append categories
        categories = ["stadium", "Expressway-toll-station", "bridge", "groundtrackfield", "Expressway-Service-area", "dam",
                      "ship", "basketballcourt", "vehicle", "golffield", "airplane", "baseballfield", "airport",
                      "harbor", "chimney", "tenniscourt", "trainstation", "overpass", "storagetank", "windmill"]
        for i, cat in enumerate(categories):
            coco.add_category(CocoCategory(id=i, name=cat))
    
    elif mode == 'car_other':
        print('"car_other" mode categories')
        coco.add_category(CocoCategory(id=0, name='Other'))
        coco.add_category(CocoCategory(id=1, name='Car'))
        for k,v in category_id_remapping.items():
            if k in 'vehicle':
                category_id_remapping[k] =1
            else:
                category_id_remapping[k]=0
    elif mode == 'car':
        # car related categories: car, pickup, van
        print('"car" mode categories')
        coco.add_category(CocoCategory(id=0, name='Car'))
        category_id_remapping = {'vehicle': '0'}
    else:
        print('pick a defined mode: [original/car_other/car]')
        sys.exit()
    
    
    split_images_lst = []
    with open(split_images_path, 'r') as f:
        for line in f:
            split_images_lst.append(line.strip().split('/')[1])

    # convert dior annotations to coco
    for image_filename in tqdm(image_filepath_list):
        if image_filename in split_images_lst:
            # get image properties
            image_filepath = str(Path(input_image_folder) / image_filename)
            annotation_filename = image_filename.split(".jpg")[0] + ".xml"
            annotation_filepath = str(Path(input_ann_folder) / annotation_filename)
            image = Image.open(image_filepath)
            cocoimage_filename = str(Path(image_filepath)).split(str(Path(data_folder_dir)))[1]
            if cocoimage_filename[0] == os.sep:
                cocoimage_filename = cocoimage_filename[1:]
            # create coco image object
            coco_image = CocoImage(file_name=cocoimage_filename, height=image.size[1], width=image.size[0])
            # read xml annotation file
            tree = ET.parse(annotation_filepath)
            xml_root = tree.getroot()

            # get all object tags in the xml file
            objects = xml_root.findall('object')

            for obj in objects:
                cat_name = obj[0].text
                bbox_tag = obj[2]
                xmin = int(obj[2][0].text)
                ymin = int(obj[2][1].text)
                xmax = int(obj[2][2].text)
                ymax = int(obj[2][3].text)
                #
                # width = maxx-minx, height = maxy-miny
                width = xmax - xmin
                height = ymax - ymin

                bbox = [xmin,
                        ymin,
                        width,
                        height]

                # get category id and name
                category_name = cat_name
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
                        coco_image.add_annotation(coco_annotation)
            coco.add_image(coco_image)

    save_path = output_file_path
    all_json_path = Path(save_path) / "{}.json".format(split_images_path.split('.')[0])
    save_json(data=coco.json, save_path=all_json_path)


if __name__ == "__main__":
    fire.Fire(dior_to_coco)