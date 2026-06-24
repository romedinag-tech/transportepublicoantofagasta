# -*- coding: utf-8 -*-
"""P73f — CENSO 2024 de Antofagasta desagregado para el dashboard.
  (a) MÉTRICAS POR ZONA EOD (coroplético): demografía, movilidad al trabajo (P45), trabajo,
      educación, vivienda, conectividad, migración — uniendo zonas censales a las 105 zonas EOD.
  (b) CRUCES DE CIUDAD (gráficos): pirámide etaria por sexo, modo al trabajo por sexo y por edad,
      educación, vivienda y sectores económicos — desde el censo de personas (comuna 2101).
Salida: antofagasta_censo.json  (metrics[], zona{}, charts{})
"""
import sys, re, glob, json; sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd, numpy as np, geopandas as gpd, warnings; warnings.filterwarnings('ignore')
from scipy.spatial import cKDTree
def nz(x): return re.sub(r'\.0$','',str(x).strip())
CB=r'../GIS Gran Concepción/Analisis uso de suelo Gran Concepción/Censo'
PERS=CB+r'/2024/viv_hog_per_censo2024/personas_censo2024.parquet'
ABK=['n_edad_0_5','n_edad_6_13','n_edad_14_17','n_edad_18_24','n_edad_25_44','n_edad_45_59','n_edad_60_mas']
ABLAB=['0-5','6-13','14-17','18-24','25-44','45-59','60+']

# ---- zonas EOD (centroides) ----
ez=pd.read_parquet('EOD_PARQUET/zonas_centroides.parquet'); ez=ez[ez['ciudad'].astype(str)=='Antofagasta'].dropna(subset=['lat','lon']).copy()
ez['zona']=ez['zona'].map(nz); ez=ez.drop_duplicates('zona').reset_index(drop=True)
tree=cKDTree(ez[['lat','lon']].values); ZN=ez['zona'].values

# ---- (a) zona-localidad censal -> zona EOD ----
NEED=['n_per','n_hombres','n_mujeres','prom_edad','prom_escolaridad18']+ABK+[
 'n_transporte_auto','n_transporte_publico','n_transporte_camina','n_transporte_bicicleta','n_transporte_motocicleta','n_transporte_otros','n_transporte_cab_lan_bote',
 'n_ocupado','n_desocupado','n_fuera_fuerza_trabajo','n_inmigrantes','n_pueblos_orig',
 'n_cine_primaria','n_cine_secundaria','n_cine_terciaria_maestria_doctorado','n_asistencia_superior',
 'n_hog','n_jefatura_mujer','n_internet','n_viv_hacinadas','n_vp_ocupada',
 'n_tipo_viv_casa','n_tipo_viv_depto','n_tenencia_propia_pagada','n_tenencia_propia_pagandose',
 'n_caenes_B','n_caenes_G','n_caenes_F','n_caenes_C','n_caenes_P','n_caenes_Q','n_caenes_H','n_caenes_O','n_caenes_I']
zp=pd.read_parquet(CB+'/parquet/censo2024_zona_localidad.parquet')
zp=zp[zp['COMUNA'].astype(str).str.upper().str.contains('ANTOFAGASTA',na=False)].copy()
for c in NEED: zp[c]=pd.to_numeric(zp.get(c),errors='coerce').fillna(0)
zp['cod']=zp['ID_ZONA'].map(nz)
# escolaridad y edad ponderadas: numerador = promedio × población
zp['esc_w']=zp['prom_escolaridad18']*zp['n_per']; zp['edad_w']=zp['prom_edad']*zp['n_per']
gz=gpd.read_parquet(CB+'/2024/Cartografia_censo2024_Pais/Cartografia_censo2024_Pais_Zonal.parquet')
gz=gz[gz['COMUNA'].astype(str).str.upper().str.contains('ANTOFAGASTA',na=False)].to_crs(4326).copy()
gz['cod']=gz['ID_ZONA'].map(nz); cc=gz.geometry.centroid; gz['clat']=cc.y; gz['clon']=cc.x
gz=gz.groupby('cod').agg(clat=('clat','mean'),clon=('clon','mean')).reset_index()
m=zp.merge(gz,on='cod').dropna(subset=['clat','clon'])
_,zi=tree.query(m[['clat','clon']].values); m['zona']=ZN[zi]
SUM=[c for c in NEED if c not in('prom_edad','prom_escolaridad18')]+['esc_w','edad_w']
g=m.groupby('zona')[SUM].sum().reindex(ZN).fillna(0)

