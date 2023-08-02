from __future__ import print_function
import argparse
import cv2
import os
import numpy as np
import argparse
import os
from scipy import ndimage
from skimage import measure
from skimage.morphology import erosion, disk, dilation, erosion, reconstruction
import argparse
from utils.progress_bar import progress_bar

# Default directory names if not specified
DEFAULT_INPUT_DIR = 'markers'
DEFAULT_SIMPLIFICATION_DIR = 'simplifications'
DEFAULT_OUTPUT_DIR = 'markers'
DEFAULT_SIMPLIFICATION_METHOD = 'ultimate_erosion'
simplification_method  = DEFAULT_SIMPLIFICATION_METHOD

method_names = {
    'ue': 'ultimate_erosion',
    'skel': 'skeletization'
}

# -----------------------------------Generating Markers-----------------------------------------
def generate_markers(dataset, output_dir):
    dataset_len = len(dataset)
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    for i, datapoint in enumerate(dataset):
        datapoint['image'] = datapoint['image'].astype('uint8')
        saveScribbles(datapoint["filename"], datapoint["image"], output_dir)
        progress_bar(i + 1, dataset_len)
    print()

def getMarkers(src_marker):
    markers = []
    objMarkers = 0
    markers_sizes = []
    getBackground(src_marker)

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

def saveScribbles(filename, src_marker, output_dir):
    src_marker = cv2.cvtColor(src_marker, cv2.COLOR_GRAY2RGB)
    markers, objMarkers, markers_sizes = getMarkers(src_marker)
    if(len(markers) == 0): 
        return
    
    f = open(output_dir+"/"+os.path.splitext(filename)[0]+".txt", 'w')
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
# --------------------------------------------------------------------------------------------
def ultimate_erosion(input_img, r):
    nb_iter = 0
    mask = generate_erosion_mask(input_img)
    img = mask
    img_niter = np.zeros_like(mask, dtype='uint16') 
    while(np.max(img) > 0):
        img_ero = erosion(img, disk(r))
        nb_iter = nb_iter+1
        reconst= reconstruction(img_ero, img,'dilation')
        residues = img - reconst
        img_niter = np.where(residues==1, nb_iter, img_niter)
        img = img_ero

    # residues relabel
    img_residue = img_niter
    img_residue[img_residue>0] = 1
    img_residue = dilation(img_residue, disk(3))
    img_residue = measure.label(img_residue, connectivity=2, background=0)
    img_residue = erosion(img_residue, disk(3))

    # reconstruction
    img_rc = np.zeros_like(img_residue, dtype='uint16') 
    i = np.max(img_niter)

    while i > 1:
        img_rc = np.where(img_niter == i, img, img_rc) 
        img_rc = dilation(img_rc, disk(r))
        i = i-1

    img_rc = np.where(img_niter == i, img_residue, img_rc) 
    return img_rc
    
def generate_erosion_mask(input_img):
    mask = np.zeros_like(input_img[..., 0], dtype='uint16') 
    mask = np.where((input_img[..., 0] > 0), 1, mask)
    mask = mask.astype(np.uint16)
    return mask

def erode(dataset, save_simplification, output_dir):
    eroded_dataset = []
    dataset_len = len(dataset)
    for i, datapoint in enumerate(dataset):
        img = datapoint['image']
        #img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        _, img = cv2.threshold(img, 100, 255, cv2.THRESH_BINARY)
        eroded_image = ultimate_erosion(img, 1)
        eroded_dataset.append({"filename": datapoint['filename'], "image": eroded_image})
        progress_bar(i + 1, dataset_len)
    print()
    if save_simplification:
        save_simplification_list(eroded_dataset, output_dir)
    return eroded_dataset

def skeletonize(dataset, save_simplification, output_dir):
    skeletons = []
    dataset_len = len(dataset)
    for i, datapoint in enumerate(dataset):
        img = datapoint['image']
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        skeleton = cv2.ximgproc.thinning(img, None, cv2.ximgproc.THINNING_ZHANGSUEN)
        skeletons.append({"filename": datapoint['filename'], "image": skeleton})
        progress_bar(i + 1, dataset_len)
    print()
    if save_simplification:
        save_simplification_list(skeletons, output_dir)
    return skeletons

def read_dataset(input_dir):
    dataset = []
    for i, filename in enumerate(os.listdir(input_dir)):
        img = cv2.imread(input_dir+"/"+filename, cv2.IMREAD_UNCHANGED)
        dataset.append({"filename": filename, "image": img})
    return dataset

def save_simplification_list(simplified_images, output_dir):
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)
    for skeleton in simplified_images:
        output_filename = skeleton["filename"] + f'_{simplification_method}.png'
        cv2.imwrite('./' + output_dir + "/" + output_filename, skeleton["image"])

def make_markers(input_dir, output_dir, save_simplification, simplification_dir):
    dataset = read_dataset(input_dir)
    print('*** Simplifying images ***')
    if simplification_method == method_names['skel']:
        simplifications = skeletonize(dataset, save_simplification, simplification_dir)
    else:
        simplifications = erode(dataset, save_simplification, simplification_dir)
    print('*** Generating markers ***')
    generate_markers(simplifications, output_dir)

def setup_arguments(parser):
    parser.add_argument('--input_dir', help='Path to the folder where the input images are located.')
    parser.add_argument('--output_dir', help='Path to the folder where the output markers will be located.', default=DEFAULT_OUTPUT_DIR)
    parser.add_argument('--save_simplifications', help='Type y to save the skeletons of the image', default = 'N')
    parser.add_argument('--simplification_dir', help='Path to the folder where the output simplifications will be located.', default=DEFAULT_SIMPLIFICATION_DIR)
    parser.add_argument('--simplification_method', help='Method used to simplify the images.', default=DEFAULT_SIMPLIFICATION_METHOD)

def arguments_validated(args):
    if(args.input_dir == None):
        print('Argument Invalid, the input folder path must not be empty!')
        return False
    return True

if __name__ == '__main__':
  acceptable_words = ['yes', 'y', 'sim', 'positive', 't', 'true']
  parser = argparse.ArgumentParser(description='Code for generating the iDISF markers given images.')
  setup_arguments(parser)
  args = parser.parse_args()

  if(arguments_validated(args)):
    input_dir = args.input_dir
    output_dir = args.output_dir
    if args.simplification_method.lower()  == 'skel':
        simplification_method =  method_names['skel'] 
    save_simplification = args.save_simplifications.lower() in acceptable_words
    simplification_dir = args.simplification_dir
    make_markers(input_dir, output_dir, save_simplification, simplification_dir)