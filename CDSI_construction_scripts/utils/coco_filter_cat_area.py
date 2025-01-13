import json
import argparse
from collections import Counter
import pandas as pd
import numpy as np    # to create dummy data
import sys


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
    print('writing the result in json file', filename)
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)


parser = argparse.ArgumentParser(description='coco files checker')
parser.add_argument('-o', '--out-file', dest='out_file', metavar='PATH', help='coco json file')
parser.add_argument('-i', '--input-file', dest='input_file', required=True, help='json file')
parser.add_argument('-m', '--min', dest='min', type=int, metavar='N', help='min area')
parser.add_argument('-x', '--max', dest='max', type=int, metavar='N', help='max area')
parser.add_argument('-c', '--cat', dest='cat', help='category')

args = parser.parse_args()
coco_json_file = args.input_file
out_json_file = args.out_file
min = args.min
max = args.max
cat = args.cat

data = read_json_data(coco_json_file)

print('orig annotation len', len(data['annotations']))
print('orig images len', len(data['images']))
print('orig categories', data['categories'])

cat_id = -1
for i in data['categories']:
    if i['name'] == cat:
        cat_id = i['id']

print('processing category:', cat, ', with id:', cat_id)

imgs = set()
obj_imgs = set()
new_ann = []
obj_range_area = []
cnt = 0
for i in data['annotations']:

    if i['category_id'] == cat_id:
        # get cars or others categories that are between min & max
        if i['area'] >= min and i['area'] < max:
            obj_range_area.append(i)
            obj_imgs.add(i['image_id'])
            new_ann.append(i)
            imgs.add(i['image_id'])


# print('obj-area > 1024:', cnt)
print('len of small objects between min & max', len(new_ann))
print('len images-small between min & max', len(imgs))
########################
new_images = []
for img in data['images']:
    if img['id'] in obj_imgs:
        new_images.append(img)

data['images'] = new_images
data['annotations'] = obj_range_area

out_file = '{}/{}_{}_{}_{}.json'.format('/'.join(out_json_file.split('/')[:-1]), out_json_file.split('/')[-1].split('.')[0], cat, min, max)
if len(obj_range_area) > 0:
    write_to_json(data, out_file)

