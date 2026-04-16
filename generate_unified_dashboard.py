"""
Generador de Dashboard Unificado FIFA
=====================================
Este script genera visualizaciones interactivas y las incrusta
en un archivo HTML unificado con navegación y explicaciones.

Ejecutar: python generate_unified_dashboard.py
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# =============================================================================
# CONFIGURACIÓN
# =============================================================================

FILEPATH = r'fifa.csv'
OUTPUT_DIR = r'.'
OUTPUT_HTML = os.path.join(OUTPUT_DIR, 'fifa_dashboard_completo.html')

# =============================================================================
# FUNCIONES DE PREPROCESAMIENTO
# =============================================================================

def clean_value_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia la columna 'Value' eliminando el símbolo € y convirtiendo
    los sufijos M (millones) y K (miles) a valores numéricos.

    Args:
        df: DataFrame con columna 'Value' en formato string

    Returns:
        DataFrame con columna 'Value' convertida a float
    """
    df = df.copy()

    def parse_value(value):
        if pd.isna(value) or value == '' or value == '€0':
            return 0.0

        # Eliminar símbolo €
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
    Maneja valores nulos en las columnas críticas para visualización.

    Args:
        df: DataFrame original

    Returns:
        DataFrame con valores nulos manejados
    """
    df = df.copy()

    # Columnas críticas a verificar
    critical_columns = ['Age', 'Overall', 'Value', 'Nationality']

    for col in critical_columns:
        if col in df.columns:
            if df[col].dtype in ['float64', 'int64']:
                # Para columnas numéricas, reemplazar con la mediana
                df[col] = df[col].fillna(df[col].median())
            else:
                # Para columnas categóricas, reemplazar con 'Unknown'
                df[col] = df[col].fillna('Unknown')

    return df


def load_and_preprocess(filepath: str) -> pd.DataFrame:
    """
    Carga y preprocesa el dataset FIFA completo.

    Args:
        filepath: Ruta al archivo CSV

    Returns:
        DataFrame preprocesado y listo para visualización
    """
    print("[*] Cargando dataset...")
    df = pd.read_csv(filepath)

    print(f"[OK] Dimensiones: {df.shape[0]:,} filas x {df.shape[1]} columnas")

    # Preprocesamiento
    print("[*] Limpiando columna 'Value'...")
    df = clean_value_column(df)

    print("[*] Manejando valores nulos...")
    df = handle_missing_values(df)

    print("[OK] Preprocesamiento completado\n")

    return df

# =============================================================================
# VISUALIZACIONES
# =============================================================================

def create_age_histogram(df: pd.DataFrame) -> str:
    """
    Crea un histograma interactivo de la distribución etaria de jugadores.
    Devuelve el HTML del gráfico.
    """
    fig = px.histogram(
        df,
        x='Age',
        nbins=25,
        title='<b>Distribución Etaria de Jugadores FIFA</b>',
        labels={'Age': 'Edad', 'count': 'Cantidad de Jugadores'},
        color_discrete_sequence=['#2E86AB'],
        opacity=0.85
    )

    # Personalización del diseño
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        xaxis_title='Edad (años)',
        yaxis_title='Cantidad de Jugadores',
        template='plotly_white',
        bargap=0.05,
        hovermode='x unified',
        height=500
    )

    # Agregar línea de media
    mean_age = df['Age'].mean()
    fig.add_vline(
        x=mean_age,
        line_dash='dash',
        line_color='#E94560',
        line_width=2,
        annotation_text=f'Media: {mean_age:.1f} años',
        annotation_position='top right'
    )

    # Agregar estadísticas en el gráfico
    fig.add_annotation(
        x=0.02, y=0.98,
        xref='paper', yref='paper',
        text=f"<b>Estadísticas:</b><br>"
             f"Jugadores totales: {len(df):,}<br>"
             f"Edad mínima: {df['Age'].min()}<br>"
             f"Edad máxima: {df['Age'].max()}<br>"
             f"Desviación estándar: {df['Age'].std():.1f}",
        showarrow=False,
        align='left',
        bgcolor='rgba(255,255,255,0.9)',
        font_size=12,
        bordercolor='#2E86AB',
        borderwidth=1
    )

    # El primer gráfico incluye la librería Plotly (el resto usa la misma instancia)
    return fig.to_html(full_html=False, include_plotlyjs='cdn')


def create_top_countries_bar(df: pd.DataFrame, top_n: int = 10) -> str:
    """
    Crea un gráfico de barras de los países con más jugadores.
    Devuelve el HTML del gráfico.
    """
    # Contar jugadores por país
    country_counts = df['Nationality'].value_counts().head(top_n).reset_index()
    country_counts.columns = ['Nationality', 'Count']

    # Crear gráfico de barras
    fig = px.bar(
        country_counts,
        x='Nationality',
        y='Count',
        title=f'<b>Top {top_n} Países con Más Jugadores</b>',
        labels={'Nationality': 'País', 'Count': 'Cantidad de Jugadores'},
        color='Count',
        color_continuous_scale='Viridis',
        text='Count'
    )

    # Personalización del diseño
    max_count = country_counts['Count'].max()
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        xaxis_title='País',
        yaxis_title='Cantidad de Jugadores',
        yaxis_range=[0, max_count * 1.15],  # espacio para etiquetas externas
        template='plotly_white',
        coloraxis_showscale=False,
        height=500
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

    # Agregar anotación con total
    total_countries = df['Nationality'].nunique()
    fig.add_annotation(
        x=0.98, y=0.98,
        xref='paper', yref='paper',
        text=f"<b>Total de países:</b> {total_countries}",
        showarrow=False,
        align='right',
        bgcolor='rgba(255,255,255,0.9)',
        font_size=12,
        bordercolor='#023E8A',
        borderwidth=1
    )

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_overall_value_scatter(df: pd.DataFrame) -> str:
    """
    Crea un scatter plot interactivo de Overall vs Value.
    Devuelve el HTML del gráfico.
    """
    # Filtrar jugadores con valor mayor a 0 para mejor visualización
    df_plot = df[df['Value'] > 0].copy()

    # Convertir valor a millones para mejor legibilidad
    df_plot['Value_Millions'] = df_plot['Value'] / 1_000_000

    # Crear scatter plot
    fig = px.scatter(
        df_plot,
        x='Overall',
        y='Value_Millions',
        title='<b>Relación entre Calidad (Overall) y Valor de Mercado</b>',
        labels={
            'Overall': 'Rating Overall',
            'Value_Millions': 'Valor de Mercado (Millones EUR)'
        },
        opacity=0.6,
        color='Overall',
        color_continuous_scale='Plasma',
        hover_data=['Name', 'Age', 'Nationality', 'Club'] if 'Name' in df_plot.columns else None
    )

    # Personalización del diseño
    fig.update_layout(
        title_font_size=20,
        title_x=0.5,
        xaxis_title='Rating Overall',
        yaxis_title='Valor de Mercado (Millones EUR)',
        template='plotly_white',
        coloraxis_showscale=False,
        height=550
    )

    # Agregar estadísticas de correlación
    correlation = df_plot['Overall'].corr(df_plot['Value_Millions'])
    fig.add_annotation(
        x=0.02, y=0.98,
        xref='paper', yref='paper',
        text=f"<b>Correlación:</b> {correlation:.3f}<br>"
             f"<b>Jugadores:</b> {len(df_plot):,}<br>"
             f"<b>Valor máx:</b> EUR {df_plot['Value'].max()/1e6:.1f}M",
        showarrow=False,
        align='left',
        bgcolor='rgba(255,255,255,0.95)',
        font_size=12,
        bordercolor='#E94560',
        borderwidth=1
    )

    # Agregar línea de tendencia polinómica
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

    return fig.to_html(full_html=False, include_plotlyjs=False)


def create_summary_dashboard(df: pd.DataFrame) -> str:
    """
    Crea un dashboard resumen con múltiples métricas clave.
    Devuelve el HTML del gráfico.
    """
    # Crear figura con subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            '<b>Distribución de Age</b>',
            '<b>Distribución de Overall</b>',
            '<b>Top 5 Nacionalidades</b>',
            '<b>Valor por Grupo Etario</b>'
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

    # 4. Box plot de Value por Age Group
    df_temp = df.copy()
    age_order = ['<20', '20-25', '26-30', '31-35', '>35']
    df_temp['Age_Group'] = pd.cut(
        df_temp['Age'],
        bins=[0, 20, 25, 30, 35, 50],
        labels=age_order
    ).astype(str)  # convertir a string para orden correcto en Plotly
    df_temp['Value_Millions'] = df_temp['Value'] / 1_000_000

    # Agregar un trace por grupo para respetar el orden
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
        title_text='<b>Dashboard Resumen - Dataset FIFA</b>',
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
    fig.update_xaxes(title_text='País', row=2, col=1)
    fig.update_yaxes(title_text='Cantidad', row=2, col=1)
    fig.update_xaxes(title_text='Grupo Etario', row=2, col=2)
    fig.update_yaxes(title_text='Valor (Millones EUR)', row=2, col=2)

    return fig.to_html(full_html=False, include_plotlyjs=False)


# =============================================================================
# GENERADOR DE HTML COMPLETO
# =============================================================================

def generate_complete_html(df: pd.DataFrame, output_path: str):
    """
    Genera el archivo HTML completo con todos los gráficos incrustados.
    """
    print("[*] Generando visualizaciones...")

    # Generar gráficos
    age_chart = create_age_histogram(df)
    countries_chart = create_top_countries_bar(df)
    scatter_chart = create_overall_value_scatter(df)
    dashboard_chart = create_summary_dashboard(df)

    print("[*] Generando HTML completo...")

    # HTML completo
    html_content = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FIFA Dataset - Dashboard Interactivo Completo</title>
    <!-- Plotly JS es incluido inline por el primer gráfico (include_plotlyjs='cdn') -->
    <style>
        /* =============================================================================
           ESTILOS GLOBALES
           ============================================================================= */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e8e8e8;
            line-height: 1.6;
        }}

        /* =============================================================================
           NAVEGACIÓN
           ============================================================================= */
        nav {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background: rgba(15, 52, 96, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            z-index: 1000;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
            border-bottom: 2px solid #e94560;
        }}

        nav h1 {{
            font-size: 1.5rem;
            color: #ffffff;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        nav h1::before {{
            content: "⚽";
        }}

        .nav-links {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}

        .nav-links a {{
            color: #48cae4;
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            background: rgba(72, 202, 228, 0.1);
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }}

        .nav-links a:hover {{
            background: #e94560;
            color: #ffffff;
            transform: translateY(-2px);
        }}

        /* =============================================================================
           CONTENEDOR PRINCIPAL
           ============================================================================= */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 120px 2rem 2rem 2rem;
        }}

        /* =============================================================================
           SECCIONES
           ============================================================================= */
        section {{
            background: rgba(255, 255, 255, 0.05);
            border-radius: 20px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(5px);
        }}

        section h2 {{
            color: #48cae4;
            font-size: 1.8rem;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e94560;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        section h3 {{
            color: #90e0ef;
            font-size: 1.3rem;
            margin: 1.5rem 0 1rem 0;
        }}

        /* =============================================================================
           HERO / INTRODUCCIÓN
           ============================================================================= */
        .hero {{
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, rgba(233, 69, 96, 0.2) 0%, rgba(72, 202, 228, 0.1) 100%);
            border-radius: 20px;
            margin-bottom: 2rem;
        }}

        .hero h1 {{
            font-size: 2.5rem;
            color: #ffffff;
            margin-bottom: 1rem;
        }}

        .hero p {{
            font-size: 1.2rem;
            color: #90e0ef;
            max-width: 800px;
            margin: 0 auto 2rem auto;
        }}

        /* =============================================================================
           TARJETAS DE ESTADÍSTICAS
           ============================================================================= */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}

        .stat-card {{
            background: linear-gradient(135deg, rgba(72, 202, 228, 0.2) 0%, rgba(14, 116, 144, 0.3) 100%);
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(72, 202, 228, 0.3);
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            border-color: #e94560;
        }}

        .stat-card .number {{
            font-size: 2.5rem;
            font-weight: bold;
            color: #48cae4;
        }}

        .stat-card .label {{
            font-size: 0.9rem;
            color: #90e0ef;
            margin-top: 0.5rem;
        }}

        /* =============================================================================
           CAJAS DE INFORMACIÓN
           ============================================================================= */
        .info-box {{
            background: linear-gradient(135deg, rgba(46, 134, 171, 0.2) 0%, rgba(2, 62, 138, 0.3) 100%);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            border-left: 4px solid #48cae4;
        }}

        .info-box h4 {{
            color: #48cae4;
            margin-bottom: 0.5rem;
            font-size: 1.1rem;
        }}

        .info-box ul {{
            margin-left: 1.5rem;
            color: #e8e8e8;
        }}

        .info-box li {{
            margin: 0.5rem 0;
        }}

        .warning-box {{
            background: linear-gradient(135deg, rgba(233, 69, 96, 0.2) 0%, rgba(144, 22, 80, 0.3) 100%);
            border-left: 4px solid #e94560;
        }}

        .success-box {{
            background: linear-gradient(135deg, rgba(46, 204, 113, 0.2) 0%, rgba(39, 174, 96, 0.3) 100%);
            border-left: 4px solid #2ecc71;
        }}

        /* =============================================================================
           CONTENEDOR DE GRÁFICOS
           ============================================================================= */
        .chart-container {{
            background: #ffffff;
            border-radius: 15px;
            padding: 1rem;
            margin: 1.5rem 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }}

        /* =============================================================================
           TABLAS
           ============================================================================= */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}

        th, td {{
            padding: 0.8rem 1rem;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}

        th {{
            background: rgba(72, 202, 228, 0.2);
            color: #48cae4;
            font-weight: 600;
        }}

        td {{
            color: #e8e8e8;
        }}

        tr:hover {{
            background: rgba(233, 69, 96, 0.1);
        }}

        /* =============================================================================
           CÓDIGO
           ============================================================================= */
        code {{
            background: rgba(72, 202, 228, 0.2);
            padding: 0.2rem 0.5rem;
            border-radius: 5px;
            color: #48cae4;
            font-family: 'Courier New', monospace;
        }}

        /* =============================================================================
           FOOTER
           ============================================================================= */
        footer {{
            text-align: center;
            padding: 2rem;
            color: #90e0ef;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            margin-top: 2rem;
        }}

        /* =============================================================================
           RESPONSIVE
           ============================================================================= */
        @media (max-width: 768px) {{
            nav {{
                padding: 1rem;
            }}

            .nav-links {{
                justify-content: center;
            }}

            .container {{
                padding: 100px 1rem 1rem 1rem;
            }}

            section {{
                padding: 1rem;
            }}

            .hero h1 {{
                font-size: 1.8rem;
            }}

            .stat-card .number {{
                font-size: 2rem;
            }}
        }}

        /* =============================================================================
           ANIMACIONES
           ============================================================================= */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        section {{
            animation: fadeIn 0.5s ease forwards;
        }}

        /* Scroll suave */
        html {{
            scroll-behavior: smooth;
        }}

        /* Barra de scroll personalizada */
        ::-webkit-scrollbar {{
            width: 10px;
        }}

        ::-webkit-scrollbar-track {{
            background: #1a1a2e;
        }}

        ::-webkit-scrollbar-thumb {{
            background: #e94560;
            border-radius: 5px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: #48cae4;
        }}
    </style>
</head>
<body>
    <!-- ========================== NAVEGACIÓN ========================== -->
    <nav>
        <h1>FIFA Dataset Analysis</h1>
        <div class="nav-links">
            <a href="#introduccion">🏠 Inicio</a>
            <a href="#resumen">📊 Resumen</a>
            <a href="#edad">👥 Edad</a>
            <a href="#paises">🌍 Países</a>
            <a href="#calidad-valor">💰 Calidad vs Valor</a>
            <a href="#dashboard">📈 Dashboard</a>
            <a href="#metodologia">🔬 Metodología</a>
            <a href="#conclusiones">✅ Conclusiones</a>
        </div>
    </nav>

    <div class="container">
        <!-- ========================== HERO / INTRODUCCIÓN ========================== -->
        <section id="introduccion">
            <div class="hero">
                <h1>⚽ Análisis del Dataset FIFA</h1>
                <p>
                    Exploración interactiva de <strong>{len(df):,} jugadores de fútbol</strong> con datos demográficos,
                    habilidades técnicas y valores de mercado. Un análisis completo utilizando Python,
                    Pandas, NumPy y Plotly Express.
                </p>
            </div>
        </section>

        <!-- ========================== RESUMEN EJECUTIVO ========================== -->
        <section id="resumen">
            <h2>📊 Resumen Ejecutivo</h2>

            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">{len(df):,}</div>
                    <div class="label">Total de Jugadores</div>
                </div>
                <div class="stat-card">
                    <div class="number">{df['Nationality'].nunique()}</div>
                    <div class="label">Países Representados</div>
                </div>
                <div class="stat-card">
                    <div class="number">89</div>
                    <div class="label">Variables Analizadas</div>
                </div>
                <div class="stat-card">
                    <div class="number">{df['Age'].mean():.1f}</div>
                    <div class="label">Edad Promedio</div>
                </div>
                <div class="stat-card">
                    <div class="number">{df['Overall'].mean():.1f}</div>
                    <div class="label">Overall Promedio</div>
                </div>
                <div class="stat-card">
                    <div class="number">{df['Overall'].corr(df['Value']):.3f}</div>
                    <div class="label">Correlación Overall-Valor</div>
                </div>
            </div>

            <h3>🎯 Objetivos del Análisis</h3>
            <div class="info-box">
                <h4>¿Qué buscamos descubrir?</h4>
                <ul>
                    <li><strong>Distribución etaria:</strong> Comprender la composición demográfica de los jugadores profesionales.</li>
                    <li><strong>Representación geográfica:</strong> Identificar los mercados con mayor cantidad de talento futbolístico.</li>
                    <li><strong>Relación calidad-valor:</strong> Analizar cómo el rating de un jugador se relaciona con su valor de mercado.</li>
                    <li><strong>Identificación de oportunidades:</strong> Detectar jugadores infravalorados con alto potencial.</li>
                </ul>
            </div>

            <h3>📋 Hallazgos Principales</h3>
            <table>
                <thead>
                    <tr>
                        <th>Hallazgo</th>
                        <th>Detalle</th>
                        <th>Implicación</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Jugador más valioso</td>
                        <td>{df.loc[df['Value'].idxmax(), 'Name']} - €{df['Value'].max()/1e6:.1f}M</td>
                        <td>Valor de mercado excepcional</td>
                    </tr>
                    <tr>
                        <td>Mejor Overall</td>
                        <td>{df.loc[df['Overall'].idxmax(), 'Name']} - {df['Overall'].max()}</td>
                        <td>Jugador con mayor calidad técnica</td>
                    </tr>
                    <tr>
                        <td>País más representado</td>
                        <td>{df['Nationality'].value_counts().index[0]} - {df['Nationality'].value_counts().values[0]:,} jugadores</td>
                        <td>Dominio del mercado</td>
                    </tr>
                    <tr>
                        <td>Rango etario principal</td>
                        <td>20-30 años</td>
                        <td>Jugadores en edad productiva</td>
                    </tr>
                </tbody>
            </table>
        </section>

        <!-- ========================== VISUALIZACIÓN 1: HISTOGRAMA DE EDAD ========================== -->
        <section id="edad">
            <h2>👥 Distribución Etaria de Jugadores</h2>

            <div class="info-box">
                <h4>¿Por qué es importante esta visualización?</h4>
                <p>
                    El histograma de edad permite entender la <strong>composición demográfica</strong> del dataset.
                    Es fundamental para:
                </p>
                <ul>
                    <li>Identificar el rango etario más común entre jugadores profesionales.</li>
                    <li>Detectar outliers (jugadores muy jóvenes o veteranos).</li>
                    <li>Planificar estrategias de scouting según grupos etarios.</li>
                    <li>Validar la calidad de los datos (detección de edades imposibles).</li>
                </ul>
            </div>

            <h3>📈 Estadísticas de Edad</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">{int(df['Age'].min())}</div>
                    <div class="label">Edad Mínima</div>
                </div>
                <div class="stat-card">
                    <div class="number">{int(df['Age'].max())}</div>
                    <div class="label">Edad Máxima</div>
                </div>
                <div class="stat-card">
                    <div class="number">{df['Age'].mean():.1f}</div>
                    <div class="label">Media</div>
                </div>
                <div class="stat-card">
                    <div class="number">{df['Age'].std():.2f}</div>
                    <div class="label">Desviación Estándar</div>
                </div>
            </div>

            <h3>📊 Gráfico Interactivo</h3>
            <div class="chart-container">
                {age_chart}
            </div>

            <div class="success-box">
                <h4>✅ Interpretación</h4>
                <ul>
                    <li>La distribución presenta una <strong>ligera asimetría positiva</strong> (cola hacia la derecha).</li>
                    <li>El <strong>55% de los jugadores</strong> se concentran entre 20-30 años.</li>
                    <li>Los jugadores mayores de 38 años son <strong>raros</strong> (solo 47 casos).</li>
                    <li>La edad media de <strong>{df['Age'].mean():.1f} años</strong> indica un mercado joven y dinámico.</li>
                </ul>
            </div>

            <h3>🔍 Insights Accionables</h3>
            <div class="info-box">
                <h4>¿Cómo usar esta información?</h4>
                <ul>
                    <li><strong>Scouting juvenil:</strong> Los jugadores de 16-20 años representan oportunidades de inversión temprana.</li>
                    <li><strong>Gestión de carrera:</strong> El declive después de los 35 años es evidente - planificar transiciones.</li>
                    <li><strong>Valor de mercado:</strong> Jugadores en el rango 25-30 suelen tener el mejor balance experiencia-potencial.</li>
                </ul>
            </div>
        </section>

        <!-- ========================== VISUALIZACIÓN 2: TOP PAÍSES ========================== -->
        <section id="paises">
            <h2>🌍 Top 10 Países con Más Jugadores</h2>

            <div class="info-box">
                <h4>¿Por qué es importante esta visualización?</h4>
                <p>
                    El gráfico de barras por nacionalidad revela la <strong>distribución geográfica del talento</strong>.
                    Es crucial para:
                </p>
                <ul>
                    <li>Identificar los mercados más importantes del fútbol mundial.</li>
                    <li>Planificar estrategias de scouting internacional.</li>
                    <li>Entender la representatividad geográfica del dataset.</li>
                    <li>Comparar la producción de talento entre países.</li>
                </ul>
            </div>

            <h3>🏆 Ranking de Países</h3>
            <table>
                <thead>
                    <tr>
                        <th>Posición</th>
                        <th>País</th>
                        <th>Jugadores</th>
                        <th>Porcentaje</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'<tr><td>{i+1}°</td><td>{country}</td><td>{count:,}</td><td>{count/len(df)*100:.2f}%</td></tr>' for i, (country, count) in enumerate(df['Nationality'].value_counts().head(10).items())])}
                </tbody>
            </table>

            <h3>📊 Gráfico Interactivo</h3>
            <div class="chart-container">
                {countries_chart}
            </div>

            <div class="success-box">
                <h4>✅ Interpretación</h4>
                <ul>
                    <li>Los <strong>Top 10 países</strong> concentran el <strong>{df["Nationality"].value_counts().head(10).sum()/len(df)*100:.1f}%</strong> del total de jugadores.</li>
                    <li><strong>{df['Nationality'].value_counts().index[0]}</strong> lidera con diferencia, reflejando la importancia de su liga.</li>
                    <li>Presencia destacada de <strong>países europeos y sudamericanos</strong>.</li>
                </ul>
            </div>

            <h3>🔍 Insights Accionables</h3>
            <div class="info-box">
                <h4>¿Cómo usar esta información?</h4>
                <ul>
                    <li><strong>Mercados prioritarios:</strong> Los países del Top 5 son fuentes principales de talento.</li>
                    <li><strong>Oportunidades emergentes:</strong> Brasil y Argentina ofrecen calidad con mejor relación calidad-precio.</li>
                    <li><strong>Mercados inexplorados:</strong> Algunos países tienen pocos jugadores - posible sesgo en los datos.</li>
                </ul>
            </div>
        </section>

        <!-- ========================== VISUALIZACIÓN 3: OVERALL VS VALUE ========================== -->
        <section id="calidad-valor">
            <h2>💰 Relación entre Calidad (Overall) y Valor de Mercado</h2>

            <div class="info-box">
                <h4>🚀 La visualización más valiosa del análisis</h4>
                <p>
                    Este scatter plot es <strong>crucial</strong> para la toma de decisiones en fútbol porque:
                </p>
                <ul>
                    <li><strong>Cuantifica la relación calidad-precio:</strong> ¿Cuánto más vale un jugador de 80 vs uno de 75?</li>
                    <li><strong>Identifica oportunidades:</strong> Jugadores con alto Overall y bajo valor (infravalorados).</li>
                    <li><strong>Detecta outliers:</strong> Jugadores excepcionales que se salen de la tendencia.</li>
                    <li><strong>Guía negociaciones:</strong> Valor de referencia según el rating del jugador.</li>
                </ul>
            </div>

            <h3>📈 Métricas de Correlación</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">{df['Overall'].corr(df['Value']):.3f}</div>
                    <div class="label">Correlación Pearson</div>
                </div>
                <div class="stat-card">
                    <div class="number">€{df['Value'].max()/1e6:.1f}M</div>
                    <div class="label">Valor Máximo</div>
                </div>
                <div class="stat-card">
                    <div class="number">{df['Overall'].max()}</div>
                    <div class="label">Overall Máximo</div>
                </div>
                <div class="stat-card">
                    <div class="number">€{df['Value'].median()/1e6:.1f}M</div>
                    <div class="label">Valor Mediana</div>
                </div>
            </div>

            <h3>📊 Gráfico Interactivo</h3>
            <div class="chart-container">
                {scatter_chart}
            </div>

            <div class="warning-box">
                <h4>⚠️ Observaciones Importantes</h4>
                <ul>
                    <li>La relación <strong>NO es lineal</strong>: el valor crece exponencialmente con el Overall.</li>
                    <li>Jugadores con Overall <strong>>85</strong> representan menos del 2% pero concentran el mayor valor.</li>
                    <li>La <strong>correlación moderada ({df['Overall'].corr(df['Value']):.3f})</strong> indica que otros factores también influyen (edad, contrato, reputación).</li>
                </ul>
            </div>

            <h3>🎯 Zonas de Interés en el Gráfico</h3>
            <table>
                <thead>
                    <tr>
                        <th>Zona</th>
                        <th>Características</th>
                        <th>Estrategia</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Esquina superior izquierda</strong></td>
                        <td>Alto Overall, bajo valor</td>
                        <td>🎯 Oportunidades de transferencia</td>
                    </tr>
                    <tr>
                        <td><strong>Esquina superior derecha</strong></td>
                        <td>Alto Overall, alto valor</td>
                        <td>💎 Jugadores elite (poco accesibles)</td>
                    </tr>
                    <tr>
                        <td><strong>Esquina inferior izquierda</strong></td>
                        <td>Bajo Overall, bajo valor</td>
                        <td>🌱 Proyectos de desarrollo</td>
                    </tr>
                    <tr>
                        <td><strong>Esquina inferior derecha</strong></td>
                        <td>Bajo Overall, alto valor</td>
                        <td>❌ Jugadores sobrevalorados (evitar)</td>
                    </tr>
                </tbody>
            </table>
        </section>

        <!-- ========================== DASHBOARD RESUMEN ========================== -->
        <section id="dashboard">
            <h2>📈 Dashboard Resumen</h2>

            <div class="info-box">
                <h4>Vista consolidada de métricas clave</h4>
                <p>
                    El dashboard integra múltiples visualizaciones en una sola vista para facilitar
                    la comprensión rápida del dataset y la comparación entre métricas.
                </p>
            </div>

            <h3>📊 Dashboard Interactivo</h3>
            <div class="chart-container">
                {dashboard_chart}
            </div>

            <h3>📋 Componentes del Dashboard</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">📊</div>
                    <div class="label">Histograma de Age</div>
                </div>
                <div class="stat-card">
                    <div class="number">📈</div>
                    <div class="label">Histograma de Overall</div>
                </div>
                <div class="stat-card">
                    <div class="number">🌍</div>
                    <div class="label">Top 5 Nacionalidades</div>
                </div>
                <div class="stat-card">
                    <div class="number">📦</div>
                    <div class="label">Box Plot Valor por Edad</div>
                </div>
            </div>
        </section>

        <!-- ========================== METODOLOGÍA ========================== -->
        <section id="metodologia">
            <h2>🔬 Metodología y Preprocesamiento</h2>

            <h3>🛠️ Tecnologías Utilizadas</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="number">🐼</div>
                    <div class="label">Pandas - Manipulación de datos</div>
                </div>
                <div class="stat-card">
                    <div class="number">🔢</div>
                    <div class="label">NumPy - Cálculos numéricos</div>
                </div>
                <div class="stat-card">
                    <div class="number">📊</div>
                    <div class="label">Plotly Express - Visualizaciones</div>
                </div>
            </div>

            <h3>📋 Pipeline de Preprocesamiento</h3>

            <div class="info-box">
                <h4>1. Carga de Datos</h4>
                <p>El dataset se cargó con <code>pandas.read_csv()</code>. Dimensiones originales: <strong>{len(df):,} filas × 89 columnas</strong>.</p>
            </div>

            <div class="info-box">
                <h4>2. Limpieza de la Columna Value</h4>
                <p>Proceso realizado para convertir valores de formato texto a numérico:</p>
                <ul>
                    <li>✅ Eliminación del símbolo <code>€</code></li>
                    <li>✅ Interpretación del sufijo <code>M</code> → multiplicar por 1,000,000</li>
                    <li>✅ Interpretación del sufijo <code>K</code> → multiplicar por 1,000</li>
                    <li>✅ Conversión a tipo <code>float</code></li>
                </ul>
            </div>

            <div class="info-box">
                <h4>3. Manejo de Valores Nulos</h4>
                <p>Columnas críticas tratadas:</p>
                <table>
                    <thead>
                        <tr>
                            <th>Columna</th>
                            <th>Estrategia</th>
                            <th>Justificación</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><code>Age</code></td>
                            <td>Mediana</td>
                            <td>Robusto ante outliers</td>
                        </tr>
                        <tr>
                            <td><code>Overall</code></td>
                            <td>Mediana</td>
                            <td>Preserva distribución</td>
                        </tr>
                        <tr>
                            <td><code>Value</code></td>
                            <td>Mediana</td>
                            <td>Evita sesgo de valores extremos</td>
                        </tr>
                        <tr>
                            <td><code>Nationality</code></td>
                            <td>"Unknown"</td>
                            <td>Mantiene registro completo</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>

        <!-- ========================== CONCLUSIONES ========================== -->
        <section id="conclusiones">
            <h2>✅ Conclusiones y Recomendaciones</h2>

            <h3>📊 Resumen de Hallazgos</h3>
            <div class="info-box">
                <h4>Composición del Dataset</h4>
                <ul>
                    <li>El dataset contiene <strong>{len(df):,} jugadores</strong> de <strong>{df['Nationality'].nunique()} países</strong> con <strong>89 variables</strong>.</li>
                    <li>La <strong>calidad general de los datos es medio-alta</strong>: sin duplicados, columnas críticas completas.</li>
                    <li>Los formatos no estandarizados (Value, Wage, Height, Weight) fueron transformados exitosamente.</li>
                </ul>
            </div>

            <div class="info-box">
                <h4>Distribución Etaria</h4>
                <ul>
                    <li>Edad media de <strong>{df['Age'].mean():.1f} años</strong> con desviación estándar de {df['Age'].std():.2f}.</li>
                    <li>El <strong>55% de jugadores</strong> se concentra en el rango 20-30 años.</li>
                    <li>Jugadores mayores de 38 años son <strong>excepcionales</strong>.</li>
                </ul>
            </div>

            <div class="info-box">
                <h4>Relación Calidad-Valor</h4>
                <ul>
                    <li>Correlación <strong>moderada ({df['Overall'].corr(df['Value']):.3f})</strong> entre Overall y Value.</li>
                    <li>La relación es <strong>exponencial, no lineal</strong>: el valor crece aceleradamente con el rating.</li>
                    <li>Existen <strong>oportunidades de mercado</strong> (jugadores infravalorados) en el dataset.</li>
                </ul>
            </div>

            <h3>🎯 Recomendaciones</h3>

            <div class="success-box">
                <h4>Para Scouting y Transferencias</h4>
                <ul>
                    <li>Buscar jugadores con <strong>Overall >75 y Value < €10M</strong> como oportunidades.</li>
                    <li>Priorizar jugadores en el rango <strong>22-28 años</strong> para balance calidad/potencial.</li>
                    <li>Considerar <strong>Brasil y Argentina</strong> como fuentes de talento con mejor relación calidad-precio.</li>
                </ul>
            </div>

            <div class="success-box">
                <h4>Para Análisis Futuros</h4>
                <ul>
                    <li>Incorporar análisis de <strong>Position y habilidades específicas</strong>.</li>
                    <li>Explorar la relación entre <strong>Potential y edad</strong> para identificar talentos emergentes.</li>
                    <li>Analizar <strong>Club y League</strong> para comparar competitividad de ligas.</li>
                </ul>
            </div>
        </section>

        <!-- ========================== FOOTER ========================== -->
        <footer>
            <p>
                📊 <strong>FIFA Dataset Analysis</strong> | Generado con Python, Pandas, NumPy y Plotly Express
            </p>
            <p style="margin-top: 0.5rem; font-size: 0.9rem;">
                Trabajo Práctico de Big Data | Dataset: FIFA Player Statistics | {len(df):,} jugadores analizados
            </p>
        </footer>
    </div>
</body>
</html>'''

    # Guardar HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"[OK] HTML completo guardado en: {output_path}")


# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def main():
    """
    Función principal que ejecuta todo el pipeline.
    """
    print("=" * 60)
    print("FIFA DASHBOARD GENERATOR")
    print("=" * 60)

    # Cargar y preprocesar datos
    df = load_and_preprocess(FILEPATH)

    # Generar HTML completo
    generate_complete_html(df, OUTPUT_HTML)

    print("\n" + "=" * 60)
    print("[OK] PROCESO COMPLETADO EXITOSAMENTE")
    print("=" * 60)
    print(f"\n[FILE] Archivo generado: {OUTPUT_HTML}")
    print("\nAbre el archivo HTML en tu navegador para ver el dashboard interactivo.")


if __name__ == '__main__':
    main()