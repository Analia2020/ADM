import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

# Cargar los datos desde el archivo parquet
archivo = 'trip_unif_2022.parquet' 
df_unif = pd.read_parquet(archivo)

# Filtrar y limpiar los datos
#ubicaciones = df_unif[['nombre_estacion_origen', 'lat_estacion_origen', 'long_estacion_origen']].drop_duplicates().dropna()

# Crear un título para la aplicación


st.title("Revolución de las bicicletas públicas")
st.sidebar.image("real_bikes.jpg", width=500,  use_column_width=False)
st.sidebar.header('Estaciones de origen')

# Obtener la lista de estaciones únicas, incluyendo "Todas"
opciones_estaciones = ["Todas"] + list(df_unif['nombre_estacion_origen'].unique())

# Crear un widget de selección para elegir una estación y genero
estacion_seleccionada = st.sidebar.selectbox("Selecciona una estación", opciones_estaciones)


st.sidebar.header('Género')
opciones_genero = ["Tod@s"] + list(df_unif['género'].unique())
genero_seleccionado = st.sidebar.selectbox("Selecciona una opción", opciones_genero)

# Aplicar filtros
if estacion_seleccionada == "Todas" and genero_seleccionado == "Tod@s":
    df_filtrado = df_unif  # Sin filtro
elif estacion_seleccionada == "Todas":
    df_filtrado = df_unif[df_unif['género'] == genero_seleccionado]
elif genero_seleccionado == "Tod@s":
    df_filtrado = df_unif[df_unif['nombre_estacion_origen'] == estacion_seleccionada]
else:
    df_filtrado = df_unif[(df_unif['nombre_estacion_origen'] == estacion_seleccionada) & (df_unif['género'] == genero_seleccionado)]


# Mostrar el mapa utilizando Plotly Graph Objects

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
# Lista de meses en español en el orden deseado


# Crear la tabla pivot
tabla_pivot_mes_estacion = pd.pivot_table(df_filtrado, values=['id_recorrido'],
                                          index='nombre_estacion_origen', columns='month_espanol',
                                          aggfunc={'id_recorrido': 'count'},
                                          margins=True,
                                          margins_name='Total')

 
# Ordenar las columnas en el DataFrame
 
tabla_pivot_mes_estacion = tabla_pivot_mes_estacion.round(2)

tabla_pivot_mes_estacion = tabla_pivot_mes_estacion.rename_axis("Estación")
tabla_pivot_mes_estacion.columns = tabla_pivot_mes_estacion.columns.droplevel()

# Mostrar la tabla pivot

st.markdown("**Cantidad de viajes segun Estaciones por Meses del año 2022**")
st.dataframe(tabla_pivot_mes_estacion)

# Crear un gráfico de línea con meses en el eje X y la cuenta de id_recorrido en el eje Y


# Obtener los nombres de los meses desde la última fila de la tabla pivot

meses = tabla_pivot_mes_estacion.columns

cuenta_id_recorrido = tabla_pivot_mes_estacion.loc["Total"].drop("Total")

fig_linea = go.Figure(data=go.Scatter(x=meses, y=cuenta_id_recorrido, mode='lines+markers'))

fig_linea.update_layout(title="Cantidad de recorridos por mes que se inician en las estaciones", xaxis_title="Mes", yaxis_title="Cantidad")
st.plotly_chart(fig_linea)


# Crear la tabla pivot
st.markdown("**Cantidad de viajes segun meses del año 2022 y dias de la semana**")

df_unif_dias = df_unif[['id_recorrido','dias_espanol', 'month_espanol']]
tabla_pivot_dia_semana= pd.pivot_table(df_unif_dias, values=['id_recorrido'],
                                          index='month_espanol', columns='dias_espanol',
                                          aggfunc={'id_recorrido': 'count'},
                                          margins=True,
                                          margins_name='Total')
tabla_pivot_dia_semana = tabla_pivot_dia_semana.round(2)

tabla_pivot_dia_semana = tabla_pivot_dia_semana.rename_axis("Meses")
tabla_pivot_dia_semana.columns = tabla_pivot_dia_semana.columns.droplevel()
st.dataframe(tabla_pivot_dia_semana)

# # dias = tabla_pivot_dia_semana.columns
# # cuenta_id_recorrido_dia = tabla_pivot_dia_semana.loc["Total"].drop("Total")



# # # Suponiendo que ya tienes la tabla pivot tabla_pivot_dia_semana creada y las variables "dias" y "cuenta_id_recorrido_dia" definidas
# # dias = [dia for dia in tabla_pivot_dia_semana.columns if dia != "Total"]

# # fig_barras = px.bar(x=dias, y=cuenta_id_recorrido_dia, color=tabla_pivot_dia_semana.columns, title="Barplot de Recorridos por Día de la Semana")
# # fig_barras.update_layout(xaxis_title="Día de la Semana", yaxis_title="Cantidad de Recorridos")
 

# # # Mostrar el gráfico
# # st.plotly_chart(fig_barras)


## Horas del dia


