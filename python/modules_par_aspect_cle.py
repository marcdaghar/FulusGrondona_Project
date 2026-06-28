# -*- coding: utf-8 -*-
"""
Modèle Économique et Monétaire - Version Synthétique
Basé sur les formulations mathématiques du modèle.
Inclut : Dette, Spéculation, Complexité, Don, Bimétallisme, Effondrement.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from dataclasses import dataclass
from typing import List, Tuple, Dict
import networkx as nx

# ============================================================================
# 1. MODULE : MONNAIE ET DETTE (Fiction, Pyramide de Ponzi)
# ============================================================================

class MonetarySystem:
    """Modélise le système monétaire post-1971 (fiction, dette, pyramide de Ponzi)."""
    
    def __init__(self, initial_debt: float = 100.0, growth_rate: float = 0.05, 
                 interest_rate: float = 0.03, savings_rate: float = 0.02):
        self.debt = initial_debt
        self.growth_rate = growth_rate  # g_D
        self.interest_rate = interest_rate  # r
        self.savings_rate = savings_rate  # S (proportion du PIB)
        self.history = {'debt': [initial_debt], 'time': [0]}
        
    def debt_dynamics(self, state, t):
        """Équation différentielle de la dette : dD/dt = r*D - S."""
        D = state[0]
        dD_dt = self.interest_rate * D - self.savings_rate * D  # Simplification
        return [dD_dt]
    
    def simulate(self, t_max: float = 50, n_points: int = 1000):
        """Simule l'évolution de la dette dans le temps."""
        t = np.linspace(0, t_max, n_points)
        initial_state = [self.debt]
        solution = odeint(self.debt_dynamics, initial_state, t)
        self.history['debt'] = solution[:, 0]
        self.history['time'] = t
        return self.history
    
    def is_ponzi(self, gdp_growth_rate: float) -> bool:
        """Vérifie si le système est une pyramide de Ponzi (I = g_D - g_Y > 0)."""
        return self.growth_rate > gdp_growth_rate
    
    def time_to_collapse(self, gdp_growth_rate: float) -> float:
        """Estime le temps avant effondrement (approximation)."""
        if self.is_ponzi(gdp_growth_rate):
            # Temps pour que la dette dépasse un seuil critique (ex: 2x PIB)
            # Approximation exponentielle : D(t) = D0 * exp((r - g_Y)*t)
            # On cherche t tel que D(t) = 2 * D0
            excess_growth = self.growth_rate - gdp_growth_rate
            if excess_growth > 0:
                return np.log(2) / excess_growth
        return float('inf')

# ============================================================================
# 2. MODULE : ÉCONOMIE CASINO (Spéculation, Marché comme Arbitre)
# ============================================================================

class CasinoEconomy:
    """Modélise l'économie casino : prix spéculatifs, volatilité, bulles."""
    
    def __init__(self, initial_price: float = 100.0, fundamental_value: float = 80.0,
                 volatility: float = 0.2, speculative_intensity: float = 0.5):
        self.price = initial_price
        self.fundamental_value = fundamental_value
        self.volatility = volatility
        self.speculative_intensity = speculative_intensity
        self.history = {'price': [initial_price], 'time': [0]}
        
    def price_dynamics(self, state, t):
        """Modèle de prix avec composante spéculative."""
        P = state[0]
        # Composante spéculative : bruit aléatoire + retour vers la fondamentale
        noise = np.random.normal(0, self.volatility)
        speculative_component = self.speculative_intensity * noise
        
        # Composante fondamentale : retour vers la valeur fondamentale
        fundamental_component = 0.1 * (self.fundamental_value - P)
        
        dP_dt = fundamental_component + speculative_component
        return [dP_dt]
    
    def simulate(self, t_max: float = 100, n_points: int = 1000):
        """Simule l'évolution des prix."""
        t = np.linspace(0, t_max, n_points)
        initial_state = [self.price]
        # Utilisation de odeint avec une fonction qui inclut le bruit
        # Pour une simulation stochastique, on utilise une approche pas à pas
        dt = t[1] - t[0]
        prices = [self.price]
        for i in range(1, len(t)):
            noise = np.random.normal(0, self.volatility * np.sqrt(dt))
            P = prices[-1]
            dP = (0.1 * (self.fundamental_value - P) + self.speculative_intensity * noise) * dt
            prices.append(P + dP)
        
        self.history['price'] = np.array(prices)
        self.history['time'] = t
        return self.history

