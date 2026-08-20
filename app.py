import streamlit as st
import pandas as pd
import plotly.express as px
import db
import datetime
import os

# 1. Configuración de la página
st.set_page_config(page_title="Gestor Financiero", layout="wide")

# 2. Inicializar base de datos
db.init_db()

# 3. Sistema de Seguridad (Contraseña aislada en un contenedor)
ADMIN_PASSWORD = st.secrets.get("PASSWORD", "1234")

if not st.session_state.get("password_correct", False):
    # El contenedor limpia y borra todos los elementos de login al hacer el rerun
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            with st.form("login_form"):
                st.markdown("### 🔒 Acceso Restringido")
                st.write("Introduce tu contraseña para ver las finanzas.")
                
                pwd_input = st.text_input("Contraseña", type="password")
                submit = st.form_submit_button("Entrar", use_container_width=True)
                
                if submit:
                    if pwd_input == ADMIN_PASSWORD:
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("😕 Contraseña incorrecta")
    st.stop()

# ==============================================================================
# 🚀 A PARTIR DE AQUÍ LA CONTRASEÑA ES CORRECTA
# ==============================================================================

st.title("💸 Gestor de Finanzas Personales")

CATEGORIAS_ESTANDAR = ["Alimentación", "Vivienda/Facturas", "Transporte", "Ocio", "Suscripciones"]
CATEGORIAS_DROPDOWN = CATEGORIAS_ESTANDAR + ["Otra (Personalizada)"]
METODOS_PAGO = ["Cuenta Bancaria / Transferencia", "Tarjeta de Débito", "Tarjeta de Crédito", "Efectivo", "Bizum", "PayPal"]
MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

# Obtener datos de la base de datos
df_movimientos = db.get_data("movimientos")
df_presup_cat = db.get_data("presupuestos_categorias")
df_gastos_fijos = db.get_data("gastos_fijos")
df_metas = db.get_data("metas_ahorro")

# ----------------- PROCESAMIENTO DE DATOS -----------------
if not df_movimientos.empty:
    df_movimientos['fecha'] = pd.to_datetime(df_movimientos['fecha'])
    df_movimientos['periodo'] = df_movimientos['fecha'].dt.strftime("%Y-%m")
    df_movimientos = df_movimientos.sort_values('fecha')

# ----------------- INTERFAZ DE PESTAÑAS -----------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 Dashboard", 
    "📅 Presupuestos", 
    "🎯 Metas Ahorro", 
    "📈 Tendencias",
    "📝 Añadir Movimiento", 
    "📁 Historial",
    "⚙️ Backup"
])

# --- PESTAÑA 1: DASHBOARD GENERAL ---
with tab1:
    st.subheader("Resumen General")
    if not df_movimientos.empty:
        ingresos = df_movimientos[df_movimientos['tipo'] == 'Ingreso']['cantidad'].sum()
        gastos = df_movimientos[df_movimientos['tipo'] == 'Gasto']['cantidad'].sum()
        balance = ingresos - gastos
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Ingresos", f"{ingresos:.2f} €")
        col2.metric("Total Gastos", f"{gastos:.2f} €")
        col3.metric("Balance General (Ahorro)", f"{balance:.2f} €", delta=float(balance))
        
        st.markdown("---")
        
        col_graf1, col_graf2 = st.columns(2)
        df_solo_gastos = df_movimientos[df_movimientos['tipo'] == 'Gasto']
        
        with col_graf1:
            st.markdown("#### Distribución por Categoría")
            if not df_solo_gastos.empty or balance > 0:
                gastos_agrupados = df_solo_gastos.groupby('categoria')['cantidad'].sum().reset_index() if not df_solo_gastos.empty else pd.DataFrame(columns=['categoria', 'cantidad'])
                
                if balance > 0:
                    fila_ahorro = pd.DataFrame([{'categoria': '✅ Ahorrado / No gastado', 'cantidad': balance}])
                    gastos_agrupados = pd.concat([gastos_agrupados, fila_ahorro], ignore_index=True)
                
                fig_general = px.pie(
                    gastos_agrupados, values='cantidad', names='categoria', hole=0.4, color='categoria',
                    color_discrete_map={'✅ Ahorrado / No gastado': '#2ecc71'}
                )
                st.plotly_chart(fig_general, use_container_width=True)
            else:
                st.info("Sin datos para gráfica.")

        with col_graf2:
            st.markdown("#### Uso de Métodos de Pago (Gastos)")
            if not df_solo_gastos.empty and 'metodo_pago' in df_solo_gastos.columns:
                pagos_agrupados = df_solo_gastos.groupby('metodo_pago')['cantidad'].sum().reset_index()
                pagos_agrupados = pagos_agrupados.sort_values('cantidad', ascending=True)
                
                fig_pagos = px.bar(
                    pagos_agrupados, x='cantidad', y='metodo_pago', orientation='h',
                    labels={'cantidad': 'Gastado (€)', 'metodo_pago': 'Método'},
                    color='metodo_pago'
                )
                fig_pagos.update_layout(showlegend=False)
                st.plotly_chart(fig_pagos, use_container_width=True)
            else:
                st.info("Sin datos de métodos de pago registrados.")
    else:
        st.info("Añade movimientos para ver tu resumen.")

