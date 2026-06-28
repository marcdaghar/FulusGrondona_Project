"""
Système Monétaire Bimétallique avec Crypto-Fulus
Auteur: Marc Daghar
Licence: CC BY-SA

Simulation d'un écosystème monétaire basé sur:
- Dinar (Or) et Dirham (Argent) comme réserve de valeur
- Fulus numérique local comme moyen d'échange
- Optimisation efficience-résilience selon les principes de François Roddier
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.integrate import odeint
import networkx as nx
from dataclasses import dataclass
from typing import List, Tuple
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PARTIE 1: THERMODYNAMIQUE ET SYSTÈMES COMPLEXES
# ============================================================================

class ThermodynamicEconomy:
    """
    Classe implémentant les principes thermodynamiques de François Roddier
    pour l'économie monétaire.
    """
    
    def __init__(self):
        self.k_B = 1.380649e-23  # Constante de Boltzmann
        self.T_economic = 300    # Température économique (analogue)
        
    def entropy_boltzmann(self, W: float) -> float:
        """Entropie de Boltzmann: S = k_B * ln(W)"""
        return self.k_B * np.log(W)
    
    def entropy_shannon(self, probabilities: np.ndarray) -> float:
        """Entropie de Shannon: H = -Σ p_i * log(p_i)"""
        return -np.sum(probabilities * np.log(probabilities + 1e-10))
    
    def carnot_efficiency(self, T_hot: float, T_cold: float) -> float:
        """Rendement de Carnot: r = (T_hot - T_cold) / T_hot"""
        return (T_hot - T_cold) / T_hot if T_hot > 0 else 0
    
    def max_entropy_production(self, energy_flow: float, dissipation_rate: float) -> float:
        """
        Principe de Production Maximale d'Entropie (MEP)
        dS/dt = flux_energie * taux_dissipation
        """
        return energy_flow * dissipation_rate


class VanDerWaalsEconomy:
    """
    Équation de Van der Waals appliquée à l'économie.
    Simule la transition de phase entre économie réelle et financière.
    """
    
    def __init__(self, a=0.5, b=0.1, R=1.0):
        self.a = a  # Attraction sociale
        self.b = b  # Volume de production minimal
        self.R = R  # Constante économique
        
    def pressure(self, V: float, T: float) -> float:
        """
        Pression économique (offre/demande)
        (P + a/V²)(V - b) = R*T
        """
        return (self.R * T / (V - self.b)) - (self.a / V**2)
    
    def critical_point(self) -> Tuple[float, float]:
        """Point critique de condensation économique"""
        V_c = 3 * self.b
        T_c = 8 * self.a / (27 * self.R * self.b)
        P_c = self.a / (27 * self.b**2)
        return V_c, T_c, P_c
    
    def phase_transition(self, V: float, T: float) -> str:
        """
        Détermine la phase économique (vapeur/liquide)
        basée sur l'équation de Van der Waals
        """
        V_c, T_c, _ = self.critical_point()
        if T > T_c:
            return "vapeur"  # Économie réelle, producteurs
        else:
            P = self.pressure(V, T)
            P_c = self.a / (27 * self.b**2)
            return "liquide" if P > P_c else "vapeur"  # Économie financière


# ============================================================================
# PARTIE 2: SYSTÈME MONÉTAIRE BIMÉTALLIQUE
# ============================================================================

@dataclass
class MonetaryAgent:
    """Agent économique individuel"""
    id: int
    wealth: float
    labor: float
    consumption: float
    savings_gold: float  # Épargne en or (dinar)
    savings_silver: float  # Épargne en argent (dirham)
    fulus_balance: float  # Monnaie locale (crypto-fulus)
    
    def total_wealth(self, gold_price: float, silver_price: float) -> float:
        """Richesse totale en équivalent or"""
        return (self.savings_gold + 
                self.savings_silver * silver_price / gold_price + 
                self.fulus_balance / gold_price)


class BimetallicSystem:
    """
    Système monétaire bimétallique avec:
    - Dinar (or) et Dirham (argent) comme réserves
    - Fulus numérique comme moyen d'échange local
    """
    
    def __init__(self, num_agents=100, initial_gold_supply=1000, 
                 initial_silver_supply=10000, initial_fulus_supply=100000):
        self.num_agents = num_agents
        self.gold_supply = initial_gold_supply  # Masse de dinar-or
        self.silver_supply = initial_silver_supply  # Masse de dirham-argent
        self.fulus_supply = initial_fulus_supply  # Masse de crypto-fulus
        
        # Taux de change
        self.gold_price = 1.0  # Prix de l'or en unités de compte
        self.silver_price = 0.05  # Prix de l'argent (1/20 de l'or)
        self.exchange_rate = 20.0  # Dirham par Dinar (1:20)
        
        # Agents économiques
        self.agents = self._initialize_agents()
        
        # Paramètres de la loi de Gresham
        self.gresham_factor = 0.8  # Tendance à thésauriser les métaux
    
    def _initialize_agents(self) -> List[MonetaryAgent]:
        """Initialise la distribution de richesse (loi de Pareto)"""
        agents = []
        # Distribution de Pareto pour la richesse (80/20)
        pareto_shape = 1.16
        wealth_dist = np.random.pareto(pareto_shape, self.num_agents)
        wealth_dist = wealth_dist / wealth_dist.sum() * self.gold_supply
        
        for i in range(self.num_agents):
            agent = MonetaryAgent(
                id=i,
                wealth=wealth_dist[i],
                labor=np.random.uniform(0.5, 2.0),
                consumption=np.random.uniform(0.1, 1.0),
                savings_gold=wealth_dist[i] * 0.2,
                savings_silver=wealth_dist[i] * 4.0,
                fulus_balance=wealth_dist[i] * 10.0
            )
            agents.append(agent)
        return agents
    
    def gresham_dynamics(self, velocity_fulus: float, velocity_gold: float) -> float:
        """
        Loi de Gresham: "Le mauvais argent chasse le bon"
        Le fulus (monnaie) circule plus vite que l'or et l'argent
        """
        # Le fulus est préféré si sa vélocité est plus élevée
        return velocity_fulus / (velocity_fulus + velocity_gold)
    
    def fisher_equation(self, M: float, V: float, P: float, Y: float) -> float:
        """
        Équation de Fisher: M * V = P * Y
        """
        return M * V - P * Y
    
    def optimize_efficiency_resilience(self, efficiency: float, resilience: float) -> float:
        """
        Fonction d'optimisation: maximiser D = f(E, R)
        Selon le principe de Roddier: optimiser, pas maximiser
        """
        # Fonction de durabilité: D = E * R / (E + R) (moyenne harmonique)
        return 2 * efficiency * resilience / (efficiency + resilience + 1e-10)
    
    def zakat_calculation(self, wealth: float, nisab: float=85, rate: float=0.025) -> float:
        """
        Calcul de la Zakat sur les métaux précieux
        Nisab: seuil minimum (85g d'or)
        """
        if wealth >= nisab:
            return wealth * rate
        return 0.0
    
    def simulate_transactions(self, steps: int=100, velocity: float=0.1):
        """
        Simule les transactions entre agents dans le système bimétallique
        """
        history = {
            'gold_supply': [],
            'silver_supply': [],
            'fulus_supply': [],
            'total_wealth': [],
            'gini_coefficient': [],
            'efficiency': [],
            'resilience': []
        }
        
        for step in range(steps):
            # Transactions aléatoires entre agents
            for _ in range(self.num_agents * 2):
                i, j = np.random.choice(self.num_agents, 2, replace=False)
                agent_i = self.agents[i]
                agent_j = self.agents[j]
                
                # Transaction en fulus (monnaie locale)
                amount = np.random.exponential(scale=10)
                if agent_i.fulus_balance >= amount:
                    agent_i.fulus_balance -= amount
                    agent_j.fulus_balance += amount
                    
                    # Une partie de la transaction est convertie en or/argent
                    gold_amount = amount * 0.01 * self.gresham_factor
                    if agent_j.savings_gold + gold_amount < self.gold_supply * 0.1:
                        agent_j.savings_gold += gold_amount
                        agent_i.savings_gold -= gold_amount * 0.5
            
            # Vélocité de la monnaie
            total_fulus = sum(a.fulus_balance for a in self.agents)
            velocity_fulus = velocity * (1 + 0.1 * np.sin(step * 0.1))
            
            # Évolution de la masse monétaire
            self.fulus_supply = total_fulus
            
            # Collecte des métriques
            total_wealth = sum(a.total_wealth(self.gold_price, self.silver_price) for a in self.agents)
            
            # Calcul de l'efficience et de la résilience
            efficiency = self._calculate_efficiency()
            resilience = self._calculate_resilience()
            
            history['gold_supply'].append(self.gold_supply)
            history['silver_supply'].append(self.silver_supply)
            history['fulus_supply'].append(total_fulus)
            history['total_wealth'].append(total_wealth)
            history['efficiency'].append(efficiency)
            history['resilience'].append(resilience)
            
            # Coefficient de Gini (inégalité)
            wealths = sorted([a.total_wealth(self.gold_price, self.silver_price) for a in self.agents])
            gini = self._gini_coefficient(wealths)
            history['gini_coefficient'].append(gini)
        
        return history
    
    def _calculate_efficiency(self) -> float:
        """Efficacité du système (simplification et spécialisation)"""
        # Plus les agents sont spécialisés, plus l'efficacité est élevée
        labor_std = np.std([a.labor for a in self.agents])
        return 1.0 / (1.0 + labor_std)
    
    def _calculate_resilience(self) -> float:
        """Résilience du système (diversité des moyens d'échange)"""
        # Diversité des portefeuilles
        gold_ratios = [a.savings_gold / (a.savings_gold + a.fulus_balance + 1e-10) for a in self.agents]
        diversity = 1.0 - np.std(gold_ratios)
        return diversity
    
    def _gini_coefficient(self, wealths: List[float]) -> float:
        """Coefficient de Gini"""
        n = len(wealths)
        if n == 0:
            return 0.0
        wealths = sorted(wealths)
        cumsum = np.cumsum(wealths)
        return (2 * np.sum((np.arange(n) + 1) * wealths) / (n * np.sum(wealths))) - (n + 1) / n


# ============================================================================
# PARTIE 3: MODÉLISATION AVEC NETLOGO (SIMULATION AGENT-BASED)
# ============================================================================

class CryptoFulusModel:
    """
    Modèle agent-based pour le système crypto-fulus
    Inspiré des approches de modélisation avec NetLogo
    """
    
    def __init__(self, grid_size=50, num_agents=200):
        self.grid_size = grid_size
        self.num_agents = num_agents
        self.agents = []
        self.grid = np.zeros((grid_size, grid_size))
        self.time = 0
        
        # Réseau social (topologie de petit monde)
        self.social_network = nx.watts_strogatz_graph(num_agents, 4, 0.3)
        
    def initialize(self):
        """Initialise les agents sur la grille"""
        for i in range(self.num_agents):
            x = np.random.randint(0, self.grid_size)
            y = np.random.randint(0, self.grid_size)
            self.agents.append({
                'id': i,
                'x': x,
                'y': y,
                'fulus': np.random.uniform(10, 100),
                'gold': np.random.uniform(1, 10),
                'silver': np.random.uniform(10, 100),
                'productivity': np.random.uniform(0.5, 1.5),
                'trust': np.random.uniform(0.3, 0.9)
            })
            self.grid[x, y] += 1
    
    def simulate_step(self):
        """Simule un pas de temps du modèle"""
        self.time += 1
        
        for agent in self.agents:
            # Production de richesse
            production = agent['productivity'] * np.random.uniform(0.8, 1.2)
            agent['fulus'] += production
            
            # Échange avec les voisins (interaction locale)
            neighbors = self._get_neighbors(agent)
            for neighbor in neighbors:
                if np.random.random() < agent['trust'] * 0.1:
                    trade_amount = min(agent['fulus'] * 0.05, neighbor['fulus'] * 0.05)
                    agent['fulus'] -= trade_amount
                    neighbor['fulus'] += trade_amount
                    
                    # Conversion partielle en or/argent
                    gold_trade = trade_amount * 0.01
                    if neighbor['gold'] + gold_trade < 20:
                        neighbor['gold'] += gold_trade
                        agent['gold'] -= gold_trade * 0.5
            
            # Zakat (2.5% du surplus)
            if agent['gold'] > 85:  # Nisab
                zakat = agent['gold'] * 0.025
                agent['gold'] -= zakat
                # Zakat redistribuée aux plus pauvres
                poorest = min(self.agents, key=lambda a: a['fulus'])
                poorest['gold'] += zakat / len(self.agents)
        
        # Mise à jour de la grille
        self.grid = np.zeros((self.grid_size, self.grid_size))
        for agent in self.agents:
            self.grid[int(agent['x']), int(agent['y'])] += 1
    
    def _get_neighbors(self, agent):
        """Récupère les voisins dans le réseau social"""
        neighbors_ids = list(self.social_network.neighbors(agent['id']))
        return [self.agents[i] for i in neighbors_ids if i < len(self.agents)]
    
    def get_statistics(self):
        """Retourne les statistiques du système"""
        total_wealth = sum(a['fulus'] + a['gold'] * 20 + a['silver'] for a in self.agents)
        mean_trust = np.mean([a['trust'] for a in self.agents])
        gini = self._gini_coefficient([a['fulus'] + a['gold'] * 20 for a in self.agents])
        
        return {
            'total_wealth': total_wealth,
            'mean_trust': mean_trust,
            'gini_coefficient': gini,
            'num_agents': len(self.agents),
            'time': self.time
        }
    
    def _gini_coefficient(self, values):
        """Coefficient de Gini"""
        n = len(values)
        if n == 0:
            return 0.0
        values_sorted = sorted(values)
        cumsum = np.cumsum(values_sorted)
        return (2 * np.sum((np.arange(n) + 1) * values_sorted) / (n * np.sum(values_sorted))) - (n + 1) / n


# ============================================================================
# PARTIE 4: VISUALISATION ET ANALYSE
# ============================================================================

class MonetaryVisualization:
    """
    Visualisation du système monétaire bimétallique
    """
    
    def __init__(self, system: BimetallicSystem):
        self.system = system
        self.fig = None
        self.axs = None
    
    def plot_efficiency_resilience(self, history: dict):
        """Trace la courbe Efficience vs Résilience"""
        fig, ax = plt.subplots(2, 2, figsize=(12, 10))
        
        # 1. Efficience et Résilience
        ax[0, 0].plot(history['efficiency'], label='Efficience', color='blue')
        ax[0, 0].plot(history['resilience'], label='Résilience', color='green')
        ax[0, 0].axhline(y=0.5, color='red', linestyle='--', label='Optimum')
        ax[0, 0].set_title('Efficience vs Résilience')
        ax[0, 0].set_xlabel('Temps')
        ax[0, 0].set_ylabel('Valeur')
        ax[0, 0].legend()
        ax[0, 0].grid(True, alpha=0.3)
        
        # 2. Masse monétaire
        ax[0, 1].plot(history['gold_supply'], label='Or (Dinar)', color='gold')
        ax[0, 1].plot(history['silver_supply'], label='Argent (Dirham)', color='silver')
        ax[0, 1].plot(history['fulus_supply'], label='Fulus', color='brown')
        ax[0, 1].set_title('Masse Monétaire')
        ax[0, 1].set_xlabel('Temps')
        ax[0, 1].set_ylabel('Quantité')
        ax[0, 1].legend()
        ax[0, 1].grid(True, alpha=0.3)
        
        # 3. Richesse totale et Gini
        ax[1, 0].plot(history['total_wealth'], label='Richesse Totale', color='purple')
        ax[1, 0].set_title('Richesse Totale')
        ax[1, 0].set_xlabel('Temps')
        ax[1, 0].set_ylabel('Valeur')
        ax[1, 0].grid(True, alpha=0.3)
        
        ax[1, 1].plot(history['gini_coefficient'], label='Coefficient de Gini', color='red')
        ax[1, 1].axhline(y=0.4, color='orange', linestyle='--', label='Seuil d\'alerte')
        ax[1, 1].set_title('Inégalité (Gini)')
        ax[1, 1].set_xlabel('Temps')
        ax[1, 1].set_ylabel('Gini')
        ax[1, 1].legend()
        ax[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        return fig
    
    def plot_phase_diagram(self):
        """Trace le diagramme de phase économie réelle vs financière"""
        V = np.linspace(0.1, 2.0, 100)
        vdw = VanDerWaalsEconomy()
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        for T in [0.5, 1.0, 1.5, 2.0]:
            P = vdw.pressure(V, T)
            label = f'T={T}'
            if T > vdw.critical_point()[1]:
                ax.plot(V, P, 'b-', alpha=0.5, label=label)
            else:
                ax.plot(V, P, 'r-', alpha=0.5, label=label)
        
        # Point critique
        V_c, T_c, P_c = vdw.critical_point()
        ax.plot(V_c, P_c, 'go', markersize=10, label='Point Critique')
        
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.2)
        ax.axvline(x=vdw.b, color='black', linestyle='--', alpha=0.3)
        
        ax.set_xlabel('Volume de Production (V)')
        ax.set_ylabel('Pression Économique (P)')
        ax.set_title('Diagramme de Phase Économique (Van der Waals)')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Annotation des phases
        ax.annotate('Phase "Vapeur" (Économie Réelle)', 
                   xy=(0.8, 2), fontsize=10, color='blue')
        ax.annotate('Phase "Liquide" (Économie Financière)', 
                   xy=(1.5, 0.3), fontsize=10, color='red')
        
        plt.tight_layout()
        plt.show()
        return fig
    
    def plot_agent_distribution(self):
        """Trace la distribution de la richesse des agents"""
        wealths = [a.total_wealth(self.system.gold_price, self.system.silver_price) 
                   for a in self.system.agents]
        
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        
        # Histogramme
        ax[0].hist(wealths, bins=30, color='skyblue', edgecolor='black', alpha=0.7)
        ax[0].axvline(np.mean(wealths), color='red', linestyle='--', label='Moyenne')
        ax[0].axvline(np.median(wealths), color='green', linestyle='--', label='Médiane')
        ax[0].set_xlabel('Richesse')
        ax[0].set_ylabel('Fréquence')
        ax[0].set_title('Distribution de la Richesse')
        ax[0].legend()
        
        # Courbe de Lorenz
        wealths_sorted = np.sort(wealths)
        cumsum = np.cumsum(wealths_sorted) / wealths_sorted.sum()
        x = np.arange(len(wealths_sorted)) / len(wealths_sorted)
        
        ax[1].plot(x, cumsum, 'b-', label='Courbe de Lorenz')
        ax[1].plot([0, 1], [0, 1], 'r--', label='Égalité parfaite')
        ax[1].fill_between(x, x, cumsum, alpha=0.3)
        ax[1].set_xlabel('Population cumulée')
        ax[1].set_ylabel('Richesse cumulée')
        ax[1].set_title('Courbe de Lorenz')
        ax[1].legend()
        
        plt.tight_layout()
        plt.show()
        return fig


# ============================================================================
# PARTIE 5: EXÉCUTION ET SIMULATION
# ============================================================================

def run_simulation():
    """
    Exécute la simulation complète du système bimétallique
    """
    print("=" * 60)
    print("SYSTÈME MONÉTAIRE BIMÉTALLIQUE AVEC CRYPTO-FULUS")
    print("Basé sur les travaux de François Roddier")
    print("=" * 60)
    
    # 1. Initialisation du système
    print("\n[1] Initialisation du système bimétallique...")
    system = BimetallicSystem(num_agents=200)
    viz = MonetaryVisualization(system)
    
    # 2. Simulation
    print("[2] Simulation des transactions...")
    history = system.simulate_transactions(steps=200, velocity=0.15)
    
    # 3. Résultats
    print("[3] Résultats de la simulation:")
    print(f"    - Richesse totale finale: {history['total_wealth'][-1]:.2f}")
    print(f"    - Gini final: {history['gini_coefficient'][-1]:.3f}")
    print(f"    - Efficience finale: {history['efficiency'][-1]:.3f}")
    print(f"    - Résilience finale: {history['resilience'][-1]:.3f}")
    
    # 4. Visualisations
    print("\n[4] Génération des visualisations...")
    viz.plot_efficiency_resilience(history)
    viz.plot_phase_diagram()
    viz.plot_agent_distribution()
    
    return system, history


def run_agent_based_model(steps=100):
    """
    Exécute le modèle agent-based (NetLogo-like)
    """
    print("\n" + "=" * 60)
    print("MODÈLE AGENT-BASED CRYPTO-FULUS (NETLOGO)")
    print("=" * 60)
    
    model = CryptoFulusModel(grid_size=30, num_agents=150)
    model.initialize()
    
    statistics = []
    for step in range(steps):
        model.simulate_step()
        stats = model.get_statistics()
        statistics.append(stats)
        
        if step % 20 == 0:
            print(f"Étape {step}: Richesse Totale = {stats['total_wealth']:.2f}, "
                  f"Gini = {stats['gini_coefficient']:.3f}")
    
    # Visualisation des résultats
    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    
    total_wealth = [s['total_wealth'] for s in statistics]
    gini = [s['gini_coefficient'] for s in statistics]
    
    ax[0].plot(total_wealth, color='green')
    ax[0].set_title('Richesse Totale (Modèle Agent-Based)')
    ax[0].set_xlabel('Temps')
    ax[0].set_ylabel('Richesse')
    ax[0].grid(True, alpha=0.3)
    
    ax[1].plot(gini, color='red')
    ax[1].axhline(y=0.4, color='orange', linestyle='--', label='Seuil d\'alerte')
    ax[1].set_title('Coefficient de Gini')
    ax[1].set_xlabel('Temps')
    ax[1].set_ylabel('Gini')
    ax[1].legend()
    ax[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return model, statistics


if __name__ == "__main__":
    # Exécution de la simulation principale
    system, history = run_simulation()
    
    # Exécution du modèle agent-based
    model, stats = run_agent_based_model(steps=200)

