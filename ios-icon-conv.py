import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os

def resize(size):
    ## 读取原始图片
    img_original = Image.open("circle-cropped.png")
    print('generating {}x{}'.format(size, size))
    img = img_original.resize((size, size))
    img.save('output/icon_{}x{}.png'.format(size, size))

def preview_np(np_img):
    img = Image.fromarray(np_img, 'RGBA')
    img.show()

def preview_np_RGB(np_img):
    img = Image.fromarray(np_img, 'RGB')
    img.show()

def get_mask_margin(np_mask):
    return 0,0,0,0

def load_mask_image(mask_filename):
    img_mask = Image.open(mask_filename)
    np_mask = np.array(img_mask)
    assert (np_mask.shape[2] == 4)
    if np_mask.shape[0] == 34:
        img_mask = img_mask.resize((32,32))
        np_mask = np.array(img_mask)
    margin = get_mask_margin(np_mask)
    print('Mask margin: ', margin)
    mask_actual_width = np_mask.shape[1] - margin[1] - margin[3]
    mask_actual_height = np_mask.shape[0] - margin[0] - margin[2]
    print('Mask real size: ', (mask_actual_width, mask_actual_height))
    return np_mask, margin, mask_actual_width, mask_actual_height

def generate_icon(mask_filename, image_filename):
    np_mask, margin, mask_actual_width, mask_actual_height = load_mask_image('ios-templates/'+mask_filename)
    img = Image.open('input/'+image_filename)
    mask_side_length = max(mask_actual_height, mask_actual_width)
    # 裁切原图为正方形
    np_img = np.array(img)
    print('Input image size: ', np_img.shape)
    img_side_length = np.min([np_img.shape[0], np_img.shape[1]])
    np_img = np_img[0:img_side_length,0:img_side_length,:]
    print('Croped image size: ', np_img.shape)
    #preview_np_RGB(np_img)
    img_cropped = Image.fromarray(np_img, 'RGB')
    img_cropped = img_cropped.resize((mask_actual_width, mask_actual_height))
    np_cropped = np.array(img_cropped)
    print('resized image size: ', np_cropped.shape)
    # 覆盖mask
    mask_identity = np.sum(np_mask, 2)
    line_length_margin = 0
    for i in range(margin[0]+line_length_margin, mask_identity.shape[0]-margin[2]-line_length_margin):
        for j in range(margin[3]+line_length_margin, mask_identity.shape[1]-margin[1]-line_length_margin):
            if mask_identity[i][j] > 200*4:
                np_mask[i][j] = [*np_cropped[i-margin[0]][j-margin[3]], 255]
    # 保存文件
    img = Image.fromarray(np_mask, 'RGBA')
    img.save('output/{}_ios/{}'.format(image_filename, mask_filename))

def gen_ios14_icon_(input_filename):
    templates = (os.listdir('ios-templates'))
    for maskf in templates:
        print('** Generating: {} **'.format(maskf))
        generate_icon(maskf, input_filename)

def gen_ios14_icon():
    inputs = (os.listdir('input'))
    for inpf in inputs:
        if inpf[0] == '.':
            continue
        print(" ==================== ")
        print("  {}".format(inpf))
        try:
            os.mkdir('output/{}_ios'.format(inpf))
        except:
            pass
        gen_ios14_icon_(inpf)

if __name__ == "__main__":
    try:
        os.mkdir("output")
    except:
        pass
    gen_ios14_icon()