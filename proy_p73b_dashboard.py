# -*- coding: utf-8 -*-
"""P73b — Dashboard HTML autocontenido de la proyección de Antofagasta 2024 (sin EOD).
Reusa el pipeline de proy_p73 y agrega métricas POR ZONA (generación, atracción, volumen por
modo, modo dominante) + flujos O-D, y emite antofagasta_dashboard.html (coroplético tipo EOD).
"""
import sys, re, glob, os, json; sys.stdout.reconfigure(encoding='utf-8')
import pandas as pd, numpy as np, warnings; warnings.filterwarnings('ignore')
from scipy.spatial import cKDTree
CITY='Antofagasta'; POB=401096; TELETRAB=0.331; PCT60=0.144; AV=0.16
TASA_PC=2.33      # tasas-edad del pool × estructura etaria censal de Antofagasta (joven: 34% en 25-44) — metodología §1
TARGET_DIST=5.0   # distancia media objetivo (km) para calibrar β a la geometría LINEAL (31 km N-S); 1 g.l./ciudad
GIS=r'C:\Users\Rodrigo\Análisis RMG\GIS Gran Concepción\Analisis uso de suelo Gran Concepción'; OTROS=GIS+r'\otros datos'
GEOJSON=r'C:\Users\Rodrigo\Análisis RMG\eod-chile\data\geojson\Antofagasta.geojson'
def nz(z): return re.sub(r'\.0$','',str(z).strip())
def hav(lo1,la1,lo2,la2):
    R=6371.0;p1,p2=np.radians(la1),np.radians(la2)
    a=np.sin(np.radians(la2-la1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin(np.radians(lo2-lo1)/2)**2
    return 2*R*np.arcsin(np.sqrt(a))

cent=pd.read_parquet('EOD_PARQUET/zonas_centroides.parquet'); cent=cent[cent['ciudad'].astype(str)==CITY].dropna(subset=['lat','lon']).copy()
cent['zona']=cent['zona'].map(nz); cent=cent.drop_duplicates('zona').reset_index(drop=True)
ZN=cent['zona'].values; LAT=cent['lat'].astype(float).values; LON=cent['lon'].astype(float).values; n=len(ZN); idx={z:i for i,z in enumerate(ZN)}
la0,la1,lo0,lo1=LAT.min()-.05,LAT.max()+.05,LON.min()-.05,LON.max()+.05; tree=cKDTree(np.column_stack([LAT,LON]))
DST=np.zeros((n,n))
for i in range(n): DST[i]=hav(np.full(n,LON[i]),np.full(n,LAT[i]),LON,LAT)
np.fill_diagonal(DST,0.4)

def load_pts(key):
    subs=glob.glob(OTROS+'\\'+key+'*'); shp=None
    for s in subs:
        if os.path.isdir(s):
            gg=glob.glob(s+r'\*.shp')
            if gg: shp=gg[0]; break
    if not shp: return np.zeros(n)
    import geopandas as gpd
    g=gpd.read_file(shp)
    try: g=g.to_crs(4326)
    except: pass
    df=pd.DataFrame({'lat':g.geometry.y,'lon':g.geometry.x}).dropna(); df=df[df['lat'].between(la0,la1)&df['lon'].between(lo0,lo1)]
    w=np.zeros(n)
    if len(df): _,zi=tree.query(df[['lat','lon']].values); [w.__setitem__(i,w[i]+1) for i in zi]
    return w
A_est=load_pts('layer_jardines_infantiles_junji')+load_pts('layer_establecimientos_educacion_escolar')+load_pts('layer_establecimientos_de_educacion_superior')
SAL=np.zeros(n)
try:
    import geopandas as gpd
    sg=gpd.read_file(OTROS+r'\l_990_v1_establecimientos_de_salud_febrero_2026.geojson')
    try: sg=sg.to_crs(4326)
    except: pass
    sg['lat']=sg.geometry.y; sg['lon']=sg.geometry.x; sg=sg[sg['lat'].between(la0,la1)&sg['lon'].between(lo0,lo1)]
    if len(sg): _,zi=tree.query(sg[['lat','lon']].values); [SAL.__setitem__(i,SAL[i]+1) for i in zi]
except: pass
cat=pd.read_parquet(glob.glob(GIS+r'\comunas_parquet\Antofagasta_2201.parquet')[0],columns=['destinoDescripcion','sup_construida_total','lat','lon'])
cat['m2']=pd.to_numeric(cat['sup_construida_total'],errors='coerce').fillna(0)
cat['lat']=pd.to_numeric(cat['lat'],errors='coerce'); cat['lon']=pd.to_numeric(cat['lon'],errors='coerce'); cat=cat.dropna(subset=['lat','lon'])
cat=cat[cat['lat'].between(la0,la1)&cat['lon'].between(lo0,lo1)]; _,zi=tree.query(cat[['lat','lon']].values); cat['zi']=zi
m2_of=lambda u: cat[cat['destinoDescripcion'].isin(u)].groupby('zi')['m2'].sum().reindex(range(n)).fillna(0).values
A_pop=m2_of(['HABITACIONAL']); A_trab=m2_of(['OFICINA','COMERCIO','INDUSTRIA','ADM. PUBLICA Y DEFENSA','BODEGA Y ALMACENAJE']); A_com=m2_of(['COMERCIO'])
if A_pop.sum()==0: A_pop=np.ones(n)

# generación + distribución segmentada (transferida)
red_tele=0.31*TELETRAB*0.5; viajes=POB*TASA_PC*(1-red_tele); O_pop=A_pop/A_pop.sum()
v=pd.read_parquet('EOD_PARQUET/viajes_analiticos.parquet',columns=['proposito_h','factor']); v['factor']=pd.to_numeric(v['factor'],errors='coerce'); v=v.dropna(subset=['factor'])
psh=(v.groupby(v['proposito_h'].astype('string'))['factor'].sum()); psh=(psh/psh.sum()).to_dict()
PMAP={'Trabajo':(A_trab,0.30),'Estudio':(A_est,0.45),'Salud':(SAL,0.22),'Compras':(A_com,0.40),'Trámites':(A_trab,0.40),'Comer':(A_com,0.50),'Recreación':(A_com+0.3*A_pop,0.40),'Volver a casa':(A_pop,0.30),'Buscar/Dejar':(A_pop+0.5*A_com,0.45)}
DEF=(A_com+0.3*A_pop,0.45)
def gravity(O,A,beta):
    F=np.exp(-beta*DST)*np.maximum(A,1e-9)[None,:]; F=F/F.sum(1,keepdims=True); return O[:,None]*np.nan_to_num(F)
def build_T(bscale):
    Tt=np.zeros((n,n))
    for pr,sh in psh.items():
        if sh>0: A,beta=PMAP.get(str(pr),DEF); Tt+=gravity(viajes*sh*O_pop,A,beta*bscale)
    return Tt
# calibrar escala global de β (1 g.l.) para que la distancia media = TARGET_DIST (geometría lineal)
lo,hi=0.08,1.0
for _ in range(34):
    mid=(lo+hi)/2; dm=np.average(DST,weights=build_T(mid))
    if dm<TARGET_DIST: hi=mid
    else: lo=mid
BSCALE=(lo+hi)/2; T=build_T(BSCALE)
print('  β recalibrada ×%.3f -> distancia media %.2f km (objetivo %.1f)'%(BSCALE,np.average(DST,weights=T),TARGET_DIST))

# modal por celda (logit anidado transferido) -> volúmenes por modo
C=json.load(open('proy_p33_coef.json')); par=np.array(C['par']); ST=C['ST']; COLS=C['COLS']; na=len(COLS)+1; lam=1/(1+np.exp(-par[2*na]))
female,youth,elderly,trabajo,estudio=0.50,0.36,PCT60,psh.get('Trabajo',0.17),psh.get('Estudio',0.14); lsize=np.log(viajes)
ba=par[:na]; bp=par[na:2*na]
logd=np.log(np.clip(DST,0.2,None)); lz=(logd-ST['logd'][0])/ST['logd'][1]; avz=(AV-ST['av'][0])/ST['av'][1]; sz=(lsize-ST['lsize'][0])/ST['lsize'][1]; axs=avz*sz; o=np.ones((n,n))
U=lambda b: b[0]*o+b[1]*lz+b[2]*avz+b[3]*female+b[4]*youth+b[5]*elderly+b[6]*trabajo+b[7]*estudio+b[8]*sz+b[9]*axs
a=U(ba)/lam; bb=U(bp)/lam; mx=np.maximum(a,bb); LS=mx+np.log(np.exp(a-mx)+np.exp(bb-mx)); logD=np.logaddexp(0,lam*LS); Pm=np.exp(lam*LS-logD)
Pa=Pm*np.exp(a-LS); Pp=Pm*np.exp(bb-LS); Pw=np.exp(-logD)
Tauto=T*Pa; Tpub=T*Pp; Tact=T*Pw

# métricas por zona
gen=T.sum(1); atr=T.sum(0); auto_z=Tauto.sum(1); pub_z=Tpub.sum(1); act_z=Tact.sum(1)
tot=gen.copy(); tot[tot==0]=1
modos=['Auto','Público','Activa']
zonas=[]
for i in range(n):
    sh=[auto_z[i]/tot[i]*100,pub_z[i]/tot[i]*100,act_z[i]/tot[i]*100]
    zonas.append({'zona':ZN[i],'lat':round(float(LAT[i]),5),'lng':round(float(LON[i]),5),
        'gen':round(float(gen[i])),'atr':round(float(atr[i])),
        'auto':round(float(auto_z[i])),'pub':round(float(pub_z[i])),'act':round(float(act_z[i])),
        'dom':modos[int(np.argmax(sh))],'sh':[round(x) for x in sh]})
# flujos OD top
pairs=[]
for i in range(n):
    for j in range(n):
        if i!=j and T[i,j]>0: pairs.append((float(T[i,j]),ZN[i],ZN[j],float(LAT[i]),float(LON[i]),float(LAT[j]),float(LON[j])))
pairs.sort(reverse=True); pairs=pairs[:70]
od=[{'o':p[1],'d':p[2],'olat':round(p[3],5),'olng':round(p[4],5),'dlat':round(p[5],5),'dlng':round(p[6],5),'n':round(p[0])} for p in pairs]
kpi={'pob':POB,'viajes':round(viajes),'auto':round(Tauto.sum()/T.sum()*100),'pub':round(Tpub.sum()/T.sum()*100),'act':round(Tact.sum()/T.sum()*100),'dist':round(np.average(DST,weights=T),2),'av':AV}
GEO=json.load(open(GEOJSON,encoding='utf-8'))
print('zonas %d · viajes %d · modal %d/%d/%d · od pares %d'%(n,kpi['viajes'],kpi['auto'],kpi['pub'],kpi['act'],len(od)))

# ---- HTML autocontenido ----
DATA=json.dumps({'zonas':zonas,'od':od,'kpi':kpi},ensure_ascii=False)
GEOS=json.dumps(GEO,ensure_ascii=False)
html=r'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Antofagasta 2024 — proyección EOD×Censo (sin EOD)</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
:root{--navy:#0f2942;--or:#d97706}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;color:#1a2330;background:#f4f5f7}
header{background:var(--navy);color:#fff;padding:14px 20px}h1{margin:0;font-size:19px}.sub{opacity:.8;font-size:13px;margin-top:3px}
.kpis{display:flex;gap:10px;flex-wrap:wrap;padding:12px 20px;background:#fff;border-bottom:1px solid #e3e6ea}
.kpi{background:#f4f5f7;border-radius:8px;padding:8px 14px;font-size:13px}.kpi b{display:block;font-size:18px;color:var(--navy)}
.bar{display:flex;gap:6px;flex-wrap:wrap;padding:12px 20px;align-items:center}
button{border:1px solid #cfd4da;background:#fff;border-radius:20px;padding:7px 14px;cursor:pointer;font-size:13px}
button.on{background:var(--navy);color:#fff;border-color:var(--navy)}
#map{height:62vh;min-height:440px;margin:0 20px 20px;border-radius:10px;border:1px solid #e3e6ea}
.note{padding:0 20px 20px;font-size:12px;color:#5f6670;max-width:900px}
.legend{background:#fff;padding:8px 10px;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.2);font-size:12px;line-height:1.5}
.info{background:#fff;padding:8px 10px;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,.2);font-size:12px;min-width:150px}
.leaflet-popup-content{font-size:13px}
</style></head><body>
<header><h1>Antofagasta 2024 — proyección de movilidad (sin EOD)</h1>
<div class="sub">Modelo EOD×Censo transferido · comportamiento de 18 EOD + Censo 2024 + uso de suelo SII · 105 zonas</div></header>
<div class="kpis" id="kpis"></div>
<div class="bar" id="bar"></div>
<div id="map"></div>
<div class="note" id="note"></div>
<script>
var DATA=__DATA__, GEO=__GEO__;
var NAVY="#0f2942",OR="#d97706";
var VIEWS=[["gen","Generación","#d97706"],["atr","Atracción","#185fa5"],["auto","Auto","#c0392b"],["pub","Público","#185fa5"],["act","Activa","#1e8449"],["dom","Modo dominante",""],["od","Flujos O-D",""]];
var byZ={}; DATA.zonas.forEach(function(z){byZ[String(z.zona)]=z});
var k=DATA.kpi;
document.getElementById("kpis").innerHTML=[
 ["Población 2024",k.pob.toLocaleString("es-CL")],["Viajes/día",k.viajes.toLocaleString("es-CL")],
 ["Auto",k.auto+"%"],["Público",k.pub+"%"],["Activa",k.act+"%"],["Dist. media",k.dist+" km"]
].map(function(x){return '<div class="kpi">'+x[1]+'<small style="color:#5f6670;font-weight:normal"> '+x[0]+'</small></div>'}).join("");
var map=L.map("map",{preferCanvas:true}).setView([(-23.63),( -70.39)],12);
L.tileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",{attribution:"© OpenStreetMap © CARTO",maxZoom:19}).addTo(map);
var info=L.control({position:"topright"});info.onAdd=function(){this._d=L.DomUtil.create("div","info");this._d.innerHTML="<b>Pasa el cursor</b><br>sobre una zona";return this._d};info.update=function(h){this._d.innerHTML=h||"<b>Pasa el cursor</b><br>sobre una zona"};info.addTo(map);
var legend=L.control({position:"bottomright"});legend.onAdd=function(){this._d=L.DomUtil.create("div","legend");return this._d};legend.addTo(map);
var DOMC={Auto:"#c0392b","Público":"#185fa5",Activa:"#1e8449"};
function mix(a,b,t){function h(x){return [parseInt(x.slice(1,3),16),parseInt(x.slice(3,5),16),parseInt(x.slice(5,7),16)]}var p=h(a),q=h(b);return "#"+p.map(function(v,i){return Math.round(v+(q[i]-v)*t).toString(16).padStart(2,"0")}).join("")}
var layer=null,view="gen";
function val(z,v){return v==="dom"?z.dom:z[v]}
function draw(){
 if(layer)map.removeLayer(layer);
 var cfg=VIEWS.find(function(x){return x[0]===view});
 if(view==="od"){drawOD();return}
 var vals=DATA.zonas.map(function(z){return val(z,view)}).filter(function(x){return typeof x==="number"&&x>0}).sort(function(a,b){return a-b});
 var brks=[.2,.4,.6,.8].map(function(p){return vals[Math.floor(p*vals.length)]});
 var light=view==="dom"?"#eee":mix("#ffffff",cfg[2],.18),base=cfg[2];
 var ramp=[0,1,2,3,4].map(function(i){return mix(light,base,.18+.82*i/4)});
 function bin(x){var b=0;brks.forEach(function(t){if(x>t)b++});return b}
 layer=L.geoJSON(GEO,{style:function(f){var z=byZ[String(f.properties.zona)];if(!z)return{fillOpacity:.05,weight:.5,color:"#fff"};
   var c=view==="dom"?DOMC[z.dom]:ramp[bin(z[view])];return{fillColor:c,fillOpacity:.82,color:"#fff",weight:.5}},
  onEachFeature:function(f,ly){var z=byZ[String(f.properties.zona)];if(!z)return;
   ly.on("mouseover",function(){ly.setStyle({weight:2.2,color:base||NAVY,fillOpacity:.95});ly.bringToFront();
    info.update("<b>Zona "+z.zona+"</b><br>Generación: <b>"+z.gen.toLocaleString("es-CL")+"</b><br>Atracción: <b>"+z.atr.toLocaleString("es-CL")+"</b><br>Auto/Púb/Activa: <b>"+z.sh[0]+"/"+z.sh[1]+"/"+z.sh[2]+"%</b><br>Modo dominante: <b>"+z.dom+"</b>")});
   ly.on("mouseout",function(){layer.resetStyle(ly);info.update(null)});
   ly.bindPopup("<b>Zona "+z.zona+"</b><br>Gen "+z.gen.toLocaleString("es-CL")+" · Atr "+z.atr.toLocaleString("es-CL")+"<br>Auto "+z.auto.toLocaleString("es-CL")+" · Púb "+z.pub.toLocaleString("es-CL")+" · Activa "+z.act.toLocaleString("es-CL"));}}).addTo(map);
 try{map.fitBounds(layer.getBounds().pad(.05))}catch(e){}
 if(view==="dom"){legend._d.innerHTML="<b>Modo dominante</b>"+Object.keys(DOMC).map(function(m){return '<div><span style="display:inline-block;width:14px;height:12px;background:'+DOMC[m]+'"></span> '+m+'</div>'}).join("")}
 else{var f=function(x){return Math.round(x).toLocaleString("es-CL")};
  legend._d.innerHTML="<b>"+cfg[1]+"</b><br><small>viajes/zona</small>"+[["< "+f(brks[0]),0],[f(brks[0])+"–"+f(brks[1]),1],[f(brks[1])+"–"+f(brks[2]),2],[f(brks[2])+"–"+f(brks[3]),3],["> "+f(brks[3]),4]].map(function(r){return '<div><span style="display:inline-block;width:14px;height:12px;background:'+ramp[r[1]]+'"></span> '+r[0]+'</div>'}).join("")}
}
function drawOD(){
 var mx=DATA.od[0].n;layer=L.layerGroup();
 DATA.od.forEach(function(p){var w=1.2+p.n/mx*7;L.polyline([[p.olat,p.olng],[p.dlat,p.dlng]],{color:OR,weight:w,opacity:.5+p.n/mx*.4}).addTo(layer)
   .bindPopup("<b>Zona "+p.o+" → "+p.d+"</b><br>"+p.n.toLocaleString("es-CL")+" viajes/día")});
 layer.addTo(map);
 legend._d.innerHTML="<b>Flujos O-D</b><br><small>top "+DATA.od.length+" pares · grosor ∝ viajes</small>"
}
var bar=document.getElementById("bar");
VIEWS.forEach(function(x){var b=document.createElement("button");b.textContent=x[1];b.onclick=function(){view=x[0];[].forEach.call(bar.children,function(c){c.classList.remove("on")});b.classList.add("on");draw()};bar.appendChild(b)});
bar.children[0].classList.add("on");
document.getElementById("note").innerHTML="<b>Proyección sin EOD</b> (procedimiento de transferencia): el comportamiento viene del pool de 18 EOD; el nivel se ancla al Censo 2024 (P45 trabajo: auto 26%/TP 46%) y al uso de suelo SII de Antofagasta. <b>Escenario</b> con disponibilidad de auto av="+k.av+" autos/persona. Aproximaciones: población por zona ≈ m² residencial; demografía/av representativas; el transporte de personal minero (≈18% del P45) no lo captura el modelo. Sin EOD propia no hay validación interna.";
draw();
</script></body></html>'''
html=html.replace('__DATA__',DATA).replace('__GEO__',GEOS)
open('antofagasta_dashboard.html','w',encoding='utf-8').write(html)
print('-> antofagasta_dashboard.html (%d KB)'%(len(html)//1024))
