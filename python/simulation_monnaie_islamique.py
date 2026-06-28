import matplotlib.pyplot as plt
import numpy as np

# ==============================================
# 1. FONCTIONS DE BASE : MODÉLISATION CONCEPTUELLE
# ==============================================

def monnaie_rapport_social(C, A, L):
    """
    Modélise la monnaie (M) comme un rapport social total.
    M = f(C, A, L), où C est la croyance collective, A l'affect collectif,
    et L la légitimité (ancrage politique ou conventionnel).
    """
    return (C + A) * L

def desir_argent(M, T, theta):
    """
    Modélise le désir mimétique de l'argent (D_argent).
    D_argent = h(M, T, θ), où T est la tension mimétique et θ le seuil subjectif.
    """
    return M * T / (1 + theta)

def valeur_nuqud(P_metaux, P_technique, eta=0.8):
    """
    Valeur du Nuqud (or, argent) : combine prix des métaux et coût technique.
    """
    return eta * (P_metaux + P_technique)

def valeur_fulus(C_convention, P_autorite):
    """
    Valeur du Fulus (monnaie de compte) : entièrement conventionnelle.
    """
    return C_convention + P_autorite

def efficacite_legitimatrice(L_substantielle, L_formelle, L_intellectuelle):
    """
    Efficacité légitimatrice (E_L) : force de la croyance en valeur.
    """
    if (L_formelle + L_intellectuelle) == 0:
        return L_substantielle
    return L_substantielle / (L_formelle + L_intellectuelle)

def sacre_comme_filtre(L_intellectuelle, seuil=0.8):
    """
    Fonction filtre pour le sacré : si la médiation intellectuelle est trop forte,
    la valeur est exposée à la critique réflexive.
    """
    if L_intellectuelle > seuil:
        return 0  # La valeur est exposée, donc elle perd son caractère sacré
    else:
        return 1  # La valeur est protégée

def zakat(M_monnaie, N_isab=100):
    """
    Calcule la Zakat comme prélèvement sur la richesse au-delà du nisab.
    Z = 0.025 * (M - N)
    """
    if M_monnaie > N_isab:
        return 0.025 * (M_monnaie - N_isab)
    else:
        return 0

def reflexe_archaique(L_substantielle, E_modernite):
    """
    Réactivation du réflexe archaïque en période de crise.
    """
    if E_modernite == 0:
        return L_substantielle
    return L_substantielle / E_modernite

# ==============================================
# 2. FONCTIONS DE SIMULATION ET VISUALISATION
# ==============================================

def simuler_desir_argent():
    """
    Simule l'évolution du désir d'argent en fonction de la tension mimétique (T).
    """
    M = 1  # Rapport social monétaire constant
    theta = 0.5  # Seuil subjectif
    T_values = np.linspace(0.1, 2.0, 20)  # Tension mimétique variable
    desire_values = [desir_argent(M, T, theta) for T in T_values]

    plt.figure(figsize=(10, 6))
    plt.plot(T_values, desire_values, 'b-o', label='Désir d\'argent (D_argent)')
    plt.xlabel('Tension Mimétique (T)')
    plt.ylabel('Intensité du Désir d\'Argent')
    plt.title('Modélisation du Désir Mimétique de l\'Argent')
    plt.grid(True)
    plt.legend()
    plt.show()

def simuler_efficacite_legitimatrice():
    """
    Simule la perte d'efficacité légitimatrice (E_L) avec la médiation intellectuelle.
    """
    L_substantielle = 10  # Force de la croyance substantielle
    L_formelle = 2  # Force de la légitimité formelle (constante)
    L_intellectuelle_values = np.linspace(0, 10, 20)  # Médiation intellectuelle variable
    efficacite_values = [efficacite_legitimatrice(L_substantielle, L_formelle, L_int) for L_int in L_intellectuelle_values]
    sacre_status = [sacre_comme_filtre(L_int) for L_int in L_intellectuelle_values]

    plt.figure(figsize=(12, 6))

    # Graphique de l'efficacité
    plt.subplot(1, 2, 1)
    plt.plot(L_intellectuelle_values, efficacite_values, 'r-o', label='Efficacité Légitimatrice (E_L)')
    plt.xlabel('Médiation Intellectuelle (L_intellectuelle)')
    plt.ylabel('Efficacité')
    plt.title('Perte d\'Efficacité avec la Rationalité')
    plt.grid(True)
    plt.legend()

    # Graphique du statut du sacré
    plt.subplot(1, 2, 2)
    plt.step(L_intellectuelle_values, sacre_status, where='mid', label='Statut du Sacré (S)')
    plt.xlabel('Médiation Intellectuelle (L_intellectuelle)')
    plt.ylabel('1 = Protégé, 0 = Exposé')
    plt.title('Filtre du Sacré face à la Critique Réflexive')
    plt.ylim(-0.1, 1.1)
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()

