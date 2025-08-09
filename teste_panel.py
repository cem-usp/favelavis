# favela_panel_app.py
import panel as pn
import geopandas as gpd
import rasterio
from rasterio.mask import mask
import tempfile
import numpy as np
import leafmap.leafmap as leafmap

pn.extension()

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
    "Superfície": ['MDS', 'Diferança']
}

# --- WIDGETS ---
favela_widget = pn.widgets.Select(name='Favela', options=list(gdf.fv_nome))
tema_widget = pn.widgets.Select(name='Tema', options=list(mapas.keys()))
mapa_widget = pn.widgets.Select(name='Mapa')
anos_widget = pn.widgets.DiscreteSlider(name='Ano', options=anos_disponiveis, value=2024)

@pn.depends(tema_widget)
def update_mapa_options(tema):
    mapa_widget.options = mapas[tema]
    mapa_widget.value = mapas[tema][0]
    return

update_mapa_options(tema_widget.value)
tema_widget.param.watch(lambda e: update_mapa_options(e.new), 'value')

# --- FUNÇÃO RASTER ---
def raster_path(ano, mapa):
    base_path = f'../LiDAR_produtos/{ano}'
    raster_dict = {
        'Gabaritos': f'{base_path}/BHM-{ano}-50cm.tiff',
        'Pavimentos': f'{base_path}/BHM-{ano}-50cm.tiff',
        'Hipsometria': f'{base_path}/MDT-{ano}-50cm.tiff',
        'Declividade': f'{base_path}/MDT-{ano}-50cm.tiff',
        'MDS': f'{base_path}/MDS_sem_vegetacao-{ano}-1m-preenchido.tiff',
        'Diferança': f'{base_path}/MDS_sem_vegetacao-{ano}-1m-preenchido.tiff'
    }
    return raster_dict.get(mapa)

def raster_temp(geometry, mapa, ano):
    with rasterio.open(raster_path(ano, mapa)) as src:
        out_image, out_transform = mask(src, [geometry], crop=True)
        out_meta = src.meta.copy()

        out_meta.update({
            "driver": "GTiff",
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform
        })

        nodata = src.nodata
        data = out_image[out_image != nodata]
        min_val = float(data.min())
        max_val = float(data.max())

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".tif")
        with rasterio.open(temp_file.name, "w", **out_meta) as dest:
            dest.write(out_image)

    return temp_file.name, min_val, max_val

# --- VISUALIZAÇÃO PRINCIPAL ---
@pn.depends(favela_widget, tema_widget, mapa_widget, anos_widget)
def render_mapa(favela, tema, mapa, ano):
    gdf_fav = gdf[gdf['fv_nome'] == favela]
    geometry = gdf_fav.geometry.iloc[0]
    gdf_fav = gdf_fav.to_crs(epsg=4326)

    # Raster
    raster_file, vmin, vmax = raster_temp(geometry.__geo_interface__, mapa, ano)

    m = leafmap.Map(center=(geometry.centroid.y, geometry.centroid.x), zoom=16)
    m.add_basemap("CartoDB.Positron")
    m.add_gdf(gdf_fav, layer_name=favela)
    m.add_raster(raster_file, layer_name=f"{mapa} - {ano}", palette=["blue", "green", "yellow", "red"], vmin=vmin, vmax=vmax, nodata=0)
    m.add_colorbar(colors=["blue", "green", "yellow", "red"], vmin=vmin, vmax=vmax, label=mapa, position="bottomleft")

    return pn.panel(m, height=600)

# --- LAYOUT ---
sidebar = pn.Column("# FavelaVIS", favela_widget, tema_widget, mapa_widget, anos_widget, width=300)
main = pn.Column(render_mapa)

pn.Row(sidebar, main).servable()
pn.panel(main).servable()

