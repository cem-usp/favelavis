import geopandas as gpd
from nicegui import ui, app
from shapely.geometry import Point
import rasterio
from rasterio.mask import mask
import numpy as np
import matplotlib.pyplot as plt
import os
import folium

# Pega o caminho absoluto para o diretório onde o script está
script_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(script_dir, 'static')
app.add_static_files('/static', static_dir)

# --- 0. Configuração ---
os.makedirs(static_dir, exist_ok=True)
RASTER_INPUT_PATH = '../../LiDAR_produtos/2017/MDT-points-2017-50cm.tiff'
RASTER_OUTPUT_PATH = os.path.join(static_dir, 'raster_overlay.png')
RASTER_URL_PATH = '/static/raster_overlay.png'

# --- 1. Preparação dos Dados Vetoriais ---
gdf = gpd.read_file('../data/SIRGAS_GPKG_favela.gpkg')
gdf.geometry = gdf.buffer(0)
gdf_sao_remo = gdf.loc[gdf.fv_nome == 'São Remo', :].copy()
gdf_sao_remo.to_crs(epsg=4326, inplace=True)

# --- 2. Preparação dos Dados para o Mapa ---
if gdf_sao_remo.empty:
    @ui.page('/')
    def error_page():
        ui.label("Erro: Feição 'São Remo' não encontrada.").classes('text-red-500 text-2xl')
else:
    centroide = gdf_sao_remo.geometry.centroid.iloc[0]
    map_center = (centroide.y, centroide.x)

    # --- 3. PROCESSAMENTO DO RASTER ---
    try:
        with rasterio.open(RASTER_INPUT_PATH) as src:
            raster_crs = src.crs
            original_nodata_value = src.nodata
            if original_nodata_value is None:
                fill_value_for_mask = np.nan
            else:
                fill_value_for_mask = original_nodata_value
            
            gdf_sao_remo_reproj = gdf_sao_remo.to_crs(raster_crs)
            
            out_image, out_transform = mask(
                src, gdf_sao_remo_reproj.geometry, 
                crop=True, 
                nodata=fill_value_for_mask 
            )
            out_meta = src.meta.copy()

        out_meta.update({"driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform})
        
        masking_value = fill_value_for_mask
        image_data = out_image.squeeze()
        
        if np.isnan(masking_value):
            masked_data = np.ma.masked_invalid(image_data)
        else:
            masked_data = np.ma.masked_equal(image_data, masking_value)

        cmap = plt.get_cmap('viridis').copy()
        cmap.set_bad(alpha=0)
        
        plt.imsave(RASTER_OUTPUT_PATH, masked_data, cmap=cmap, format='png')
        print(f"Raster recortado e salvo como PNG transparente em '{RASTER_OUTPUT_PATH}'")

        # --- 4. CALCULAR OS LIMITES GEOGRÁFICOS DA IMAGEM ---
        bounds = rasterio.transform.array_bounds(out_meta['height'], out_meta['width'], out_meta['transform'])
        points_utm = [Point(bounds[0], bounds[1]), Point(bounds[2], bounds[3])]
        gdf_bounds = gpd.GeoDataFrame(geometry=points_utm, crs=raster_crs)
        gdf_bounds_wgs84 = gdf_bounds.to_crs(epsg=4326)
        min_lon, min_lat = gdf_bounds_wgs84.geometry[0].x, gdf_bounds_wgs84.geometry[0].y
        max_lon, max_lat = gdf_bounds_wgs84.geometry[1].x, gdf_bounds_wgs84.geometry[1].y
        image_bounds_for_leaflet = [[min_lat, min_lon], [max_lat, max_lon]]
        
        raster_processado = True

    except Exception as e:
        print(f"Erro ao processar o raster: {e}")
        raster_processado = False

    # --- 5. Criação da Interface com NiceGUI e Folium ---
    @ui.page('/')
    def map_page():
        ui.label('Mapa da Favela São Remo (com Folium)').classes('text-h3')

        m = folium.Map(location=map_center, zoom_start=15, tiles="OpenStreetMap")

        # --- AQUI ESTÁ A MUDANÇA: fillOpacity: 0 ---
        style_function = lambda x: {
            'fillColor': '#ff7800',  # Cor ainda pode estar definida, mas não será visível
            'color': '#ff0000',      # Cor da borda
            'weight': 3,             # Espessura da borda
            'fillOpacity': 0,        # <--- Defina a opacidade do preenchimento como 0 para ser transparente
            'opacity': 0.7           # Opacidade da borda
        }

        folium.GeoJson(gdf_sao_remo, style_function=style_function).add_to(m)

        if raster_processado:
            folium.raster_layers.ImageOverlay(
                image=RASTER_OUTPUT_PATH,
                bounds=image_bounds_for_leaflet,
                opacity=0.7,
                interactive=True
            ).add_to(m)

        map_html = m._repr_html_()
        ui.html(map_html).classes('w-full h-[600px]')

# Inicia a aplicação
ui.run()