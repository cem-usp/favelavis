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
anos_disponiveis = [2017, 2020, 2024]
deltas = ['2020-2017', '2024-2020']

# Carregar feições
gdf = gpd.read_file('data/SIRGAS_GPKG_favela.gpkg')
gdf.geometry = gdf.buffer(0)
gdf = gdf.dissolve(by='fv_nome').reset_index()

# Mapas por tema
mapas = {
    "Edificações":
        [
            'Gabaritos',
            'Pavimentos'
        ],
    "Topografia":
        [
            'Hipsometria',
            'Declividade'
        ],
    "Superfície": 
        [
            'MDS',
            'Diferança'
        ]
}

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
with st.sidebar.expander("Favelas", expanded=True):
    favela = st.selectbox(
        "Favela:",
        gdf.fv_nome.to_list()
    )

# Visualiza Mapa
with st.sidebar.expander("Mapas", expanded=True):
    # Checkbox para comparação
    dividir_mapa = st.checkbox("Dividir mapa")

    anos = st.select_slider(
        "Época:",
        options=anos_disponiveis,
        value=(2017, 2024) if dividir_mapa else (2024)  # valores iniciais  
    )

    tema = st.selectbox(f"Tema{' da esquerda' if dividir_mapa else ''}:", list(mapas.keys()))
    mapa = st.selectbox(f"Mapa:{' da esquerda' if dividir_mapa else ''}:", list(mapas[tema]))

    if dividir_mapa:
        tema2 = st.selectbox(f"Tema da direita:", list(mapas.keys()))
        mapa2 = st.selectbox("Mapa da direita:", list(mapas[tema2]))

# Selecionar Atributo
with st.sidebar.expander("Atributos"):
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

# ajusta os limites do mapa e o zoom
bounds = favela_selecionada.total_bounds
m.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

def raster_path(ano, mapa):

    mapa = mapa

    if isinstance(ano, int):
        i = ano
    else:
        i = 2024

    BHMs = f'../LiDAR_produtos/{i}/BHM-{i}-50cm.tiff' # 50cm
    MDTs = f'../LiDAR_produtos/{i}/MDT-{i}-50cm.tiff' # 50cm
    MDSs_sem_veg = f'../LiDAR_produtos/{i}/MDS_sem_vegetacao-{i}-1m-preenchido.tiff' # 1m
    MDSs_sem_veg_delta = f'../LiDAR_produtos/{i}/MDS_sem_vegetacao-{i}-1m-preenchido.tiff' # 1m

    raster_path = {
        'Gabaritos': BHMs,
        'Pavimentos': BHMs,
        'Hipsometria': MDTs,
        'Declividade': MDTs,
        'MDS': MDSs_sem_veg,
        'Diferança': MDSs_sem_veg_delta
    }

    return raster_path.get(mapa, "SEILA")

# Recortar o raster pela máscara da favela
geometry = [favela_sirgas.geometry.iloc[0].__geo_interface__]

# gera um raster temporário para o determinado mapa e ano para a favela selecionada
def raster_temp(geometry=geometry, mapa=mapa, anos=anos): 
    with rasterio.open(raster_path(anos, mapa)) as src:
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
    with rasterio.open(temp_file.name, "w", **out_meta) as dest:
        dest.write(out_image)   # Banda principal 

    return temp_file, min_val, max_val

if dividir_mapa:
    # Separar os parâmetros
    anos_a, anos_b = anos
    mapa_a = mapa
    mapa_b = mapa2

    # Processar raster da esquerda
    temp_file_a, min_val_a, max_val_a = raster_temp(anos=anos_a, mapa=mapa_a)

    # Processar raster da direita
    temp_file_b, min_val_b, max_val_b = raster_temp(anos=anos_b, mapa=mapa_b)

    # Paleta de cores (pode ser igual ou diferente para cada lado)
    palette = ["blue", "green", "yellow", "red"]

    # Centro do mapa (pode ajustar conforme necessário)
    lat = favela_sirgas.geometry.iloc[0].centroid.y
    lon = favela_sirgas.geometry.iloc[0].centroid.x

    # Mapa A (esquerda)
    m1 = leafmap.Map(center=(lat, lon), zoom=16)
    m1.add_raster(temp_file_a.name, layer_name=f"{mapa_a} - {anos_a}",
                palette=palette, vmin=min_val_a, vmax=max_val_a, nodata=0)
    m1.add_colorbar(colors=palette, vmin=min_val_a, vmax=max_val_a,
                    label=f"{mapa_a} - {anos_a}", position="bottomleft")

    # Mapa B (direita)
    m2 = leafmap.Map(center=(lat, lon), zoom=16)
    m2.add_raster(temp_file_b.name, layer_name=f"{mapa_b} - {anos_b}",
                palette=palette, vmin=min_val_b, vmax=max_val_b, nodata=0)
    m2.add_colorbar(colors=palette, vmin=min_val_b, vmax=max_val_b,
                    label=f"{mapa_b} - {anos_b}", position="bottomright")

    # Linked maps sincronizados
    linked = leafmap.linked_maps(
        maps=[m1, m2],
        left_labels=[f"{mapa_a} - {anos_a}"],
        right_labels=[f"{mapa_b} - {anos_b}"],
        label_position="top",
        height=600
    )

    # Exibir no Streamlit
    linked.to_streamlit()
else:
    temp_file, min_val, max_val = raster_temp()

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
st.subheader(f"Análises Quantitativas de {favela}, {anos}")
st.write("Aqui será exibida uma tabela de atributos ou estatísticas calculadas.")

# --- ANÁLISES GRáFICAS ---

# --- ANÁLISE TEXTUAL ---

# --- FEEDBACK TEXTUAL ---



