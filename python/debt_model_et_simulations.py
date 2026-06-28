# debt_model.py
# Modèle de dette avec intérêts composés et équilibre de Ponzi

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint

class DebtModel:
    """
    Modèle de dette avec intérêts composés
    """
    
    def __init__(self, principal=1000, rate=0.05, years=30):
        self.principal = principal
        self.rate = rate
        self.years = years
        
    def compound_interest(self, periods_per_year=12):
        """Intérêts composés"""
        t = np.linspace(0, self.years, self.years * periods_per_year)
        A = self.principal * (1 + self.rate / periods_per_year) ** (periods_per_year * t)
        return t, A
    
    def differential_growth(self):
        """Croissance exponentielle continue"""
        t = np.linspace(0, self.years, 1000)
        D = self.principal * np.exp(self.rate * t)
        return t, D
    
    def ponzi_condition(self, gdp_growth=0.02):
        """Condition d'équilibre de Ponzi: D(t) / PIB(t) -> infini"""
        t = np.linspace(0, self.years, 1000)
        D = self.principal * np.exp(self.rate * t)
        GDP = 10000 * np.exp(gdp_growth * t)
        ratio = D / GDP
        return t, ratio
    
    def sustainability_condition(self, surplus_function=None):
        """
        Condition de soutenabilité: lim D(t)/(1+r)^t = 0
        """
        if surplus_function is None:
            surplus_function = lambda t: 100 * np.exp(0.01 * t)
        
        t = np.linspace(0, self.years, 1000)
        D = np.zeros_like(t)
        D[0] = self.principal
        
        dt = t[1] - t[0]
        for i in range(1, len(t)):
            D[i] = D[i-1] * (1 + self.rate * dt) - surplus_function(t[i-1]) * dt
            
        # Condition de soutenabilité
        sustainability = D / ((1 + self.rate) ** t)
        
        return t, D, sustainability
    
    def plot_all(self):
        """Visualisation de tous les scénarios"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Intérêts composés
        t, A = self.compound_interest()
        axes[0, 0].plot(t, A)
        axes[0, 0].set_title(f'Intérêts composés (r={self.rate*100:.1f}%)')
        axes[0, 0].set_xlabel('Années')
        axes[0, 0].set_ylabel('Montant')
        axes[0, 0].grid(True)
        
        # Croissance exponentielle
        t, D = self.differential_growth()
        axes[0, 1].plot(t, D)
        axes[0, 1].set_title('Croissance exponentielle de la dette')
        axes[0, 1].set_xlabel('Années')
        axes[0, 1].set_ylabel('Dette')
        axes[0, 1].grid(True)
        
        # Ratio Dette/PIB (condition de Ponzi)
        t, ratio = self.ponzi_condition()
        axes[1, 0].plot(t, ratio)
        axes[1, 0].axhline(y=1, color='r', linestyle='--', label='Seuil critique')
        axes[1, 0].set_title('Ratio Dette/PIB')
        axes[1, 0].set_xlabel('Années')
        axes[1, 0].set_ylabel('Dette / PIB')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
        
        # Condition de soutenabilité
        t, D, sustainability = self.sustainability_condition()
        axes[1, 1].plot(t, sustainability)
        axes[1, 1].axhline(y=0, color='r', linestyle='--', label='Limite')
        axes[1, 1].set_title('Condition de soutenabilité: lim D/(1+r)^t')
        axes[1, 1].set_xlabel('Années')
        axes[1, 1].set_ylabel('D / (1+r)^t')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.show()
        
        return fig


# Exemple d'utilisation
if __name__ == "__main__":
    model = DebtModel(principal=1000, rate=0.05, years=50)
    model.plot_all()

# bimetallism_model.py
# Modèle de bimétallisme et loi de Gresham

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

class BimetallismModel:
    """
    Modèle de système bimétallique avec loi de Gresham
    """
    
    def __init__(self, gold_price=1500, silver_price=25, ratio_fixed=60):
        self.gold_price = gold_price
        self.silver_price = silver_price
        self.ratio_fixed = ratio_fixed
        self.ratio_market = gold_price / silver_price
        
    def gresham_law(self, legal_ratio, market_ratio):
        """
        Loi de Gresham: la mauvaise monnaie chasse la bonne
        
        Returns:
            'good_money' or 'bad_money' selon le cas
        """
        if legal_ratio > market_ratio:
            # L'or est surévalué légalement, l'argent est chassé
            return "L'argent (bonne monnaie) est thésaurisé"
        elif legal_ratio < market_ratio:
            # L'argent est surévalué légalement, l'or est chassé
            return "L'or (bonne monnaie) est thésaurisé"
        else:
            return "Équilibre parfait"
    
    def grandona_system(self, ratio_initial, ratio_target, steps=100):
        """
        Système Grandona: convergence vers un ratio fixe
        
        dx/dt = k(ratio_target - x)
        """
        t = np.linspace(0, 10, steps)
        k = 0.5  # vitesse de convergence
        ratio = ratio_target + (ratio_initial - ratio_target) * np.exp(-k * t)
        return t, ratio
    
    def equilibrium_conditions(self):
        """
        Conditions d'équilibre pour le bimétallisme
        """
        # Équation de parité: P_or / P_argent = R_fixe
        def parity_equation(x):
            return self.gold_price / x - self.ratio_fixed
        
        # Résolution
        silver_price_equilibrium = fsolve(parity_equation, self.silver_price)[0]
        
        return {
            'silver_price_equilibrium': silver_price_equilibrium,
            'gold_price_equilibrium': self.gold_price,
            'ratio': self.ratio_fixed
        }
    
    def monetary_velocity(self, money_supply, gdp, velocity=1.5):
        """
        Équation de la vitesse de la monnaie: MV = PY
        """
        price_level = (money_supply * velocity) / gdp
        return price_level
    
    def plot_gresham(self):
        """Visualisation de la loi de Gresham"""
        legal_ratios = np.linspace(40, 80, 100)
        market_ratio = self.ratio_market
        
        # Régions
        gold_overvalued = legal_ratios > market_ratio
        silver_overvalued = legal_ratios < market_ratio
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.fill_between(legal_ratios, 0, gold_overvalued, 
                       color='gold', alpha=0.3, label='L\'or surévalué')
        ax.fill_between(legal_ratios, 0, silver_overvalued, 
                       color='silver', alpha=0.3, label='L\'argent surévalué')
        
        ax.axvline(x=market_ratio, color='k', linestyle='--', 
                  label=f'Ratio de marché: {market_ratio:.1f}')
        
        ax.set_xlabel('Ratio légal or/argent')
        ax.set_ylabel('Régime monétaire')
        ax.set_title('Loi de Gresham: Zones d\'instabilité')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_grandona(self):
        """Visualisation du système Grandona"""
        t, ratio = self.grandona_system(
            ratio_initial=self.ratio_market,
            ratio_target=self.ratio_fixed
        )
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(t, ratio, 'b-', linewidth=2)
        ax.axhline(y=self.ratio_fixed, color='r', linestyle='--', 
                  label=f'Ratio cible: {self.ratio_fixed}')
        ax.axhline(y=self.ratio_market, color='g', linestyle='--', 
                  label=f'Ratio initial: {self.ratio_market:.1f}')
        
        ax.set_xlabel('Temps')
        ax.set_ylabel('Ratio or/argent')
        ax.set_title('Système Grandona: Convergence vers l\'équilibre')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()


# Exemple d'utilisation
if __name__ == "__main__":
    model = BimetallismModel(gold_price=1500, silver_price=25, ratio_fixed=60)
    print(model.gresham_law(60, 1500/25))
    model.plot_gresham()
    model.plot_grandona()

# blockchain_model.py
# Modèle de blockchain et crypto-monnaies

import numpy as np
import hashlib
import time
from typing import List, Tuple
import matplotlib.pyplot as plt

class CryptoModel:
    """
    Modèle de crypto-monnaie avec effet réseau
    """
    
    def __init__(self, initial_price=100, adoption_rate=0.01):
        self.initial_price = initial_price
        self.adoption_rate = adoption_rate
        
    def metcalfe_law(self, n_users: int) -> float:
        """
        Loi de Metcalfe: la valeur du réseau est proportionnelle à n²
        """
        return self.initial_price * (n_users ** 2) / 1000
    
    def adoption_dynamics(self, n0: int, max_users: int, steps: int) -> np.ndarray:
        """
        Dynamique d'adoption: logistique
        """
        t = np.linspace(0, 10, steps)
        r = self.adoption_rate
        
        # Équation logistique
        n = n0 * max_users * np.exp(r * t) / (max_users + n0 * (np.exp(r * t) - 1))
        return t, n
    
    def network_effect(self, n_users: int, transaction_volume: float) -> float:
        """
        Effet réseau: plus d'utilisateurs = plus de valeur
        """
        return self.metcalfe_law(n_users) * (1 + transaction_volume / 1000)
    
    def blockchain_difficulty(self, hash_power: float, target_time: float) -> float:
        """
        Ajustement de la difficulté de minage
        """
        return hash_power / target_time
    
    def transaction_throughput(self, block_size: int, block_time: float) -> float:
        """
        Débit des transactions
        """
        return block_size / block_time
    
    def ponzi_simulation(self, n_users: int, price: float) -> dict:
        """
        Simulation d'un système de Ponzi dans les crypto
        """
        # Simuler l'effet de la dilution
        market_cap = price * n_users
        new_price = market_cap / (n_users * 1.1)  # 10% de dilution
        
        return {
            'market_cap': market_cap,
            'new_price': new_price,
            'dilution': (price - new_price) / price * 100
        }
    
    def plot_adoption(self):
        """Visualisation de l'adoption"""
        t, n = self.adoption_dynamics(n0=100, max_users=10000, steps=100)
        value = self.metcalfe_law(n)
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Adoption
        axes[0].plot(t, n)
        axes[0].set_title('Adoption du réseau')
        axes[0].set_xlabel('Temps')
        axes[0].set_ylabel('Nombre d\'utilisateurs')
        axes[0].grid(True)
        
        # Valeur du réseau (Metcalfe)
        axes[1].plot(t, value)
        axes[1].set_title('Valeur du réseau (Loi de Metcalfe)')
        axes[1].set_xlabel('Temps')
        axes[1].set_ylabel('Valeur')
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.show()