# --- PESTAÑA 2: PRESUPUESTO MENSUAL ---
with tab2:
    st.subheader("Planificación y Seguimiento de Gastos")
    
    fecha_hoy = datetime.date.today()
    periodo_actual_defecto = fecha_hoy.strftime("%Y-%m")
    
    periodos_existentes = {periodo_actual_defecto}
    if not df_movimientos.empty:
        periodos_existentes.update(df_movimientos['periodo'].dropna().unique())
    if not df_presup_cat.empty:
        periodos_existentes.update(df_presup_cat['periodo'].dropna().unique())
        
    lista_periodos = sorted(list(periodos_existentes), reverse=True)
    
    def formatear_mes(periodo_str):
        y, m = periodo_str.split('-')
        return f"{MESES[int(m)-1]} {y}"
        
    col_selector, _ = st.columns([1, 2])
    with col_selector:
        periodo_view = st.selectbox(
            "📅 Selecciona el mes a visualizar:",
            options=lista_periodos,
            index=lista_periodos.index(periodo_actual_defecto),
            format_func=formatear_mes
        )
        
    df_pres_mes = df_presup_cat[df_presup_cat['periodo'] == periodo_view] if not df_presup_cat.empty else pd.DataFrame()
    
    st.markdown("---")
    col_auto1, col_auto2 = st.columns([2, 1])
    with col_auto1:
        st.info(f"💡 Puedes inyectar automáticamente tus gastos fijos recurrentes en el mes de **{formatear_mes(periodo_view)}**.")
    with col_auto2:
        if st.button("🚀 Cargar Gastos Fijos", use_container_width=True):
            cargados = db.aplicar_gastos_fijos(periodo_view)
            if cargados > 0:
                st.success(f"¡Se han añadido {cargados} gastos fijos!")
                st.rerun()
            else:
                st.warning("No hay nuevos gastos fijos para cargar.")

    with st.expander("⚙️ Gestionar Plantilla de Gastos Fijos y Presupuestos", expanded=False):
        st.markdown("#### 🔄 Plantilla de Gastos Fijos Recurrentes")
        if not df_gastos_fijos.empty:
            st.dataframe(df_gastos_fijos.drop(columns=['id']), use_container_width=True, hide_index=True)
            gasto_a_borrar = st.selectbox("Selecciona gasto fijo a eliminar", options=[None] + list(df_gastos_fijos['id']), format_func=lambda x: f"ID {x}: {df_gastos_fijos[df_gastos_fijos['id']==x]['concepto'].values[0]}" if x else "Ninguno", key="del_gasto_fijo")
            if gasto_a_borrar and st.button("Eliminar Gasto Fijo Seleccionado"):
                db.delete_gasto_fijo(gasto_a_borrar)
                st.success("Eliminado.")
                st.rerun()
        else:
            st.write("No hay gastos fijos configurados.")
            
        with st.form("form_nuevo_gasto_fijo", clear_on_submit=True):
            st.markdown("##### Añadir nuevo gasto fijo")
            fc1, fc2, fc3 = st.columns(3)
            with fc1: f_conc = st.text_input("Concepto")
            with fc2: f_cat = st.selectbox("Categoría", CATEGORIAS_ESTANDAR)
            with fc3: f_cant = st.number_input("Cantidad (€)", min_value=0.0, format="%.2f")
            f_metodo = st.selectbox("Método de Pago", METODOS_PAGO)
            f_notas = st.text_input("Notas")
            if st.form_submit_button("Guardar en Plantilla"):
                if f_conc.strip():
                    db.add_gasto_fijo(f_conc, f_cat, f_cant, f_metodo, f_notas)
                    st.success("Guardado.")
                    st.rerun()

        st.markdown("---")
        st.markdown("#### 1️⃣ Configurar Presupuestos Base")
        with st.form("form_presupuesto_base"):
            y_def, m_def = periodo_view.split('-')
            col_y, col_m = st.columns(2)
            with col_y: y_base = st.number_input("Año", value=int(y_def), step=1, key="y_base")
            with col_m: m_base = st.selectbox("Mes", MESES, index=int(m_def) - 1, key="m_base")
            
            st.markdown("---")
            cols = st.columns(3)
            inputs_base = {}
            for i, cat in enumerate(CATEGORIAS_ESTANDAR):
                valor_defecto = float(df_pres_mes[df_pres_mes['categoria'] == cat]['cantidad'].iloc[0]) if not df_pres_mes.empty and cat in df_pres_mes['categoria'].values else 0.0
                with cols[i % 3]:
                    inputs_base[cat] = st.number_input(f"{cat} (€)", min_value=0.0, value=valor_defecto, format="%.2f", step=50.0)
            if st.form_submit_button("Guardar Presupuestos Base"):
                mes_num = MESES.index(m_base) + 1
                for cat, cant in inputs_base.items():
                    db.set_presupuesto_categoria(f"{y_base}-{mes_num:02d}", cat, cant)
                st.success("Guardado.")
                st.rerun()

    st.markdown("---")
    st.markdown(f"### Progreso Global de {formatear_mes(periodo_view)}")
    df_gastos_mes = df_movimientos[(df_movimientos['tipo'] == 'Gasto') & (df_movimientos['periodo'] == periodo_view)] if not df_movimientos.empty else pd.DataFrame()
    total_presupuesto = df_pres_mes['cantidad'].sum() if not df_pres_mes.empty else 0.0
    total_gastado = df_gastos_mes['cantidad'].sum() if not df_gastos_mes.empty else 0.0
    
    if total_presupuesto > 0:
        restante_global = total_presupuesto - total_gastado
        pct_global = min(total_gastado / total_presupuesto, 1.0) if total_presupuesto > 0 else 0
        cg1, cg2, cg3 = st.columns(3)
        cg1.metric("Presupuesto", f"{total_presupuesto:.2f} €")
        cg2.metric("Gastado", f"{total_gastado:.2f} €")
        cg3.metric("Restante", f"{restante_global:.2f} €", delta=float(restante_global), delta_color="normal" if restante_global >= 0 else "inverse")
        st.progress(pct_global)
    else:
        st.info("Configura presupuestos para ver el progreso.")

    st.markdown("### 🔍 Desglose por Categorías")
    categorias_activas = set()
    if not df_pres_mes.empty: categorias_activas.update(df_pres_mes['categoria'].unique())
    if not df_gastos_mes.empty: categorias_activas.update(df_gastos_mes['categoria'].unique())
    
    if categorias_activas:
        for cat in sorted(categorias_activas):
            with st.container():
                st.markdown(f"**{cat}**")
                limite_cat = df_pres_mes[df_pres_mes['categoria'] == cat]['cantidad'].iloc[0] if not df_pres_mes.empty and cat in df_pres_mes['categoria'].values else 0.0
                gastado_cat = df_gastos_mes[df_gastos_mes['categoria'] == cat]['cantidad'].sum() if not df_gastos_mes.empty and cat in df_gastos_mes['categoria'].values else 0.0
                restante_cat = limite_cat - gastado_cat
                c1, c2, c3 = st.columns(3)
                c1.metric("Presupuesto", f"{limite_cat:.2f} €")
                c2.metric("Gastado", f"{gastado_cat:.2f} €")
                if limite_cat > 0:
                    c3.metric("Restante", f"{restante_cat:.2f} €", delta=float(restante_cat), delta_color="normal" if restante_cat >= 0 else "inverse")
                    st.progress(min(gastado_cat / limite_cat, 1.0))
                else:
                    c3.metric("Restante", f"{restante_cat:.2f} €", delta=float(restante_cat), delta_color="inverse")
                    st.error("Sin presupuesto fijado.")
                st.write("---")
    else:
        st.write("Aún no hay datos.")

