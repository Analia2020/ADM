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
st.markdown("""Las bicicletas públicas son una opción de transporte sostenible, saludable y económica.



A continuación, se presentan algunas preguntas que se pueden responder al analizar los datos del Sistema EcoBici de la Ciudad de Buenos Aires en 2022:



**Patrones de uso del sistema:**
- ¿Cómo se utilizan las bicicletas públicas?
- ¿A qué horas se utilizan más?
- ¿En qué mes son más populares?
- ¿Los fines de semana se utilizan más que entre semana?



**Ubicación de las estaciones:**
- ¿Dónde se encuentran las estaciones más utilizadas?



**Uso de las bicicletas:**
- ¿Cuánto tiempo se utilizan las bicicletas en promedio?
- ¿Cuánto tiempo se utilizan las 10 estaciones más utilizadas?



**Usuarios del sistema:**
- ¿Quiénes son los usuarios del sistema?
- ¿Cuál es su edad y sexo?
            
---         
            
            """)



# Obtener la lista de estaciones únicas, incluyendo "Todas"
opciones_estaciones = ["Todas"] + list(df_unif['nombre_estacion_origen'].unique())

# Crear un widget de selección para elegir una estación, género y mes
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
                                                             ).reset_index().sort_values(
                                                                 by='id_recorrido', ascending=False)
result_10 = result.iloc[:10, :]
result_est = result_10["nombre_estacion_origen"].tolist()

df_filtrado_top10 = df_unif[df_unif['nombre_estacion_origen'].isin(result_est)]



# Mapa utilizando Plotly Graph Objects

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

st.header("Ubicación de las estaciones de bicicletas en CABA")

# Personalizar el mapa
fig.update_layout(title=f"Estación: {estacion_seleccionada}")
fig.update_traces(
    hovertemplate='<b>Estación:</b> %{text}',  # Define el formato del hover
)

# Mostrar el mapa en Streamlit
st.plotly_chart(fig)

# Titulo
st.header("Viajes durante 2022")
# Metricas
col1, col2= st.columns(2)
col1.metric("Cantidad de viajes", len(df_filtrado.id_recorrido.unique()))
col2.metric("Cantidad de usuarios", len(df_filtrado.id_usuario_numero.unique()))

col1, col2= st.columns(2)
col1.metric("Estacion con mayor cantidad de viajes", result.nombre_estacion_origen.tolist()[0])
valor_resultado = result.nombre_estacion_origen.tolist()[-1]
# Aplicar el if
if valor_resultado == "Balboa Definitivo":
    valor_resultado = result.nombre_estacion_origen.tolist()[-2]
if valor_resultado == "Mantenimiento Barracas":
    valor_resultado = result.nombre_estacion_origen.tolist()[-3]

col2.metric("Estacion con menor cantidad de viajes", valor_resultado)

# Crear df de estaciones por meses
tabla_pivot_mes_estacion = pd.pivot_table(df_filtrado, values=['id_recorrido'],
                                          index='nombre_estacion_origen', columns='month_espanol',
                                          aggfunc={'id_recorrido': 'count'},
                                          margins=True,
                                          margins_name='Total')
 
# Ordenar las columnas en el DataFrame
tabla_pivot_mes_estacion = tabla_pivot_mes_estacion.round(2)
tabla_pivot_mes_estacion = tabla_pivot_mes_estacion.rename_axis("Estación")
tabla_pivot_mes_estacion.columns = tabla_pivot_mes_estacion.columns.droplevel()

meses = tabla_pivot_mes_estacion.columns
cuenta_id_recorrido_mes = tabla_pivot_mes_estacion.loc["Total"].drop("Total")
# Grafico de linea 
fig_line = go.Figure(data=go.Scatter(x=meses, y=cuenta_id_recorrido_mes, 
                                     mode='lines+markers', line=dict(color='seagreen')))

fig_line.update_layout(
    title="Viajes por mes",
    xaxis_title="Meses",
    yaxis_title="Cantidad",
)

st.plotly_chart(fig_line)

# Mostrar la tabla pivot

st.markdown("**Viajes según Estaciones por Meses del año 2022**")
st.dataframe(tabla_pivot_mes_estacion)


#Viajes por meses y dias

df_unif_dias = df_filtrado[['id_recorrido','dias_espanol', 'month_espanol']]

