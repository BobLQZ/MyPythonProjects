import cv2
import os

def frames_to_video(frame_list, output_path, fps):
    height, width, _ = frame_list[0].shape
    video_writer = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for frame in frame_list:
        video_writer.write(frame)
    video_writer.release()

# 加载图片
def load_images_from_folder(folder_path):
    image_list = []
    for filename in sorted(os.listdir(folder_path)):  # 确保按文件名顺序加载
        if filename.endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(folder_path, filename)
            image = cv2.imread(img_path)  # 使用 OpenCV 读取图片
            if image is not None:
                image_list.append(image)
                print(f"图片: {filename}, 像素大小: {image.shape}")  # 输出图片的像素大小
            else:
                print(f"无法读取图片: {filename}")
    return image_list  # 返回图像列表

# 加载数据
images = load_images_from_folder("my_images/")  # 图片文件夹路径
print(f"加载了 {len(images)} 张图片")  # 输出图片数量和维度

frames_to_video(images, 'plant_growth.mp4', fps=1)
