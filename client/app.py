import streamlit as st
import requests
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import plotly.express as px
from folium.plugins import MarkerCluster
import pandas as pd

api_url = "http://localhost:8502"
st.set_page_config(page_title="IGRM en France",page_icon=":fr")

st.markdown(
        """
        L'Indicateur Mensuel Gaz Renouvelable des territoires par département, abrégé en IGRM-dep.\n
        Ce jeu de données offre des informations cruciales concernant la production et la consommation de gaz renouvelable au niveau départemental en France.
        Cet indicateur se renouvelle chaque mois, apportant un éclairage essentiel sur la transition vers une énergie plus propre et durable à travers les départements français.
        """
    )

st.markdown("""
Ces données couvrent la période allant de l'année 2020 jusqu'à la dernière mise à jour en septembre 2023. Les principaux éléments inclus sont les suivants :
""")
st.write('Nom Officiel du Département : Le nom du département français.')
st.write('Code Officiel du Département : Le code officiel correspondant à chaque département.')
st.write('Année : L\'année à laquelle les données se rapportent.')
st.write('''Production Locale de Gaz Renouvelable : La quantité de gaz renouvelable produite localement en mètres cubes (m³) par mois et par département.''')
st.write('''Consommation Locale de Gaz : La consommation de gaz en mètres cubes (m³) par mois et par département.''')
def fetch_data(endpoint, params=None):
    try:
        response = requests.get(f"{api_url}/{endpoint}", params=params)
        response.raise_for_status()
        data = response.json()
        return gpd.GeoDataFrame(data)
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération des données depuis l'API : {e}")
        return None

all_data = fetch_data("api/data")

if all_data is not None:
    st.title("Application Open Data Environnement")
    st.subheader("Données environnementales")
    page_number = st.number_input("Page", min_value=1, value=1)
    page_size = st.number_input("Taille de la page", min_value=1, value=10)
    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size
    st.write(all_data.iloc[start_idx:end_idx])

filtered_data = fetch_data("api/data/filter", params=None)

st.subheader("Graphique modulable")
x_axis = st.selectbox("Axe X", all_data.columns,index=1)
y_axis = st.selectbox("Axe Y", all_data.columns,index=3)
if filtered_data is not None:
    fig = px.scatter(filtered_data, x=x_axis, y=y_axis)
    st.plotly_chart(fig)

st.title("Graphique de la moyenne de l'IGRM par date pour tous les départements")

fig = px.line(all_data, x='date', y='igrm', color='nom_officiel_departement', title="Moyenne IGRM par date")

fig.update_layout(xaxis_title='Date', yaxis_title='Moyenne IGRM (%)')

st.plotly_chart(fig)

#######################
# Carte OpenStreetMap #
#######################
st.title("Carte OpenStreetMap")

m = folium.Map(location=[48.8588443, 2.2943506], zoom_start=5)  # Centre sur Paris

# centrée sur Paris
m = folium.Map(location=[48.8588443, 2.2943506], zoom_start=5)

# Couleurs pour légende
bins = [0.0, 7.5, 16.0, 30.0, 40.0, 100.0, float('inf')]
colors = [
    'rgb(187, 209, 184)',
    'rgb(140, 185, 169)',
    'rgb(93, 162, 154)',
    'rgb(46, 138, 139)',
    'rgb(0, 115, 124)',
    'rgb(89, 23, 135)',
    'white'
]
legend_labels = [
    '0,0 -> 7,5',
    '7,6 -> 16,0',
    '17,0 -> 30,0',
    '31,0 -> 40,0',
    '41,0 -> 100,0',
    'IGRm (%) indéfinis',
    'IGRm (%) en dehors des bornes'
]

# légende custom (avec carrés)
legend_html = """
     <div style="position: fixed; 
     bottom: 10px; left: 10px; width: 300px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color: white;
     ">&nbsp; <b>Indicateur mensuel Gaz Renouvelable des territoires</b><br>
     &nbsp; IGRm (%)<br>
     &nbsp; <i style="background:{}; width:20px; height:20px; display:inline-block;"></i> {}<br>
     &nbsp; <i style="background:{}; width:20px; height:20px; display:inline-block;"></i> {}<br>
     &nbsp; <i style="background:{}; width:20px; height:20px; display:inline-block;"></i> {}<br>
     &nbsp; <i style="background:{}; width:20px; height:20px; display:inline-block;"></i> {}<br>
     &nbsp; <i style="background:{}; width:20px; height:20px; display:inline-block;"></i> {}<br>
     &nbsp; <i style="background:{}; width:20px; height:20px; display:inline-block;"></i> {}<br>
     &nbsp; <i style="background:{}; width:20px; height:20px; display:inline-block;"></i> {}<br>
     </div>
     """.format(
        colors[0], legend_labels[0],
        colors[1], legend_labels[1],
        colors[2], legend_labels[2],
        colors[3], legend_labels[3],
        colors[4], legend_labels[4],
        colors[5], legend_labels[5],
        colors[6], legend_labels[6]
     )
m.get_root().html.add_child(folium.Element(legend_html))

# parcourt les données + ajoute les polygones à la carte (avec infobulle)
for index, row in all_data.iterrows():
    if "geom" in row and "centroid" in row:
        geom = row["geom"]
        centroid = row["centroid"]
        nom = row["nom_officiel_departement"]
        code_departement = row["code_officiel_departement"]
        date = row["date"]
        igrm = row["igrm"]

        # couleur en fonction de l'IGRm
        color = None
        for i in range(len(bins) - 1):
            if bins[i] <= igrm <= bins[i + 1]:
                color = colors[i]
                break

        # polygone pour chaque département avec la couleur correspondante
        if color:
            folium.GeoJson(
                geom,
                name=nom,
                style_function=lambda x, color=color: {
                    'fillColor': color,
                    'color': 'black',  # Couleur de la bordure
                    'weight': 1,  # Épaisseur de la bordure
                    'dashArray': '5, 5'  # Tirets pointillés
                },
                tooltip=nom + f", IGRM: {igrm}, Longitude: {centroid['lon']}, Latitude: {centroid['lat']}",
                popup=f"Date: {date}<br>Nom Officiel Département: {nom}<br>Code Officiel Département: {code_departement}<br>IGRm (%): {igrm}"
            ).add_to(m)

st.markdown(legend_html, unsafe_allow_html=True)
st.write("Carte OpenStreetMap avec légende:")
folium_static(m)