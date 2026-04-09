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


def create_summary_dashboard(df: pd.DataFrame) -> go.Figure:
    """
    Crea un dashboard resumen con multiples metricas clave.

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

    # 4. Box plot de Value por Age Group
    df_temp = df.copy()
    df_temp['Age_Group'] = pd.cut(
        df_temp['Age'],
        bins=[0, 20, 25, 30, 35, 50],
        labels=['<20', '20-25', '26-30', '31-35', '>35']
    )
    df_temp['Value_Millions'] = df_temp['Value'] / 1_000_000

    fig.add_trace(
        go.Box(
            x=df_temp['Age_Group'],
            y=df_temp['Value_Millions'],
            name='Valor (M EUR)',
            marker_color='#48CAE4'
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
        height=700,
        width=1200
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
# FUNCION PRINCIPAL
# =============================================================================

def main():
    """
    Funcion principal que ejecuta todo el pipeline de visualizacion.
    """
    # Ruta del dataset
    filepath = r'C:\Users\IPF-2026\Desktop\big-data-trabajo-1\fifa.csv'

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
    # VISUALIZACION 4: Dashboard Resumen
    # ==========================================================================
    print("\n4. Generando dashboard resumen...")
    fig_dashboard = create_summary_dashboard(df)
    fig_dashboard.show()

    print("""
    INTERPRETACION - Dashboard Resumen:
    ----------------------------------
    El dashboard integra multiples visualizaciones en una sola vista.
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

    output_dir = r'C:\Users\IPF-2026\Desktop\big-data-trabajo-1'

    fig_age.write_html(f"{output_dir}\\fifa_age_histogram.html")
    print(f"Guardado: {output_dir}\\fifa_age_histogram.html")

    fig_countries.write_html(f"{output_dir}\\fifa_top_countries.html")
    print(f"Guardado: {output_dir}\\fifa_top_countries.html")

    fig_scatter.write_html(f"{output_dir}\\fifa_overall_value_scatter.html")
    print(f"Guardado: {output_dir}\\fifa_overall_value_scatter.html")

    fig_dashboard.write_html(f"{output_dir}\\fifa_dashboard.html")
    print(f"Guardado: {output_dir}\\fifa_dashboard.html")

    print("\n" + "="*60)
    print("PROCESO COMPLETADO EXITOSAMENTE")
    print("="*60)


if __name__ == '__main__':
    main()