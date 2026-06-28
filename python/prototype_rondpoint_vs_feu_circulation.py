"""
PROTOTYPE DE SIMULATION MONÉTAIRE - SYSTÈME BIMÉTALLIQUE vs SYSTÈME DE DETTE
Thèse : Refonder l'économie, réformer l'homo economicus
Licence : CC BY-SA
Auteur : Marc Daghar
Description : Simulation de la vélocité monétaire comparant un système bimétallique
(Grondona) à un système de dette centralisée (feu de circulation)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle, Rectangle, FancyBboxPatch
from matplotlib.collections import PatchCollection
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional
import seaborn as sns

# Configuration du style
sns.set_style("darkgrid")
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['legend.fontsize'] = 10

# ============================================================================
# 1. CONSTANTES ET PARAMÈTRES
# ============================================================================

@dataclass
class SimulationConfig:
    """Configuration de la simulation"""
    n_agents: int = 200
    n_steps: int = 500
    initial_money: float = 100.0
    time_window: int = 50  # Fenêtre pour la vélocité
    seed: int = 42

    # Paramètres du système bimétallique (rond-point)
    gold_reserve: float = 1000.0
    silver_reserve: float = 7500.0  # 7.5x plus d'argent
    conversion_threshold: float = 0.1  # Seuil de conversion

    # Paramètres du système de dette (feu de circulation)
    interest_rate: float = 0.05
    reserve_ratio: float = 0.1
    debt_limit: float = 1000.0

# ============================================================================
# 2. AGENTS ÉCONOMIQUES
# ============================================================================

class Agent:
    """Agent économique avec comportement et croyances"""
    
    def __init__(self, agent_id: int, initial_money: float, system_type: str):
        self.id = agent_id
        self.money = initial_money
        self.wealth_history = [initial_money]
        self.debt = 0.0
        self.system_type = system_type
        self.trust_level = 0.8  # Confiance initiale dans la monnaie
        self.cooperation_score = 0.5
        self.transaction_count = 0
        
        # Traits psychologiques (Big Five)
        self.traits = {
            'openness': random.uniform(0.3, 0.9),
            'conscientiousness': random.uniform(0.3, 0.9),
            'extraversion': random.uniform(0.3, 0.9),
            'agreeableness': random.uniform(0.3, 0.9),
            'neuroticism': random.uniform(0.1, 0.7)
        }
        
        # État émotionnel (psychophonie)
        self.emotional_state = {
            'fear': 0.1,
            'trust': 0.8,
            'greed': 0.3,
            'hope': 0.6
        }
    
    def update_trust(self, system_performance: float):
        """Met à jour la confiance basée sur la performance du système"""
        # Confiance augmente avec performance, diminue avec peur
        trust_update = 0.5 * system_performance - 0.3 * self.emotional_state['fear']
        self.trust_level = np.clip(self.trust_level + trust_update * 0.01, 0, 1)
    
    def update_emotions(self, transaction_success: bool, wealth_change: float):
        """Met à jour l'état émotionnel"""
        if transaction_success:
            self.emotional_state['trust'] = min(1, self.emotional_state['trust'] + 0.01)
            self.emotional_state['fear'] = max(0, self.emotional_state['fear'] - 0.01)
        else:
            self.emotional_state['trust'] = max(0, self.emotional_state['trust'] - 0.02)
            self.emotional_state['fear'] = min(1, self.emotional_state['fear'] + 0.03)
        
        # Effet de la richesse sur les émotions
        if wealth_change > 0:
            self.emotional_state['greed'] = min(1, self.emotional_state['greed'] + 0.005)
            self.emotional_state['hope'] = min(1, self.emotional_state['hope'] + 0.01)
        else:
            self.emotional_state['greed'] = max(0, self.emotional_state['greed'] - 0.01)
            self.emotional_state['hope'] = max(0, self.emotional_state['hope'] - 0.01)

# ============================================================================
# 3. SYSTÈME BIMÉTALLIQUE (ROND-POINT)
# ============================================================================

