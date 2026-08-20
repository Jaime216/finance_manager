import pandas as pd
from datetime import datetime
import streamlit as st
import requests

# ------------------------------------------------------------------------------
# CONEXIÓN A TURSO (Vía API HTTP)
# ------------------------------------------------------------------------------
TURSO_URL = st.secrets["TURSO_URL"].replace("libsql://", "https://")
TURSO_AUTH_TOKEN = st.secrets["TURSO_AUTH_TOKEN"]

DB_NAME = "finance_manager.db"  # Definido de nuevo para evitar el error en app.py

def execute_query(query, params=None):
    """Ejecuta una consulta SQL en Turso a través de su API HTTP."""
    headers = {
        "Authorization": f"Bearer {TURSO_AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    args = []
    if params:
        for p in params:
            if isinstance(p, float):
                args.append({"type": "float", "value": p})  
            elif isinstance(p, int):
                args.append({"type": "integer", "value": str(p)}) 
            elif p is None:
                args.append({"type": "null"})
            else:
                args.append({"type": "text", "value": str(p)})
    
    payload = {
        "requests": [
            {
                "type": "execute",
                "stmt": {
                    "sql": query,
                    "args": args
                }
            },
            {"type": "close"}
        ]
    }
    
    response = requests.post(f"{TURSO_URL}/v2/pipeline", headers=headers, json=payload)
    if response.status_code != 200:
        raise Exception(f"Error de base de datos: {response.text}")
    
    return response.json()

def get_data(table_name: str) -> pd.DataFrame:
    """Obtiene una tabla completa de Turso y la devuelve como un DataFrame de Pandas."""
    try:
        res = execute_query(f"SELECT * FROM {table_name.lower()}")
        results = res["results"][0]
        if "response" in results and "result" in results["response"]:
            data = results["response"]["result"]
            cols = [col["name"] for col in data["cols"]]
            rows = []
            for r in data["rows"]:
                row_data = []
                for val in r:
                    if val["type"] == "null":
                        row_data.append(None)
                    elif val["type"] in ["integer", "float"]:
                        row_data.append(float(val["value"]))
                    else:
                        row_data.append(val["value"])
                rows.append(row_data)
            return pd.DataFrame(rows, columns=cols)
        return pd.DataFrame()
    except Exception as e:
        print(f"Error al leer la tabla {table_name}: {e}")
        return pd.DataFrame()

def init_db():
    queries = [
        '''CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            tipo TEXT,
            categoria TEXT,
            concepto TEXT,
            cantidad REAL,
            metodo_pago TEXT,
            notas TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS presupuestos_categorias (
            periodo TEXT,
            categoria TEXT,
            cantidad REAL,
            PRIMARY KEY (periodo, categoria)
        )''',
        '''CREATE TABLE IF NOT EXISTS gastos_fijos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concepto TEXT,
            categoria TEXT,
            cantidad REAL,
            metodo_pago TEXT,
            notas TEXT
        )''',
        '''CREATE TABLE IF NOT EXISTS metas_ahorro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            objetivo REAL,
            actual REAL
        )'''
    ]
    
    for q in queries:
        try:
            execute_query(q)
        except Exception as e:
            print(f"Error inicializando tabla: {e}")

# Inicializar tablas al cargar el módulo
init_db()

# ------------------------------------------------------------------------------
# MOVIMIENTOS
# ------------------------------------------------------------------------------
def add_movimiento(fecha, tipo, categoria, concepto, cantidad, metodo_pago, notas):
    execute_query(
        "INSERT INTO movimientos (fecha, tipo, categoria, concepto, cantidad, metodo_pago, notas) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (fecha, tipo, categoria, concepto, float(cantidad), metodo_pago, notas)
    )
    return True

# ------------------------------------------------------------------------------
# PRESUPUESTOS
# ------------------------------------------------------------------------------
def set_presupuesto_categoria(periodo, categoria, cantidad):
    execute_query(
        "REPLACE INTO presupuestos_categorias (periodo, categoria, cantidad) VALUES (?, ?, ?)", 
        (periodo, categoria, float(cantidad))
    )
    return True

# ------------------------------------------------------------------------------
# GASTOS FIJOS
# ------------------------------------------------------------------------------
def add_gasto_fijo(concepto, categoria, cantidad, metodo_pago, notas):
    execute_query(
        "INSERT INTO gastos_fijos (concepto, categoria, cantidad, metodo_pago, notas) VALUES (?, ?, ?, ?, ?)",
        (concepto, categoria, float(cantidad), metodo_pago, notas)
    )
    return True

def delete_gasto_fijo(gasto_id):
    execute_query("DELETE FROM gastos_fijos WHERE id = ?", (int(gasto_id),))
    return True

def aplicar_gastos_fijos(periodo):
    """Inyecta los gastos fijos en el día 1 del mes seleccionado (periodo format: 'YYYY-MM')"""
    df_fijos = get_data("gastos_fijos")
    if df_fijos.empty:
        return 0
    
    cargados = 0
    fecha_aplicacion = f"{periodo}-01"
    df_movs = get_data("movimientos")
    
    for _, row in df_fijos.iterrows():
        concepto = row['concepto']
        categoria = row['categoria']
        cantidad = float(row['cantidad'])
        metodo_pago = row['metodo_pago']
        notas = row['notas']
        
        existe = False
        if not df_movs.empty:
            match = df_movs[(df_movs['fecha'] == fecha_aplicacion) & 
                            (df_movs['concepto'] == concepto) & 
                            (df_movs['tipo'] == 'Gasto')]
            if not match.empty:
                existe = True
        
        if not existe:
            add_movimiento(fecha_aplicacion, 'Gasto', categoria, concepto, cantidad, metodo_pago, notas)
            cargados += 1
            
    return cargados

# ------------------------------------------------------------------------------
# METAS DE AHORRO
# ------------------------------------------------------------------------------
def add_meta_ahorro(nombre, objetivo, actual=0.0):
    execute_query(
        "INSERT INTO metas_ahorro (nombre, objetivo, actual) VALUES (?, ?, ?)", 
        (nombre, float(objetivo), float(actual))
    )
    return True

def sumar_a_meta(meta_id, cantidad):
    execute_query(
        "UPDATE metas_ahorro SET actual = actual + ? WHERE id = ?", 
        (float(cantidad), int(meta_id))
    )
    return True

def delete_meta_ahorro(meta_id):
    execute_query("DELETE FROM metas_ahorro WHERE id = ?", (int(meta_id),))
    return True
