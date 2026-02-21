import sys
import os
import cv2
import traceback
from datetime import datetime
from core.pipeline import MangaCleanerPipeline
from core.exceptions import MangaCleanerError
from core.logger import logger

def main():
    """
    Main entry point for Desktop Application.
    Designed to be robust and fail-safe.
    """
    if len(sys.argv) < 2:
        print("Usage: python launcher.py <image_path> [output_path]")
        return

    image_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else f"cleaned_{os.path.basename(image_path)}"
    
    pipeline = MangaCleanerPipeline()
    job_id = f"desktop_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        print(f"[*] Initializing MangaCleaner V2 [Job: {job_id}]")
        print(f"[*] Processing: {image_path}")
        
        if not os.path.exists(image_path):
            print(f"[!] Error: File not found: {image_path}")
            return

        # Read image
        image = cv2.imread(image_path)
        if image is None:
            print(f"[!] Error: Could not read image: {image_path}")
            return

        # Execute Pipeline
        cleaned_image = pipeline.clean_image(image, job_id=job_id)
        
        # Save result
        cv2.imwrite(output_path, cleaned_image)
        print(f"[+] Success! Cleaned image saved to: {output_path}")

    except MangaCleanerError as e:
        # Managed error: Display friendly message
        print(f"\n[!] A processing error occurred:")
        print(f"    Code: {e.error_code}")
        print(f"    Message: {e.message}")
        print(f"\nDetails have been logged to app.log")
        logger.error(f"Desktop managed error: {e.message}")

    except Exception as e:
        # Unmanaged error: Capture and log but don't show stack trace to user
        print(f"\n[CRITICAL] An unexpected error occurred.")
        print(f"Please check the log file (error.log) for details.")
        
        # Log full traceback
        logger.critical(f"Desktop unhandled exception: {str(e)}\n{traceback.format_exc()}")
        
    finally:
        # Ensure any specific cleanup if needed
        pass

if __name__ == "__main__":
    main()
