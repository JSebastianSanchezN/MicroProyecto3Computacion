import os
import json
import base64
import io
import numpy as np
import cv2
import tensorflow as tf
import pydicom

def init():
    global model
    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'conv_MLP_84.h5')
    model = tf.keras.models.load_model(model_path, compile=False)
    print("Modelo cargado exitosamente.")

def preprocess_image(image_array):
    array = cv2.resize(image_array, (512, 512))
    if len(array.shape) > 2 and array.shape[2] == 3:
        array = cv2.cvtColor(array, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    array = clahe.apply(array)
    array = array / 255.0
    array = np.expand_dims(array, axis=-1)
    array = np.expand_dims(array, axis=0)
    return array

def run(raw_data):
    try:
        data = json.loads(raw_data)
        image_base64 = data['data']
        is_dicom = data.get('is_dicom', False)

        image_bytes = base64.b64decode(image_base64)

        if is_dicom:
            dcm = pydicom.dcmread(io.BytesIO(image_bytes))
            image_array = dcm.pixel_array
            img2 = image_array.astype(float)
            img2 = (np.maximum(img2, 0) / img2.max()) * 255.0
            img2 = np.uint8(img2)
            image_array = cv2.cvtColor(img2, cv2.COLOR_GRAY2RGB)
        else:
            image_np = np.frombuffer(image_bytes, np.uint8)
            image_array = cv2.imdecode(image_np, cv2.IMREAD_COLOR)

        processed_array = preprocess_image(image_array)
        prediction_raw = model.predict(processed_array)

        prediction_index = np.argmax(prediction_raw)
        probability = float(np.max(prediction_raw))

        labels = ["bacteriana", "normal", "viral"]
        label = labels[prediction_index]

        result = {"label": label, "probability": probability}
        
        return result

    except Exception as e:
        error = str(e)
        return {"error": error}