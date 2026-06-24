# -*- coding: utf-8 -*-
"""P73c — población REAL del Censo 2024 por ZONA EOD × edad (Antofagasta), vía unión espacial.
Reemplaza el proxy de m² residencial: une las zonas censales 2024 (geometría) a las 105 zonas EOD
asignando cada zona censal a la zona EOD más cercana, y agrega población por los 7 tramos de edad.
Salida: antofagasta_pop_zona.csv (zona, n_edad_*). La usa proy_p73b para la generación (método puro).
"""
import sys, re; sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd, numpy as np, geopandas as gpd, warnings; warnings.filterwarnings('ignore')
from scipy.spatial import cKDTree
def nz(x): return re.sub(r'\.0$','',str(x).strip())
CB=r'../GIS Gran Concepción/Analisis uso de suelo Gran Concepción/Censo'
AGES=['n_edad_0_5','n_edad_6_13','n_edad_14_17','n_edad_18_24','n_edad_25_44','n_edad_45_59','n_edad_60_mas']

# población por zona censal × edad
zp=pd.read_parquet(CB+'/parquet/censo2024_zona_localidad.parquet')
zp=zp[zp['COMUNA'].astype(str).str.upper().str.contains('ANTOFAGASTA',na=False)].copy()
for c in AGES: zp[c]=pd.to_numeric(zp[c],errors='coerce').fillna(0)
zp['cod']=zp['ID_ZONA'].map(nz)
zp=zp.groupby('cod')[AGES].sum().reset_index()

# geometría de zonas censales -> centroide
gz=gpd.read_parquet(CB+'/2024/Cartografia_censo2024_Pais/Cartografia_censo2024_Pais_Zonal.parquet')
gz=gz[gz['COMUNA'].astype(str).str.upper().str.contains('ANTOFAGASTA',na=False)].to_crs(4326).copy()
gz['cod']=gz['ID_ZONA'].map(nz)
cen=gz.geometry.centroid; gz['clat']=cen.y; gz['clon']=cen.x
gz=gz.groupby('cod').agg(clat=('clat','mean'),clon=('clon','mean')).reset_index()

m=zp.merge(gz,on='cod',how='inner').dropna(subset=['clat','clon'])
print('zonas censales con población+geometría: %d (pob %d)'%(len(m),int(m[AGES].sum().sum())))

# zonas EOD (centroides) -> asignar cada zona censal a la EOD más cercana
ez=pd.read_parquet('EOD_PARQUET/zonas_centroides.parquet'); ez=ez[ez['ciudad'].astype(str)=='Antofagasta'].dropna(subset=['lat','lon']).copy()
ez['zona']=ez['zona'].map(nz); ez=ez.drop_duplicates('zona').reset_index(drop=True)
tree=cKDTree(ez[['lat','lon']].values)
_,zi=tree.query(m[['clat','clon']].values)
m['zona_eod']=ez['zona'].values[zi]

out=m.groupby('zona_eod')[AGES].sum().reindex(ez['zona'].values).fillna(0).reset_index().rename(columns={'index':'zona'})
out.columns=['zona']+AGES
out.to_csv('antofagasta_pop_zona.csv',index=False)
print('-> antofagasta_pop_zona.csv (%d zonas EOD, pob asignada %d / %d)'%(len(out),int(out[AGES].sum().sum()),int(m[AGES].sum().sum())))
print('   zonas EOD con población >0:',int((out[AGES].sum(1)>0).sum()))
