from __future__ import print_function
import argparse
import cv2 as cv2
import os
from scipy import ndimage

DEFAULT_INPUT_DIR = 'masks'
DEFAULT_OUTPUT_DIR = 'markers'

def read_dataset(input_folder):
    # dataset -> tuple(marker, image, filename)
    dataset = []
    for i,filename in enumerate(os.listdir(input_folder)):
        src_marker = cv2.imread(cv2.samples.findFile(input_folder+"/"+filename))
        src_image = cv2.imread(cv2.samples.findFile(input_folder+"/"+filename))
        
        if src_marker is None:
            print('Could not open or find the image: ', filename)
            exit(0)
        src_image = cv2.cvtColor(src_image, cv2.COLOR_BGR2GRAY)
        dataset.append((filename, src_image, src_marker))
    return dataset

def make_markers(input_dir_name, output_dir_name):
        if not os.path.isdir(output_dir_name):
            os.mkdir(output_dir_name)
        dataset = read_dataset(input_dir_name)
        for item in dataset:
            saveScribbles(item[0], item[1], item[2])

def getMarkers(src_image, src_marker):
    markers = []
    objMarkers = 0
    markers_sizes = []
    getBackground(src_marker)
    width, height, channels = src_marker.shape
    
    image, number_of_objects = ndimage.label(src_marker[:,:,2])
    blobs = ndimage.find_objects(image)
    for i, j in enumerate(blobs):
        marker = []
        for y in range(j[0].start,j[0].stop):
            for x in range(j[1].start,j[1].stop):
                if(image[y,x] != 0):
                    marker.append([x,y])
    
        markers_sizes.insert(0, len(marker))
        markers = marker + markers
        objMarkers += 1

    image, number_of_objects = ndimage.label(src_marker[:,:,0])
    blobs = ndimage.find_objects(image)
    
    for i,j in enumerate(blobs):
      marker = []
      for y in range(j[0].start,j[0].stop):
        for x in range(j[1].start,j[1].stop):
          if(image[y,x] != 0):
            marker.append([x,y])
      
      markers_sizes.append(len(marker))
      markers = markers + marker    

    return markers, objMarkers, markers_sizes

def getBackground(src_marker):
    for i in range(src_marker.shape[0]):
        for j in range(src_marker.shape[1]):
            if(i == 0 or i == (src_marker.shape[0]-1) or j == 0 or j == (src_marker.shape[1]-1)):
                if(src_marker[i,j,0] != 255):
                    src_marker[i,j,0] = 127
                else:
                    src_marker[i,j,0] = 0
            else:
                src_marker[i,j,0] = 0

def saveScribbles(filename, src_image, src_marker):
    markers, objMarkers, markers_sizes = getMarkers(src_image, src_marker)
    if(len(markers) == 0): 
        return
    f = open(DEFAULT_OUTPUT_DIR+"/"+os.path.splitext(filename)[0]+".txt", 'w')
    f.write("%d\n"%(len(markers_sizes)))
    f.write("%d\n"%(markers_sizes[0]))

    index_sizes=0
    acum=0

    for i in range(len(markers)-1):
        if(acum == markers_sizes[index_sizes]):
            index_sizes+=1
            acum=0
            f.write("%d\n"%(markers_sizes[index_sizes]))
        
        [x,y] = markers[i]
        f.write("%d;%d\n"%(x,y))
        acum+=1

    if(acum == markers_sizes[index_sizes]):
        index_sizes+=1
        acum=0
        f.write("%d\n"%(markers_sizes[index_sizes]))
    
    [x,y] = markers[-1]
    f.write("%d;%d\n"%(x,y))
    f.write("%d"%(objMarkers))
    f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Code for Eroding and Dilating tutorial.')
    parser.add_argument('--input', help='Path to input folder.', default=None)
    parser.add_argument('--output', help='Path to output folder.', default = DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    make_markers(args.input, args.output)