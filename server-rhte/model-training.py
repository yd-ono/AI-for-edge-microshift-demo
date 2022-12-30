#!/usr/bin/env python3

import face_recognition
import pickle
import yaml
from yaml.loader import SafeLoader
import os

known_face_encodings = []
known_face_metadata = []

with open(os.environ.get('MODEL_TRAINING_YAML', 'model-training.yaml')) as f:
    data = yaml.load(f, Loader=SafeLoader)


for info in data['faces']:
    print("Train face of %s" % info['name'])
    known_face_metadata.append({
        "name": info['name'],
    })

    face_encoding = face_recognition.face_encodings(
        face_recognition.load_image_file(info['image']))[0]

    known_face_encodings.append(face_encoding)


filename = os.environ.get('MODEL_FILENAME', 'model.data')

with open(filename, "wb") as face_data_file:
    face_data = [known_face_encodings, known_face_metadata]
    pickle.dump(face_data, face_data_file)
    print("Known faces backed up to disk: %s" % filename)