tabla_pivot_dia_semana= pd.pivot_table(df_unif_dias, values=['id_recorrido'],
                                          index='month_espanol', columns='dias_espanol',
                                          aggfunc={'id_recorrido': 'count'},
                                          margins=True,
                                          margins_name='Total')
tabla_pivot_dia_semana = tabla_pivot_dia_semana.round(2)

tabla_pivot_dia_semana = tabla_pivot_dia_semana.rename_axis("Meses")
tabla_pivot_dia_semana.columns = tabla_pivot_dia_semana.columns.droplevel()


dias = tabla_pivot_dia_semana.columns
cuenta_id_recorrido_dia = tabla_pivot_dia_semana.loc["Total"].drop("Total")

# Grafico de barra por dias de semana
fig_bar = go.Figure(data=go.Bar(x=dias, y=cuenta_id_recorrido_dia, marker=dict(color='seagreen'),
                                ))

fig_bar.update_layout(title="Viajes por día de semana", 
                      xaxis_title="Día de semana", yaxis_title="Cantidad",
                      )
st.plotly_chart(fig_bar)
st.markdown("**Viajes según meses del año 2022 y días de la semana**")
st.dataframe(tabla_pivot_dia_semana)

#Viajes por horas y dias de semana
df_unif_horas= df_filtrado[['id_recorrido','dias_espanol', 'hora']]

st.markdown("**Viajes según horas del día y días de la semana**")
# Heatmap de horas y dias de semana
df_m = pd.crosstab( df_unif_horas.hora, df_unif_horas.dias_espanol,)
fig, ax = plt.subplots(figsize=(16,10))
cmap= sns.light_palette("seagreen", as_cmap=True)
sns.heatmap(df_m, cmap=cmap, annot=True, fmt = '.0f',  vmin=0, vmax=8000)
plt.yticks(rotation=0)
ax.set_xlabel(None)
ax.set_ylabel("Horas del dia")
st.pyplot(plt)

st.markdown("""
            
---       
              
            """)
# Titulo
st.header("Tiempo de uso de bicicletas")
# Metricas
col1, col2= st.columns(2)
col1.metric("Tiempo promedio de uso (min)", df_filtrado.diferencia_minutos.mean().round(2))
col2.metric("Mediana de tiempo de uso (min)", df_filtrado.diferencia_minutos.median().round(2))


col1, col2, col3 = st.columns(3)
col1.metric("Tiempo máximo de uso (min)", df_filtrado.diferencia_minutos.max().round(2))
col2.metric("Desvio standard (min)", df_filtrado.diferencia_minutos.std().round(2))
col3.metric("Tiempo mínimo de uso (min)", df_filtrado.diferencia_minutos.min().round(2))


# Crear el boxplot 
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
    yaxis_title="Minutos de uso",
    title="Tiempo de uso de bicicleta en minutos"
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig, use_container_width=True)


st.markdown("""
            
---       
              
            """)
# Titulo
st.header("Edad de los usuarios de las bicicletas públicas")

df_edad = df_filtrado.edad_usuario.value_counts()
df_edad = pd.DataFrame({'labels': df_edad.index, 'values': df_edad.values })
colors = ['#2E8B57', '#3CB371', '#20B2AA',] #'#008B8B', '#00CED1']


col1, col2= st.columns(2)
col1.metric("Promedio de edad (años)", df_filtrado.edad_usuario.mean().round(2))
col2.metric("Mediana de edad (años)", df_filtrado.edad_usuario.median().round(2))


col1, col2, col3 = st.columns(3)
col1.metric("Edad máxima (años)", df_filtrado.edad_usuario.max().round(2))
col2.metric("Desvio standard de edad (años)", df_filtrado.edad_usuario.std().round(2))
col3.metric("Edad mínima (años)", df_filtrado.edad_usuario.min().round(2))

#Treemap cantidad de viajes por edad
fig_tree = px.treemap(df_edad, path=['labels'],values='values', width=1200, height=500, title= "Cantidad de viajes por edad (años)")
fig_tree.update_layout(
   treemapcolorway = colors) #defines the colors in the treemap)
fig_tree.update_traces(
    hovertemplate='<b>Edad (años):</b> %{label}<br><b>Cantidad de viajes:</b> %{value}',  # Define el formato del hover
)

st.plotly_chart(fig_tree, use_container_width=True)