# -*- coding: utf-8 -*-
"""P73e — insumos del modelo modal POR ZONA EOD (Antofagasta): av, sexo, edad.
Corrige la aplicación uniforme: el logit debe recibir av y demografía de la zona de ORIGEN.
  av por zona: valor de propiedad SII (proxy ingreso) -> quintil -> gradiente av-ingreso del POOL
               (transferible: 0,113/0,158/0,198/0,247/0,366), anclado a la media INE comunal (0,18).
  sexo y edad por zona: Censo 2024 (n_mujeres, n_edad_*), unión espacial a zonas EOD.
Salida: antofagasta_zona_inputs.csv (zona, female, youth, elderly, av).
"""
import sys, re, glob; sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd, numpy as np, geopandas as gpd, warnings; warnings.filterwarnings('ignore')
from scipy.spatial import cKDTree
def nz(x): return re.sub(r'\.0$','',str(x).strip())
CB=r'../GIS Gran Concepción/Analisis uso de suelo Gran Concepción/Censo'
GIS=r'../GIS Gran Concepción/Analisis uso de suelo Gran Concepción'
AV_Q={1:0.113,2:0.158,3:0.198,4:0.247,5:0.366}; AV_INE=72139/401096   # gradiente pool + nivel INE comunal
AGES=['n_edad_0_5','n_edad_6_13','n_edad_14_17','n_edad_18_24','n_edad_25_44','n_edad_45_59','n_edad_60_mas']

# zonas EOD
ez=pd.read_parquet('EOD_PARQUET/zonas_centroides.parquet'); ez=ez[ez['ciudad'].astype(str)=='Antofagasta'].dropna(subset=['lat','lon']).copy()
ez['zona']=ez['zona'].map(nz); ez=ez.drop_duplicates('zona').reset_index(drop=True)
tree=cKDTree(ez[['lat','lon']].values); ZN=ez['zona'].values; n=len(ZN)

# --- censo: sexo + edad por zona censal -> zona EOD ---
zp=pd.read_parquet(CB+'/parquet/censo2024_zona_localidad.parquet')
zp=zp[zp['COMUNA'].astype(str).str.upper().str.contains('ANTOFAGASTA',na=False)].copy()
for c in AGES+['n_hombres','n_mujeres']: zp[c]=pd.to_numeric(zp[c],errors='coerce').fillna(0)
zp['cod']=zp['ID_ZONA'].map(nz)
gz=gpd.read_parquet(CB+'/2024/Cartografia_censo2024_Pais/Cartografia_censo2024_Pais_Zonal.parquet')
gz=gz[gz['COMUNA'].astype(str).str.upper().str.contains('ANTOFAGASTA',na=False)].to_crs(4326).copy()
gz['cod']=gz['ID_ZONA'].map(nz); cc=gz.geometry.centroid; gz['clat']=cc.y; gz['clon']=cc.x
gz=gz.groupby('cod').agg(clat=('clat','mean'),clon=('clon','mean')).reset_index()
m=zp.merge(gz,on='cod').dropna(subset=['clat','clon'])
_,zi=tree.query(m[['clat','clon']].values); m['zona']=ZN[zi]
ag=m.groupby('zona')[AGES+['n_hombres','n_mujeres']].sum().reindex(ZN).fillna(0)
tot=ag[AGES].sum(1).replace(0,np.nan)
female=(ag['n_mujeres']/(ag['n_hombres']+ag['n_mujeres']).replace(0,np.nan)).fillna(0.5).values
youth=((ag['n_edad_0_5']+ag['n_edad_6_13']+ag['n_edad_14_17']+ag['n_edad_18_24'])/tot).fillna(0.35).values
elderly=(ag['n_edad_60_mas']/tot).fillna(0.12).values
pop=ag[AGES].sum(1).values

# --- SII: valor de propiedad residencial por zona EOD (proxy ingreso) ---
f=glob.glob(GIS+r'/comunas_parquet/Antofagasta_2201.parquet')[0]
cat=pd.read_parquet(f,columns=['destinoDescripcion','valorComercial_clp_m2','lat','lon'])
cat=cat[cat['destinoDescripcion']=='HABITACIONAL'].copy()
cat['val']=pd.to_numeric(cat['valorComercial_clp_m2'],errors='coerce'); cat['lat']=pd.to_numeric(cat['lat'],errors='coerce'); cat['lon']=pd.to_numeric(cat['lon'],errors='coerce')
cat=cat.dropna(subset=['lat','lon','val']); cat=cat[cat['val']>0]
_,zi=tree.query(cat[['lat','lon']].values); cat['zona']=ZN[zi]
val=cat.groupby('zona')['val'].median().reindex(ZN)
val=val.fillna(val.median())

# --- av por zona: rank por valor -> quintil (ponderado por población) -> av del pool -> anclar media a INE ---
order=val.values.argsort()
cum=np.cumsum(pop[order])/max(pop.sum(),1)
quint=np.empty(n,int)
for rank,idx in enumerate(order): quint[idx]=min(5,int(cum[rank]*5)+1)
av=np.array([AV_Q[q] for q in quint],float)
av=av*(AV_INE/np.average(av,weights=np.where(pop>0,pop,1)))     # anclar media ponderada a la INE comunal
out=pd.DataFrame({'zona':ZN,'female':np.round(female,3),'youth':np.round(youth,3),'elderly':np.round(elderly,3),'av':np.round(av,3),'pop':pop.astype(int),'valor_m2':val.values.round(0)})
out.to_csv('antofagasta_zona_inputs.csv',index=False)
print('av por zona: media %.3f (INE %.3f) · min %.3f max %.3f · gradiente sur/norte:'%(np.average(av,weights=np.where(pop>0,pop,1)),AV_INE,av.min(),av.max()))
sur=ez['lat'].values<np.median(ez['lat'].values)
print('  SUR av medio %.3f vs NORTE %.3f (poblado)'%(np.average(av[sur],weights=np.where(pop[sur]>0,pop[sur],1)),np.average(av[~sur],weights=np.where(pop[~sur]>0,pop[~sur],1))))
print('-> antofagasta_zona_inputs.csv')