class SchwundgeldModel:
    """
    Modèle de monnaie fondante (Schwundgeld)
    """
    
    def __init__(self, initial_value=100, decay_rate=0.01):
        self.initial_value = initial_value
        self.decay_rate = decay_rate
    
    def value_over_time(self, t: np.ndarray) -> np.ndarray:
        """Valeur décroissante exponentiellement"""
        return self.initial_value * np.exp(-self.decay_rate * t)
    
    def velocity_increase(self, base_velocity: float) -> float:
        """
        Augmentation de la vitesse de circulation
        """
        return base_velocity * (1 + self.decay_rate * 10)
    
    def plot_decay(self):
        """Visualisation de la dépréciation"""
        t = np.linspace(0, 100, 1000)
        value = self.value_over_time(t)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(t, value)
        ax.axhline(y=self.initial_value * np.exp(-1), color='r', linestyle='--',
                  label=f'T1: {self.initial_value * np.exp(-1):.1f}')
        
        ax.set_xlabel('Temps')
        ax.set_ylabel('Valeur de la monnaie')
        ax.set_title('Schwundgeld: Monnaie à valeur déclinante')
        ax.legend()
        ax.grid(True)
        
        plt.tight_layout()
        plt.show()


# Exemple d'utilisation
if __name__ == "__main__":
    model = CryptoModel(initial_price=100, adoption_rate=0.05)
    model.plot_adoption()
    
    schwund = SchwundgeldModel(initial_value=100, decay_rate=0.02)
    schwund.plot_decay()

