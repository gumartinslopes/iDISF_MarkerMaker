# -*- coding: utf-8 -*-
import numpy as np
import cv2
from skimage import measure
from skimage.morphology import erosion, disk, dilation, erosion, reconstruction
import argparse

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

def setup_arguments(parser):
    parser.add_argument('-i', help='input mask image path')
    parser.add_argument('-o', help='output label image path')
    parser.add_argument('-r', help='ultimate erosion disk radius')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    setup_arguments(parser)
    args = parser.parse_args()
    input_img = cv2.imread('%s' %(str(args.i)), cv2.IMREAD_UNCHANGED)
    if args.r:
        r = int(args.r)
    
    r = 1
    eroded_image = ultimate_erosion(input_img, r)
    cv2.imwrite('%s' %(str(args.o)), eroded_image)