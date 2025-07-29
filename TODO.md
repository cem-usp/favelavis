# TODO – Análises Topográficas com RichDEM

Este documento reúne as análises e etapas recomendadas para mapeamento de talvegues, áreas alagáveis e riscos de deslizamento utilizando um MDT (Modelo Digital do Terreno) com **RichDEM**.

---

## 1. Estratégia Geral

- **Escolha de Escopo:**
  - [ ] Avaliar se o *flow accumulation* será calculado para **toda a cidade** (mais completo) ou apenas para um **buffer da favela** (mais rápido).
  - [ ] Se optar pela cidade, considerar:
    - [ ] Reduzir a resolução (5m ou 10m).
    - [ ] Dividir o MDT em **tiles** e processar por partes.
    - [ ] Unir os tiles processados no final.
    - [ ] Usar ferramentas eficientes, como **WhiteboxTools**.

---

## 2. Análises a Realizar com RichDEM

- [ ] **Flow Accumulation (Acumulação de Fluxo):**
  - Gera raster indicando a quantidade de pixels que drenam para cada célula.
  - Usar para detectar **talvegues** (threshold).

- [ ] **Slope (Declividade):**
  - Avaliar riscos de **deslizamento** e áreas íngremes.
  - Classificar em faixas: plano (<5°), suave (5–15°), médio (15–30°), íngreme (>30°).

- [ ] **Aspect (Direção da Encosta):**
  - Entender exposição solar e impactos climáticos.
  - Pode ser útil para estudos de erosão.

- [ ] **Curvature (Curvatura):**
  - Detectar áreas côncavas (acúmulo de água) e convexas (erosão).

- [ ] **TWI (Topographic Wetness Index):**
  - Indica áreas de saturação e risco de alagamento.
  - Fórmula: `TWI = ln((flow_acc + 1) / tan(slope))`.

- [ ] **TPI (Topographic Position Index):**
  - Classifica pontos como topo, encosta ou vale.
  - Útil para caracterização geomorfológica.

- [ ] **TRI (Terrain Ruggedness Index):**
  - Mede irregularidade e complexidade do relevo.

---

## 3. Pós-processamento de Talvegues

- [ ] Aplicar **threshold** sobre `flow_accumulation.tif` para extrair principais linhas de drenagem.
- [ ] **Skeletonize (skimage.morphology.skeletonize):**
  - Reduz a máscara de talvegues a uma linha de 1 pixel.
- [ ] Converter raster binário em **linhas vetoriais (GeoJSON)**:
  - Usar `rasterio.features.shapes()` ou QGIS Raster-to-Vector.

---

## 4. Visualização

- [ ] Aplicar **escala logarítmica** no raster de flow accumulation:
  - No QGIS: usar **Raster Calculator** com `log10("flow_accumulation@1" + 1)`.
- [ ] Sobrepor talvegues em **Hillshade** (sombreamento do MDT).
- [ ] Gerar mapas de:
  - Declividade (`slope.tif`).
  - Áreas alagáveis (TWI alto).
  - Talvegues (`talvegues.geojson`).

---

## 5. Próximos Scripts a Criar

- [ ] **Pipeline RichDEM** para gerar automaticamente:
  - `flow_accumulation.tif`.
  - `slope.tif`, `aspect.tif`, `curvature.tif`.
  - `twi.tif`.
- [ ] **Conversor de Talvegues**:
  - Lê `flow_accumulation.tif`.
  - Aplica threshold.
  - Executa skeletonize.
  - Exporta `talvegues.geojson`.

---

## 6. Notas sobre Flow Accumulation

- Cada pixel armazena o **número de células contribuintes** (incluindo ele mesmo).
- **Dependência da resolução:**
  - Mais pixels = valores maiores.
  - Para obter **área de contribuição (m²)**: `flow_acc * pixel_area`.
- Nos pontos mais baixos da bacia, os valores podem chegar a milhões.

---

## 7. Tarefas Futuras

- [ ] Implementar **delimitação de microbacias** com base na rede de talvegues e pontos de saída.
- [ ] Criar **mapa de risco integrado** (declividade + TWI + uso do solo).
- [ ] Explorar **WhiteboxTools** para processamento em escala urbana.