def simuler_zakat_et_accumulation():
    """
    Simule l'effet de la Zakat sur la richesse nette.
    """
    richesse_initiale = 1000
    taux_croissance = 0.08
    n_years = 20
    nisab = 500

    richesse_sans_zakat = [richesse_initiale * (1 + taux_croissance)**i for i in range(n_years)]
    richesse_avec_zakat = []
    r = richesse_initiale
    for i in range(n_years):
        zakat = zakat(r, nisab)
        r = r - zakat + (taux_croissance * r)  # Croissance moins prélèvement
        richesse_avec_zakat.append(r)

    years = np.arange(n_years)

    plt.figure(figsize=(12, 6))
    plt.plot(years, richesse_sans_zakat, 'g-o', label='Richesse sans Zakat')
    plt.plot(years, richesse_avec_zakat, 'r-o', label='Richesse avec Zakat')
    plt.xlabel('Années')
    plt.ylabel('Richesse')
    plt.title('Effet de la Zakat sur l\'Accumulation de Richesse')
    plt.axhline(y=nisab, color='blue', linestyle='--', label=f'Nisab = {nisab}')
    plt.grid(True)
    plt.legend()
    plt.show()

def simuler_bimetallisme_stabilite():
    """
    Simule la volatilité relative du bimétallisme par rapport à une monnaie unique.
    """
    # Génération de prix simulés
    np.random.seed(42)
    prix_or = 100 + np.cumsum(np.random.randn(100) * 0.5)
    prix_argent = 10 + np.cumsum(np.random.randn(100) * 0.3)

    # Volatilité calculée sur les 100 jours
    volatilite_or = np.std(prix_or)
    volatilite_argent = np.std(prix_argent)

    # Volatilité du bimétallisme
    volatilite_bimetallique = (volatilite_or + volatilite_argent) / 2

    print(f"Volatilité de l'Or : {volatilite_or:.2f}")
    print(f"Volatilité de l'Argent : {volatilite_argent:.2f}")
    print(f"Volatilité du Bimétallisme : {volatilite_bimetallique:.2f}")

    # Visualisation
    plt.figure(figsize=(12, 6))
    plt.plot(prix_or, label='Or')
    plt.plot(prix_argent, label='Argent')
    plt.title('Simulation des Prix des Métaux Précieux')
    plt.xlabel('Jours')
    plt.ylabel('Prix')
    plt.legend()
    plt.grid(True)
    plt.show()

def simuler_pharmakon_crypto():
    """
    Simule l'évolution d'un pharmakon (Crypto-Fulus) comme alternative au système.
    """
    # Paramètres de la simulation
    temps = np.linspace(0, 100, 100)
    convention = 0.5
    archaique = 0.3
    techno = 1.0
    cloture = 0.2

    # Puissance du pharmakon
    pharmacon = convention + archaique + techno - cloture

    # Simuler un système capitaliste usuraire en déclin (effet de l'adoption)
    adoption_pharmakon = 1 / (1 + np.exp(-0.1 * (temps - 50)))  # Courbe en S
    effet_systeme = 1 - adoption_pharmakon  # Le système usuraire perd de l'importance

    plt.figure(figsize=(12, 6))
    plt.plot(temps, adoption_pharmakon, 'b-', label='Adoption du Pharmakon (Crypto-Fulus)')
    plt.plot(temps, effet_systeme, 'r-', label='Déclin du Système Usuraire')
    plt.xlabel('Temps')
    plt.ylabel('Intensité')
    plt.title('Le Pharmakon : Adoption du Crypto-Fulus et Déclin du Capitalisme')
    plt.grid(True)
    plt.legend()
    plt.show()

# ==============================================
# 3. EXÉCUTION DES SIMULATIONS
# ==============================================

if __name__ == "__main__":
    print("=== SIMULATION 1 : DÉSIR MIMÉTIQUE DE L'ARGENT ===")
    simuler_desir_argent()

    print("\n=== SIMULATION 2 : EFFICACITÉ LÉGITIMATRICE ET SACRÉ ===")
    simuler_efficacite_legitimatrice()

    print("\n=== SIMULATION 3 : EFFET DE LA ZAKAT SUR L'ACCUMULATION ===")
    simuler_zakat_et_accumulation()

    print("\n=== SIMULATION 4 : STABILITÉ DU BIMÉTALLISME ===")
    simuler_bimetallisme_stabilite()

    print("\n=== SIMULATION 5 : PHARMAKON CAPITALISTE (BLOCKCHAIN) ===")
    simuler_pharmakon_crypto()

