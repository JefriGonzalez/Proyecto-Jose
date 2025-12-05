import plotly.graph_objects as go

def update_chart_layout(fig, title=None):
    """
    Configuración universal para todos los gráficos en la app.
    Se aplica automáticamente sin necesidad de cambios en testeo.py
    """
    
    # ===== PALETA DE COLORES PARA ALTO CONTRASTE =====
    COLORS = {
        # Títulos y textos principales
        'title': '#1e3a8a',           # Azul oscuro - máximo contraste con blanco
        'axis': '#4b5563',            # Gris oscuro para ejes
        'text': '#374151',            # Gris para texto general
        'grid': '#e5e7eb',            # Gris claro para líneas de grid
        'legend_title': '#1e40af',    # Azul para título de leyenda
        
        # Colores para series (mejorados para daltonismo)
        'series': [
            '#3b82f6',  # Azul
            '#ef4444',  # Rojo
            '#10b981',  # Verde
            '#f59e0b',  # Amarillo/naranja
            '#8b5cf6',  # Violeta
            '#ec4899',  # Rosa
            '#06b6d4',  # Cian
            '#84cc16',  # Lima
            '#f97316',  # Naranja
            '#6366f1',  # Índigo
        ],
        
        # Fondo
        'paper_bg': 'rgba(255,255,255,1)',      # Fondo blanco sólido
        'plot_bg': 'rgba(255,255,255,1)',       # Área de gráfico blanco
    }
    
    # ===== APLICAR COLORES A LAS SERIES =====
    # Asignar colores distintos a cada traza para mejor diferenciación
    if hasattr(fig, 'data') and fig.data:
        for i, trace in enumerate(fig.data):
            # Solo asignar color si no tiene uno ya definido
            if not hasattr(trace, 'marker') or (hasattr(trace.marker, 'color') and trace.marker.color is None):
                color_idx = i % len(COLORS['series'])
                # Para gráficos de barras
                if hasattr(trace, 'marker'):
                    trace.marker.color = COLORS['series'][color_idx]
                # Para gráficos de líneas
                if hasattr(trace, 'line'):
                    trace.line.color = COLORS['series'][color_idx]
    
    # ===== CONFIGURACIÓN DEL LAYOUT =====
    layout_updates = {
        # ===== TEXTO GENERAL =====
        'font': dict(
            family="Inter, Arial, sans-serif",
            color=COLORS['text'],
            size=12
        ),
        
        # ===== TÍTULO =====
        'title': dict(
            font=dict(
                family="Inter, Arial, sans-serif",
                size=18,
                color=COLORS['title'],  # AZUL OSCURO PARA BUEN CONTRASTE
                weight="bold"
            ),
            x=0.05,      # Alinear a la izquierda
            xanchor="left",
            y=0.95,      # Cerca del top
            pad=dict(t=10, b=20)  # Padding arriba y abajo
        ),
        
        # ===== FONDOS =====
        'paper_bgcolor': COLORS['paper_bg'],
        'plot_bgcolor': COLORS['plot_bg'],
        
        # ===== MÁRGENES =====
        'margin': dict(l=60, r=40, t=100, b=100),
        
        # ===== EJE X =====
        'xaxis': dict(
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor='#d1d5db',
            tickfont=dict(
                size=12,
                color=COLORS['axis']
            ),
            title_font=dict(
                size=14,
                color=COLORS['title'],  # Mismo azul que el título principal
                weight="bold"
            ),
            zeroline=False,
            automargin=True
        ),
        
        # ===== EJE Y =====
        'yaxis': dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=COLORS['grid'],
            showline=False,
            tickfont=dict(
                size=12,
                color=COLORS['axis']
            ),
            title_font=dict(
                size=14,
                color=COLORS['title'],  # Mismo azul que el título principal
                weight="bold"
            ),
            zeroline=False
        ),
        
        # ===== LEYENDA =====
        'legend': dict(
            orientation="h",
            yanchor="top",
            y=-0.2,  # Debajo del gráfico
            xanchor="center",
            x=0.5,
            font=dict(
                size=12,
                color=COLORS['text']
            ),
            title_font=dict(
                size=13,
                color=COLORS['legend_title'],
                weight="bold"
            ),
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#e5e7eb",
            borderwidth=1,
            itemwidth=30
        ),
        
        # ===== HOVER =====
        'hoverlabel': dict(
            font_size=12,
            font_family="Inter, Arial, sans-serif",
            bgcolor="white",
            bordercolor="#d1d5db"
        ),
        
        # ===== GENERAL =====
        'autosize': True,
        'separators': ",."
    }
    
    # Aplicar todas las actualizaciones al layout
    fig.update_layout(**layout_updates)
    
    # Si el gráfico tiene título, asegurar que use nuestros colores
    if title or (hasattr(fig.layout, 'title') and fig.layout.title.text):
        # Si se pasa un nuevo título, actualizarlo
        if title:
            fig.update_layout(
                title_text=f"<b>{title}</b>",
                title_font_color=COLORS['title']
            )
        # Si ya tenía título, asegurar que tenga nuestro color
        elif hasattr(fig.layout, 'title') and fig.layout.title.text:
            fig.update_layout(
                title_font_color=COLORS['title']
            )
    
    # ===== AJUSTES ESPECÍFICOS POR TIPO DE GRÁFICO =====
    if fig.data:
        # Para gráficos de barras
        if any(trace.type == 'bar' for trace in fig.data):
            fig.update_layout(
                bargap=0.15,
                bargroupgap=0.05
            )
            # Asegurar que las barras tengan colores visibles
            for trace in fig.data:
                if trace.type == 'bar':
                    if not hasattr(trace, 'marker') or not hasattr(trace.marker, 'color'):
                        trace.update(marker=dict(color=COLORS['series'][0]))
        
        # Para gráficos de líneas
        if any(trace.type == 'scatter' and hasattr(trace, 'mode') and 'lines' in trace.mode for trace in fig.data):
            for trace in fig.data:
                if trace.type == 'scatter' and hasattr(trace, 'mode') and 'lines' in trace.mode:
                    if not hasattr(trace, 'line') or not hasattr(trace.line, 'color'):
                        trace.update(line=dict(width=3, color=COLORS['series'][0]))
        
        # Para gráficos de torta
        if any(trace.type == 'pie' for trace in fig.data):
            # Asegurar que el texto de la torta sea visible
            fig.update_traces(
                textfont=dict(
                    color=COLORS['text'],
                    size=12,
                    family="Inter, Arial, sans-serif"
                ),
                marker=dict(line=dict(color='white', width=2))
            )
            fig.update_layout(
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="right",
                    x=1.2
                )
            )
        
        # Para gráficos de dispersión (scatter)
        if any(trace.type == 'scatter' and hasattr(trace, 'mode') and 'markers' in trace.mode for trace in fig.data):
            for trace in fig.data:
                if trace.type == 'scatter' and hasattr(trace, 'mode') and 'markers' in trace.mode:
                    if not hasattr(trace, 'marker') or not hasattr(trace.marker, 'color'):
                        trace.update(marker=dict(size=10, color=COLORS['series'][0]))
    
    return fig


