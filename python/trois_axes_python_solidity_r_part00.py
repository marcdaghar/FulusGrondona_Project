import numpy as np
import matplotlib.pyplot as plt

# Paramètres de la simulation
annees = 30
population = 1000
travail_initial = 100  # Unité de travail par agent
taux_interet = 0.05  # 5% d'intérêt (riba)
taux_croissance_reelle = 0.02  # Croissance de la production

# 1. Simulation du système usuraire (Riba)
def simulation_riba(annees, population, travail_initial, taux_interet):
    dette_totale = np.zeros(annees)
    richesse_accumulee = np.zeros(annees)
    dette_par_agent = travail_initial * (1 - 1/(1+taux_interet))  # Dette initiale pour consommer
    richesse_totale = population * travail_initial
    
    for t in range(annees):
        # La dette augmente avec les intérêts composés
        dette_par_agent *= (1 + taux_interet)
        # La richesse totale (PIB) croît lentement
        richesse_totale *= (1 + taux_croissance_reelle)
        
        dette_totale[t] = dette_par_agent * population
        richesse_accumulee[t] = richesse_totale
        
    return dette_totale, richesse_accumulee

# 2. Simulation du système Crypto-Fulus (Monnaie-Travail)
def simulation_fulus(annees, population, travail_initial):
    # Pas de dette. La monnaie est émise en fonction du travail.
    masse_monetaire = np.zeros(annees)
    production_totale = np.zeros(annees)
    travail_total = population * travail_initial
    
    for t in range(annees):
        # La production augmente avec le travail réel
        production_totale[t] = travail_total * (1 + taux_croissance_reelle)**t
        # La monnaie est strictement équivalente à la production (MV=PY)
        masse_monetaire[t] = production_totale[t]
        
    return masse_monetaire, production_totale

# Exécution des simulations
dette, richesse = simulation_riba(annees, population, travail_initial, taux_interet)
fulus, production = simulation_fulus(annees, population, travail_initial)

# 3. Visualisation
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Graphique 1 : Système Usuraire
ax1.plot(dette, label="Dette Totale (Intérêts Composés)", color='red')
ax1.plot(richesse, label="PIB Réel", color='blue')
ax1.set_title("Système Usuraire (Riba)")
ax1.set_xlabel("Années")
ax1.set_ylabel("Valeur (Unités)")
ax1.legend()
ax1.grid(True)

# Graphique 2 : Système Crypto-Fulus
ax2.plot(fulus, label="Masse Monétaire (Fulus)", color='green')
ax2.plot(production, label="Production (PIB)", color='blue', linestyle='--')
ax2.set_title("Système Crypto-Fulus (Monnaie-Travail)")
ax2.set_xlabel("Années")
ax2.set_ylabel("Valeur (Unités)")
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.show()

# 4. Sortie de l'analyse
print("--- Analyse Comparative ---")
print(f"1. Dette finale (Riba): {dette[-1]:,.2f} unités")
print(f"2. Richesse finale (PIB): {richesse[-1]:,.2f} unités")
print(f"3. Rapport Dette/PIB (Riba): {dette[-1]/richesse[-1]:.2f}%")
print(f"4. Masse monétaire (Fulus): {fulus[-1]:,.2f} unités")
print(f"5. La dette (Riba) croît exponentiellement, tandis que la monnaie-travail (Fulus) reste alignée sur la production réelle.")

