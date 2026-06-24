# Antofagasta 2024 — proyección de movilidad (sin EOD)

Dashboard interactivo de la movilidad urbana proyectada de Antofagasta al 2024, estimada **sin EOD propia** mediante el modelo de transferencia **EOD × Censo 2024**: el comportamiento de viaje se transfiere del pool de 18 Encuestas Origen-Destino homologadas, y el nivel se ancla localmente al Censo 2024 (población, P45) y al uso de suelo del SII.

👉 **[Ver el dashboard](https://romedinag-tech.github.io/antofagasta/)** (GitHub Pages) · o abrir `index.html` directamente.

## Qué muestra (105 zonas)
Explorador con dos caras de la misma ciudad, conmutables desde el panel lateral:

**Modelo EOD (proyección)**
- **Generación** y **Atracción** de viajes por zona (coroplético).
- **Partición modal** Auto / Público / Activa y **modo dominante** por zona.
- **Flujos origen-destino** (líneas de deseo).

**Censo 2024 (observado)** — desagregado por zona y cruzado por sexo / edad / modo:
- **Demografía**: población, % mujeres, edad promedio, % 0-17 y % 60+.
- **Movilidad al trabajo (P45)**: auto, público, activa, otros/personal.
- **Trabajo y educación**: tasa de desocupación, escolaridad, % terciaria.
- **Vivienda**: % departamentos, hacinamiento, tenencia propia, jefatura femenina.
- **Conectividad y migración**: % internet, % inmigrantes, % pueblos originarios.
- **Cruces de ciudad (Chart.js)**: pirámide etaria por sexo, modo al trabajo por sexo y por edad, **modelo EOD vs censo**, sectores económicos (CAENES) y educación/vivienda.

**Mapa**: fondo conmutable **claro / oscuro / satélite** (Esri) y **tema claro/oscuro** de toda la interfaz (botón ☀/🌙, recuerda la preferencia).

## Cómo se estima (procedimiento de transferencia)
1. **Generación**: población del **Censo 2024 por zona × edad** (unión espacial de las zonas censales a las 105 zonas EOD) × tasas de viaje por edad del pool. ≈860.000 viajes/día (≈2,2 v/p·día; ciudad joven). Corrección por teletrabajo (33%). La desagregación por edad se **conserva hasta la distribución**: cada zona reparte su generación entre propósitos con la cuota propósito-por-edad del pool, no con una mezcla única de ciudad → una zona joven origina más viajes de estudio, una zona activa más de trabajo (cuota de estudio en el origen ~ fracción joven de la zona, corr 0,99).
2. **Atracción**: m² por uso del catastro SII de Antofagasta + capas de educación/salud. El atractor de **estudio se pondera por nivel** (jardín 0,15 / colegio 0,62 / superior 0,23) según la mezcla etaria de los viajes de estudio del pool, en vez de sumar todos los establecimientos por igual.
3. **Distribución**: gravedad segmentada por propósito con f(d) transferida y **orígenes propios por propósito** (resueltos por la estructura etaria de cada zona); el coeficiente β se calibra a la distancia media de la ciudad (que Antofagasta no tiene medida → ver supuestos abajo).
4. **Partición modal**: logit **anidado** (1º activo/motorizado, 2º auto/público) estimado sobre las 18 EOD (sin Antofagasta), aplicado con los insumos de la **zona de ORIGEN**, no constantes de ciudad: **av, sexo y edad por zona**. La av por zona combina el nivel INE comunal (0,18) con el ranking de ingreso por **valor de propiedad SII** y el gradiente ingreso→av del pool (Q1–Q5 = 0,11–0,37) → el sur acomodado tiene más auto (av 0,21) que el norte (0,16).

**Validación espacial (Censo P45 por zona):** la cuota de auto simulada correlaciona **+0,66** con la del censo por zona (antes, con insumos uniformes, era −0,34): el sur de altos ingresos sale con más auto, como en el censo. La brecha de género (hombre−mujer en auto) coincide en **11 pp** con el censo. El nivel global de auto aún se sobre-predice ~6 pp (no captura el transporte de personal minero ni el alto uso de TP de Antofagasta).

> La **metodología validada** (cada valor demostrado en la investigación) vive aparte, en `METODOLOGIA.md` del proyecto EOD. Lo de abajo NO es metodología: son decisiones específicas y provisionales para estudiar Antofagasta sin EOD.

## Supuestos de ESTE estudio (provisionales)
Como Antofagasta no tiene EOD, estos valores son atajos del estudio, no reglas del método. Con una EOD se reemplazan por dato:
- **β / distancia media**: sin O-D medida, la distancia media se predijo con una relación auxiliar dist↔extensión ajustada sobre las 18 EOD (R²≈0,71) → ≈3,56 km, y β se calibró a ella. Es un atajo de un solo análisis.
- **Teletrabajo**: factor de sustitución de viajes (0,5) supuesto.

> La **generación, la población por zona y la disponibilidad de auto ya NO son aproximaciones**: usan dato real — **Censo 2024** por zona × edad (unión espacial zona censal → zona EOD) y **parque INE 2024** (72.139 automóviles → av 0,18 autos/persona). Antes se usaban proxies; corregido. Quedan provisionales solo la β (relación auxiliar) y el factor de teletrabajo.

## Límites (honestidad)
- **Proyección sin validación interna** (no hay EOD de Antofagasta): se ancla al Censo 2024 (P45 trabajo: auto 26% / TP 46%).
- Sin O-D medida, los flujos largos quedan repartidos en muchos pares chicos → el top por volumen sale corto (los commutes norte→centro existen, pero difusos).
- El **transporte de personal minero** (≈18% del residual P45) no lo captura el modelo (estimado sobre ciudades no mineras).

## Reproducir
Pipeline (requiere los datos del proyecto EOD: parquet del Censo 2024, catastro SII, geojson de zonas, parque INE):
1. `python proy_p73c_pop_censo.py` · `python proy_p73e_zona_inputs.py` — insumos por zona (población censal, av/sexo/edad).
2. `python proy_p73b_dashboard.py` — corre el modelo de 4 etapas → `antofagasta_modelo_zona.json`.
3. `python proy_p73f_censo_zona.py` — extrae el Censo 2024 desagregado por zona y los cruces de ciudad → `antofagasta_censo.json`.
4. `python proy_p73g_dashboard.py` — compone el explorador → `index.html`.
5. `python proy_p73d_consistencia_zona.py` — valida modelo vs censo por zona (corr +0,66).

Los `*.json` quedan versionados, así que el `index.html` es autocontenido (no necesita los parquet para verse).

---
Análisis y desarrollo: Rodrigo Medina González · Universidad de Concepción. Modelo EOD × Censo 2024.
