# -*- coding: utf-8 -*-
"""
Annexe Technique : Modèle Agent-Based de Vélocité Monétaire
Comparaison : Système Centralisé (Feu de circulation) vs. Système Décentralisé (Rond-point / Bimétallique)
"""

import numpy as np
import matplotlib.pyplot as plt

# -----------------------------------------------------------
# Paramètres de la simulation
# -----------------------------------------------------------
N_AGENTS = 100
N_STEPS = 100
CAPITAL_INITIAL = 1000.0

# -----------------------------------------------------------
# 1. Modèle Centralisé (Monnaie Fractionnaire / Dette)
# -----------------------------------------------------------
masse_monetaire_centrale = CAPITAL_INITIAL * N_AGENTS
taux_interet = 0.02  # Le coût du "feu rouge"
velocite_centrale = []

for step in range(N_STEPS):
    # La banque centrale prête à un sous-ensemble d'agents
    emprunteurs = np.random.choice(N_AGENTS, size=int(0.3 * N_AGENTS), replace=False)
    for _ in emprunteurs:
        # Création monétaire ex nihilo par le crédit
        masse_monetaire_centrale += 100.0 * taux_interet
    
    # Calcul de la vélocité (Transactions / Masse Monétaire)
    transactions = np.random.uniform(5000, 10000)
    velocite_centrale.append(transactions / (masse_monetaire_centrale / N_AGENTS))

# -----------------------------------------------------------
# 2. Modèle Décentralisé (Rond-point / Bimétallique)
# -----------------------------------------------------------
masse_monetaire_decentrale = CAPITAL_INITIAL * N_AGENTS  # Fixe (or/argent)
velocite_decentrale = []
reseau_confiance = np.random.rand(N_AGENTS, N_AGENTS)  # Matrice de confiance
np.fill_diagonal(reseau_confiance, 0)  # Pas d'auto-confiance

for step in range(N_STEPS):
    transactions = 0.0
    for i in range(N_AGENTS):
        for j in range(N_AGENTS):
            # L'échange a lieu si la confiance est suffisante
            if reseau_confiance[i, j] > 0.5 and i != j:
                transactions += np.random.uniform(10, 100) * reseau_confiance[i, j]
    
    velocite_decentrale.append(transactions / (masse_monetaire_decentrale / N_AGENTS))
    
    # Effet Mimétique : la confiance augmente avec l'usage (Ricci Flow simplifié)
    reseau_confiance = reseau_confiance * 1.01
    reseau_confiance = np.clip(reseau_confiance, 0, 1)

# -----------------------------------------------------------
# 3. Visualisation des Résultats
# -----------------------------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(velocite_centrale, label='Système Centralisé (Feu de circulation / Dette)', color='red')
plt.plot(velocite_decentrale, label='Système Décentralisé (Rond-point / Bimétallique)', color='green')
plt.xlabel('Temps (Étapes de simulation)')
plt.ylabel('Vélocité Monétaire')
plt.title('Comparaison de la Vélocité Monétaire : Dette vs. Confiance Bimétallique')
plt.legend()
plt.grid(True, alpha=0.3)

# Affichage des moyennes
print(f"Vélocité moyenne (Centralisé) : {np.mean(velocite_centrale):.3f}")
print(f"Vélocité moyenne (Décentralisé) : {np.mean(velocite_decentrale):.3f}")
print(f"Gain de vélocité : {np.mean(velocite_decentrale) / np.mean(velocite_centrale):.2f}x")

plt.show()

# Calcul du poids de validation pour un membre de la guilde
# w_i = (s_i/S)*alpha + (a_i/A)*beta + (p_i/P)*gamma + (r_i/R)*delta

def calculer_poids_validation(s_i, a_i, p_i, r_i, S, A, P, R, alpha=0.3, beta=0.3, gamma=0.2, delta=0.2):
    """
    Calcule le poids de validation d'un membre selon le mécanisme PoSS.
    
    Paramètres:
    - s_i: solde en fulus du membre
    - a_i: ancienneté dans la guilde (jours, plafonnée à 365)
    - p_i: preuve de participation active (0-100)
    - r_i: réputation (score pairs, 0-100)
    - S, A, P, R: sommes des quantités correspondantes sur l'ensemble des validateurs
    - alpha, beta, gamma, delta: coefficients (fixés par la DAO)
    
    Retourne:
    - w_i: poids de validation
    """
    w_i = (s_i / S) * alpha + (a_i / A) * beta + (p_i / P) * gamma + (r_i / R) * delta
    return w_i