# ============================================================================
# 3. MODULE : COMPLEXITÉ ÉCONOMIQUE (Sally Goerner)
# ============================================================================

class ComplexityEconomics:
    """Modélise l'économie comme un système adaptatif complexe."""
    
    def __init__(self, n_agents: int = 100):
        self.n_agents = n_agents
        self.agents = [ComplexAgent() for _ in range(n_agents)]
        self.network = self._build_network()
        
    def _build_network(self) -> nx.Graph:
        """Crée un réseau d'agents (small-world)."""
        G = nx.watts_strogatz_graph(self.n_agents, 4, 0.1)
        return G
    
    def simulate(self, n_steps: int = 100):
        """Simule l'évolution du système complexe."""
        for step in range(n_steps):
            # Chaque agent interagit avec ses voisins
            for agent in self.agents:
                neighbors = list(self.network.neighbors(agent.id))
                if neighbors:
                    # Influence des voisins
                    agent.update(neighbors, self.agents)
            
            # Mise à jour du réseau (adaptation)
            self._update_network()
    
    def _update_network(self):
        """Met à jour le réseau en fonction des interactions."""
        # Exemple : renforcer les liens entre agents qui coopèrent
        pass

class ComplexAgent:
    """Agent dans un système économique complexe."""
    
    def __init__(self, id: int = 0):
        self.id = id
        self.state = np.random.uniform(0, 1)
        self.wealth = np.random.uniform(100, 1000)
        self.trust = np.random.uniform(0, 1)
    
    def update(self, neighbors: List[int], all_agents: List):
        """Met à jour l'état de l'agent en fonction de ses voisins."""
        if neighbors:
            # Influence des voisins sur l'état
            neighbor_states = [all_agents[j].state for j in neighbors]
            self.state = 0.9 * self.state + 0.1 * np.mean(neighbor_states)

# ============================================================================
# 4. MODULE : DON ET DETTE DE VIE (Marcel Mauss)
# ============================================================================

class GiftEconomy:
    """Modélise le cycle du don (donner-recevoir-rendre) vs la dette capitaliste."""
    
    def __init__(self, n_agents: int = 50):
        self.n_agents = n_agents
        self.gifts = np.zeros((n_agents, n_agents))  # Matrice des dons
        self.debts = np.zeros((n_agents, n_agents))  # Matrice des dettes
        self.cycle = {'give': 0, 'receive': 0, 'return': 0}
    
    def gift_cycle(self, giver: int, receiver: int, amount: float):
        """Effectue un don dans le cycle."""
        self.gifts[giver, receiver] += amount
        self.cycle['give'] += amount
        self.cycle['receive'] += amount
        # La dette de vie : obligation de rendre
        self.debts[receiver, giver] += amount * 1.1  # Intérêt symbolique
    
    def capitalist_debt(self, lender: int, borrower: int, amount: float, interest_rate: float = 0.05):
        """Crée une dette capitaliste (isole l'obligation de rendre)."""
        self.debts[borrower, lender] += amount * (1 + interest_rate)
    
    def simulate_cycle(self, n_steps: int = 10):
        """Simule le cycle du don sur plusieurs étapes."""
        for step in range(n_steps):
            # Choisir un donneur et un receveur aléatoires
            giver = np.random.randint(0, self.n_agents)
            receiver = np.random.randint(0, self.n_agents)
            amount = np.random.uniform(10, 100)
            
            # Don
            self.gift_cycle(giver, receiver, amount)
            
            # Rendre (simulé)
            if self.debts[giver, receiver] > 0:
                return_amount = min(self.debts[giver, receiver], amount)
                self.debts[giver, receiver] -= return_amount
                self.cycle['return'] += return_amount

# ============================================================================
# 5. MODULE : BIMÉTALLISME (Or/Argent)
# ============================================================================

