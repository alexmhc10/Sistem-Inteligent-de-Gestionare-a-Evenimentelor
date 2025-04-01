import face_recognition as fr
import numpy as np
from base.models import Profile
from PIL import Image, ImageFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import warnings


def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'



def validate_and_convert_image(img):
    """Universal image validation and conversion for all image sources"""
    # If img is already numpy array (from face_recognition)
    if isinstance(img, np.ndarray):
        if len(img.shape) == 2:  # Grayscale
            img = np.stack((img,)*3, axis=-1)
        elif img.shape[2] == 4:   # RGBA
            img = img[:, :, :3]
        return img
    
    # If img is file path or file-like object
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        pil_img = Image.open(img)
        
        if pil_img.mode == '1':  # 1-bit pixels
            pil_img = pil_img.convert('L')
        if pil_img.mode in ('L', 'P'):  # Grayscale or palette
            pil_img = pil_img.convert('RGB')
        elif pil_img.mode == 'RGBA':
            background = Image.new('RGB', pil_img.size, (255, 255, 255))
            background.paste(pil_img, mask=pil_img.split()[-1])
            pil_img = background
            
        return np.array(pil_img)

def get_encoded_faces():
    """Improved face encoding with robust image handling"""
    encoded = {}
    qs = Profile.objects.select_related('user').exclude(photo__exact='')
    
    for p in qs:
        try:
            # Validate and convert image
            img_array = validate_and_convert_image(p.photo.path)
            
            # Face detection with fallback models
            face_locations = fr.face_locations(img_array, model='hog')
            if not face_locations:
                face_locations = fr.face_locations(img_array, model='cnn')
                
            if face_locations:
                encoding = fr.face_encodings(
                    img_array, 
                    known_face_locations=face_locations,
                    num_jitters=2,
                    model='large'
                )[0]
                encoded[p.user.username] = encoding
                
        except Exception as e:
            print(f"Skipped {p.user.username}: {str(e)}")
            continue
            
    return encoded

def classify_face(img_source, tolerance=0.6):
    """
    Robust face classification with improved error handling
    :param img_source: Can be file path, file object, or numpy array
    :param tolerance: Lower = more strict matching (0.6 is default)
    :return: name or False
    """
    try:
        # Load and validate input image
        img_array = validate_and_convert_image(img_source)
        
        # Get encodings with fallback
        faces = get_encoded_faces()
        if not faces:
            return False
            
        # Detect faces with multiple attempts
        face_locations = fr.face_locations(img_array)
        if not face_locations:
            return False
            
        # Process each found face
        unknown_encodings = fr.face_encodings(img_array, face_locations)
        best_match = None
        best_distance = tolerance  # Start with threshold
        
        for encoding in unknown_encodings:
            distances = fr.face_distance(list(faces.values()), encoding)
            min_index = np.argmin(distances)
            min_distance = distances[min_index]
            
            if min_distance < best_distance:
                best_distance = min_distance
                best_match = list(faces.keys())[min_index]
        
        return best_match if best_match else False
        
    except Exception as e:
        print(f"Classification error: {e}")
        return False