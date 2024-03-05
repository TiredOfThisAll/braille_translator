import zipfile
from io import BytesIO
import os
from PIL import Image

file_extensions = [".png", ".jpg", ".jpeg", ".zip"]


def unpack_files(file, filename):
    head, tail = os.path.splitext(filename)
    if tail not in file_extensions:
        return "Wrong file format"
    if tail == ".zip":
        res_images = []
        with zipfile.ZipFile(file, 'r') as archive:
            for file in archive.filelist:
                with archive.open(file) as f:
                    res_images.append((Image.open(BytesIO(f.read())), f.name))
        return res_images
    return [(Image.open(file), filename)]


def pack_files(data, filename):
    memory_zip = BytesIO()

    with zipfile.ZipFile(memory_zip, 'w') as zipf:
        for elem in data:
            filename, ext = os.path.splitext(elem["name"])
            if "image" in elem.keys():
                ext = ext if ext.lower() == ".png" else ".JPEG"
                image_bytes = BytesIO()
                elem["image"].save(image_bytes, ext[1:])
                zipf.writestr(filename + ext.lower(), image_bytes.getvalue())
            if "translated_text" in elem.keys():
                zipf.writestr(filename + "_braille" + ".txt", elem["translated_text"])
            if "braille_text" in elem.keys():
                zipf.writestr(filename + "_translation" + ".txt", elem["braille_text"])
                
    memory_zip.seek(0)

    return memory_zip.getvalue()