# Exemple d'utilisation
S = 1000000  # Masse monétaire totale
A = 365 * 50  # Ancienneté totale (max 365 jours * 50 membres)
P = 100 * 50  # Participation totale (max 100 * 50 membres)
R = 100 * 50  # Réputation totale (max 100 * 50 membres)

membre_exemple = {
    's_i': 10000,
    'a_i': 180,
    'p_i': 75,
    'r_i': 85
}

w = calculer_poids_validation(**membre_exemple, S=S, A=A, P=P, R=R)
print(f"Poids de validation : {w:.4f}")
# -*- coding: utf-8 -*-
"""
Simulation du mécanisme DAV (Delayed Approval Voting)
pour l'élection sans candidat dans une guilde monétaire
"""

import numpy as np
import matplotlib.pyplot as plt

# -----------------------------------------------------------
# Paramètres de la simulation
# -----------------------------------------------------------
N_MEMBRES = 50  # Nombre de membres de la guilde
N_PROPOSITIONS = 5  # Nombre de propositions techniques
N_VOTANTS = int(0.7 * N_MEMBRES)  # 70% de participation (quorum)

# Génération des poids de réputation (PoSS)
poids_reputation = np.random.uniform(0.5, 1.0, N_MEMBRES)
poids_reputation = poids_reputation / np.sum(poids_reputation)  # Normalisation

# Génération des points idéaux des membres sur le paramètre θ (ex: frais de transaction)
thetas_ideal = np.random.uniform(0, 1, N_MEMBRES)

# Propositions (valeurs de θ soumises au vote)
propositions = np.linspace(0.1, 0.9, N_PROPOSITIONS)

# -----------------------------------------------------------
# Simulation du vote DAV
# -----------------------------------------------------------
# Chaque membre vote "oui" aux propositions qui sont proches de son point idéal
# (seuil d'acceptation : distance < 0.15)
votes = np.zeros((N_MEMBRES, N_PROPOSITIONS))

for i in range(N_MEMBRES):
    for j, prop in enumerate(propositions):
        distance = abs(thetas_ideal[i] - prop)
        if distance < 0.15:
            votes[i, j] = 1

# Pondération des votes par la réputation
votes_ponderes = np.zeros(N_PROPOSITIONS)
for j in range(N_PROPOSITIONS):
    votes_ponderes[j] = np.sum(votes[:, j] * poids_reputation)

# Proposition gagnante
proposition_gagnante = np.argmax(votes_ponderes)
theta_elu = propositions[proposition_gagnante]

# -----------------------------------------------------------
# Affichage des résultats
# -----------------------------------------------------------
print(f"Propositions soumises au vote : {propositions}")
print(f"Votes pondérés : {votes_ponderes}")
print(f"Proposition gagnante : θ = {theta_elu:.3f}")

# Médiane pondérée (vérification théorique)
indices_tries = np.argsort(thetas_ideal)
poids_cumules = np.cumsum(poids_reputation[indices_tries])
mediane_ponderee = thetas_ideal[indices_tries[np.where(poids_cumules >= 0.5)[0][0]]]
print(f"Médiane pondérée théorique : θ = {mediane_ponderee:.3f}")

# Visualisation
plt.figure(figsize=(12, 6))
plt.bar(range(N_PROPOSITIONS), votes_ponderes, tick_label=[f"{p:.2f}" for p in propositions])
plt.axhline(y=np.max(votes_ponderes), color='red', linestyle='--', label=f'Gagnant: θ={theta_elu:.2f}')
plt.axvline(x=proposition_gagnante, color='green', linestyle='-', linewidth=2)
plt.xlabel('Propositions (θ)')
plt.ylabel('Votes pondérés')
plt.title('Mécanisme DAV (Delayed Approval Voting)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()
