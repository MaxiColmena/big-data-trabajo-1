"""
Visualizaciones Interactivas del Dataset FIFA
================================================
Este script genera visualizaciones interactivas usando Plotly Express
para analizar el dataset de jugadores de FIFA.

Requisitos:
- pandas
- numpy
- plotly

Instalación: pip install pandas numpy plotly
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# =============================================================================
# FUNCIONES DE PREPROCESAMIENTO
# =============================================================================

def clean_value_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia la columna 'Value' eliminando el simbolo € y convirtiendo
    los sufijos M (millones) y K (miles) a valores numericos.

    Args:
        df: DataFrame con columna 'Value' en formato string

    Returns:
        DataFrame con columna 'Value' convertida a float
    """
    df = df.copy()

    def parse_value(value):
        if pd.isna(value) or value == '' or value == '€0':
            return 0.0

        # Eliminar simbolo €
        value = str(value).replace('€', '').strip()

        # Interpretar sufijos
        if 'M' in value:
            return float(value.replace('M', '')) * 1_000_000
        elif 'K' in value:
            return float(value.replace('K', '')) * 1_000
        else:
            try:
                return float(value)
            except ValueError:
                return 0.0

    df['Value'] = df['Value'].apply(parse_value)
    return df


def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Maneja valores nulos en las columnas criticas para visualizacion.

    Args:
        df: DataFrame original

    Returns:
        DataFrame con valores nulos manejados
    """
    df = df.copy()

    # Columnas criticas a verificar
    critical_columns = ['Age', 'Overall', 'Value', 'Nationality']

    for col in critical_columns:
        if col in df.columns:
            if df[col].dtype in ['float64', 'int64']:
                # Para columnas numericas, reemplazar con la mediana
                df[col] = df[col].fillna(df[col].median())
            else:
                # Para columnas categoricas, reemplazar con 'Unknown'
                df[col] = df[col].fillna('Unknown')

    return df


def load_and_preprocess(filepath: str) -> pd.DataFrame:
    """
    Carga y preprocesa el dataset FIFA completo.

    Args:
        filepath: Ruta al archivo CSV

    Returns:
        DataFrame preprocesado y listo para visualizacion
    """
    print("Cargando dataset...")
    df = pd.read_csv(filepath)

    print(f"Dimensiones originales: {df.shape[0]} filas x {df.shape[1]} columnas")
    print(f"Columnas disponibles: {list(df.columns)[:10]}...")

    # Preprocesamiento
    print("\nLimpiando columna 'Value'...")
    df = clean_value_column(df)

    print("Manejando valores nulos...")
    df = handle_missing_values(df)

    # Estadisticas descriptivas basicas
    print("\n" + "="*60)
    print("ESTADISTICAS DESCRIPTIVAS")
    print("="*60)
    print(f"\nAge - Min: {df['Age'].min()}, Max: {df['Age'].max()}, Mean: {df['Age'].mean():.1f}")
    print(f"Overall - Min: {df['Overall'].min()}, Max: {df['Overall'].max()}, Mean: {df['Overall'].mean():.1f}")
    print(f"Value (EUR) - Min: {df['Value'].min():,.0f}, Max: {df['Value'].max():,.0f}, Mean: {df['Value'].mean():,.0f}")
    print(f"Paises unicos: {df['Nationality'].nunique()}")

    return df


# =============================================================================
# VISUALIZACIONES
# =============================================================================

def create_age_histogram(df: pd.DataFrame) -> go.Figure:
    """
    Crea un histograma interactivo de la distribucion etaria de jugadores.

    Racional del grafico:
    - Un histograma es ideal para visualizar la distribucion de una variable numerica continua
    - Permite identificar la concentracion de jugadores por rango de edad
    - Facilita detectar sesgos o anomalas en la composicion etaria

    Args:
        df: DataFrame con columna 'Age'

    Returns:
        Figura interactiva de Plotly
    """
    fig = px.histogram(
        df,
        x='Age',
        nbins=25,
        title='<b>Distribucion Etaria de Jugadores FIFA</b>',
        labels={'Age': 'Edad', 'count': 'Cantidad de Jugadores'},
        color_discrete_sequence=['#2E86AB'],
        opacity=0.85
    )

    # Personalizacion del diseño
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        template='plotly_white',
        bargap=0.05,
        hovermode='x unified'
    )

    # Agregar linea de media
    mean_age = df['Age'].mean()
    fig.add_vline(
        x=mean_age,
        line_dash='dash',
        line_color='#E94560',
        line_width=2,
        annotation_text=f'Media: {mean_age:.1f} anos',
        annotation_position='top right'
    )

    # Agregar estadisticas en el grafico
    fig.add_annotation(
        x=0.02, y=0.98,
        xref='paper', yref='paper',
        text=f"<b>Estadisticas:</b><br>"
             f"Jugadores totales: {len(df):,}<br>"
             f"Edad minima: {df['Age'].min()}<br>"
             f"Edad maxima: {df['Age'].max()}<br>"
             f"Desviacion estandar: {df['Age'].std():.1f}",
        showarrow=False,
        align='left',
        bgcolor='rgba(255,255,255,0.8)',
        font_size=12
    )

    return fig


def create_top_countries_bar(df: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """
    Crea un grafico de barras de los paises con mas jugadores.

    Racional del grafico:
    - Un grafico de barras es ideal para comparar frecuencias entre categorias
    - Mostrar solo el Top 10 evita saturacion visual y facilita comparacion
    - Permite identificar rapidamente los paises con mayor representacion

    Args:
        df: DataFrame con columna 'Nationality'
        top_n: Numero de paises a mostrar

    Returns:
        Figura interactiva de Plotly
    """
    # Contar jugadores por pais
    country_counts = df['Nationality'].value_counts().head(top_n).reset_index()
    country_counts.columns = ['Nationality', 'Count']

    # Crear grafico de barras
    fig = px.bar(
        country_counts,
        x='Nationality',
        y='Count',
        title=f'<b>Top {top_n} Paises con Mas Jugadores</b>',
        labels={'Nationality': 'Pais', 'Count': 'Cantidad de Jugadores'},
        color='Count',
        color_continuous_scale='Viridis',
        text='Count'
    )

    # Personalizacion del diseño
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        template='plotly_white',
        coloraxis_showscale=False
    )

    # Rotar etiquetas del eje X para mejor legibilidad
    fig.update_xaxes(tickangle=-45)

    # Mostrar valores encima de las barras
    fig.update_traces(
        textposition='outside',
        textfont_size=12,
        marker_line_width=1.5,
        marker_line_color='white'
    )

    # Agregar anotacion con total
    total_countries = df['Nationality'].nunique()
    fig.add_annotation(
        x=0.98, y=0.98,
        xref='paper', yref='paper',
        text=f"<b>Total de paises:</b> {total_countries}",
        showarrow=False,
        align='right',
        bgcolor='rgba(255,255,255,0.8)',
        font_size=12
    )

    return fig


def create_overall_value_scatter(df: pd.DataFrame) -> go.Figure:
    """
    Crea un scatter plot interactivo de Overall vs Value.

    Racional del grafico:
    - Un scatter plot es ideal para visualizar la relacion entre dos variables numericas
    - Permite identificar correlaciones y outliers
    - La relacion calidad-valor de mercado es fundamental en analisis futbolistico

    Args:
        df: DataFrame con columnas 'Overall' y 'Value'

    Returns:
        Figura interactiva de Plotly
    """
    # Filtrar jugadores con valor mayor a 0 para mejor visualizacion
    df_plot = df[df['Value'] > 0].copy()

    # Convertir valor a millones para mejor legibilidad
    df_plot['Value_Millions'] = df_plot['Value'] / 1_000_000

    # Crear scatter plot
    fig = px.scatter(
        df_plot,
        x='Overall',
        y='Value_Millions',
        title='<b>Relacion entre Calidad (Overall) y Valor de Mercado</b>',
        labels={
            'Overall': 'Rating Overall',
            'Value_Millions': 'Valor de Mercado (Millones EUR)'
        },
        opacity=0.6,
        color='Overall',
        color_continuous_scale='Plasma',
        hover_data=['Name', 'Age', 'Nationality', 'Club'] if 'Name' in df_plot.columns else None
    )

    # Personalizacion del diseño
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        xaxis_title_font_size=14,
        yaxis_title_font_size=14,
        template='plotly_white',
        coloraxis_showscale=False
    )

    # Agregar estadisticas de correlacion
    correlation = df_plot['Overall'].corr(df_plot['Value_Millions'])
    fig.add_annotation(
        x=0.02, y=0.98,
        xref='paper', yref='paper',
        text=f"<b>Correlacion:</b> {correlation:.3f}<br>"
             f"<b>Jugadores:</b> {len(df_plot):,}<br>"
             f"<b>Valor max:</b> EUR {df_plot['Value'].max()/1e6:.1f}M",
        showarrow=False,
        align='left',
        bgcolor='rgba(255,255,255,0.9)',
        font_size=12
    )

    # Agregar linea de tendencia
    z = np.polyfit(df_plot['Overall'], df_plot['Value_Millions'], 2)
    p = np.poly1d(z)
    x_line = np.linspace(df_plot['Overall'].min(), df_plot['Overall'].max(), 100)
    y_line = p(x_line)

    fig.add_trace(
        go.Scatter(
            x=x_line,
            y=y_line,
            mode='lines',
            name='Tendencia',
            line=dict(color='#E94560', width=2, dash='dash'),
            showlegend=True
        )
    )

    return fig


def create_summary_reporte(df: pd.DataFrame) -> go.Figure:
    """
    Crea un reporte resumen con multiples metricas clave.

    Args:
        df: DataFrame preprocesado

    Returns:
        Figura interactiva con subplots
    """
    # Crear figura con subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Distribucion de Age',
            'Distribucion de Overall',
            'Top 5 Nacionalidades',
            'Valor por Age Group'
        ),
        specs=[
            [{'type': 'histogram'}, {'type': 'histogram'}],
            [{'type': 'bar'}, {'type': 'box'}]
        ]
    )

    # 1. Histograma de Age
    fig.add_trace(
        go.Histogram(
            x=df['Age'],
            name='Age',
            marker_color='#2E86AB',
            opacity=0.75
        ),
        row=1, col=1
    )

    # 2. Histograma de Overall
    fig.add_trace(
        go.Histogram(
            x=df['Overall'],
            name='Overall',
            marker_color='#E94560',
            opacity=0.75
        ),
        row=1, col=2
    )

    # 3. Top 5 nacionalidades
    top_5_countries = df['Nationality'].value_counts().head(5)
    fig.add_trace(
        go.Bar(
            x=top_5_countries.index,
            y=top_5_countries.values,
            name='Nacionalidad',
            marker_color='#023E8A'
        ),
        row=2, col=1
    )

    # 4. Box plot de Value por Age Group (un trace por grupo para orden correcto)
    df_temp = df.copy()
    age_order = ['<20', '20-25', '26-30', '31-35', '>35']
    df_temp['Age_Group'] = pd.cut(
        df_temp['Age'],
        bins=[0, 20, 25, 30, 35, 50],
        labels=age_order
    ).astype(str)
    df_temp['Value_Millions'] = df_temp['Value'] / 1_000_000

    for group in age_order:
        mask = df_temp['Age_Group'] == group
        fig.add_trace(
            go.Box(
                y=df_temp.loc[mask, 'Value_Millions'],
                name=group,
                marker_color='#48CAE4',
                showlegend=False
            ),
            row=2, col=2
        )

    # Actualizar layout
    fig.update_layout(
        title_text='<b>Reporte Resumen - Dataset FIFA</b>',
        title_font_size=24,
        title_x=0.5,
        showlegend=False,
        template='plotly_white',
        height=700
        # sin width fijo: el gráfico se adapta al contenedor HTML
    )

    fig.update_xaxes(title_text='Edad', row=1, col=1)
    fig.update_yaxes(title_text='Frecuencia', row=1, col=1)
    fig.update_xaxes(title_text='Rating Overall', row=1, col=2)
    fig.update_yaxes(title_text='Frecuencia', row=1, col=2)
    fig.update_xaxes(title_text='Pais', row=2, col=1)
    fig.update_yaxes(title_text='Cantidad', row=2, col=1)
    fig.update_xaxes(title_text='Grupo Etario', row=2, col=2)
    fig.update_yaxes(title_text='Valor (Millones EUR)', row=2, col=2)

    return fig


# =============================================================================
# ACTIVIDAD 6: LANDING PAGE
# =============================================================================

def generate_landing_page(
    fig1_html: str,
    fig2_html: str,
    fig3_html: str,
    fig4_html: str,
    output_path: str,
    df: pd.DataFrame = None
) -> None:
    """
    Genera una Landing Page HTML5 completa con los graficos de Plotly embebidos.

    Toma los divs HTML exportados por Plotly y los inyecta dentro de una
    plantilla HTML5 con estilos CSS, un encabezado descriptivo y una seccion
    de introduccion. El archivo resultante es completamente autocontenido y
    puede abrirse en cualquier navegador sin conexion a internet.

    Args:
        fig1_html: Div HTML del histograma de edades (Plotly to_html)
        fig2_html: Div HTML del grafico de barras Top 10 paises
        fig3_html: Div HTML del scatter plot Overall vs Value
        fig4_html: Div HTML del reporte resumen (subplots)
        output_path: Ruta completa del archivo .html de salida
        df: DataFrame con los datos (opcional, para incluir estadísticas)

    Returns:
        None. Guarda el archivo HTML en output_path.

    Ejemplo de uso:
        import plotly.io as pio

        fig1_div = pio.to_html(fig_age, full_html=False, include_plotlyjs='cdn')
        fig2_div = pio.to_html(fig_countries, full_html=False, include_plotlyjs=False)
        fig3_div = pio.to_html(fig_scatter, full_html=False, include_plotlyjs=False)
        fig4_div = pio.to_html(fig_reporte, full_html=False, include_plotlyjs=False)

        generate_landing_page(fig1_div, fig2_div, fig3_div, fig4_div,
                              'fifa_landing_page.html', df)
    """
    # Valores por defecto si df no se proporciona
    num_jugadores = len(df) if df is not None else 18208
    num_paises = df['Nationality'].nunique() if df is not None else 164
    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Reporte interactivo con analisis exploratorio del dataset FIFA 19. Visualizaciones de distribucion etaria, top paises, relacion calidad-valor y resumen estadistico.">
    <title>FIFA Analytics Reporte</title>
    <style>
        /* ==============================
           RESET Y VARIABLES GLOBALES
        ============================== */
        *, *::before, *::after {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        :root {{
            --color-bg:        #0d1117;
            --color-surface:   #161b22;
            --color-border:    #30363d;
            --color-accent:    #2E86AB;
            --color-accent2:   #E94560;
            --color-text:      #e6edf3;
            --color-muted:     #8b949e;
            --radius:          12px;
            --transition:      0.25s ease;
            --max-width:       1280px;
        }}

        /* ==============================
           BASE
        ============================== */
        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background-color: var(--color-bg);
            color: var(--color-text);
            line-height: 1.6;
            min-height: 100vh;
        }}

        /* ==============================
           HEADER / HERO
        ============================== */
        header {{
            background: linear-gradient(135deg, #0d1117 0%, #1a2a3a 50%, #0d1117 100%);
            border-bottom: 1px solid var(--color-border);
            padding: 60px 24px 48px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        header::before {{
            content: '';
            position: absolute;
            top: -60px; left: 50%;
            transform: translateX(-50%);
            width: 600px; height: 600px;
            background: radial-gradient(circle, rgba(46,134,171,0.15) 0%, transparent 70%);
            pointer-events: none;
        }}

        .header-badge {{
            display: inline-block;
            background: rgba(46,134,171,0.15);
            border: 1px solid rgba(46,134,171,0.4);
            color: var(--color-accent);
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            padding: 6px 16px;
            border-radius: 999px;
            margin-bottom: 20px;
        }}

        header h1 {{
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 800;
            background: linear-gradient(90deg, #e6edf3 0%, var(--color-accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 16px;
            line-height: 1.15;
        }}

        header p.subtitle {{
            font-size: 1.05rem;
            color: var(--color-muted);
            max-width: 640px;
            margin: 0 auto 28px;
        }}

        .header-stats {{
            display: flex;
            justify-content: center;
            gap: 32px;
            flex-wrap: wrap;
            margin-top: 8px;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-item .stat-value {{
            display: block;
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--color-accent);
        }}

        .stat-item .stat-label {{
            font-size: 0.8rem;
            color: var(--color-muted);
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}

        /* ==============================
           NAVEGACION INTERNA
        ============================== */
        nav {{
            background: var(--color-surface);
            border-bottom: 1px solid var(--color-border);
            padding: 0 24px;
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        nav ul {{
            display: flex;
            list-style: none;
            gap: 0;
            max-width: var(--max-width);
            margin: 0 auto;
            overflow-x: auto;
        }}

        nav ul li a {{
            display: block;
            padding: 14px 20px;
            color: var(--color-muted);
            text-decoration: none;
            font-size: 0.88rem;
            font-weight: 500;
            transition: color var(--transition), border-bottom var(--transition);
            border-bottom: 2px solid transparent;
            white-space: nowrap;
        }}

        nav ul li a:hover {{
            color: var(--color-text);
            border-bottom-color: var(--color-accent);
        }}

        /* ==============================
           CONTENIDO PRINCIPAL
        ============================== */
        main {{
            max-width: var(--max-width);
            margin: 0 auto;
            padding: 48px 24px 80px;
        }}

        /* ==============================
           SECCION DE INTRODUCCION
        ============================== */
        .intro-section {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: var(--radius);
            padding: 40px 44px;
            margin-bottom: 56px;
            position: relative;
            overflow: hidden;
        }}

        .intro-section::before {{
            content: '';
            position: absolute;
            top: 0; left: 0;
            width: 4px; height: 100%;
            background: linear-gradient(180deg, var(--color-accent), var(--color-accent2));
            border-radius: var(--radius) 0 0 var(--radius);
        }}

        .intro-section h2 {{
            font-size: 1.4rem;
            font-weight: 700;
            color: var(--color-text);
            margin-bottom: 14px;
        }}

        .intro-section p {{
            color: var(--color-muted);
            font-size: 0.97rem;
            margin-bottom: 20px;
            max-width: 800px;
        }}

        .intro-section p:last-child {{
            margin-bottom: 0;
        }}

        .tag-list {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 20px;
        }}

        .tag {{
            background: rgba(46,134,171,0.12);
            border: 1px solid rgba(46,134,171,0.3);
            color: var(--color-accent);
            font-size: 0.8rem;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 999px;
        }}

        /* ==============================
           SECCIONES DE GRAFICOS
        ============================== */
        .chart-section {{
            margin-bottom: 64px;
        }}

        .chart-header {{
            display: flex;
            align-items: flex-start;
            gap: 16px;
            margin-bottom: 20px;
        }}

        .chart-icon {{
            font-size: 2rem;
            flex-shrink: 0;
            margin-top: 2px;
        }}

        .chart-header-text h2 {{
            font-size: 1.3rem;
            font-weight: 700;
            color: var(--color-text);
            margin-bottom: 4px;
        }}

        .chart-header-text p {{
            font-size: 0.9rem;
            color: var(--color-muted);
        }}

        .chart-badge {{
            display: inline-block;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            padding: 3px 10px;
            border-radius: 999px;
            margin-bottom: 6px;
        }}

        .badge-dist {{
            background: rgba(46,134,171,0.15);
            color: #2E86AB;
            border: 1px solid rgba(46,134,171,0.35);
        }}

        .badge-comp {{
            background: rgba(72,202,228,0.12);
            color: #48CAE4;
            border: 1px solid rgba(72,202,228,0.3);
        }}

        .badge-rel {{
            background: rgba(233,69,96,0.12);
            color: #E94560;
            border: 1px solid rgba(233,69,96,0.3);
        }}

        .chart-wrapper {{
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            border-radius: var(--radius);
            padding: 12px;
            overflow: hidden;
            transition: border-color var(--transition);
        }}

        .chart-wrapper:hover {{
            border-color: var(--color-accent);
        }}

        /* ==============================
           DIVIDER
        ============================== */
        .section-divider {{
            border: none;
            border-top: 1px solid var(--color-border);
            margin: 0 0 56px;
        }}

        /* ==============================
           FOOTER
        ============================== */
        footer {{
            background: var(--color-surface);
            border-top: 1px solid var(--color-border);
            text-align: center;
            padding: 32px 24px;
            color: var(--color-muted);
            font-size: 0.85rem;
        }}

        footer strong {{
            color: var(--color-accent);
        }}

        /* ==============================
           RESPONSIVE
        ============================== */
        @media (max-width: 640px) {{
            .intro-section {{
                padding: 28px 24px;
            }}
            .header-stats {{
                gap: 20px;
            }}
            nav ul li a {{
                padding: 12px 14px;
            }}
        }}
    </style>
</head>
<body>

    <!-- ============================================================
         CABECERA / HERO
    ============================================================ -->
    <header>
        <div class="header-badge">Big Data &mdash; Trabajo Pr&aacute;ctico 1</div>
        <h1>FIFA Analytics Reporte</h1>
        <p class="subtitle">
            An&aacute;lisis exploratorio interactivo del dataset FIFA 19: distribuciones,
            comparaciones geogr&aacute;ficas y relaci&oacute;n calidad&ndash;valor de mercado.
        </p>
        <div class="header-stats">
            <div class="stat-item">
                <span class="stat-value">{num_jugadores:,}</span>
                <span class="stat-label">Jugadores</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">{num_paises}</span>
                <span class="stat-label">Países</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">89</span>
                <span class="stat-label">Variables</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">4</span>
                <span class="stat-label">Visualizaciones</span>
            </div>
        </div>
    </header>

    <!-- ============================================================
         NAVEGACION INTERNA
    ============================================================ -->
    <nav>
        <ul>
            <li><a href="#introduccion">Introducci&oacute;n</a></li>
            <li><a href="#distribucion-edad">Distribuci&oacute;n de Edad</a></li>
            <li><a href="#top-paises">Top Pa&iacute;ses</a></li>
            <li><a href="#overall-valor">Overall vs Valor</a></li>
            <li><a href="#reporte">Reporte Resumen</a></li>
        </ul>
    </nav>

    <!-- ============================================================
         CONTENIDO PRINCIPAL
    ============================================================ -->
    <main>

        <!-- SECCION DE INTRODUCCION -->
        <section class="intro-section" id="introduccion">
            <h2>&#128200; Sobre este Reporte</h2>
            <p>
                Este reporte interactivo presenta un an&aacute;lisis exploratorio de datos (EDA) completo
                sobre el dataset <strong>FIFA Player Statistics</strong>, extra&iacute;do de
                <a href="https://www.kaggle.com" style="color: var(--color-accent);" target="_blank" rel="noopener">Kaggle</a>.
                El dataset contiene informaci&oacute;n detallada de <strong>{num_jugadores:,} jugadores profesionales</strong>
                de {num_paises} pa&iacute;ses, incluyendo atributos de juego, datos demogr&aacute;ficos y valores de mercado.
            </p>
            <p>
                Las cuatro visualizaciones fueron construidas con <strong>Plotly</strong> y clasificadas
                seg&uacute;n su prop&oacute;sito te&oacute;rico: <em>Distribuci&oacute;n</em> (histograma y box plot),
                <em>Comparaci&oacute;n</em> (barras) y <em>Relaci&oacute;n</em> (scatter plot).
                Todos los gr&aacute;ficos son completamente interactivos: haz zoom, pasa el cursor sobre
                los puntos o haz clic en la leyenda para explorar los datos.
            </p>
            <div class="tag-list">
                <span class="tag">Python 3.8+</span>
                <span class="tag">Plotly 5.0+</span>
                <span class="tag">Pandas 2.0+</span>
                <span class="tag">NumPy 1.24+</span>
                <span class="tag">EDA</span>
                <span class="tag">Big Data</span>
                <span class="tag">FIFA 19</span>
            </div>
        </section>

        <!-- GRAFICO 1: HISTOGRAMA DE EDAD -->
        <section class="chart-section" id="distribucion-edad">
            <div class="chart-header">
                <div class="chart-icon">&#128202;</div>
                <div class="chart-header-text">
                    <span class="chart-badge badge-dist">Distribuci&oacute;n</span>
                    <h2>Distribuci&oacute;n Etaria de Jugadores</h2>
                    <p>
                        El histograma muestra c&oacute;mo se distribuyen las edades de los {num_jugadores:,} jugadores.
                        La l&iacute;nea punteada indica la media del dataset (~25 a&ntilde;os).
                    </p>
                </div>
            </div>
            <div class="chart-wrapper">
                {fig1_html}
            </div>
        </section>

        <hr class="section-divider">

        <!-- GRAFICO 2: TOP 10 PAISES -->
        <section class="chart-section" id="top-paises">
            <div class="chart-header">
                <div class="chart-icon">&#127758;</div>
                <div class="chart-header-text">
                    <span class="chart-badge badge-comp">Comparaci&oacute;n</span>
                    <h2>Top 10 Pa&iacute;ses con M&aacute;s Jugadores</h2>
                    <p>
                        El gr&aacute;fico de barras compara los pa&iacute;ses con mayor volumen de jugadores
                        en el dataset. Inglaterra lidera ampliamente, seguida por Alemania y Espa&ntilde;a.
                    </p>
                </div>
            </div>
            <div class="chart-wrapper">
                {fig2_html}
            </div>
        </section>

        <hr class="section-divider">

        <!-- GRAFICO 3: SCATTER OVERALL VS VALUE -->
        <section class="chart-section" id="overall-valor">
            <div class="chart-header">
                <div class="chart-icon">&#128279;</div>
                <div class="chart-header-text">
                    <span class="chart-badge badge-rel">Relaci&oacute;n</span>
                    <h2>Overall vs Valor de Mercado</h2>
                    <p>
                        El scatter plot revela la relaci&oacute;n entre el rating global de cada jugador
                        y su valor de mercado en euros. La curva de tendencia refleja una relaci&oacute;n
                        exponencial (correlaci&oacute;n de Pearson r &asymp; 0.627).
                    </p>
                </div>
            </div>
            <div class="chart-wrapper">
                {fig3_html}
            </div>
        </section>

        <hr class="section-divider">

        <!-- GRAFICO 4: REPORTE RESUMEN -->
        <section class="chart-section" id="reporte">
            <div class="chart-header">
                <div class="chart-icon">&#128203;</div>
                <div class="chart-header-text">
                    <span class="chart-badge badge-dist">Reporte</span>
                    <h2>Reporte Resumen &mdash; 4 M&eacute;tricas Clave</h2>
                    <p>
                        Vista consolidada con histograma de edad, histograma de overall, top 5 pa&iacute;ses
                        y box plot de valor de mercado por grupo etario. Ideal para una presentaci&oacute;n
                        ejecutiva r&aacute;pida.
                    </p>
                </div>
            </div>
            <div class="chart-wrapper">
                {fig4_html}
            </div>
        </section>

    </main>

    <!-- ============================================================
         FOOTER
    ============================================================ -->
    <footer>
        <p>
            <strong>FIFA Analytics Reporte</strong> &mdash;
            Big Data &bull; Trabajo Pr&aacute;ctico 1 &bull;
            Generado con Python + Plotly &bull; Dataset: FIFA 19 (Kaggle)
        </p>
    </footer>

</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"Landing page generada exitosamente: {output_path}")


# =============================================================================
# FUNCION PRINCIPAL
# =============================================================================

def main():
    """
    Funcion principal que ejecuta todo el pipeline de visualizacion.
    """
    # Ruta del dataset (relativa al directorio del script)
    filepath = 'fifa.csv'

    # Cargar y preprocesar datos
    df = load_and_preprocess(filepath)

    print("\n" + "="*60)
    print("GENERANDO VISUALIZACIONES INTERACTIVAS")
    print("="*60)

    # ==========================================================================
    # VISUALIZACION 1: Histograma de Age
    # ==========================================================================
    print("\n1. Generando histograma de Age...")
    fig_age = create_age_histogram(df)
    fig_age.show()

    print("""
    INTERPRETACION - Histograma de Age:
    ------------------------------------
    Este grafico muestra la distribucion de edades de los jugadores.
    - El pico de la distribucion indica la edad mas comun entre jugadores
    - La asimetria revela si hay mas jugadores jovenes o veteranos
    - Los outliers pueden indicar jugadores atipicos (muy jovenes o veteranos)

    Utilidad analitica:
    - Ayuda a entender la composicion demografica del dataset
    - Permite identificar rangos etarios objetivo para estrategias
    - Facilita la deteccion de posibles errores en los datos
    """)

    # ==========================================================================
    # VISUALIZACION 2: Top 10 Paises
    # ==========================================================================
    print("\n2. Generando grafico de Top 10 paises...")
    fig_countries = create_top_countries_bar(df)
    fig_countries.show()

    print("""
    INTERPRETACION - Top 10 Paises con Mas Jugadores:
    -------------------------------------------------
    Este grafico de barras muestra los paises con mayor representacion.
    - La altura de cada barra representa la cantidad de jugadores
    - Facilita la comparacion rapida entre paises principales

    Utilidad analitica:
    - Identificar mercados con mayor talento disponible
    - Entender la representatividad geografica del dataset
    - Apoyar decisiones de scouting internacional
    """)

    # ==========================================================================
    # VISUALIZACION 3: Scatter Overall vs Value
    # ==========================================================================
    print("\n3. Generando scatter plot Overall vs Value...")
    fig_scatter = create_overall_value_scatter(df)
    fig_scatter.show()

    print("""
    INTERPRETACION - Relacion Overall vs Valor de Mercado:
    -----------------------------------------------------
    Este scatter plot revela la relacion entre calidad y valor.
    - Cada punto representa un jugador
    - La correlacion indica que tan bien predice el rating el valor
    - Los outliers son jugadores sobrevalorados o infravalorados

    Utilidad analitica:
    - Identificar jugadores infravalorados (alto rating, bajo valor)
    - Detectar jugadores premium (alto rating, alto valor)
    - Entender la valoracion del mercado futbolistico
    """)

    # ==========================================================================
    # VISUALIZACION 4: Reporte Resumen
    # ==========================================================================
    print("\n4. Generando reporte resumen...")
    fig_reporte = create_summary_reporte(df)
    fig_reporte.show()

    print("""
    INTERPRETACION - Reporte Resumen:
    ----------------------------------
    El reporte integra multiples visualizaciones en una sola vista.
    - Permite una comprension rapida del dataset completo
    - Facilita la comparacion entre diferentes metricas

    Utilidad analitica:
    - Vision general para presentaciones ejecutivas
    - Punto de partida para analisis mas profundos
    - Deteccion rapida de patrones y anomalias
    """)

    # ==========================================================================
    # CONCLUSIONES GENERALES
    # ==========================================================================
    print("\n" + "="*60)
    print("CONCLUSIONES GENERALES")
    print("="*60)

    # Calcular estadisticas clave
    top_country = df['Nationality'].value_counts().index[0]
    top_country_count = df['Nationality'].value_counts().values[0]

    most_valuable = df.loc[df['Value'].idxmax()]
    best_player = df.loc[df['Overall'].idxmax()]

    print(f"""
    1. COMPOSICION ETARIA:
       - Edad promedio: {df['Age'].mean():.1f} anos
       - Rango de edades: {df['Age'].min()} - {df['Age'].max()} anos
       - Mayoria de jugadores en edad productiva (20-30 anos)

    2. DISTRIBUCION GEOGRAFICA:
       - Total de paises representados: {df['Nationality'].nunique()}
       - Pais mas representado: {top_country} ({top_country_count:,} jugadores)
       - Alta concentracion en paises europeos y sudamericanos

    3. CALIDAD Y VALOR:
       - Correlacion Overall-Valor: {df['Overall'].corr(df['Value']):.3f}
       - Jugador mas valioso: {most_valuable['Name']} (EUR {most_valuable['Value']/1e6:.1f}M)
       - Mejor jugador: {best_player['Name']} (Overall: {best_player['Overall']})

    VISUALIZACION MAS VALIOSA:
    -------------------------
    El scatter plot de Overall vs Value proporciona el mayor valor analitico porque:
    - Revela oportunidades de mercado (jugadores infravalorados)
    - Cuantifica la relacion calidad-precio
    - Facilita decisiones de scouting y transferencias
    - Permite identificar outliers estrategicamente importantes
    """)

    # Guardar visualizaciones como archivos HTML
    print("\n" + "="*60)
    print("GUARDANDO VISUALIZACIONES")
    print("="*60)

    output_dir = '.'

    fig_age.write_html(f"{output_dir}\\fifa_age_histogram.html")
    print(f"Guardado: {output_dir}\\fifa_age_histogram.html")

    fig_countries.write_html(f"{output_dir}\\fifa_top_countries.html")
    print(f"Guardado: {output_dir}\\fifa_top_countries.html")

    fig_scatter.write_html(f"{output_dir}\\fifa_overall_value_scatter.html")
    print(f"Guardado: {output_dir}\\fifa_overall_value_scatter.html")

    fig_reporte.write_html(f"{output_dir}\\fifa_reporte.html")
    print(f"Guardado: {output_dir}\\fifa_reporte.html")

    print("\n" + "="*60)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("="*60)


if __name__ == '__main__':
    main()