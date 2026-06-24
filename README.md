# Antofagasta 2024 — proyección de movilidad (sin EOD)

Dashboard interactivo de la movilidad urbana proyectada de Antofagasta al 2024, estimada **sin EOD propia** mediante el modelo de transferencia **EOD × Censo 2024**: el comportamiento de viaje se transfiere del pool de 18 Encuestas Origen-Destino homologadas, y el nivel se ancla localmente al Censo 2024 (población, P45) y al uso de suelo del SII.

👉 **[Ver el dashboard](https://romedinag-tech.github.io/antofagasta/)** (GitHub Pages) · o abrir `index.html` directamente.

## Qué muestra (105 zonas)
- **Generación** y **Atracción** de viajes por zona (coroplético).
- **Intensidad por modo**: Auto / Público / Activa.
- **Modo dominante** por zona.
- **Flujos origen-destino** (líneas de deseo).

## Cómo se estima (procedimiento de transferencia)
1. **Generación**: población del **Censo 2024 por zona × edad** (unión espacial de las zonas censales a las 105 zonas EOD) × tasas de viaje por edad del pool. ≈860.000 viajes/día (≈2,2 v/p·día; ciudad joven). Corrección por teletrabajo (33%).
2. **Atracción**: m² por uso del catastro SII de Antofagasta + capas de educación/salud.
3. **Distribución**: gravedad segmentada por propósito con f(d) transferida; el coeficiente β se calibra a la distancia media de la ciudad (que Antofagasta no tiene medida → ver supuestos abajo).
4. **Partición modal**: logit anidado estimado sobre las 18 EOD (sin Antofagasta), aplicado con la disponibilidad de auto, demografía y tamaño urbano locales.

> La **metodología validada** (cada valor demostrado en la investigación) vive aparte, en `METODOLOGIA.md` del proyecto EOD. Lo de abajo NO es metodología: son decisiones específicas y provisionales para estudiar Antofagasta sin EOD.

## Supuestos de ESTE estudio (provisionales)
Como Antofagasta no tiene EOD, estos valores son atajos del estudio, no reglas del método. Con una EOD se reemplazan por dato:
- **β / distancia media**: sin O-D medida, la distancia media se predijo con una relación auxiliar dist↔extensión ajustada sobre las 18 EOD (R²≈0,71) → ≈3,56 km, y β se calibró a ella. Es un atajo de un solo análisis.
- **Disponibilidad de auto**: av = 0,16 autos/persona (representativa; idealmente parque INE por hogar).
- **Teletrabajo**: factor de sustitución de viajes (0,5) supuesto.

> La **generación y la población por zona ya NO son aproximaciones**: usan el **Censo 2024 real por zona × edad** (unión espacial zona censal → zona EOD). Antes se usaba un proxy de m² residencial; corregido.

## Límites (honestidad)
- **Proyección sin validación interna** (no hay EOD de Antofagasta): se ancla al Censo 2024 (P45 trabajo: auto 26% / TP 46%).
- Sin O-D medida, los flujos largos quedan repartidos en muchos pares chicos → el top por volumen sale corto (los commutes norte→centro existen, pero difusos).
- El **transporte de personal minero** (≈18% del residual P45) no lo captura el modelo (estimado sobre ciudades no mineras).

## Reproducir
`python proy_p73b_dashboard.py` regenera `index.html` (requiere los datos del proyecto EOD: parquet, catastro SII, geojson de zonas).

---
Análisis y desarrollo: Rodrigo Medina González · Universidad de Concepción. Modelo EOD × Censo 2024.
