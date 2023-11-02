from dotenv import load_dotenv
import os
import pandas as pd
import requests
import json
from flask import Flask, jsonify

app = Flask(__name__)

# Carga el archivo .env
load_dotenv()

# Configuración del archivo .env
file = os.getenv('FILE')
separator = os.getenv('SEPARATOR')
encoding = os.getenv('ENCODING')

@app.route('/procesar_archivo', methods=['GET'])

def procesar_archivo():

    try:
        # Lectura del archivo
        df = pd.read_csv(file, sep=separator, encoding=encoding)

        # Crear la clave del ítem
        df['clave'] = df['site'] + df['id'].astype(str)

        # Consulta a las APIs desde el archivo .env
        ENDPOINTMELI = os.getenv('ENDPOINTMELI')
        CLIENTSECRET = os.getenv('CLIENTSECRET')
        APPID = os.getenv('APPID')

        # Obtener el ACCESS_TOKEN
        access_token_url = f'{ENDPOINTMELI}/oauth/token'
        access_token_payload = {
            'grant_type': 'client_credentials',
            'client_id': APPID,
            'client_secret': CLIENTSECRET
        }

        access_token_response = requests.post(access_token_url, data=access_token_payload)
        access_token_data = access_token_response.json()
        access_token = access_token_data.get('access_token', '')

        # Estructuras para almacenar los datos
        item_data = []
        category_data = {}
        currency_data = {}
        user_data = {}
    except requests.exceptions.HTTPError as err:
        if access_token_response.status_code == 500:
            print('Error: ', access_token_response.status_code)
        else:
            print('Otro error HTTP: ', err)
    except Exception as e:
        print('Algo salió mal: ', e)    


    for clave in df['clave']:
        try:
            site, id = clave[:3], clave[3:]
            # Consulta la API de categorias
            item_url = f'{ENDPOINTMELI}/sites/{site}/search?category={id}'
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            item_response = requests.get(item_url)
            item_info = json.loads(item_response.text)
            
            if 'price' in item_info and 'start_time' in item_info:
                price = item_info['price']
                start_time = item_info['start_time']
            else:
                price = None
                start_time = None
            # Consulta la API de categorías
            if 'category_id' in item_info:
                category_id = item_info['category_id']
                if category_id not in category_data:
                    category_url = ENDPOINTMELI + '/categories/' + category_id
                    category_response = requests.get(category_url)
                    category_info = json.loads(category_response.text)
                    category_data[category_id] = category_info.get('name', None)
                category_name = category_data[category_id]
            else:
                category_name = None

            # Consulta la API de monedas (currencies)
            if 'currency_id' in item_info:
                currency_id = item_info['currency_id']
                if currency_id not in currency_data:
                    currency_url = ENDPOINTMELI + '/currencies/' + currency_id
                    currency_response = requests.get(currency_url)
                    currency_info = json.loads(currency_response.text)
                    currency_data[currency_id] = currency_info.get('description', None)
                currency_description = currency_data[currency_id]
            else:
                currency_description = None

            # Consulta la API de usuarios (sellers)
            if 'seller_id' in item_info:
                seller_id = item_info['seller_id']
                if seller_id not in user_data:
                    user_url = ENDPOINTMELI + '/users/' + seller_id
                    user_response = requests.get(user_url)
                    user_info = json.loads(user_response.text)
                    user_data[seller_id] = user_info.get('nickname', None)
                seller_nickname = user_data[seller_id]
            else:
                seller_nickname = None

            # Almacena los datos obtenidos en una estructura
            item_data.append({
                'site': site,
                'id': id,
                'price': price,
                'start_time': start_time,
                'name': category_name,
                'description': currency_description,
                'nickname': seller_nickname
            })
            # return jsonify(item_data)
        except requests.exceptions.HTTPError as err:
            if item_response.status_code == 500:
                print('Error: ', item_response.status_code)
            else:
                print('Otro error HTTP: ', err)
        except Exception as e:
            print('Algo salió mal: ', e)
    

if __name__ == '__main__':
    app.run(debug=True)