def pct(a,b): b=b.replace(0,np.nan); return (a/b*100)
mob=g[['n_transporte_auto','n_transporte_publico','n_transporte_camina','n_transporte_bicicleta','n_transporte_motocicleta','n_transporte_otros','n_transporte_cab_lan_bote']].sum(1)
Z={}
for z in ZN:
    r=g.loc[z]; per=r['n_per'] or np.nan; mo=mob.loc[z] or np.nan; hog=r['n_hog'] or np.nan
    act=r['n_transporte_camina']+r['n_transporte_bicicleta']; otr=r['n_transporte_otros']+r['n_transporte_cab_lan_bote']
    Z[nz(z)]={
      'c_pob':int(r['n_per']),
      'c_muj':round(r['n_mujeres']/per*100,1) if per==per else None,
      'c_edad':round(r['edad_w']/per,1) if per==per else None,
      'c_joven':round((r['n_edad_0_5']+r['n_edad_6_13']+r['n_edad_14_17'])/per*100,1) if per==per else None,
      'c_mayor':round(r['n_edad_60_mas']/per*100,1) if per==per else None,
      'c_auto':round(r['n_transporte_auto']/mo*100,1) if mo==mo else None,
      'c_pub':round(r['n_transporte_publico']/mo*100,1) if mo==mo else None,
      'c_activa':round(act/mo*100,1) if mo==mo else None,
      'c_otros':round(otr/mo*100,1) if mo==mo else None,
      'c_desoc':round(r['n_desocupado']/(r['n_ocupado']+r['n_desocupado'])*100,1) if (r['n_ocupado']+r['n_desocupado'])>0 else None,
      'c_escol':round(r['esc_w']/per,1) if per==per else None,
      'c_terc':round(r['n_cine_terciaria_maestria_doctorado']/per*100,1) if per==per else None,
      'c_depto':round(r['n_tipo_viv_depto']/(r['n_tipo_viv_casa']+r['n_tipo_viv_depto']).clip(min=1)*100,1),
      'c_hacin':round(r['n_viv_hacinadas']/(r['n_vp_ocupada'] or np.nan)*100,1) if r['n_vp_ocupada']>0 else None,
      'c_propia':round((r['n_tenencia_propia_pagada']+r['n_tenencia_propia_pagandose'])/hog*100,1) if hog==hog else None,
      'c_jefa':round(r['n_jefatura_mujer']/hog*100,1) if hog==hog else None,
      'c_internet':round(r['n_internet']/hog*100,1) if hog==hog else None,
      'c_inmig':round(r['n_inmigrantes']/per*100,1) if per==per else None,
      'c_orig':round(r['n_pueblos_orig']/per*100,1) if per==per else None,
    }
    # cuota modal LABORAL a 3 modos comparables (auto/público/activa), para bondad de ajuste vs modelo
    m3=r['n_transporte_auto']+r['n_transporte_publico']+act
    Z[nz(z)]['cw_auto']=round(r['n_transporte_auto']/m3*100,1) if m3>0 else None
    Z[nz(z)]['cw_pub']=round(r['n_transporte_publico']/m3*100,1) if m3>0 else None
    Z[nz(z)]['cw_act']=round(act/m3*100,1) if m3>0 else None
    Z[nz(z)]['cw_n']=int(m3)