# governance_model.py
# Modèle de vote DAV et gouvernance DAO

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

class DAVModel:
    """
    Delayed Approval Voting (DAV) Model
    """
    
    def __init__(self, n_voters=1000, n_candidates=5, max_score=10):
        self.n_voters = n_voters
        self.n_candidates = n_candidates
        self.max_score = max_score
        
    def generate_preferences(self, distribution='uniform'):
        """
        Génération des préférences des électeurs
        """
        if distribution == 'uniform':
            preferences = np.random.randint(0, self.max_score + 1, 
                                          (self.n_voters, self.n_candidates))
        elif distribution == 'normal':
            preferences = np.random.normal(self.max_score/2, self.max_score/3,
                                          (self.n_voters, self.n_candidates))
            preferences = np.clip(preferences, 0, self.max_score).astype(int)
        else:
            raise ValueError("Distribution non reconnue")
        
        return preferences
    
    def calculate_scores(self, preferences):
        """Calcul des scores totaux"""
        scores = np.sum(preferences, axis=0)
        return scores
    
    def elect_candidate(self, preferences, delay=0.5):
        """
        Élection avec délai (DAV)
        """
        scores = self.calculate_scores(preferences)
        
        # Ajouter du bruit représentant le délai d'information
        noise = np.random.normal(0, delay * np.std(scores), len(scores))
        noisy_scores = scores + noise
        
        winner = np.argmax(noisy_scores)
        
        return {
            'scores': scores,
            'noisy_scores': noisy_scores,
            'winner': winner,
            'winner_score': scores[winner]
        }
    
    def simulate_election(self, n_elections=1000):
        """
        Simulation de nombreuses élections pour analyser la stabilité
        """
        winners = []
        score_variance = []
        
        for _ in range(n_elections):
            preferences = self.generate_preferences('normal')
            result = self.elect_candidate(preferences)
            winners.append(result['winner'])
            score_variance.append(np.var(result['scores']))
        
        return {
            'winners': winners,
            'score_variance': score_variance,
            'winner_counts': np.bincount(winners, minlength=self.n_candidates)
        }
    
    def plot_election(self):
        """Visualisation des résultats"""
        preferences = self.generate_preferences('normal')
        result = self.elect_candidate(preferences)
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Scores par candidat
        candidates = range(self.n_candidates)
        axes[0].bar(candidates, result['scores'], alpha=0.7, label='Scores réels')
        axes[0].bar(candidates, result['noisy_scores'], alpha=0.5, 
                   label='Scores avec délai')
        axes[0].axvline(x=result['winner'], color='r', linestyle='--', 
                       label='Élu')
        axes[0].set_xlabel('Candidats')
        axes[0].set_ylabel('Scores')
        axes[0].set_title('Élection DAV')
        axes[0].legend()
        axes[0].grid(True)
        
        # Distribution des scores
        for i in range(self.n_candidates):
            axes[1].hist(preferences[:, i], alpha=0.5, bins=range(self.max_score+1),
                        label=f'Candidat {i}')
        axes[1].set_xlabel('Score')
        axes[1].set_ylabel('Fréquence')
        axes[1].set_title('Distribution des préférences')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.show()


