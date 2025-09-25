import base64
import json
import os
import glob

def image_to_base64(path):
    if not os.path.exists(path):
        print(f"Error: La imagen no se encuentra en la ruta especificada: {path}")
        return None
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def main():
    # Definir el directorio de búsqueda y los patrones de archivo
    search_dir = r"C:\Users\sanjo\Desktop\Espe\Computacion\MicroProyecto3\data"
    patterns = ["**/*.jpg", "**/*.jpeg", "**/*.dcm"]
    
    image_files = []
    for pattern in patterns:
        image_files.extend(glob.glob(os.path.join(search_dir, pattern), recursive=True))

    if not image_files:
        print(f"No se encontraron imágenes en el directorio: {search_dir}")
        return

    print("Por favor, selecciona el número de la imagen que deseas usar para generar el JSON:")
    for i, file_path in enumerate(image_files):
        print(f"{i + 1}: {os.path.relpath(file_path, search_dir)}")

    try:
        choice = int(input("Introduce el número de tu elección: ")) - 1
        if 0 <= choice < len(image_files):
            selected_path = image_files[choice]
            print(f"\nHas seleccionado: {selected_path}\n")
        else:
            print("Selección inválida.")
            return
    except ValueError:
        print("Entrada inválida. Por favor, introduce un número.")
        return

    # Convertir la imagen seleccionada a base64
    base64_image_string = image_to_base64(selected_path)

    if base64_image_string:
        # Determinar si el archivo es DICOM por su extensión
        is_dicom = selected_path.lower().endswith('.dcm')
        
        # Crear el payload JSON
        payload = {
          "data": base64_image_string,
          "is_dicom": is_dicom
        }
        
        # Imprimir el JSON resultante
        print("--- JSON Generado ---")
        print(json.dumps(payload, indent=2))
        print("---------------------")
    else:
        print("No se pudo generar el JSON debido a un error al leer la imagen.")

if __name__ == "__main__":
    main()