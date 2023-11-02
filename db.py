from pymongo import MongoClient
import json

# Conexión a MongoDB
client = MongoClient('mongodb://myUser:myUserPassword@127.0.0.1:27017/')
database = client['nombre_de_tu_base_de_datos']
collection = database['nombre_de_tu_colección']

# Insertar datos en MongoDB
for item in item_data:
    collection.insert_one(item)

with open('datos.json', 'w', encoding='utf-8') as json_file:
    json.dump(item_data, json_file, ensure_ascii=False, indent=4)
