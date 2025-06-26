import face_recognition as fr
import numpy as np
from base.models import Profile, Event, FaceEncoding
import os

def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'


def get_encoded_faces(event_id):
    """
    Returnează un dicționar {username: encoding_numpy_array} pentru toți invitații unui eveniment.
    1. Încearcă să încarce encodările precompute din modelul FaceEncoding.
    2. Dacă lipsesc encodări, se calculează on-the-fly și se persistă pentru utilizări viitoare.
    """
    event = Event.objects.get(id=event_id)

    # 1. Încarcă encodările existente
    precomputed_qs = FaceEncoding.objects.filter(event_id=event_id)
    encoded: dict[str, np.ndarray] = {}

    for rec in precomputed_qs.select_related("profile__user"):
        try:
            encoded[rec.profile.user.username] = np.array(rec.encoding, dtype=float)
        except Exception:
            # Dacă apare o eroare de conversie, ignorăm și recalc.
            pass

    # 2. Identifică invitații fără encodări
    guests_without = []
    guest_profiles = Profile.objects.filter(id__in=event.guests.values_list('profile', flat=True))
    for p in guest_profiles.select_related("user"):
        if p.user.username not in encoded:
            guests_without.append(p)

    # 3. Calculează encodările lipsă
    for p in guests_without:
        encoding = None
        if p.photo and os.path.exists(p.photo.path):
            try:
                face = fr.load_image_file(p.photo.path)
                face_encodings = fr.face_encodings(face)
                if face_encodings:
                    encoding = face_encodings[0]
                    print(f"✅ Față detectată pentru {p.user.username}")
                else:
                    print(f"⚠️ Nicio față detectată în imaginea lui {p.user.username}")
            except Exception as e:
                print(f"❌ Eroare la procesarea imaginii pentru {p.user.username}: {e}")

        if encoding is not None:
            encoded[p.user.username] = encoding
            # Persistă în FaceEncoding pentru utilizări viitoare
            try:
                FaceEncoding.objects.update_or_create(
                    profile=p,
                    event=event,
                    defaults={"encoding": encoding.tolist()}
                )
            except Exception as e:
                print(f"❌ Eroare la salvarea encodării pentru {p.user.username}: {e}")

    return encoded

def classify_face(img, event_id):

    faces = get_encoded_faces(event_id)
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())

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