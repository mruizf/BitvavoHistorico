# -*- coding: utf-8 -*-
"""
Created on Sun Aug 24 18:30:32 2025

@author: M R
"""

import sqlite3,os,zlib,pickle,shutil
from python_bitvavo_api.bitvavo import Bitvavo
from typing import NoReturn,NewType,List

from contextlib import closing
from datetime import datetime, timedelta



#New type because there isnt BLOB
BLOB = NewType("BLOB", bytes)

class BitbavoTickers:
    TICKERS=['BTC-EUR','ETH-EUR','SOL-EUR','LINK-EUR']

DBNAME="criptoLOB.db"
SCHEMA="SchemaLOB.sql"

class QueryBase():
    
    SQL="" #Query a lanzar
    registro={} # Mapa para las variables nombradas 

    def execute(self,conn):
        """Ejecuta la query usando el conector dado"""
       
        try: 
           with closing(conn.cursor()) as cursor:
                cursor.execute(self.SQL, self.registro)
                
                query_type = self.SQL.strip().split()[0].upper()
        
                if query_type == "SELECT":
                   result = cursor.fetchall()
                   return result
                else:
                   conn.commit()
                   affected = cursor.rowcount
                   return affected
        except sqlite3.IntegrityError as e:
            print(f"Error de integridad: {e}")
        except sqlite3.DatabaseError as e:
            print(f"Error de DB: {e}")
        except sqlite3.ProgammingError as e:
            print(f"Error de programación: {e}")
            

#table field names 
class DB_ASSETS:
    TABLE       = "assets"
    ID_ASSET    = "id_asset"
    NOMBRE      = "nombre"
    
class DB_LOBS:
    TABLE            = "lobs"
    ID_ENTRY         = "id_entry "
    ID_ASSET         = "id_asset"
    TIMESTAMP        = "timestamp"
    BITVAVO_NONCE    = "bitvavo_nonce"
    BID_ASK_SNAPSHOT = "bid_ask_snapshot"
    
class DB_CREATION_DATE:
    TABLE     = "creationDate"
    TIMESTAMP = "timestamp"
    
class BunchFields:
    BID="bid"
    ASK="ask"

class BitvavoFields:
    BIDS="bids"
    ASKS="asks"


class InsertCreationDate(QueryBase):
    def __init__(self, timestamp):
        self.registro={DB_CREATION_DATE.TIMESTAMP:timestamp}
        self.SQL = f"""INSERT INTO {DB_CREATION_DATE.TABLE} ({DB_CREATION_DATE.TIMESTAMP}) 
                    VALUES (:{DB_CREATION_DATE.TIMESTAMP})"""

class InsertNewAsset(QueryBase):
    def __init__(self, nombre_asset=""):
        self.registro={DB_ASSETS.NOMBRE:nombre_asset}
        self.SQL = f"""INSERT OR IGNORE INTO {DB_ASSETS.TABLE} ({DB_ASSETS.NOMBRE}) 
                    VALUES (:{DB_ASSETS.NOMBRE})"""

class InsertNewLOB(QueryBase):
    def __init__(self, idAsset="",timestamp_ms=0,bitvavo_nonce=0,bid_ask_snapshot:BLOB = None):
        
        
        self.registro={DB_LOBS.ID_ASSET        :idAsset, 
                       DB_LOBS.TIMESTAMP       :timestamp_ms, 
                       DB_LOBS.BITVAVO_NONCE   :bitvavo_nonce, 
                       DB_LOBS.BID_ASK_SNAPSHOT:bid_ask_snapshot}
    
        self.SQL = f"""INSERT INTO {DB_LOBS.TABLE} ({DB_LOBS.ID_ASSET},{DB_LOBS.TIMESTAMP},
                    {DB_LOBS.BITVAVO_NONCE},{DB_LOBS.BID_ASK_SNAPSHOT}) 
                    VALUES (:{DB_LOBS.ID_ASSET}, :{DB_LOBS.TIMESTAMP}, 
                            :{DB_LOBS.BITVAVO_NONCE}, :{DB_LOBS.BID_ASK_SNAPSHOT})"""

