import numpy as np
import matplotlib.pyplot as plt

class FractionalReserveSystem:
    """Modélisation du système de réserve fractionnaire et de la création monétaire"""
    
    def __init__(self, reserve_ratio=0.1, initial_deposit=1000, interest_rate=0.05, years=50):
        self.reserve_ratio = reserve_ratio
        self.initial_deposit = initial_deposit
        self.interest_rate = interest_rate
        self.years = years
        
    def money_multiplier(self):
        """Calcule le multiplicateur de crédit"""
        return 1 / self.reserve_ratio
    
    def total_money_created(self):
        """Calcule la masse monétaire totale créée"""
        multiplier = self.money_multiplier()
        return self.initial_deposit * multiplier
    
    def debt_growth(self):
        """Simule la croissance exponentielle de la dette avec intérêts composés"""
        years = np.arange(self.years)
        debt = self.initial_deposit * (1 + self.interest_rate) ** years
        return years, debt
    
    def structural_deficit(self):
        """Calcule le déficit structurel du système"""
        total_money = self.total_money_created()
        total_debt_with_interest = self.initial_deposit * (1 + self.interest_rate) ** self.years
        return total_debt_with_interest - total_money
    
    def plot_debt_growth(self):
        """Visualise la croissance de la dette"""
        years, debt = self.debt_growth()
        
        plt.figure(figsize=(10, 6))
        plt.plot(years, debt, label='Dette avec intérêts', linewidth=2)
        plt.axhline(y=self.total_money_created(), color='red', linestyle='--', 
                   label=f'Masse monétaire totale ({self.total_money_created():.0f})')
        plt.xlabel('Années')
        plt.ylabel('Montant')
        plt.title('Croissance Exponentielle de la Dette')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
        
        print(f"Taux de réserve : {self.reserve_ratio*100}%")
        print(f"Multiplicateur de crédit : {self.money_multiplier():.1f}")
        print(f"Masse monétaire créée : {self.total_money_created():.0f}")
        print(f"Déficit structurel après {self.years} ans : {self.structural_deficit():.0f}")

# Exemple
system = FractionalReserveSystem(reserve_ratio=0.1, initial_deposit=1000, interest_rate=0.05, years=50)
system.plot_debt_growth()

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

class ParadoxicalInjunction:
    """Modélise l'injonction paradoxale de l'État (double bind)"""
    
    def __init__(self, population_size=1000):
        self.population_size = population_size
        
    def generate_behaviors(self):
        """Génère des comportements aléatoires (GAFAM vs Souverain)"""
        behaviors = np.random.choice(['GAFAM', 'Souverain'], size=self.population_size, p=[0.6, 0.4])
        
        # Facteurs de risque pour chaque comportement
        risk_scores = {
            'GAFAM': np.random.normal(loc=0.3, scale=0.1, size=sum(behaviors == 'GAFAM')),
            'Souverain': np.random.normal(loc=0.7, scale=0.15, size=sum(behaviors == 'Souverain'))
        }
        
        return behaviors, risk_scores
    
    def signal_risk(self, risk_score, threshold=0.5):
        """Détermine si le comportement est signalé comme radical"""
        return risk_score > threshold
    
    def simulate_double_bind(self):
        """Simule l'injonction paradoxale"""
        behaviors, risk_scores = self.generate_behaviors()
        
        # Taux de signalement par catégorie
        gafam_risks = risk_scores['GAFAM']
        souverain_risks = risk_scores['Souverain']
        
        gafam_signaled = sum(gafam_risks > 0.5) / len(gafam_risks) if len(gafam_risks) > 0 else 0
        souverain_signaled = sum(souverain_risks > 0.5) / len(souverain_risks) if len(souverain_risks) > 0 else 0
        
        # Visualisation
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        # Distribution des risques
        ax1.hist(gafam_risks, bins=20, alpha=0.5, label='GAFAM', color='blue')
        ax1.hist(souverain_risks, bins=20, alpha=0.5, label='Souverain', color='red')
        ax1.axvline(x=0.5, color='black', linestyle='--', label='Seuil de signalement')
        ax1.set_xlabel('Score de risque')
        ax1.set_ylabel('Fréquence')
        ax1.set_title('Distribution des Scores de Risque par Comportement')
        ax1.legend()
        
        # Taux de signalement
        ax2.bar(['GAFAM', 'Souverain'], [gafam_signaled*100, souverain_signaled*100], 
                color=['blue', 'red'], alpha=0.7)
        ax2.set_ylabel('% Signalé comme Radical')
        ax2.set_title('Taux de Signalement par Type de Comportement')
        ax2.set_ylim(0, 100)
        
        for i, v in enumerate([gafam_signaled*100, souverain_signaled*100]):
            ax2.text(i, v + 2, f'{v:.1f}%', ha='center')
        
        plt.tight_layout()
        plt.show()
        
        print(f"Taux de signalement GAFAM : {gafam_signaled*100:.1f}%")
        print(f"Taux de signalement Souverain : {souverain_signaled*100:.1f}%")
        print(f"Injonction Paradoxale : {souverain_signaled > gafam_signaled}")

