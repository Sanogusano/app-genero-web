import streamlit as st
import pandas as pd
import re
import matplotlib.pyplot as plt

st.set_page_config(page_title="Clasificador de Género por Nombre", layout="centered")
st.title("👤 Clasificador de Género por Nombre")

st.markdown("Sube un archivo .CSV con una columna llamada **Nombre**. El sistema asignará un género usando un diccionario de nombres.")

@st.cache_data
def cargar_diccionario():
    file_id = "1lRgjBBj9GN-Et3y0aOPBULGl3wBuqAfw"
    url = f"https://drive.google.com/uc?id={file_id}"
    df = pd.read_csv(url)
    df = df.drop_duplicates(subset="forename")
    return df[["forename", "gender"]]

diccionario = cargar_diccionario()

archivo = st.file_uploader("📂 Sube tu archivo CSV", type=["csv"])

if archivo:
    try:
        df = pd.read_csv(archivo, encoding="utf-8", sep=";", on_bad_lines="skip")
        df.columns = df.columns.str.strip().str.lower()

        if "nombre" not in df.columns:
            st.error("El archivo debe tener una columna llamada 'Nombre'")
            st.stop()

        # Limpiar nombre y cruzar con diccionario
        df["nombre_limpio"] = df["nombre"].str.lower().str.strip()
        df["nombre_limpio"] = df["nombre_limpio"].str.replace(r"[^a-záéíóúüñ ]", "", regex=True)
        df_genero = df.merge(diccionario, how="left", left_on="nombre_limpio", right_on="forename")
        df_genero["gender"] = df_genero["gender"].fillna("No identificado")

        st.success("✅ Resultado del análisis")
        st.dataframe(df_genero[["nombre", "gender"]])

        # Gráfico de resumen
        genero_counts = df_genero["gender"].value_counts()
        fig, ax = plt.subplots()
        genero_counts.plot(kind='bar', ax=ax, color='mediumslateblue')
        ax.set_title("Distribución de Géneros Detectados")
        ax.set_xlabel("Género")
        ax.set_ylabel("Cantidad")
        st.pyplot(fig)

        # Botón de descarga
        csv_final = df_genero[["nombre", "gender"]].to_csv(index=False)
        st.download_button("📥 Descargar resultados", csv_final, file_name="genero_detectado.csv", mime="text/csv")

    except Exception as e:
        st.error(f"Error al leer el archivo: {e}")
