import os
from pathlib import Path
import fire
from PIL import Image
from sahi.utils.coco import Coco, CocoAnnotation, CocoCategory, CocoImage
from sahi.utils.file import save_json
from tqdm import tqdm
import sys
import xml.etree.ElementTree as ET


NAME_TO_COCO_CATEGORY = {
    "A220": {"name": "A220", "supercategory": "A220"},
    "A321": {"name": "A321", "supercategory": "A321"},
    "A330": {"name": "A330", "supercategory": "A330"},
    "A350": {"name": "A350", "supercategory": "A350"},
    "ARJ21": {"name": "ARJ21", "supercategory": "ARJ21"},
    "Baseball Field": {"name": "Baseball Field", "supercategory": "Baseball Field"},
    "Basketball Court": {"name": "Basketball Court", "supercategory": "Basketball Court"},
    "Boeing737": {"name": "Boeing737", "supercategory": "Boeing737"},
    "Boeing747": {"name": "Boeing747", "supercategory": "Boeing747"},
    "Boeing777": {"name": "Boeing777", "supercategory": "Boeing777"},
    "Boeing787": {"name": "Boeing787", "supercategory": "Boeing787"},
    "Bridge": {"name": "Bridge", "supercategory": "Bridge"},
    "Bus": {"name": "Bus", "supercategory": "Bus"},
    "C919": {"name": "C919", "supercategory": "C919"},
    "Cargo Truck": {"name": "Cargo Truck", "supercategory": "Cargo Truck"},
    "Dry Cargo Ship": {"name": "Dry Cargo Ship", "supercategory": "Dry Cargo Ship"},
    "Dump Truck": {"name": "Dump Truck", "supercategory": "Dump Truck"},
    "Engineering Ship": {"name": "Engineering Ship", "supercategory": "Engineering Ship"},
    "Excavator": {"name": "Excavator", "supercategory": "Excavator"},
    "Fishing Boat": {"name": "Fishing Boat", "supercategory": "Fishing Boat"},
    "Football Field": {"name": "Football Field", "supercategory": "Football Field"},
    "Intersection": {"name": "Intersection", "supercategory": "Intersection"},
    "Liquid Cargo Ship": {"name": "Liquid Cargo Ship", "supercategory": "Liquid Cargo"},
    "Motorboat": {"name": "Motorboat", "supercategory": "Motorboat"},
    "other-airplane": {"name": "other-airplane", "supercategory": "other-airplane"},
    "other-ship": {"name": "other-ship", "supercategory": "other-ship"},
    "other-vehicle": {"name": "other-vehicle", "supercategory": "other-vehicle"},
    "Passenger Ship": {"name": "Passenger Ship", "supercategory": "Passenger Ship"},
    "Roundabout": {"name": "Roundabout", "supercategory": "Roundabout"},
    "Small Car": {"name": "Small Car", "supercategory": "Small Car"},
    "Tennis Court": {"name": "Tennis Court", "supercategory": "Tennis Court"},
    "Tractor": {"name": "Tractor", "supercategory": "Tractor"},
    "Trailer": {"name": "Trailer", "supercategory": "Trailer"},
    "Truck Tractor": {"name": "Truck", "supercategory": "Truck"},
    "Tugboat": {"name": "Tugboat", "supercategory": "Tugboat"},
    "Van": {"name": "Van", "supercategory": "Van"},
    "Warship": {"name": "Warship", "supercategory": "Warship"}
}

CATEGORY_ID_REMAPPING = {
    "A220": "0", 
    "A321": "1", 
    "A330": "2", 
    "A350": "3", 
    "ARJ21": "4", 
    "Baseball Field": "5", 
    "Basketball Court": "6", 
    "Boeing737": "7", 
    "Boeing747": "8",
    "Boeing777": "9", 
    "Boeing787": "10", 
    "Bridge": "11", 
    "Bus": "12", 
    "C919": "13", 
    "Cargo Truck": "14", 
    "Dry Cargo Ship": "15", 
    "Dump Truck": "16",
    "Engineering Ship": "17", 
    "Excavator": "18", 
    "Fishing Boat": "19", 
    "Football Field": "20", 
    "Intersection": "21", 
    "Liquid Cargo Ship": "22",
    "Motorboat": "23", 
    "other-airplane": "24", 
    "other-ship": "25", 
    "other-vehicle": "26", 
    "Passenger Ship": "27", 
    "Roundabout": "28", 
    "Small Car": "29", 
    "Tennis Court": "30", 
    "Tractor": "31", 
    "Trailer": "32", 
    "Truck Tractor": "33", 
    "Tugboat": "34", 
    "Van": "35", 
    "Warship": "36"
}

def fair1m_to_coco(
    data_folder_dir,
    split_images_path,
    output_file_path,
    mode,
    category_id_remapping=None,
):
    """
    Converts fair1m annotations into coco annotation.

    Args:
        data_folder_dir: str
            'fair1m' folder directory
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
    input_image_folder = str(Path(data_folder_dir) / "images")
    input_ann_folder = str(Path(data_folder_dir) / "labelXml")

    image_filepath_list = os.listdir(input_image_folder)
    
    if category_id_remapping is None:
        category_id_remapping = CATEGORY_ID_REMAPPING
    
    # init coco object
    coco = Coco()
    
    if mode == 'original':
        # append categories
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
            if k in ['Small Car', 'Van']:
                category_id_remapping[k] =1
            else:
                category_id_remapping[k]=0
    elif mode == 'car':
        # car related categories: car, pickup, van
        print('"car" mode categories')
        coco.add_category(CocoCategory(id=0, name='Car'))
        category_id_remapping = {'Small Car': '0', 'Van': '0'}
    else:
        print('pick a defined mode: [original/car_other/car]')
        sys.exit()
    
    split_images_lst = []
    with open(split_images_path, 'r') as f:
        for line in f:
            split_images_lst.append(line.strip().split('/')[1])

    # convert fair1m annotations to coco
    for image_filename in tqdm(image_filepath_list):
        if image_filename in split_images_lst:
            # get image properties
            image_filepath = str(Path(input_image_folder) / image_filename)
            annotation_filename = image_filename.split(".tif")[0] + ".xml"
            annotation_filepath = str(Path(input_ann_folder) / annotation_filename)
            image = Image.open(image_filepath)
            cocoimage_filename = str(Path(image_filepath)).split(str(Path(data_folder_dir)))[1]
            if cocoimage_filename[0] == os.sep:
                cocoimage_filename = cocoimage_filename[1:]
            # create coco image object
            coco_image = CocoImage(file_name=cocoimage_filename, height=image.size[1], width=image.size[0])
            # parse annotation file
            ###
            tree = ET.parse(annotation_filepath)
            xml_root = tree.getroot()
            objects = xml_root[3]
            for obj in objects:
                cat = obj[3][0].text
                points = obj[4]
                p1 = points[0].text
                p2 = points[1].text
                p3 = points[2].text
                p4 = points[3].text
                x_corners = []
                y_corners = []
                for p in points:
                    broken = p.text.split(',')
                    x_corners.append(float(broken[0]))
                    y_corners.append(float(broken[1]))

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
                
                category_name = cat
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
    fire.Fire(fair1m_to_coco)