class BimetallicSystem:
    """
    Système monétaire bimétallique basé sur le mécanisme Grondona
    Modèle du rond-point : circulation fluide, auto-régulation
    """
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.gold_reserve = config.gold_reserve
        self.silver_reserve = config.silver_reserve
        self.money_supply = config.initial_money * config.n_agents
        self.price_gold = 50.0  # Prix initial de l'or
        self.price_silver = 5.0   # Prix initial de l'argent
        self.velocity_history = []
        self.transaction_count = 0
        self.blocked_transactions = 0
        self.cooperation_index = 0.5
        
    def compute_velocity(self, transactions: List[float], time_window: int) -> float:
        """Calcule la vélocité monétaire"""
        if len(transactions) < 2:
            return 0.0
        recent = transactions[-time_window:]
        total_value = sum(recent)
        # Vélocité = valeur totale des transactions / masse monétaire
        velocity = total_value / self.money_supply if self.money_supply > 0 else 0
        return min(velocity, 10.0)  # Plafonnement
    
    def adjust_supply(self, market_demand: float):
        """
        Ajustement automatique de la masse monétaire via le mécanisme Grondona
        """
        # Demande de monnaie basée sur les prix des métaux
        gold_demand = market_demand * 0.4
        silver_demand = market_demand * 0.6
        
        # Émission basée sur les réserves
        gold_issued = min(gold_demand, self.gold_reserve / self.price_gold)
        silver_issued = min(silver_demand, self.silver_reserve / self.price_silver)
        
        new_money = gold_issued * self.price_gold + silver_issued * self.price_silver
        
        # Ajustement avec seuil pour éviter les oscillations
        delta = new_money - self.money_supply
        if abs(delta) > self.config.conversion_threshold * self.money_supply:
            self.money_supply += delta * 0.1  # Ajustement graduel
        
        # Mise à jour des prix (mécanisme de marché)
        price_update_gold = 0.01 * (gold_demand - gold_issued) / max(1, self.gold_reserve)
        self.price_gold = max(1, self.price_gold + price_update_gold)
        
        price_update_silver = 0.01 * (silver_demand - silver_issued) / max(1, self.silver_reserve)
        self.price_silver = max(0.1, self.price_silver + price_update_silver)
    
    def process_transaction(self, buyer: Agent, seller: Agent, amount: float) -> bool:
        """
        Traite une transaction dans le système bimétallique
        Retourne True si la transaction est réussie
        """
        # Vérification des fonds
        if buyer.money < amount:
            self.blocked_transactions += 1
            return False
        
        # Coefficient de confiance (affecte la fluidité)
        trust_factor = (buyer.trust_level + seller.trust_level) / 2
        
        # Probabilité de blocage inverse à la confiance
        blockage_prob = 0.1 * (1 - trust_factor)
        
        if random.random() < blockage_prob:
            self.blocked_transactions += 1
            return False
        
        # Transaction réussie
        buyer.money -= amount
        seller.money += amount
        buyer.transaction_count += 1
        seller.transaction_count += 1
        self.transaction_count += 1
        self.cooperation_index = 0.9 * self.cooperation_index + 0.1 * trust_factor
        
        # Ajustement du système
        self.adjust_supply(self.money_supply * 0.01)
        
        return True

# ============================================================================
# 4. SYSTÈME DE DETTE (FEU DE CIRCULATION)
# ============================================================================

