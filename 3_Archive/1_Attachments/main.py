
import cv2
import matplotlib.pyplot as plt
from utils import apply_sobel, apply_otsu, apply_morphological_operations, apply_laplacian, apply_canny, apply_2d_fft

# Load image in grayscale
img = cv2.imread('/workspace/dataset/positive/00001.jpg', 0)

# Apply each processing function
sobel_result = apply_sobel(img)
otsu_result = apply_otsu(img)
morphological_result = apply_morphological_operations(img)
laplacian_result = apply_laplacian(img)
canny_result = apply_canny(img)
fft_result = apply_2d_fft(img)

# Display original and results
plt.figure(figsize=(15, 10))
plt.subplot(2, 3, 1)
plt.imshow(img, cmap='gray')
plt.title("Original Image")
plt.axis("off")

plt.subplot(2, 3, 2)
plt.imshow(sobel_result, cmap='gray')
plt.title("Sobel Edge Detection")
plt.axis("off")

plt.subplot(2, 3, 3)
plt.imshow(otsu_result, cmap='gray')
plt.title("Otsu Thresholding")
plt.axis("off")

plt.subplot(2, 3, 4)
plt.imshow(morphological_result, cmap='gray')
plt.title("Morphological Operation")
plt.axis("off")

plt.subplot(2, 3, 5)
plt.imshow(laplacian_result, cmap='gray')
plt.title("Laplacian Edge Detection")
plt.axis("off")

plt.subplot(2, 3, 6)
plt.imshow(canny_result, cmap='gray')
plt.title("Canny Edge Detection")
plt.axis("off")

plt.tight_layout()
plt.show()
