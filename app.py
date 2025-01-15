import streamlit as st
import math
from scipy.optimize import fsolve
import numpy as np
import pandas as pd
import plotly.express as px

# Données du tableau avec rugosité ajoutée
tubes_data = {
    "Acier": {
        "rugosites": 0.05,
        "D": {
            "1\" 1/4 (DN 32)": 35.9,
            "1\" 1/2 (DN 40)": 41.8,
            "2\" (DN 50)": 53.1,
            "2\" 1/2 (DN 65)": 68.1,
            "3\" (DN 80)": 80.8,
            "3\" 1/2 (DN90)": 93.6,
            "4\" (DN100)": 105.3,
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





# Données de perte de charge statique pour chaque modèle MMTC
pertes_charge_statique = {
    'MMTC 20': 1.63,
    'MMTC 26': 2.04,
    'MMTC 33': 2.08,
    'MMTC 40': 1.17,
    'MHTC 20': 1.45,
    'MHTC 30': 2.55,
    '2 x MMTC 20': 1.63,
    '2 x MMTC 26': 2.04,
    '2 x MMTC 33': 2.08,
    '2 x MMTC 40': 1.17,
    '2 x MHTC 20': 1.45,
    '2 x MHTC 30': 2.55,
    '3 x MMTC 20': 1.63,
    '3 x MMTC 26': 2.04,
    '3 x MMTC 33': 2.08,
    '3 x MMTC 40': 1.17,
    '3 x MHTC 20': 1.45,
    '3 x MHTC 30': 2.55,
    '4 x MMTC 20': 1.63,
    '4 x MMTC 26': 2.04,
    '4 x MMTC 33': 2.08,
    '4 x MMTC 40': 1.17,
    '4 x MHTC 20': 1.45,
    '4 x MHTC 30': 2.55,
    '5 x MMTC 20': 1.63,
    '5 x MMTC 26': 2.04,
    '5 x MMTC 33': 2.08,
    '5 x MMTC 40': 1.17,
    '5 x MHTC 20': 1.45,
    '5 x MHTC 30': 2.55,
    '6 x MMTC 20': 1.63,
    '6 x MMTC 26': 2.04,
    '6 x MMTC 33': 2.08,
    '6 x MMTC 40': 1.17,
    '6 x MHTC 20': 1.45,
    '6 x MHTC 30': 2.55,

}



# --- Données des ballons ---
ballons = {
    "B650-B800": {"debit": 4.6, "pdc": 1.6},
    "B1000": {"debit": 5.1, "pdc": 2.0},
    "B1500-B3000": {"debit": 5.1, "pdc": 2.0}
}


# # Fonction pour calculer la viscosité cinématique de l'eau en fonction de la température
# def viscosite_cinematique_eau(temperature):
#     # Approximation pour l'eau en fonction de la température (valeurs en m²/s)
#     if temperature < 10:
#         temperature = 10
#     if temperature > 80:
#         temperature = 80
#     return 1.787e-6 * (10 / temperature)**1.5  # Formule simplifiée pour l'eau


# Fonction Colebrook-White
def colebrook(f, epsilon, D, Re):
    return 1 / math.sqrt(f) + 2 * math.log10(epsilon / (3.7 * D) + 2.51 / (Re * math.sqrt(f)))

# Fonction pour calculer les pertes de charge par mètre
def perte_charge_par_metre(f, D, v):
    return f * ((v**2)/2)*(1/D) * 1000/ 10000  # Convertir en mmCE/m

# Fonction pour calculer la vitesse d'écoulement
def calculer_vitesse(Q, D):
    A = math.pi * (D / 2) ** 2  # Aire de la section transversale du tuyau
    v = Q / A
    return v

# Données pour les modèles de pompe
# data = {
#     'modèle': ['MMTC 20', 'MMTC 26', 'MMTC 33', 'MMTC 40', 'MHTC 20', 'MHTC 30', '2 x MMTC 20', '2 x MMTC 26', '2 x MMTC 33', '2 x MMTC 40',
#                '3 x MMTC 20', '3 x MMTC 26', '3 x MMTC 33', '3 x MMTC 40'],
#     'débit': [3.68, 4.72, 5.79, 6.98, 3.5, 5.24, 7.36, 9.44, 11.58, 13.96, 11.04, 14.16, 17.37, 20.94],
#     'HMT dispo': [6.3, 3.2, 5.5, 2.8, 6.4, 4.4, 6.3, 3.2, 5.5, 2.8, 6.3, 3.2, 5.5, 2.8]
# }

# data = {
#     'modèle': ['MMTC 20', 'MMTC 26', 'MMTC 33', 'MMTC 40', 'MHTC 20', 'MHTC 30', '2 x MMTC 20', '2 x MMTC 26', '2 x MMTC 33', '2 x MMTC 40',
#                '3 x MMTC 20', '3 x MMTC 26', '3 x MMTC 33', '3 x MMTC 40', '2 x MHTC 20', '2 x MHTC 30', '3 x MHTC 20', '3 x MHTC 30',
#                '4 x MMTC 20', '4 x MMTC 26', '4 x MMTC 33', '4 x MMTC 40', '4 x MHTC 20', '4 x MHTC 30', '4 x MHTC 20', '4 x MHTC 30',
#                 '5 x MMTC 20', '5 x MMTC 26', '5 x MMTC 33', '5 x MMTC 40', '5 x MHTC 20', '5 x MHTC 30', '5 x MHTC 20', '5 x MHTC 30',
#                 '6 x MMTC 20', '6 x MMTC 26', '6 x MMTC 33', '6 x MMTC 40', '6 x MHTC 20', '6 x MHTC 30', '6 x MHTC 20', '6 x MHTC 30'],
#     'débit': [3.68, 4.72, 5.79, 6.98, 3.5, 5.24, 7.36, 9.44, 11.58, 13.96, 11.04, 14.16, 17.37, 20.94, 7.0, 10.48, 10.5, 15.72],
#     'HMT dispo': [6.3, 3.2, 5.5, 2.8, 6.4, 4.4, 6.3, 3.2, 5.5, 2.8, 6.3, 3.2, 5.5, 2.8, 6.4, 4.4, 6.4, 4.4]
# }

data = {
    'modèle': [
        'MMTC 20', 'MMTC 26', 'MMTC 33', 'MMTC 40', 
        'MHTC 20', 'MHTC 30', 
        '2 x MMTC 20', '2 x MMTC 26', '2 x MMTC 33', '2 x MMTC 40', 
        '3 x MMTC 20', '3 x MMTC 26', '3 x MMTC 33', '3 x MMTC 40', 
        '2 x MHTC 20', '2 x MHTC 30', '3 x MHTC 20', '3 x MHTC 30', 
        '4 x MMTC 20', '4 x MMTC 26', '4 x MMTC 33', '4 x MMTC 40', 
        '4 x MHTC 20', '4 x MHTC 30', 
        '5 x MMTC 20', '5 x MMTC 26', '5 x MMTC 33', '5 x MMTC 40', 
        '5 x MHTC 20', '5 x MHTC 30', 
        '6 x MMTC 20', '6 x MMTC 26', '6 x MMTC 33', '6 x MMTC 40', 
        '6 x MHTC 20', '6 x MHTC 30'
    ],
    'débit': [
        3.68, 4.72, 5.79, 6.98, 
        3.5, 5.24, 
        2 * 3.68, 2 * 4.72, 2 * 5.79, 2 * 6.98, 
        3 * 3.68, 3 * 4.72, 3 * 5.79, 3 * 6.98, 
        2 * 3.5, 2 * 5.24, 3 * 3.5, 3 * 5.24, 
        4 * 3.68, 4 * 4.72, 4 * 5.79, 4 * 6.98, 
        4 * 3.5, 4 * 5.24, 
        5 * 3.68, 5 * 4.72, 5 * 5.79, 5 * 6.98, 
        5 * 3.5, 5 * 5.24, 
        6 * 3.68, 6 * 4.72, 6 * 5.79, 6 * 6.98, 
        6 * 3.5, 6 * 5.24
    ],
    'HMT dispo': [
        6.3, 3.2, 5.5, 2.8, 
        6.4, 4.4, 
        6.3, 3.2, 5.5, 2.8, 
        6.3, 3.2, 5.5, 2.8, 
        6.4, 4.4, 6.4, 4.4, 
        6.3, 3.2, 5.5, 2.8, 
        6.4, 4.4, 
        6.3, 3.2, 5.5, 2.8, 
        6.4, 4.4, 
        6.3, 3.2, 5.5, 2.8, 
        6.4, 4.4
    ]
}


import streamlit as st

# Dictionnaire des températures et viscosités cinématiques correspondantes (en m²/s)
viscosity_data = 1.31e-6

#Titre de l'app
st.title("Longueur maximale des conduites pour PAC MMTC et MHTC")

# Titre de l'application
# st.subheader("Viscosité cinématique de l'eau")

# Barre de sélection horizontale pour choisir une température
# temperature = st.slider(
#     "Choisissez une température (°C) :",
#     min_value=min(viscosity_data.keys()),
#     max_value=max(viscosity_data.keys()),
#     step=5,
#     value=20  # Valeur par défaut
# )

# Récupération de la viscosité correspondant à la température choisie
viscosity = viscosity_data

# Affichage des résultats
st.write(f"Nous utilisons la viscosité cinématique de l'eau à 10°: **{viscosity_data} m²/s**.")




def main():
    
    
    # Sélection du modèle de PAC
    st.markdown('<p style="font-size:20px; margin-bottom: 0px; margin-top: 20px;"><strong>Choisissez un modèle de PAC:</strong></p>', unsafe_allow_html=True)
    modèle = st.selectbox("", data['modèle'])

    # Sélection du matériau
    st.markdown('<p style="font-size:20px; margin-bottom: 0px;margin-top: 20px;"><strong>Choisissez un matériau de conduit:</strong></p>', unsafe_allow_html=True)
    materiau = st.selectbox("", list(tubes_data.keys()))

    # Sélection de la taille du tube en fonction du matériau
    st.markdown('<p style="font-size:20px; margin-bottom: 0px;margin-top: 20px;"><strong>Choisissez la taille du tube:</strong></p>', unsafe_allow_html=True)
    diamètre = st.selectbox("", list(tubes_data[materiau]["D"].keys()))


    nu = viscosity


    # Récupérer le diamètre intérieur et la rugosité
    Diam = tubes_data[materiau]["D"][diamètre]   # Convertir en mètres
    D = Diam/1000
    rugos = tubes_data[materiau]["rugosites"]   # Convertir en mètres
    rugosites = rugos/1000
    st.write(f"Le diamètre intérieur pour le tube en {materiau}, taille {diamètre} est : {Diam} mm.")
    st.write(f"Rugosité utilisée pour le tube en {materiau} : {rugos} mm.")

    # Trouver le débit correspondant au modèle choisi
    index = data['modèle'].index(modèle)
    Q_h = data['débit'][index]
    HMT_dispo = data['HMT dispo'][index]

    # Convertir le débit volumique de m³/h en m³/s
    Q = Q_h / 3600  # 1 heure = 3600 secondes

    # Calculer la vitesse d'écoulement
    v = calculer_vitesse(Q, D)
    if v > 1.5:
        st.markdown(f"<div style='background-color: red; padding: 10px;'>La vitesse d'écoulement est de {v:.2f} m/s</div>", unsafe_allow_html=True)
    else:
        st.write(f"La vitesse d'écoulement est de {v:.2f} m/s")

    # Calculer le nombre de Reynolds avec la nouvelle valeur de nu
    Re = (v * D) / nu
    st.write(f"Le nombre de Reynolds est de {Re:.0f}")



    # Nombre de coudes à 90° grand angle

    st.markdown('<p style="font-size:20px; margin-bottom: 0px;margin-top: 20px;"><strong>Nombre de coudes à 90° grand angle:</strong></p>', unsafe_allow_html=True)
    coudes = st.selectbox("", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16 , 17, 18, 19, 20])

    # PdC singulières (T, VI, entrée-sortie BT)
    # st.markdown('<p style="font-size:20px; margin-bottom: 0px;margin-top: 20px;"><strong>Somme des dzeta si connues</strong></p>', unsafe_allow_html=True)
    # dzeta_T_VI_BT = st.number_input("", min_value=0.0, step=0.1)

    # PdC filtre + clapet
    st.markdown('<p style="font-size:20px; margin-bottom: 0px;margin-top: 20px;"><strong>Pertes de charges supplémentaires (vanne équilibrages, serpentin ballon, accidents,...(mCE)</strong></p>', unsafe_allow_html=True)

    pdc_autre1 = st.number_input(".", min_value=0.0, step=0.1, key='pdc_autre1')
    pdc_autre2 = st.number_input(".", min_value=0.0, step=0.1, key='pdc_autre2')
    pdc_autre3 = st.number_input(".", min_value=0.0, step=0.1, key='pdc_autre3')


    pdc_autre = pdc_autre1 + pdc_autre2 + pdc_autre3


    # Choix de déduire la perte de charge statique

    st.markdown('<p style="font-size:20px; margin-bottom: 0px;margin-top: 20px;"><strong>Déduction de la perte de charge totale théorique pour: VI, Filtre, Clapet AR, T et Brides Tampon en fonction du modèle MMTC:</strong></p>', unsafe_allow_html=True)
    deduire_pdc_statique = st.checkbox("Déduire", value=True)


   


    Total_pdc_statique = 0

       



    # v²/2g
    y = (v**2)/(2*9.81)

    # PdC coudes 90°
    pdc_coudes = y * coudes * 0.45

    # PdC pour 2Té + 2 VI + 2 Brides
    # pdc_T_VI_BT = dzeta_T_VI_BT * y

     # Si déduction de la perte de charge statique
    if deduire_pdc_statique and modèle in pertes_charge_statique:
        pdc_statique = pertes_charge_statique[modèle]
        Total_pdc_statique = pdc_coudes + pdc_statique + pdc_autre1 + pdc_autre2 + pdc_autre3
        st.write(f"Perte de charge statique déduite : {pdc_statique} mCE")
        # st.image('Tableau_PdC2.png', caption='Tableau PdC2')
        st.image("Tableau_PdC2.png",  use_container_width=True)
        
    else:
        Total_pdc_statique = pdc_coudes + pdc_autre




    # Calculer les pertes de charge métriques et la longueur possible du tube
    if Re > 2000:
        initial_guess = 0.02
        f_solution, = fsolve(colebrook, initial_guess, args=(rugosites, D, Re))
        perte_par_metre = perte_charge_par_metre(f_solution, D, v)
        longueur_possible = (HMT_dispo - Total_pdc_statique ) / perte_par_metre

          # Afficher les résultats
        st.write(f"Le coefficient de frottement est de {f_solution:.3f}")

        #st.write(f"PdC singulières pour: 2 Té + 2 Vannes d'isolement + 2 Brides volume tampon sont: {pdc_T_VI_Br:.3f} mCE")
        st.write(f"Les PdC singulières totales sont de {Total_pdc_statique:.3f} mCE")
        st.write(f"Les PdC métriques sont de {perte_par_metre:.3f} mCE/m")

        if longueur_possible > 0:
            st.markdown(f"<div style='background-color: lightgreen; padding: 10px;'>La longueur maximale aller-retour de la conduite est de {longueur_possible:.2f} mètres</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='background-color: red; padding: 10px;'>Les pertes de charge dépassent la HMT disponible, aucune longueur n'est possible.</div>", unsafe_allow_html=True)

    else:
        st.write("L'écoulement est laminaire, utilisez une autre méthode de calcul.")



    
    st.write("")
    st.write("")
    st.divider()
    st.write("")



    # --- Interface utilisateur ---
    st.title("Calcul des pertes de charge des ballons B aux débit des PAC")
    st.markdown("Saisissez le débit et choisissez le ballon pour afficher les pertes de charge et le graphique correspondant.")

   
    # st.image("Tableau_debit.png",  use_container_width=True)

  

    st.image('Tableau3.jpg', use_container_width=True)


    # st.image("Tableau_debit.png",  use_column_width=True)

    debit_ballon = st.slider(
    "Choisissez un débit pour le ballon ECS :",
    min_value = 0.0,
    max_value= 10.0,
    step=0.1,
    value=5.  # Valeur par défaut
)


    # 2️⃣ Sélection du ballon
    ballon_choisi = st.selectbox(
        "Choisissez le type de ballon :", options=list(ballons.keys())
    )

    # --- Récupération des données du ballon choisi ---
    debit_reference = ballons[ballon_choisi]["debit"]
    pdc_reference = ballons[ballon_choisi]["pdc"]

    # --- Calcul des pertes de charge (formule de perte de charge proportionnelle au carré du débit) ---
    def calcul_pdc(debit, debit_ref, pdc_ref):
        """Calcule la perte de charge pour un débit donné en utilisant la loi quadratique."""
        return pdc_ref * (debit / debit_ref) ** 2

    pdc_utilisateur = calcul_pdc(debit_ballon, debit_reference, pdc_reference)

    # 3️⃣ Affichage des résultats
    st.subheader("Résultats")
    st.markdown(f"**Ballon choisi** : {ballon_choisi}")
    st.markdown(f"**Débit saisi** : {debit_ballon:.2f} m³/h")
    st.markdown(f"**Pertes de charge** : {pdc_utilisateur:.2f} mCE")

    # 4️⃣ Tracé du graphique
    debits = np.linspace(0, 10, 100)  # Plage de débits de 0 à 10 m³/h
    pdc_values = [calcul_pdc(d, debit_reference, pdc_reference) for d in debits]  # Calcul des pertes de charge

    # Crée un DataFrame pour le traçage du graphique
    df = pd.DataFrame({
        "Débit (m³/h)": debits,
        "Pertes de charge (mCE)": pdc_values
    })

    # Tracé avec le point de fonctionnement
    fig = px.line(df, x="Débit (m³/h)", y="Pertes de charge (mCE)", title="Courbe des pertes de charge")
    fig.add_scatter(
        x=[debit_ballon], 
        y=[pdc_utilisateur], 
        mode='markers+text', 
        marker=dict(size=10, color='red'), 
        name='Point de fonctionnement',
        text=["Point de fonctionnement"],
        textposition="bottom right"
    )

    # Tracé des lignes pointillées
    fig.add_scatter(
        x=[debit_ballon, debit_ballon], 
        y=[0, pdc_utilisateur], 
        mode='lines', 
        line=dict(dash='dot', color='red'), 
        name='Ligne pointillée'
    )
    fig.add_scatter(
        x=[0, debit_ballon], 
        y=[pdc_utilisateur, pdc_utilisateur], 
        mode='lines', 
        line=dict(dash='dot', color='red'), 
        name='Ligne pointillée'
    )

    # Affichage du graphique
    st.plotly_chart(fig)











if __name__ == "__main__":
    main()


