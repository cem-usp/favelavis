import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap  # Import correto para Streamlit
import rasterio
from rasterio.mask import mask
import tempfile
import os
import numpy as np

# --- CONFIGURAÇÕES E VARIÁVEIS ---
st.set_page_config(layout="wide")  # Tela larga para melhor aproveitamento

# Carregar feições
gdf = gpd.read_file('data/SIRGAS_GPKG_favela.gpkg')
gdf.geometry = gdf.buffer(0)
gdf = gdf.dissolve(by='fv_nome').reset_index()

# favelas para teste
favelas_test = [
    "Heliópolis",
    "Cocaia I",
    "Paraisópolis",
    "Futuro Melhor",
    "São Remo"
]
gdf = gdf[gdf['fv_nome'].isin(favelas_test)]


# --- SIDEBAR ---
st.sidebar.title("FavelaVIS")

# Selecionar Favela
with st.sidebar.expander("Selecionar Favela", expanded=True):
    favela = st.selectbox(
        "Escolha a Favela:",
        gdf.fv_nome.to_list()
    )

# Selecionar Atributo
with st.sidebar.expander("Selecionar Atributo"):
    atributo = st.radio("Atributos:", [
        "Pavimentos",
        "Gabaritos",
        "Área construída estimada",
        "Área construída por gabarito/pavimento",
        "Área de projeção estimada",
        "CA",
        "TO",
        "Rugosidade da superfície",
        "Rugosidade do terreno",
        "Correlação entre atributos (17, 20 e 24)"
    ])

# Visualiza Mapa
with st.sidebar.expander("Visualizar Mapa"):
    tema = st.selectbox("Tema:", [
        "Número de Pavimentos",
        "Altura das edificações",
        "Topografia (hipsometria)",
        "Superfície sem vegetação (altitude)",
        "Superfície com vegetação (altitude)",
        "Diferença construtiva 2020-2017",
        "Diferença construtiva 2024-2020"
    ])
    ano_base = st.selectbox("Ano base:", [2017, 2020, 2024])
    subproduto = st.selectbox("Subproduto LiDAR:", [
        "Modelo de altura das edificações",
        "Modelo digital de superfície",
        "Modelo digital de terreno",
        "Ortofoto",
        "Fator de visão do céu"
    ])

# --- CONTEUDO ---

# --- Filtrar a feição correspondente ---
favela_selecionada = gdf[gdf["fv_nome"] == favela].to_crs(epsg=4326)
favela_sirgas = gdf[gdf["fv_nome"] == favela]

# Criar mapa Leafmap (folium)
m = leafmap.Map()

# Adicionar a camada vetorial
m.add_gdf(favela_selecionada, layer_name="Altura dos pavimentos")

# Adicionar uma camada base
m.add_basemap("CartoDB.Positron")

# Ajustando ao frame do mapa
bounds = favela_selecionada.total_bounds
m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

# Caminho do raster original
raster_path = "../LiDAR_produtos/2017/BHM-2017-50cm.tiff"

# Recortar o raster pela máscara da favela
geometry = [favela_sirgas.geometry.iloc[0].__geo_interface__]
with rasterio.open(raster_path) as src:
    out_image, out_transform = mask(src, geometry, crop=True)
    out_meta = src.meta.copy()

    out_meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform
    })

# Remover pixels nodata
nodata = src.nodata
data = out_image[out_image != nodata]

# Encontrar valores min e max
min_val = data.min()
max_val = data.max()

# Criar um arquivo temporário para o raster recortado
temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
# with rasterio.open(temp_file.name, "w", **out_meta) as dest:
#     dest.write(out_image)
with rasterio.open(temp_file.name, "w", **out_meta) as dest:
    dest.write(out_image)   # Banda principal 

palette = ["blue", "green", "yellow", "red"]

# Adicionar ao mapa Leafmap (tons de cinza)
m.add_raster(temp_file.name, layer_name="Raster Recortado", nodata=0, opacity=1.0, vmin=min_val, vmax=max_val, palette=palette)

# Adicionar legenda (escala de cores)
m.add_colorbar(
    colors=palette,
    vmin=min_val,
    vmax=max_val,
    label="Altura (m)",
    position="bottomleft"  # texto da legenda
)

# Exibir mapa
m.to_streamlit(height=600)

# --- ATRIBUTOS ---
st.subheader(f"Análises Quantitativas de {favela}")
st.write("Aqui será exibida uma tabela de atributos ou estatísticas calculadas.")

# --- ANÁLISES GRáFICAS ---

# --- ANÁLISE TEXTUAL ---

# --- FEEDBACK TEXTUAL ---



