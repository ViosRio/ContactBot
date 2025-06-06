from PIL import Image
import os

class ImageOptimizer:
    def __init__(self, image_folder):
        self.image_folder = image_folder

    def optimize_images(self):
        for filename in os.listdir(self.image_folder):
            if filename.endswith((".jpg", ".jpeg", ".png")):
                image_path = os.path.join(self.image_folder, filename)
                img = Image.open(image_path)

                # Görselin formatını RGB'ye çevirerek kaliteyi koru
                img = img.convert("RGB")
                optimized_path = os.path.join(self.image_folder, f"optimized_{filename}")
                
                # Kaliteyi tam tutarak yeniden kaydet
                img.save(optimized_path, "JPEG", quality=100)  

        print("Görseller başarıyla optimize edildi!")

# Kullanım
image_folder = "./"
optimizer = ImageOptimizer(image_folder)
optimizer.optimize_images()
