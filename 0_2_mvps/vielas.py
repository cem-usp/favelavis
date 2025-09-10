from nicegui import ui
import geopandas as gpd
import rasterio
from rasterio.mask import mask
from rasterio.features import geometry_mask
import numpy as np
import matplotlib.pyplot as plt
import skfmm

TITLE = 'Favela3D+t - São Remo - Vielas'

# Carregar feições de favelas
gdf = gpd.read_file('../data/SIRGAS_GPKG_favela.gpkg')
gdf.geometry = gdf.buffer(0)

# Filtrar apenas a São Remo
gdf_sao_remo = gdf.loc[gdf.fv_nome == 'São Remo', :]

# Dicionário com anos, pastas e articulações
als = {
    2017: {
        "arquivos_laz": "../../LiDAR-Sampa-2017",
        "articulacao": "../data/quadricula_folha_mdt.zip",
        "atributo_quadricula": "cd_quadric",
        "nome_fn": lambda row, dados: f"MDS_color_{row[dados['atributo_quadricula']]}.laz",
        "raster_path": '../../LiDAR_produtos/2017/MDT-points-2017-50cm.tiff'
    },
    2020: {
        "arquivos_laz": "../../LiDAR-Sampa-2020",
        "articulacao": "../data/quadricula_folha_mdt_mds_2020.zip",
        "atributo_quadricula": "cd_quadric",
        "nome_fn": lambda row, dados: f"MDS_{row[dados['atributo_quadricula']]}_1000.laz",
        "raster_path": '../../LiDAR_produtos/2020/MDT-points-2020-50cm.tiff'
    },
    2024: {
        "arquivos_laz": "../../LiDAR-Sampa-2024",
        "articulacao": "../../LiDAR-Sampa-2024/poligonos_consolidados.gpkg",
        "atributo_quadricula": "nome_arquivo",
        "nome_fn": lambda row, dados: f'{row[dados["atributo_quadricula"]]}.laz',
        "raster_path": '../../LiDAR_produtos/2024/MDT-points-2024-50cm.tiff' 
    }
}

favela_geom = gdf_sao_remo.geometry.values.tolist()
raster_path  = als[2017]['raster_path']
# Abrir raster e recortar pela feição
with rasterio.open(raster_path) as src:
    print("Raster CRS:", src.crs)
    print("Bounds do raster:", src.bounds)
    print("Bounds da favela 0:", gdf.loc[gdf.fv_nome == 'São Remo', :].geometry.bounds)
    out_image, out_transform = mask(src, favela_geom, crop=True)
    out_data = out_image[0]

    # Filtrar valores válidos
    valid_data = out_data[out_data != src.nodata]

# Ordenar os valores
sorted_data = np.sort(valid_data)

import io
import base64
import matplotlib.pyplot as plt

# Exemplo: gerar PNG base64 a partir do raster
fig, ax = plt.subplots()
ax.imshow(out_data, cmap='terrain')
ax.axis('off')
buf = io.BytesIO()
plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0)
plt.close(fig)
png_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
bounds = src.bounds

# -----------------------
# INTERFACE NICEGUI
# -----------------------
# Barra de título fixa
with ui.header().classes('bg-blue-600 text-white items-center'):
    ui.label(TITLE).classes('text-xl font-bold p-2')

# Conteúdo principal com expansíveis
with ui.column().classes('p-4 space-y-2'):

    with ui.expansion('⚫ (0D) - Atributos calculados por Favela', value=False):
        ui.label('exemplo de conteúdo aqui...')

    with ui.expansion('··· (0.5D) - Atributos auto-referenciados', value=False):
        ui.label('proporção de Vs, frequência de larguras...')

    with ui.expansion('➖ (1D) - Rede de LineStrings', value=False):
        ui.label('Skeletonize...')

    with ui.expansion('📏 (1.5D) - Rede de LineStrings com tema', value=False):
        ui.label('largura, tipo: V...')

    with ui.expansion('🔲 (2D) - Rasteres, mapas e modelos', value=False):
        ui.html('<div id="map" style="height:500px; width:100%"></div>')

    with ui.expansion('🗺️ (2.5D) - Rasteres e mapas derivados', value=False):
        ui.label('agrupamentos por largura, FMM...')

    with ui.expansion('🧊 (3D)', value=False):
        ui.label('HxW, LineString 3D...')

    with ui.expansion('⏳ (+t)', value=False):
        ui.label('cada D + tempo...')

# injetar CSS e JS de Leaflet + inicialização do mapa
ui.add_body_html('''
<link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
''')

ui.add_body_html(f'''
<script>
  var map = L.map('map').setView([{(bounds.top+bounds.bottom)/2}, {(bounds.left+bounds.right)/2}], 15);
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      maxZoom: 19,
  }}).addTo(map);

  var imageUrl = "data:image/png;base64,{png_b64}";
  var imageBounds = [[{bounds.bottom}, {bounds.left}], [{bounds.top}, {bounds.right}]];
  L.imageOverlay(imageUrl, imageBounds, {{opacity:0.8}}).addTo(map);
</script>
''')

ui.run(title=TITLE)