class DebtSystem:
    """
    Système monétaire de dette centralisée
    Modèle du feu de circulation : arrêts, blocages, cycles
    """
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.money_supply = config.initial_money * config.n_agents
        self.interest_rate = config.interest_rate
        self.reserve_ratio = config.reserve_ratio
        self.debt_limit = config.debt_limit
        self.total_debt = 0.0
        self.velocity_history = []
        self.transaction_count = 0
        self.blocked_transactions = 0
        self.cycle_phase = 0  # 0=expansion, 1=crunch, 2=recovery
        
    def compute_velocity(self, transactions: List[float], time_window: int) -> float:
        """Calcule la vélocité monétaire"""
        if len(transactions) < 2:
            return 0.0
        recent = transactions[-time_window:]
        total_value = sum(recent)
        velocity = total_value / self.money_supply if self.money_supply > 0 else 0
        return min(velocity, 10.0)  # Plafonnement
    
    def process_transaction(self, buyer: Agent, seller: Agent, amount: float) -> bool:
        """
        Traite une transaction dans le système de dette
        Avec blocages périodiques (feu de circulation)
        """
        # Mise à jour du cycle (feu de circulation)
        self.cycle_phase = (self.cycle_phase + 0.01) % 3
        
        # Vérification des fonds
        if buyer.money < amount:
            # Tentative de crédit
            if buyer.debt < self.debt_limit * buyer.traits['conscientiousness']:
                credit = amount - buyer.money
                buyer.debt += credit * (1 + self.interest_rate)
                self.total_debt += credit
                buyer.money += credit
            else:
                self.blocked_transactions += 1
                return False
        
        # Blocage cyclique (feu rouge)
        if self.cycle_phase < 0.8:  # Période de blocage
            self.blocked_transactions += 1
            return False
        
        # Transaction réussie
        buyer.money -= amount
        seller.money += amount
        buyer.transaction_count += 1
        seller.transaction_count += 1
        self.transaction_count += 1
        
        # Accumulation de dette (effet de levier)
        if buyer.debt > 0:
            buyer.debt *= (1 + self.interest_rate * 0.01)
        
        return True

# ============================================================================
# 5. SIMULATION PRINCIPALE
# ============================================================================

