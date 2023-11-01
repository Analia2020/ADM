import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.graph_objects as go

# Cargar los datos desde el archivo parquet
archivo = 'trip_unif_2022.parquet' 
df_unif = pd.read_parquet(archivo)

# Filtrar y limpiar los datos
ubicaciones = df_unif[['nombre_estacion_origen', 'lat_estacion_origen', 'long_estacion_origen']].drop_duplicates().dropna()

# Crear un título para la aplicación
st.title("Revolucion de las bicicletas publicas")

# Crear un mapa utilizando Plotly Graph Objects y configurar el estilo de OpenStreetMap
fig = go.Figure(go.Scattermapbox(
    lat=ubicaciones['lat_estacion_origen'],
    lon=ubicaciones['long_estacion_origen'],
    mode='markers',
    marker=dict(size=9),
    text=ubicaciones['nombre_estacion_origen']
))

# Configurar el estilo de OpenStreetMap
fig.update_layout(
    mapbox_style="open-street-map",
    mapbox_center={"lat": -34.6118, "lon": -58.4173},  # Coordenadas de Buenos Aires
    mapbox_zoom=10  # Ajusta el nivel de zoom según sea necesario
)

# Personalizar el mapa
fig.update_layout(title="Mapa de Bicicletas")

# Mostrar el mapa en Streamlit
st.plotly_chart(fig)