# Exemple
simulation = ParadoxicalInjunction(population_size=2000)
simulation.simulate_double_bind()

import numpy as np
import matplotlib.pyplot as plt

class AntifragileSystem:
    """Modélisation de l'antifragilité selon Taleb"""
    
    def __init__(self, shock_magnitude=0.2, n_agents=1000):
        self.shock_magnitude = shock_magnitude
        self.n_agents = n_agents
        
    def simulate_shock(self):
        """Simule un choc sur le système"""
        # Fragile: perte exponentielle
        fragile = np.random.uniform(100, 120, self.n_agents)
        fragile_loss = self.shock_magnitude * fragile * np.random.normal(1.5, 0.3, self.n_agents)
        fragile_after = fragile - fragile_loss
        
        # Robust: perte linéaire
        robust = np.random.uniform(100, 120, self.n_agents)
        robust_loss = self.shock_magnitude * robust
        robust_after = robust - robust_loss
        
        # Antifragile: gain du désordre
        antifragile = np.random.uniform(100, 120, self.n_agents)
        antifragile_gain = self.shock_magnitude * antifragile * np.random.normal(0.8, 0.2, self.n_agents)
        antifragile_after = antifragile + antifragile_gain
        
        return {
            'fragile': (fragile, fragile_after),
            'robust': (robust, robust_after),
            'antifragile': (antifragile, antifragile_after)
        }
    
    def plot_impact(self):
        """Visualise l'impact des chocs sur les différents systèmes"""
        results = self.simulate_shock()
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        categories = ['Fragile', 'Robuste', 'Antifragile']
        colors = ['red', 'orange', 'green']
        
        for idx, (cat, (before, after)) in enumerate(results.items()):
            ax = axes[idx]
            ax.scatter(before, after, alpha=0.3, color=colors[idx])
            ax.plot([min(before), max(before)], [min(before), max(before)], 
                   'k--', alpha=0.5, label='Équilibre (pas de changement)')
            
            mean_loss = np.mean(after - before)
            ax.set_title(f'{cat}\nChangement moyen: {mean_loss:.1f}')
            ax.set_xlabel('Valeur initiale')
            ax.set_ylabel('Valeur après choc')
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        plt.tight_layout()
        plt.show()

# Exemple
system = AntifragileSystem(shock_magnitude=0.2, n_agents=1000)
system.plot_impact()

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

class OptimalGovernmentSize:
    """Modélisation de la taille optimale de l'État"""
    
    def __init__(self, alpha=10, beta=0.5, gamma=2, delta=0.1):
        """
        alpha: gain marginal de l'intervention de l'État
        beta: perte due à la bureaucratie (effet quadratique)
        gamma: importance de la complexité sociale
        delta: facteur de décroissance pour les rendements décroissants
        """
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
    
    def welfare_function(self, size):
        """
        Fonction de bien-être social
        size: taille de l'État en % du PIB (0-100)
        """
        # Bénéfices de l'État (sécurité, infrastructures)
        benefits = self.alpha * size
        
        # Coûts de la bureaucratie (effet quadratique)
        bureaucracy_costs = self.beta * (size ** 2)
        
        # Effet de la complexité sociale (rendements décroissants)
        complexity = self.gamma * (1 - np.exp(-self.delta * size))
        
        return benefits - bureaucracy_costs + complexity
    
    def optimal_size(self):
        """Trouve la taille optimale de l'État"""
        result = minimize_scalar(lambda x: -self.welfare_function(x), bounds=(0, 100), method='bounded')
        return result.x
    
    def plot_welfare(self):
        """Visualise la fonction de bien-être"""
        sizes = np.linspace(0, 100, 1000)
        welfare = [self.welfare_function(s) for s in sizes]
        
        optimal = self.optimal_size()
        optimal_welfare = self.welfare_function(optimal)
        
        plt.figure(figsize=(12, 6))
        plt.plot(sizes, welfare, linewidth=2, label='Bien-être social')
        plt.axvline(x=optimal, color='red', linestyle='--', 
                   label=f'Taille optimale: {optimal:.1f}%')
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        plt.scatter(optimal, optimal_welfare, color='red', s=100, zorder=5)
        
        plt.xlabel('Taille de l\'État (% du PIB)')
        plt.ylabel('Bien-être Social')
        plt.title('Modélisation de la Taille Optimale de l\'État')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
        
        return optimal

# Exemple
model = OptimalGovernmentSize(alpha=10, beta=0.5, gamma=2, delta=0.1)
model.plot_welfare()

import numpy as np
import matplotlib.pyplot as plt

