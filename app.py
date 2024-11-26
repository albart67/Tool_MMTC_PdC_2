import streamlit as st
import math
from scipy.optimize import fsolve

# Données du tableau avec rugosité ajoutée
tubes_data = {
    "Acier": {
        "rugosites": 0.05,
        "D": {
            "1\" 1/4 (DN 32)": 35.9,
            "1\" 1/2 (DN 40)": 41.8,
            "2\" (DN 50)": 53,
            "2\" 1/2 (DN 65)": 68.8,
            "3\" (DN 80)": 80.8
        }
    },
    "Multicouches": {
        "rugosites": 0.002,
        "D": {
            "1\" 1/4 (DN 32)": 33,
            "1\" 1/2 (DN 40)": 41,
            "2\" (DN 50)": 51,
            "2\" 1/2 (DN 65)": 58,
            "3\" (DN 80)": 70
        }
    },
    "Cuivre": {
        "rugosites": 0.01,
        "D": {
            "1\" 1/4 (DN 32)": 33,
            "1\" 1/2 (DN 40)": 40,
            "2\" (DN 50)": 50,
            "2\" 1/2 (DN 65)":65,
            "3\" (DN 80)": 80
        }
    }
}

# Fonction pour calculer la viscosité cinématique de l'eau en fonction de la température
def calcul_viscosite_cinematique_eau(temp):
    # Equation empirique pour la viscosité dynamique en m²/s
    viscosite_dynamique = (2.414e-5) * 10**(247.8 / (temp + 273.15 - 140))  # Pa·s
    densite_eau = 1000  # kg/m³
    viscosite_cinematique = viscosite_dynamique / densite_eau  # m²/s
    return viscosite_cinematique

# Autres fonctions inchangées ici (colebrook, perte_charge_par_metre, calculer_vitesse)...

def main():
    st.title("Longueur maximale des conduites pour PAC MMTC et MHTC")
    
    # Barre de sélection de température
    st.markdown("<p style='font-size:20px;'><strong>Sélectionnez la température de l'eau (°C):</strong></p>", unsafe_allow_html=True)
    temperature = st.slider("Température de l'eau", 10, 80, 20)  # Valeur par défaut : 20 °C

    # Calcul de la viscosité cinématique en fonction de la température
    nu = calcul_viscosite_cinematique_eau(temperature)
    st.write(f"La viscosité cinématique de l'eau à {temperature} °C est de {nu:.8f} m²/s")

    # Reste du code de sélection du modèle, matériau, calcul des pertes, etc.
    # Par exemple :
    st.markdown('<p style="font-size:20px; margin-top: 20px;"><strong>Choisissez un modèle de PAC:</strong></p>', unsafe_allow_html=True)
    modèle = st.selectbox("", list(tubes_data.keys()))

    # Exemple de récupération de données et calcul
    materiau = st.selectbox("Choisissez un matériau de conduit", list(tubes_data.keys()))
    diamètre = st.selectbox("Choisissez la taille du tube", list(tubes_data[materiau]["D"].keys()))
    D = tubes_data[materiau]["D"][diamètre] / 1000
    st.write(f"Diamètre intérieur : {D*1000:.1f} mm")

    # Utilisation de la viscosité cinématique dans les calculs
    # Exemple : Nombre de Reynolds
    v = 1.2  # Exemple de vitesse arbitraire
    Re = (v * D) / nu
    st.write(f"Nombre de Reynolds : {Re:.0f}")

    # Continuez avec les calculs et affichages restants...

if __name__ == "__main__":
    main()
