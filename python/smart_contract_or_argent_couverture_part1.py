import matplotlib.pyplot as plt
import numpy as np

# Paramètres du système
DEPOT_INITIAL = 1000  # Dépôt initial en dollars
RESERVE_FRACTION = 0.1  # 10% de réserve obligatoire
ANNEES = 20  # Simulation sur 20 ans
TAUX_INTERET = 0.05  # 5% d'intérêt annuel

def systeme_reserve_fractionnaire(depot, reserve, annees):
    """Simule la création monétaire dans le système actuel."""
    masse_monetaire = [depot]
    credit_total = 0
    
    for annee in range(1, annees + 1):
        # Multiplicateur du crédit : chaque dépôt crée un crédit
        nouveau_credit = masse_monetaire[-1] * (1/reserve - 1)
        credit_total += nouveau_credit
        # La masse monétaire augmente (dépôt + crédit) avec les intérêts
        nouvelle_masse = (masse_monetaire[-1] + nouveau_credit) * (1 + TAUX_INTERET)
        masse_monetaire.append(nouvelle_masse)
    
    return masse_monetaire, credit_total

def systeme_crypto_fulus(depot, reserve, annees):
    """Simule le système proposé : couverture 100%."""
    masse_monetaire = [depot]
    credit_total = 0
    
    for annee in range(1, annees + 1):
        # Dans le système Crypto-Fulus, pas de création ex nihilo
        # La masse monétaire ne peut pas dépasser les réserves physiques
        # On simule une économie stable sans intérêt
        nouvelle_masse = masse_monetaire[-1]  # Pas de croissance monétaire
        masse_monetaire.append(nouvelle_masse)
        # Pas de crédit supplémentaire
        credit_total += 0
    
    return masse_monetaire, credit_total

# Exécution des simulations
masse_reserve_fractionnaire, credit_reserve = systeme_reserve_fractionnaire(DEPOT_INITIAL, RESERVE_FRACTION, ANNEES)
masse_crypto_fulus, credit_crypto = systeme_crypto_fulus(DEPOT_INITIAL, RESERVE_FRACTION, ANNEES)

# Affichage des résultats
print(f"Système actuel (Réserve fractionnaire) : Masse monétaire finale = {masse_reserve_fractionnaire[-1]:.2f}")
print(f"Système actuel (Réserve fractionnaire) : Crédit total créé = {credit_reserve:.2f}")
print(f"Crypto-Fulus : Masse monétaire finale = {masse_crypto_fulus[-1]:.2f}")
print(f"Crypto-Fulus : Crédit total créé = {credit_crypto:.2f}")

# Graphique
plt.figure(figsize=(12, 6))
plt.plot(range(ANNEES+1), masse_reserve_fractionnaire, label='Système Réserve Fractionnaire (Création ex nihilo)')
plt.plot(range(ANNEES+1), masse_crypto_fulus, label='Crypto-Fulus (Couverture 100%)')
plt.xlabel('Années')
plt.ylabel('Masse Monétaire (en unités)')
plt.title('Comparaison de la création monétaire : Allais vs Crypto-Fulus')
plt.legend()
plt.grid(True)
plt.show()

# Calcul du ratio de couverture
def ratio_couverture(masse_monetaire, reserves_physiques):
    return reserves_physiques / masse_monetaire

reserves_physiques = DEPOT_INITIAL  # Les réserves physiques n'augmentent pas
ratio_actuel = ratio_couverture(masse_reserve_fractionnaire[-1], reserves_physiques)
ratio_propose = ratio_couverture(masse_crypto_fulus[-1], reserves_physiques)

print(f"Ratio de couverture actuel : {ratio_actuel:.4f}")
print(f"Ratio de couverture proposé : {ratio_propose:.4f}")

