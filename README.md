# Easy Flood Emergency Planning
### A Python-based evacuation routing system for flood emergencies on the Isle of Wight  

<img width="770" height="608" alt="Picture 1" src="https://github.com/user-attachments/assets/d68d0cc7-de9e-4220-a99e-22d209f8f8a3" />

## 1. Overview
This project computes the optimal walking evacuation route from a user-provided location to the highest accessible ground within 5 km.  
The system integrates elevation raster analysis, ITN (Integrated Transport Network) routing, and map visualization.

## 2. Features
- Validates user input and ensures location lies on the island  
- Extracts highest elevation within 5 km buffer  
- Identifies nearest ITN nodes using R-tree  
- Computes shortest walking-time path via Dijkstra (with Naismith-based weights)  
- Generates map visualisations; optional GUI for layer toggling (Windows only)  
- Supports multi-solution path comparison and road-name navigation   
  (Creative features, see report pp. 16–19) :contentReference[oaicite:1]{index=1}

## 3. Installation
Python 3.8 recommended.

```bash
pip install shapely==2.0.0 geopandas==0.12.2 rasterio==1.3.4 \
pandas==1.5.2 numpy==1.19.1 rtree==1.0.1 networkx==2.8.8 \
cartopy==0.18.0 matplotlib==3.3.1 pyproj==3.4.1
