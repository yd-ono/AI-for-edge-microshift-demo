from glob import glob
from os import path
from pickle import dump

from face_recognition import face_encodings, load_image_file


def scan_images_folder(images_folder='./face-images/'):
    print(f'Scanning images folder {images_folder}.')

    image_file_paths = glob(path.join(images_folder, "*.jpg"))
    image_names = [
        file_path.split('/')[-1].rstrip('.jpg')
        for file_path in image_file_paths
    ]
    print(f'Found image files: {image_file_paths}.')
    print(f'Image names: {image_names}.')
    return image_names, image_file_paths


def load_and_encode(image_file_paths):
    print('Encoding faces.')
    encodings = [
        encode_face(image_file_path)
        for image_file_path in image_file_paths
    ]
    return encodings


def encode_face(image_file_path):
    face_image = load_image_file(image_file_path)
    encoding = face_encodings(face_image, num_jitters=100, model='large')[0]
    return encoding


def package(encodings, image_names):
    print('Packaging face encodings and metadata.')
    model_package = (encodings, image_names)
    return model_package


def dump_model_package(model_package, output_file_path='model.data'):
    print('Serializing model package.')
    with open(output_file_path, 'wb') as outputfile:
        dump(model_package, outputfile)
        print(f'Dumped model package to {output_file_path}.')


if __name__ == '__main__':
    image_names, image_file_paths = scan_images_folder()
    encodings = load_and_encode(image_file_paths)
    model_package = package(encodings, image_names)
    dump_model_package(model_package)
    print('Done.')
