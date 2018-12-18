import numpy as np
import json
import sys
from time import time

from imageio import imread, imsave
from skimage.transform import resize
from PIL import Image, ImageDraw

import requests
from io import BytesIO

map_id = {'Void':0, 'Sky':1, 'Vegetation':2, 'Building':3, 'Sidewalk':4,
          'Obstacles on sidewalk':5, 'Pole':6, 'Road':7, 'Curb Stone':8, 'Lane Divider &amp; Traffic Cone':9,
          'Lane':10, 'Traffic Sign':11, 'Traffic Light':12, 'other Obstacles on road':13,
          'Truck':14, 'Bus':15, 'Car':16, 'Tricycle':17, 'Bicycle &amp; Motor':18, 'Person':19}

map_id_reversed = {map_id[key]:key for key in map_id}

label_colours = np.array([[0,0,0], [69, 129, 180], [106, 142, 35], [69, 69, 69], [244, 35, 231],
                 [100, 30, 30], [153, 153, 153], [128, 64, 128], [102, 102, 156], [190, 153, 153],
                 [128,128,128], [219, 219, 0], [250, 170, 29], [0, 60, 100],
                 [0, 0, 69], [0, 60, 100],  [0, 0, 142], [0, 0, 230], [119, 10, 32], [219, 19, 60]])

width, height = 1920, 1200

def add_color(mask):
    h, w = mask.shape
    mask = mask.reshape(-1)
    color_mask = label_colours[mask].reshape(h, w, 3)
    return color_mask

def show(img, output, color_ratio=0.6, shape=None):
    color = add_color(output)
    img_resized = resize(img, color.shape[:2])
    img_show = color/255.*color_ratio + img_resized*(1-color_ratio)
    if shape:
        img_show = resize(img_show, shape)
    return img_show

def get_mask(img_d):
    img_path = img_d['name'].replace('2.2', '3.101')
    img = imread(BytesIO(requests.get(img_path).content))

    mask = Image.new('L', (width, height), 0)
    labels = {i:[] for i in range(1,20)}

    if not img_d['labels']:
        print('Unlabeled, check latter; )')
    else:
        for label in img_d['labels']:
            category = label['category']

            for poly in label['poly2d']:
                polygon = list(np.array(poly['vertices']).reshape(-1))
                labels[map_id[category]].append(polygon)
        for i in range(1,20):
            for polygon in labels[i]:
                ImageDraw.Draw(mask).polygon(polygon, outline=i, fill=i)
    return img, np.array(mask)

def category_show(img, mask, i):
    mask_cp = np.copy(mask)
    mask_cp[mask_cp != i] = 0
    return show(img, mask_cp)

def get_idx(task, item):
    return task*300+(item-1)

task = int(sys.argv[1])
item = int(sys.argv[2])
project_name = sys.argv[3]

print(task, item, project_name)

d = requests.get('http://192.168.3.101:8686/postExport?project_name='+project_name).json()

i = get_idx(task, item)
img, mask = get_mask(d[i])
mask_show = show(img, mask)
imsave('mask.jpg', mask_show)
mask[mask==0]=255
imsave('unlabeld_area.jpg', mask)
