import folium
import pandas as pd
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import streamlit as st
import xata
from st_xatadb_connection import XataConnection
from geopy.geocoders import Nominatim

# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)

if "latq" in st.query_params:
    local_lat = st.query_params["latq"]
else:
    st.write("Faltou query params"),
    st.stop()

if "lonq" in st.query_params:
    local_long = st.query_params["lonq"]
else:
    st.write("Faltou query params"),
    st.stop()

#   dados de conexão ao banco de dados
colunas = 'SELECT "ANO_ESTATISTICA", "MES_ESTATISTICA", "NUM_BO", "DATA_OCORRENCIA_BO", "HORA_OCORRENCIA_BO", "DESC_PERIODO",\
        "NOME_DEPARTAMENTO_CIRCUNSCRIÇÃO", "NOME_SECCIONAL_CIRCUNSCRIÇÃO", "NOME_DELEGACIA_CIRCUNSCRIÇÃO", \
        "NOME_MUNICIPIO_CIRCUNSCRIÇÃO", "BAIRRO", "LOGRADOURO", "NUMERO_LOGRADOURO","LATITUDE","LONGITUDE",\
        "DESCR_TIPOLOCAL", "RUBRICA", "NATUREZA_APURADA"'

# =============================================================================================
# conversão para pwa
HIDE_ST_STYLE = """
                <style>
                div[data-testid="stToolbar"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stDecoration"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                div[data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
                }
                #MainMenu {
                visibility: hidden;
                height: 0%;
                }
                header {
                visibility: hidden;
                height: 0%;
                }
                footer {
                visibility: hidden;
                height: 0%;
                }
                .block-container {
                padding-top: 0rem;
                }
                </style>
                """
def init_style():
    st.set_page_config(
        page_title="GeoCrimes PWA",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="auto",
        menu_items=None,
    )
    st.markdown(HIDE_ST_STYLE,unsafe_allow_html=True)



#@st.cache_data
def dados():
    xata = st.connection('xata',type=XataConnection)

    xquery = colunas + f' FROM "SSPDados" where (6371 * acos(cos(radians({local_lat})) * cos(radians("LATITUDE")) * \
            cos(radians({local_long}) - radians("LONGITUDE")) + sin(radians({local_lat})) * sin(radians("LATITUDE")) )) <= 0.5 LIMIT 1000'

    sql_response = xata.sql_query(xquery)
    nx = pd.json_normalize(sql_response['records'])
    return nx

# =======================================================
# geração do mapa de cluster da seleção especifica
def main():
    nx = dados()
    mapa(nx)
    return None

def mapa(nx):

    #st.header('Densidade do Entorno ', divider=False)

    density_map = folium.Map(location=[nx[['LATITUDE']].mean(),
                                        nx[['LONGITUDE']].mean()],
                                        zoom_start=14, control_scale=True)

    marker_cluster = MarkerCluster().add_to(density_map)

    folium.Marker(
        location=[local_lat, local_long],
        tooltip="Onde estou!",
        popup="Local base",
        icon=folium.Icon(color="green"),
    ).add_to(marker_cluster)

    for name, row in nx.iterrows():
        if row['HORA_OCORRENCIA_BO']:
            xhora = ' ' + row['HORA_OCORRENCIA_BO'][11:16]
        else:
            xhora = ' ' + row['DESC_PERIODO']

        folium.Marker([row['LATITUDE'], row['LONGITUDE']], tooltip=row['RUBRICA'],
                      popup=folium.Popup("<h3>Fatos :</h3> <ul> <li>{0}</li> <li>{1}</li> <li>{2}{3}</li> <li>{4}{5}</li> "
                                         "<li>{6}</li></ul>".format(row['RUBRICA'],
                            row['NATUREZA_APURADA'], row['DATA_OCORRENCIA_BO'][:10], xhora,
                            row['LOGRADOURO'] + ' ', row['NUMERO_LOGRADOURO'],'<a href="https://www.google.com/maps?layer=c&cbll=' + str(row['LATITUDE']) + ',' + str(row['LONGITUDE']) + '" target="blank">GOOGLE STREET VIEW</a>'
                                                                    ), parse_html=False, max_width=120)).add_to(marker_cluster)
                                                     # row['NOME_MUNICIPIO_CIRCUNSCRIÇÃO'],
                                                     # row['NOME_SECCIONAL_CIRCUNSCRIÇÃO'])).add_to(marker_cluster)

    #folium_static(density_map, height=700)

    #st.header("EV Charging Stations in the Vancouver", divider=True)
    st.components.v1.html(folium.Figure().add_child(density_map).render(), width=400 , height=600)

    return None


# ===================================================
# This is the main app app itself, which appears when the user selects "Run the app"..
if __name__ == '__main__':
    init_style()
    main()