class EconomicEntropy:
    """Modèle thermodynamique de l'économie usuraire"""
    
    def __init__(self, initial_resources=1000, growth_rate=0.05, extraction_rate=0.1, years=50):
        self.initial_resources = initial_resources
        self.growth_rate = growth_rate
        self.extraction_rate = extraction_rate
        self.years = years
    
    def simulate_entropy(self):
        """Simule l'augmentation de l'entropie dans une économie usuraire"""
        time = np.arange(self.years)
        
        # Ressources naturelles
        resources = self.initial_resources * np.exp(-self.extraction_rate * time)
        
        # Production économique (PIB)
        production = self.initial_resources * (1 + self.growth_rate) ** time
        
        # Entropie (désordre) - proportionnelle à la production et à la destruction des ressources
        entropy = 1 - (resources / self.initial_resources) + production / self.initial_resources
        
        # Capacité néguentropique (ordre) - diminue avec l'entropie
        negentropy = 1 / (1 + entropy * 0.1)
        
        return time, resources, production, entropy, negentropy
    
    def plot_entropy(self):
        """Visualise l'évolution de l'entropie"""
        time, resources, production, entropy, negentropy = self.simulate_entropy()
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Ressources
        axes[0, 0].plot(time, resources, color='green', linewidth=2)
        axes[0, 0].set_xlabel('Années')
        axes[0, 0].set_ylabel('Ressources')
        axes[0, 0].set_title('Dégradation des Ressources')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Production
        axes[0, 1].plot(time, production, color='blue', linewidth=2)
        axes[0, 1].set_xlabel('Années')
        axes[0, 1].set_ylabel('Production')
        axes[0, 1].set_title('Croissance de la Production')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Entropie
        axes[1, 0].plot(time, entropy, color='red', linewidth=2)
        axes[1, 0].set_xlabel('Années')
        axes[1, 0].set_ylabel('Entropie')
        axes[1, 0].set_title('Augmentation de l\'Entropie')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Capacité Néguentropique
        axes[1, 1].plot(time, negentropy, color='purple', linewidth=2)
        axes[1, 1].set_xlabel('Années')
        axes[1, 1].set_ylabel('Capacité Néguentropique')
        axes[1, 1].set_title('Déclin de la Capacité à Créer de l\'Ordre')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # Points clés
        print(f"Ressources restantes après {self.years} ans : {resources[-1]:.0f}")
        print(f"Entropie finale : {entropy[-1]:.2f}")
        print(f"Capacité néguentropique finale : {negentropy[-1]:.2f}")

# Exemple
entropy_model = EconomicEntropy(initial_resources=1000, growth_rate=0.05, extraction_rate=0.1, years=50)
entropy_model.plot_entropy()

import numpy as np
import matplotlib.pyplot as plt

class BimetallicSystem:
    """Modélisation d'un système bimétallique (or/argent)"""
    
    def __init__(self, gold_price=1500, silver_price=20, ratio=15, volatility=0.02):
        self.gold_price = gold_price
        self.silver_price = silver_price
        self.ratio = ratio  # Rapport or/argent
        self.volatility = volatility
    
    def simulate_prices(self, days=100):
        """Simule les fluctuations des prix de l'or et de l'argent"""
        time = np.arange(days)
        
        # Simuler les variations avec volatilité
        gold_returns = np.random.normal(0, self.volatility, days)
        silver_returns = np.random.normal(0, self.volatility * 1.5, days)
        
        gold_prices = self.gold_price * np.exp(np.cumsum(gold_returns))
        silver_prices = self.silver_price * np.exp(np.cumsum(silver_returns))
        
        # Rapport réel
        actual_ratio = gold_prices / silver_prices
        
        # Arbitrage (rétablissement du ratio)
        arbitrage_opportunity = (actual_ratio - self.ratio) / self.ratio
        
        return time, gold_prices, silver_prices, actual_ratio, arbitrage_opportunity
    
    def plot_system(self):
        """Visualise le système bimétallique"""
        time, gold_prices, silver_prices, actual_ratio, arbitrage = self.simulate_prices()
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))
        
        # Prix
        ax1.plot(time, gold_prices, label='Or ($/oz)', linewidth=2, color='gold')
        ax1.plot(time, silver_prices, label='Argent ($/oz)', linewidth=2, color='silver')
        ax1.set_xlabel('Jours')
        ax1.set_ylabel('Prix')
        ax1.set_title('Fluctuations des Prix de l\'Or et de l\'Argent')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Ratio
        ax2.plot(time, actual_ratio, label='Ratio réel', linewidth=2, color='blue')
        ax2.axhline(y=self.ratio, color='red', linestyle='--', label=f'Ratio officiel ({self.ratio})')
        ax2.set_xlabel('Jours')
        ax2.set_ylabel('Ratio Or/Argent')
        ax2.set_title('Évolution du Ratio')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Opportunités d'arbitrage
        ax3.plot(time, arbitrage * 100, linewidth=2, color='green')
        ax3.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        ax3.fill_between(time, 0, arbitrage * 100, where=(arbitrage > 0), color='green', alpha=0.3)
        ax3.fill_between(time, 0, arbitrage * 100, where=(arbitrage < 0), color='red', alpha=0.3)
        ax3.set_xlabel('Jours')
        ax3.set_ylabel('Opportunité d\'Arbitrage (%)')
        ax3.set_title('Opportunités d\'Arbitrage')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

# Exemple
bimetallic = BimetallicSystem(gold_price=1500, silver_price=20, ratio=15, volatility=0.02)
bimetallic.plot_system()

