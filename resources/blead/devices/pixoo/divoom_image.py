#!/usr/bin/python
# -*- coding: latin-1 -*-
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import math
import os
import sys
import logging
from . timeboximage import TimeBoxImage

def _slices(image,slice_size=16):
    '''Create 10x10 images from a bigger image e.g. 10x40.'''
    width, height = image.size
    slices = 1
    slices = width - slice_size

    result_images = []
    for slice in range(0,slices,2):
        new_box = (slice, 0, slice+slice_size, height)
        new_img = image.crop(new_box)
        result_images.append(new_img)
    return result_images

def scroll_between(old_img, new_img):
    '''Does a scroll between the old and the new image and returns all images in between.'''
    img = None
    img = concatenate(old_img, new_img, 1)
    return sliced_images

def concatenate(image1, image2):
    '''Concatenates the sencond image to the first'''
    width = image1.width + image2.width
    height = max(image1.height, image2.height)
    result_img = create_default_image((width, 16))
    result_img.paste(image1, (0, 0))
    result_img.paste(image2, (image1.width, 0))
    return result_img



def horizontal_slices(image, slice_size=16):
    '''Create 10x10 images from a bigger image e.g. 10x40.'''
    return _slices(image=image,slice_size=slice_size)

def image_horizontal_slices(image_path, slice_size=16):
    '''Create 10x10 images from a bigger image given as path.'''
    img = Image.open(image_path)
    return horizontal_slices(img, slice_size)

def create_default_image(size=(16,16)):
    '''Create an image with the correct palette'''
    im = Image.new("RGBA", size,(0,0,0,255))
    return im

def draw_text_to_image(text, color="red", size=(0,16), empty_start=True, empty_end=True, font = None):
    '''Draws the string in given color to an image and returns this iamge'''
    if not font:
        fn = ImageFont.truetype(os.path.join(os.path.dirname(__file__),'fonts/font.ttf'),16)
    else:
        fn = font
    draw_txt = ImageDraw.Draw(create_default_image())
    width, height = draw_txt.textsize(text, font=fn)
    del draw_txt
    if empty_start:
        width += size[1]
    if empty_end:
        width += size[1]
    im = create_default_image((width, size[1]))
    draw = ImageDraw.Draw(im)
    if empty_start:
        offset_x = size[1]
    else:
        offset_x = 0
    draw.text((offset_x,0), text, font=fn, fill=color)
    del draw
    return im

def draw_multiple_to_image(texts, font=None):
    img_result = create_default_image((0,0))
    empty_start = True
    for txt, color in texts:
        im = draw_text_to_image(txt, color, empty_start=empty_start, empty_end=False, font=font)
        empty_start = False
        img_result = concatenate(img_result, im)
    img_result = concatenate(img_result, create_default_image((16,16)))
    return img_result


def build_img(img, size=(16,16)):
    logging.debug('BUILD IMG')
    tb_img = TimeBoxImage()
    rgb_im = img.convert('RGBA')
    rgb_im = rgb_im.resize((size[0], size[1]))
    arrayPixel=[]
    arrayColor=[]
    for y in range(rgb_im.height):
        for x in range(rgb_im.width):
            r,g,b,a=rgb_im.getpixel((x,y))
            hexcolor=rgb_to_hex((r,g,b))
            if (not (hexcolor in arrayColor)):
                arrayColor.append(hexcolor)
            arrayPixel.append(hexcolor)
    numbits= get_numbits(len(arrayColor))
    data = hex(len(arrayColor))[2:].zfill(2)
    for color in arrayColor:
        data += color
    binary = ''
    for pixel in arrayPixel:
        binary = str(bin(arrayColor.index(pixel))[2:]).zfill(numbits) + binary
    binaryArray = [binary[i:i+8] for i in range(0, len(binary), 8)]
    binaryArray.reverse()
    logging.debug(str(binaryArray))
    for computebinary in binaryArray:
        data += hex(int(computebinary,2))[2:].zfill(2)
    logging.debug(data)
    return data

