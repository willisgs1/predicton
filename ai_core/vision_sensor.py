import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
import torchvision.transforms as transforms
import torchvision.models as models
import torch
import numpy as np

class VisionSensor:
    def __init__(self):
        # We use a lightweight pre-trained MobileNetV3 for "Sight"
        # It converts images into a 1000-dimensional vector (classification logits)
        # We will reduce this to a smaller vector for our Brain.
        try:
            self.model = models.mobilenet_v3_small(weights=models.MobileNet_V3_Small_Weights.DEFAULT)
            self.model.eval()
            print("[Vision] MobileNetV3 Retina initialized.")
        except Exception as e:
            print(f"[Vision] Warning: Could not load Retina ({e}). Vision will be blind.")
            self.model = None

        self.preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

    def scan_page_for_images(self, url):
        """
        Finds the first significant image on a page and processes it.
        Returns a numpy vector of the image features.
        """
        if not self.model:
            return np.zeros(8) # Blind mode

        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')

            images = soup.find_all('img')
            for img in images:
                src = img.get('src')
                if src and src.startswith('http'):
                    # Found an image candidate
                    return self.process_image(src)

            # No images found
            return np.zeros(8)

        except Exception:
            return np.zeros(8)

    def process_image(self, image_url):
        try:
            response = requests.get(image_url, timeout=5, stream=True)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content)).convert('RGB')
                input_tensor = self.preprocess(img)
                input_batch = input_tensor.unsqueeze(0)

                with torch.no_grad():
                    output = self.model(input_batch)

                # Output is 1x1000. We want a dense 8-dim summary for our seed brain.
                # We can average chunks of the vector.
                output_np = output.numpy().flatten()

                # Simple dimensionality reduction: Average every 125 elements to get 8 values
                reduced = output_np.reshape(8, 125).mean(axis=1)

                # Normalize
                norm = np.linalg.norm(reduced)
                if norm > 0:
                    reduced = reduced / norm

                return reduced
        except Exception as e:
            # print(f"[Vision] Failed to process image: {e}")
            pass

        return np.zeros(8)

if __name__ == "__main__":
    vision = VisionSensor()
    # Test with a known image
    vec = vision.process_image("https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png")
    print("Visual Vector:", vec)
