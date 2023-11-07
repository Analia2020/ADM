import streamlit as st
import pandas as pd
import os
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()
from datetime import date

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

# Crear un widget de selección para elegir una estación y género
estacion_seleccionada = st.sidebar.selectbox("Selecciona una estación", opciones_estaciones)

st.sidebar.header('Género')
opciones_genero = ["Tod@s"] + list(df_unif['género'].unique())
genero_seleccionado = st.sidebar.selectbox("Selecciona una opción", opciones_genero)


st.sidebar.header('Mes')
opciones_mes = ["Todos"] + sorted(list(df_unif['month_o'].unique()), reverse=False)
mes_seleccionado = st.sidebar.selectbox("Selecciona una opción", opciones_mes)

# Aplicar filtros
if estacion_seleccionada == "Todas" and genero_seleccionado == "Tod@s":
    df_filtrado = df_unif  # Sin filtro
else:
    df_filtrado = df_unif

if estacion_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado['nombre_estacion_origen'] == estacion_seleccionada]

if genero_seleccionado != "Tod@s":
    df_filtrado = df_filtrado[df_filtrado['género'] == genero_seleccionado]

if mes_seleccionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado['month_o'] == mes_seleccionado]

result = df_filtrado.groupby(['nombre_estacion_origen']).agg({'id_recorrido': 'count'}
                                                             ).reset_index().iloc[:10, :]
result_est = result["nombre_estacion_origen"].tolist()

df_filtrado_top10 = df_unif[df_unif['nombre_estacion_origen'].isin(result_est)]


# Mostrar el mapa utilizando Plotly Graph Objects

fig = go.Figure(go.Scattermapbox(
    lat=df_filtrado['lat_estacion_origen'].unique(),
    lon=df_filtrado['long_estacion_origen'].unique(),
    mode='markers',
    marker=dict(size=9, color = "seagreen"),
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

# Crear estaciones por meses
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

col1, col2, col3 = st.columns(3)
col1.metric("Tiempo promedio de uso (min)", df_filtrado.diferencia_minutos.mean().round(2))
col2.metric("Mediana de tiempo de uso (min)", df_filtrado.diferencia_minutos.median().round(2))
col3.metric("Tiempo mínimo de uso (min)", df_filtrado.diferencia_minutos.min().round(2))

# # if estacion_seleccionada == "Todas" and genero_seleccionado == "Tod@s":
# #     result = df_filtrado.groupby(['nombre_estacion_origen']).agg({'id_recorrido': 'count'}).reset_index().iloc[:10, :]
# #     result_est = result["nombre_estacion_origen"].tolist()
# #     df_filtrado_top10 = df_unif[df_unif['nombre_estacion_origen'].isin(result_est)]
# # elif:
# #     df_filtrado_top10 = df_filtrado

plt.rcParams["figure.figsize"] = [14, 10]
plt.rcParams["figure.autolayout"] = True

# Crear el boxplot y asignarlo a una variable
# Crear un objeto de figura para el boxplot
fig = go.Figure()

# Agregar el boxplot a la figura
color_cajas = '#228B22'  # Verde oscuro
color_bordes = 'black'
fig.add_trace(go.Box(
    x=df_filtrado_top10['nombre_estacion_origen'],  # Datos para el eje x
    y=df_filtrado_top10['diferencia_minutos'],  # Datos para el eje y
    marker_color='#77DD77',  # Color verde pastel más oscuro
    boxmean=True,
    #boxpoints='all',  # Mostrar todos los puntos
    fillcolor=color_cajas,  # Color de relleno de las cajas
    line=dict(color=color_bordes),  # Color de los bordes
))  # Mostrar la línea de la mediana

fig.update_yaxes(range=[0, 250])
# Configurar el diseño del gráfico
fig.update_layout(
    yaxis_title="Diferencia en Minutos",
    title="Boxplot de Diferencia en Minutos por Estación de Origen"
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig, use_container_width=True)


#Viajes por meses y dias
st.markdown("**Cantidad de viajes segun meses del año 2022 y dias de la semana**")

df_unif_dias = df_filtrado[['id_recorrido','dias_espanol', 'month_espanol']]

tabla_pivot_dia_semana= pd.pivot_table(df_unif_dias, values=['id_recorrido'],
                                          index='month_espanol', columns='dias_espanol',
                                          aggfunc={'id_recorrido': 'count'},
                                          margins=True,
                                          margins_name='Total')
tabla_pivot_dia_semana = tabla_pivot_dia_semana.round(2)

tabla_pivot_dia_semana = tabla_pivot_dia_semana.rename_axis("Meses")
tabla_pivot_dia_semana.columns = tabla_pivot_dia_semana.columns.droplevel()
st.dataframe(tabla_pivot_dia_semana)

dias = tabla_pivot_dia_semana.columns
cuenta_id_recorrido_dia = tabla_pivot_dia_semana.loc["Total"].drop("Total")

fig_bar = go.Figure(data=go.Bar(x=dias, y=cuenta_id_recorrido_dia, marker=dict(color='seagreen'),
                                ))

fig_bar.update_layout(title="Cantidad de recorridos por dia de semana", 
                      xaxis_title="Dia de semana", yaxis_title="Cantidad",
                      )
st.plotly_chart(fig_bar)


#Viajes por horas y dias de semana
df_unif_horas= df_filtrado[['id_recorrido','dias_espanol', 'hora']]

st.markdown("**Cantidad de viajes según horas del día y días de la semana**")
df_m = pd.crosstab( df_unif_horas.hora, df_unif_horas.dias_espanol,)
fig, ax = plt.subplots(figsize=(16,10))
cmap= sns.light_palette("seagreen", as_cmap=True)
sns.heatmap(df_m, cmap=cmap, annot=True, fmt = '.0f',  vmin=0, vmax=8000)
plt.yticks(rotation=0)
ax.set_xlabel(None)
ax.set_ylabel("Horas del dia")
st.pyplot(plt)
