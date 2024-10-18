from PIL import Image  

def remove_white_background(input_jpg, output_png):  
    # 打开 JPG 文件  
    img = Image.open(input_jpg).convert("RGBA")  
    
    # 获取图像数据  
    datas = img.getdata()  

    new_data = []  
    for item in datas:  
        # 将白色（或近似白色）的背景变为透明  
        if item[0] > 60 and item[1] > 60 and item[2] > 60:  
            new_data.append((255, 255, 255, 0))  # 透明  
        else:  
            new_data.append(item)  
    
    # 更新图像数据  
    img.putdata(new_data)  
    # 保存为 PNG 文件  
    img.save(output_png, "PNG")  

# 使用示例  
remove_white_background("lsj-qm2.jpg", "lsj-qm2.png")