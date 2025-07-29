# Especificação Técnica Inicial do Protótipo FavelaVIS

Esta especificação técnica inicial descreve as funcionalidades previstas para o protótipo do **FavelaVIS**, organizado em módulos para facilitar o desenvolvimento com **Streamlit + Leaflet (via streamlit-folium)** e um backend simples (arquivos raster e tabelas de atributos).

---

## **1. Objetivo**
O protótipo do FavelaVIS permitirá ao usuário:
- Selecionar uma favela de uma lista pré-determinada.
- Visualizar **camadas raster** e comparar diferentes camadas ou anos usando **slider lado-a-lado** (Leaflet Side-by-Side).
- Explorar **atributos temporais** (2017, 2020, 2024) via **tabelas e gráficos dinâmicos**.
- Alternar entre camadas de **fundo/base** (BHM, MDS, MDT, ortofoto, SVF).

---

## **2. Módulos Principais**

### **2.1. Seleção de Favela**
- **Dropdown** para escolher uma favela (ex.: São Remo, Heliópolis, Paraisópolis).
- Ao selecionar a favela:
  - Carrega automaticamente **os rasters e atributos disponíveis**.
  - Mostra uma visão geral inicial (por exemplo, BHM 2024 como default).

---

### **2.2. Visualização Cartográfica (Leaflet)**
**Camadas Raster disponíveis:**
- **Número de pavimentos (BHM recalculado).**
- **Altura das edificações (BHM).**
- **Terreno (MDT).**
- **Superfície com vegetação (MDS).**
- **Superfície sem vegetação (MDS sem vegetação).**
- **Área lateral efetiva (ALE).** (área da parede lateral sem obstáculo construtivo a uma distância de 3m)
- **Diferença construtiva**:
  - 2017 – 2020.
  - 2020 – 2024.

**Camadas de fundo/base:**
- BHM (default).
- MDS.
- MDT.
- Ortofoto.
- SVF.

**Funcionalidades do mapa:**
- **Ferramenta de comparação lado-a-lado** (Leaflet Side-by-Side).
- **Controle de opacidade** (slider de transparência).
- **Zoom inicial** focado na favela selecionada.

---

### **2.3. Análise Atributiva**
**Atributos por favela e ano (2017, 2020, 2024):**
- Pavimentos (vetor)
- Gabaritos (vetor)
    - pavimentos e gabaritos são valores múltiplos/vetores que requerem uma atenção específica
- Área construída estimada (soma de pixels)
- Área construída por gabarito/pavimento (calculo)
- Área lateral efetiva total
- Área lateral efetiva sobre área total
- Área de projeção estimada. (contagem de pixels)
- CA (Coeficiente de Aproveitamento). (calculo)
- TO (Taxa de Ocupação). (calculo)
- Rugosidade da superfície. (desvio padrão da superfície)
- Rugosidade do terreno. (desvio padrão do terreno)
- Correlação entre variáveis (considerando cada variável em cada um dos anos 3D)

**Interface:**
- **Tabela interativa** com todos os atributos e valores para 2017, 2020, 2024.
- **Seletor de atributo** (dropdown) para visualizar **gráficos dinâmicos**.
- **Gráficos de linha** para evolução temporal (2017 → 2020 → 2024).
- **Comparação entre atributos** (scatter plot ou gráfico de correlação).

---

## **3. Estrutura Técnica**
- **Frontend:** Streamlit (UI e gráficos) + streamlit-folium (mapa interativo).
- **Mapa:** Leaflet com controle **Side-by-Side**.
- **Gráficos:** Altair.
- **Dados Raster:** Arquivos GeoTIFF organizados por uma estrutura de pastas pre-estabelecidas, a principio processando por código e gerando uma pasta temporária
- **Atributos:** Calculados a partir de pré-processamentos realizados e documentados

---

## **4. Fluxo do Usuário **
1. Seleciona **favela** → Mapa centraliza na área.
2. Escolhe **camada raster** (ou comparação de duas camadas).
3. Escolhe **camada de fundo** (BHM, MDS, MDT...).
4. Visualiza **diferenças construtivas** (2017-2020 ou 2020-2024).
5. Consulta **atributos** e alterna **gráficos/variáveis**.
6. (Futuro) Pode inserir comentários ou gerar análises automáticas com IA.

---

## **5. Primeira Versão Viável (MVP)**
Para um **MVP funcional**, sugiro implementar:
1. **Seleção de favela (4 favelas de exemplo).**
2. **Mapa Leaflet com camadas raster básicas (BHM, MDT, MDS).**
3. **Ferramenta de comparação lado-a-lado (Leaflet Side-by-Side).**
4. **Tabela de atributos + gráfico de evolução temporal para 1 ou 2 variáveis-chave (ex.: pavimentos e área construída).**