class DAOOptimization:
    """
    Optimisation des paramètres de la DAO
    """
    
    def __init__(self, n_members=1000, base_velocity=1.5):
        self.n_members = n_members
        self.base_velocity = base_velocity
    
    def utility_function(self, n, v, theta):
        """
        Fonction d'utilité collective
        U(N,V,θ) = bien-être collectif - coût de gouvernance
        """
        # Bien-être collectif: augmente avec la taille et la vélocité
        well_being = np.log(n) * v * (1 + theta / 100)
        
        # Coût de gouvernance: quadratique en fonction de la taille
        governance_cost = 0.01 * n * (1 + theta / 50)
        
        return well_being - governance_cost
    
    def optimize_parameters(self):
        """
        Optimisation des paramètres de la DAO
        """
        # Grille de recherche
        n_grid = np.linspace(10, self.n_members, 50)
        theta_grid = np.linspace(0, 10, 20)
        
        utility_grid = np.zeros((len(n_grid), len(theta_grid)))
        
        for i, n in enumerate(n_grid):
            for j, theta in enumerate(theta_grid):
                utility_grid[i, j] = self.utility_function(
                    n, self.base_velocity, theta
                )
        
        # Trouver l'optimum
        i_opt, j_opt = np.unravel_index(np.argmax(utility_grid), utility_grid.shape)
        n_opt = n_grid[i_opt]
        theta_opt = theta_grid[j_opt]
        
        return {
            'n_optimal': n_opt,
            'theta_optimal': theta_opt,
            'max_utility': np.max(utility_grid),
            'utility_grid': utility_grid,
            'n_grid': n_grid,
            'theta_grid': theta_grid
        }
    
    def plot_optimization(self):
        """Visualisation de l'optimisation"""
        result = self.optimize_parameters()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Heatmap
        im = ax.imshow(result['utility_grid'].T, aspect='auto',
                      extent=[min(result['n_grid']), max(result['n_grid']),
                             min(result['theta_grid']), max(result['theta_grid'])],
                      origin='lower', cmap='viridis')
        
        # Point optimal
        ax.plot(result['n_optimal'], result['theta_optimal'], 'r*', 
               markersize=15, label='Optimum')
        
        ax.set_xlabel('Taille de la DAO (N)')
        ax.set_ylabel('Paramètre de gouvernance (θ)')
        ax.set_title('Optimisation des paramètres de la DAO')
        ax.legend()
        plt.colorbar(im, label='Utilité')
        plt.tight_layout()
        plt.show()


