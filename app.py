import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

st.set_page_config(page_title="Clasificador de Género por Correo", layout="centered")
st.title("👤 Clasificador de Género por Correo Electrónico")

st.markdown("Sube un archivo .CSV con una columna llamada **Email**. El sistema extraerá el nombre del correo y asignará un género basado en un diccionario.")

@st.cache_data
def cargar_diccionario():
    df = pd.read_csv("forenames.csv")
    df = df.drop_duplicates(subset="forename")
    return df[["forename", "gender"]]

diccionario = cargar_diccionario()

archivo = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if archivo:
    try:
        df = pd.read_csv(archivo, encoding="utf-8", on_bad_lines="skip")

        # Normalizar encabezados
        df.columns = df.columns.str.strip().str.lower()

        if "email" not in df.columns:
            st.error("El archivo debe tener una columna llamada 'Email'")
            st.stop()
        else:
            # Extraer nombre
            df["nombre_extraido"] = df["email"].apply(lambda x: re.split(r"[._\\-]", x.split("@")[0])[0].lower())
            df_genero = df.merge(diccionario, how="left", left_on="nombre_extraido", right_on="forename")
            df_genero["gender"] = df_genero["gender"].fillna("No identificado")

            st.success("Resultado del análisis")
            st.dataframe(df_genero[["email", "gender"]])

            # Gráfico de resumen
            genero_counts = df_genero["gender"].value_counts()
            fig, ax = plt.subplots()
            genero_counts.plot(kind='bar', ax=ax, color='skyblue')
            ax.set_title("Distribución de Géneros Detectados")
            ax.set_xlabel("Género")
            ax.set_ylabel("Cantidad")
            st.pyplot(fig)

            # Botón de descarga
            csv_final = df_genero[["email", "gender"]].to_csv(index=False)
            st.download_button("📥 Descargar resultados", csv_final, file_name="genero_detectado.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
