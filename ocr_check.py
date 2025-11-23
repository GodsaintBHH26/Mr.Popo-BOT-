import pytesseract
from PIL import Image
import imagehash
import io
import cv2
import numpy as np
from db_bot import add_points

def check_win_position(img_bytes, template_path, threshold=0.55):
    np_img = np.frombuffer(img_bytes, np.uint8)
    img_rgb = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template_gray=cv2.imread(template_path, 0)
    
    if template_gray is None:
        raise FileNotFoundError(f"Template Not found at {template_path}")
    
    result  = cv2.matchTemplate(img_gray, template_gray, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    
    if max_val >= threshold:
        top_left = max_loc
        h, w = template_gray.shape
        center_y = top_left[1] + h//2
        
        img_height = img_gray.shape[0]
        half_height = img_height//2
        
        if center_y < half_height:
            return "Win"
        else: 
            return "Lose"
    else:
        return "Not detected"

async def img_validation(attachments, channelName, userId):
    submitted_hashes = set()
    valid_count = 0
    text = None
    
    if channelName == "forfeit-screens":
        for idx, attachment in enumerate(attachments):
            try:
                img_bytes = attachment["bytes"]
                pil_img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                pil_img.thumbnail((720 , 1280))
            
                text=pytesseract.image_to_string(pil_img)
                if "opponent" and "forfeited" in text:
                    text+=" You get 15 points"
                    await add_points(user_id=userId, points_to_add=15)
                else:
                    text+=" You get 5 points"
                    await add_points(user_id=userId, points_to_add=5)
            except Exception as e:
                print(f'Error processing image {idx + 1}: {e}')
                continue
            
    elif channelName == "matches":
        for idx, attachment in enumerate(attachments):
            # This is where we check if the template exists in that picture
            try:
                img_bytes = attachment["bytes"]
                template_img = "templates/squadra_win_template.jpg"
                result = check_win_position(img_bytes, template_img)
                if result == "Win":
                    await add_points(user_id=userId, points_to_add=10)
                    text = f"Seems like you {result} the match, 10 points"
                elif result == "Lose":
                    await add_points(user_id=userId, points_to_add=5)
                    text = f"Seems like you {result} the match, 5 points"
                print(text)
                
            except Exception as e:
                print(f'Error processing match image {idx + 1}: {e}')
                text = f"Error: {e}"
                continue
            
    else:
        await add_points(user_id=userId, points_to_add=5) 
        
        
    return valid_count, text