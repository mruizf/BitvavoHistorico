-- Tabla Fibras
CREATE TABLE IF NOT EXISTS assets (
    id_asset INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);

-- Tabla Distribuciones
CREATE TABLE IF NOT EXISTS lobs (
    id_entry INTEGER PRIMARY KEY AUTOINCREMENT,
    id_asset INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    bitvavo_nonce INTEGER NOT NULL,
    bid_ask_snapshot BLOB NOT NULL,    
    FOREIGN KEY (id_asset) REFERENCES assets(id_asset),
    UNIQUE (id_asset,timestamp)
);

--Tabla para guardar la fecha de creacion de la BD y usarla en la rotacion
CREATE TABLE IF NOT EXISTS creationDate(
    timestamp INTEGER NOT NULL
);