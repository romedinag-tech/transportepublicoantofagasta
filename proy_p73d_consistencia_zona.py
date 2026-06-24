# -*- coding: utf-8 -*-
"""P73d — consistencia POR ZONA: cuota de auto al trabajo del Censo 2024 vs la simulación EOD.
El censo (n_transporte_* por zona censal) se une espacialmente a las zonas EOD; se compara la cuota
de auto observada vs simulada, en especial el SUR de altos ingresos (juicio experto del usuario).
"""
import sys, re, json; sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd, numpy as np, geopandas as gpd, warnings; warnings.filterwarnings('ignore')
from scipy.spatial import cKDTree
def nz(x): return re.sub(r'\.0$','',str(x).strip())
CB=r'../GIS Gran Concepción/Analisis uso de suelo Gran Concepción/Censo'
TM={'n_transporte_auto':'auto','n_transporte_publico':'pub','n_transporte_camina':'act','n_transporte_bicicleta':'act'}

# ---- censo: modo al trabajo + escolaridad por zona censal ----
zp=pd.read_parquet(CB+'/parquet/censo2024_zona_localidad.parquet')
zp=zp[zp['COMUNA'].astype(str).str.upper().str.contains('ANTOFAGASTA',na=False)].copy()
for c in list(TM)+['n_ocupado','prom_escolaridad18']: zp[c]=pd.to_numeric(zp[c],errors='coerce').fillna(0)
zp['cod']=zp['ID_ZONA'].map(nz)
zp['c_auto']=zp['n_transporte_auto']; zp['c_pub']=zp['n_transporte_publico']; zp['c_act']=zp['n_transporte_camina']+zp['n_transporte_bicicleta']
zp['esc_w']=zp['prom_escolaridad18']*zp['n_ocupado']

# geometría -> centroide
gz=gpd.read_parquet(CB+'/2024/Cartografia_censo2024_Pais/Cartografia_censo2024_Pais_Zonal.parquet')
gz=gz[gz['COMUNA'].astype(str).str.upper().str.contains('ANTOFAGASTA',na=False)].to_crs(4326).copy()
gz['cod']=gz['ID_ZONA'].map(nz); cc=gz.geometry.centroid; gz['clat']=cc.y; gz['clon']=cc.x
gz=gz.groupby('cod').agg(clat=('clat','mean'),clon=('clon','mean')).reset_index()
m=zp.merge(gz,on='cod',how='inner').dropna(subset=['clat','clon'])

# ---- zonas EOD: centroides + asignación ----
ez=pd.read_parquet('EOD_PARQUET/zonas_centroides.parquet'); ez=ez[ez['ciudad'].astype(str)=='Antofagasta'].dropna(subset=['lat','lon']).copy()
ez['zona']=ez['zona'].map(nz); ez=ez.drop_duplicates('zona').reset_index(drop=True)
tree=cKDTree(ez[['lat','lon']].values); _,zi=tree.query(m[['clat','clon']].values); m['zona']=ez['zona'].values[zi]
cen=m.groupby('zona').agg(c_auto=('c_auto','sum'),c_pub=('c_pub','sum'),c_act=('c_act','sum'),
                          esc_w=('esc_w','sum'),nocu=('n_ocupado','sum')).reset_index()
cen['cens_auto']=cen['c_auto']/(cen[['c_auto','c_pub','c_act']].sum(1)).replace(0,np.nan)*100
cen['escol']=cen['esc_w']/cen['nocu'].replace(0,np.nan)

# ---- simulación: cuota auto por zona (de antofagasta_dashboard.html) ----
h=open('antofagasta_dashboard.html',encoding='utf-8').read()
zon=json.loads(re.search(r'var DATA=(\{.*?\}), GEO=',h,re.S).group(1))['zonas']
sim=pd.DataFrame(zon); sim['zona']=sim['zona'].astype(str).map(nz)
sim['sim_auto']=sim['auto']/(sim['auto']+sim['pub']+sim['act']).replace(0,np.nan)*100

d=cen.merge(sim[['zona','sim_auto','lat']],on='zona',how='inner')
d=d[(cen['nocu']>30).values[np.isin(cen['zona'],d['zona'])] if False else (d['c_auto']+d['c_pub']+d['c_act']>30)]
print('=== consistencia POR ZONA (n=%d zonas con datos) ==='%len(d))
print('correlación cuota auto censo vs simulación: %.2f'%d[['cens_auto','sim_auto']].corr().iloc[0,1])
print('cuota auto media: censo %.0f%% · simulación %.0f%%'%(d['cens_auto'].mean(),d['sim_auto'].mean()))
# norte vs sur (lat más negativa = sur)
med=d['lat'].median()
sur=d[d['lat']<med]; nor=d[d['lat']>=med]
print('\\n--- NORTE (lat>=%.3f) vs SUR (lat<%.3f) ---'%(med,med))
print('  SUR : censo auto %.0f%% · sim auto %.0f%% · escolaridad %.1f'%(sur['cens_auto'].mean(),sur['sim_auto'].mean(),sur['escol'].mean()))
print('  NORTE: censo auto %.0f%% · sim auto %.0f%% · escolaridad %.1f'%(nor['cens_auto'].mean(),nor['sim_auto'].mean(),nor['escol'].mean()))
# correlación auto con escolaridad (ingreso)
print('\\ncorrelación cuota auto ~ escolaridad (proxy ingreso):')
print('  censo: %.2f  ·  simulación: %.2f'%(d[['cens_auto','escol']].corr().iloc[0,1],d[['sim_auto','escol']].corr().iloc[0,1]))
print('\\n(si censo correlaciona auto con escolaridad y la simulación NO -> el modelo no captura el ingreso/av por zona)')
d.to_csv('antofagasta_consistencia_zona.csv',index=False)
