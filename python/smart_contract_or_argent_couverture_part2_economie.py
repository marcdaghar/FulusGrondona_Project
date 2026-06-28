import numpy as np
import matplotlib.pyplot as plt

class Economie:
    def __init__(self, capital_initial, salaire, interet, productivite):
        self.capital = capital_initial
        self.salaire = salaire
        self.interet = interet
        self.productivite = productivite
        self.valeur_creee = []
        self.profits = []
        self.dette = []
        
    def simuler(self, annees):
        for annee in range(annees):
            # La productivité crée de la valeur
            valeur_produite = self.capital * self.productivite
            self.valeur_creee.append(valeur_produite)
            
            # Le coût du travail
            cout_travail = self.salaire
            
            # Le profit avant intérêt
            profit_brut = valeur_produite - cout_travail
            
            # L'intérêt à payer (l'usure)
            interet_a_payer = self.capital * self.interet
            self.dette.append(interet_a_payer)
            
            # Le profit net (ce qui reste après avoir payé l'usure)
            profit_net = profit_brut - interet_a_payer
            self.profits.append(profit_net)
            
            # Si le profit net est négatif, c'est le "vol" (l'usure consomme le travail)
            if profit_net < 0:
                print(f"Année {annee+1}: L'usure vole {-profit_net:.2f} de valeur au travailleur !")
            
            # Le capital s'accumule
            self.capital += profit_net
            
    def afficher_resultats(self):
        plt.figure(figsize=(14, 6))
        
        plt.subplot(1, 2, 1)
        plt.plot(self.valeur_creee, label='Valeur Créée par le Travail')
        plt.plot(self.dette, label='Usure (Intérêt à payer)')
        plt.xlabel('Années')
        plt.ylabel('Valeur')
        plt.title('L\'Usure : Vol de la Valeur des Travailleurs')
        plt.legend()
        plt.grid(True)
        
        plt.subplot(1, 2, 2)
        plt.plot(self.profits, label='Profit Net (Après Usure)')
        plt.axhline(y=0, color='r', linestyle='--', label='Seuil de Vol')
        plt.xlabel('Années')
        plt.ylabel('Profit')
        plt.title('Profit Net : quand l\'usure consomme tout')
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()

# Paramètres
economie = Economie(
    capital_initial=1000,
    salaire=500,
    interet=0.1,  # 10% d'intérêt
    productivite=0.6  # 60% de rendement
)

economie.simuler(20)
economie.afficher_resultats()

