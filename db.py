from pymongo import MongoClient
import os
import pymongo.errors

MONGODBURL = os.getenv('MONGODBURL')

def database_insertion(item_data_batch):
    try:
        # Crear la conexión
        client = MongoClient(MONGODBURL)
        db = client['meli']
        collection = db['datacollection']

        if item_data_batch:
            print('item_data_batch.',item_data_batch)
            # Utiliza insert_many para insertar los documentos en un lote
            collection.insert_many(item_data_batch)
        
    except pymongo.errors.ConnectionFailure as cf_err:
        print('Error de conexión a MongoDB:', cf_err)
    except Exception as e:
        print('Algo salió mal en mongo: ', e)
