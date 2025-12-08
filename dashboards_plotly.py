import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# CONFIG STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Dashboard Netflix — Streamlit",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Dashboard Netflix — Streamlit & Plotly")
st.write("Selecciona un gráfico del catálogo de Netflix para visualizarlo y leer su descripción abajo.")

# ==========================================
# CARGA DEL DATASET
# ==========================================
@st.cache_data
def load_data():
    df = pd.read_csv("netflix_titles.csv")

    df['release_year'] = df['release_year'].astype(int)
    df['main_country'] = df['country'].fillna('Unknown').str.split(',').str[0].str.strip()
    df['type'] = df['type'].astype(str)

    df['duration'] = df['duration'].astype(str)
    df['duration_value'] = df['duration'].str.extract(r'(\d+)').astype(float)
    df['duration_unit'] = df['duration'].str.extract(r'(\D+)$').astype(str).apply(lambda x: x.str.strip())

    df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
    df['added_month'] = df['date_added'].dt.month

    return df

df = load_data()

# ==========================================
# PALETAS NETFLIX
# ==========================================
netflix_mono = ["#8A0008", "#B20710", "#E50914", "#FF4A55", "#FF7A82", "#FFB4B7"]
netflix_complementary = ["#E50914", "#09E5DA", "#079C94", "#73FFF6"]
netflix_triadic = ["#E50914", "#1409E5", "#09E514"]
netflix_tetrad = ["#E50914", "#09E5DA", "#E5DA09", "#5A09E5"]

netflix_continuous_red = [
    (0.0, "#221F1F"),
    (0.5, "#E50914"),
    (1.0, "#FFB4B7"),
]

netflix_continuous_map = [
    (0.0, "#221F1F"),
    (0.5, "#E50914"),
    (1.0, "#FFE5E7"),
]

base_layout = dict(
    template='plotly_dark',
    paper_bgcolor='#000000',
    plot_bgcolor='#000000',
    font=dict(color='#FFFFFF'),
)

