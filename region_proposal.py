# -*- coding: utf-8 -*-
"""
region_proposal.ipynb

Name: Tchangmena A Nken Allassan

Creation_date: 11/10/2021

Update_date: 11/10/2021

Here we propose a function, which extract, multiple sub images from an image in the form of bounding boxes, using selective 
image search algorithm, after which, we perform intersection over union to get different regions proposals
"""

# !unzip 'Test_Images.zip'

# import necessary libraries
import numpy as np
import pandas as pd
import cv2
from calculate_iou import compute_iou

cv2.setUseOptimized(True)
ss=cv2.ximgproc.segmentation.createSelectiveSearchSegmentation()

#data=pd.read_csv('Train.csv')
#data.head()

def filter_by_iou(image_path,data,thresh=0.5):

  """
  We create many bounding box for a particular image and we filter out the one with iou>=0.5

  image_path: path to the images

  data: data frame containing the labels [class,xmin,ymin,height,width]

  thresh: the threshold of the filtering
  """
  img_name=image_path.split('/')[-1][:-4]

  data_bb=data[data['Image_ID']==img_name].reset_index(drop=True)

  img=cv2.imread(image_path)

  ss.setBaseImage(img)

  ss.switchToSelectiveSearchFast()

  rects=ss.process()

  ss_bbox=rects[:500] #generating 1000 bounding boxes

  filter_selective_search=[]

  negative_example=[]

  pseudo_negative=[]

  #generating iou for the gerated bb_boxes created

  for i in range(len(data_bb)):

    #getting the different coordinates

    true_xmin,true_ymin,true_width,true_height=data_bb.loc[i,'xmin'],data_bb.loc[i,'ymin'],data_bb.loc[i,'width'],data_bb.loc[i,'height']
    true_label=data_bb.loc[i,'class']

    #compute iou for selective search of a label ok
    for j,rect in enumerate(ss_bbox):

      compute_iou_for_selective_search=compute_iou([true_xmin,true_ymin,true_width,true_height],rect)

      if compute_iou_for_selective_search > thresh:

        filter_selective_search.append([list(rect),true_label])

      elif compute_iou_for_selective_search < 0.2:

        pseudo_negative.append(list(rect))

  #remove duplicate entries

  def remove(duplicate):
    final_list=[]
    for num in duplicate:
      if num not in final_list:
        final_list.append(num)
    return(final_list)

  pseudo_negative=remove(pseudo_negative)

  filter_selective_search=remove(filter_selective_search)

  ##now we will try to create a background class

  labels_of_selective_search=[x[0] for x in filter_selective_search]

  for lab in pseudo_negative:

    condition=[]

    for true_labs in labels_of_selective_search:

      iou_for_negative_ex=compute_iou(true_labs,lab)

      condition.append(True) if iou_for_negative_ex <= 0.3 else condition.append(False)

    if False not in condition:

      negative_example.append(lab)

  negative_example=remove(negative_example)

  random_background_images_index = np.random.randint(low=0, high=len(negative_example), size=2*len(labels_of_selective_search))

  random_background_images = [negative_example[x] for x in random_background_images_index]

  return filter_selective_search, remove(random_background_images)