class MonetarySimulation:
    """Simulation complète comparant les deux systèmes"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.bimetallic_system = BimetallicSystem(config)
        self.debt_system = DebtSystem(config)
        
        # Agents pour chaque système
        self.bimetallic_agents = [
            Agent(i, config.initial_money, 'bimetallic') 
            for i in range(config.n_agents)
        ]
        self.debt_agents = [
            Agent(i, config.initial_money, 'debt') 
            for i in range(config.n_agents)
        ]
        
        # Historiques
        self.bimetallic_history = {
            'velocities': [],
            'gini': [],
            'trust': [],
            'transactions': [],
            'cooperation': [],
            'blocked_ratio': []
        }
        self.debt_history = {
            'velocities': [],
            'gini': [],
            'trust': [],
            'transactions': [],
            'cooperation': [],
            'blocked_ratio': []
        }
        
        # Suivi des transactions pour la vélocité
        self.bimetallic_transactions = []
        self.debt_transactions = []
        
    def compute_gini(self, agents: List[Agent]) -> float:
        """Calcule l'indice de Gini (inégalité)"""
        wealths = sorted([a.money for a in agents])
        n = len(wealths)
        if n == 0 or sum(wealths) == 0:
            return 0.0
        cumsum = np.cumsum(wealths)
        return (2 * np.sum(cumsum) - (n + 1) * np.sum(wealths)) / (n * np.sum(wealths))
    
    def compute_average_trust(self, agents: List[Agent]) -> float:
        """Calcule la confiance moyenne"""
        return np.mean([a.trust_level for a in agents])
    
    def compute_average_cooperation(self, agents: List[Agent]) -> float:
        """Calcule le score de coopération moyen"""
        return np.mean([a.cooperation_score for a in agents])
    
    def step(self, step_num: int):
        """Effectue une étape de simulation"""
        
        # --- Système bimétallique ---
        for i in range(len(self.bimetallic_agents)):
            # Sélection aléatoire d'une paire
            buyer_idx = random.randint(0, len(self.bimetallic_agents) - 1)
            seller_idx = random.randint(0, len(self.bimetallic_agents) - 1)
            while seller_idx == buyer_idx:
                seller_idx = random.randint(0, len(self.bimetallic_agents) - 1)
            
            buyer = self.bimetallic_agents[buyer_idx]
            seller = self.bimetallic_agents[seller_idx]
            
            amount = min(
                buyer.money * random.uniform(0.01, 0.2),
                seller.money * 0.5 + 10
            )
            
            if amount > 0:
                success = self.bimetallic_system.process_transaction(buyer, seller, amount)
                wealth_change = -amount if success else 0
                buyer.update_emotions(success, wealth_change)
                seller.update_emotions(success, amount if success else 0)
                
                if success:
                    self.bimetallic_transactions.append(amount)
                    # Mise à jour de la coopération
                    buyer.cooperation_score = min(1, buyer.cooperation_score + 0.01)
                    seller.cooperation_score = min(1, seller.cooperation_score + 0.01)
        
        # Mise à jour de la confiance basée sur la performance
        if len(self.bimetallic_transactions) > 0:
            recent_success_rate = 1 - self.bimetallic_system.blocked_transactions / max(1, self.bimetallic_system.transaction_count)
            for agent in self.bimetallic_agents:
                agent.update_trust(recent_success_rate)
        
        # Calcul des métriques bimétalliques
        self.bimetallic_history['velocities'].append(
            self.bimetallic_system.compute_velocity(self.bimetallic_transactions, self.config.time_window)
        )
        self.bimetallic_history['gini'].append(
            self.compute_gini(self.bimetallic_agents)
        )
        self.bimetallic_history['trust'].append(
            self.compute_average_trust(self.bimetallic_agents)
        )
        self.bimetallic_history['cooperation'].append(
            self.compute_average_cooperation(self.bimetallic_agents)
        )
        self.bimetallic_history['transactions'].append(
            self.bimetallic_system.transaction_count
        )
        self.bimetallic_history['blocked_ratio'].append(
            self.bimetallic_system.blocked_transactions / max(1, self.bimetallic_system.transaction_count)
        )
        
        # --- Système de dette ---
        for i in range(len(self.debt_agents)):
            buyer_idx = random.randint(0, len(self.debt_agents) - 1)
            seller_idx = random.randint(0, len(self.debt_agents) - 1)
            while seller_idx == buyer_idx:
                seller_idx = random.randint(0, len(self.debt_agents) - 1)
            
            buyer = self.debt_agents[buyer_idx]
            seller = self.debt_agents[seller_idx]
            
            amount = min(
                buyer.money * random.uniform(0.01, 0.2),
                seller.money * 0.5 + 10
            )
            
            if amount > 0:
                success = self.debt_system.process_transaction(buyer, seller, amount)
                wealth_change = -amount if success else 0
                buyer.update_emotions(success, wealth_change)
                seller.update_emotions(success, amount if success else 0)
                
                if success:
                    self.debt_transactions.append(amount)
        
        # Mise à jour de la confiance (système de dette - confiance érodée)
        if len(self.debt_transactions) > 0:
            recent_success_rate = 1 - self.debt_system.blocked_transactions / max(1, self.debt_system.transaction_count)
            for agent in self.debt_agents:
                agent.update_trust(recent_success_rate * 0.8)  # Confiance plus fragile
        
        # Calcul des métriques du système de dette
        self.debt_history['velocities'].append(
            self.debt_system.compute_velocity(self.debt_transactions, self.config.time_window)
        )
        self.debt_history['gini'].append(
            self.compute_gini(self.debt_agents)
        )
        self.debt_history['trust'].append(
            self.compute_average_trust(self.debt_agents)
        )
        self.debt_history['cooperation'].append(
            self.compute_average_cooperation(self.debt_agents)
        )
        self.debt_history['transactions'].append(
            self.debt_system.transaction_count
        )
        self.debt_history['blocked_ratio'].append(
            self.debt_system.blocked_transactions / max(1, self.debt_system.transaction_count)
        )
    
    def run(self) -> dict:
        """Exécute la simulation complète"""
        for step in range(self.config.n_steps):
            self.step(step)
            
            # Affichage de progression
            if step % 50 == 0:
                print(f"Step {step}/{self.config.n_steps}")
        
        return {
            'bimetallic': self.bimetallic_history,
            'debt': self.debt_history
        }

