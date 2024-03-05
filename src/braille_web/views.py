from django.http import HttpResponse, HttpResponseNotFound
from threading import Thread
from io import BytesIO
from uuid import uuid4
from time import time, sleep
import os

from braille.object_detection.RetinaNet.infer import infer_retina_web
from braille_web.utils import pack_files, unpack_files

from django.template import loader

status = {}
data = {}


def delete_expired_files():
    while True:
        keys_to_delete = []
        keys_to_delete = [key for key in data.keys() if time() - data[key]["creation_time"] > 600]
        for key in keys_to_delete:
            del data[key]
        sleep(60)


check_expired_files_thread = Thread(target=delete_expired_files).start()


def main_page(request):
    template = loader.get_template("braille_web/main.html")
    return HttpResponse(template.render(request=request))


def upload_file(request):
    if request.method == "POST":
        recognition_options = {
            "language": request.POST["language"],
            "image_required": request.POST["image_checkbox"],
            "translation_required": request.POST["translation_checkbox"],
            "braille_required": request.POST["braille_checkbox"]
        }
        upload_id = str(uuid4())
        status[upload_id] = 0
        file = BytesIO(request.FILES["filename"].read())
        file_name = request.FILES["filename"].name
        thread = Thread(target=work, args=(upload_id, file, file_name, recognition_options))
        thread.start()
        return HttpResponse(upload_id)


def work(upload_id, file, filename, recognition_options):
    file = unpack_files(file, filename)
    results = infer_retina_web(file, filename, status, upload_id, recognition_options)
    file = pack_files(results, filename)

    data[upload_id] = {"file": file, "filename": filename, "creation_time": time()}


def upload_file_status(request):
    upload_id = request.GET.get('upload_id')
    return HttpResponse(status[upload_id])


def download_file(request):
    upload_id = request.GET.get('upload_id')
    if upload_id not in data:
        return HttpResponseNotFound("This link is probably expired or not existed")
    filename, ext = os.path.splitext(data[upload_id]["filename"])
    response = HttpResponse(data[upload_id]["file"], content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{filename + ".zip"}"'
    return response