METRICS=[
 ['c_pob','Población','Demografía','hab','#6b7280',False],
 ['c_muj','% Mujeres','Demografía','%','#a855f7',False],
 ['c_edad','Edad promedio','Demografía','años','#0891b2',False],
 ['c_joven','% 0-17 años','Demografía','%','#16a34a',False],
 ['c_mayor','% 60+ años','Demografía','%','#b45309',False],
 ['c_auto','Auto (al trabajo)','Movilidad censal','%','#c0392b',False],
 ['c_pub','Público (al trabajo)','Movilidad censal','%','#185fa5',False],
 ['c_activa','Activa (al trabajo)','Movilidad censal','%','#1e8449',False],
 ['c_otros','Otros/personal','Movilidad censal','%','#7c3aed',False],
 ['c_desoc','Tasa desocupación','Trabajo','%','#dc2626',True],
 ['c_terc','% Educación terciaria','Educación','%','#2563eb',False],
 ['c_escol','Escolaridad (18+)','Educación','años','#0d9488',False],
 ['c_depto','% Departamentos','Vivienda','%','#9333ea',False],
 ['c_hacin','% Viv. hacinadas','Vivienda','%','#ea580c',True],
 ['c_propia','% Vivienda propia','Vivienda','%','#0891b2',False],
 ['c_jefa','% Jefatura femenina','Vivienda','%','#db2777',False],
 ['c_internet','% Hogares con internet','Conectividad','%','#0284c7',False],
 ['c_inmig','% Inmigrantes','Migración','%','#7c3aed',False],
 ['c_orig','% Pueblos originarios','Migración','%','#b45309',False],
]

# ---- (b) cruces de ciudad desde el censo de personas ----
p=pd.read_parquet(PERS,columns=['comuna','sexo','edad','p45_medio_transporte'])
p=p[p['comuna'].astype('string').str.replace('.0','',regex=False)=='2101'].copy()
p['ab']=pd.cut(p['edad'],[0,6,14,18,25,45,60,200],labels=ABLAB,right=False)
# pirámide etaria por sexo
pir_h=[int(((p['ab']==l)&(p['sexo']==1)).sum()) for l in ABLAB]
pir_m=[int(((p['ab']==l)&(p['sexo']==2)).sum()) for l in ABLAB]
# modo al trabajo (P45) agrupado
MMAP={1:'Auto',2:'Público',3:'Activa',4:'Activa',5:'Moto',6:'Otros',7:'Otros'}
pm=p.dropna(subset=['p45_medio_transporte']).copy(); pm['mo']=pm['p45_medio_transporte'].astype(int).map(MMAP)
pm=pm[pm['mo'].notna()]; MODOS=['Auto','Público','Activa','Moto','Otros']
modo_sexo={'Hombre':[int(((pm['mo']==mm)&(pm['sexo']==1)).sum()) for mm in MODOS],
           'Mujer':[int(((pm['mo']==mm)&(pm['sexo']==2)).sum()) for mm in MODOS]}
modo_edad={l:[int(((pm['mo']==mm)&(pm['ab']==l)).sum()) for mm in MODOS] for l in ABLAB}
# educación y vivienda y sectores (totales de ciudad, de zona-localidad)
tot=g.sum()
edu={'Primaria':int(tot['n_cine_primaria']),'Secundaria':int(tot['n_cine_secundaria']),'Terciaria':int(tot['n_cine_terciaria_maestria_doctorado'])}
viv={'Casa':int(tot['n_tipo_viv_casa']),'Departamento':int(tot['n_tipo_viv_depto'])}
CAEN=[('n_caenes_B','Minería'),('n_caenes_G','Comercio'),('n_caenes_F','Construcción'),('n_caenes_P','Enseñanza'),
      ('n_caenes_Q','Salud'),('n_caenes_H','Transporte'),('n_caenes_C','Manufactura'),('n_caenes_O','Adm. pública'),('n_caenes_I','Aloj./comida')]
sect={lab:int(tot[c]) for c,lab in CAEN}
sect=dict(sorted(sect.items(),key=lambda kv:-kv[1]))

out={'metrics':[{'key':k,'label':l,'group':gp,'unit':u,'color':c,'inv':inv} for k,l,gp,u,c,inv in METRICS],
     'zona':Z,
     'charts':{'edades':ABLAB,'pir_h':pir_h,'pir_m':pir_m,
               'modos':MODOS,'modo_sexo':modo_sexo,'modo_edad':modo_edad,
               'edu':edu,'viv':viv,'sect':sect}}
json.dump(out,open('antofagasta_censo.json','w',encoding='utf-8'),ensure_ascii=False)
print('zonas con censo: %d/%d · personas (cruces): %d'%(sum(1 for z in Z.values() if z['c_pob']>0),len(ZN),len(p)))
print('pirámide H/M total: %d / %d'%(sum(pir_h),sum(pir_m)))
print('modo al trabajo (H):',dict(zip(MODOS,modo_sexo['Hombre'])))
print('sectores top:',list(sect.items())[:4])
print('-> antofagasta_censo.json')
