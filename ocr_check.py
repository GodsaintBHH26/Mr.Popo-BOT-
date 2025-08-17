import pytesseract
from PIL import Image
import imagehash
import io

def img_validation(attachments):
    submitted_hashes = set()
    valid_count = 0
    
    for idx, attachment in enumerate(attachments):
        try:
            img_bytes = attachment["bytes"]
            img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
            
            img.thumbnail((720, 1280))
            
            text=pytesseract.image_to_string(img)
            
        except Exception as e:
            print(f'Error processing image {idx + 1}: {e}')
            continue
        
    return valid_count, text