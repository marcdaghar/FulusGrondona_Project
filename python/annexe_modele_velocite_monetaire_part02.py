from datetime import datetime, timedelta

# -----------------------------------------------------------
# Configuration du pilote
# -----------------------------------------------------------
N_ENTREPRISES = 40
MASSE_INITIALE = 1_000_000  # Fulus initiaux
DUREE_SIMULATION = 365  # Jours

# Types d'entreprises dans la zone de Dora
SECTEURS = ['Mécanique', 'Logistique', 'Agro-alimentaire', 'Services', 'Construction']
POIDS_SECTEURS = [0.25, 0.20, 0.25, 0.15, 0.15]

# -----------------------------------------------------------
# Génération des entreprises
# -----------------------------------------------------------
np.random.seed(42)

entreprises = []
for i in range(N_ENTREPRISES):
    secteur = np.random.choice(SECTEURS, p=POIDS_SECTEURS)
    ca_annuel = np.random.uniform(100_000, 2_000_000)  # USD
    taille = np.random.choice(['Petite', 'Moyenne', 'Grande'], p=[0.5, 0.35, 0.15])
    entreprise = {
        'id': i,
        'nom': f"Entreprise_{i:02d}",
        'secteur': secteur,
        'ca_annuel': ca_annuel,
        'taille': taille,
        'taux_conversion_fulus': 0.0,  # % des transactions en fulus
        'solde_fulus': 0.0,
        'reseau': []
    }
    entreprises.append(entreprise)

# -----------------------------------------------------------
# Initialisation : allocation initiale des fulus
# -----------------------------------------------------------
# Distribution basée sur le CA (équité vs. proportionnalité)
masse_totale = MASSE_INITIALE
ca_total = sum(e['ca_annuel'] for e in entreprises)

for e in entreprises:
    # 50% distribution égalitaire, 50% proportionnelle au CA
    part_egalitaire = (masse_totale * 0.5) / N_ENTREPRISES
    part_proportionnelle = (masse_totale * 0.5) * (e['ca_annuel'] / ca_total)
    e['solde_fulus'] = part_egalitaire + part_proportionnelle

# -----------------------------------------------------------
# Simulation des transactions
# -----------------------------------------------------------
def simuler_transactions(entreprises, jours, taux_adoption=0.03):
    """
    Simule les transactions journalières entre entreprises
    avec adoption progressive du fulus
    """
    historique = []
    adoption_moyenne = []
    
    for jour in range(jours):
        # Mise à jour du taux d'adoption (logistique)
        if jour < 30:
            progression = 0.01  # Phase 1: faible
        elif jour < 90:
            progression = 0.05  # Phase 2: accélération
        else:
            progression = 0.02  # Phase 3: maturité
        
        for e in entreprises:
            # Augmentation progressive du taux de conversion
            e['taux_conversion_fulus'] = min(1.0, e['taux_conversion_fulus'] + progression * np.random.uniform(0.5, 1.5))
        
        # Transactions quotidiennes
        transactions_jour = []
        for i in range(N_ENTREPRISES):
            e1 = entreprises[i]
            for j in range(i+1, N_ENTREPRISES):
                e2 = entreprises[j]
                # Probabilité de transaction (basée sur la proximité sectorielle)
                proba = 0.3 if e1['secteur'] == e2['secteur'] else 0.1
                if np.random.random() < proba:
                    # Montant de la transaction
                    montant_usd = np.random.uniform(100, 5000)
                    # Part payée en fulus
                    taux = (e1['taux_conversion_fulus'] + e2['taux_conversion_fulus']) / 2
                    montant_fulus = montant_usd * taux
                    montant_usd_restant = montant_usd * (1 - taux)
                    
                    # Vérification du solde
                    montant_fulus = min(montant_fulus, e1['solde_fulus'])
                    
                    if montant_fulus > 0:
                        e1['solde_fulus'] -= montant_fulus
                        e2['solde_fulus'] += montant_fulus * 0.95  # 5% de frais (brûlé)
                        
                        transactions_jour.append({
                            'jour': jour,
                            'expediteur': e1['nom'],
                            'destinataire': e2['nom'],
                            'montant_fulus': montant_fulus,
                            'montant_usd': montant_usd,
                            'taux_adoption': taux
                        })
        
        historique.extend(transactions_jour)
        adoption_moyenne.append(np.mean([e['taux_conversion_fulus'] for e in entreprises]))
    
    return historique, adoption_moyenne

# -----------------------------------------------------------
# Exécution de la simulation
# -----------------------------------------------------------
transactions, adoption = simuler_transactions(entreprises, DUREE_SIMULATION)

# -----------------------------------------------------------
# Analyse des résultats
# -----------------------------------------------------------
print("=" * 60)
print("RÉSULTATS DE LA SIMULATION DU PILOTE DORA")
print("=" * 60)

print(f"\n1. Activité transactionnelle:")
print(f"   - Nombre total de transactions : {len(transactions)}")
print(f"   - Volume total en fulus : {sum(t['montant_fulus'] for t in transactions):.2f} fulus")
print(f"   - Volume total en USD : {sum(t['montant_usd'] for t in transactions):.2f} USD")

print(f"\n2. Adoption du fulus:")
print(f"   - Taux d'adoption final : {adoption[-1]*100:.1f}%")
print(f"   - Taux d'adoption moyen : {np.mean(adoption)*100:.1f}%")