class BimetallicSystem:
    """Modélise un système monétaire bimétallique (or + argent)."""
    
    def __init__(self, gold_price: float = 2000.0, silver_price: float = 25.0,
                 gold_weight: float = 0.6, silver_weight: float = 0.4):
        self.gold_price = gold_price  # Prix de l'or (USD/oz)
        self.silver_price = silver_price  # Prix de l'argent (USD/oz)
        self.gold_weight = gold_weight  # Poids de l'or dans la monnaie
        self.silver_weight = silver_weight  # Poids de l'argent
        
        # Vérification : les poids doivent sommer à 1
        assert abs(self.gold_weight + self.silver_weight - 1.0) < 1e-6
    
    def money_value(self) -> float:
        """Calcule la valeur de la monnaie bimétallique."""
        return self.gold_weight * self.gold_price + self.silver_weight * self.silver_price
    
    def update_prices(self, new_gold_price: float, new_silver_price: float):
        """Met à jour les prix des métaux."""
        self.gold_price = new_gold_price
        self.silver_price = new_silver_price
    
    def simulate_price_volatility(self, n_steps: int = 100, volatility: float = 0.02):
        """Simule la volatilité des prix de l'or et de l'argent."""
        prices = []
        for _ in range(n_steps):
            # Random walk
            self.gold_price *= (1 + np.random.normal(0, volatility))
            self.silver_price *= (1 + np.random.normal(0, volatility * 1.5))  # L'argent est plus volatil
            prices.append(self.money_value())
        return prices

# ============================================================================
# 6. MODULE : MODÈLE D'EFFONDREMENT (Club de Rome)
# ============================================================================

class CollapseModel:
    """Modèle de type 'Limits to Growth' (Club de Rome) appliqué localement."""
    
    def __init__(self, population: float = 1000.0, resources: float = 10000.0,
                 production: float = 100.0, pollution: float = 0.0):
        self.population = population  # P
        self.resources = resources  # R
        self.production = production  # Y
        self.pollution = pollution  # Pol
        
        # Paramètres
        self.growth_rate = 0.02  # Taux de croissance de la population
        self.resource_depletion = 0.1  # k
        self.pollution_rate = 0.05  # p
        self.tech_growth = 0.01  # Progrès technique
        
    def dynamics(self, state, t):
        """Équations différentielles du modèle d'effondrement."""
        P, R, Y, Pol = state
        
        # Croissance de la population (limitée par la pollution et les ressources)
        dP_dt = self.growth_rate * P * (1 - Pol / 1000) * (R / 10000)
        
        # Épuisement des ressources
        dR_dt = -self.resource_depletion * Y
        
        # Production (limitée par les ressources et la pollution)
        dY_dt = self.tech_growth * Y - self.pollution_rate * Y * (Pol / 100)
        
        # Accumulation de la pollution
        dPol_dt = self.pollution_rate * Y - 0.01 * Pol  # Décroissance naturelle
        
        return [dP_dt, dR_dt, dY_dt, dPol_dt]
    
    def simulate(self, t_max: float = 100, n_points: int = 1000):
        """Simule l'effondrement du système."""
        t = np.linspace(0, t_max, n_points)
        initial_state = [self.population, self.resources, self.production, self.pollution]
        solution = odeint(self.dynamics, initial_state, t)
        
        return {
            'time': t,
            'population': solution[:, 0],
            'resources': solution[:, 1],
            'production': solution[:, 2],
            'pollution': solution[:, 3]
        }

# ============================================================================
# 7. MODULE : PARTICIPATION ET TROISIÈME VOIE (De Gaulle)
# ============================================================================

class ParticipationModel:
    """Modélise la 'troisième voie' : participation des travailleurs."""
    
    def __init__(self, n_workers: int = 100, capital: float = 10000.0,
                 profits: float = 1000.0, participation_rate: float = 0.3):
        self.n_workers = n_workers
        self.capital = capital
        self.profits = profits
        self.participation_rate = participation_rate  # α : part des bénéfices reversée
        
        # Salaires initiaux
        self.wages = np.ones(n_workers) * (capital / n_workers) * 0.1
        
    def worker_income(self, worker_id: int) -> float:
        """Calcule le revenu d'un travailleur (salaire + participation aux bénéfices)."""
        return self.wages[worker_id] + self.participation_rate * (self.profits / self.n_workers)
    
    def simulate_participation(self, n_steps: int = 50):
        """Simule l'évolution de la participation."""
        history = {'income': [], 'profits': [], 'participation': []}
        
        for step in range(n_steps):
            # Les bénéfices fluctuent
            self.profits *= (1 + np.random.normal(0, 0.05))
            
            # Revenu des travailleurs
            total_income = sum([self.worker_income(i) for i in range(self.n_workers)])
            history['income'].append(total_income)
            history['profits'].append(self.profits)
            history['participation'].append(self.participation_rate * self.profits / self.n_workers)
        
        return history

