import face_recognition as fr
import numpy as np
from base.models import Profile, Event, FaceEncoding
import os

def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_encoded_faces(event_id):

    event = Event.objects.get(id=event_id)

    precomputed_qs = FaceEncoding.objects.filter(event_id=event_id)
    encoded: dict[str, np.ndarray] = {}

    for rec in precomputed_qs.select_related("profile__user"):
        try:
            encoded[rec.profile.user.username] = np.array(rec.encoding, dtype=float)
        except Exception:
            pass

    guests_without = []
    guest_profiles = Profile.objects.filter(id__in=event.guests.values_list('profile', flat=True))
    for p in guest_profiles.select_related("user"):
        if p.user.username not in encoded:
            guests_without.append(p)

    for p in guests_without:
        encoding = None
        if p.photo and os.path.exists(p.photo.path):
            try:
                face = fr.load_image_file(p.photo.path)
                face_encodings = fr.face_encodings(face)
                if face_encodings:
                    encoding = face_encodings[0]
                    print(f"Față detectată pentru {p.user.username}")
                else:
                    print(f"Nicio față detectată în imaginea lui {p.user.username}")
            except Exception as e:
                print(f"Eroare la procesarea imaginii pentru {p.user.username}: {e}")

        if encoding is not None:
            encoded[p.user.username] = encoding
            try:
                FaceEncoding.objects.update_or_create(
                    profile=p,
                    event=event,
                    defaults={"encoding": encoding.tolist()}
                )
            except Exception as e:
                print(f"Eroare la salvarea encodării pentru {p.user.username}: {e}")

    return encoded

def classify_face(img, event_id):

    faces = get_encoded_faces(event_id)
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