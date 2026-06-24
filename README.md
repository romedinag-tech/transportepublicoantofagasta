# Antofagasta 2024 — proyección de movilidad (sin EOD)

Dashboard interactivo de la movilidad urbana proyectada de Antofagasta al 2024, estimada **sin EOD propia** mediante el modelo de transferencia **EOD × Censo 2024**: el comportamiento de viaje se transfiere del pool de 18 Encuestas Origen-Destino homologadas, y el nivel se ancla localmente al Censo 2024 (población, P45) y al uso de suelo del SII.

👉 **[Ver el dashboard](https://romedinag-tech.github.io/antofagasta/)** (GitHub Pages) · o abrir `index.html` directamente.

## Qué muestra (105 zonas)
- **Generación** y **Atracción** de viajes por zona (coroplético).
- **Intensidad por modo**: Auto / Público / Activa.
- **Modo dominante** por zona.
- **Flujos origen-destino** (líneas de deseo).

## Cómo se estima (procedimiento de transferencia)
1. **Generación**: tasas de viaje por edad del pool × estructura etaria censal de Antofagasta (≈2,33 v/p·día; ciudad joven). Corrección por teletrabajo (33%).
2. **Atracción**: m² por uso del catastro SII de Antofagasta + capas de educación/salud.
3. **Distribución**: gravedad segmentada por propósito con f(d) transferida; el coeficiente de impedancia β se re-calibra a la geometría **lineal** de Antofagasta (~31 km N-S, distancia media objetivo 5 km).
4. **Partición modal**: logit anidado estimado sobre las 18 EOD (sin Antofagasta), aplicado con la disponibilidad de auto, demografía y tamaño urbano locales.

## Escenario y límites (honestidad)
- Es una **proyección sin validación interna** (no hay EOD de Antofagasta): se ancla al Censo 2024 (P45 trabajo: auto 26% / TP 46%).
- Escenario con disponibilidad de auto av = 0,16 autos/persona.
- Aproximaciones: población por zona ≈ m² residencial; demografía/av representativas.
- El **transporte de personal minero** (≈18% del residual P45) no lo captura el modelo (estimado sobre ciudades no mineras).

## Reproducir
`python proy_p73b_dashboard.py` regenera `index.html` (requiere los datos del proyecto EOD: parquet, catastro SII, geojson de zonas).

---
Análisis y desarrollo: Rodrigo Medina González · Universidad de Concepción. Modelo EOD × Censo 2024.
