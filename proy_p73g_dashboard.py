# -*- coding: utf-8 -*-
"""P73g — DASHBOARD rico de Antofagasta: modelo EOD (proyección) + Censo 2024 (observado).
Compone antofagasta_modelo_zona.json (p73b) + antofagasta_censo.json (p73f) + GeoJSON de zonas.
Nivel de detalle del dashboard EOD: tema claro/oscuro, capas claro/oscuro/satélite, coroplético
multi-métrica (modelo y censo) y cruces del censo en Chart.js (pirámide, modo×sexo/edad, sectores).
Salida: antofagasta_dashboard.html
"""
import sys, json; sys.stdout.reconfigure(encoding='utf-8')
GEOJSON=r'C:\Users\Rodrigo\Análisis RMG\eod-chile\data\geojson\Antofagasta.geojson'
MOD=json.load(open('antofagasta_modelo_zona.json',encoding='utf-8'))
CEN=json.load(open('antofagasta_censo.json',encoding='utf-8'))
GEO=json.load(open(GEOJSON,encoding='utf-8'))
DATA=json.dumps({'mod':MOD,'cen':CEN},ensure_ascii=False)
GEOS=json.dumps(GEO,ensure_ascii=False)

HTML=r'''<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Antofagasta 2024 — Modelo EOD × Censo · explorador</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
:root{--bg:#f4f5f7;--surface:#fff;--sf2:#f4f5f7;--sf3:#e9ecf0;--ink:#1a2330;--ink2:#2b3440;--mut:#5f6670;--mut2:#8a909a;--line:#e3e6ea;--navy:#0f2942;--navy2:#185fa5;--or:#d97706;--shadow:0 1px 4px rgba(15,23,42,.08)}
html.dark{--bg:#0d1117;--surface:#161b22;--sf2:#1c2330;--sf3:#21262d;--ink:#e6edf3;--ink2:#c9d1d9;--mut:#8b949e;--mut2:#6e7681;--line:#30363d;--navy:#58a6ff;--navy2:#79c0ff;--or:#e3b341;--shadow:0 1px 3px rgba(0,0,0,.4)}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,Segoe UI,Roboto,sans-serif;color:var(--ink);background:var(--bg);transition:background .2s,color .2s}
header.hero{background:var(--navy);color:#fff;padding:16px 22px}html.dark header.hero{background:#010409;border-bottom:1px solid var(--line)}
.hero-top{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;flex-wrap:wrap}
.hero-chip{display:inline-block;background:rgba(255,255,255,.14);border:1px solid rgba(255,255,255,.2);border-radius:20px;padding:3px 11px;font-size:11.5px;font-weight:600;letter-spacing:.02em;margin-bottom:7px}
html.dark .hero-chip{background:rgba(88,166,255,.1);border-color:rgba(88,166,255,.25);color:#79c0ff}
h1.hero-title{margin:0;font-size:21px;font-weight:700}.hero-desc{opacity:.82;font-size:13px;margin-top:4px;max-width:760px}
.hero-author{font-size:11.5px;opacity:.7;margin-top:8px}
.theme-btn{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.22);color:#fff;border-radius:9px;width:40px;height:40px;cursor:pointer;font-size:18px;display:flex;align-items:center;justify-content:center;flex:none}
.theme-btn:hover{background:rgba(255,255,255,.22)}
.kpis{display:flex;gap:9px;flex-wrap:wrap;padding:13px 22px;background:var(--surface);border-bottom:1px solid var(--line)}
.kpi{background:var(--sf2);border:1px solid var(--line);border-radius:9px;padding:8px 14px;font-size:12px;color:var(--mut)}
.kpi b{display:block;font-size:18px;color:var(--navy);font-weight:700;margin-bottom:1px}
.wrap{display:flex;gap:0;align-items:stretch;min-height:64vh}
.side{width:260px;flex:none;background:var(--surface);border-right:1px solid var(--line);padding:12px 0;overflow-y:auto;max-height:84vh}
.side .grp{font-size:10.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--mut2);padding:11px 18px 5px}
.side button{display:block;width:100%;text-align:left;border:0;background:none;color:var(--ink2);padding:7px 18px;font-size:13px;cursor:pointer;border-left:3px solid transparent}
.side button:hover{background:var(--sf2)}
.side button.on{background:var(--sf2);border-left-color:var(--or);color:var(--ink);font-weight:600}
.side button .u{float:right;color:var(--mut2);font-size:11px;font-weight:400}
.mapcol{flex:1;position:relative;min-width:0;padding:14px 18px}
#map{height:100%;min-height:460px;border-radius:11px;border:1px solid var(--line)}
.legend,.info{background:var(--surface);color:var(--ink2);padding:8px 11px;border-radius:9px;box-shadow:var(--shadow);border:1px solid var(--line);font-size:12px;line-height:1.55}
.legend b,.info b{color:var(--navy2)}
.legend i{width:14px;height:12px;display:inline-block;margin-right:5px;border-radius:2px;vertical-align:-1px}
.charts{padding:6px 22px 26px;background:var(--bg)}
.charts h2{font-size:16px;color:var(--ink);margin:18px 0 3px}.charts .lead{color:var(--mut);font-size:12.5px;margin:0 0 12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:14px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:11px;padding:13px 15px 10px;box-shadow:var(--shadow)}
.card h3{margin:0 0 2px;font-size:13.5px;color:var(--ink2)}.card p.cap{margin:0 0 8px;font-size:11.5px;color:var(--mut)}
.r2{float:right;font-size:11.5px;font-weight:700;color:#fff;background:var(--navy2);border-radius:6px;padding:1px 8px}
.fitkpis{display:flex;gap:10px;flex-wrap:wrap;margin:2px 0 12px}
.fitkpi{background:var(--surface);border:1px solid var(--line);border-radius:9px;padding:7px 13px;font-size:11.5px;color:var(--mut);box-shadow:var(--shadow)}
.fitkpi b{font-size:16px;color:var(--navy);font-weight:700}.fitkpi .md{display:block;color:var(--mut2);font-size:10.5px;text-transform:uppercase;letter-spacing:.04em}
.card .cv{position:relative;height:230px}
.note{margin:16px 22px;padding:11px 14px;background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--or);border-radius:8px;font-size:12px;color:var(--mut);line-height:1.6}
footer{padding:16px 22px;border-top:1px solid var(--line);font-size:11.5px;color:var(--mut)}footer b{color:var(--navy2)}
@media(max-width:720px){.wrap{flex-direction:column}.side{width:auto;max-height:none;display:flex;flex-wrap:wrap;border-right:0;border-bottom:1px solid var(--line)}.side .grp{width:100%}.side button{width:auto}.mapcol{height:60vh}}
</style></head><body>
<header class="hero"><div class="hero-top"><div>
<span class="hero-chip">ANTOFAGASTA · PROYECCIÓN SIN EOD</span>
<h1 class="hero-title">Movilidad y población de Antofagasta 2024</h1>
<div class="hero-desc">Explorador del <b>modelo EOD×Censo</b> (proyección de demanda transferida de 18 EOD, anclada al Censo 2024 y al SII) junto al <b>Censo 2024 observado</b>, desagregado por zona, sexo, edad, modo, trabajo, educación y vivienda.</div>
<div class="hero-author">Rodrigo Medina González · Universidad de Concepción · Modelo EOD × Censo 2024</div>
</div><button class="theme-btn" id="themeToggle" title="Cambiar tema">🌙</button></div></header>
<div class="kpis" id="kpis"></div>
<div class="wrap"><div class="side" id="side"></div>
<div class="mapcol"><div id="map"></div></div></div>
<div class="note" id="note"></div>
<div class="charts">
<h2>Cruces del Censo 2024 (observado)</h2>
<p class="lead">Distribuciones de la población de Antofagasta (comuna 2101, 401.096 personas) por sexo, edad, modo al trabajo y actividad — la cara empírica que ancla la proyección.</p>
<div class="grid">
<div class="card"><h3>Pirámide etaria por sexo</h3><p class="cap">Población por tramo y sexo</p><div class="cv"><canvas id="ch-pir"></canvas></div></div>
<div class="card"><h3>Modo al trabajo por sexo</h3><p class="cap">Censo P45 · cómo viaja al trabajo cada sexo</p><div class="cv"><canvas id="ch-msx"></canvas></div></div>
<div class="card"><h3>Modo al trabajo por edad</h3><p class="cap">Censo P45 · composición modal por tramo etario</p><div class="cv"><canvas id="ch-med"></canvas></div></div>
<div class="card"><h3>Modelo EOD vs Censo — partición modal</h3><p class="cap">Cuota modal proyectada vs observada al trabajo (3 modos)</p><div class="cv"><canvas id="ch-cmp"></canvas></div></div>
<div class="card"><h3>Sectores económicos (CAENES)</h3><p class="cap">Ocupados por rama · perfil minero-portuario</p><div class="cv"><canvas id="ch-sec"></canvas></div></div>
<div class="card"><h3>Educación y vivienda</h3><p class="cap">Nivel educativo alcanzado y tipo de vivienda</p><div class="cv"><canvas id="ch-ev"></canvas></div></div>
</div>
<h2>Bondad de ajuste — partición modal laboral (modelo vs Censo P45)</h2>
<p class="lead">Para cada modo, la cuota modal <b>laboral</b> predicha por el modelo (eje Y) frente a la observada en el Censo P45 (eje X), zona por zona. La línea punteada es el ajuste perfecto 1:1; el <b>R²</b> mide qué tan cerca caen los puntos de esa recta (1 = perfecto; puede ser negativo si el sesgo domina). Se incluyen las zonas con ≥30 trabajadores con modo declarado.</p>
<div class="fitkpis" id="fitkpis"></div>
<div class="grid">
<div class="card"><h3>Auto <span class="r2" id="r2-auto">·</span></h3><p class="cap">cuota laboral de auto por zona · modelo vs censo</p><div class="cv"><canvas id="fit-auto"></canvas></div></div>
<div class="card"><h3>Público <span class="r2" id="r2-pub">·</span></h3><p class="cap">cuota laboral de público por zona · modelo vs censo</p><div class="cv"><canvas id="fit-pub"></canvas></div></div>
<div class="card"><h3>Activa <span class="r2" id="r2-act">·</span></h3><p class="cap">cuota laboral activa por zona · modelo vs censo</p><div class="cv"><canvas id="fit-act"></canvas></div></div>
</div></div>
<footer>Proyección sin EOD propia: comportamiento transferido del pool de 18 EOD; nivel anclado a Censo 2024, parque INE y SII. El censo es <b>observado</b>; el modelo es <b>escenario condicional</b>. El transporte de personal minero (modo «otros», ≈18% del P45) no lo captura el modelo. · <b>R. Medina G.</b></footer>
<script>
var D=__DATA__, GEO=__GEO__;
var mod=D.mod, cen=D.cen;
/* ---- merge modelo + censo por zona ---- */
var byZ={}; mod.zonas.forEach(function(z){z.m_auto=z.sh[0];z.m_pub=z.sh[1];z.m_act=z.sh[2];byZ[String(z.zona)]=z});
Object.keys(cen.zona).forEach(function(k){var z=byZ[k]||(byZ[k]={zona:k});var c=cen.zona[k];for(var p in c)z[p]=c[p]});
var ZL=Object.keys(byZ).map(function(k){return byZ[k]});
var k=mod.kpi;
document.getElementById("kpis").innerHTML=[
 ["Población 2024",k.pob.toLocaleString("es-CL")],["Viajes/día (modelo)",k.viajes.toLocaleString("es-CL")],
 ["Auto",k.auto+"%"],["Público",k.pub+"%"],["Activa",k.act+"%"],["Dist. media",k.dist+" km"],["Disp. auto",k.av]
].map(function(x){return '<div class="kpi"><b>'+x[1]+'</b>'+x[0]+'</div>'}).join("");

/* ---- métricas: modelo + censo ---- */
var MMET=[
 {key:'gen',label:'Generación',unit:'viajes',color:'#d97706',kind:'count'},
 {key:'atr',label:'Atracción',unit:'viajes',color:'#185fa5',kind:'count'},
 {key:'m_auto',label:'Auto',unit:'%',color:'#c0392b',kind:'num'},
 {key:'m_pub',label:'Público',unit:'%',color:'#185fa5',kind:'num'},
 {key:'m_act',label:'Activa',unit:'%',color:'#1e8449',kind:'num'},
 {key:'dom',label:'Modo dominante',unit:'',color:'',kind:'dom'},
 {key:'od',label:'Flujos O-D',unit:'',color:'',kind:'od'}
];
cen.metrics.forEach(function(m){MMET.push({key:m.key,label:m.label,unit:m.unit,color:m.color,kind:m.key=='c_pob'?'count':'num',group:m.group,inv:m.inv})});
var MET={}; MMET.forEach(function(m){MET[m.key]=m});

/* ---- sidebar agrupado ---- */
var GROUPS=[['Modelo EOD (proyección)',['gen','atr','m_auto','m_pub','m_act','dom','od']]];
var cg={}; cen.metrics.forEach(function(m){(cg[m.group]=cg[m.group]||[]).push(m.key)});
Object.keys(cg).forEach(function(g){GROUPS.push(['Censo · '+g,cg[g]])});
var side=document.getElementById("side"),cur='gen';
GROUPS.forEach(function(G){
 var h=document.createElement("div");h.className="grp";h.textContent=G[0];side.appendChild(h);
 G[1].forEach(function(key){var m=MET[key];var b=document.createElement("button");b.dataset.k=key;
  b.innerHTML=m.label+(m.unit?'<span class="u">'+m.unit+'</span>':'');
  b.onclick=function(){cur=key;[].forEach.call(side.querySelectorAll("button"),function(c){c.classList.remove("on")});b.classList.add("on");draw()};
  side.appendChild(b)});
});

/* ---- mapa + capas claro/oscuro/satélite ---- */
var CL="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    CD="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    SAT="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}";
function isDark(){return document.documentElement.classList.contains("dark")}
var map=L.map("map",{preferCanvas:true}).setView([-23.63,-70.39],12);
var bClaro=L.tileLayer(CL,{attribution:"© OSM © CARTO",maxZoom:19}),
    bOscuro=L.tileLayer(CD,{attribution:"© OSM © CARTO",maxZoom:19}),
    bSat=L.tileLayer(SAT,{attribution:"Imagery © Esri, Maxar, Earthstar Geographics",maxZoom:19});
bClaro.addTo(map);
var baseCtl=L.control.layers({"Mapa claro":bClaro,"Mapa oscuro":bOscuro,"Satélite":bSat},null,{position:"topleft",collapsed:true}).addTo(map);
function syncBase(){ // al cambiar tema, si la base es claro/oscuro la alinea (satélite se respeta)
 if(map.hasLayer(bSat))return;
 if(isDark()){if(map.hasLayer(bClaro)){map.removeLayer(bClaro);bOscuro.addTo(map)}}
 else{if(map.hasLayer(bOscuro)){map.removeLayer(bOscuro);bClaro.addTo(map)}}
}
var info=L.control({position:"topright"});info.onAdd=function(){this._d=L.DomUtil.create("div","info");this.update();return this._d};
info.update=function(h){this._d.innerHTML=h||"<b>Pasa el cursor</b><br>sobre una zona"};info.addTo(map);
var legend=L.control({position:"bottomright"});legend.onAdd=function(){this._d=L.DomUtil.create("div","legend");return this._d};legend.addTo(map);

function mix(a,b,t){function h(x){return[parseInt(x.slice(1,3),16),parseInt(x.slice(3,5),16),parseInt(x.slice(5,7),16)]}var p=h(a),q=h(b);return"#"+p.map(function(v,i){return Math.round(v+(q[i]-v)*t).toString(16).padStart(2,"0")}).join("")}
var DOMC={Auto:"#c0392b","Público":"#185fa5",Activa:"#1e8449"};
var layer=null;
function fmt(x){return (typeof x=="number")?(Math.abs(x)>=1000?Math.round(x).toLocaleString("es-CL"):x):"—"}
function draw(){
 if(layer){map.removeLayer(layer);layer=null}
 var m=MET[cur];
 if(m.kind=='od'){drawOD();return}
 var vals=ZL.map(function(z){return z[cur]}).filter(function(x){return typeof x=="number"}).sort(function(a,b){return a-b});
 var brks=[.2,.4,.6,.8].map(function(p){return vals[Math.floor(p*vals.length)]});
 var base=m.color||"#185fa5",light=mix(isDark()?"#1a2230":"#ffffff",base,.16);
 var ramp=[0,1,2,3,4].map(function(i){return mix(light,base,.16+.84*i/4)});
 function bin(x){var b=0;brks.forEach(function(t){if(x>t)b++});return b}
 var empty=isDark()?"#1a2230":"#eceef1",edge=isDark()?"#0b1220":"#fff";
 layer=L.geoJSON(GEO,{style:function(f){var z=byZ[String(f.properties.zona)];var v=z?z[cur]:null;
   if(m.kind=='dom'){return{fillColor:z&&z.dom?DOMC[z.dom]:empty,fillOpacity:z&&z.dom?.85:.18,color:edge,weight:.5}}
   if(typeof v!="number")return{fillColor:empty,fillOpacity:.18,color:edge,weight:.5};
   return{fillColor:ramp[bin(v)],fillOpacity:.85,color:edge,weight:.5}},
  onEachFeature:function(f,ly){var z=byZ[String(f.properties.zona)];if(!z)return;
   ly.on("mouseover",function(){ly.setStyle({weight:2.2,color:base,fillOpacity:.97});ly.bringToFront();info.update(card(z))});
   ly.on("mouseout",function(){layer.resetStyle(ly);info.update(null)})}}).addTo(map);
 try{map.fitBounds(layer.getBounds().pad(.04))}catch(e){}
 drawLegend(m,brks,ramp);
}
function card(z){
 var rows='<b>Zona '+z.zona+'</b>';
 if(z.c_pob!=null)rows+='<br>Población: <b>'+fmt(z.c_pob)+'</b>';
 if(z.gen!=null)rows+='<br>Generación: <b>'+fmt(z.gen)+'</b> · Atr <b>'+fmt(z.atr)+'</b>';
 if(z.sh)rows+='<br>Modelo A/P/Act: <b>'+z.sh[0]+'/'+z.sh[1]+'/'+z.sh[2]+'%</b>';
 if(z.c_auto!=null)rows+='<br>Censo A/P/Act: <b>'+z.c_auto+'/'+z.c_pub+'/'+z.c_activa+'%</b>';
 var m=MET[cur];if(m.kind!='dom'&&m.kind!='od'&&typeof z[cur]=="number")rows+='<br><span style="color:'+(m.color||'#185fa5')+'">●</span> '+m.label+': <b>'+fmt(z[cur])+(m.unit?' '+m.unit:'')+'</b>';
 return rows;
}
function drawLegend(m,brks,ramp){
 if(m.kind=='dom'){legend._d.innerHTML="<b>Modo dominante</b>"+Object.keys(DOMC).map(function(d){return '<div><i style="background:'+DOMC[d]+'"></i>'+d+'</div>'}).join("");return}
 var f=function(x){return (m.unit=='%'||m.unit=='años')?(Math.round(x*10)/10):Math.round(x).toLocaleString("es-CL")};
 legend._d.innerHTML="<b>"+m.label+"</b>"+(m.unit?' <small>('+m.unit+')</small>':'')+
  [["< "+f(brks[0]),0],[f(brks[0])+"–"+f(brks[1]),1],[f(brks[1])+"–"+f(brks[2]),2],[f(brks[2])+"–"+f(brks[3]),3],["> "+f(brks[3]),4]]
   .map(function(r){return '<div><i style="background:'+ramp[r[1]]+'"></i>'+r[0]+'</div>'}).join("")+
   (m.inv?'<div style="color:var(--mut2);margin-top:3px;font-size:10.5px">↑ peor</div>':'');
}
function drawOD(){
 var mx=mod.od[0].n;layer=L.layerGroup();var col=isDark()?"#e3b341":"#d97706";
 mod.od.forEach(function(p){var w=1.2+p.n/mx*7;L.polyline([[p.olat,p.olng],[p.dlat,p.dlng]],{color:col,weight:w,opacity:.45+p.n/mx*.4}).addTo(layer)
   .bindPopup("<b>Zona "+p.o+" → "+p.d+"</b><br>"+p.n.toLocaleString("es-CL")+" viajes/día")});
 layer.addTo(map);
 legend._d.innerHTML="<b>Flujos O-D</b><br><small>top "+mod.od.length+" pares · grosor ∝ viajes</small>";
}

/* ---- gráficos (Chart.js) ---- */
var charts=[];
function gridc(){return isDark()?"rgba(48,54,61,.7)":"rgba(15,23,42,.06)"}
function tickc(){return isDark()?"#8b949e":"#64748b"}
var MODCOL={Auto:"#c0392b","Público":"#185fa5",Activa:"#1e8449",Moto:"#9333ea",Otros:"#7c3aed"};
function baseOpts(stacked,extra){var o={responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:tickc(),font:{size:11},boxWidth:12}}},
 scales:{x:{stacked:!!stacked,grid:{color:gridc()},ticks:{color:tickc(),font:{size:10}}},y:{stacked:!!stacked,grid:{color:gridc()},ticks:{color:tickc(),font:{size:10}}}}};
 return Object.assign(o,extra||{})}
function buildCharts(){
 charts.forEach(function(c){c.destroy()});charts=[];var c=cen.charts;
 // pirámide (hombres negativos)
 charts.push(new Chart("ch-pir",{type:'bar',data:{labels:c.edades,datasets:[
   {label:'Hombres',data:c.pir_h.map(function(v){return -v}),backgroundColor:'#185fa5'},
   {label:'Mujeres',data:c.pir_m,backgroundColor:'#c026d3'}]},
   options:baseOpts(true,{indexAxis:'y',plugins:{legend:{labels:{color:tickc(),boxWidth:12}},tooltip:{callbacks:{label:function(t){return t.dataset.label+': '+Math.abs(t.raw).toLocaleString('es-CL')}}}},
    scales:{x:{stacked:true,grid:{color:gridc()},ticks:{color:tickc(),font:{size:10},callback:function(v){return Math.abs(v/1000)+'k'}}},y:{stacked:true,grid:{color:gridc()},ticks:{color:tickc(),font:{size:10}}}}})}));
 // modo x sexo (%)
 var ms=c.modo_sexo,sexs=['Hombre','Mujer'];
 var msd=c.modos.map(function(mm,i){return {label:mm,data:sexs.map(function(s){var t=ms[s].reduce(function(a,b){return a+b},0);return t?ms[s][i]/t*100:0}),backgroundColor:MODCOL[mm]}});
 charts.push(new Chart("ch-msx",{type:'bar',data:{labels:sexs,datasets:msd},options:baseOpts(true,{plugins:{legend:{labels:{color:tickc(),boxWidth:12}},tooltip:{callbacks:{label:function(t){return t.dataset.label+': '+t.raw.toFixed(1)+'%'}}}},scales:{x:{stacked:true,grid:{color:gridc()},ticks:{color:tickc(),font:{size:10}}},y:{stacked:true,max:100,grid:{color:gridc()},ticks:{color:tickc(),font:{size:10}}}}})}));
 // modo x edad (%)
 var med=c.modo_edad;
 var medd=c.modos.map(function(mm,i){return {label:mm,data:c.edades.map(function(e){var a=med[e],t=a.reduce(function(x,y){return x+y},0);return t?a[i]/t*100:0}),backgroundColor:MODCOL[mm]}});
 charts.push(new Chart("ch-med",{type:'bar',data:{labels:c.edades,datasets:medd},options:baseOpts(true,{plugins:{legend:{labels:{color:tickc(),boxWidth:12}}},scales:{x:{stacked:true,grid:{color:gridc()},ticks:{color:tickc(),font:{size:10}}},y:{stacked:true,max:100,grid:{color:gridc()},ticks:{color:tickc(),font:{size:10}}}}})}));
 // modelo vs censo (3 modos al trabajo)
 var cm=ms.Hombre.map(function(v,i){return v+ms.Mujer[i]}); // totales por modo
 var iA=c.modos.indexOf('Auto'),iP=c.modos.indexOf('Público'),iAc=c.modos.indexOf('Activa'),iM=c.modos.indexOf('Moto'),iO=c.modos.indexOf('Otros');
 var cAuto=cm[iA],cPub=cm[iP],cAct=cm[iAc]+ (iM>=0?cm[iM]:0), cOtr=iO>=0?cm[iO]:0;
 var tt=cAuto+cPub+cAct; // censo SIN "otros" (personal minero), 3 modos comparables
 var censo3=[cAuto/tt*100,cPub/tt*100,cAct/tt*100];
 var mod3=[k.auto,k.pub,k.act];
 charts.push(new Chart("ch-cmp",{type:'bar',data:{labels:['Auto','Público','Activa'],datasets:[
   {label:'Censo 2024 (obs.)',data:censo3,backgroundColor:'#185fa5'},
   {label:'Modelo EOD (proy.)',data:mod3,backgroundColor:'#d97706'}]},
   options:baseOpts(false,{plugins:{legend:{labels:{color:tickc(),boxWidth:12}},tooltip:{callbacks:{label:function(t){return t.dataset.label+': '+t.raw.toFixed(0)+'%'}}}},scales:{x:{grid:{color:gridc()},ticks:{color:tickc()}},y:{max:60,grid:{color:gridc()},ticks:{color:tickc()}}}})}));
 // sectores
 var se=c.sect,sk=Object.keys(se);
 charts.push(new Chart("ch-sec",{type:'bar',data:{labels:sk,datasets:[{data:sk.map(function(x){return se[x]}),backgroundColor:'#0d9488'}]},
   options:baseOpts(false,{indexAxis:'y',plugins:{legend:{display:false}},scales:{x:{grid:{color:gridc()},ticks:{color:tickc(),font:{size:10}}},y:{grid:{display:false},ticks:{color:tickc(),font:{size:10}}}}})}));
 // educación + vivienda
 var ed=c.edu,vv=c.viv;
 charts.push(new Chart("ch-ev",{type:'bar',data:{labels:['Primaria','Secundaria','Terciaria','Casa','Depto'],
   datasets:[{data:[ed.Primaria,ed.Secundaria,ed.Terciaria,vv.Casa,vv.Departamento],
    backgroundColor:['#94a3b8','#64748b','#2563eb','#16a34a','#9333ea']}]},
   options:baseOpts(false,{plugins:{legend:{display:false}},scales:{x:{grid:{display:false},ticks:{color:tickc(),font:{size:10}}},y:{grid:{color:gridc()},ticks:{color:tickc(),font:{size:10}}}}})}));
 buildFit();
}
/* ---- bondad de ajuste: modelo vs censo, partición modal laboral por zona ---- */
function r2of(P){ // P:[{x:censo,y:modelo}] · R² 1:1 = 1 - SSres/SStot (obs=censo)
 var n=P.length; if(n<3)return null; var mo=0; P.forEach(function(p){mo+=p.x}); mo/=n;
 var ssr=0,sst=0; P.forEach(function(p){ssr+=(p.x-p.y)*(p.x-p.y); sst+=(p.x-mo)*(p.x-mo)});
 return sst>0?1-ssr/sst:null;}
function corr(P){var n=P.length;if(n<3)return null;var mx=0,my=0;P.forEach(function(p){mx+=p.x;my+=p.y});mx/=n;my/=n;
 var sxy=0,sx=0,sy=0;P.forEach(function(p){sxy+=(p.x-mx)*(p.y-my);sx+=(p.x-mx)*(p.x-mx);sy+=(p.y-my)*(p.y-my)});
 return (sx>0&&sy>0)?sxy/Math.sqrt(sx*sy):null;}
function pairs(km,kc){return ZL.filter(function(z){return z.cw_n>=30&&typeof z[km]=="number"&&typeof z[kc]=="number"})
   .map(function(z){return {x:z[kc],y:z[km],z:z.zona}})}
function fitChart(cv,P,col,r2id){
 var r2=r2of(P),rr=corr(P),mxv=0;P.forEach(function(p){mxv=Math.max(mxv,p.x,p.y)});var lim=Math.min(100,Math.ceil((mxv+5)/10)*10);
 var badge=document.getElementById(r2id);if(badge)badge.textContent='R² '+(r2==null?'—':r2.toFixed(2));
 charts.push(new Chart(cv,{data:{datasets:[
   {type:'scatter',label:'zonas',data:P,backgroundColor:col,pointRadius:3.5,pointHoverRadius:5},
   {type:'line',label:'1:1',data:[{x:0,y:0},{x:lim,y:lim}],borderColor:isDark()?'#6e7681':'#9aa7b3',borderDash:[5,4],borderWidth:1.3,pointRadius:0,fill:false}]},
   options:baseOpts(false,{plugins:{legend:{display:false},tooltip:{callbacks:{label:function(t){return t.raw.z?('Zona '+t.raw.z+': censo '+t.raw.x.toFixed(0)+'% · modelo '+t.raw.y.toFixed(0)+'%'):''}}}},
    scales:{x:{type:'linear',min:0,max:lim,title:{display:true,text:'Censo P45 (observado) %',color:tickc(),font:{size:10}},grid:{color:gridc()},ticks:{color:tickc(),font:{size:10}}},
            y:{type:'linear',min:0,max:lim,title:{display:true,text:'Modelo EOD (predicho) %',color:tickc(),font:{size:10}},grid:{color:gridc()},ticks:{color:tickc(),font:{size:10}}}}})}));
 return {r2:r2,r:rr,n:P.length};
}
function buildFit(){
 var fa=fitChart('fit-auto',pairs('w_auto','cw_auto'),'#c0392b','r2-auto');
 var fp=fitChart('fit-pub',pairs('w_pub','cw_pub'),'#185fa5','r2-pub');
 var fc=fitChart('fit-act',pairs('w_act','cw_act'),'#1e8449','r2-act');
 document.getElementById('fitkpis').innerHTML=[['Auto',fa],['Público',fp],['Activa',fc]].map(function(x){
   return '<div class="fitkpi"><span class="md">'+x[0]+'</span><b>R² '+(x[1].r2==null?'—':x[1].r2.toFixed(2))+'</b> · r '+(x[1].r==null?'—':x[1].r.toFixed(2))+' · n='+x[1].n+'</div>'}).join('')+
   '<div class="fitkpi" style="border-left:3px solid var(--or)"><span class="md">Lectura</span>el patrón espacial correlaciona (r), pero el sesgo de nivel del auto baja su R² 1:1</div>';
}

/* ---- tema ---- */
function setTheme(d){document.documentElement.classList.toggle("dark",d);try{localStorage.setItem("theme_anto",d?"dark":"light")}catch(e){}
 document.getElementById("themeToggle").textContent=d?"☀️":"🌙";syncBase();draw();buildCharts()}
document.getElementById("themeToggle").onclick=function(){setTheme(!isDark())};
try{if(localStorage.getItem("theme_anto")=="dark"||(!localStorage.getItem("theme_anto")&&matchMedia("(prefers-color-scheme:dark)").matches))document.documentElement.classList.add("dark")}catch(e){}
document.getElementById("themeToggle").textContent=isDark()?"☀️":"🌙";
map.on("baselayerchange",function(){draw()});

document.getElementById("note").innerHTML="<b>Cómo leer este explorador.</b> El panel izquierdo alterna entre variables del <b>modelo EOD</b> (proyección de viajes: generación, atracción, partición modal, flujos O-D) y del <b>Censo 2024</b> (observado: demografía, modo al trabajo, trabajo, educación, vivienda, conectividad, migración). El mapa admite fondo <b>claro, oscuro o satélite</b> (control arriba a la izquierda) y el botón ☀/🌙 cambia el tema. Validación: la cuota de auto del modelo correlaciona +0,66 por zona con el censo; el nivel de auto se sobre-predice ~6 pp porque el censo registra un modo «otros» (transporte de personal minero, ≈18%) que el modelo no captura.";
side.querySelector("button").classList.add("on");
draw();buildCharts();
</script></body></html>'''
HTML=HTML.replace('__DATA__',DATA).replace('__GEO__',GEOS)
open('antofagasta_dashboard.html','w',encoding='utf-8').write(HTML)
print('-> antofagasta_dashboard.html (%d KB) · métricas modelo+censo · cruces Chart.js · tema+satélite'%(len(HTML)//1024))