# ==========================================
# FUNCIÓN QUE GENERA LAS 10 GRÁFICAS
# ==========================================
def generate_graph(fig_id):

    # ======================================================
    # FIG 1 — Conteo de películas vs series
    # ======================================================
    if fig_id == "fig1":
        data = df['type'].value_counts().reset_index()
        data.columns = ['type', 'count']

        fig = px.bar(
            data,
            x='type',
            y='count',
            color='type',
            text='count',
            color_discrete_sequence=netflix_mono
        )
        fig.update_layout(**base_layout)
        title = "Gráfico 1 — Conteo de Películas vs Series"
        desc = "Cuenta cuántas películas y series tiene Netflix."

        return fig, title, desc

    # ======================================================
    # FIG 2 — Títulos por año
    # ======================================================
    elif fig_id == "fig2":
        d = df.groupby('release_year').size().reset_index(name='count')

        fig = px.line(d, x='release_year', y='count', markers=True)
        fig.update_traces(line=dict(color="#E50914", width=3))
        fig.update_layout(**base_layout)

        return fig, "Gráfico 2 — Títulos lanzados por año", \
               "Muestra cuántos títulos se lanzaron cada año."

    # ======================================================
    # FIG 3 — Top 10 países con más títulos
    # ======================================================
    elif fig_id == "fig3":
        d = df['main_country'].value_counts().head(10).reset_index()
        d.columns = ['country', 'count']

        fig = px.bar(
            d,
            x='count',
            y='country',
            color='country',
            orientation='h',
            color_discrete_sequence=netflix_complementary
        )
        fig.update_layout(**base_layout)

        return fig, "Gráfico 3 — Top 10 países con más títulos", \
               "Los países que más contenido aportan a Netflix."

    # ======================================================
    # FIG 4 — Distribución de clasificaciones (Rating)
    # ======================================================
    elif fig_id == "fig4":
        ratings = df['rating'].fillna('Unknown').value_counts().reset_index()
        ratings.columns = ['rating', 'count']

        fig = px.bar(
            ratings,
            x='rating',
            y='count',
            color='rating',
            color_discrete_sequence=netflix_triadic + netflix_mono
        )
        fig.update_layout(**base_layout)

        return fig, "Gráfico 4 — Distribución de clasificaciones", \
               "Clasificaciones de edad más comunes en Netflix."

    # ======================================================
    # FIG 5 — Treemap géneros
    # ======================================================
    elif fig_id == "fig5":
        g = df.assign(genre=df['listed_in'].str.split(', ')).explode('genre')
        c = g['genre'].value_counts().reset_index()
        c.columns = ['genre', 'count']

        fig = px.treemap(
            c,
            path=['genre'],
            values='count',
            color='count',
            color_continuous_scale=netflix_continuous_red
        )
        fig.update_layout(**base_layout)

        return fig, "Gráfico 5 — Treemap de géneros", \
               "Géneros más populares en Netflix."

    # ======================================================
    # FIG 6 — Boxplot duración películas
    # ======================================================
    elif fig_id == "fig6":
        movies = df[(df['type'] == 'Movie') & (df['duration_value'].notnull())]

        fig = px.box(movies, y='duration_value', points="all")
        fig.update_layout(**base_layout)

        return fig, "Gráfico 6 — Duración de películas", \
               "Distribución de duración de películas."

    # ======================================================
    # FIG 7 — Duración promedio por década
    # ======================================================
    elif fig_id == "fig7":
        m = df[df['type'] == 'Movie'].copy()
        m = m[m['duration_value'].notnull()]
        m['decade'] = (m['release_year'] // 10) * 10

        d = m.groupby('decade')['duration_value'].mean().reset_index()

        fig = px.bar(
            d,
            x='decade',
            y='duration_value',
            text='duration_value',
            color='decade',
            color_continuous_scale=netflix_continuous_red
        )
        fig.update_layout(**base_layout)

        return fig, "Gráfico 7 — Duración promedio por década", \
               "Cómo ha cambiado la duración promedio del contenido."

    # ======================================================
    # FIG 8 — Mapa mundial de títulos por país
    # ======================================================
    elif fig_id == "fig8":
        c = df['main_country'].value_counts().reset_index()
        c.columns = ['country', 'count']

        fig = px.choropleth(
            c,
            locations='country',
            locationmode='country names',
            color='count',
            color_continuous_scale=netflix_continuous_map
        )
        fig.update_layout(**base_layout)

        return fig, "Gráfico 8 — Mapa mundial de títulos", \
               "Cantidad de títulos por país."

    # ======================================================
    # FIG 9 — Títulos añadidos por mes
    # ======================================================
    elif fig_id == "fig9":
        c = df.groupby('added_month').size().reset_index(name='count')

        fig = px.bar(
            c,
            x='added_month',
            y='count',
            color='added_month',
            color_continuous_scale=netflix_continuous_red
        )
        fig.update_layout(**base_layout)

        return fig, "Gráfico 9 — Títulos añadidos por mes", \
               "Meses con más contenido agregado en Netflix."

    # ======================================================
    # FIG 10 — Duración promedio por clasificación y tipo
    # ======================================================
    elif fig_id == "fig10":
        d = df[df['duration_value'].notnull()].groupby(['rating', 'type'])['duration_value'].mean().reset_index()

        fig = px.treemap(
            d,
            path=['rating', 'type'],
            values='duration_value',
            color='duration_value',
            color_continuous_scale=netflix_continuous_red
        )
        fig.update_layout(**base_layout)

        return fig, "Gráfico 10 — Duración por clasificación y tipo", \
               "Duración promedio de cada clasificación."

# ==========================================
# STREAMLIT UI
# ==========================================
option = st.selectbox(
    "Selecciona un gráfico:",
    [
        ("1) Películas vs Series", "fig1"),
        ("2) Títulos por año", "fig2"),
        ("3) Top países", "fig3"),
        ("4) Ratings", "fig4"),
        ("5) Géneros", "fig5"),
        ("6) Duración Películas", "fig6"),
        ("7) Duración por década", "fig7"),
        ("8) Mapa mundial", "fig8"),
        ("9) Añadidos por mes", "fig9"),
        ("10) Duración por clasificación y tipo", "fig10"),
    ],
    format_func=lambda x: x[0]
)

fig_id = option[1]

fig, title, desc = generate_graph(fig_id)

st.subheader(title)
st.plotly_chart(fig, use_container_width=True)

st.markdown("### Descripción")
st.markdown(desc)
