# On terminal, you should use:
# pip install Pillow

from PIL import Image
import filter.rotation
import math

# Input image
image_name = str(input('Image name to be read: '))
input_image = Image.open(image_name)
width, height = input_image.size
print('> Opened image from path \'{0}\' (width = {1}, height = {2})'.format(input_image.fp.name, width, height))

# Rotation angle (in degrees)
degrees = float(input('Rotation angle (in degrees): '))
    
# Conversion from degrees to radians
theta = math.radians(degrees)  

mapping = str(input('Type "direct" for direct_mapping or "reverse" for reverse_mapping.\n'))

# New image rotated
if mapping == 'direct':
    rotation_matrix = filter.rotation.rotate_image_dmap(image_name, theta)
    can_continue = True
elif mapping == 'reverse':
    rotation_matrix = filter.rotation.rotate_image_rmap(image_name, theta)
    can_continue = True
else:
    print('\n\nERROR: the option that you typed does not exist.')
    can_continue = False
    
# Generate output image file
if (can_continue):
    Image.fromarray(rotation_matrix.astype('uint8')).show()
    Image.fromarray(rotation_matrix.astype('uint8')).save('results/rotation_' + mapping + '_mapping_.png')
    print('> New image saved.')