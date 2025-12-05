def update_chart_layout(fig, title=None):
    fig.update_layout(
        template=None, # Force Streamlit theme inheritance
        font_family="Inter",
        title_font_family="Inter",
        title_font_size=18,
        # title_font_color removed to adapt to theme
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=50, b=200),
        xaxis=dict(
            showgrid=False,
            showline=True,
            # linecolor removed
            # tickfont removed
            # title_font removed
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            showline=False,
            # gridcolor removed
            # tickfont removed
            # title_font removed
        ),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.6,
            xanchor="center",
            x=0.5,
            font=dict(size=12),
            title_font=dict(size=12),
        )
    )
    if title:
        fig.update_layout(title_text=title)
    return fig
 
 
