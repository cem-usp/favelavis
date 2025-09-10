from nicegui import ui
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import tempfile
import leafmap.foliumap as leafmap  # usar backend folium
import os
from shapely.geometry import shape

# --- DADOS ---
gdf = gpd.read_file('data/SIRGAS_GPKG_favela.gpkg')
gdf.geometry = gdf.buffer(0)
gdf = gdf.dissolve(by='fv_nome').reset_index()
favelas_test = ["Heliópolis", "Cocaia I", "Paraisópolis", "Futuro Melhor", "São Remo"]
gdf = gdf[gdf['fv_nome'].isin(favelas_test)]

anos_disponiveis = [2017, 2020, 2024]
mapas = {
    "Edificações": ['Gabaritos', 'Pavimentos'],
    "Topografia": ['Hipsometria', 'Declividade'],
    "Superfície": ['MDS', 'Diferença']
}

# --- FUNÇÕES ---
def raster_path(ano, mapa):
    base_path = f'../LiDAR_produtos/{ano}'
    raster_dict = {
        'Gabaritos': f'{base_path}/BHM-{ano}-50cm.tiff',
        'Pavimentos': f'{base_path}/BHM-{ano}-50cm.tiff',
        'Hipsometria': f'{base_path}/MDT-{ano}-50cm.tiff',
        'Declividade': f'{base_path}/MDT-{ano}-50cm.tiff',
        'MDS': f'{base_path}/MDS_sem_vegetacao-{ano}-1m-preenchido.tiff',
        'Diferença': f'{base_path}/MDS_sem_vegetacao-{ano}-1m-preenchido.tiff'
    }
    return raster_dict.get(mapa)

def raster_temp(geometry, mapa, ano):
    with rasterio.open(raster_path(ano, mapa)) as src:
        # Se geometry veio como dict (geo_interface), converte de volta para shapely
        if isinstance(geometry, dict):
            geometry = shape(geometry)

        # Cria GeoDataFrame com shapely geometry
        gdf_geom = gpd.GeoDataFrame(geometry=[geometry], crs="EPSG:4326")
        gdf_geom = gdf_geom.to_crs(src.crs)  # reprojeta para o CRS do raster

        geom_proj = [gdf_geom.geometry.iloc[0]]

        out_image, out_transform = mask(src, geom_proj, crop=True)
        out_meta = src.meta.copy()

        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
        with rasterio.open(temp_file.name, "w", **out_meta) as dest:
            dest.write(out_image)

    return temp_file.name

def render_map(favela, tema, mapa, ano):
    gdf_fav = gdf[gdf['fv_nome'] == favela].to_crs(epsg=4326)
    geometry = gdf_fav.geometry.iloc[0].__geo_interface__

    raster_file = raster_temp(geometry, mapa, ano)

    m = leafmap.Map(center=(gdf_fav.geometry.centroid.y.mean(),
                            gdf_fav.geometry.centroid.x.mean()),
                    zoom=16)

    m.add_basemap("CartoDB.Positron")
    m.add_gdf(gdf_fav, layer_name=favela)
    m.add_raster(raster_file, layer_name=f"{mapa} - {ano}",
                 palette=["blue", "green", "yellow", "red"])

    html_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html").name
    m.to_html(outfile=html_file)
    with open(html_file, 'r') as f:
        return f.read()

# --- INTERFACE NICEGUI ---
favela = ui.select(options=list(gdf.fv_nome), value="São Remo", label="Favela")
tema = ui.select(options=list(mapas.keys()), value="Topografia", label="Tema")
mapa = ui.select(options=mapas["Topografia"], value="Hipsometria", label="Mapa")
ano = ui.select(options=anos_disponiveis, value=2024, label="Ano")

@ui.refreshable
def mapa_leaf():
    html = render_map(favela.value, tema.value, mapa.value, ano.value)
    ui.html(html).classes('w-full h-[600px]')

# sempre que mudar, recarrega o mapa
favela.on('update:model-value', lambda e: mapa_leaf.refresh())
tema.on('update:model-value', lambda e: (mapa.set_options(mapas[tema.value]), mapa_leaf.refresh()))
mapa.on('update:model-value', lambda e: mapa_leaf.refresh())
ano.on('update:model-value', lambda e: mapa_leaf.refresh())

with ui.row():
    with ui.column():
        favela
        tema
        mapa
        ano
    with ui.column():
        mapa_leaf()

ui.run(title='Favela3D+t - NiceGUI Mapas')
