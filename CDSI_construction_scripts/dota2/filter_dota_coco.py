"""
this script is written to filter existing dota-coco files generated using dotadevkit for all categories
"""
import sys
import argparse
import json


def read_json_data(filename):
    """
    Get json object from file
    :param filename: path with filename
    :return: json data
    """
    with open(filename) as json_file:
        data = json.load(json_file)
    return data


def write_to_json(data, filename):
    """
    Write dictionary to json file
    :param data: dictionary data
    :param filename: filename to write
    :return: None
    """
    print('writing the result in json file')
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)


parser = argparse.ArgumentParser(description='DOTA-v2.0 coco files filter')
parser.add_argument('-f', '--input-file', dest='input_file', metavar='PATH', help='coco json file')
parser.add_argument('-o', '--out-file', dest='out_file', metavar='PATH', help='out coco json file')
parser.add_argument('-x', '--max', dest='max', type=int, metavar='N', help='max area')
parser.add_argument('--car-only', action='store_true', help='car-only mode')
args = parser.parse_args()

coco_json_file = args.input_file
out_coco_json_file = args.out_file
car_only_mode = args.car_only
max_area = args.max

data = read_json_data(coco_json_file)

print('original_images_len', len(data['images']))
print('original_annotations_len', len(data['annotations']))
print('original_categories_len', len(data['categories']))
print('original_categories', data['categories'])

new_lst = []
img_ids = set()

if car_only_mode:
    for ann in data['annotations']:
        if ann['area'] < max_area and ann['category_id'] == 5:
            ann['category_id'] = 0
            new_lst.append(ann)
            img_ids.add(ann['image_id'])

    data['annotations'] = new_lst

    imgs_uniq = []
    for i in data['images']:
        if i['id'] in img_ids:
            imgs_uniq.append(i)


    data['images'] = imgs_uniq
    data['categories'] = [{'id': 0, 'name': 'Car', 'supercategory': 'Car'}]

else:
    print('=== car-other mode ===')
    
    for ann in data['annotations']:
        if ann['area'] < max_area:
            if ann['category_id'] == 5: # car category
                ann['category_id'] = 1
            else:
                ann['category_id'] = 0
            new_lst.append(ann)
            img_ids.add(ann['image_id'])

    data['annotations'] = new_lst

    imgs_uniq = []
    for i in data['images']:
        if i['id'] in img_ids:
            imgs_uniq.append(i)


    data['images'] = imgs_uniq
    data['categories'] = [{'id': 0, 'name': 'Other', 'supercategory': 'Other'}, {'id': 1, 'name': 'Car', 'supercategory': 'Car'}]
    
    print('=== END car-other mode ===')

print('====================================')
print('modified_images_len', len(data['images']))
print('modified_annotations_len', len(data['annotations']))
print('modified_categories_len', len(data['categories']))

write_to_json(data, out_coco_json_file)
