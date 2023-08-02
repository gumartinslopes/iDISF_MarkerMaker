import argparse
import cv2
import os

# Default directory names if not specified
DEFAULT_MARKER_DIR = 'markers'
DEFAULT_OUTPUT_DIR = 'skeletons'

def make_skeletons(input_dir, output_dir):
      # tuple list(skeleton_img, file_name)
      skeletons = []
      print("*** Generating Skeletons ***")
      for index, file in enumerate(os.listdir(input_dir)):
        img = cv2.imread(input_dir+"/"+file, cv2.IMREAD_GRAYSCALE)
        ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        skeleton = cv2.ximgproc.thinning(img, None, cv2.ximgproc.THINNING_ZHANGSUEN)
        skeletons.append((skeleton, file))
      save_skeleton_list(skeletons, output_dir)   
      return skeletons

def save_skeleton_list(skeletons, output_dir):
  output_dir = output_dir if output_dir!= None else DEFAULT_OUTPUT_DIR 
  if not os.path.isdir(output_dir):
      os.mkdir(output_dir)
  for skeleton in skeletons:
      output_filename = skeleton[1] + '_skeleton.png'
      cv2.imwrite('./' + output_dir + "/" + output_filename, skeleton[0])

def setup_arguments(parser):
   parser.add_argument('--input_dir', help='Path to the folder where the input images are located.')
   parser.add_argument('--output_dir', help='Path to the folder where the output images will be located. If not defined, the default folder will be called skeletons')

def arguments_validated(args):
  if(args.input_dir == None):
      print('Argument Invalid, the input folder path must not be empty!')
      return False
  return True

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Code for generating skeletons on the  given images.')
  setup_arguments(parser)
  args = parser.parse_args()

  if(arguments_validated(args)):
    input_dir = args.input_dir
    output_dir = args.output_dir
    make_skeletons(input_dir, output_dir)