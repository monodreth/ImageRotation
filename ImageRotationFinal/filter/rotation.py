# Rotation funcions

from PIL import Image
import numpy
import math

rgb_channels_size = 3  # 3 because means RGB. Do not change this!

# Creates an extended matrix to the size that will be needed
# in the final image (rotated) 

def extended_matrix(image_name, theta):
    # Opening original image
    input_image = Image.open(image_name)
    width, height = input_image.size
    
    # sin(theta) and cos(theta)
    sin = math.sin(theta)
    cos = math.cos(theta)
    
    # New image size
    if theta <= math.pi/2: # theta <= 90º
        newHeight = round(width * sin + height * cos)
        newWidth = round(width * cos + height * sin)
    elif math.pi/2 < theta <= math.pi: # 90º < theta <= 180º
        newHeight = round(width * sin + -height * cos)
        newWidth = round(-width * cos + height * sin)
    elif math.pi < theta <= 3*math.pi/2: # 180º < theta <= 270º
        newHeight = round(-width * sin + -height * cos)
        newWidth = round(-width * cos + -height * sin)
    elif 3*math.pi/2 < theta <= 2*math.pi: # 270º < theta <= 360º
        newHeight = round(-width * sin + height * cos)
        newWidth = round(width * cos + -height * sin)
    print('> New image size: (width = {0}, height = {1})\n'.format(newWidth, newHeight))
    
    # New clean image
    extended_matrix = numpy.zeros((newHeight, newWidth, rgb_channels_size))
    
    return extended_matrix

# Image rotation - Direct mapping
# Rotation based on angle 'theta' and center of rotation (xCenter, yCenter)
def rotate_image_dmap(image_name, theta): 
    # Opening image
    input_image = Image.open(image_name)
    width, height = input_image.size
    
    # Angle fix
    theta = theta % (2*math.pi)  # Range fix (prevent values more than 360)
    if theta < 0:
        theta = theta + 2*math.pi # Fix negative values
    print('Actual angle read (in degrees): {0}'.format(round(math.degrees(theta), 2)))
    print()
    
    # New image with extended size and clean
    extended_mat = extended_matrix(image_name, theta)
    newWidth = extended_mat.shape[0]
    newHeight = extended_mat.shape[1]
    
    # Center position
    yCenter = int((height - 1) / 2)
    xCenter = int((width - 1) / 2)
    print('> Center position (of original image): (x = {0}, y = {1})'.format(xCenter, yCenter))
    print()
        
    # Fix black line (issues with some angles)
    dX = 0
    dY = 0
    if theta == math.pi/2: # same as 90º
        dY = 1
    elif theta == 3*math.pi/2: # same as 270º
        dX = 1
    elif theta == 0: #same as 360º or 2*pi
        dX = 1
        dY = 1
    
    # Final matrix
    rotation_matrix = numpy.copy(extended_mat) 
    
    # sin(theta) and cos(theta)
    sin = math.sin(theta)
    cos = math.cos(theta)
    
    print('> Generating new image ...\n')
    # Definition of the new value of (x, y) for each pixel after rotation
    for y in range(height):
        for x in range(width):
            original_pixel = input_image.getpixel((x, y))
            
            # New center position
            toYCenter = y - yCenter
            toXCenter = x - xCenter
    
            # Offset         
            offsetY = round(newWidth / 2 - yCenter) -dY
            offsetX = round(newHeight / 2 - xCenter) -dX
    
            # New position
            toY = round(toXCenter * sin + toYCenter * cos + yCenter) + offsetY
            toX = round(toXCenter * cos - toYCenter * sin + xCenter) + offsetX
    
            # Make sure the new points are within the dimensions of the new image
            toY = min(toY, newWidth - 1)  
            toX = min(toX, newHeight - 1)  
    
            rotation_matrix[toY, toX] = original_pixel
    return rotation_matrix