# --- PESTAÑA 3: METAS DE AHORRO / HUCHA VIRTUAL ---
with tab3:
    st.subheader("🎯 Objetivos y Huchas Virtuales")
    st.write("Define metas específicas para tu dinero ahorrado y haz un seguimiento visual de su progreso.")
    
    col_crear, col_abonar = st.columns(2)
    
    with col_crear:
        with st.form("form_crear_meta", clear_on_submit=True):
            st.markdown("#### ➕ Crear Nueva Hucha")
            n_nombre = st.text_input("Nombre de la Meta (ej. Viaje a Japón)")
            n_objetivo = st.number_input("Cantidad Objetivo (€)", min_value=1.0, format="%.2f", step=100.0)
            n_inicial = st.number_input("Ahorro inicial acumulado (€)", min_value=0.0, format="%.2f", step=50.0)
            
            if st.form_submit_button("Crear Meta"):
                if n_nombre.strip():
                    db.add_meta_ahorro(n_nombre, n_objetivo, n_inicial)
                    st.success(f"¡Hucha '{n_nombre}' creada con éxito!")
                    st.rerun()
                else:
                    st.error("Pon un nombre válido.")

    with col_abonar:
        with st.form("form_abonar_meta", clear_on_submit=True):
            st.markdown("#### 💰 Ingresar Dinero en una Hucha")
            if not df_metas.empty:
                meta_dict = {row['nombre']: row['id'] for _, row in df_metas.iterrows()}
                meta_elegida = st.selectbox("Selecciona Hucha", options=list(meta_dict.keys()))
                cantidad_aporte = st.number_input("Cantidad a añadir (€)", min_value=0.01, format="%.2f", step=10.0)
                
                if st.form_submit_button("Aportar a la Hucha"):
                    meta_id = meta_dict[meta_elegida]
                    db.sumar_a_meta(meta_id, cantidad_aporte)
                    st.success(f"¡Has añadido {cantidad_aporte:.2f} € a '{meta_elegida}'!")
                    st.rerun()
            else:
                st.write("Crea primero una hucha a la izquierda para poder ingresar dinero.")

    st.markdown("---")
    st.subheader("Mis Huchas Activas")
    
    df_metas_actual = db.get_data("metas_ahorro")
    
    if not df_metas_actual.empty:
        for i in range(0, len(df_metas_actual), 2):
            cols_meta = st.columns(2)
            for j in range(2):
                if i + j < len(df_metas_actual):
                    meta = df_metas_actual.iloc[i + j]
                    m_id = meta['id']
                    m_nombre = meta['nombre']
                    m_obj = meta['objetivo']
                    m_act = meta['actual']
                    
                    pct = min(m_act / m_obj, 1.0) if m_obj > 0 else 0
                    
                    with cols_meta[j]:
                        with st.container(border=True):
                            st.markdown(f"### 🎯 {m_nombre}")
                            st.metric("Progreso actual", f"{m_act:.2f} € / {m_obj:.2f} €", f"{pct*100:.1f}%")
                            st.progress(pct)
                            
                            if m_act >= m_obj:
                                st.balloons()
                                st.success("🎉 ¡Objetivo conseguido!")
                                
                            if st.button("🗑️ Eliminar hucha", key=f"del_meta_{m_id}"):
                                db.delete_meta_ahorro(m_id)
                                st.rerun()
    else:
        st.info("No tienes ninguna hucha activa.")

