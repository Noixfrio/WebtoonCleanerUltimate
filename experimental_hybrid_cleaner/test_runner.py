import time
import sys
import os
import cv2
import numpy as np

# Adjust python path to allow importing the isolated module explicitly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from hybrid_cleaner import HybridCleaner

def main():
    print("--------------------------------------------------")
    print("Initializing Experimental Hybrid Cleaner Test Runner")
    print("--------------------------------------------------\n")
    
    input_path = "input.png"
    mask_path = "mask.png"
    output_path = "output_test.png"

    # Automatically generate dummy files if missing
    if not os.path.exists(input_path) or not os.path.exists(mask_path):
        print("[!] Missing input/mask files. Generating basic test suite...")
        
        # Generate dummy image with a noise block simulating a defect/texture
        dummy_img = np.ones((512, 512, 3), dtype=np.uint8) * 200
        noise = np.random.randint(0, 100, (100, 100, 3), dtype=np.uint8)
        dummy_img[200:300, 200:300] = noise
        cv2.imwrite(input_path, dummy_img)
        
        # Generate dummy mask for the defect
        dummy_mask = np.zeros((512, 512), dtype=np.uint8)
        dummy_mask[210:290, 210:290] = 255
        cv2.imwrite(mask_path, dummy_mask)
        print("[+] Created dummy 'input.png' and 'mask.png'\n")

    # Load images
    image = cv2.imread(input_path)
    if image is None:
        print(f"[Error] Could not read image at '{input_path}'")
        return
        
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
    if mask is None:
        print(f"[Error] Could not read mask at '{mask_path}'")
        return

    print("[+] Assets loaded successfully.")

    # Guard against completely empty test masks
    if not np.any(mask):
        print("[Warning] The provided mask is entirely empty. Immediate return expected.")

    # Calculate ROI used
    y_idx, x_idx = np.where(mask > 0)
    roi_size_str = "Full Image / Empty Mask"
    if len(y_idx) > 0 and len(x_idx) > 0:
        roi_h = y_idx.max() - y_idx.min()
        roi_w = x_idx.max() - x_idx.min()
        roi_size_str = f"{roi_w}px x {roi_h}px (width x height)"

    # Instantiate HybridCleaner with safe defaults
    cleaner = HybridCleaner(
        inpaint_radius=5,
        blur_kernel=51,
        texture_strength=1.1,
        feather_radius=5,
        padding=20
    )

    # Output parameter report
    print("\n[Execution Parameters]")
    print(f" - Inpaint Radius:   {cleaner.inpaint_radius}")
    print(f" - Blur Kernel:      {cleaner.freq_sep_plugin.blur_kernel}")
    print(f" - Texture Strength: {cleaner.freq_sep_plugin.texture_strength}")
    print(f" - Feather Radius:   {cleaner.freq_sep_plugin.feather_radius}")
    print(f" - Padding Bounds:   {cleaner.freq_sep_plugin.padding}")
    print(f" - Estimated ROI:    {roi_size_str}")

    print("\n[Executing Pipeline]")
    
    # Process & compute time
    start_time = time.time()
    try:
        result = cleaner.process(image, mask)
        execution_time = time.time() - start_time
        print(f"[+] Completed! Total processing time: {execution_time:.4f} seconds")
    except Exception as e:
        print(f"[Error] Pipeline failure: {e}")
        return

    # Save output
    if cv2.imwrite(output_path, result):
        print(f"[+] Output isolated result successfully saved to: {output_path}")
    else:
        print(f"[Error] Failed to write output to '{output_path}'")

    print("\n--------------------------------------------------")

if __name__ == "__main__":
    main()
