
from flask import Flask, request, jsonify, send_from_directory
import requests
import json

app = Flask(__name__)

# --- Configuración del Endpoint de Azure ---
AZURE_URL = 'URL_AZURE'
AZURE_API_KEY = 'CLAVE_PRIMARIA_AZURE'
# ----------------------------------------

@app.route('/')
def index():
    """Sirve el archivo index.html"""
    return send_from_directory('.', 'index.html')

@app.route('/score', methods=['POST'])
def proxy_score():
    """Recibe la petición del navegador, la reenvía a Azure y devuelve la respuesta."""
    if not AZURE_API_KEY:
        return jsonify({"error": "La clave de API de Azure no está configurada en el servidor proxy."}), 500

    # 1. Recibir los datos de la imagen desde el navegador
    browser_data = request.get_json()
    if not browser_data:
        return jsonify({"error": "No se recibieron datos en la petición."}), 400

    # 2. Preparar la petición para Azure
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + AZURE_API_KEY
    }

    # 3. Enviar la petición a Azure
    try:
        response = requests.post(AZURE_URL, data=json.dumps(browser_data), headers=headers)
        response.raise_for_status()  # Lanza un error para respuestas 4xx/5xx

        # 4. Devolver la respuesta de Azure al navegador
        return jsonify(response.json())

    except requests.exceptions.HTTPError as error:
        print(f"Error en la petición a Azure: {error}")
        print(f"Respuesta de Azure: {error.response.text}")
        return jsonify({
            "error": f"Error del servidor de Azure: {error.response.status_code}",
            "details": error.response.text
        }), error.response.status_code
    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")
        return jsonify({"error": "Ha ocurrido un error inesperado en el servidor proxy."}), 500

if __name__ == '__main__':
    print("Iniciando servidor proxy...")
    print("Abre tu navegador y ve a http://127.0.0.1:5000")
    app.run(port=5000, debug=True)
