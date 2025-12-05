import plotly.graph_objects as go

def update_chart_layout(fig, title=None):
    # Configuración de colores para ALTO CONTRASTE
    TITLE_COLOR = "#1e3a8a"        # Azul oscuro profesional
    AXIS_COLOR = "#4b5563"         # Gris oscuro para ejes
    TEXT_COLOR = "#374151"         # Gris para texto general
    GRID_COLOR = "#e5e7eb"         # Gris claro para grid
    LEGEND_TITLE_COLOR = "#1e40af" # Azul para título de leyenda
    
    fig.update_layout(
        # ===== COLORES DE TEXTO =====
        font=dict(
            family="Inter, Arial, sans-serif",
            color=TEXT_COLOR,  # Color base para TODO el texto
            size=12
        ),
        
        # ===== TÍTULO =====
        title=dict(
            font=dict(
                family="Inter, Arial, sans-serif",
                size=18,
                color=TITLE_COLOR,  # Azul oscuro para máximo contraste
                weight="bold"
            ),
            x=0.05,  # Alinear a la izquierda
            xanchor="left",
            y=0.95   # Más cerca del top
        ),
        
        # ===== FONDOS =====
        paper_bgcolor="rgba(255,255,255,1)",  # Fondo blanco sólido
        plot_bgcolor="rgba(255,255,255,1)",   # Fondo blanco sólido
        
        # ===== MÁRGENES =====
        margin=dict(l=50, r=50, t=80, b=100),  # Más espacio para títulos
        
        # ===== EJE X =====
        xaxis=dict(
            showgrid=False,
            showline=True,
            linewidth=2,
            linecolor="#d1d5db",  # Gris para línea del eje
            tickfont=dict(
                size=12,
                color=AXIS_COLOR  # Gris oscuro para números
            ),
            title_font=dict(
                size=14,
                color=TITLE_COLOR,  # Azul oscuro como título
                weight="bold"
            ),
            zeroline=False,
            automargin=True  # Auto-ajustar márgenes
        ),
        
        # ===== EJE Y =====
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor=GRID_COLOR,  # Gris claro para grid
            showline=False,
            tickfont=dict(
                size=12,
                color=AXIS_COLOR   # Gris oscuro para números
            ),
            title_font=dict(
                size=14,
                color=TITLE_COLOR,  # Azul oscuro como título
                weight="bold"
            ),
            zeroline=False
        ),
        
        # ===== LEYENDA =====
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,  # Justo arriba del gráfico
            xanchor="center",
            x=0.5,
            font=dict(
                size=12,
                color=TEXT_COLOR
            ),
            title_font=dict(
                size=13,
                color=LEGEND_TITLE_COLOR,  # Azul para título de leyenda
                weight="bold"
            ),
            bgcolor="rgba(255,255,255,0.9)",  # Fondo semi-transparente
            bordercolor="#e5e7eb",
            borderwidth=1
        ),
        
        # ===== HOVER =====
        hoverlabel=dict(
            font_size=12,
            font_family="Inter, Arial, sans-serif",
            bgcolor="white",
            bordercolor="#d1d5db"
        ),
        
        # ===== GENERAL =====
        autosize=True,
        separators=",."
    )
    
    # Si se pasa título personalizado, actualizarlo
    if title:
        fig.update_layout(
            title_text=f"<b>{title}</b>",  # Negrita para más énfasis
            title_x=0.05  # Alinear a la izquierda
        )
    
    # ===== AJUSTES ESPECÍFICOS POR TIPO DE GRÁFICO =====
    if fig.data:
        # Para gráficos de barras, mejorar contraste
        if any(trace.type == 'bar' for trace in fig.data):
            fig.update_layout(
                bargap=0.15,  # Espacio entre barras
                bargroupgap=0.1
            )
            
        # Para gráficos de línea, hacer líneas más gruesas
        if any(trace.type == 'scatter' and trace.mode == 'lines' for trace in fig.data):
            for trace in fig.data:
                if trace.type == 'scatter' and trace.mode == 'lines':
                    trace.update(line=dict(width=3))
    
    return fig


# ===== FUNCIÓN ADICIONAL PARA TÍTULOS DE ALTO CONTRASTE =====
def set_high_contrast_title(fig, title_text):
    """
    Configura un título con máximo contraste (fondo oscuro, texto claro)
    """
    # Añadir anotación como título con fondo
    fig.add_annotation(
        text=f"<b>{title_text}</b>",
        xref="paper",
        yref="paper",
        x=0.05,
        y=1.05,
        showarrow=False,
        font=dict(
            size=20,
            color="white",
            family="Inter, Arial, sans-serif",
            weight="bold"
        ),
        align="left",
        bgcolor="#1e3a8a",  # Azul oscuro de fondo
        bordercolor="#1e40af",
        borderwidth=2,
        borderpad=10,
        width=None  # Auto-ancho
    )
    
    # También actualizar título normal (como respaldo)
    fig.update_layout(
        title_text=f"<b>{title_text}</b>",
        title_font=dict(
            size=20,
            color="#1e3a8a",
            family="Inter, Arial, sans-serif",
            weight="bold"
        ),
        title_x=0.05,
        title_y=0.95
    )
    
    return fig


# ===== FUNCIÓN PARA GRAFICOS EN TARJETAS =====
def card_chart_layout(fig, title=None):
    """
    Layout especial para gráficos dentro de tarjetas
    """
    fig = update_chart_layout(fig, title)
    
    # Ajustes extra para tarjetas
    fig.update_layout(
        margin=dict(l=40, r=40, t=60, b=80),
        paper_bgcolor="rgba(248,250,252,0.8)",  # Azul muy claro sutil
        plot_bgcolor="rgba(255,255,255,1)",
        xaxis=dict(
            title_font=dict(color="#1e40af")  # Azul más vibrante
        ),
        yaxis=dict(
            title_font=dict(color="#1e40af")
        )
    )
    
    return fig
