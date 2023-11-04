import os
import requests
import json

# Configuración del archivo .env
ENDPOINTMELI = os.getenv('ENDPOINTMELI')
CLIENTSECRET = os.getenv('CLIENTSECRET')
APPID = os.getenv('APPID')

# Función para obtener el token de acceso
def get_access_token():
    try:
        access_token_url = f'{ENDPOINTMELI}/oauth/token'
        access_token_payload = {
            'grant_type': 'client_credentials',
            'client_id': APPID,
            'client_secret': CLIENTSECRET
        }
        access_token_response = requests.post(access_token_url, data=access_token_payload)
        access_token_response.raise_for_status()
        access_token_data = access_token_response.json()
        return access_token_data.get('access_token', '')
    except requests.exceptions.RequestException as e:
        print(f'Error en la solicitud del token de acceso: {str(e)}')


# Función para obtener la categoría de un elemento
def endpoint_category(item_info, category_data):
    # Obtiene el ID de la categoría del elemento
    category_id = item_info.get('category_id')
    
    # Si no hay ID de categoría, retorna None
    if not category_id:
        return None

    # Si ya se ha consultado esta categoría, retorna la información almacenada previamente
    if category_id in category_data:
        return category_data[category_id]

    try:
        # Construye la URL de la API de categorías
        category_url = f'{ENDPOINTMELI}/categories/{category_id}'
        
        # Realiza una solicitud GET a la API de categorías
        category_response = requests.get(category_url)
        category_response.raise_for_status()
        
        # Obtiene la información de la categoría
        category_info = json.loads(category_response.text)
        category_name = category_info.get('name')
        
        # Si se encuentra el nombre de la categoría, lo almacena en el diccionario para futuras referencias
        if category_name:
            category_data[category_id] = category_name
            return category_name
    except requests.exceptions.RequestException as e:
        print(f'Error en la solicitud a la API de categorías: {str(e)}')
    except Exception as e:
        print(f'Error inesperado al obtener la categoría: {str(e)}')

    return None

# Función para obtener la descripción de la moneda de un elemento
def endpoint_currency(item_info, currency_data):
    # Obtiene el ID de la moneda del elemento
    currency_id = item_info.get('currency_id')
    
    # Si no hay ID de moneda, retorna None
    if not currency_id:
        return None

    # Si ya se ha consultado esta moneda, retorna la descripción almacenada previamente
    if currency_id in currency_data:
        return currency_data[currency_id]

    try:
        # Construye la URL de la API de monedas
        currency_url = f'{ENDPOINTMELI}/currencies/{currency_id}'
        
        # Realiza una solicitud GET a la API de monedas
        currency_response = requests.get(currency_url)
        currency_response.raise_for_status()
        
        # Obtiene la información de la moneda
        currency_info = json.loads(currency_response.text)
        currency_description = currency_info.get('description')
        
        # Si se encuentra la descripción de la moneda, la almacena en el diccionario para futuras referencias
        if currency_description:
            currency_data[currency_id] = currency_description
            return currency_description
    except requests.exceptions.RequestException as e:
        print(f'Error en la solicitud a la API de monedas: {str(e)}')
    except Exception as e:
        print(f'Error inesperado al obtener la descripción de la moneda: {str(e)}')

    return None

# Función para obtener el nombre del vendedor de un elemento
def endpoint_users(item_info, user_data):
    # Obtiene el ID del vendedor del elemento
    seller_id = str(item_info.get('seller_id'))
    
    # Si no hay ID de vendedor, retorna None
    if not seller_id:
        return None

    # Si ya se ha consultado este vendedor, retorna el nombre almacenado previamente
    if seller_id in user_data:
        return user_data[seller_id]

    try:
        # Construye la URL de la API de usuarios
        user_url = f'{ENDPOINTMELI}/users/{seller_id}'
        
        # Realiza una solicitud GET a la API de usuarios
        user_response = requests.get(user_url)
        user_response.raise_for_status()
        
        # Obtiene la información del usuario
        user_info = json.loads(user_response.text)
        seller_nickname = user_info.get('nickname')
        
        # Si se encuentra el nombre del vendedor, lo almacena en el diccionario para futuras referencias
        if seller_nickname:
            user_data[seller_id] = seller_nickname
            return seller_nickname
    except requests.exceptions.RequestException as e:
        print(f'Error en la solicitud a la API de usuarios: {str(e)}')
    except Exception as e:
        print(f'Error inesperado al obtener el nombre del usuario: {str(e)}')

    return 
