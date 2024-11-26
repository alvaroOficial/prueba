import requests
import streamlit as st
from groq import Groq
import fitz  # PyMuPDF
from io import BytesIO

# Configura el cliente de Groq
API_KEY = "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"
client = Groq(api_key=API_KEY)

# Modelo fijo
modelo = 'llama3-8b-8192'

# Función para descargar el PDF desde Google Drive


def descargar_pdf_drive(link: str) -> BytesIO:
    """Descargar un archivo PDF desde un enlace de Google Drive."""
    # Reemplaza el link para obtener el enlace de descarga directa
    file_id = link.split('/d/')[1].split('/')[0]
    download_link = f"https://drive.google.com/uc?export=download&id={file_id}"

    # Hacer la solicitud para obtener el archivo
    response = requests.get(download_link)
    if response.status_code == 200:
        return BytesIO(response.content)
    else:
        raise Exception("No se pudo descargar el archivo desde Google Drive.")

# Función para extraer texto completo del PDF


def extraer_texto_pdf(pdf_file: BytesIO) -> str:
    texto_completo = ""
    # Usamos BytesIO como archivo en memoria
    doc = fitz.open(stream=pdf_file, filetype="pdf")

    # Extraer texto de todas las páginas
    for pagina in doc:
        texto_completo += pagina.get_text()

    return texto_completo

# Función para generar respuestas del modelo


def generate_chat_responses(chat_completion) -> str:
    """Genera respuestas carácter por carácter desde el modelo."""
    respuesta_completa = ""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            respuesta_completa += chunk.choices[0].delta.content
    return respuesta_completa

# Interfaz de usuario en Streamlit


def app():
    st.title("Chatbot Especializado TrustCoffe")

    # Caja de entrada para el enlace de Google Drive
    pdf_link = st.text_input(
        "Introduce la información:", "")

    if pdf_link:
        try:
            # Descargamos el contenido del PDF desde Google Drive
            pdf_file = descargar_pdf_drive(pdf_link)

            # Extraemos el contenido completo del PDF
            contenido_pdf = extraer_texto_pdf(pdf_file)

            # Historial de chat
            mensajes = [{"role": "system", "content": "Este es un chatbot especializado para responder preguntas relacionadas con el contenido del PDF. Puedes preguntarme cualquier cosa sobre el documento."}]

            # Caja de entrada para las preguntas del usuario
            user_input = st.text_input("Tú:", "")

            if user_input:
                # Agregar mensaje del usuario al historial
                mensajes.append({"role": "user", "content": user_input})

                try:
                    # Crear una respuesta del modelo utilizando el contenido del PDF como contexto
                    chat_completion = client.chat.completions.create(
                        model=modelo,
                        messages=mensajes +
                        [{"role": "system", "content": contenido_pdf}],
                        stream=True  # Streaming para procesar por partes
                    )

                    # Generar y mostrar la respuesta
                    respuesta_completa = generate_chat_responses(
                        chat_completion)
                    st.write(f"Chatbot: {respuesta_completa}")

                    # Agregar respuesta al historial
                    mensajes.append(
                        {"role": "assistant", "content": respuesta_completa})

                except Exception as e:
                    st.error(f"Error al generar respuesta: {e}")

        except Exception as e:
            st.error(f"Error al cargar el archivo PDF: {e}")


if __name__ == "__main__":
    app()
