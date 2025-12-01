# charts.py

import plotly.io as pio

def update_chart_layout(fig):
    """
    Ajusta el estilo general de los gráficos Plotly.
    Compatible con todos los gráficos que usa la app.
    """
    fig.update_layout(
        template="plotly_white",
        hovermode="closest",
        margin=dict(l=30, r=30, t=60, b=30),
        legend=dict(title=None),
    )
    return fig
