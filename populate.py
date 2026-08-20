import sqlite3
import random

DB_NAME = "finance_manager.db"

def populate_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Limpieza total de todas las tablas existentes
    print("🧹 Limpiando la base de datos...")
    cursor.execute("DELETE FROM movimientos")
    cursor.execute("DELETE FROM presupuestos_categorias")
    cursor.execute("DELETE FROM gastos_fijos")
    cursor.execute("DELETE FROM metas_ahorro")
    
    # 2. Inyectar Plantilla de Gastos Fijos
    print("📌 Inyectando plantilla de gastos fijos recurrentes...")
    fijos = [
        ('Alquiler', 'Vivienda/Facturas', 750.0, 'Cuenta Bancaria / Transferencia', 'Pago mensual piso'),
        ('Internet Fibra', 'Vivienda/Facturas', 35.0, 'Cuenta Bancaria / Transferencia', 'Fibra óptica 1Gb'),
        ('Netflix', 'Suscripciones', 12.99, 'PayPal', 'Plan estándar'),
        ('Spotify', 'Suscripciones', 9.99, 'PayPal', 'Cuenta individual'),
        ('Gimnasio', 'Suscripciones', 29.90, 'Tarjeta de Débito', 'Cuota mensual club fitness')
    ]
    cursor.executemany("INSERT INTO gastos_fijos (concepto, categoria, cantidad, metodo_pago, notas) VALUES (?, ?, ?, ?, ?)", fijos)
    
    # 3. Inyectar Metas de Ahorro (Huchas Virtuales)
    print("🎯 Inyectando huchas virtuales...")
    metas = [
        ('Viaje a Japón', 2500.0, 1450.0),
        ('Fondo de Emergencia', 3000.0, 3000.0), # Meta conseguida para probar efectos
        ('Nuevo Ordenador', 1200.0, 450.0)
    ]
    cursor.executemany("INSERT INTO metas_ahorro (nombre, objetivo, actual) VALUES (?, ?, ?)", metas)
    
    presupuestos = []
    movimientos = []
    
    conceptos_alim = ['Mercadona', 'Carrefour', 'Lidl', 'Frutería', 'Carnicería']
    conceptos_ocio = ['Cine', 'Cena en restaurante', 'Cervezas con amigos', 'Entradas concierto']
    conceptos_trans = ['Gasolina', 'Abono Metro', 'Taxi/Uber']
    metodos_pago_varios = ['Tarjeta de Débito', 'Tarjeta de Crédito', 'Efectivo', 'Bizum']
    
    print("📈 Generando historial financiero de 8 meses (Enero - Agosto 2026)...")
    
    for mes in range(1, 9):
        periodo = f'2026-{mes:02d}'
        
        # Presupuestos por categoría para este mes (incluyendo uno personalizado 'Vacaciones')
        presupuestos.extend([
            (periodo, 'Alimentación', 400.0),
            (periodo, 'Vivienda/Facturas', 850.0),
            (periodo, 'Transporte', 120.0),
            (periodo, 'Ocio', 250.0),
            (periodo, 'Suscripciones', 60.0),
            (periodo, 'Vacaciones', 200.0)
        ])
        
        # Ingresos mensuales
        movimientos.append((f'2026-{mes:02d}-01', 'Ingreso', 'Otra (Personalizada)', 'Nómina', 2300.0, 'Cuenta Bancaria / Transferencia', 'Nómina mensual'))
        
        # Paga extra de verano (Junio)
        if mes == 6:
            movimientos.append((f'2026-{mes:02d}-25', 'Ingreso', 'Otra (Personalizada)', 'Paga Extra Verano', 2300.0, 'Cuenta Bancaria / Transferencia', ''))
            
        # Simulación de aplicación de gastos fijos en el mes
        movimientos.append((f'2026-{mes:02d}-02', 'Gasto', 'Vivienda/Facturas', 'Alquiler', 750.0, 'Cuenta Bancaria / Transferencia', 'Pago mensual piso'))
        movimientos.append((f'2026-{mes:02d}-05', 'Gasto', 'Vivienda/Facturas', 'Internet Fibra', 35.0, 'Cuenta Bancaria / Transferencia', 'Fibra óptica 1Gb'))
        movimientos.append((f'2026-{mes:02d}-01', 'Gasto', 'Suscripciones', 'Netflix', 12.99, 'PayPal', 'Plan estándar'))
        movimientos.append((f'2026-{mes:02d}-02', 'Gasto', 'Suscripciones', 'Spotify', 9.99, 'PayPal', 'Cuenta individual'))
        movimientos.append((f'2026-{mes:02d}-15', 'Gasto', 'Suscripciones', 'Gimnasio', 29.90, 'Tarjeta de Débito', 'Cuota mensual club fitness'))
        
        # Factura de luz variable
        factura_luz = round(random.uniform(45.0, 90.0), 2)
        movimientos.append((f'2026-{mes:02d}-10', 'Gasto', 'Vivienda/Facturas', 'Factura Luz', factura_luz, 'Cuenta Bancaria / Transferencia', ''))

        # Gastos variables de Alimentación
        for _ in range(random.randint(8, 12)):
            dia = random.randint(1, 28)
            cant = round(random.uniform(25.0, 75.0), 2)
            movimientos.append((f'2026-{mes:02d}-{dia:02d}', 'Gasto', 'Alimentación', random.choice(conceptos_alim), cant, random.choice(metodos_pago_varios), ''))
            
        # Gastos de Ocio (más elevados en Julio y Agosto)
        num_ocio = random.randint(8, 14) if mes in [7, 8] else random.randint(3, 7)
        for _ in range(num_ocio):
            dia = random.randint(1, 28)
            cant = round(random.uniform(15.0, 65.0), 2)
            movimientos.append((f'2026-{mes:02d}-{dia:02d}', 'Gasto', 'Ocio', random.choice(conceptos_ocio), cant, random.choice(metodos_pago_varios), ''))
            
        # Gastos de Transporte
        for _ in range(random.randint(4, 8)):
            dia = random.randint(1, 28)
            cant = round(random.uniform(10.0, 40.0), 2)
            movimientos.append((f'2026-{mes:02d}-{dia:02d}', 'Gasto', 'Transporte', random.choice(conceptos_trans), cant, random.choice(metodos_pago_varios), ''))
            
        # Gasto en categoría personalizada (Vacaciones en meses estivales)
        if mes in [7, 8]:
            movimientos.append((f'2026-{mes:02d}-20', 'Gasto', 'Vacaciones', 'Reserva Hotel Playa', 180.0, 'Tarjeta de Crédito', 'Escapada verano'))

    # 4. Volcado masivo a SQLite
    cursor.executemany("INSERT INTO presupuestos_categorias (periodo, categoria, cantidad) VALUES (?, ?, ?)", presupuestos)
    cursor.executemany("INSERT INTO movimientos (fecha, tipo, categoria, concepto, cantidad, metodo_pago, notas) VALUES (?, ?, ?, ?, ?, ?, ?)", movimientos)
    
    conn.commit()
    conn.close()
    print("✅ ¡Base de datos limpia y poblada al 100%! Ya puedes lanzar la aplicación.")

if __name__ == "__main__":
    populate_db()