def bilinear_interpolation(image_name, x, y):
    # Opening image
    input_image = Image.open(image_name)
    
    i = int(x)
    j = int(y)
          
    pixel = input_image.getpixel((i, j))                   # f(i, j)
    right_pixel = input_image.getpixel((i+1, j))           # f(i+1, j)
    down_pixel = input_image.getpixel((i, j+1))            # f(i, j+1)
    down_right_pixel = input_image.getpixel((i+1, j+1))    # f(i+1,j+1)
    
    ### Steps to get the bellow equations (for interpolation reconstruction) ###
    ####################### in the tuple (R, G, B): ############################
    #   f(i, y) = f(i, j) + (y - j)*[f(i, j+1) - f(i, j)]
    #   f(i+1, y) = f(i+1, j) + (y - j)*[f(i+1, j+1) - f(i+1, j)]
    #   f(x, y) = f(i, y) + (x - i)*[f(i+1, y) - f(i, y)]
    
    subY = (y - j)
    subX = (x - i)
    
    # d_pixel_minus_pixel = (y - j)*[f(i, j+1) - f(i, j)]
    d_pixel_minus_pixel = [elemA - elemB for elemA, elemB in zip(down_pixel, pixel)]
    d_pixel_minus_pixel = [i*subY for i in d_pixel_minus_pixel]
    
    # dr_pixel_minus_r_pixel = (y - j)*[f(i+1, j+1) - f(i+1, j)]
    dr_pixel_minus_r_pixel = [elemA - elemB for elemA, elemB in zip(down_right_pixel, right_pixel)]
    dr_pixel_minus_r_pixel = [i*subY for i in dr_pixel_minus_r_pixel]
    
    # f(i, y) = f(i, j) + (y - j)*[f(i, j+1) - f(i, j)]
    f_iy = [elemA + elemB for elemA, elemB in zip(pixel, d_pixel_minus_pixel)]
    
    # f(i+1, y) = f(i+1, j) + (y - j)*[f(i+1, j+1) - f(i+1, j)]
    f_i1y = [elemA + elemB for elemA, elemB in zip(right_pixel, dr_pixel_minus_r_pixel)]
    
    # f_i1y_minus_f_iy = (x - i)*[f(i+1, y) - f(i, y)]
    f_i1y_minus_f_iy = [elemA - elemB for elemA, elemB in zip(f_i1y, f_iy)]
    f_i1y_minus_f_iy = [i*subX for i in f_i1y_minus_f_iy]
    
    # f(x, y) = f(i, y) + (x - i)*[f(i+1, y) - f(i, y)]
    f_xy = [elemA + elemB for elemA, elemB in zip(f_i1y, f_i1y_minus_f_iy)]
    f_xy = [max(0, min(round(i), 255)) for i in f_xy] # To make sure that
                                                      # the value will be
                                                      # within range [0, 255]
    # f(x, y) returns the corresponding (R, G, B) of the original image
    ###########################################################################
    
    # (R, G, B) values of the corresponding pixel in the original image
    original_pixel = f_xy
    
    # Fix for images that have more than 3 channels
    if len(original_pixel) > 3:
        for i in range(3, len(pixel)): 
            del(original_pixel[i])
        
    return original_pixel

def rotate_image_rmap(image_name, theta):
    # Opening image
    input_image = Image.open(image_name)
    width, height = input_image.size
    
    # Angle fix
    theta = theta % (2*math.pi)  # Range fix (prevent values more than 360)
    if theta < 0:
        theta = theta + 2*math.pi # Fix negative values
    print('Actual angle read (in degrees): {0}'.format(round(math.degrees(theta), 2)))
    print()
    
     # Fix black line (issues with some angles)
    dY = 0.5
    dX = 0.5
    if theta == math.pi/2: # same as 90º
        dX = 1.5 
    elif theta == 3*math.pi/2: # same as 270º
        dY = 1.5
    elif theta == 0: #same as 360º or 2*pi
        dY = 1.5
        dX = 1.5
        
    # New image with extended size and clean
    extended_mat = extended_matrix(image_name, theta)
    newWidth = extended_mat.shape[0]
    newHeight = extended_mat.shape[1]
    
    # Center position
    yCenter = int((newHeight -1) / 2)
    xCenter = int((newWidth -1) / 2)
    print('> Center position (of original image): (x = {0}, y = {1})'.format(xCenter, yCenter))
    print()
    
    # Final matrix
    rotation_matrix = numpy.copy(extended_mat) 
    
    # sin(theta) and cos(theta)
    sin = math.sin(-theta)
    cos = math.cos(-theta)

    print('> Generating new image ...\n')
    # Definition of the new value of (x, y) for each pixel after rotation
    for toX in range (newHeight):
        for toY in range (newWidth):
                
            # New center position
            toYCenter = toY - yCenter
            toXCenter = toX - xCenter
    
            # Offset         
            offsetY = width / 2 - yCenter
            offsetX = height / 2 - xCenter
    
            # New position
            y = (toXCenter * sin + toYCenter * cos + yCenter) + offsetY - dY
            x = (toXCenter * cos - toYCenter * sin + xCenter) + offsetX - dX
            
            # Ensures that the point (x, y) to be searched for exists in the original image
            if (int(x) >= 0) and (int(x+1) < height) and (int(y) >= 0) and (int(y+1) < width):
                original_pixel = bilinear_interpolation(image_name, x , y)
                rotation_matrix[toY, toX] = original_pixel
                
    return rotation_matrix