# ============================================================================
# 6. VISUALISATION
# ============================================================================

class SimulationVisualizer:
    """Visualisation avancée de la simulation"""
    
    def __init__(self, results: dict, config: SimulationConfig):
        self.results = results
        self.config = config
        self.fig = None
        self.axes = None
        
    def create_figure(self):
        """Crée la figure avec plusieurs sous-graphiques"""
        self.fig, self.axes = plt.subplots(2, 3, figsize=(16, 10))
        self.fig.suptitle('Simulation Monétaire : Bimétallisme vs Système de Dette', 
                         fontsize=16, fontweight='bold')
        return self.fig, self.axes
    
    def plot_all(self):
        """Affiche tous les graphiques"""
        fig, axes = self.create_figure()
        
        # 1. Vélocité monétaire
        ax1 = axes[0, 0]
        ax1.plot(self.results['bimetallic']['velocities'], 
                label='Bimétallique (Rond-point)', color='green', linewidth=2)
        ax1.plot(self.results['debt']['velocities'], 
                label='Dette (Feu de circulation)', color='red', linewidth=2, alpha=0.7)
        ax1.set_title('Vélocité monétaire')
        ax1.set_xlabel('Étapes')
        ax1.set_ylabel('Vélocité')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Indice de Gini (inégalité)
        ax2 = axes[0, 1]
        ax2.plot(self.results['bimetallic']['gini'], 
                label='Bimétallique', color='green', linewidth=2)
        ax2.plot(self.results['debt']['gini'], 
                label='Dette', color='red', linewidth=2, alpha=0.7)
        ax2.set_title('Indice de Gini (inégalité)')
        ax2.set_xlabel('Étapes')
        ax2.set_ylabel('Gini')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Confiance moyenne
        ax3 = axes[0, 2]
        ax3.plot(self.results['bimetallic']['trust'], 
                label='Bimétallique', color='green', linewidth=2)
        ax3.plot(self.results['debt']['trust'], 
                label='Dette', color='red', linewidth=2, alpha=0.7)
        ax3.set_title('Confiance moyenne')
        ax3.set_xlabel('Étapes')
        ax3.set_ylabel('Confiance')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_ylim(0, 1)
        
        # 4. Coopération moyenne
        ax4 = axes[1, 0]
        ax4.plot(self.results['bimetallic']['cooperation'], 
                label='Bimétallique', color='green', linewidth=2)
        ax4.plot(self.results['debt']['cooperation'], 
                label='Dette', color='red', linewidth=2, alpha=0.7)
        ax4.set_title('Coopération moyenne')
        ax4.set_xlabel('Étapes')
        ax4.set_ylabel('Coopération')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim(0, 1)
        
        # 5. Transactions cumulées
        ax5 = axes[1, 1]
        ax5.plot(self.results['bimetallic']['transactions'], 
                label='Bimétallique', color='green', linewidth=2)
        ax5.plot(self.results['debt']['transactions'], 
                label='Dette', color='red', linewidth=2, alpha=0.7)
        ax5.set_title('Transactions cumulées')
        ax5.set_xlabel('Étapes')
        ax5.set_ylabel('Nombre de transactions')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
        
        # 6. Taux de blocage
        ax6 = axes[1, 2]
        ax6.plot(self.results['bimetallic']['blocked_ratio'], 
                label='Bimétallique', color='green', linewidth=2)
        ax6.plot(self.results['debt']['blocked_ratio'], 
                label='Dette', color='red', linewidth=2, alpha=0.7)
        ax6.set_title('Taux de transactions bloquées')
        ax6.set_xlabel('Étapes')
        ax6.set_ylabel('Taux de blocage')
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_velocity_comparison(self):
        """Graphique spécifique de comparaison des vélocités"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        b_v = self.results['bimetallic']['velocities']
        d_v = self.results['debt']['velocities']
        
        # Moyennes et écarts-types
        b_mean = np.mean(b_v)
        d_mean = np.mean(d_v)
        b_std = np.std(b_v)
        d_std = np.std(d_v)
        
        # Graphique principal
        ax.plot(b_v, label=f'Bimétallique (μ={b_mean:.2f}, σ={b_std:.2f})', 
                color='green', linewidth=2)
        ax.plot(d_v, label=f'Dette (μ={d_mean:.2f}, σ={d_std:.2f})', 
                color='red', linewidth=2, alpha=0.7)
        
        # Bandes de confiance
        ax.fill_between(range(len(b_v)), 
                       b_mean - b_std, b_mean + b_std, 
                       color='green', alpha=0.1)
        ax.fill_between(range(len(d_v)), 
                       d_mean - d_std, d_mean + d_std, 
                       color='red', alpha=0.1)
        
        ax.axhline(y=b_mean, color='green', linestyle='--', alpha=0.5)
        ax.axhline(y=d_mean, color='red', linestyle='--', alpha=0.5)
        
        ax.set_title('Comparaison de la Vélocité Monétaire\nRond-point (Bimétallique) vs Feu de circulation (Dette)',
                    fontsize=14)
        ax.set_xlabel('Étapes de simulation')
        ax.set_ylabel('Vélocité monétaire')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Annotation des résultats
        improvement = (b_mean - d_mean) / d_mean * 100
        ax.text(0.02, 0.95, 
                f'Amélioration : {improvement:.1f}%', 
                transform=ax.transAxes,
                fontsize=12,
                bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    def plot_phase_diagram(self):
        """Diagramme de phase : confiance vs vélocité"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Système bimétallique
        ax.scatter(self.results['bimetallic']['trust'], 
                  self.results['bimetallic']['velocities'],
                  label='Bimétallique', color='green', alpha=0.5, s=20)
        
        # Système de dette
        ax.scatter(self.results['debt']['trust'], 
                  self.results['debt']['velocities'],
                  label='Dette', color='red', alpha=0.5, s=20)
        
        # Tracés de régression
        z_b = np.polyfit(self.results['bimetallic']['trust'], 
                        self.results['bimetallic']['velocities'], 1)
        p_b = np.poly1d(z_b)
        x_b = np.linspace(0, 1, 100)
        ax.plot(x_b, p_b(x_b), color='green', linestyle='--', alpha=0.5)
        
        z_d = np.polyfit(self.results['debt']['trust'], 
                        self.results['debt']['velocities'], 1)
        p_d = np.poly1d(z_d)
        x_d = np.linspace(0, 1, 100)
        ax.plot(x_d, p_d(x_d), color='red', linestyle='--', alpha=0.5)
        
        ax.set_title('Diagramme de Phase : Confiance vs Vélocité')
        ax.set_xlabel('Confiance moyenne')
        ax.set_ylabel('Vélocité monétaire')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig

