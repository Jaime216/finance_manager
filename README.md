# 💸 Gestor de Finanzas Personales

Una aplicación web moderna, intuitiva y privada para la gestión de finanzas personales, desarrollada en **Python** utilizando **Streamlit**, **SQLite**, **Pandas** y **Plotly**. Sin conexiones bancarias automáticas: tus datos son tuyos y se almacenan localmente.

---

## ✨ Características Principales

* **📊 Dashboard General:** Resumen de ingresos, gastos y balance neto con gráficos de distribución por categorías y desglose por métodos de pago.
* **📅 Presupuestos Mensuales:** Planificación de gastos por categorías, seguimiento de progreso global y un selector histórico para consultar presupuestos pasados.
* **🔄 Automatización de Gastos Fijos:** Configura una plantilla de gastos recurrentes (alquiler, suscripciones, gimnasio) e inyéctalos automáticamente cada mes con un solo clic.
* **🎯 Metas de Ahorro (Huchas Virtuales):** Crea objetivos específicos (ej. viaje, fondo de emergencia), haz aportaciones y sigue barras de progreso visuales.
* **📈 Tendencias Históricas:** Gráficos avanzados de evolución del patrimonio acumulado y comparativas mensuales de gastos por categorías.
* **📝 Registro y Filtrado:** Añade ingresos o gastos indicando categoría, concepto, cantidad y **método de pago** (Tarjeta, Bizum, Efectivo, etc.).
* **📁 Historial y Exportación:** Filtra los movimientos por mes y exporta los datos seleccionados a formato **CSV** o realiza copias de seguridad completas de la base de datos (`.db`).

---

## 📂 Estructura del Proyecto

```text
gestor-financiero/
│
├── app.py              # Interfaz gráfica principal (Streamlit)
├── db.py               # Capa de gestión de base de datos (SQLite)
├── populate.py         # Script opcional para generar datos de prueba
├── requirements.txt    # Dependencias de Python
└── README.md           # Documentación del proyecto