class GetIdAssetObj(QueryBase):
    def __init__(self,asset):
        self.registro ={DB_ASSETS.ID_ASSET:asset}
        self.SQL = f"""SELECT {DB_ASSETS.ID_ASSET} FROM {DB_ASSETS.TABLE} WHERE 
                    {DB_ASSETS.NOMBRE} = :{DB_ASSETS.ID_ASSET}"""

class GetDBTimestamp(QueryBase):
    def __init__(self):
        self.registro ={}
        self.SQL = f"SELECT {DB_CREATION_DATE.TIMESTAMP} FROM {DB_CREATION_DATE.TABLE}"

def GetIdAsset(conn,asset):
    get=GetIdAssetObj(asset)
    resultados=get.execute(conn)
    
    if not resultados:
        print("No se encontró la activo")
        return None
    else:
        #id_asset = resultados[0][0]   # fetalldone devuelve una lista de tuplas
        (id_asset,), = resultados #desempaqueta la primera tupla
        return id_asset

def GetDBTimestamp(dbName):
    with sqlite3.connect(dbName) as conn:
        get=GetDBTimestamp(conn)
        resultados=get.execute(conn)

        if not resultados:
            print("No hay timestamp")
            return None
        else:
            (timestamp,), = resultados #desempaqueta la primera tupla
            return timestamp

def rotate_db(dbName:str):
    if not os.path.exists(dbName):
        return  # No hay nada que rotar

    # Nombre del archivo rotado: orderbook_YYYY-MM-DD.db
    
    today = datetime.now()
    timestampCreation=GetDBTimestamp(dbName)
    
    datetimeCreation=datetime.fromtimestamp(timestampCreation)
    dateCreationStr = datetimeCreation.strftime("%d_%m_%Y")
    
    delta = today-datetimeCreation
    
    if delta > timedelta(days=7):
        rotated_name = f"lob_{dateCreationStr}.db"
        rotated_path = rotated_name

        if not os.path.exists(rotated_path):
            # Mueve la base de datos actual a un archivo rotado
            shutil.move(dbName, rotated_path)
            print(f"DB rotada a {rotated_path}")

def create_db_and_setup(dbName:str,schemaLOB:str,tickers:List) -> NoReturn:
    if not os.path.exists(dbName):
        print("Base de datos no encontrada. Creando nueva...")
        with sqlite3.connect(dbName) as conn:
            cursor = conn.cursor()

            with open(schemaLOB, "r", encoding="utf-8") as f:
                schema = f.read()
                cursor.executescript(schema)

            conn.commit()
            
            #Ahora guardamos la fecha de creacion
            timestamp = datetime.now().timestamp()
            insCD=InsertCreationDate(timestamp)
            insCD.execute(conn)
            
            #insertamos los activos, las criptos en este caso que tambien son los tickers de bitvavo
            for ticker in tickers:    
                ins=InsertNewAsset(ticker)
                ins.execute(conn)
        
            conn.commit()
        print("Base de datos creada con éxito.")
    else:
        print("La base de datos ya existe, no se modificó.")

#############################MAIN#################################################

if __name__=="__main__":
    
    bitvavo = Bitvavo()
    
    rotate_db(DBNAME)
    create_db_and_setup(DBNAME, SCHEMA, BitbavoTickers.TICKERS)
    
    conn = sqlite3.connect(DBNAME)
    #cursor = conn.cursor()
        
    for asset in BitbavoTickers.TICKERS:
        response = bitvavo.book(asset, {})
        bid_ask={"bid":response["bids"],"ask":response["asks"]}
        compressed_bid_ask = zlib.compress(pickle.dumps(bid_ask))
        
        idAsset = GetIdAsset(conn, asset)
        
        insLob=InsertNewLOB(idAsset,response["timestamp"],response["nonce"],compressed_bid_ask)
        insLob.execute(conn)
        
    conn.commit()
    conn.close()