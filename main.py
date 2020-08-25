import os
import sys
import base64
import math
from datetime import datetime

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_cors import CORS
from flask import session

import random
import string
import asyncio

import cloudmersive_ocr_api_client
from cloudmersive_ocr_api_client.rest import ApiException

# settigns
import settings
from werkzeug.utils import secure_filename
from flask.json import jsonify

api_instance = cloudmersive_ocr_api_client.ImageOcrApi()
image_file = "test.png"

api_instance.api_client.configuration.api_key = {}
api_instance.api_client.configuration.api_key["Apikey"] = os.environ.get("API_KEY_OCR")
print("{}" .format(api_instance.api_client.configuration.api_key["Apikey"]))



app = Flask(__name__)
app.secret_key = os.urandom(42)
CORS(app)
# limite 16 megas
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG"]

CARPETA_SUBIDAS = os.path.abspath("static/images/archivos_subidos")
print("capr:" + CARPETA_SUBIDAS)
app.config["CARPETA_SUBIDAS"] = CARPETA_SUBIDAS

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/t", methods=["post"])
def test():
    return jsonify({"resultado": "True"})

@app.route("/api/", methods=["POST"])
def home_post():
    print("1")
    if "user_image" in request.files:
        try:
            print("2")
            # Converts an uploaded image in common formats such as JPEG, PNG into text via Optical Character Recognition.
            # datafile_b64 = request.form["image"]
            tamanoarchivo_bytes = sys.getsizeof(request.files["user_image"])
            print("3")
            if tamanoarchivo_bytes > app.config["MAX_CONTENT_LENGTH"] or tamanoarchivo_bytes <= 0:
                return redirect("home")
            print("4")
            f = request.files["user_image"]
            print("5")
            nombrefile = get_random_string(12) + "-" + datetime.utcnow().strftime("%d-%b-%Y-%H.%M.%S.%f_") + "." + f.content_type.split("/")[1]
            print("6")
            print(os.path.join(app.config["CARPETA_SUBIDAS"], nombrefile))
            with open(os.path.join(app.config["CARPETA_SUBIDAS"], nombrefile), "wb") as arch:
                # cad_cero = datafile_b64.find(',')
                # imagen_data64 = datafile_b64[cad_cero + 1:]
                # arch.write(base64.decodebytes(imagen_data64.encode()))
                print("7")
                arch.write(f.read())
                arch.close()

            # imagen_archivo = f.read().decode('UTF-8')
            # imagen_archivo = base64.b64encode(imagen_archivo)
            print("8")
            file_absolute_path = os.path.join(app.config['CARPETA_SUBIDAS'], nombrefile)
            # uploaded_file = open(file_absolute_path, 'rb',encoding=str)
            api_response = api_instance.image_ocr_post(file_absolute_path)
            print(api_response.text_result)
            print("9")
            if (api_response.text_result != ""):
                print("10.A")
                return {"resultado": api_response.text_result}
            else:
                print("10.B")
                return {"resultado": "Sin Texto"}

        except ApiException as e:
            print("Exception when calling ImageOcrApi->image_ocr_post: %s\n" % e)

    return redirect(url_for("home"))



def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


if __name__ == "__main__":
    settings.readconfig()
    env_host = os.environ.get("HOST", "0.0.0.0")
    env_port = int(os.environ.get("PORT", 5000))
    env_debug = os.environ.get("FLASK_DEBUG", True)
    app.run(host=env_host, port=env_port, debug=env_debug)
