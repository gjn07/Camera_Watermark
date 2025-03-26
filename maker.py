import exifread
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from PIL.ExifTags import TAGS
import os

def create_rounded_rectangle_mask(size, radius):
    width, height = size
    mask = Image.new('L', size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
    return mask

def get_photo_info(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        info = {}

        # 获取焦距信息
        focal_length_key = None
        for tag, value in TAGS.items():
            if value == 'FocalLength':
                focal_length_key = tag
                break
        if focal_length_key and focal_length_key in exif_data:
            focal_length = exif_data[focal_length_key]
            if isinstance(focal_length, tuple):
                focal_length = focal_length[0] / focal_length[1]
            info['focal_length'] = focal_length
        else:
            info['focal_length'] = None

        # 获取光圈大小信息
        aperture_key = None
        for tag, value in TAGS.items():
            if value == 'FNumber':
                aperture_key = tag
                break
        if aperture_key and aperture_key in exif_data:
            aperture = exif_data[aperture_key]
            if isinstance(aperture, tuple):
                aperture = aperture[0] / aperture[1]
            info['aperture'] = aperture
        else:
            info['aperture'] = None

        # 获取感光度信息
        iso_key = None
        for tag, value in TAGS.items():
            if value == 'ISOSpeedRatings':
                iso_key = tag
                break
        if iso_key and iso_key in exif_data:
            info['iso'] = exif_data[iso_key]
        else:
            info['iso'] = None

        return info
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def process_image(input_path, output_path):
    # 打开原始图片
    image = Image.open(input_path)

    # 扩大图片 20%
    width, height = image.size
    new_width = int(width * 1.2)
    new_height = int(height * 1.2)
    x = int(new_width * 0.1)
    y = int(new_height * 0.07)
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)

    # 高斯模糊
    blurred_image = resized_image.filter(ImageFilter.GaussianBlur(radius=100))

    # 打开照片
    photo = Image.open(input_path)
    photo_width = photo.width
    photo_height = photo.height
    photo = photo.resize((photo_width, photo_height), Image.LANCZOS)

    # 创建圆角矩形遮罩
    radius = 150
    mask = create_rounded_rectangle_mask((photo_width, photo_height), radius)

    # 应用遮罩到照片
    photo = Image.composite(photo, Image.new('RGBA', photo.size, (0, 0, 0, 0)), mask)

    # 创建一个带有四周阴影的照片
    shadow_size = 150
    shadow_color = (0, 0, 0, 100)

    # 创建一个透明的图像用于绘制阴影
    shadow_image = Image.new('RGBA', blurred_image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_image)
    # 绘制圆角矩形阴影
    shadow_draw.rounded_rectangle((x - shadow_size, y - shadow_size, x + photo_width + shadow_size,
                                   y + photo_height + shadow_size), radius=radius + shadow_size, fill=shadow_color)

    # 对阴影图像进行模糊处理
    shadow_image = shadow_image.filter(ImageFilter.GaussianBlur(radius=shadow_size))

    # 将阴影图像与原图像合并
    blurred_image = Image.alpha_composite(blurred_image.convert('RGBA'), shadow_image)

    # 将圆角矩形照片粘贴到指定位置
    blurred_image.paste(photo, (x, y), photo)

    # 保存处理后的图片
    blurred_image.convert('RGB').save(output_path)

    # 添加文字到图片下方靠上一点的位置
    draw = ImageDraw.Draw(blurred_image)
    # 设置字体文件和大小
    font_size = 90
    font = ImageFont.truetype("ARLRDBD.TTF", font_size)
    str1 = ""
    texts = ["1", "2"]
    exposure_time = ''
    with open(input_path, 'rb') as f:
        tags = exifread.process_file(f)
        # 使用get方法获取键的值，如果键不存在则返回空字符串
        image_make = str(tags.get('Image Make', ''))
        image_model = str(tags.get('Image Model', ''))
        ss = str(tags.get('EXIF ExposureTime', ''))
        # 拼接字符串
        texts[0] = image_make + " " + image_model
        str1 = str(ss)


    photo_info = get_photo_info(input_path)
    if photo_info:
        s1 = str(photo_info['focal_length']) if photo_info['focal_length'] else "None"
        s2 = str(photo_info['aperture']) if photo_info['aperture'] else "None"
        s3 = str(photo_info['iso']) if photo_info['iso'] else "None"

        texts[1] = s1 + "mm F" + s2 + " " + str1 + "s ISO" + s3
    line_height = font.getbbox(texts[0])[3] - font.getbbox(texts[0])[1]
    total_text_height = line_height * len(texts)
    padding = int(new_height * 0.05)
    available_height = blurred_image.height - padding - total_text_height

    left, top, right, bottom = font.getbbox(texts[0])
    text_width = right - left
    text_x = (blurred_image.width - text_width) // 2
    text_y = available_height
    draw.text((text_x, text_y), texts[0], fill=(255, 255, 255), font=font)

    left, top, right, bottom = font.getbbox(texts[1])
    text_width = right - left
    text_x = (blurred_image.width - text_width) // 2
    text_y = available_height + line_height * 2
    draw.text((text_x, text_y), texts[1], fill=(255, 255, 255), font=font)

    # 保存处理后的图片
    blurred_image.convert('RGB').save(output_path)
    print(f"图片处理完成，保存至 {output_path}")

def make_watermark(input_image_path):
    filename = os.path.basename(input_image_path)
    output_image_path = './' + str(filename)
    process_image(input_image_path, output_image_path)
    return output_image_path