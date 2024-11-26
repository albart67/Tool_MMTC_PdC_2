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
            "2\" 1/2 (DN 65)": 65,
            "3\" (DN 80)": 80
        }
    }
}

# Fonction pour calculer la viscosité cinématique de l'eau en fonction de la température
def calcul_viscosite_cinematique_eau(temp):
    viscosite_dynamique = (2.414e-5) * 10**(247.8 / (temp + 273.15 - 140))  # Pa·s
    densite_eau = 1000  # kg/m³
    viscosite_cinematique = viscosite_dynamique / densite_eau  # m²/s
    return viscosite_cinematique

# Fonction de Colebrook pour calculer le facteur de friction
def colebrook(Re, e, D):
    def equation(f):
        return -2 * math.log10((e / (3.7 * D)) + (2.51 / (Re * math.sqrt(f)))) - 1 / math.sqrt(f)
    f_initial_guess = 0.02
    f_solution = fsolve(equation, f_initial_guess)[0]
    return f_solution

# Fonction pour calculer la perte de charge par mètre
def perte_charge_par_metre(f, rho, v, D):
    return f * (rho * v**2) / (2 * D)

# Fonction pour calculer la vitesse en fonction du débit
def calculer_vitesse(debit, D):
    section = math.pi * (D / 2)**2
    return debit / section

# Fonction principale
def main():
    st.title("Longueur maximale des conduites pour PAC MMTC et MHTC")
    
    # Sélection de la température
    st.markdown("<p style='font-size:20px;'><strong>Sélectionnez la température de l'eau (°C):</strong></p>", unsafe_allow_html=True)
    temperature = st.slider("Température de l'eau", 10, 80, 20)
    nu = calcul_viscosite_cinematique_eau(temperature)
    st.write(f"La viscosité cinématique de l'eau à {temperature} °C est de {nu:.8f} m²/s")

    # Sélection du matériau et du diamètre
    materiau = st.selectbox("Choisissez un matériau de conduit", list(tubes_data.keys()))
    rugosite = tubes_data[materiau]["rugosites"]
    diamètre = st.selectbox("Choisissez la taille du tube", list(tubes_data[materiau]["D"].keys()))
    D = tubes_data[materiau]["D"][diamètre] / 1000
    st.write(f"Diamètre intérieur : {D*1000:.1f} mm")
    st.write(f"Rugosité : {rugosite} mm")

    # Saisie du débit
    debit = st.number_input("Entrez le débit (m³/h):", min_value=0.0, value=1.0)
    debit_m3_s = debit / 3600
    v = calculer_vitesse(debit_m3_s, D)
    st.write(f"Vitesse d'écoulement : {v:.2f} m/s")

    # Calcul du nombre de Reynolds
    Re = (v * D) / nu
    st.write(f"Nombre de Reynolds : {Re:.0f}")

    # Calcul du facteur de friction avec Colebrook
    if Re > 2000:
        f = colebrook(Re, rugosite / 1000, D)
        st.write(f"Facteur de friction (f) : {f:.4f}")

        # Calcul des pertes de charge
        rho = 1000  # Masse volumique de l'eau en kg/m³
        pertes_par_metre = perte_charge_par_metre(f, rho, v, D)
        st.write(f"Perte de charge par mètre : {pertes_par_metre:.2f} Pa/m")
        
        # Longueur maximale calculée
        pression_disponible = st.number_input("Entrez la pression disponible (Pa):", min_value=0.0, value=50000.0)
        longueur_max = pression_disponible / pertes_par_metre
        st.write(f"Longueur maximale : {longueur_max:.2f} m")
    else:
        st.write("L'écoulement est laminaire. Le calcul basé sur Colebrook n'est pas applicable.")

if __name__ == "__main__":
    main()