# ===== FUNCIÓN PARA GRAFICOS DE ALTO CONTRASTE =====
def high_contrast_chart(fig, title=None):
    """
    Versión alternativa para gráficos que necesitan MÁXIMO contraste
    (Se aplica automáticamente según el tipo de gráfico)
    """
    # Primero aplicar el layout normal
    fig = update_chart_layout(fig, title)
    
    # Colores para máximo contraste
    HIGH_CONTRAST_COLORS = {
        'title': '#0f172a',           # Casi negro azulado
        'text': '#1e293b',            # Gris muy oscuro
        'axis': '#475569',            # Gris oscuro
        'series': [
            '#1d4ed8',  # Azul intenso
            '#dc2626',  # Rojo intenso
            '#059669',  # Verde intenso
            '#d97706',  # Naranja intenso
            '#7c3aed',  # Violeta intenso
        ]
    }
    
    # Aplicar colores de alto contraste
    fig.update_layout(
        title_font_color=HIGH_CONTRAST_COLORS['title'],
        font_color=HIGH_CONTRAST_COLORS['text'],
        xaxis_title_font_color=HIGH_CONTRAST_COLORS['title'],
        yaxis_title_font_color=HIGH_CONTRAST_COLORS['title'],
        xaxis_tickfont_color=HIGH_CONTRAST_COLORS['axis'],
        yaxis_tickfont_color=HIGH_CONTRAST_COLORS['axis']
    )
    
    # Aplicar colores de serie de alto contraste
    if fig.data:
        for i, trace in enumerate(fig.data):
            color_idx = i % len(HIGH_CONTRAST_COLORS['series'])
            if hasattr(trace, 'marker'):
                trace.marker.color = HIGH_CONTRAST_COLORS['series'][color_idx]
            if hasattr(trace, 'line'):
                trace.line.color = HIGH_CONTRAST_COLORS['series'][color_idx]
    
    return fig
