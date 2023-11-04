from more_itertools import chunked
from dotenv import load_dotenv
import os
import pandas as pd
import requests
import json
from flask import Flask, jsonify
from db import database_insertion
from endpoints import endpoint_currency, endpoint_users, endpoint_category, get_access_token
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Carga el archivo .env
load_dotenv()

# Configuración del archivo .env
file = os.getenv('FILE')
separator = os.getenv('SEPARATOR')
encoding = os.getenv('ENCODING')
ENDPOINTMELI = os.getenv('ENDPOINTMELI')


# Estructuras para almacenar los datos
item_data = []
category_data = {}
currency_data = {}
user_data = {}

# Función para procesar un elemento
def process_item(item):
    try:
        # Divide el elemento en 'site' e 'id'
        site, id = item[:3], item[3:]
        
        # Obtén el token de acceso
        access_token = get_access_token()

        # Consulta la API de productos
        item_info = get_item_info(site, id, access_token)

        # Si la solicitud a la API de productos fue exitosa y el elemento existe
        if item_info:
            # Consulta la categoría
            category_name = endpoint_category(item_info, category_data)

            # Consulta la descripción de la moneda
            currency_description = endpoint_currency(item_info, currency_data)

            # Consulta el nombre del vendedor
            seller_nickname = endpoint_users(item_info, user_data)
            price = item_info.get('price', '')
            start_time = item_info.get('start_time', '')
            # Agrega los datos a la lista de elementos
            item_data.append({
                'site': site,
                'id': id,
                'price': price,
                'start_time': start_time,
                'name': category_name,
                'description': currency_description,
                'nickname': seller_nickname
            })
    except requests.exceptions.RequestException as e:
        print(f'Error en la solicitud de elementos: {str(e)}')
    except Exception as e:
        print(f'Error inesperado: {str(e)}')


# Función para procesar lotes de elementos en hilos
def process_batch(df):
    items = df['clave']
    total_items = len(items)
    batch_size = 100

    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        for batch in chunked(items, batch_size):
            executor.map(process_item, batch)
            print(f'Procesados {len(batch)} de {total_items} elementos.')


# Endpoint para procesar el archivo
@app.route('/process_file', methods=['GET'])
def process_file():
    try:
        # Lectura del archivo
        df = pd.read_csv(file, sep=separator, encoding=encoding)

        # Crear la clave del elemento
        df['clave'] = df['site'] + df['id'].astype(str)

        # Procesar el archivo en lotes
        process_batch(df)
        if item_data:
            # Inserta los datos en la base de datos
            print('database_insertion.',item_data)
            database_insertion(item_data)
            response = jsonify({"message": "Proceso completado"})
            return response
        response = jsonify({"message": "Proceso no completado"})
        return response

    except Exception as e:
        print(f'Error inesperado en process_file: {str(e)}')
        return jsonify({"error": "Ocurrió un error al procesar el archivo"}), 500


# Función para consultar la API de productos
def get_item_info(site, id, access_token):
    try:
        item_url = f'{ENDPOINTMELI}/items/{site}{id}'
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        item_response = requests.get(item_url, headers=headers)
        item_response.raise_for_status()
        return json.loads(item_response.text)
    except requests.exceptions.RequestException as e:
        print(f'Error en la solicitud a la API de productos: {str(e)}')
        return {}  # Devuelve un diccionario vacío en caso de error


if __name__ == '__main__':
    app.run(debug=True)
