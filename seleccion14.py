import streamlit as st

def cargar_servicios(archivo):
    """Carga los servicios desde el archivo y los organiza por especialidad."""
    servicios_por_especialidad = {}
    with open(archivo, 'r') as f:
        for linea in f:
            partes = linea.strip().split('|')
            if len(partes) != 3:
                st.warning(f"Línea mal formateada: {linea.strip()}")
                continue

            clave, nombre, especialidad = partes
            if especialidad not in servicios_por_especialidad:
                servicios_por_especialidad[especialidad] = []

            servicios_por_especialidad[especialidad].append(f"{clave} - {nombre}")
    return servicios_por_especialidad

# Cargar los servicios desde el archivo
archivo_servicios = "SERVICIOS.txt"
servicios_por_especialidad = cargar_servicios(archivo_servicios)

# Inicializar el estado de los servicios seleccionados si no existe
if "seleccionados" not in st.session_state:
    st.session_state["seleccionados"] = set()

# Título de la aplicación
st.title("Selección de Servicios Médicos")

# Menú desplegable para seleccionar la especialidad
especialidades = list(servicios_por_especialidad.keys())
especialidad_seleccionada = st.selectbox("Seleccione la especialidad", especialidades)

# Mostrar los servicios disponibles con checkboxes para selección
st.subheader("Servicios Disponibles:")
for servicio in servicios_por_especialidad.get(especialidad_seleccionada, []):
    seleccionado = servicio in st.session_state["seleccionados"]
    if st.checkbox(servicio, value=seleccionado, key=f"chk_disp_{servicio}"):
        st.session_state["seleccionados"].add(servicio)
    else:
        st.session_state["seleccionados"].discard(servicio)

# Mostrar los servicios seleccionados con checkboxes para eliminación directa
st.subheader("Servicios Seleccionados:")
for servicio in list(st.session_state["seleccionados"]):
    col1, col2 = st.columns([0.9, 0.1])
    with col1:
        if not st.checkbox(servicio, value=True, key=f"chk_sel_{servicio}"):
            st.session_state["seleccionados"].remove(servicio)

# Botón para confirmar la selección final
if st.button("Confirmar Selección"):
    if st.session_state["seleccionados"]:
        st.success(f"Selección final: {', '.join(st.session_state['seleccionados'])}")
        # Limpiar la lista después de confirmar
        st.session_state["seleccionados"].clear()
    else:
        st.warning("No ha seleccionado ningún servicio.")