# --- PESTAÑA 4: TENDENCIAS ---
with tab4:
    st.subheader("Análisis Histórico y Tendencias")
    if not df_movimientos.empty:
        df_resumen = df_movimientos.pivot_table(index='periodo', columns='tipo', values='cantidad', aggfunc='sum', fill_value=0).reset_index()
        if 'Ingreso' not in df_resumen.columns: df_resumen['Ingreso'] = 0.0
        if 'Gasto' not in df_resumen.columns: df_resumen['Gasto'] = 0.0
        
        df_resumen['Balance Mensual'] = df_resumen['Ingreso'] - df_resumen['Gasto']
        df_resumen['Patrimonio Acumulado'] = df_resumen['Balance Mensual'].cumsum()
        
        st.markdown("#### 📈 Evolución del Ahorro (Patrimonio Acumulado)")
        fig_ahorro = px.line(df_resumen, x='periodo', y='Patrimonio Acumulado', markers=True)
        fig_ahorro.update_traces(line_color='#2ecc71', fill='tozeroy')
        st.plotly_chart(fig_ahorro, use_container_width=True)

        st.markdown("---")
        st.markdown("#### 📊 Comparativa de Gastos por Mes")
        df_solo_gastos = df_movimientos[df_movimientos['tipo'] == 'Gasto']
        if not df_solo_gastos.empty:
            df_gastos_hist = df_solo_gastos.groupby(['periodo', 'categoria'])['cantidad'].sum().reset_index()
            fig_gastos = px.bar(df_gastos_hist, x='periodo', y='cantidad', color='categoria')
            st.plotly_chart(fig_gastos, use_container_width=True)
        else:
            st.info("Aún no tienes gastos registrados.")
    else:
        st.info("Añade movimientos para generar tus gráficas históricas.")