# ============================================================================
# 8. MODULE : WARFARE ÉCONOMIQUE (Dollar Hegemony)
# ============================================================================

class EconomicWarfare:
    """Modélise la suprématie du dollar imposée par la guerre."""
    
    def __init__(self, us_power: float = 1.0, china_power: float = 0.8,
                 eu_power: float = 0.6, other_power: float = 0.4):
        self.powers = {'US': us_power, 'China': china_power, 'EU': eu_power, 'Other': other_power}
        self.dollar_hegemony = 0.8  # Part du dollar dans les échanges mondiaux
        self.history = {'dollar_share': [self.dollar_hegemony], 'time': [0]}
    
    def warfare_dynamics(self, state, t):
        """Dynamique de la domination monétaire."""
        dollar_share = state[0]
        
        # Forces de dédollarisation (BRI, crypto, etc.)
        dedollarization = 0.01 * (self.powers['China'] + self.powers['Other'])
        
        # Résistance du dollar (soft power, militaire)
        resistance = 0.005 * self.powers['US']
        
        dD_dt = -dedollarization * dollar_share + resistance * (1 - dollar_share)
        return [dD_dt]
    
    def simulate(self, t_max: float = 50, n_points: int = 1000):
        """Simule l'évolution de l'hégémonie du dollar."""
        t = np.linspace(0, t_max, n_points)
        initial_state = [self.dollar_hegemony]
        solution = odeint(self.warfare_dynamics, initial_state, t)
        
        self.history['dollar_share'] = solution[:, 0]
        self.history['time'] = t
        return self.history

# ============================================================================
# 9. MODULE : KAIZEN ET AMÉLIORATION CONTINUE
# ============================================================================

class KaizenModel:
    """Modélise le processus d'amélioration continue (kaizen) dans l'économie."""
    
    def __init__(self, initial_efficiency: float = 0.5, improvement_rate: float = 0.01):
        self.efficiency = initial_efficiency
        self.improvement_rate = improvement_rate
        self.history = {'efficiency': [initial_efficiency], 'time': [0]}
    
    def kaizen_dynamics(self, state, t):
        """Amélioration continue : l'efficacité croît avec le temps."""
        E = state[0]
        # L'amélioration est proportionnelle à l'efficacité (loi de verrouillage)
        dE_dt = self.improvement_rate * E * (1 - E)  # Logistique
        return [dE_dt]
    
    def simulate(self, t_max: float = 100, n_points: int = 1000):
        """Simule l'amélioration continue."""
        t = np.linspace(0, t_max, n_points)
        initial_state = [self.efficiency]
        solution = odeint(self.kaizen_dynamics, initial_state, t)
        
        self.history['efficiency'] = solution[:, 0]
        self.history['time'] = t
        return self.history

# ============================================================================
# 10. VISUALISATION ET ANALYSE
# ============================================================================

