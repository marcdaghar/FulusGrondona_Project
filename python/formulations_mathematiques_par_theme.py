import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class FisherModel:
    """Modèle de l'équation de Fisher M × V = P × Y"""
    money_supply: float  # M
    velocity: float      # V
    price_level: float   # P
    real_output: float   # Y
    
    @property
    def nominal_gdp(self) -> float:
        """Calcul du PIB nominal = M × V"""
        return self.money_supply * self.velocity
    
    @property
    def calculated_price(self) -> float:
        """Calcul du niveau des prix = (M × V) / Y"""
        return self.nominal_gdp / self.real_output
    
    def simulate_velocity_impact(self, velocities: np.ndarray) -> np.ndarray:
        """Simule l'impact de la vitesse de circulation"""
        return velocities * self.money_supply
    
    def evaluate_efficiency(self) -> float:
        """Évalue l'efficacité monétaire"""
        return self.velocity / self.money_supply

# Exemple d'utilisation
fisher = FisherModel(
    money_supply=1000,
    velocity=5,
    price_level=2,
    real_output=2500
)

print(f"PIB nominal: {fisher.nominal_gdp}")
print(f"Prix calculé: {fisher.calculated_price}")
print(f"Efficacité: {fisher.evaluate_efficiency()}")
import numpy as np
import pandas as pd

class ChequeSimulation:
    """Simulation de l'histoire du chèque sans provision"""
    
    def __init__(self, cheque_amount: float, num_merchants: int, margin: float):
        self.cheque_amount = cheque_amount
        self.num_merchants = num_merchants
        self.margin = margin
        self.merchants = []
    
    def simulate_transactions(self) -> pd.DataFrame:
        """Simule la circulation du chèque"""
        data = []
        cumulative_transactions = 0
        cumulative_profits = 0
        
        for i in range(self.num_merchants):
            transaction = self.cheque_amount
            profit = transaction * self.margin
            cumulative_transactions += transaction
            cumulative_profits += profit
            
            data.append({
                'Merchant': i + 1,
                'Transaction': transaction,
                'Profit': profit,
                'Cumulative_Transactions': cumulative_transactions,
                'Cumulative_Profits': cumulative_profits
            })
        
        return pd.DataFrame(data)
    
    def calculate_final_impact(self) -> dict:
        """Calcule l'impact final quand le chèque est rejeté"""
        df = self.simulate_transactions()
        total_transactions = df['Cumulative_Transactions'].iloc[-1]
        total_profits = df['Cumulative_Profits'].iloc[-1]
        
        # Perte partagée
        loss_per_merchant = self.cheque_amount / self.num_merchants
        net_profit_per_merchant = (total_profits / self.num_merchants) - loss_per_merchant
        
        return {
            'total_transactions': total_transactions,
            'total_profits': total_profits,
            'loss_per_merchant': loss_per_merchant,
            'net_profit_per_merchant': net_profit_per_merchant,
            'net_profit_total': net_profit_per_merchant * self.num_merchants
        }

# Exemple d'utilisation
sim = ChequeSimulation(
    cheque_amount=1000,
    num_merchants=10,
    margin=0.25
)

print("Simulation du chèque sans provision:")
print(sim.simulate_transactions())
print("\nImpact final:")
print(sim.calculate_final_impact())
import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

class DissipativeStructure:
    """Modèle de structure dissipative (système auto-organisé)"""
    
    def __init__(self, a: float, b: float, c: float):
        self.a = a  # Paramètre de forçage
        self.b = b  # Paramètre de dissipation
        self.c = c  # Paramètre de couplage
    
    def system(self, state: np.ndarray, t: float) -> np.ndarray:
        """Système d'équations différentielles pour une structure dissipative"""
        x, y, z = state
        
        dx = self.a * (y - x)
        dy = x * (self.b - z) - y
        dz = x * y - self.c * z
        
        return np.array([dx, dy, dz])
    
    def simulate(self, initial_state: np.ndarray, t_span: np.ndarray) -> np.ndarray:
        """Simule l'évolution du système"""
        return odeint(self.system, initial_state, t_span)
    
    def compute_entropy(self, state: np.ndarray) -> float:
        """Calcule l'entropie du système (approximée)"""
        # Utilisation de l'énergie cinétique comme proxy
        kinetic = 0.5 * np.sum(state**2)
        return -np.log(kinetic + 1e-10) if kinetic > 0 else 0

