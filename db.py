import sqlite3
import pandas as pd

DB_NAME = "finance_manager.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabla general de movimientos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha DATE,
            tipo TEXT,
            categoria TEXT,
            concepto TEXT,
            cantidad REAL,
            metodo_pago TEXT,
            notas TEXT
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE movimientos ADD COLUMN metodo_pago TEXT DEFAULT 'Desconocido'")
    except sqlite3.OperationalError:
        pass 
        
    # Tabla de Presupuestos por Categorías
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS presupuestos_categorias (
            periodo TEXT,
            categoria TEXT,
            cantidad REAL,
            PRIMARY KEY (periodo, categoria)
        )
    ''')
    
    # Tabla de Plantilla de Gastos Fijos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gastos_fijos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concepto TEXT,
            categoria TEXT,
            cantidad REAL,
            metodo_pago TEXT,
            notas TEXT
        )
    ''')
    
    # NUEVA TABLA: Metas de Ahorro (Huchas Virtuales)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metas_ahorro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            objetivo REAL,
            actual REAL
        )
    ''')
    
    conn.commit()
    conn.close()

def add_movimiento(fecha, tipo, categoria, concepto, cantidad, metodo_pago, notas):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO movimientos (fecha, tipo, categoria, concepto, cantidad, metodo_pago, notas) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (fecha, tipo, categoria, concepto, cantidad, metodo_pago, notas))
    conn.commit()
    conn.close()

def set_presupuesto_categoria(periodo, categoria, cantidad):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("REPLACE INTO presupuestos_categorias (periodo, categoria, cantidad) VALUES (?, ?, ?)", 
                   (periodo, categoria, cantidad))
    conn.commit()
    conn.close()

def add_gasto_fijo(concepto, categoria, cantidad, metodo_pago, notas):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO gastos_fijos (concepto, categoria, cantidad, metodo_pago, notas) VALUES (?, ?, ?, ?, ?)",
                   (concepto, categoria, cantidad, metodo_pago, notas))
    conn.commit()
    conn.close()

def delete_gasto_fijo(gasto_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gastos_fijos WHERE id = ?", (gasto_id,))
    conn.commit()
    conn.close()

def aplicar_gastos_fijos(periodo):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, concepto, categoria, cantidad, metodo_pago, notas FROM gastos_fijos")
    fijos = cursor.fetchall()
    cargados = 0
    fecha_aplicacion = f"{periodo}-01"
    
    for _, concepto, categoria, cantidad, metodo_pago, notas in fijos:
        cursor.execute("SELECT id FROM movimientos WHERE fecha = ? AND concepto = ? AND tipo = 'Gasto'", (fecha_aplicacion, concepto))
        existe = cursor.fetchone()
        if not existe:
            cursor.execute("INSERT INTO movimientos (fecha, tipo, categoria, concepto, cantidad, metodo_pago, notas) VALUES (?, 'Gasto', ?, ?, ?, ?, ?)",
                           (fecha_aplicacion, categoria, concepto, cantidad, metodo_pago, notas))
            cargados += 1
            
    conn.commit()
    conn.close()
    return cargados

# NUEVAS FUNCIONES PARA METAS DE AHORRO
def add_meta_ahorro(nombre, objetivo, actual=0.0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO metas_ahorro (nombre, objetivo, actual) VALUES (?, ?, ?)", (nombre, objetivo, actual))
    conn.commit()
    conn.close()

def sumar_a_meta(meta_id, cantidad):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE metas_ahorro SET actual = actual + ? WHERE id = ?", (cantidad, meta_id))
    conn.commit()
    conn.close()

def delete_meta_ahorro(meta_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM metas_ahorro WHERE id = ?", (meta_id,))
    conn.commit()
    conn.close()

def get_data(table_name):
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    except:
        df = pd.DataFrame()
    conn.close()
    return df