def plot_all_models():
    """Visualise tous les modèles dans une figure."""
    fig, axes = plt.subplots(3, 3, figsize=(15, 12))
    
    # 1. Dette (Pyramide de Ponzi)
    monetary = MonetarySystem()
    debt_history = monetary.simulate()
    axes[0, 0].plot(debt_history['time'], debt_history['debt'])
    axes[0, 0].set_title('Dette Mondiale (Pyramide de Ponzi)')
    axes[0, 0].set_xlabel('Temps')
    axes[0, 0].set_ylabel('Dette')
    
    # 2. Économie Casino
    casino = CasinoEconomy()
    price_history = casino.simulate()
    axes[0, 1].plot(price_history['time'], price_history['price'])
    axes[0, 1].axhline(y=casino.fundamental_value, color='r', linestyle='--', label='Valeur Fondamentale')
    axes[0, 1].set_title('Économie Casino (Spéculation)')
    axes[0, 1].set_xlabel('Temps')
    axes[0, 1].set_ylabel('Prix')
    axes[0, 1].legend()
    
    # 3. Bimétallisme
    bimetallic = BimetallicSystem()
    bimetallic_prices = bimetallic.simulate_price_volatility()
    axes[0, 2].plot(bimetallic_prices)
    axes[0, 2].axhline(y=bimetallic.money_value(), color='g', linestyle='--', label='Valeur Initiale')
    axes[0, 2].set_title('Monnaie Bimétallique (Or/Argent)')
    axes[0, 2].set_xlabel('Temps')
    axes[0, 2].set_ylabel('Valeur de la Monnaie')
    axes[0, 2].legend()
    
    # 4. Effondrement (Club de Rome)
    collapse = CollapseModel()
    collapse_history = collapse.simulate()
    axes[1, 0].plot(collapse_history['time'], collapse_history['population'], label='Population')
    axes[1, 0].plot(collapse_history['time'], collapse_history['resources'], label='Ressources')
    axes[1, 0].plot(collapse_history['time'], collapse_history['production'], label='Production')
    axes[1, 0].plot(collapse_history['time'], collapse_history['pollution'], label='Pollution')
    axes[1, 0].set_title('Effondrement (Limits to Growth)')
    axes[1, 0].set_xlabel('Temps')
    axes[1, 0].set_ylabel('Valeur')
    axes[1, 0].legend()
    
    # 5. Participation (De Gaulle)
    participation = ParticipationModel()
    part_history = participation.simulate_participation()
    axes[1, 1].plot(part_history['income'], label='Revenu Total')
    axes[1, 1].plot(part_history['profits'], label='Bénéfices')
    axes[1, 1].set_title('Participation (Troisième Voie)')
    axes[1, 1].set_xlabel('Temps')
    axes[1, 1].set_ylabel('Valeur')
    axes[1, 1].legend()
    
    # 6. Dollar Hegemony (Warfare)
    warfare = EconomicWarfare()
    warfare_history = warfare.simulate()
    axes[1, 2].plot(warfare_history['time'], warfare_history['dollar_share'])
    axes[1, 2].set_title('Hégémonie du Dollar (Warfare)')
    axes[1, 2].set_xlabel('Temps')
    axes[1, 2].set_ylabel('Part du Dollar')
    
    # 7. Kaizen (Amélioration Continue)
    kaizen = KaizenModel()
    kaizen_history = kaizen.simulate()
    axes[2, 0].plot(kaizen_history['time'], kaizen_history['efficiency'])
    axes[2, 0].set_title('Kaizen (Amélioration Continue)')
    axes[2, 0].set_xlabel('Temps')
    axes[2, 0].set_ylabel('Efficacité')
    
    # 8. Cycle du Don (Mauss)
    gift = GiftEconomy(n_agents=20)
    gift.simulate_cycle(n_steps=50)
    axes[2, 1].bar(['Donner', 'Recevoir', 'Rendre'], 
                   [gift.cycle['give'], gift.cycle['receive'], gift.cycle['return']])
    axes[2, 1].set_title('Cycle du Don (Mauss)')
    axes[2, 1].set_ylabel('Montant')
    
    # 9. Complexité (Réseau d'Agents)
    complex_model = ComplexityEconomics(n_agents=50)
    complex_model.simulate(n_steps=50)
    # Visualiser le réseau
    pos = nx.spring_layout(complex_model.network)
    nx.draw(complex_model.network, pos, ax=axes[2, 2], node_size=50, with_labels=False)
    axes[2, 2].set_title('Réseau d\'Agents (Complexité)')
    
    plt.tight_layout()
    plt.show()

# ============================================================================
# 11. EXÉCUTION PRINCIPALE
# ============================================================================

if __name__ == "__main__":
    print("=== MODÈLE ÉCONOMIQUE ET MONÉTAIRE ===")
    print("Visualisation de tous les sous-modèles...")
    plot_all_models()
    print("Visualisation terminée.")
    
    # Exemple d'analyse : temps avant effondrement
    monetary = MonetarySystem(growth_rate=0.05, interest_rate=0.03)
    gdp_growth = 0.02
    print(f"\n--- Analyse de la Dette ---")
    print(f"Le système est-il une pyramide de Ponzi ? {monetary.is_ponzi(gdp_growth)}")
    print(f"Temps estimé avant effondrement : {monetary.time_to_collapse(gdp_growth):.2f} années")
    
    # Exemple d'analyse : bimétallisme
    bimetallic = BimetallicSystem()
    print(f"\n--- Analyse du Bimétallisme ---")
    print(f"Valeur initiale de la monnaie bimétallique : {bimetallic.money_value():.2f}")
    print(f"Volatilité simulée (écart-type) : {np.std(bimetallic.simulate_price_volatility()):.2f}")

Module
Concept
