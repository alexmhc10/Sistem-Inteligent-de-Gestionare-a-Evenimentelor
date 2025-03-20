import face_recognition as fr
import numpy as np
from .models import Profile, RSVP
from PIL import Image
import cv2
import os



def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'



def get_encoded_faces():
    profiles = Profile.objects.all()
    encoded = {}

    for p in profiles:
        try:
            print(f"📂 Procesăm imaginea: {p.photo.path}")

            pil_img = Image.open(p.photo).convert("RGB") 
            print(f"📸 PIL Image Mode: {pil_img.mode}, Format: {pil_img.format}")

            img_np = np.array(pil_img, dtype=np.uint8)
            print(f"🧐 Imagine convertită pentru face_recognition: {img_np.shape}, Tip: {img_np.dtype}")

            if img_np.shape[-1] != 3:
                raise ValueError("Imaginea nu are exact 3 canale de culoare!")

            face_encodings = fr.face_encodings(img_np)

            if len(face_encodings) > 0:
                encoded[p.user.username] = face_encodings[0]
                print(f"✅ Encoding obținut pentru {p.user.username}")
            else:
                print("❌ Nicio față detectată în imagine")

        except Exception as e:
            print(f"❌ Eroare la procesare: {e}")

    return encoded


def classify_face(img):
    """
    This function takes an image as input and returns the name of the face it contains
    """
    faces = get_encoded_faces()
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())

    img = fr.load_image_file(img)
 
    try:
        face_locations = fr.face_locations(img)

        unknown_face_encodings = fr.face_encodings(img, face_locations)

        face_names = []
        for face_encoding in unknown_face_encodings:
            matches = fr.compare_faces(faces_encoded, face_encoding)

            face_distances = fr.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            else:
                name = "Unknown"

            face_names.append(name)

        return face_names[0]
    except:
        return False    