# Exemple d'utilisation
if __name__ == "__main__":
    # DAV
    dav = DAVModel(n_voters=1000, n_candidates=5, max_score=10)
    dav.plot_election()
    
    # Simulation
    results = dav.simulate_election(n_elections=1000)
    print("Distribution des élus:", results['winner_counts'])
    
    # Optimisation DAO
    dao = DAOOptimization(n_members=1000, base_velocity=1.5)
    result = dao.optimize_parameters()
    print(f"N optimal: {result['n_optimal']:.0f}")
    print(f"θ optimal: {result['theta_optimal']:.1f}")
    dao.plot_optimization()

# psychology_model.py
# Modèle des effets psychologiques de la monnaie

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import convolve

class NeuroMonetaryModel:
    """
    Modèle des effets neurologiques de la monnaie
    """
    
    def __init__(self):
        # Paramètres des régions cérébrales
        self.insula = {
            'response_time': 0.1,  # réponse immédiate
            'intensity': 0.8,
            'decay': 0.5
        }
        self.prefrontal = {
            'response_time': 0.5,  # réponse plus lente
            'intensity': 0.4,
            'decay': 0.2
        }
    
    def monetary_stimulus(self, amount, time):
        """Stimulus monétaire"""
        return amount * np.exp(-time)
    
    def insula_response(self, stimulus, time):
        """Réponse de l'insula (satisfaction immédiate)"""
        tau = self.insula['response_time']
        intensity = self.insula['intensity']
        return intensity * stimulus * np.exp(-time/tau)
    
    def prefrontal_response(self, stimulus, time):
        """Réponse du cortex préfrontal (contrôle)"""
        tau = self.prefrontal['response_time']
        intensity = self.prefrontal['intensity']
        return intensity * stimulus * np.exp(-time/tau)
    
    def brain_dynamics(self, amount=100, duration=10, sampling=1000):
        """
        Dynamique des réponses cérébrales
        """
        t = np.linspace(0, duration, sampling)
        stimulus = self.monetary_stimulus(amount, t)
        
        insula = self.insula_response(stimulus, t)
        prefrontal = self.prefrontal_response(stimulus, t)
        
        # Ratio I/P
        ratio = insula / (prefrontal + 1e-6)
        
        return {
            'time': t,
            'stimulus': stimulus,
            'insula': insula,
            'prefrontal': prefrontal,
            'ratio': ratio
        }
    
    def vohs_experiment(self, n_participants=100):
        """
        Simulation de l'expérience Vohs (2006)
        """
        # Groupe exposé à l'argent
        money_group = np.random.normal(0.3, 0.1, n_participants)  # faible coopération
        # Groupe contrôle
        control_group = np.random.normal(0.7, 0.15, n_participants)  # haute coopération
        
        return {
            'money_group': money_group,
            'control_group': control_group,
            'difference': np.mean(control_group) - np.mean(money_group)
        }
    
    def plot_brain_response(self):
        """Visualisation des réponses cérébrales"""
        data = self.brain_dynamics(amount=100, duration=5)
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Stimulus
        axes[0, 0].plot(data['time'], data['stimulus'])
        axes[0, 0].set_title('Stimulus monétaire')
        axes[0, 0].set_xlabel('Temps')
        axes[0, 0].set_ylabel('Intensité')
        axes[0, 0].grid(True)
        
        # Insula
        axes[0, 1].plot(data['time'], data['insula'], 'r-', label='Insula')
        axes[0, 1].set_title('Réponse de l\'insula (impulsion)')
        axes[0, 1].set_xlabel('Temps')
        axes[0, 1].set_ylabel('Activité')
        axes[0, 1].grid(True)
        
        # Cortex préfrontal
        axes[1, 0].plot(data['time'], data['prefrontal'], 'b-', label='Préfrontal')
        axes[1, 0].set_title('Réponse du cortex préfrontal (contrôle)')
        axes[1, 0].set_xlabel('Temps')
        axes[1, 0].set_ylabel('Activité')
        axes[1, 0].grid(True)
        
        # Ratio I/P
        axes[1, 1].plot(data['time'], data['ratio'], 'g-')
        axes[1, 1].axhline(y=1, color='r', linestyle='--', label='Seuil I/P=1')
        axes[1, 1].set_title('Ratio Insula/Préfrontal')
        axes[1, 1].set_xlabel('Temps')
        axes[1, 1].set_ylabel('Ratio I/P')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.show()
    
    def plot_vohs_simulation(self):
        """Visualisation de l'expérience Vohs"""
        data = self.vohs_experiment(n_participants=100)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Histogrammes
        ax.hist(data['money_group'], alpha=0.5, bins=20, label='Groupe argent')
        ax.hist(data['control_group'], alpha=0.5, bins=20, label='Groupe contrôle')
        
        ax.axvline(x=np.mean(data['money_group']), color='r', linestyle='--',
                  label=f'Moyenne argent: {np.mean(data["money_group"]):.2f}')
        ax.axvline(x=np.mean(data['control_group']), color='b', linestyle='--',
                  label=f'Moyenne contrôle: {np.mean(data["control_group"]):.2f}')
        
        ax.set_xlabel('Score de coopération')
        ax.set_ylabel('Fréquence')
        ax.set_title("Expérience Vohs (2006): Effet de l'argent sur la coopération")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        print(f"Différence de coopération: {data['difference']:.2f}")


