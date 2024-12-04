import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import transforms
from PIL import Image
import numpy as np
import os
import cv2

# 加载图片
def load_images_from_folder(folder_path):
    image_list = []
    transform = transforms.Compose([
        transforms.ToTensor(),  # 转换为张量
    ])
    for filename in sorted(os.listdir(folder_path)):  # 确保按文件名顺序加载
        if filename.endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(folder_path, filename)
            image = Image.open(img_path).convert("RGB")  # 确保是 RGB 图片
            image = transform(image)
            image_list.append(image)
    return torch.stack(image_list)  # 将所有图片合并为一个张量

# 加载数据
images = load_images_from_folder("my_images/")  # 图片文件夹路径
print(f"加载了 {images.shape[0]} 张图片，大小为 {images.shape[1:]}")  # 输出图片数量和维度

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

images = images.to(device)  # 数据转移到 GPU

# 定义VAE模型
class VAE(nn.Module):
    def __init__(self, img_channels=3, latent_dim=16):
        super(VAE, self).__init__()

        self.img_channels = img_channels
        self.latent_dim = latent_dim

        # 编码器部分
        self.encoder_conv = nn.Sequential(
            nn.Conv2d(img_channels, 32, 4, 2, 1),  # 32xH/2xW/2
            nn.ReLU(),
            nn.Conv2d(32, 64, 4, 2, 1),   # 64xH/4xW/4
            nn.ReLU(),
            nn.Conv2d(64, 128, 4, 2, 1),   # 128xH/8xW/8
            nn.ReLU()
        )

        # 计算图像经过卷积层后得到的尺寸
        self._to_latent_dim = self._get_conv_output((3, 64, 64))  # 假设输入是 64x64 大小的图像
        self.fc_mu = nn.Linear(self._to_latent_dim, latent_dim)
        self.fc_logvar = nn.Linear(self._to_latent_dim, latent_dim)

        # 解码器部分
        self.fc_decode = nn.Linear(latent_dim, self._to_latent_dim)
        self.decoder_conv = nn.Sequential(
            nn.ConvTranspose2d(128, 64, 4, 2, 1),
            nn.ReLU(),
            nn.ConvTranspose2d(64, 32, 4, 2, 1),
            nn.ReLU(),
            nn.ConvTranspose2d(32, img_channels, 4, 2, 1),
            nn.Sigmoid()  # 输出 RGB 图片
        )

    # 计算卷积后的尺寸
    def _get_conv_output(self, shape):
        # 模拟通过卷积层后的输出尺寸
        o = torch.rand(1, *shape)
        o = self.encoder_conv(o)
        return int(np.prod(o.size()))

    def encode(self, x):
        x = self.encoder_conv(x)
        x = x.view(x.size(0), -1)  # 展平
        print(f"Shape after flattening: {x.shape}")  # 添加调试打印
        mu = self.fc_mu(x)
        logvar = self.fc_logvar(x)
        return mu, logvar

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        x = self.fc_decode(z)
        x = x.view(-1, 128, 8, 8)  # 根据上面的尺寸计算，解码成原始尺寸
        x = self.decoder_conv(x)
        return x

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar

# 训练过程
def train_vae(images, epochs=100, latent_dim=16, lr=1e-3):
    vae = VAE(latent_dim=latent_dim).to(device)  # 模型转移到 GPU
    optimizer = optim.Adam(vae.parameters(), lr=lr)
    criterion = nn.MSELoss()

    for epoch in range(epochs):
        vae.train()
        optimizer.zero_grad()
        recon_imgs, mu, logvar = vae(images)  # 数据已经在 GPU 上
        # 损失函数：重建误差 + KL散度
        recon_loss = criterion(recon_imgs, images)
        # kl_divergence = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        kl_divergence = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()) / images.size(0)  # 加上 batch 平均
        loss = recon_loss + kl_divergence
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 10 == 0:
            print(f"Epoch [{epoch + 1}/{epochs}], Loss: {loss.item():.4f}")

    return vae

# 插值生成中间帧
def generate_interpolations(vae, images, num_steps=10):
    # 确保 VAE 在评估模式
    vae.eval()
    with torch.no_grad():
        mu1, _ = vae.encode(images[0:1].to(device))  # 数据转移到 GPU
        mu2, _ = vae.encode(images[-1:].to(device))  # 数据转移到 GPU
        interpolations = []
        for alpha in np.linspace(0, 1, num_steps):
            z = (1 - alpha) * mu1 + alpha * mu2
            interp_img = vae.decode(z).cpu()  # 解码后的结果转移到 CPU
            interpolations.append(interp_img.squeeze(0).permute(1, 2, 0).numpy())
    return interpolations

# 创建视频
def create_video(image_folder, video_name, fps=24):
    images = [img for img in os.listdir(image_folder) if img.endswith(".png")]
    images.sort()  # 按名称排序

    frame = cv2.imread(os.path.join(image_folder, images[0]))
    height, width, _ = frame.shape

    video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_folder, image)))

    video.release()

# 主程序
vae = train_vae(images, epochs=100, latent_dim=16, lr=1e-3)
interpolations = generate_interpolations(vae, images, num_steps=30)  # 生成30帧中间图像

# 保存生成的图片
for i, img in enumerate(interpolations):
    img = (img * 255).clip(0, 255).astype(np.uint8)  # 将像素值转换为0-255, 8位图像
    save_path = f"interpolation_frame_{i}.png"
    cv2.imwrite(save_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

# 合成视频
create_video("output_images", "growth_video.mp4")
print("视频已生成：growth_video.mp4")
