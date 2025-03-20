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

            # Încărcăm imaginea cu PIL
            pil_img = Image.open(p.photo.path).convert("RGB")  # Asigură-te că este RGB
            print(f"📸 PIL Image Mode: {pil_img.mode}, Format: {pil_img.format}")

            # Convertim la numpy array manual
            img_np = np.array(pil_img, dtype=np.uint8)
            print(f"🧐 Imagine convertită pentru face_recognition: {img_np.shape}, Tip: {img_np.dtype}")

            # Verificare dacă imaginea este corectă (RGB)
            if img_np.shape[-1] != 3:
                raise ValueError("Imaginea nu are exact 3 canale de culoare!")

            # Încercăm să obținem encodingul
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
    # Load all the known faces and their encodings
    faces = get_encoded_faces()
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())

    # Load the input image
    img = fr.load_image_file(img)
 
    try:
        # Find the locations of all faces in the input image
        face_locations = fr.face_locations(img)

        # Encode the faces in the input image
        unknown_face_encodings = fr.face_encodings(img, face_locations)

        # Identify the faces in the input image
        face_names = []
        for face_encoding in unknown_face_encodings:
            # Compare the encoding of the current face to the encodings of all known faces
            matches = fr.compare_faces(faces_encoded, face_encoding)

            # Find the known face with the closest encoding to the current face
            face_distances = fr.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)

            # If the closest known face is a match for the current face, label the face with the known name
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            else:
                name = "Unknown"

            face_names.append(name)

        # Return the name of the first face in the input image
        return face_names[0]
    except:
        # If no faces are found in the input image or an error occurs, return False
        return False