# Exemple d'utilisation
if __name__ == "__main__":
    model = NeuroMonetaryModel()
    model.plot_brain_response()
    model.plot_vohs_simulation()

# game_theory.py
# Modèle de théorie des jeux pour la coopération monétaire

import numpy as np
import matplotlib.pyplot as plt
from itertools import product

class MonetaryGame:
    """
    Modèle de jeu monétaire: coopération vs compétition
    """
    
    def __init__(self):
        # Matrice de paiement pour le dilemme du prisonnier
        self.payoff_matrix = np.array([
            [[3, 0],  # Coopérer
             [5, 1]]  # Trahir
        ])
    
    def prisoner_dilemma(self, strategy_a, strategy_b):
        """
        Dilemme du prisonnier appliqué à la monnaie
        """
        # 0 = Coopérer, 1 = Trahir
        payoffs = {
            (0, 0): (3, 3),  # Coopération mutuelle
            (0, 1): (0, 5),  # A coopère, B trahit
            (1, 0): (5, 0),  # A trahit, B coopère
            (1, 1): (1, 1)   # Trahison mutuelle
        }
        return payoffs[(strategy_a, strategy_b)]
    
    def evolutionary_dynamics(self, n_iterations=1000, n_agents=100):
        """
        Dynamique évolutionnaire des stratégies
        """
        # Initialisation: 50% coopérateurs, 50% traîtres
        strategies = np.random.choice([0, 1], size=n_agents)
        
        history = {'cooperators': [], 'defectors': []}
        
        for _ in range(n_iterations):
            # Paires aléatoires
            pairs = np.random.permutation(n_agents).reshape(-1, 2)
            
            # Calcul des paiements
            total_payoffs = np.zeros(n_agents)
            for pair in pairs:
                if len(pair) == 2:
                    p1, p2 = self.prisoner_dilemma(strategies[pair[0]], 
                                                  strategies[pair[1]])
                    total_payoffs[pair[0]] += p1
                    total_payoffs[pair[1]] += p2
            
            # Reproduction: les agents avec haut paiement se reproduisent
            new_strategies = np.copy(strategies)
            for i in range(n_agents):
                if np.random.random() < 0.1:  # mutation
                    new_strategies[i] = 1 - strategies[i]
                else:
                    # Sélection par roulette
                    probs = np.exp(total_payoffs) / np.sum(np.exp(total_payoffs))
                    new_strategies[i] = strategies[np.random.choice(n_agents, p=probs)]
            
            strategies = new_strategies
            
            # Enregistrement
            history['cooperators'].append(np.sum(strategies == 0))
            history['defectors'].append(np.sum(strategies == 1))
        
        return history
    
    def public_goods_game(self, n_players=10, endowment=10, multiplier=2):
        """
        Jeu de biens publics: contribution monétaire
        """
        # Contributions aléatoires
        contributions = np.random.uniform(0, endowment, n_players)
        
        # Total du bien public
        total = np.sum(contributions)
        public_good = total * multiplier / n_players
        
        # Paiements individuels
        payoffs = endowment - contributions + public_good
        
        return {
            'contributions': contributions,
            'payoffs': payoffs,
            'total': total,
            'public_good': public_good
        }
    
    def plot_evolution(self):
        """Visualisation de la dynamique évolutionnaire"""
        history = self.evolutionary_dynamics(n_iterations=500, n_agents=100)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(history['cooperators'], 'g-', label='Coopérateurs')
        ax.plot(history['defectors'], 'r-', label='Traîtres')
        
        ax.set_xlabel('Générations')
        ax.set_ylabel('Nombre d\'agents')
        ax.set_title('Dynamique évolutionnaire de la coopération')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_public_goods(self):
        """Visualisation du jeu de biens publics"""
        result = self.public_goods_game(n_players=10)
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Contributions
        axes[0].bar(range(len(result['contributions'])), result['contributions'])
        axes[0].axhline(y=np.mean(result['contributions']), color='r', 
                       linestyle='--', label='Moyenne')
        axes[0].set_xlabel('Joueurs')
        axes[0].set_ylabel('Contribution')
        axes[0].set_title('Contributions au bien public')
        axes[0].legend()
        axes[0].grid(True)
        
        # Paiements
        axes[1].bar(range(len(result['payoffs'])), result['payoffs'])
        axes[1].axhline(y=result['endowment'], color='k', 
                       linestyle='--', label='Dotation initiale')
        axes[1].set_xlabel('Joueurs')
        axes[1].set_ylabel('Paiement final')
        axes[1].set_title('Paiements finaux')
        axes[1].legend()
        axes[1].grid(True)
        
        plt.tight_layout()
        plt.show()


