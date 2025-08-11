from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icon():
    """创建应用图标"""
    # 创建512x512的图标
    size = 512
    img = Image.new('RGBA', (size, size), (70, 130, 180, 255))  # 钢蓝色背景
    draw = ImageDraw.Draw(img)
    
    # 绘制时钟图标
    center = size // 2
    radius = size // 3
    
    # 绘制外圆
    draw.ellipse([center-radius, center-radius, center+radius, center+radius], 
                 outline=(255, 255, 255, 255), width=8)
    
    # 绘制时针和分针
    # 时针指向3点
    draw.line([center, center, center+radius//2, center], 
              fill=(255, 255, 255, 255), width=6)
    # 分针指向12点
    draw.line([center, center, center, center-radius*0.8], 
              fill=(255, 255, 255, 255), width=4)
    
    # 绘制中心点
    draw.ellipse([center-8, center-8, center+8, center+8], 
                 fill=(255, 255, 255, 255))
    
    # 添加文字
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    
    text = "限时"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    text_x = (size - text_width) // 2
    text_y = center + radius // 2
    
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)
    
    # 保存不同尺寸的图标
    img.save('icon.png')
    
    # 创建启动画面
    splash = Image.new('RGBA', (720, 1280), (70, 130, 180, 255))
    splash_draw = ImageDraw.Draw(splash)
    
    # 在启动画面中央放置图标
    icon_size = 200
    resized_icon = img.resize((icon_size, icon_size))
    splash.paste(resized_icon, ((720-icon_size)//2, (1280-icon_size)//2))
    
    # 添加应用名称
    try:
        title_font = ImageFont.truetype("arial.ttf", 60)
    except:
        title_font = ImageFont.load_default()
    
    title = "手机时间限制器"
    title_bbox = splash_draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (720 - title_width) // 2
    title_y = (1280 + icon_size) // 2 + 50
    
    splash_draw.text((title_x, title_y), title, fill=(255, 255, 255, 255), font=title_font)
    
    splash.save('presplash.png')
    
    print("图标和启动画面创建完成！")

if __name__ == "__main__":
    create_app_icon()