def build_animation(file, size=(16,16)):
    logging.debug('BUILD ANIMATION')
    alldata = ''
    arrayAllColor=[]
    counter = 0
    with Image.open(file) as imagedata:
        duration = 250
        logging.debug(str(imagedata.info))
        if 'duration' in imagedata.info:
            duration = imagedata.info['duration']
        durationdata = hex(int(duration))[2:].zfill(4)
        for img in getFrames(imagedata):
            data=''
            tb_img = TimeBoxImage()
            rgb_im = img.convert('RGBA')
            rgb_im = rgb_im.resize((size[0], size[1]))
            arrayPixel=[]
            arrayColor=[]
            for y in range(rgb_im.height):
                for x in range(rgb_im.width):
                    r,g,b,a=rgb_im.getpixel((x,y))
                    hexcolor=rgb_to_hex((r,g,b))
                    if (not (hexcolor in arrayColor) and not (hexcolor in arrayAllColor)):
                        arrayColor.append(hexcolor)
                        arrayAllColor.append(hexcolor)
                    arrayPixel.append(hexcolor)
            numbits= get_numbits(len(arrayAllColor))
            data+= hex(len(arrayColor))[2:].zfill(2)
            for color in arrayColor:
                data += color
            binary = ''
            for pixel in arrayPixel:
                binary = str(bin(arrayAllColor.index(pixel))[2:]).zfill(numbits) + binary
            binaryArray = [binary[i:i+8] for i in range(0, len(binary), 8)]
            binaryArray.reverse()
            logging.debug(str(binaryArray))
            for computebinary in binaryArray:
                data += hex(int(computebinary,2))[2:].zfill(2)
            lensubdata = hex(int((len(data)+12)/2))[2:].zfill(4)
            increment = '00'
            if counter>0:
                increment ='01'
            data = 'aa'+lensubdata[2:]+lensubdata[0:2]+durationdata[2:]+durationdata[0:2]+increment+data
            logging.debug(data)
            alldata+=data
            counter+=1
    splitedArray = [alldata[i:i+400] for i in range(0, len(alldata), 400)]
    messagecounter = 0
    lendata = hex(int(len(alldata)/2))[2:].zfill(4)
    messages =[]
    if len(splitedArray) > 1:
        for message in splitedArray:
            messagecounterhex =hex(int(messagecounter))[2:].zfill(2)
            splitdata=''
            splitdata += '49'+lendata[2:]+lendata[0:2]+messagecounterhex
            splitdata += message
            messagecounter +=1
            messages.append(splitdata)
    else:
        messages.append('49'+lendata[2:]+lendata[0:2]+'00'+splitedArray[0])
    return messages


def load_image(file, sz=(16,16)):
    logging.debug('LOADING IMG')
    with Image.open(file).convert("RGBA") as imagedata:
        return build_img(imagedata,sz)

def analyseImage(im):
    '''
    Pre-process pass over the image to determine the mode (full or additive).
    Necessary as assessing single frames isn't reliable. Need to know the mode
    before processing all frames.
    '''
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    im.seek(0)
    return results

def getFrames(im):
    '''
    Iterate the GIF, extracting each frame.
    '''
    mode = analyseImage(im)['mode']

    p = im.getpalette()
    last_frame = im.convert('RGBA')

    try:
        while True:
            '''
            If the GIF uses local colour tables, each frame will have its own palette.
            If not, we need to apply the global palette to the new frame.
            '''
            if not im.getpalette():
                im.putpalette(p)

            new_frame = Image.new('RGBA', im.size)

            '''
            Is this file a "partial"-mode GIF where frames update a region of a different size to the entire image?
            If so, we need to construct the new frame by pasting it on top of the preceding frames.
            '''
            if mode == 'partial':
                new_frame.paste(last_frame)

            new_frame.paste(im, (0,0), im.convert('RGBA'))
            yield new_frame

            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass


def load_gif_frames(file,sz=(16,16)):
    data = []
    with Image.open(file) as imagedata:
        for f in getFrames(imagedata):
            data.append(build_img(f,sz))
    return data

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def get_numbits(nbcolor):
    result = math.log(nbcolor)/math.log(2)
    return int(math.ceil(result))
