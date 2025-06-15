import face_recognition as fr
import numpy as np
from base.models import Profile, Event
import os

def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_encoded_faces(event_id):
    """
    This function loads all user profile images and encodes their faces.
    It handles missing files and skips images where no face is detected.
    """
    event = Event.objects.get(id=event_id)
    guests = event.guests.all()
    qs = Profile.objects.filter(id__in=guests.values_list('profile', flat=True))
    encoded = {}

    for p in qs:
        encoding = None

        # Verificăm dacă există imaginea și dacă fișierul există fizic pe disc
        if p.photo and os.path.exists(p.photo.path):
            try:
                face = fr.load_image_file(p.photo.path)
                face_encodings = fr.face_encodings(face)

                if face_encodings:
                    encoding = face_encodings[0]
                    print(f"✅ Față detectată pentru {p.user.username}")
                else:
                    print(f"⚠️ Nicio față detectată în imaginea lui {p.user.username}")

                if encoding is not None:
                    encoded[p.user.username] = encoding
            except Exception as e:
                print(f"❌ Eroare la procesarea imaginii pentru {p.user.username}: {e}")
        else:
            print(f"🛑 Imagine lipsă pentru {p.user.username} - {p.photo}")

    return encoded

def classify_face(img, event_id):
    """
    This function takes an image as input and returns the name of the face it contains
    """
    # Load all the known faces and their encodings
    faces = get_encoded_faces(event_id)
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