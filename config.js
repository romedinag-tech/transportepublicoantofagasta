/* Config de ciudad para el shell compartido (_motor/dashboard_kit). El shell es IDÉNTICO entre ciudades;
   solo cambia este archivo + data/. Una mejora transversal se hace en el kit y se despliega con deploy_dashboard.py. */
window.CITY = {
  slug: "antofagasta",
  nombre: "Antofagasta",
  sigla: "AF",
  lat0: -23.65, lon0: -70.40,
  comunas: ["Antofagasta"],            // 1 comuna → sin pestañas por comuna, sin ranking/comparador
  comunasGeojson: "comuna_antofagasta.geojson",
  live: false,                          // estático: sin feed GTFS-RT
  liveBase: "",
  repo: "transportepublicoAntofagasta",
  voz: { ejeSing: "eje", ejePlur: "ejes", EjePlur: "Ejes" },   // Antofagasta no tiene corredores segregados
};
