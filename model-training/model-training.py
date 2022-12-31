#!/usr/bin/env python3

import face_recognition
import pickle
import yaml
from yaml.loader import SafeLoader
import os

known_face_encodings = []
known_face_metadata = []

metadata_file = os.environ.get('MODEL_TRAINING_YAML', 'metadata.yaml')
iamge_basedir = os.path.dirname(metadata_file)

with open(metadata_file) as f:
    data = yaml.load(f, Loader=SafeLoader)


for info in data['faces']:
    image = "%s/%s" % ( iamge_basedir, info['image'])
    print("Train face of %s => %s" % (info['name'],image))
    known_face_metadata.append( info['name'] )


    face_encoding = face_recognition.face_encodings(
        face_recognition.load_image_file(image))[0]

    known_face_encodings.append(face_encoding)


filename = os.environ.get('MODEL_FILENAME', 'model.data')

with open(filename, "wb") as face_data_file:
    face_data = [known_face_encodings, known_face_metadata]
    pickle.dump(face_data, face_data_file)
    print("Known faces backed up to disk: %s" % filename)
