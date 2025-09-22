#!/bin/bash

# Delay entre ejecuciones (en segundos)
DELAY=15

# Ruta completa a tu script Python
SCRIPT=~/BitvavoHistorico/BitvavoHistorico.py

# Ruta de tu base de datos SQLite
DB=~/BitvavoHistorico/criptoLOB.db

# Log de salida
LOG=~/BitvavoHistorico/bitvavo_runner.log

while true
do
    START=$(date +%s)  # tiempo de inicio en segundos
    echo "Ejecución a $(date)" >> "$LOG"

    # Ejecutar script Python
    python3 "$SCRIPT" >> "$LOG" 2>&1

    END=$(date +%s)  # tiempo de fin
    DURATION=$((END-START))  # duración en segundos

    # Tamaño de la base de datos en KB
    if [ -f "$DB" ]; then
        DBSIZE=$(du -k "$DB" | cut -f1)
    else
        DBSIZE=0
    fi

    echo "Terminado ejecución a $(date). Duración: ${DURATION} segundos. Tamaño DB: ${DBSIZE} KB" >> "$LOG"
    echo "-------------------------------------------" >> "$LOG"

    sleep $DELAY
done
