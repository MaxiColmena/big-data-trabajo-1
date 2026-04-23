# 📊 FIFA Dataset Analysis - Dashboard Interactivo

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0%2B-150458?logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.24%2B-013243?logo=numpy&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.0%2B-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**Análisis exploratorio de datos y visualizaciones interactivas del dataset FIFA**

[Ver Dashboard](#-dashboard-interactivo) • [Instalación](#-instalación) • [Uso](#-uso) • [Documentación](#-documentación)

</div>

---

## 📖 Introducción

Este repositorio contiene un **análisis exploratorio de datos (EDA) completo** del dataset de jugadores de FIFA, implementando un pipeline de procesamiento de datos con Python y generando un **dashboard interactivo** con visualizaciones profesionales.

### 🎯 Objetivos del Proyecto

| Objetivo | Descripción |
|----------|-------------|
| **Análisis de datos** | Explorar y comprender la estructura del dataset FIFA |
| **Preprocesamiento** | Limpiar y transformar datos para análisis |
| **Visualización** | Crear gráficos interactivos para comunicación efectiva |
| **Documentación** | Generar reportes comprensibles para stakeholders |

### 🏆 Resultados

- ✅ **18,207 jugadores analizados** de 164 países
- ✅ **4 visualizaciones interactivas** generadas
- ✅ **Dashboard unificado** con navegación y explicaciones
- ✅ **Pipeline reproducible** documentado

---

## 📁 Estructura del Proyecto

```
big-data-trabajo-1/
│
├── 📄 README.md                    # Documentación completa del proyecto
├── 📄 fifa.csv                     # Dataset original (18,207 registros)
│
├── 🐍 generate_unified_dashboard.py # Script principal de generación
├── 🐍 fifa_visualizations.py       # Módulo de visualizaciones (alternativo)
│
├── 🌐 fifa_dashboard_completo.html # Dashboard interactivo final
│
└── 📂 .claude/                    # Configuración de agentes
    └── 📂 agents/
        ├── csv-data-analyst.md
        └── data-visualization-specialist.md
```

---

## 🗃️ Descripción del Dataset

### Origen y Contexto

El dataset **FIFA Player Statistics** contiene información detallada de jugadores de fútbol profesional, extraída de la base de datos del videojuego FIFA. Los datos incluyen características demográficas, habilidades técnicas, atributos físicos y valores de mercado.

### 📌 Actividad 1 — Fuente de Datos

El dataset utilizado en este proyecto, **FIFA Player Statistics**, fue extraído de [Kaggle](https://www.kaggle.com/), una plataforma pública de ciencia de datos que aloja datasets listos para análisis. El archivo `fifa.csv` contiene información de jugadores registrados en el videojuego FIFA 19, incluyendo atributos de juego, datos demográficos y valores de mercado, y fue publicado originalmente por la comunidad de Kaggle como recurso de práctica para análisis de datos deportivos.

### Dimensiones

| Métrica | Valor |
|---------|-------|
| **Registros** | 18,207 jugadores |
| **Variables** | 89 columnas |
| **Países** | 164 nacionalidades |
| **Formato** | CSV (8.7 MB) |

### Tipos de Variables

El dataset contiene **6 categorías principales** de variables:

#### 1. Identificadores y Datos Básicos

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `ID` | int | Identificador único del jugador |
| `Name` | string | Nombre del jugador |
| `Age` | int | Edad del jugador |
| `Nationality` | string | Nacionalidad |
| `Club` | string | Club actual |

#### 2. Valoración y Potencial

| Columna | Tipo | Descripción | Rango |
|---------|------|-------------|-------|
| `Overall` | int | Rating general del jugador | 46-94 |
| `Potential` | int | Rating máximo potencial | 48-95 |
| `Special` | int | Puntuación especial | 731-2346 |

#### 3. Variables Financieras

| Columna | Tipo Original | Tipo Procesado | Descripción |
|---------|---------------|----------------|-------------|
| `Value` | string (€110.5M) | float | Valor de mercado en euros |
| `Wage` | string (€565K) | float | Salario semanal en euros |
| `Release Clause` | string (€226.5M) | float | Cláusula de rescisión |

#### 4. Atributos Físicos

| Columna | Formato Original | Descripción |
|---------|------------------|-------------|
| `Height` | 5'7 (pies) | Estatura |
| `Weight` | 159lbs | Peso en libras |

#### 5. Habilidades de Juego (29 columnas)

| Columna | Rango | Descripción |
|---------|-------|-------------|
| `Crossing` | 1-99 | Centros |
| `Finishing` | 1-99 | Definición |
| `HeadingAccuracy` | 1-99 | Precisión de cabeza |
| `ShortPassing` | 1-99 | Pases cortos |
| `Dribbling` | 1-99 | Regate |
| `...` | ... | (24 habilidades más) |

#### 6. Habilidades de Portero (5 columnas)

| Columna | Rango | Descripción |
|---------|-------|-------------|
| `GKDiving` | 1-99 | Inmersión |
| `GKHandling` | 1-99 | Manejo de balón |
| `GKKicking` | 1-99 | Saques |
| `GKPositioning` | 1-99 | Posicionamiento |
| `GKReflexes` | 1-99 | Reflejos |

---

## 🔧 Preprocesamiento de Datos

### Pipeline de Limpieza

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Carga CSV     │ ──► │   Limpieza      │ ──► │   Manejo de     │
│   (18,207 rows) │     │   Columnas      │     │   Valores Nulos │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Transformaciones Aplicadas

#### 1. Limpieza de la Columna `Value`

La columna `Value` contenía valores en formato de texto con símbolos y sufijos:

```python
# Ejemplos de valores originales:
"€110.5M"  → 110500000.0  # M = Millones (× 1,000,000)
"€565K"    → 565000.0     # K = Miles (× 1,000)
"€0"       → 0.0          # Sin valor

# Función de transformación:
def parse_value(value):
    value = str(value).replace('€', '').strip()
    if 'M' in value:
        return float(value.replace('M', '')) * 1_000_000
    elif 'K' in value:
        return float(value.replace('K', '')) * 1_000
    return float(value)
```

#### 2. Manejo de Valores Nulos

| Columna | Nulos Originales | Estrategia | Justificación |
|---------|------------------|------------|---------------|
| `Age` | 0 | Mediana | Robusto ante outliers |
| `Overall` | 0 | Mediana | Preserva distribución |
| `Value` | 0 | Mediana | Evita sesgo de extremos |
| `Nationality` | 0 | "Unknown" | Mantiene registro |
| `Loaned From` | 16,943 (93%) | **No procesado** | Esperado - jugadores no cedidos |
| `Release Clause` | 1,564 (8.6%) | **No procesado** | No crítico para análisis |

### Calidad de Datos Post-Procesamiento

| Métrica | Valor |
|---------|-------|
| Registros válidos | 18,207 (100%) |
| Duplicados eliminados | 0 |
| Valores nulos críticos | 0 |
| Variables transformadas | 1 (`Value`) |

---

### ⚠️ Actividad 3 — Problemas Comunes al Manipular los Datos

Durante el preprocesamiento del dataset FIFA se identificaron dos problemas principales que requirieron tratamiento especial:

#### 1. Formato no numérico de la columna `Value`

La columna `Value` (valor de mercado del jugador) no contenía números directamente utilizables, sino cadenas de texto con el símbolo monetario `€` y sufijos multiplificadores:

- `€110.5M` → debe interpretarse como **110,500,000** euros (sufijo `M` = millones × 1,000,000)
- `€565K` → debe interpretarse como **565,000** euros (sufijo `K` = miles × 1,000)
- `€0` → jugadores sin valor de mercado asignado

Este problema es muy frecuente en datasets financieros reales. Para solucionarlo se implementó la función `clean_value_column()`, que elimina el símbolo `€`, detecta el sufijo y multiplica por el factor correspondiente, convirtiendo cada valor a un número flotante puro apto para cálculos y visualizaciones.

#### 2. Alta proporción de valores nulos en columnas auxiliares

Algunas columnas presentaron tasas de nulidad muy elevadas que debieron ser tratadas con cuidado:

| Columna | Nulos | % del total | Causa probable |
|---------|-------|-------------|----------------|
| `Loaned From` | ~16,943 | ~93% | Solo aplica a jugadores cedidos. La gran mayoría no están en calidad de préstamo, por lo que el nulo es esperado y **no es un error**. |
| `Release Clause` | ~1,564 | ~8.6% | No todos los jugadores tienen cláusula de rescisión en su contrato. |

Estos nulos no fueron imputados porque hacerlo introduciría información ficticia. En cambio, se documentaron y se excluyeron del análisis cuando correspondió.

---

## 📊 Visualizaciones Generadas

### 🎯 Actividad 2 — Justificación de Gráficos

La elección de cada tipo de visualización responde a la clasificación teórica estándar del material de estudio, que organiza los gráficos según su **propósito comunicativo**:

| Tipo de Gráfico | Categoría Teórica | Variable Representada | Justificación |
|-----------------|-------------------|-----------------------|---------------|
| **Histograma de Edad** | 📊 **Distribución** | `Age` | El histograma es el gráfico canónico para mostrar cómo se distribuye una variable numérica continua. Permite observar el rango, la concentración y la asimetría de la edad de los jugadores. |
| **Box Plot de Valor por Grupo Etario** | 📊 **Distribución** | `Value` × `Age Group` | El diagrama de caja y bigotes muestra la dispersión, la mediana y los outliers de una variable numérica para distintos grupos. Es ideal para comparar la distribución del valor de mercado entre rangos de edad. |
| **Barras — Top 10 Países** | 📈 **Comparación** | `Nationality` | El gráfico de barras es el tipo más efectivo para comparar magnitudes entre categorías discretas. Permite ver claramente qué países tienen mayor representación de jugadores. |
| **Scatter Plot — Overall vs Value** | 🔗 **Relación** | `Overall` vs `Value` | El diagrama de dispersión es la herramienta estándar para visualizar la relación (o correlación) entre dos variables numéricas. Permite detectar tendencias, outliers y oportunidades de mercado. |

---

### 1. Histograma de Edad

**Objetivo:** Analizar la distribución etaria de los jugadores profesionales.

```
    Cantidad
    de Jugadores
         │
    800 ─┤        ▄▄▄▄
         │       ▄██████
    600 ─┤      ████████▄
         │     ███████████
    400 ─┤    ████████████
         │   ██████████████
    200 ─┤  ████████████████
         │ ██████████████████
      0 ─┴──────────────────────
          16  20  25  30  35  40
                    Edad
```

**Hallazgos:**

| Estadística | Valor | Interpretación |
|-------------|-------|----------------|
| Media | 25.1 años | Edad promedio del jugador |
| Mediana | 25 años | 50% de jugadores por debajo |
| Desv. Estándar | 4.67 | Dispersión moderada |
| Mínimo | 16 años | Jugadores juveniles |
| Máximo | 45 años | Jugadores veteranos |

**Insights:**

- La distribución presenta **asimetría positiva** (cola hacia la derecha)
- El **55% de jugadores** se concentra entre 20-30 años
- Jugadores mayores de 38 años son **excepcionales** (solo 47 casos)
- La edad media indica un **mercado joven y dinámico**

---

### 2. Top 10 Países con Más Jugadores

**Objetivo:** Identificar los mercados con mayor representación de talento futbolístico.

**Ranking:**

| Pos | País | Jugadores | Porcentaje |
|-----|------|-----------|------------|
| 1° | England | 1,662 | 9.13% |
| 2° | Germany | 1,198 | 6.58% |
| 3° | Spain | 1,072 | 5.89% |
| 4° | Argentina | 937 | 5.15% |
| 5° | France | 914 | 5.02% |
| 6° | Brazil | 827 | 4.54% |
| 7° | Italy | 702 | 3.86% |
| 8° | Colombia | 618 | 3.39% |
| 9° | Japan | 478 | 2.63% |
| 10° | Netherlands | 453 | 2.49% |

**Concentración del Mercado:**

```
Top 10 países:  48.7% del total
Top 20 países: 68.6% del total
Resto (144):   31.4% del total
```

**Insights:**

- **Inglaterra domina** con diferencia, reflejando la importancia de la Premier League
- Alta representación de **países europeos y sudamericanos**
- Japón (9°) es el único país asiático en el Top 10
- 24 países tienen solo **1 jugador** en el dataset

---

### 3. Scatter Plot: Overall vs Value

**Objetivo:** Analizar la relación entre la calidad del jugador y su valor de mercado.

**Esta es la visualización más valiosa para decisiones de scouting.**

```
    Valor (M €)
         │
   120 ─┤                                    ● Neymar
         │                                  ●
    80 ─┤                            ●  ●
         │                        ●
    40 ─┤                    ● ●
         │                ● ●
         │            ● ●●
     0 ─┴──────────────────────────────────
          46    60    70    80    94
                    Overall
         │
         └──●──●──●──●──●──●──●── (tendencia exponencial)
```

**Métricas de Correlación:**

| Métrica | Valor | Interpretación |
|---------|-------|-----------------|
| Correlación Pearson | 0.627 | Moderada positiva |
| Valor máximo | €118.5M | Neymar Jr |
| Overall máximo | 94 | L. Messi |
| Valor mediano | €2.4M | 50% de jugadores |

**Zonas Estratégicas del Gráfico:**

```
                    │ ALTO OVERALL
                    │
    ┌───────────────┼───────────────┐
    │  💎 ELITE     │  🎯 OPORTUN.  │
    │  Alto valor   │  Bajo valor   │
    │  Alto overall │  Alto overall │
    ├───────────────┼───────────────┤
    │  ❌ SOBREVAL. │  🌱 DESARRO.  │
    │  Alto valor   │  Bajo valor   │
    │  Bajo overall │  Bajo overall │
    └───────────────┼───────────────┘
                    │
                    │ BAJO OVERALL
         BAJO VALOR         ALTO VALOR
```

**Insights:**

- La relación es **exponencial, no lineal**
- Jugadores con **Overall >85** representan menos del 2% pero concentran el mayor valor
- La correlación moderada indica que **otros factores influyen** (edad, contrato, reputación)
- Existen **oportunidades de mercado** en la esquina superior izquierda

---

### 4. Dashboard Resumen (4 Gráficos Integrados) — Actividad 5

#### 🖥️ Elementos, Características y Beneficios del Dashboard

Un **cuadro de mando (dashboard)** es una herramienta de visualización que consolida múltiples métricas e indicadores clave en una única interfaz, facilitando la toma de decisiones basada en datos para distintos tipos de stakeholders (directivos, analistas, scouts).

**Elementos del dashboard elaborado:**

| Elemento | Descripción |
|----------|-------------|
| **Histograma de Age** | Muestra la distribución etaria del plantel analizado |
| **Histograma de Overall** | Expone la distribución del rating de calidad de los jugadores |
| **Gráfico de Barras – Top 5 Países** | Compara los mercados con mayor volumen de jugadores |
| **Box Plot – Valor por Grupo Etario** | Analiza la dispersión del valor de mercado según la edad |

**Características destacadas:**

- **Interactividad nativa:** Todos los gráficos permiten zoom, paneo y tooltip al pasar el cursor, habilitando exploración sin necesidad de reprocesar datos.
- **Layout de cuadrícula 2×2:** El diseño en grilla permite comparar visualmente las cuatro métricas de forma simultánea, sin necesidad de desplazarse entre pestañas.
- **Paleta de colores coherente:** Se utilizaron colores distintivos por tipo de gráfico (`#2E86AB`, `#E94560`, `#023E8A`, `#48CAE4`) para facilitar la identificación rápida de cada visualización.
- **Exportación standalone:** El dashboard completo se genera como un único archivo `.html` autocontenido, sin necesidad de servidor ni conexión a internet para visualizarlo.

**Beneficios para la toma de decisiones:**

- Los **scouts** pueden identificar en segundos el perfil etario y de calidad del mercado.
- Los **analistas financieros** obtienen una visión clara de cómo evoluciona el valor de mercado con la edad.
- Los **directivos** acceden a un resumen ejecutivo listo para presentar sin configuración adicional.

**Componentes:**

| Gráfico | Tipo | Variable | Insight |
|---------|------|----------|---------|
| 1 | Histograma | Age | Distribución etaria |
| 2 | Histograma | Overall | Distribución de calidad |
| 3 | Barras | Nationality | Top 5 países |
| 4 | Box Plot | Value × Age Group | Valor por grupo etario |

**Hallazgos del Box Plot:**

```
    Valor (M €)
         │
   100 ─┤              ┌───┐
         │              │   │    ┌───────┐
    50 ─┤    ┌────┐    │   │    │       │
         │    │    │    │   │    │       │
     0 ─┴────┴────┴────┴───┴────┴───────┴───
           <20  20-25   26-30    31-35    >35
                         Age Group
```

**Interpretación:**

- El grupo **26-30 años** tiene los valores medianos más altos
- Los jugadores **>35 años** muestran mayor dispersión (veteranos de élite)
- El grupo **<20 años** tiene valores más bajos pero con outliers (promesas)

---

## 💻 Tecnologías Utilizadas

### Stack Tecnológico

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.8+ | Lenguaje principal |
| **Pandas** | 2.0+ | Manipulación de datos |
| **NumPy** | 1.24+ | Cálculos numéricos |
| **Plotly** | 5.0+ | Visualizaciones interactivas |

### Justificación de Tecnologías

#### 🐼 Pandas

**¿Por qué Pandas?**

| Característica | Beneficio |
|----------------|-----------|
| **Manipulación de datos** | API intuitiva para cargar, filtrar y transformar datasets |
| **Tipos de datos** | Manejo automático de tipos numéricos y categóricos |
| **Valores nulos** | Funciones integradas para detectar y manejar datos faltantes |
| **Integración** | Compatible con NumPy, Plotly y otros formatos |

**Uso en el proyecto:**

```python
import pandas as pd

# Carga de datos
df = pd.read_csv('fifa.csv')

# Filtrado y agregaciones
top_countries = df['Nationality'].value_counts().head(10)

# Transformación de columnas
df['Value'] = df['Value'].apply(parse_value)
```

#### 🔢 NumPy

**¿Por qué NumPy?**

| Característica | Beneficio |
|----------------|-----------|
| **Rendimiento** | Operaciones vectorizadas 10-100x más rápidas que Python puro |
| **Arrays** | Estructuras optimizadas para datos numéricos |
| **Funciones matemáticas** | Estadísticas, álgebra lineal, transformaciones |
| **Integración** | Base de Pandas y Plotly |

**Uso en el proyecto:**

```python
import numpy as np

# Cálculo de correlación
correlation = df['Overall'].corr(df['Value'])

# Línea de tendencia polinómica
z = np.polyfit(df['Overall'], df['Value_Millions'], 2)
p = np.poly1d(z)
y_line = p(x_line)
```

#### 📊 Plotly Express

**¿Por qué Plotly Express?**

| Característica | Beneficio |
|----------------|-----------|
| **Interactividad** | Zoom, pan, hover con información detallada |
| **Exportación** | HTML standalone sin servidor |
| **API declarativa** | Código limpio y mantenible |
| **Tipos de gráficos** | Histogramas, barras, scatter, box plots, etc. |

**Comparativa con Alternativas:**

| Librería | Interactividad | Facilidad | Exportación |
|----------|---------------|-----------|-------------|
| **Plotly** | ✅ Nativa | ✅ Alta | ✅ HTML standalone |
| Matplotlib | ❌ Baja | ⚠️ Media | ⚠️ PNG/PDF |
| Seaborn | ❌ Baja | ✅ Alta | ⚠️ PNG/PDF |
| Bokeh | ✅ Alta | ⚠️ Media | ⚠️ Requiere servidor |

**Uso en el proyecto:**

```python
import plotly.express as px
import plotly.graph_objects as go

# Histograma interactivo
fig = px.histogram(df, x='Age', nbins=25, title='Distribución Etaria')

# Scatter plot con hover
fig = px.scatter(df, x='Overall', y='Value',
                 hover_data=['Name', 'Age', 'Nationality'])

# Exportación a HTML
fig.write_html('grafico.html')
```

#### Alternativas Consideradas

| Alternativa | Descartada por |
|-------------|----------------|
| **Matplotlib** | No interactivo, exportación estática |
| **Seaborn** | Dependiente de Matplotlib, sin interactividad |
| **Bokeh** | Curva de aprendizaje más alta, requiere servidor para features avanzados |
| **Altair** | Limitaciones en personalización, menor documentación |

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes)

### Instalación de Dependencias

```bash
# Instalar todas las dependencias
pip install pandas numpy plotly

# O con requirements.txt
pip install -r requirements.txt
```

### Crear requirements.txt

```bash
# Generar archivo de dependencias
pip freeze > requirements.txt
```

**Contenido de `requirements.txt`:**

```
pandas>=2.0.0
numpy>=1.24.0
plotly>=5.0.0
```

---

## 📖 Uso

### Ejecución Rápida

```bash
# Clonar el repositorio
git clone <url-del-repo>
cd big-data-trabajo-1

# Ejecutar el script principal
python generate_unified_dashboard.py
```

### Uso Programático

```python
from generate_unified_dashboard import load_and_preprocess, create_age_histogram

# Cargar y preprocesar datos
df = load_and_preprocess('fifa.csv')

# Crear visualización
fig = create_age_histogram(df)
fig.show()

# Guardar como HTML
fig.write_html('mi_grafico.html')
```

### Personalización de Gráficos

```python
import plotly.express as px

# Modificar colores
fig = px.histogram(df, x='Age',
                   color_discrete_sequence=['#FF6B6B'])

# Cambiar título
fig.update_layout(title='Mi Título Personalizado')

# Ajustar tamaño
fig.update_layout(height=600, width=800)
```

---

## 📚 Documentación Adicional

### Estructura del Código

```
generate_unified_dashboard.py
│
├── Preprocesamiento
│   ├── clean_value_column()      # Limpia columna Value (€, M, K)
│   ├── handle_missing_values()    # Maneja valores nulos
│   └── load_and_preprocess()      # Pipeline completo
│
├── Visualizaciones
│   ├── create_age_histogram()     # Histograma de edad
│   ├── create_top_countries_bar() # Top países
│   ├── create_overall_value_scatter() # Scatter plot
│   └── create_summary_dashboard()  # Dashboard resumen
│
└── Generación HTML
    └── generate_complete_html()   # HTML con estilos y gráficos
```

### Funciones Principales

#### `clean_value_column(df)`

Transforma valores de texto a numéricos.

```python
# Entrada: "€110.5M"
# Salida:  110500000.0

df = clean_value_column(df)
```

#### `handle_missing_values(df)`

Imputa valores nulos con estrategias específicas.

```python
# Age, Overall, Value → Mediana
# Nationality → "Unknown"

df = handle_missing_values(df)
```

#### `load_and_preprocess(filepath)`

Pipeline completo de carga y limpieza.

```python
df = load_and_preprocess('fifa.csv')
# Retorna DataFrame listo para análisis
```

---

## 📈 Interpretación de Resultados

### Correlaciones Identificadas

| Variables | Correlación | Interpretación |
|-----------|-------------|----------------|
| Overall × Value | 0.627 | Moderada positiva |
| Age × Overall | 0.45 | Débil positiva |
| Age × Potential | -0.25 | Débil negativa |
| Overall × Reactions | 0.85 | Fuerte positiva |

### Patrones Detectados

#### 1. Valor de Mercado Exponencial

El valor no crece linealmente con el Overall. Un jugador de 90 cuesta **más del doble** que uno de 85.

```
Overall 80 → ~€10M
Overall 85 → ~€30M  (3x más)
Overall 90 → ~€80M  (8x más)
```

#### 2. Edad Óptima de Valor

El valor máximo se alcanza entre **26-30 años**, con declive acelerado después de 32.

#### 3. Concentración Geográfica

Los **Top 10 países** concentran casi la mitad del talento (48.7%).

---

## 🎯 Casos de Uso

### Para Scouting

```python
# Identificar jugadores infravalorados
bargains = df[(df['Overall'] >= 75) & (df['Value'] < 10_000_000)]
# Jugadores con alto rating pero bajo valor
```

### Para Análisis de Mercado

```python
# Comparar mercados por país
market_comparison = df.groupby('Nationality')['Value'].agg(['mean', 'median', 'count'])
# Valor promedio y volumen por país
```

### Para Predicción de Valor

```python
# Variables más relevantes para el valor
correlations = df.corr()['Value'].sort_values(ascending=False)
# Overall, International Reputation, Potential son los principales
```

---

## ✅ Actividad 7 — Efectividad de las Visualizaciones

Las cuatro visualizaciones generadas en este proyecto son **efectivas** para representar el dataset FIFA por las siguientes razones:

### 1. Interactividad con Plotly

A diferencia de librerías estáticas como Matplotlib o Seaborn, Plotly genera gráficos **completamente interactivos** en el navegador. El usuario puede:
- Hacer **zoom** en zonas de interés (por ejemplo, jugadores con Overall > 85)
- Ver **tooltips detallados** al pasar el cursor sobre cada punto (nombre, club, valor, edad)
- **Filtrar series** haciendo clic en la leyenda
- **Descargar** el gráfico como imagen PNG con un solo clic

Esta interactividad convierte las visualizaciones en herramientas de exploración activa, no meros reportes pasivos.

### 2. Claridad visual y paleta de colores

Se evitaron colores arbitrarios o sobrecargados. En cambio:
- Los **histogramas** usan un azul uniforme (`#2E86AB`) que no distrae del patrón de distribución.
- El **scatter plot** usa la escala `Plasma` (de azul oscuro a amarillo) para codificar el Overall, haciendo intuitivo que los puntos más brillantes son los mejores jugadores.
- El **gráfico de barras** usa la escala `Viridis`, legible incluso en condiciones de daltonismo.
- Se incluyen **líneas de media** y **curvas de tendencia** que guían la interpretación sin saturar el gráfico.

### 3. Detección ágil de patrones

Cada gráfico fue diseñado para responder una pregunta analítica concreta:

| Pregunta | Visualización | Patrón detectable |
|----------|--------------|-------------------|
| ¿Cómo se distribuyen las edades? | Histograma | Asimetría positiva; concentración en 20-28 años |
| ¿Qué países dominan? | Barras | Inglaterra lidera con amplia ventaja |
| ¿Hay relación calidad-valor? | Scatter Plot | Tendencia exponencial con r = 0.627 |
| ¿Cómo varía el valor con la edad? | Box Plot | Pico en 26-30 años; outliers en >35 |

### 4. Formato HTML standalone

Los gráficos se exportan a HTML autocontenido, lo que permite **compartirlos sin instalar ningún software**, abrirlos directamente en cualquier navegador moderno y mantener toda su interactividad. Esto los hace especialmente adecuados para presentaciones a stakeholders no técnicos.

### Conclusión

La combinación de **interactividad nativa de Plotly**, **paletas de color semánticamente significativas**, **curvas de tendencia explícitas** y **exportación sin dependencias externas** hace que estas visualizaciones cumplan con los principios de efectividad en la comunicación de datos: son claras, honestas, interactivas y accionables.

---

## 📝 Conclusiones

### Resumen de Hallazgos

| Hallazgo | Implicación |
|----------|-------------|
| Correlación Overall-Valor 0.627 | La calidad es un predictor importante pero no único |
| Concentración en Top 10 países | Mercados principales para scouting |
| Edad promedio 25.1 años | Mercado joven y dinámico |
| Valor mediano €2.4M | Mayoría de jugadores accesibles |

### Recomendaciones

#### Para Scouting y Transferencias

1. **Buscar oportunidades en:** Jugadores con Overall >75 y Value <€10M
2. **Priorizar edad:** Rango 22-28 años para balance calidad/potencial
3. **Mercados alternativos:** Brasil y Argentina ofrecen mejor relación calidad-precio

#### Para Análisis Futuros

1. Incorporar análisis de **Position y habilidades específicas**
2. Explorar relación entre **Potential y edad**
3. Analizar **Club y League** para comparar competitividad

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📧 Contacto

Para preguntas o sugerencias sobre este análisis, por favor abre un issue en el repositorio.

---

<div align="center">

**Hecho con ❤️ para Big Data - Trabajo Práctico 1 -
Alumnos:
Ayala, Santiago
Colman, Maximo
Martínez, Javier
Pereyra, Ramiro
Zigaran, Lucas**

📊 **Dashboard:** `fifa_dashboard_completo.html` | 🐍 **Script:** `generate_unified_dashboard.py`

</div>