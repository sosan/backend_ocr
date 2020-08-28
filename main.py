# PROGRAMA DONDE HACEMOS OCR DE UNA IMAGEN
# DEVOLVEMOS EL TEXTO EN JSON

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

# ocr con cloudmersive
api_instance = cloudmersive_ocr_api_client.ImageOcrApi()

api_instance.api_client.configuration.api_key = {}
api_instance.api_client.configuration.api_key["Apikey"] = os.environ.get("API_KEY_OCR")


# configuracion de la app
app = Flask(__name__)
app.secret_key = os.urandom(42)
CORS(app)

# limite 16 megas del fichero
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG"]

CARPETA_SUBIDAS = os.path.abspath("static/images/archivos_subidos")
# print("capr:" + CARPETA_SUBIDAS)
app.config["CARPETA_SUBIDAS"] = CARPETA_SUBIDAS

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/api", methods=["POST"])
def home_post():
    print("fff")
    # nos enviar una imagen sin formato base64
    if "user_image" in request.files:
        try:
            tamanoarchivo_bytes = sys.getsizeof(request.files["user_image"])
            if tamanoarchivo_bytes > app.config["MAX_CONTENT_LENGTH"] or tamanoarchivo_bytes <= 0:
                return redirect("home")
            f = request.files["user_image"]

            nombrefile = get_random_string(12) + "-" + datetime.utcnow().strftime("%d-%b-%Y-%H.%M.%S.%f_") + "." + f.content_type.split("/")[1]

            with open(os.path.join(app.config["CARPETA_SUBIDAS"], nombrefile), "wb") as arch:
                arch.write(f.read())
                arch.close()

            file_absolute_path = os.path.join(app.config['CARPETA_SUBIDAS'], nombrefile)
            api_response = api_instance.image_ocr_post(file_absolute_path)
            # print(api_response.text_result)
            if (api_response.text_result != ""):
                return {"resultado": api_response.text_result}
            else:
                return {"resultado": "Sin Texto"}

        except ApiException as e:
            # TODO: colocar el error en la db
            print("Exception when calling ImageOcrApi->image_ocr_post: %s\n" % e)
            return jsonify({"resultado": "Error"})
    else:
        # imagen en formato base64
        if "user_image" in request.form:
            # 9j/4AAQSkZJRgABAQAAAQABAAD/2wBDABALDA4MChAODQ4SERATGCgaGBYWGDEjJR0oOjM9PDkz
            tamanoarchivo = sys.getsizeof(request.form["user_image"])
            if tamanoarchivo > app.config["MAX_CONTENT_LENGTH"] or tamanoarchivo <= 0:
                return jsonify({"resultado": "Error"})
            file_base64 = request.form["user_image"]
            api_response = api_instance.image_ocr_post(file_base64)
            
            if (api_response.text_result != ""):
                return {"resultado": api_response.text_result}
            else:
                return {"resultado": "Sin Texto"}

            
        else:
            return jsonify({"resultado": "Error"})
        
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
