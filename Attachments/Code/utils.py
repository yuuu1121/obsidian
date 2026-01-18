
import cv2
import numpy as np

def apply_sobel(img):
    # Apply GaussianBlur for noise reduction
    blurred_img = cv2.GaussianBlur(img, (5, 5), 0)
    # Sobel filter in x and y direction
    sobelx = cv2.Sobel(blurred_img, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(blurred_img, cv2.CV_64F, 0, 1, ksize=3)
    # Absolute value and combination
    sobelx_abs = cv2.convertScaleAbs(sobelx)
    sobely_abs = cv2.convertScaleAbs(sobely)
    combined_sobel = cv2.addWeighted(sobelx_abs, 0.5, sobely_abs, 0.5, 0)
    return combined_sobel

def apply_otsu(img):
    _, binary_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary_img

def apply_morphological_operations(img):
    blurred_img = cv2.GaussianBlur(img, (5, 5), 0)
    adaptive_thresh = cv2.adaptiveThreshold(
        blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )
    kernel = np.ones((3, 3), np.uint8)
    closing = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
    return closing

def apply_laplacian(img):
    blurred_img = cv2.GaussianBlur(img, (5, 5), 0)
    laplacian = cv2.Laplacian(blurred_img, cv2.CV_64F)
    laplacian_abs = cv2.convertScaleAbs(laplacian)
    return laplacian_abs

def apply_canny(img, low_threshold=50, high_threshold=150):
    blurred_img = cv2.GaussianBlur(img, (5, 5), 0)
    edges = cv2.Canny(blurred_img, low_threshold, high_threshold)
    return edges

def apply_2d_fft(img):
    f_transform = np.fft.fft2(img)
    f_transform_shifted = np.fft.fftshift(f_transform)
    # Remove low-frequency components
    center_x, center_y = f_transform_shifted.shape[0] // 2, f_transform_shifted.shape[1] // 2
    f_transform_shifted[center_x-5:center_x+5, center_y-5:center_y+5] = 0
    # Inverse FFT to reconstruct image
    f_transform_inverse_shifted = np.fft.ifftshift(f_transform_shifted)
    img_reconstructed = np.fft.ifft2(f_transform_inverse_shifted)
    return np.abs(img_reconstructed)
