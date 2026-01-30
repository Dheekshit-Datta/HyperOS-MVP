"""
Element detector - finds UI elements using OCR
"""
import pytesseract
from PIL import Image
import re

def detect_elements(screenshot):
    """
    Detect UI elements on screen using OCR
    Returns list of detected text and coordinates
    """
    
    try:
        # Run OCR on screenshot
        ocr_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
        
        elements = []
        n_boxes = len(ocr_data['text'])
        
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            
            if text:  # If text found
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                w = ocr_data['width'][i]
                h = ocr_data['height'][i]
                conf = ocr_data['conf'][i]
                
                elements.append({
                    "text": text,
                    "x": x + w//2,  # Center coordinates
                    "y": y + h//2,
                    "confidence": conf
                })
        
        return elements
    except Exception as e:
        print(f"⚠️ OCR detection failed: {e}")
        print("   Note: Make sure Tesseract OCR is installed")
        print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Mac: brew install tesseract")
        print("   Linux: sudo apt-get install tesseract-ocr")
        return []
