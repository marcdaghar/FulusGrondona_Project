def dette_usuraire(t):
    return dette_initiale * np.exp(taux_riba * t)

# 2. La confiance s'érode avec la dette et les crises
# (L'illusion monétaire se dissipe)
def confiance_credite(t, seuil_crise=150):
    # La confiance chute brusquement lorsque la dette devient insoutenable (équilibre ponctué)
    if t > seuil_crise:
        return 0.1  # Érosion rapide
    else:
        return 0.95 - (t / 200) * 0.4  # Érosion lente

# 3. Émergence du Crypto-Fulus (Monnaie-travail)
# L'adhésion est mimétique (effet de seuil)
def adhesion_fulus(t):
    # Seuil critique atteint pendant la crise (tache d'huile)
    if t > 150:
        return 0.8  # Forte adhésion
    elif t > 100:
        return 0.5  # Croissance
    else:
        return 0.1  # Adhésion faible

# 4. Simulation du "Coup de Banque" : le gouvernement se réapproprie l'État
def coup_de_banque(t):
    # À partir d'un certain point, la banque est rendue obsolète
    if t > 160:
        return "Bimétallisme Instauré"
    else:
        return "Système Usuraire en Place"

# Génération des données
dette = [dette_usuraire(i) for i in t]
confiance = [confiance_credite(i) for i in t]
adhesion = [adhesion_fulus(i) for i in t]

# Visualisation de la "Grande Transformation"
fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('Temps (Unité de crise)')
ax1.set_ylabel('Dette Usuraire', color=color)
ax1.plot(t, dette, color=color, label='Dette (Riba)')
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()
color = 'tab:blue'
ax2.set_ylabel('Confiance / Adhésion', color=color)
ax2.plot(t, confiance, color='tab:green', label='Confiance Crédit (Illusion)')
ax2.plot(t, adhesion, color='tab:orange', label='Adhésion Fulus (Réalité)')
ax2.tick_params(axis='y', labelcolor=color)

# Ajout de la ligne de "Coup de Banque" (Équilibre Ponctué)
ax1.axvline(x=160, color='k', linestyle='--', label='Coup de Banque (Transition)')

plt.title('Logique du Détour : De l\'Usure au Bimétallisme')
fig.tight_layout()
plt.show()

# Résultat du modèle : les dynasties usuraires conservent leur richesse mais perdent leur pouvoir
print("Résultat de la Simulation :")
print(f"- Dette finale (dynasties) : {dette[-1]:.2f}")
print(f"- Confiance dans le crédit : {confiance[-1]:.2f}")
print(f"- Adhésion au Crypto-Fulus : {adhesion[-1]:.2f}")
print(f"- Régime : {coup_de_banque(170)}")
Concept
Implémentation