# Exemple d'utilisation
if __name__ == "__main__":
    game = MonetaryGame()
    game.plot_evolution()
    game.plot_public_goods()

# main_simulation.py
# Simulation globale intégrée

import numpy as np
import matplotlib.pyplot as plt
from debt_model import DebtModel
from bimetallism_model import BimetallismModel
from blockchain_model import CryptoModel, SchwundgeldModel
from governance_model import DAVModel, DAOOptimization
from psychology_model import NeuroMonetaryModel
from game_theory import MonetaryGame

class GlobalSimulation:
    """
    Simulation intégrée de tous les modèles
    """
    
    def __init__(self):
        self.debt_model = DebtModel(principal=1000, rate=0.05, years=50)
        self.bimetal_model = BimetallismModel(gold_price=1500, silver_price=25, ratio_fixed=60)
        self.crypto_model = CryptoModel(initial_price=100, adoption_rate=0.05)
        self.schwund_model = SchwundgeldModel(initial_value=100, decay_rate=0.02)
        self.dav_model = DAVModel(n_voters=1000, n_candidates=5, max_score=10)
        self.dao_model = DAOOptimization(n_members=1000, base_velocity=1.5)
        self.neuro_model = NeuroMonetaryModel()
        self.game_model = MonetaryGame()
    
    def run_all_simulations(self):
        """Exécute toutes les simulations"""
        results = {
            'debt': self.debt_model.differential_growth(),
            'bimetal': self.bimetal_model.equilibrium_conditions(),
            'crypto': self.crypto_model.adoption_dynamics(100, 10000, 100),
            'schwund': (np.linspace(0, 100, 1000), 
                       self.schwund_model.value_over_time(np.linspace(0, 100, 1000))),
            'dav': self.dav_model.simulate_election(1000),
            'dao': self.dao_model.optimize_parameters(),
            'vohs': self.neuro_model.vohs_experiment(100)
        }
        return results
    
    def plot_global_summary(self):
        """Visualisation globale"""
        results = self.run_all_simulations()
        
        fig = plt.figure(figsize=(16, 12))
        
        # 1. Dette
        ax1 = plt.subplot(3, 3, 1)
        t, D = results['debt']
        ax1.plot(t, D)
        ax1.set_title('Croissance de la dette')
        ax1.set_xlabel('Années')
        ax1.set_ylabel('Dette')
        ax1.grid(True)
        
        # 2. Bimétallisme
        ax2 = plt.subplot(3, 3, 2)
        eco = results['bimetal']
        ax2.bar(['Gold', 'Silver'], 
                [eco['gold_price_equilibrium'], eco['silver_price_equilibrium']])
        ax2.set_title('Prix d\'équilibre bimétallique')
        ax2.set_ylabel('Prix')
        ax2.grid(True)
        
        # 3. Adoption crypto
        ax3 = plt.subplot(3, 3, 3)
        t, n = results['crypto']
        ax3.plot(t, n)
        ax3.set_title('Adoption crypto')
        ax3.set_xlabel('Temps')
        ax3.set_ylabel('Utilisateurs')
        ax3.grid(True)
        
        # 4. Schwundgeld
        ax4 = plt.subplot(3, 3, 4)
        t, v = results['schwund']
        ax4.plot(t, v)
        ax4.set_title('Monnaie fondante')
        ax4.set_xlabel('Temps')
        ax4.set_ylabel('Valeur')
        ax4.grid(True)
        
        # 5. Élections DAV
        ax5 = plt.subplot(3, 3, 5)
        ax5.bar(range(len(results['dav']['winner_counts'])), 
                results['dav']['winner_counts'])
        ax5.set_title('Distribution des élus (DAV)')
        ax5.set_xlabel('Candidats')
        ax5.set_ylabel('Fréquence')
        ax5.grid(True)
        
        # 6. Optimisation DAO
        ax6 = plt.subplot(3, 3, 6)
        im = ax6.imshow(results['dao']['utility_grid'].T, aspect='auto',
                       extent=[min(results['dao']['n_grid']), max(results['dao']['n_grid']),
                              min(results['dao']['theta_grid']), max(results['dao']['theta_grid'])],
                       origin='lower', cmap='viridis')
        ax6.plot(results['dao']['n_optimal'], results['dao']['theta_optimal'], 
                'r*', markersize=15)
        ax6.set_title('Optimisation DAO')
        ax6.set_xlabel('N')
        ax6.set_ylabel('θ')
        plt.colorbar(im, ax=ax6)
        
        # 7. Expérience Vohs
        ax7 = plt.subplot(3, 3, 7)
        ax7.boxplot([results['vohs']['money_group'], results['vohs']['control_group']],
                   labels=['Argent', 'Contrôle'])
        ax7.set_title('Expérience Vohs')
        ax7.set_ylabel('Coopération')
        ax7.grid(True)
        
        # 8. Théorie des jeux
        ax8 = plt.subplot(3, 3, 8)
        history = self.game_model.evolutionary_dynamics(200, 50)
        ax8.plot(history['cooperators'], 'g-', label='Coopérateurs')
        ax8.plot(history['defectors'], 'r-', label='Traîtres')
        ax8.set_title('Dynamique évolutionnaire')
        ax8.set_xlabel('Générations')
        ax8.set_ylabel('Nombre')
        ax8.legend()
        ax8.grid(True)
        
        # 9. Neurosciences
        ax9 = plt.subplot(3, 3, 9)
        brain = self.neuro_model.brain_dynamics(amount=100, duration=3)
        ax9.plot(brain['time'], brain['ratio'])
        ax9.axhline(y=1, color='r', linestyle='--')
        ax9.set_title('Ratio Insula/Préfrontal')
        ax9.set_xlabel('Temps')
        ax9.set_ylabel('I/P')
        ax9.grid(True)
        
        plt.suptitle('Simulation Globale des Modèles Monétaires', fontsize=16)
        plt.tight_layout()
        plt.show()


# Exécution de la simulation globale
if __name__ == "__main__":
    sim = GlobalSimulation()
    sim.plot_global_summary()

Fichier
Description
Modules
debt_model.py
