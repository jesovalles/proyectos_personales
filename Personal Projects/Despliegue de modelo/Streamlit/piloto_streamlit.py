import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import time
from streamlit_extras.metric_cards import style_metric_cards
import matplotlib.pyplot as plt
import plotly.graph_objs as go

########### CONFIGURACION DE LA PAGINA #################
st.set_page_config(page_title="Inmel Ingeniería", page_icon="inmel.ico", layout="wide")
st.header("Analítica de datos - Inmel Company")

# carga de CSS personalizado
try:
    with open('style.css') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("Archivo 'style.css' no encontrado.")

################# CARGA DE DATOS #######################
try:
    df = pd.read_excel('C:\\Users\\jesus.ovalles\\Proyectos\\Streamlit\\data.xlsx')
except FileNotFoundError:
    st.error("Archivo 'data.xlsx' no encontrado.")
    st.stop()

# Primero configuramos la barra lateral con el menú y los filtros
with st.sidebar:
    selected = option_menu(
        menu_title="Menú Principal",
        options=["Home", "Progress"],
        icons=["house", "eye"],
        menu_icon="cast",
        default_index=0
    )
    
    st.header("Panel de filtros:")
    with st.expander("Pulsa para expandir:", expanded=True):
        # filtro de region
        region = st.multiselect(
            "Selecciona la región:",
            options=df["Region"].unique(),
            default=[]
        )
        # filtro de zona
        location = st.multiselect(
            "Selecciona la zona:",
            options=df["Location"].unique(),
            default=[]
        )
        # filtro de materiales
        construction = st.multiselect(
            "Selecciona el material empleado:",
            options=df["Construction"].unique(),
            default=[]
        )
    
    # Mostrar logo en la barra lateral
    try:
        st.image("logo.jpg", caption="")
    except FileNotFoundError:
        st.warning("Archivo 'logo1.png' no encontrado.")

# filtrar datos del df
if not region and not location and not construction:
    df_selection = df  # mostrar todo el df si no hay filtros aplicados
else:
    df_selection = df[
        (df["Region"].isin(region) if region else True) &
        (df["Location"].isin(location) if location else True) &
        (df["Construction"].isin(construction) if construction else True)
    ]

def Home():
    ###### DATASET ######
    with st.expander("Visualización del dataset"):
        showData = st.multiselect(
            'Seleccionar columnas a visualizar (Opcional):',
            df_selection.columns,
            default=[]
        )
        if showData:
            st.dataframe(df_selection[showData], use_container_width=True, hide_index=True)
        else:
            st.dataframe(df_selection, use_container_width=True, hide_index=True)
    
    #### METRICAS #####
    total_investment = df_selection['Investment'].sum()
    investment_mode = df_selection['Investment'].mode()
    investment_mean = df_selection['Investment'].mean()
    investment_median = df_selection['Investment'].median()
    rating = df_selection['Rating'].sum()
    # manejo de múltiples modos
    if not investment_mode.empty:
        investment_mode = investment_mode.iloc[0]
    else:
        investment_mode = 0

    ##### TARJETAS ##########
    total1, total2, total3, total4, total5 = st.columns(5, gap='small')
    with total1:
        st.info('Suma Invertida', icon="💰")
        st.metric(label="Sum TZS", value=f"{total_investment:,.0f}")

    with total2:
        st.info('Mayor inversión', icon="💰")
        st.metric(label="Mode TZS", value=f"{investment_mode:,.0f}")

    with total3:
        st.info('Promedio invertido', icon="💰")
        st.metric(label="Average TZS", value=f"{investment_mean:,.0f}")

    with total4:
        st.info('Ganancias', icon="💰")
        st.metric(label="Median TZS", value=f"{investment_median:,.0f}")

    with total5:
        st.info('Ratings', icon="💰")
        st.metric(label="Rating", value=numerize(rating), help=f"Total Rating: {rating}")
    
    # Actualizar los colores de las tarjetas a tonos rojos
    style_metric_cards(
        background_color="#FFFFFF",
        border_left_color="#FF4C4C",
        border_color="#FF1A1A",
        box_shadow="#FF6666"
    )

    ##### HISTORIGRAMA ########
    with st.expander("Distribución de las inversiones"):
        fig, ax = plt.subplots(figsize=(6, 3))
        df_selection['Investment'].hist(ax=ax, color='#FF4C4C', zorder=2, rwidth=0.9)
        st.pyplot(fig)

def graphs():
    # Inversión por tipo de negocio
    investment_by_business_type = (
        df_selection.groupby(by=["BusinessType"]).count()[["Investment"]].sort_values(by="Investment")
    )
    fig_investment = px.bar(
        investment_by_business_type,
        x="Investment",
        y=investment_by_business_type.index,
        orientation="h",
        title="<b> Inversión por Tipo de negocio </b>",
        color_discrete_sequence=["#FF0000"]*len(investment_by_business_type),
        template="plotly_white",
    )

    fig_investment.update_traces(text=investment_by_business_type["Investment"], textposition="auto", textangle=0)

    fig_investment.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
    )

    # Inversión por estado
    investment_state = df_selection.groupby(by=["State"]).count()[["Investment"]]
    fig_state = px.line(
        investment_state,
        x=investment_state.index,
        y="Investment",
        orientation="v",
        title="<b> Inversión por Estado </b>",
        color_discrete_sequence=["#FF0000"]*len(investment_state),
        template="plotly_white",
        markers=True,
    )
    fig_state.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=False)
    )

    # Mostrar gráficos
    left, right, center = st.columns(3)
    with left:
        st.plotly_chart(fig_state, use_container_width=True)
    with right:
        st.plotly_chart(fig_investment, use_container_width=True)
    with center:
        # Gráfico de pastel
        fig = px.pie(
            df_selection, 
            values='Rating', 
            names='State', 
            title='Ratings por Región', 
            color_discrete_sequence=px.colors.sequential.Reds[::-1]
        )
        fig.update_layout(legend_title="Regions", legend_y=0.9)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)

def Progressbar():
    st.markdown(
        """<style>
        .stProgress > div > div > div > div { 
            background-image: linear-gradient(to right, #99ff99 , #FFFF00)
        }
        </style>""",
        unsafe_allow_html=True,
    )
    target = 3000000000
    current = df_selection["Investment"].sum()
    percent = min(round((current / target) * 100), 100)

    if percent >= 100:
        st.subheader("¡Objetivo alcanzado! 🎉")
    else:
        st.write(f"Tienes **{percent}%** de **{numerize(target)} TZS**")
        st.progress(percent, text="Porcentaje de Objetivo")

# Aplicar estilos para ocultar elementos de Streamlit
hide_st_style = """ 
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# Manejo de la navegación
if selected == "Home":
    Home()
    graphs()
elif selected == "Progress":
    Progressbar()
    graphs()

# Gráfico de caja al final
st.subheader('Distribución por Cuartíles')
feature_y = st.selectbox('Seleccionar categoría para visualizar la distribución por cuartíles', df_selection.select_dtypes("number").columns)
fig2 = go.Figure(
    data=[go.Box(x=df_selection['BusinessType'], y=df_selection[feature_y], marker_color='red')],
    layout=go.Layout(
        title=go.layout.Title(text="Inversión por Tipo de negocio y Cuartíl"),
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        font=dict(color='#000000'),
    )
)
st.plotly_chart(fig2, use_container_width=True)