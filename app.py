import streamlit as st
import pandas as pd
import plotly.express as px
import db
import datetime
import os

# Inicializar base de datos y migrar si es necesario
db.init_db()

st.set_page_config(page_title="Gestor Financiero", layout="wide")

# ----------------- SISTEMA DE SEGURIDAD -----------------
def check_password():
    """Devuelve True si el usuario introduce la contraseña correcta."""
    def password_entered():
        if st.session_state["password"] == st.secrets["PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # No guardamos la contraseña en estado
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Primer inicio, pedimos contraseña
        st.text_input("🔒 Introduce la contraseña para acceder a tus finanzas:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Contraseña incorrecta
        st.text_input("🔒 Introduce la contraseña para acceder a tus finanzas:", type="password", on_change=password_entered, key="password")
        st.error("😕 Contraseña incorrecta")
        return False
    else:
        # Contraseña correcta
        return True

if not check_password():
    st.stop()  # Detiene la ejecución de la app aquí si no hay acceso válido

# ----------------- INICIO DE LA APLICACIÓN -----------------
st.title("💸 Gestor de Finanzas Personales")
# ... (el resto de tu código de app.py sigue exactamente igual a partir de aquí)
