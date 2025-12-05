def update_chart_layout(fig, title=None):
    fig.update_layout(
        template="plotly_white", # Use Light Theme
        font_family="Inter",
        title_font_family="Inter",
        title_font_size=18,
        title_font_color="#0E1117", # Black for light theme
        paper_bgcolor="rgba(0,0,0,0)", # Transparent to blend with card
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=150, t=50, b=150), # Right margin for legend
        xaxis=dict(
            showgrid=False,
            showline=True,
            linecolor="#D6D6D9", # Light grey line
            tickfont=dict(color="#262730"),
            title_font=dict(color="#262730"),
            tickangle=-45,
            automargin=True,
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor="#E6E6EA", # Very light grey grid
            showline=False,
            tickfont=dict(color="#262730"),
            title_font=dict(color="#262730"),
        ),
        legend=dict(
            orientation="v", # Vertical legend
            yanchor="top",
            y=1, 
            xanchor="left",
            x=1.02, # Move to right side
            font=dict(size=12, color="#262730"),
            title_font=dict(size=12, color="#262730"),
            bgcolor="rgba(255,255,255,0.5)" # Semi-transparent white
        ),
        # Add Polar config for Radar Charts
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(
                showgrid=True,
                gridcolor="#B0B0B0", # Visible grid (the "structure")
                gridwidth=1,
                linecolor="#B0B0B0", # Axis lines
                showline=True,
                tickfont=dict(color="#262730"),
            ),
            angularaxis=dict(
                showgrid=True,
                gridcolor="#B0B0B0", # Visible rings
                gridwidth=1,
                linecolor="#B0B0B0",
                tickfont=dict(color="#262730"),
            )
        )
    )
    if title:
        fig.update_layout(title_text=title)
    return fig