# --- PESTAÑA 5: REGISTRO GENERAL ---
with tab5:
    st.subheader("Nuevo Movimiento Financiero")
    with st.form("form_movimiento", clear_on_submit=True):
        m_tipo = st.radio("Tipo de movimiento", ["Gasto", "Ingreso"], horizontal=True)
        m_fecha = st.date_input("Fecha", datetime.date.today())
        
        col_c, col_p = st.columns([2, 1])
        with col_c: m_conc = st.text_input("Concepto")
        with col_p: m_metodo = st.selectbox("Método de Pago", METODOS_PAGO)
        
        opcion_cat = st.selectbox("Categoría", CATEGORIAS_DROPDOWN)
        m_cat_custom = st.text_input("Escribe la nueva categoría (Solo si elegiste 'Otra')")
        
        m_cant = st.number_input("Cantidad (€)", min_value=0.0, format="%.2f")
        m_notas = st.text_area("Notas opcionales")
        
        if st.form_submit_button("Guardar Movimiento"):
            categoria_final = m_cat_custom if opcion_cat == "Otra (Personalizada)" and m_cat_custom else opcion_cat
            db.add_movimiento(m_fecha.strftime("%Y-%m-%d"), m_tipo, categoria_final, m_conc, m_cant, m_metodo, m_notas)
            st.success("Movimiento registrado correctamente.")
            st.rerun()

# --- PESTAÑA 6: HISTORIAL ---
with tab6:
    st.subheader("Historial de Movimientos")
    if not df_movimientos.empty:
        periodos_historial = ["Todos los meses"] + sorted(list(df_movimientos['periodo'].dropna().unique()), reverse=True)
        
        def formatear_mes_historial(val):
            if val == "Todos los meses": return val
            y, m = val.split('-')
            return f"{MESES[int(m)-1]} {y}"
            
        col_filtro, col_descarga = st.columns([1, 1])
        with col_filtro:
            filtro_mes = st.selectbox("📅 Filtrar por mes:", options=periodos_historial, format_func=formatear_mes_historial)
            
        if filtro_mes == "Todos los meses":
            df_mostrar = df_movimientos.copy()
            nombre_archivo = "historial_completo.csv"
        else:
            df_mostrar = df_movimientos[df_movimientos['periodo'] == filtro_mes]
            nombre_archivo = f"historial_{filtro_mes}.csv"
            
        df_limpio = df_mostrar.sort_values('fecha', ascending=False).drop(columns=['periodo'])
        
        with col_descarga:
            st.markdown("<br>", unsafe_allow_html=True) 
            csv = df_limpio.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Descargar datos filtrados (CSV)", data=csv, file_name=nombre_archivo, mime='text/csv', use_container_width=True)
            
        st.dataframe(df_limpio, use_container_width=True, hide_index=True)
    else:
        st.write("Aún no hay movimientos registrados.")

# --- PESTAÑA 7: BACKUP E IMPORTACIÓN ---
with tab7:
    st.subheader("Gestión de la Base de Datos")
    st.write("Nota: Al usar Turso en la nube, los datos se almacenan de forma segura de manera remota. Puedes usar la pestaña de Historial para descargar tus datos en formato CSV en cualquier momento.")
    
    if os.path.exists(db.DB_NAME):
        with open(db.DB_NAME, "rb") as f:
            db_bytes = f.read()
        st.download_button("Descargar Copia de Seguridad Local (.db)", data=db_bytes, file_name=f"backup_finanzas_{datetime.date.today()}.db", mime="application/octet-stream")
