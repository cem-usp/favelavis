# FavelaVis

Processamento e visualizador de dados das favelas de São Paulo processados a partir de levantamentos LiDAR 3D

## Introdução

Esse repositório destina-se ao desenvolvimento do processamento dos dados e da construção de um visualizador para os resultados obtidos a partir dos levantamentos LiDAR 3D realizados na cidade de São Paulo nos anos de 2017, 2020 e 2024 na cidade de São Paulo

## Objetivo

Esse projeto tem o objetivo de apresentar, de maneira inédita, os quantitativos da morfologia das favelas da cidade de São Paulo e a sua dinâmica no decorrer do intervalo entre os levantamentos realizados.

## Materiais e métodos

- Limites geográficos das favelas estabelecidos pela HABISP da Prefeitura de São Paulo
- Levantamentos LiDAR de 2017 e 2020 levantados pela Prefeitura de São Paulo
- Levantamento LiDAR de 2024 disponibilizado pelo IGC do Governo do Estado de São Paulo

Os dados vão ser lidos e analisados utilizando diversas ferramentas de código aberto, incluindo: Python, GeoPandas, PDAL, Shapely, GDAL entre outros. Depois de processados e armazenados em uma tabela contendo cada uma das favelas de São Paulo os dados serão apresentados em um painel de visualização utilizando o Streamlit.

## Resultados esperados

Ao término do desenvolvimento espera-se manter disponível de uma maneira ampla e de fácil acesso os dados levantados e calculados para todas as favelas e assim contribuir com dados empíricos para a discussão e elaboração de políticas públicas, hipóteses e comparações dessa porção do tecido urbano. 
