import streamlit as st
from datetime import datetime, timedelta
from fpdf import FPDF

def verificar_disponibilidad(fecha_str, hora_str):
    """Verifica si una fecha y hora están disponibles en reservaciones.txt."""
    with open('reservaciones.txt', 'r') as file:
        for linea in file:
            try:
                fecha_reservada, hora_reservada, *_ = linea.strip().split("|")
                if fecha_reservada == fecha_str and hora_reservada == hora_str:
                    return False  # La fecha y hora ya están ocupadas
            except ValueError:
                st.write(f"[Depuración] Línea malformada: {linea}")
    return True  # Si no se encontró la fecha y hora, está disponible

def encontrar_proxima_disponibilidad(dias_preferidos, turno):
    """Encuentra la próxima disponibilidad según los días y turno preferidos."""
    fecha_actual = datetime.today()
    intentos = 0
    dias_semana = {"lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3, "viernes": 4}
    dias_preferidos_numeros = [dias_semana[dia.lower()] for dia in dias_preferidos]

    while intentos < 365 * 2:
        dia_semana_actual = fecha_actual.weekday()
        if dia_semana_actual in dias_preferidos_numeros:
            hora_inicial = 7 if turno == 'Mañana' else 12
            for hora in range(hora_inicial, hora_inicial + 6):
                hora_str = f"{hora:02d}:00"
                fecha_str = fecha_actual.strftime('%Y-%m-%d')
                st.write(f"[Depuración] Intentando: {fecha_str} a las {hora_str}")
                if verificar_disponibilidad(fecha_str, hora_str):
                    return fecha_str, hora_str
        fecha_actual += timedelta(days=1)
        intentos += 1
    raise Exception("No se encontró disponibilidad en los próximos dos años.")

def registrar_cita(fecha, hora, expediente, paciente, servicio):
    with open('reservaciones.txt', 'a') as f:
        f.write(f"{fecha}|{hora}|{expediente}|{paciente}|{servicio}\n")

def generar_pdf(paciente, usuario, expediente, citas_asignadas):
    pdf = FPDF()
    pdf.add_page()
    pdf.image('escudo_COLOR.jpg', 10, 8, 33)
    pdf.set_font("Arial", size=12)
    pdf.ln(40)
    pdf.cell(200, 10, txt=f"Nombre del Paciente: {paciente}", ln=True, align="L")
    pdf.cell(200, 10, txt=f"Nombre del Usuario: {usuario}", ln=True, align="L")
    pdf.ln(10)

    for i, cita in enumerate(citas_asignadas, start=1):
        fecha, hora, estudio, clinica = cita
        pdf.cell(200, 10, txt=f"Fecha: {fecha}", ln=True)
        pdf.cell(200, 10, txt=f"Horario: {hora}", ln=True)
        pdf.cell(200, 10, txt=f"Estudio: {estudio}", ln=True)
        pdf.cell(200, 10, txt=f"Clínica: {clinica}", ln=True)
        pdf.ln(5)
        if i % 4 == 0:
            pdf.add_page()
            pdf.image('escudo_COLOR.jpg', 10, 8, 33)
            pdf.set_font("Arial", size=12)
            pdf.ln(40)
            pdf.cell(200, 10, txt=f"Nombre del Paciente: {paciente}", ln=True, align="L")
            pdf.cell(200, 10, txt=f"Nombre del Usuario: {usuario}", ln=True, align="L")
            pdf.ln(10)
#            pdf.cell(0, 10, f"Página {pdf.page_no()}", align='C')

    pdf_file = f"citas_{expediente}.pdf"
    pdf.output(pdf_file)
    return pdf_file

def cargar_usuarios():
    usuarios = {}
    with open('usuarios.txt', 'r') as f:
        for linea in f:
            password, usuario = linea.strip().split('|')
            usuarios[password] = usuario
    return usuarios

st.title("Sistema de Gestión de Citas Médicas")
usuarios = cargar_usuarios()
password = st.text_input("Ingrese su contraseña:", type="password")

if password in usuarios:
    usuario = usuarios[password]
    st.success(f"Bienvenido(a), {usuario}")
    expediente = st.text_input("Número de Expediente:")
    paciente = st.text_input("Nombre del Paciente:")
    turno = st.selectbox("Seleccione el turno:", ["Mañana", "Tarde"])
    dias_preferidos = st.multiselect(
        "Días preferentes:", ["lunes", "martes", "miércoles", "jueves", "viernes"]
    )
    servicios_disponibles = [
        "060102|Antígeno-anticuerpo VIH|BANCO DE SANGRE",
        "060103|Antígeno de superficie y anticuerpo core del virus de la hepatitis B|BANCO DE SANGRE",
        "000000|CARDIONEUMOLOGÍA|BANCO DE SANGRE",
        "082001|Cateterismo derecho con prueba farmacológica|BANCO DE SANGRE",
        "082014|Cateterismo derecho|BANCO DE SANGRE",
        "082002|Broncoscopía estándar|BANCO DE SANGRE",
        "082003|Espirometría simple|BANCO DE SANGRE",
        "082004|Difusión|BANCO DE SANGRE",
        "082005|Sonda pleural, colocación|BANCO DE SANGRE",
        "082007|Biopsia por aspiración|BANCO DE SANGRE",
        "082015|Espirometría con pletismografía|BANCO DE SANGRE",
        "015003|Curación|CONSULTA EXTERNA",
        "015008|Consulta externa, primera vez|CONSULTA EXTERNA",
        "015009|Consulta externa, subsecuente|CONSULTA EXTERNA",
        "015010|Interconsulta a otras instituciones|CONSULTA EXTERNA",
        "015011|Preconsulta, incluye placa de tórax|CONSULTA EXTERNA",
        "015012|Consulta externa, interconsulta|CONSULTA EXTERNA",
        "050010|Ecocardiograma transtorácico bidimensional|ECOCARDIOGRAFÍA",
        "050011|Ecocardiograma transesofágico bidimensional|ECOCARDIOGRAFÍA",
        "050012|Ecocardiograma Fetal|ECOCARDIOGRAFÍA",
        "050115|Ecocardiograma transtorácico con estrés farmacologico|ECOCARDIOGRAFÍA"
    ]    
    servicios_seleccionados = st.multiselect("Seleccione los servicios:", servicios_disponibles)

    if st.button("Asignar Citas"):
        try:
            citas_asignadas = []
            for servicio in servicios_seleccionados:
                codigo, estudio, clinica = servicio.split("|")
                fecha, hora = encontrar_proxima_disponibilidad(dias_preferidos, turno)
                registrar_cita(fecha, hora, expediente, paciente, servicio)
                citas_asignadas.append((fecha, hora, estudio, clinica))

            pdf_file = generar_pdf(paciente, usuario, expediente, citas_asignadas)
            st.success("Citas asignadas correctamente.")
            st.download_button("Descargar PDF", data=open(pdf_file, "rb"), file_name=pdf_file)
        except Exception as e:
            st.error(f"Error: {str(e)}")
else:
    st.error("Contraseña incorrecta.")

