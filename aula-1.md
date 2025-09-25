---
marp: true
theme: default
paginate: true
footer: "Fundamentos do LiDAR — Aula 1 | © 2025"
title: "Fundamentos do LiDAR"
author: "Fernando Gomes"
---

# Fundamentos do LiDAR  
### Da nuvem de pontos à cidade em 3D  

_Subtítulo: primeiros passos para compreender formatos, processamentos e aplicações_  

---

## Qual a diferença entre LiDAR, nuvem de pontos e .LAZ?  

🔹 **LiDAR** = tecnologia (laser + tempo de retorno).  
🔹 **Nuvem de pontos** = resultado bruto da aquisição.  
🔹 **LAS/LAZ** = formatos padronizados dos pontos.  

---

## Origem e princípios básicos  
**Wehr & Lohr (1999); Baltsavias (1999)**  

- Sistema ativo: emissão de pulso laser + tempo de retorno.  
- Permite múltiplos retornos → vegetação, telhado, solo.  
- Alta densidade de pontos, precisão vertical.  

![bg right:40% 80%](https://upload.wikimedia.org/wikipedia/commons/1/1b/Lidar-scanner-principle.png)

---

## Estrutura e sistemas  
**Shan & Toth (2020)**  

- **ALS** – aéreo, áreas extensas.  
- **TLS** – terrestre, alta densidade local.  
- **MLS** – móvel, corredores urbanos.  
- **SLAM** – drones/portáteis, indoor.  

➡ Geometria: GNSS + IMU + ângulo de varredura.  
➡ Fluxo: aquisição → filtragem → classificação → produtos (MDT, MDS).  

---

## Processamento e classificação  
**Vosselman & Maas (2010); Meng et al. (2010)**  

- Separar terreno / edificações / vegetação.  
- Métodos:  
  - TIN adaptativo (Axelsson, 2000).  
  - Filtros progressivos / morfologia.  
- Softwares: **CloudCompare**, **PCL**.  

![bg right:40% 80%](https://www.cloudcompare.org/images/screenshots/snapshot3d.jpg)

---

## Formatos e padrões  
**ASPRS (2019); Isenburg (2013)**  

- **LAS**: padrão aberto, atributos (X,Y,Z, intensidade, retornos).  
- **LAZ**: compressão lossless (LASzip), ~80% menor.  
- Estrutura: cabeçalho + pontos + atributos.  

📄 [LAS Specification 1.4](https://www.asprs.org/wp-content/uploads/2019/03/LAS_1_4_r14.pdf)  

---

## Contexto e aplicações  

- Dados abertos: **GeoSampa (PMSP)**.  
- Produtos derivados:  
  - MDT (terreno)  
  - MDS (superfície)  
  - BHM (edifícios)  
  - VHM (vegetação)  
- Usos:  
  - Planejamento urbano.  
  - Hidrologia.  
  - Patrimônio e arqueologia.  

---

## E daí? Resultados esperados  

- LiDAR revela:  
  - **Cheios e vazios** urbanos.  
  - **Fatores climáticos** (SVF, insolação).  
  - **Mudanças temporais** (2017/20/24).  

![bg right:40% 80%](https://upload.wikimedia.org/wikipedia/commons/f/f0/Lidar_point_cloud.png)

---

## 📚 Referências  

**Fundamentos**  
- BALTSAVIAS, 1999.  
- SHAN & TOTH, 2020.  
- VOSSELMAN & MAAS, 2010.  
- WEHR & LOHR, 1999.  

**Processamentos e libs**  
- CLOUDCOMPARE, 2024.  
- MENG et al., 2010.  
- RUSU & COUSINS, 2011.  

**Formatos e padrões**  
- ASPRS, 2019.  
- ISENBURG, 2013.  

**Contexto**  
- FREIRE, 1987; 2001.  
- PMSP (GeoSampa).  

---

## Pergunta freireana  

> “Se você já vê a forma da cidade todos os dias, o que o LiDAR pode te ensinar de novo sobre aquilo que já está diante dos seus olhos?”  

![bg 90%](https://www.laserscanningforum.com/forum/download/file.php?id=19326)  
