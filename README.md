# Transporte Público Antofagasta — Centro de Mando

Tablero analítico **estático** (HTML + ECharts + Leaflet) del transporte público de
**Antofagasta**, sobre datos GPS históricos de la flota (SAIP MTT/DTPR) + GTFS estático.

- **Período de datos:** junio 2025 · **11,8 millones** de pulsos GPS · **714 buses** · **13 líneas**.
- **Stack:** histórico 100% local con DuckDB sobre Parquet (costo ~0); tablero estático publicable
  en GitHub Pages. Réplica del motor del Gran Concepción.
- **Métricas:** flota / velocidad / % detenido por línea×hora, cumplimiento de frecuencia
  (GTFS programado vs despachos GPS observados), geometría oficial de líneas y paraderos.

> Nota: el GTFS vigente es de 2026; el GPS es de junio 2025. La malla de líneas coincide 100%.
> Los modos de mapa que dependen de EOD (cobertura/transbordo/espera) se incorporan cuando
> esté disponible la Encuesta Origen-Destino de Antofagasta.

Publicado con GitHub Pages desde la raíz (`index.html`).