# Exemple d'utilisation
dissipative = DissipativeStructure(a=10, b=28, c=8/3)
t = np.linspace(0, 50, 5000)
initial = np.array([1, 1, 1])

trajectory = dissipative.simulate(initial, t)
entropy = [dissipative.compute_entropy(state) for state in trajectory]

print("Structure dissipative simulée")
print(f"Entropie initiale: {entropy[0]}")
print(f"Entropie finale: {entropy[-1]}")
import numpy as np
from scipy.optimize import minimize

class ViabilityOptimizer:
    """Optimiseur de viabilité (optimisation vs maximisation)"""
    
    def __init__(self):
        self.resource_limit = 100
        self.sustainability_threshold = 0.3
    
    def economic_function(self, x: np.ndarray) -> float:
        """Fonction économique à optimiser"""
        return -x[0] * x[1] * np.exp(-x[0] / self.resource_limit)
    
    def viability_constraint(self, x: np.ndarray) -> float:
        """Contrainte de viabilité écologique"""
        return self.sustainability_threshold - np.sum(x) / self.resource_limit
    
    def find_optimum(self, initial_guess: np.ndarray) -> dict:
        """Trouve l'optimum avec contrainte de viabilité"""
        constraints = [{'type': 'ineq', 'fun': self.viability_constraint}]
        bounds = [(0, self.resource_limit), (0, self.resource_limit)]
        
        result = minimize(
            self.economic_function,
            initial_guess,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        return {
            'x_opt': result.x,
            'optimal_value': -result.fun,
            'sustainability': np.sum(result.x) / self.resource_limit
        }
    
    def compare_strategies(self) -> pd.DataFrame:
        """Compare la stratégie de maximisation vs optimisation"""
        # Stratégie de maximisation (sans contrainte)
        max_guess = np.array([self.resource_limit/2, self.resource_limit/2])
        max_result = minimize(
            self.economic_function,
            max_guess,
            method='SLSQP',
            bounds=[(0, self.resource_limit), (0, self.resource_limit)]
        )
        
        # Stratégie d'optimisation (avec contrainte de viabilité)
        opt_result = self.find_optimum(max_guess)
        
        return pd.DataFrame({
            'Strategie': ['Maximisation', 'Optimisation'],
            'Valeur': [-self.economic_function(max_result.x), opt_result['optimal_value']],
            'Durabilité': [np.sum(max_result.x)/self.resource_limit, opt_result['sustainability']]
        })

# Exemple d'utilisation
optimizer = ViabilityOptimizer()
print("Comparaison des stratégies:")
print(optimizer.compare_strategies())
import numpy as np
import random
from typing import List, Tuple, Dict

class MonetaryGeneticAlgorithm:
    """Algorithme génétique pour optimiser les paramètres monétaires"""
    
    def __init__(self, population_size: int = 100, generations: int = 100):
        self.population_size = population_size
        self.generations = generations
        self.population = []
        
    def initialize_population(self, param_bounds: List[Tuple[float, float]]) -> None:
        """Initialise la population aléatoirement"""
        self.population = [
            [random.uniform(low, high) for low, high in param_bounds]
            for _ in range(self.population_size)
        ]
        self.param_bounds = param_bounds
    
    def fitness_function(self, params: List[float]) -> float:
        """Fonction de fitness pour le système monétaire"""
        # Paramètres: [money_supply, velocity, interest_rate, inflation_target]
        m, v, r, i = params
        
        # Objectifs conflictuels
        economic_activity = m * v  # Plus est mieux
        stability = 1 / (1 + abs(r - i))  # Proche de l'objectif
        sustainability = 1 / (1 + v)  # Vitesse modérée
        
        # Pondération
        return 0.5 * economic_activity + 0.3 * stability + 0.2 * sustainability
    
    def selection(self) -> List[List[float]]:
        """Sélection par tournoi"""
        selected = []
        for _ in range(self.population_size):
            tournament = random.sample(self.population, 3)
            winner = max(tournament, key=self.fitness_function)
            selected.append(winner)
        return selected
    
    def crossover(self, parent1: List[float], parent2: List[float]) -> Tuple[List[float], List[float]]:
        """Croisement uniforme"""
        child1, child2 = [], []
        for p1, p2 in zip(parent1, parent2):
            if random.random() < 0.5:
                child1.append(p1)
                child2.append(p2)
            else:
                child1.append(p2)
                child2.append(p1)
        return child1, child2
    
    def mutation(self, individual: List[float], mutation_rate: float = 0.1) -> List[float]:
        """Mutation adaptative"""
        mutated = []
        for i, gene in enumerate(individual):
            if random.random() < mutation_rate:
                low, high = self.param_bounds[i]
                mutated.append(gene + random.gauss(0, 0.1 * (high - low)))
            else:
                mutated.append(gene)
        return mutated
    
    def evolve(self) -> Dict:
        """Exécute l'algorithme génétique"""
        best_fitness_history = []
        
        for generation in range(self.generations):
            # Évaluation
            fitness_values = [self.fitness_function(ind) for ind in self.population]
            best_idx = np.argmax(fitness_values)
            best_fitness_history.append(fitness_values[best_idx])
            
            # Sélection
            selected = self.selection()
            
            # Croisement et mutation
            new_population = []
            for i in range(0, self.population_size, 2):
                if i + 1 < self.population_size:
                    child1, child2 = self.crossover(selected[i], selected[i+1])
                    child1 = self.mutation(child1)
                    child2 = self.mutation(child2)
                    new_population.extend([child1, child2])
                else:
                    new_population.append(selected[i])
            
            self.population = new_population
        
        best_fitness = max(fitness_values)
        best_individual = self.population[best_idx]
        
        return {
            'best_parameters': best_individual,
            'best_fitness': best_fitness,
            'fitness_history': best_fitness_history
        }

# Exemple d'utilisation
ga = MonetaryGeneticAlgorithm(population_size=50, generations=100)
bounds = [(0, 100), (0, 10), (0, 0.2), (0, 0.15)]  # bornes des paramètres
ga.initialize_population(bounds)

result = ga.evolve()
print("Résultats de l'optimisation génétique:")
print(f"Meilleurs paramètres: {result['best_parameters']}")
print(f"Fitness: {result['best_fitness']}")
import numpy as np
from scipy.signal import convolve2d

class MonetaryCellularAutomaton:
    """Automate cellulaire pour modéliser la diffusion monétaire"""
    
    def __init__(self, grid_size: int = 50):
        self.grid_size = grid_size
        self.grid = np.zeros((grid_size, grid_size))
        self.wealth_grid = np.zeros((grid_size, grid_size))
        
    def initialize_with_pattern(self, pattern: np.ndarray) -> None:
        """Initialise avec un motif spécifique"""
        size = min(pattern.shape[0], self.grid_size)
        self.grid[:size, :size] = pattern[:size, :size]
    
    def initialize_random(self, density: float = 0.1) -> None:
        """Initialise aléatoirement"""
        self.grid = np.random.random((self.grid_size, self.grid_size)) < density
        self.wealth_grid = np.random.exponential(scale=10, size=(self.grid_size, self.grid_size))
    
    def neighbor_sum(self) -> np.ndarray:
        """Calcule la somme des voisins"""
        kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
        return convolve2d(self.grid.astype(float), kernel, mode='same', boundary='wrap')
    
    def wealth_diffusion(self) -> np.ndarray:
        """Simule la diffusion de richesse"""
        return convolve2d(self.wealth_grid, np.ones((3,3))/9, mode='same', boundary='wrap')
    
    def step(self, survival_threshold: int = 2, birth_threshold: int = 3) -> None:
        """Étappe d'évolution de l'automate"""
        neighbors = self.neighbor_sum()
        alive = self.grid == 1
        
        # Règles du jeu de la vie modifiées
        survive = alive & ((neighbors >= survival_threshold) & (neighbors <= 3))
        birth = ~alive & (neighbors == birth_threshold)
        
        self.grid = (survive | birth).astype(float)
        
        # Diffusion de richesse
        self.wealth_grid = self.wealth_diffusion()
        self.wealth_grid[self.grid == 0] *= 0.95  # Décroissance sans activité
        
    def simulate(self, steps: int) -> List[np.ndarray]:
        """Simule l'évolution sur plusieurs étapes"""
        history = [self.grid.copy()]
        for _ in range(steps):
            self.step()
            history.append(self.grid.copy())
        return history
    
    def compute_monetary_entropy(self) -> float:
        """Calcule l'entropie du système monétaire"""
        total_wealth = np.sum(self.wealth_grid)
        if total_wealth == 0:
            return 0
        
        probabilities = self.wealth_grid.flatten() / total_wealth
        probabilities = probabilities[probabilities > 0]
        
        return -np.sum(probabilities * np.log(probabilities))

# Exemple d'utilisation
automaton = MonetaryCellularAutomaton(grid_size=30)
automaton.initialize_random(density=0.2)

history = automaton.simulate(50)
entropy_history = [automaton.compute_monetary_entropy() for _ in range(50)]

print(f"Entropie initiale: {entropy_history[0]}")
print(f"Entropie finale: {entropy_history[-1]}")
import numpy as np
from scipy.optimize import linprog

class MonetaryGameTheory:
    """Modèles de théorie des jeux pour les interactions monétaires"""
    
    def __init__(self, num_players: int = 2):
        self.num_players = num_players
        self.payoff_matrix = None
    
    def cooperative_game(self, cooperation_benefit: float = 1.5) -> np.ndarray:
        """Modèle de jeu coopératif (prisoner's dilemma modifié)"""
        # Payoffs: [cooperate, defect]
        payoff = np.array([
            [cooperation_benefit, 0.5],  # Coopérer
            [0.5, 1.0]                   # Défaut
        ])
        return payoff
    
    def competitive_game(self, competition_intensity: float = 2.0) -> np.ndarray:
        """Modèle de jeu compétitif (zero-sum)"""
        payoff = np.array([
            [1.0, -competition_intensity],
            [-competition_intensity, 1.0]
        ])
        return payoff
    
    def find_nash_equilibrium(self, payoff_matrix: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Trouve l'équilibre de Nash (simplifié)"""
        # Simplification pour 2 joueurs, 2 stratégies
        # Utilisation de l'optimisation linéaire
        
        # Pour le joueur 1
        c = np.array([1, 1])
        A_ub = -payoff_matrix.T
        b_ub = np.array([0, 0])
        A_eq = np.array([[1, 1]])
        b_eq = np.array([1])
        
        # Limites des variables
        bounds = [(0, 1), (0, 1)]
        
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
        strategy1 = result.x if result.success else np.ones(2) / 2
        
        # Stratégie similaire pour le joueur 2
        c = np.array([1, 1])
        A_ub = -payoff_matrix
        b_ub = np.array([0, 0])
        A_eq = np.array([[1, 1]])
        b_eq = np.array([1])
        
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds)
        strategy2 = result.x if result.success else np.ones(2) / 2
        
        return strategy1, strategy2
    
    def calculate_replicator_dynamics(self, payoff_matrix: np.ndarray, 
                                     initial_strategies: np.ndarray, 
                                     steps: int = 100) -> List[np.ndarray]:
        """Simule la dynamique des réplicateurs"""
        strategies = [initial_strategies.copy()]
        
        for _ in range(steps):
            current = strategies[-1]
            total_payoff = current @ payoff_matrix @ current
            
            # Équation de réplicateur: dxi/dt = xi * (payoff_i - avg_payoff)
            avg_payoff = total_payoff / np.sum(current) if np.sum(current) > 0 else 0
            individual_payoffs = payoff_matrix @ current
            
            new_strategies = current * (individual_payoffs - avg_payoff)
            new_strategies = new_strategies / np.sum(new_strategies) if np.sum(new_strategies) > 0 else current
            
            strategies.append(new_strategies)
        
        return strategies

# Exemple d'utilisation
game = MonetaryGameTheory()

print("Jeu coopératif (Prisoner's Dilemma modifié):")
payoff_coop = game.cooperative_game(cooperation_benefit=1.5)
print(f"Matrice des paiements:\n{payoff_coop}")
print(f"Équilibre de Nash: {game.find_nash_equilibrium(payoff_coop)}")

print("\nJeu compétitif (Zero-sum):")
payoff_comp = game.competitive_game(competition_intensity=2.0)
print(f"Matrice des paiements:\n{payoff_comp}")
print(f"Équilibre de Nash: {game.find_nash_equilibrium(payoff_comp)}")

# Simulation de la dynamique
initial = np.array([0.5, 0.5])
dynamics = game.calculate_replicator_dynamics(payoff_coop, initial)
print(f"\nDynamique des réplicateurs (équilibre final): {dynamics[-1]}")
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

class ViabilityWindow:
    """Modèle de la fenêtre de viabilité pour les systèmes monétaires"""
    
    def __init__(self):
        self.fitness_function = None
        self.dissipation_function = None
    
    def viability_curve(self, x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
        """Courbe de viabilité (fonction logistique modifiée)"""
        return a / (1 + np.exp(-b * (x - c)))
    
    def dissipation_curve(self, x: np.ndarray, d: float, e: float) -> np.ndarray:
        """Courbe de dissipation d'énergie"""
        return d * x * np.exp(-e * x)
    
    def find_viability_window(self, param_space: np.ndarray, 
                            viability_threshold: float = 0.5) -> Tuple[float, float]:
        """Trouve la fenêtre de viabilité"""
        viability = self.viability_curve(param_space, 1, 0.1, 50)
        dissipation = self.dissipation_curve(param_space, 1, 0.02)
        
        # Fenêtre de viabilité: où les deux conditions sont satisfaites
        viable = (viability > viability_threshold) & (dissipation < 0.5)
        
        if not np.any(viable):
            return None, None
        
        indices = np.where(viable)[0]
        return param_space[indices[0]], param_space[indices[-1]]
    
    def calculate_optimal_point(self, param_space: np.ndarray) -> Tuple[float, float]:
        """Calcule le point optimal dans la fenêtre de viabilité"""
        viability = self.viability_curve(param_space, 1, 0.1, 50)
        dissipation = self.dissipation_curve(param_space, 1, 0.02)
        
        # Fonction objectif: maximiser viabilité, minimiser dissipation
        objective = viability - dissipation
        
        # Trouver l'optimum
        opt_idx = np.argmax(objective)
        opt_param = param_space[opt_idx]
        opt_value = objective[opt_idx]
        
        return opt_param, opt_value
    
    def get_robustness_score(self, param: float) -> float:
        """Calcule le score de robustesse pour un paramètre donné"""
        viability = self.viability_curve(np.array([param]), 1, 0.1, 50)[0]
        dissipation = self.dissipation_curve(np.array([param]), 1, 0.02)[0]
        
        return viability - dissipation

# Exemple d'utilisation
vw = ViabilityWindow()
param_space = np.linspace(0, 100, 1000)

# Trouver la fenêtre de viabilité
lower, upper = vw.find_viability_window(param_space)
print(f"Fenêtre de viabilité: [{lower:.1f}, {upper:.1f}]")

# Trouver le point optimal
opt_param, opt_value = vw.calculate_optimal_point(param_space)
print(f"Point optimal: paramètre={opt_param:.1f}, valeur={opt_value:.3f}")

# Score de robustesse pour différents paramètres
test_params = [10, 30, 50, 70, 90]
for p in test_params:
    score = vw.get_robustness_score(p)
    print(f"Paramètre {p}: score de robustesse={score:.3f}")
import numpy as np
from scipy.integrate import solve_ivp

class AutocatalyticMonetarySystem:
    """Système monétaire autocatalytique"""
    
    def __init__(self, 
                 production_rate: float = 0.1,
                 catalytic_efficiency: float = 0.05,
                 decay_rate: float = 0.01,
                 investment_threshold: float = 1.0):
        self.production_rate = production_rate
        self.catalytic_efficiency = catalytic_efficiency
        self.decay_rate = decay_rate
        self.investment_threshold = investment_threshold
    
    def system_equations(self, t: float, y: np.ndarray) -> np.ndarray:
        """
        Équations du système autocatalytique
        y[0]: Masse monétaire
        y[1]: Production réelle
        y[2]: Investissement catalytique
        """
        money, production, investment = y
        
        # Autocatalyse: l'argent génère plus d'argent via l'investissement
        dmoney_dt = self.catalytic_efficiency * investment * money - self.decay_rate * money
        
        # Production proportionnelle à l'investissement catalytique
        dproduction_dt = self.production_rate * investment * (1 - production / 100)
        
        # Investissement déclenché par la production
        dinvestment_dt = self.production_rate * (production / money) - self.decay_rate * investment
        
        return np.array([dmoney_dt, dproduction_dt, dinvestment_dt])
    
    def simulate(self, 
                initial_state: np.ndarray,
                t_span: Tuple[float, float] = (0, 100),
                t_eval: int = 1000) -> dict:
        """Simule le système autocatalytique"""
        t = np.linspace(t_span[0], t_span[1], t_eval)
        
        solution = solve_ivp(
            self.system_equations,
            t_span,
            initial_state,
            t_eval=t,
            method='RK45'
        )
        
        return {
            't': solution.t,
            'money': solution.y[0],
            'production': solution.y[1],
            'investment': solution.y[2]
        }
    
    def calculate_efficiency(self, results: dict) -> float:
        """Calcule l'efficacité du système"""
        final_money = results['money'][-1]
        initial_money = results['money'][0]
        total_production = np.trapz(results['production'], results['t'])
        
        return (final_money - initial_money) / (total_production + 1e-10)
    
    def analyze_self_sustainability(self, results: dict) -> dict:
        """Analyse la capacité d'auto-soutien du système"""
        investment = results['investment']
        production = results['production']
        
        # Ratio investissement/production
        ratio = np.mean(investment / (production + 1e-10))
        
        # Tendance de l'investissement
        investment_trend = (investment[-1] - investment[0]) / investment[0]
        
        return {
            'investment_production_ratio': ratio,
            'investment_trend': investment_trend,
            'self_sustaining': investment_trend > 0 and ratio > self.investment_threshold
        }

# Exemple d'utilisation
auto_system = AutocatalyticMonetarySystem(
    production_rate=0.1,
    catalytic_efficiency=0.05,
    decay_rate=0.01
)

initial_state = np.array([10.0, 10.0, 2.0])  # [money, production, investment]
results = auto_system.simulate(initial_state)

efficiency = auto_system.calculate_efficiency(results)
analysis = auto_system.analyze_self_sustainability(results)

print(f"Efficacité du système: {efficiency:.3f}")
print(f"Ratio investissement/production: {analysis['investment_production_ratio']:.3f}")
print(f"Tendance de l'investissement: {analysis['investment_trend']:.3f}")
print(f"Système auto-soutenable: {analysis['self_sustaining']}")
import numpy as np
from scipy.stats import gaussian_kde

class MultiScaleMonetarySystem:
    """Système monétaire multi-échelles"""
    
    def __init__(self, num_scales: int = 3):
        self.num_scales = num_scales
        self.scales = []
        self.interactions = []
    
    def create_scale(self, 
                    scale_id: int,
                    num_agents: int,
                    scale_factor: float = 1.0) -> dict:
        """Crée une échelle du système"""
        return {
            'id': scale_id,
            'num_agents': num_agents,
            'scale_factor': scale_factor,
            'agents': np.random.random(num_agents) * 100,
            'connections': np.zeros((num_agents, num_agents))
        }
    
    def initialize_scales(self, agent_counts: List[int], scale_factors: List[float]) -> None:
        """Initialise les différentes échelles"""
        for i in range(self.num_scales):
            scale = self.create_scale(i, agent_counts[i], scale_factors[i])
            self.scales.append(scale)
    
    def compute_scale_interactions(self, scale1: dict, scale2: dict) -> np.ndarray:
        """Calcule les interactions entre deux échelles"""
        n1, n2 = scale1['num_agents'], scale2['num_agents']
        return np.random.random((n1, n2)) * scale1['scale_factor'] * scale2['scale_factor']
    
    def calculate_entropy_at_scale(self, scale: dict) -> float:
        """Calcule l'entropie à une échelle donnée"""
        wealth = scale['agents']
        probabilities = wealth / np.sum(wealth)
        probabilities = probabilities[probabilities > 0]
        return -np.sum(probabilities * np.log(probabilities))
    
    def calculate_cross_scale_entropy(self) -> float:
        """Calcule l'entropie entre les échelles"""
        total_entropy = 0
        for i, scale1 in enumerate(self.scales):
            total_entropy += self.calculate_entropy_at_scale(scale1)
            
            for j, scale2 in enumerate(self.scales):
                if i < j:
                    # Interaction entre échelles
                    interaction = self.compute_scale_interactions(scale1, scale2)
                    interaction_entropy = -np.sum(interaction * np.log(interaction + 1e-10))
                    total_entropy += 0.5 * interaction_entropy
        
        return total_entropy
    
    def evolve_scales(self, steps: int = 10) -> List[float]:
        """Fait évoluer les échelles"""
        entropy_history = []
        
        for step in range(steps):
            for i, scale in enumerate(self.scales):
                # Évolution interne
                influence = np.sum(scale['connections'], axis=0)
                scale['agents'] = 0.9 * scale['agents'] + 0.1 * influence
                scale['agents'] = np.maximum(scale['agents'], 0)
                
                # Réseau de connexions
                scale['connections'] = np.random.random((scale['num_agents'], scale['num_agents']))
            
            entropy_history.append(self.calculate_cross_scale_entropy())
        
        return entropy_history
    
    def get_scale_distribution(self) -> List[np.ndarray]:
        """Obtient la distribution de richesse à chaque échelle"""
        distributions = []
        for scale in self.scales:
            kde = gaussian_kde(scale['agents'])
            x_range = np.linspace(0, 100, 50)
            distributions.append(kde(x_range))
        return distributions

# Exemple d'utilisation
multi_scale = MultiScaleMonetarySystem(num_scales=3)
agent_counts = [100, 50, 20]  # De plus en plus petit
scale_factors = [1.0, 0.5, 0.1]  # De plus en plus petit

multi_scale.initialize_scales(agent_counts, scale_factors)

initial_entropy = multi_scale.calculate_cross_scale_entropy()
print(f"Entropie initiale entre échelles: {initial_entropy:.3f}")

entropy_history = multi_scale.evolve_scales(steps=20)
print(f"Entropie finale: {entropy_history[-1]:.3f}")

# Distribution à chaque échelle
distributions = multi_scale.get_scale_distribution()
for i, dist in enumerate(distributions):
    print(f"Échelle {i}: moyenne={np.mean(dist):.3f}, écart-type={np.std(dist):.3f}")
import numpy as np
from scipy.optimize import minimize

class NegentropyMonetarySystem:
    """Système monétaire avec mesure de négentropie"""
    
    def __init__(self, initial_wealth: np.ndarray):
        self.wealth = initial_wealth.copy()
        self.energy_state = np.ones_like(initial_wealth)
        self.temperature = 1.0
    
    def compute_entropy(self, distribution: np.ndarray) -> float:
        """Calcule l'entropie de Shannon"""
        probs = distribution / np.sum(distribution)
        probs = probs[probs > 0]
        return -np.sum(probs * np.log(probs))
    
    def compute_negentropy(self) -> float:
        """Calcule la négentropie (entropie négative)"""
        current_entropy = self.compute_entropy(self.wealth)
        max_entropy = np.log(len(self.wealth))
        return max_entropy - current_entropy
    
    def compute_energy_dissipation(self, rate: float = 0.1) -> float:
        """Calcule le taux de dissipation d'énergie"""
        # Modèle simplifié: dissipation proportionnelle à l'activité
        activity = np.sum(self.wealth > 0) / len(self.wealth)
        return activity * rate * np.sum(self.wealth)
    
    def apply_transaction(self, sender: int, receiver: int, amount: float) -> bool:
        """Applique une transaction monétaire"""
        if self.wealth[sender] >= amount:
            self.wealth[sender] -= amount
            self.wealth[receiver] += amount
            
            # Mise à jour de l'état énergétique
