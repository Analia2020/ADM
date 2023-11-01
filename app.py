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

# Obtener la lista de estaciones únicas, incluyendo "Todas"
opciones_estaciones = ["Todas"] + list(df_unif['nombre_estacion_origen'].unique())

# Crear un widget de selección para elegir una estación
estacion_seleccionada = st.selectbox("Selecciona una estación", opciones_estaciones)

# Filtrar el DataFrame según la estación seleccionada
if estacion_seleccionada != "Todas":
    df_filtrado = df_unif[df_unif['nombre_estacion_origen'] == estacion_seleccionada]
else:
    df_filtrado = df_unif

# Mostrar el mapa utilizando Plotly Graph Objects
st.write("Mapa de Bicicletas:")
fig = go.Figure(go.Scattermapbox(
    lat=df_filtrado['lat_estacion_origen'].unique(),
    lon=df_filtrado['long_estacion_origen'].unique(),
    mode='markers',
    marker=dict(size=9),
    text=df_filtrado['nombre_estacion_origen'].unique()
))

# Configurar el estilo de OpenStreetMap
fig.update_layout(
    mapbox_style="open-street-map",
    mapbox_center={"lat": -34.6118, "lon": -58.4173},  # Coordenadas de Buenos Aires
    mapbox_zoom=10  # Ajusta el nivel de zoom según sea necesario
)

# Personalizar el mapa
fig.update_layout(title=f"Mapa de Bicicletas - Estación: {estacion_seleccionada}")

# Mostrar el mapa en Streamlit
st.plotly_chart(fig)

# Calcular la tabla pivot
tabla_pivot_mes_estacion = pd.pivot_table(df_filtrado, values=['id_recorrido'],
                                          index='nombre_estacion_origen', columns='month_o',
                                          aggfunc={'id_recorrido': 'count'},
                                          margins=True,
                                          margins_name='Total')
tabla_pivot_mes_estacion = tabla_pivot_mes_estacion.round(2)
tabla_pivot_mes_estacion.columns = tabla_pivot_mes_estacion.columns.droplevel()

# Mostrar la tabla pivot
st.write("Cantidad de viajes segun Estaciones por Meses del año 2022")
st.dataframe(tabla_pivot_mes_estacion)