print(f"\n3. Indicateurs de vélocité:")
masse_moyenne = np.mean([e['solde_fulus'] for e in entreprises])
velocite = sum(t['montant_fulus'] for t in transactions) / (masse_moyenne * N_ENTREPRISES)
print(f"   - Vélocité annualisée : {velocite * (365/DUREE_SIMULATION):.2f} rotations/an")

print(f"\n4. Taux de bouclage local:")
transaction_totale_usd = sum(t['montant_usd'] for t in transactions)
transaction_fulus_usd_equivalent = sum(t['montant_fulus'] * 0.1 for t in transactions)  # 1 fulus = 0.10 USD
taux_bouclage = transaction_fulus_usd_equivalent / transaction_totale_usd * 100
print(f"   - Taux de bouclage local : {taux_bouclage:.1f}%")

# -----------------------------------------------------------
# Visualisation
# -----------------------------------------------------------
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Graphique 1 : Adoption du fulus dans le temps
ax1 = axes[0, 0]
ax1.plot(range(DUREE_SIMULATION), [a*100 for a in adoption])
ax1.set_xlabel('Jours')
ax1.set_ylabel('Taux d\'adoption (%)')
ax1.set_title('Adoption progressive du crypto-fulus')
ax1.grid(True, alpha=0.3)

# Graphique 2 : Répartition sectorielle des transactions
ax2 = axes[0, 1]
transactions_par_secteur = {}
for t in transactions:
    secteur = next(e['secteur'] for e in entreprises if e['nom'] == t['expediteur'])
    transactions_par_secteur[secteur] = transactions_par_secteur.get(secteur, 0) + t['montant_fulus']
secteurs = list(transactions_par_secteur.keys())
volumes = list(transactions_par_secteur.values())
ax2.pie(volumes, labels=secteurs, autopct='%1.1f%%')
ax2.set_title('Volume des transactions par secteur')

# Graphique 3 : Distribution des soldes de fulus
ax3 = axes[1, 0]
soldes = [e['solde_fulus'] for e in entreprises]
ax3.hist(soldes, bins=20, edgecolor='black')
ax3.set_xlabel('Solde en fulus')
ax3.set_ylabel('Nombre d\'entreprises')
ax3.set_title('Distribution des soldes de fulus')
ax3.axvline(np.mean(soldes), color='red', linestyle='--', label=f'Moyenne: {np.mean(soldes):.0f}')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Graphique 4 : Corrélation adoption vs. taille
ax4 = axes[1, 1]
tailles = {'Petite': [], 'Moyenne': [], 'Grande': []}
for e in entreprises:
    tailles[e['taille']].append(e['taux_conversion_fulus'] * 100)
positions = [0, 1, 2]
bp = ax4.boxplot([tailles['Petite'], tailles['Moyenne'], tailles['Grande']], positions=positions, widths=0.6)
ax4.set_xticklabels(['Petite', 'Moyenne', 'Grande'])
ax4.set_ylabel('Taux d\'adoption (%)')
ax4.set_title('Adoption du fulus par taille d\'entreprise')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# -----------------------------------------------------------
# Rapport synthétique
# -----------------------------------------------------------
def generer_rapport():
    """Génère un rapport synthétique au format texte"""
    rapport = f"""
    ============================================================
    RAPPORT D'ÉVALUATION - PILOTE DORA
    ============================================================
    
    PÉRIODE : {DUREE_SIMULATION} jours
    ENTREPRISES : {N_ENTREPRISES}
    SECTEURS : {', '.join(SECTEURS)}
    
    --- INDICATEURS CLÉS ---
    
    1. ACTIVITÉ ÉCONOMIQUE
       - Transactions totales : {len(transactions)}
       - Volume en fulus : {sum(t['montant_fulus'] for t in transactions):.2f}
       - Volume en USD : {sum(t['montant_usd'] for t in transactions):.2f}$
    
    2. ADOPTION
       - Taux final : {adoption[-1]*100:.1f}%
       - Taux moyen : {np.mean(adoption)*100:.1f}%
       - Croissance mensuelle : {(adoption[-1] - adoption[0]) * 100 / (DUREE_SIMULATION/30):.1f}%/mois
    
    3. VÉLOCITÉ MONÉTAIRE
       - Rotations/an : {velocite * (365/DUREE_SIMULATION):.2f}
       - Masse monétaire moyenne : {masse_moyenne:.2f}
    
    4. BOUCLAGE LOCAL
       - Taux de substitution du dollar : {taux_bouclage:.1f}%
       - Réduction des coûts de conversion estimée : {(taux_bouclage/100) * 0.03 * 100:.1f}%
    
    5. RÉSILIENCE
       - Coefficient de Gini des soldes : 
         à calculer avec: G = (∑∑|x_i - x_j|) / (2n² * x̄)
    
    6. RECOMMANDATIONS
       - Renforcer l'adoption dans le secteur {min(transactions_par_secteur, key=transactions_par_secteur.get)}
       - Maintenir l'élan dans {max(transactions_par_secteur, key=transactions_par_secteur.get)}
       - Considérer une phase d'extension à Tripoli et Zahlé
    """
    return rapport

print(generer_rapport())

Fichier
Description
Chapitre/Annexe
velocite_comparaison.py