# ============================================================================
# 7. EXPORT DES DONNÉES
# ============================================================================

def export_results(results: dict, filename: str = 'simulation_results.npz'):
    """Exporte les résultats dans un fichier compressé"""
    np.savez_compressed(filename, **{
        'bimetallic_velocities': results['bimetallic']['velocities'],
        'bimetallic_gini': results['bimetallic']['gini'],
        'bimetallic_trust': results['bimetallic']['trust'],
        'bimetallic_cooperation': results['bimetallic']['cooperation'],
        'bimetallic_transactions': results['bimetallic']['transactions'],
        'bimetallic_blocked_ratio': results['bimetallic']['blocked_ratio'],
        'debt_velocities': results['debt']['velocities'],
        'debt_gini': results['debt']['gini'],
        'debt_trust': results['debt']['trust'],
        'debt_cooperation': results['debt']['cooperation'],
        'debt_transactions': results['debt']['transactions'],
        'debt_blocked_ratio': results['debt']['blocked_ratio']
    })
    print(f"Résultats exportés dans {filename}")

# ============================================================================
# 8. EXÉCUTION PRINCIPALE
# ============================================================================

def main():
    """Fonction principale d'exécution"""
    print("=" * 60)
    print("PROTOTYPE DE SIMULATION MONÉTAIRE")
    print("Système Bimétallique (Rond-point) vs Système de Dette (Feu de circulation)")
    print("=" * 60)
    
    # Configuration
    config = SimulationConfig(
        n_agents=200,
        n_steps=500,
        initial_money=100.0,
        time_window=50
    )
    
    print(f"\nConfiguration:")
    print(f"  - {config.n_agents} agents")
    print(f"  - {config.n_steps} étapes")
    print(f"  - Masse monétaire initiale : {config.initial_money:.0f}")
    print(f"  - Réserves d'or : {config.gold_reserve:.0f}")
    print(f"  - Réserves d'argent : {config.silver_reserve:.0f}")
    print(f"  - Taux d'intérêt : {config.interest_rate*100:.0f}%")
    print()
    
    # Exécution de la simulation
    print("Lancement de la simulation...")
    sim = MonetarySimulation(config)
    results = sim.run()
    print("Simulation terminée !")
    
    # Export des résultats
    export_results(results)
    
    # Visualisation
    print("\nGénération des graphiques...")
    vis = SimulationVisualizer(results, config)
    
    # Graphique principal
    fig1 = vis.plot_all()
    fig1.savefig('simulation_complete.png', dpi=150, bbox_inches='tight')
    print("  - simulation_complete.png")
    
    # Comparaison des vélocités
    fig2 = vis.plot_velocity_comparison()
    fig2.savefig('velocity_comparison.png', dpi=150, bbox_inches='tight')
    print("  - velocity_comparison.png")
    
    # Diagramme de phase
    fig3 = vis.plot_phase_diagram()
    fig3.savefig('phase_diagram.png', dpi=150, bbox_inches='tight')
    print("  - phase_diagram.png")
    
    # Résumé statistique
    print("\n" + "=" * 60)
    print("RÉSULTATS STATISTIQUES")
    print("=" * 60)
    
    b_v = results['bimetallic']['velocities']
    d_v = results['debt']['velocities']
    
    print(f"\nSystème BIMÉTALLIQUE (Rond-point):")
    print(f"  - Vélocité moyenne : {np.mean(b_v):.3f}")
    print(f"  - Vélocité écart-type : {np.std(b_v):.3f}")
    print(f"  - Gini moyen : {np.mean(results['bimetallic']['gini']):.3f}")
    print(f"  - Confiance moyenne : {np.mean(results['bimetallic']['trust']):.3f}")
    print(f"  - Coopération moyenne : {np.mean(results['bimetallic']['cooperation']):.3f}")
    print(f"  - Taux de blocage moyen : {np.mean(results['bimetallic']['blocked_ratio']):.3f}")
    
    print(f"\nSystème de DETTE (Feu de circulation):")
    print(f"  - Vélocité moyenne : {np.mean(d_v):.3f}")
    print(f"  - Vélocité écart-type : {np.std(d_v):.3f}")
    print(f"  - Gini moyen : {np.mean(results['debt']['gini']):.3f}")
    print(f"  - Confiance moyenne : {np.mean(results['debt']['trust']):.3f}")
    print(f"  - Coopération moyenne : {np.mean(results['debt']['cooperation']):.3f}")
    print(f"  - Taux de blocage moyen : {np.mean(results['debt']['blocked_ratio']):.3f}")
    
    improvement = (np.mean(b_v) - np.mean(d_v)) / np.mean(d_v) * 100
    print(f"\nAMÉLIORATION DU SYSTÈME BIMÉTALLIQUE:")
    print(f"  - Vélocité : +{improvement:.1f}%")
    
    print("\n" + "=" * 60)
    print("Simulation terminée avec succès !")
    print("=" * 60)
    
    plt.show()
    
    return results

if __name__ == "__main__":
    main()
