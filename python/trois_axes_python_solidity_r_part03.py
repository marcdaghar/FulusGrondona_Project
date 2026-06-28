#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
monetary_system_simulation.py

Simulation du système monétaire usuraire à réserve fractionnaire
avec boucles rétroactives positives et seuils d'effondrement.

Auteur : Marc Daghar
Licence : CC BY-SA 4.0
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from dataclasses import dataclass
from typing import Tuple, List
import warnings
warnings.filterwarnings('ignore')

@dataclass
class MonetaryParams:
    """Paramètres du système monétaire."""
    r: float = 0.05          # Taux d'intérêt usuraire
    g: float = 0.03          # Taux de croissance réelle
    lambda_d: float = 0.01   # Frein de la dette sur la production
    D0: float = 100.0        # Dette initiale
    P0: float = 100.0        # Production initiale
    K0: float = 100.0        # Capital social initial
    L0: float = 1.0          # Légitimité monétaire initiale
    alpha: float = 0.05      # Erosion du capital social
    beta: float = 0.02       # Renforcement endogène du capital social
    gamma: float = 0.03      # Taux de dégradation de la légitimité

class MonetarySystem:
    """Système monétaire avec boucles rétroactives."""
    
    def __init__(self, params: MonetaryParams):
        self.params = params
    
    def system_dynamics(self, state: np.ndarray, t: float) -> np.ndarray:
        """Équations différentielles du système.
        
        state = [D, P, K, L]
        D = dette
        P = production réelle
        K = capital social
        L = légitimité monétaire
        """
        D, P, K, L = state
        p = self.params
        
        # Dette croît exponentiellement
        dD_dt = p.r * D
        
        # Production réelle freinée par le service de la dette
        dP_dt = p.g * P - p.lambda_d * D
        
        # Capital social érodé par la dette, renforcé endogènement
        dK_dt = -p.alpha * D + p.beta * K * (1 - K / p.K0)
        
        # Légitimité monétaire dégradée par la dette
        dL_dt = -p.gamma * D / (P + 1e-6)
        
        return np.array([dD_dt, dP_dt, dK_dt, dL_dt])
    
    def simulate(self, t_span: Tuple[float, float], n_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Simule le système sur l'intervalle de temps."""
        t = np.linspace(t_span[0], t_span[1], n_points)
        state0 = np.array([self.params.D0, self.params.P0, self.params.K0, self.params.L0])
        
        solution = odeint(self.system_dynamics, state0, t)
        return t, solution
    
    def detect_collapse(self, t: np.ndarray, solution: np.ndarray) -> List[float]:
        """Détecte les seuils d'effondrement."""
        D, P, K, L = solution.T
        
        # Seuil 1 : la dette dépasse la production cumulée
        P_cumul = np.cumsum(P) * (t[1] - t[0])
        collapse_debt = D / (P_cumul + 1e-6) > 1.0
        
        # Seuil 2 : le capital social s'effondre
        collapse_social = K < self.params.K0 * 0.1
        
        # Seuil 3 : perte de légitimité
        collapse_legitimacy = L < 0.1
        
        collapse_time = []
        if np.any(collapse_debt):
            collapse_time.append(t[np.argmax(collapse_debt)])
        if np.any(collapse_social):
            collapse_time.append(t[np.argmax(collapse_social)])
        if np.any(collapse_legitimacy):
            collapse_time.append(t[np.argmax(collapse_legitimacy)])
        
        return collapse_time if collapse_time else [np.inf]

def plot_system_simulation():
    """Visualise la simulation du système monétaire."""
    params = MonetaryParams()
    system = MonetarySystem(params)
    t, sol = system.simulate((0, 100))
    
    D, P, K, L = sol.T
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Simulation du Système Monétaire Usuraire\nBoucles Rétroactives et Seuils d\'Effondrement', 
                 fontsize=14)
    
    # Dette
    axes[0, 0].plot(t, D, 'r-', linewidth=2, label='Dette $D(t)$')
    axes[0, 0].set_ylabel('Dette')
    axes[0, 0].set_xlabel('Temps')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    axes[0, 0].set_title('Croissance Exponentielle de la Dette')
    
    # Production
    axes[0, 1].plot(t, P, 'g-', linewidth=2, label='Production $P(t)$')
    axes[0, 1].set_ylabel('Production')
    axes[0, 1].set_xlabel('Temps')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    axes[0, 1].set_title('Production Réelle Freinée par la Dette')
    
    # Capital social
    axes[1, 0].plot(t, K, 'b-', linewidth=2, label='Capital Social $K(t)$')
    axes[1, 0].axhline(y=params.K0 * 0.1, color='r', linestyle='--', label='Seuil d\'effondrement')
    axes[1, 0].set_ylabel('Capital Social')
    axes[1, 0].set_xlabel('Temps')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend()
    axes[1, 0].set_title('Érosion du Capital Social')
    
    # Légitimité
    axes[1, 1].plot(t, L, 'm-', linewidth=2, label='Légitimité $L(t)$')
    axes[1, 1].axhline(y=0.1, color='r', linestyle='--', label='Seuil critique')
    axes[1, 1].set_ylabel('Légitimité')
    axes[1, 1].set_xlabel('Temps')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].legend()
    axes[1, 1].set_title('Perte de Légitimité Monétaire')
    
    plt.tight_layout()
    plt.savefig('monetary_system_simulation.png', dpi=300)
    plt.show()
    
    # Rapport de l'effondrement
    collapse_times = system.detect_collapse(t, sol)
    print(f"\n=== RAPPORT DE SIMULATION ===")
    print(f"Dette finale : {D[-1]:.2f}")
    print(f"Production finale : {P[-1]:.2f}")
    print(f"Rapport Dette/Production : {D[-1]/P[-1]:.2f}")
    print(f"Capital social final : {K[-1]:.2f}")
    print(f"Légitimité finale : {L[-1]:.4f}")
    if collapse_times[0] < np.inf:
        print(f"\n⚠️ EFFONDREMENT DÉTECTÉ à t = {min(collapse_times):.2f}")
    else:
        print("\n✅ Pas d'effondrement dans l'intervalle simulé.")
    
    return fig

if __name__ == "__main__":
    plot_system_simulation()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bimetallism_model.py

Modélisation du bimétallisme or/argent avec système Grondona.
Simulation de la stabilité monétaire et de la résolution de la loi de Gresham.

Auteur : Marc Daghar
Licence : CC BY-SA 4.0
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
from dataclasses import dataclass

@dataclass
class BimetallicParams:
    """Paramètres du système bimétallique."""
    M_or0: float = 100.0       # Masse d'or initiale
    M_argent0: float = 1000.0  # Masse d'argent initiale
    p_or0: float = 1.0         # Prix de l'or (unité de compte)
    p_argent0: float = 0.05    # Prix de l'argent
    R0: float = 20.0           # Ratio officiel or/argent
    alpha: float = 0.1         # Coefficient d'ajustement
    beta: float = 0.5          # Ratio cible
    gamma: float = 0.01        # Taux de croissance de la demande
    delta: float = 0.005       # Taux de dépréciation

class BimetallicSystem:
    """Système monétaire bimétallique."""
    
    def __init__(self, params: BimetallicParams):
        self.params = params
        
    def grondona_adjustment(self, M_or: float, M_argent: float) -> float:
        """Mécanisme d'ajustement Grondona."""
        p = self.params
        ratio_actuel = M_or / (M_argent + 1e-6)
        R_ajuste = p.R0 + p.alpha * (ratio_actuel - p.beta)
        return R_ajuste
    
    def market_equilibrium(self, state: np.ndarray) -> np.ndarray:
        """Équilibre de marché des métaux."""
        M_or, M_argent, p_or, p_argent = state
        p = self.params
        
        # Demande d'or (réserves, thésaurisation)
        D_or = p.gamma * M_or / (p_or + 1e-6)
        # Demande d'argent (circulation, usage industriel)
        D_argent = p.delta * M_argent / (p_argent + 1e-6)
        
        # Prix d'équilibre
        dp_or = D_or - p_or
        dp_argent = D_argent - p_argent
        
        # Évolution des masses monétaires
        dM_or = -p.alpha * (p_or - p.p_or0)
        dM_argent = -p.alpha * (p_argent - p.p_argent0)
        
        return np.array([dM_or, dM_argent, dp_or, dp_argent])
    
    def simulate(self, t_span: Tuple[float, float], n_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Simule l'évolution du système bimétallique."""
        from scipy.integrate import odeint
        
        t = np.linspace(t_span[0], t_span[1], n_points)
        state0 = np.array([
            self.params.M_or0,
            self.params.M_argent0,
            self.params.p_or0,
            self.params.p_argent0
        ])
        
        solution = odeint(self.market_equilibrium, state0, t)
        return t, solution
    
    def gresham_test(self, t: np.ndarray, solution: np.ndarray) -> np.ndarray:
        """Teste la loi de Gresham."""
        M_or, M_argent, p_or, p_argent = solution.T
        R = M_or / (M_argent + 1e-6)
        
        # Condition de Gresham : si R_marché ≠ R_légal, la mauvaise monnaie chasse la bonne
        R_legal = self.params.R0
        gresham_index = np.abs(R - R_legal) / R_legal
        
        return gresham_index

def plot_bimetallism():
    """Visualise la simulation du système bimétallique."""
    params = BimetallicParams()
    system = BimetallicSystem(params)
    t, sol = system.simulate((0, 100))
    
    M_or, M_argent, p_or, p_argent = sol.T
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Simulation du Système Bimétallique (Or/Argent)\nMécanisme de Grondona', fontsize=14)
    
    # Masses monétaires
    axes[0, 0].plot(t, M_or, 'y-', linewidth=2, label='Masse d\'or')
    axes[0, 0].plot(t, M_argent, 'gray', linewidth=2, label='Masse d\'argent')
    axes[0, 0].set_ylabel('Masse monétaire')
    axes[0, 0].set_xlabel('Temps')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    axes[0, 0].set_title('Évolution des Masses Monétaires')
    
    # Prix
    axes[0, 1].plot(t, p_or, 'y-', linewidth=2, label='Prix de l\'or')
    axes[0, 1].plot(t, p_argent, 'gray', linewidth=2, label='Prix de l\'argent')
    axes[0, 1].set_ylabel('Prix')
    axes[0, 1].set_xlabel('Temps')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    axes[0, 1].set_title('Évolution des Prix')
    
    # Ratio
    R = M_or / (M_argent + 1e-6)
    axes[1, 0].plot(t, R, 'g-', linewidth=2, label='Ratio or/argent')
    axes[1, 0].axhline(y=params.R0, color='r', linestyle='--', label='Ratio officiel')
    axes[1, 0].set_ylabel('Ratio')
    axes[1, 0].set_xlabel('Temps')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend()
    axes[1, 0].set_title('Stabilité du Ratio Bimétallique')
    
    # Indice de Gresham
    gresham = system.gresham_test(t, sol)
    axes[1, 1].plot(t, gresham, 'b-', linewidth=2, label='Indice de Gresham')
    axes[1, 1].axhline(y=0.1, color='r', linestyle='--', label='Seuil critique')
    axes[1, 1].set_ylabel('Indice de Gresham')
    axes[1, 1].set_xlabel('Temps')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].legend()
    axes[1, 1].set_title('Résolution de la Loi de Gresham')
    axes[1, 1].set_yscale('log')
    
    plt.tight_layout()
    plt.savefig('bimetallism_simulation.png', dpi=300)
    plt.show()
    
    print(f"\n=== RAPPORT BIMÉTALLIQUE ===")
    print(f"Ratio or/argent final : {R[-1]:.3f}")
    print(f"Ratio officiel : {params.R0:.3f}")
    print(f"Écart relatif : {np.abs(R[-1] - params.R0) / params.R0 * 100:.2f}%")
    print(f"Indice de Gresham final : {gresham[-1]:.5f}")
    if gresham[-1] < 0.1:
        print("✅ Le système Grondona résout la loi de Gresham.")
    else:
        print("⚠️ La loi de Gresham reste active.")
    
    return fig

if __name__ == "__main__":
    plot_bimetallism()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
confidence_network_model.py

Modélisation de la confiance monétaire comme processus de diffusion
sur un réseau social (approche mimétique).

Auteur : Marc Daghar
Licence : CC BY-SA 4.0
"""

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from typing import Tuple, List

class ConfidenceNetwork:
    """Réseau de confiance monétaire avec dynamique mimétique."""
    
    def __init__(self, n_agents: int = 100, p_connection: float = 0.1, gamma: float = 0.5):
        self.n_agents = n_agents
        self.gamma = gamma
        self.graph = nx.erdos_renyi_graph(n_agents, p_connection)
        self.adjacency = nx.to_numpy_array(self.graph)
        self.degree = np.sum(self.adjacency, axis=1)
        
    def confidence_dynamics(self, x: np.ndarray, t: float) -> np.ndarray:
        """Dynamique de la confiance monétaire (modèle de diffusion)."""
        x_mean = np.mean(x)
        dx_dt = self.gamma * (x_mean - x)
        
        # Bruit idiosyncratique
        noise = 0.01 * np.random.randn(self.n_agents)
        dx_dt += noise
        
        return dx_dt
    
    def simulate(self, t_span: Tuple[float, float], n_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Simule la dynamique de la confiance sur le réseau."""
        t = np.linspace(t_span[0], t_span[1], n_points)
        x0 = np.random.uniform(0.3, 0.8, self.n_agents)
        
        solution = odeint(self.confidence_dynamics, x0, t)
        return t, solution
    
    def compute_baseline(self, t: np.ndarray, solution: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calcule les indicateurs de confiance."""
        x_mean = np.mean(solution, axis=1)
        x_std = np.std(solution, axis=1)
        return x_mean, x_std
    
    def detect_consensus(self, t: np.ndarray, x_mean: np.ndarray) -> float:
        """Détecte le temps de convergence de la confiance."""
        threshold = 0.01
        for i in range(1, len(t)):
            if np.abs(x_mean[i] - x_mean[i-1]) < threshold:
                return t[i]
        return t[-1]

class NeuroeconomicModel:
    """Modèle neuroéconomique de la décision monétaire."""
    
    def __init__(self, alpha: float = 0.5, beta: float = 0.3):
        self.alpha = alpha  # Poids du circuit des impulsions
        self.beta = beta    # Poids du cortex préfrontal
        
    def decision_function(self, A: float, P: float) -> float:
        """Fonction de décision neuroéconomique."""
        # A = activité du circuit des impulsions
        # P = activité du cortex préfrontal (contrôle)
        return self.alpha * A / (self.beta * P + 1e-6)
    
    def simulate_decision(self, A: np.ndarray, P: np.ndarray) -> np.ndarray:
        """Simule les décisions à partir des activités neuronales."""
        return self.decision_function(A, P)

def plot_confidence_network():
    """Visualise la simulation du réseau de confiance."""
    network = ConfidenceNetwork(n_agents=50, p_connection=0.15, gamma=0.3)
    t, sol = network.simulate((0, 50), 500)
    x_mean, x_std = network.compute_baseline(t, sol)
    consensus_time = network.detect_consensus(t, x_mean)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Évolution de la confiance
    axes[0].plot(t, x_mean, 'b-', linewidth=2, label='Confiance moyenne')
    axes[0].fill_between(t, x_mean - x_std, x_mean + x_std, alpha=0.3, color='blue')
    axes[0].axhline(y=0.5, color='r', linestyle='--', label='Seuil de basculement')
    axes[0].axvline(x=consensus_time, color='g', linestyle='--', label=f'Consensus à t={consensus_time:.1f}')
    axes[0].set_ylabel('Confiance')
    axes[0].set_xlabel('Temps')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    axes[0].set_title('Dynamique de la Confiance Monétaire\n(Processus Mimétique)')
    
    # Distribution finale de la confiance
    final_confidence = sol[-1, :]
    axes[1].hist(final_confidence, bins=20, color='blue', alpha=0.7, edgecolor='black')
    axes[1].axvline(x=0.5, color='r', linestyle='--', label='Seuil de basculement')
    axes[1].set_xlabel('Confiance')
    axes[1].set_ylabel('Fréquence')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    axes[1].set_title(f'Distribution Finale de la Confiance\n(Écart-type = {x_std[-1]:.3f})')
    
    plt.tight_layout()
    plt.savefig('confidence_network_simulation.png', dpi=300)
    plt.show()
    
    print(f"\n=== RAPPORT DE CONFIANCE ===")
    print(f"Confiance moyenne initiale : {np.mean(sol[0, :]):.3f}")
    print(f"Confiance moyenne finale : {x_mean[-1]:.3f}")
    print(f"Écart-type final : {x_std[-1]:.3f}")
    print(f"Temps de consensus : {consensus_time:.1f}")
    if x_mean[-1] > 0.5:
        print("✅ Le système atteint un consensus favorable à la monnaie.")
    else:
        print("⚠️ La confiance s'effondre, la monnaie perd sa légitimité.")
    
    return fig

if __name__ == "__main__":
    plot_confidence_network()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
thermodynamic_economics.py

Modélisation thermodynamique de l'économie (entropie, énergie,
structures dissipatives).

Auteur : Marc Daghar
Licence : CC BY-SA 4.0
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from dataclasses import dataclass

@dataclass
class ThermodynamicParams:
    """Paramètres thermodynamiques de l'économie."""
    S0: float = 0.0           # Entropie initiale
    sigma_max: float = 1.0    # Capacité dissipative maximale
    tau: float = 10.0         # Constante de temps
    E_exo0: float = 100.0     # Énergie exosomatique initiale
    E_endo0: float = 50.0     # Énergie endosomatique initiale
    lambda_exo: float = 0.05  # Taux de croissance exosomatique
    lambda_endo: float = 0.02 # Taux de croissance endosomatique
    mu: float = 0.01          # Taux de dissipation

class ThermodynamicEconomy:
    """Système économique avec contraintes thermodynamiques."""
    
    def __init__(self, params: ThermodynamicParams):
        self.params = params
    
    def entropy_dynamics(self, state: np.ndarray, t: float) -> np.ndarray:
        """Équation d'évolution de l'entropie.
        
        state = [S, E_exo, E_endo]
        """
        S, E_exo, E_endo = state
        p = self.params
        
        # Production d'entropie par l'activité économique
        production_entropie = p.lambda_exo * E_exo + p.lambda_endo * E_endo
        
        # Capacité dissipative de l'écosystème
        dissipation_max = p.sigma_max * (1 - np.exp(-S / p.tau))
        
        # Évolution de l'entropie
        dS_dt = production_entropie - dissipation_max
        
        # Évolution des énergies
        dE_exo_dt = p.lambda_exo * E_exo * (1 - E_exo / p.E_exo0) - p.mu * E_exo
        dE_endo_dt = p.lambda_endo * E_endo * (1 - E_endo / p.E_endo0) - p.mu * E_endo
        
        return np.array([dS_dt, dE_exo_dt, dE_endo_dt])
    
    def simulate(self, t_span: Tuple[float, float], n_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Simule la thermodynamique de l'économie."""
        t = np.linspace(t_span[0], t_span[1], n_points)
        state0 = np.array([
            self.params.S0,
            self.params.E_exo0,
            self.params.E_endo0
        ])
        
        solution = odeint(self.entropy_dynamics, state0, t)
        return t, solution
    
    def compute_viability(self, t: np.ndarray, solution: np.ndarray) -> np.ndarray:
        """Calcule l'indicateur de viabilité thermodynamique."""
        S = solution[:, 0]
        viability = 1 - S / self.params.sigma_max
        return np.clip(viability, 0, 1)
    
    def detect_bifurcation(self, t: np.ndarray, solution: np.ndarray) -> List[float]:
        """Détecte les points de bifurcation (structures dissipatives)."""
        S = solution[:, 0]
        
        # Seuil de bifurcation : dérivée seconde de l'entropie change de signe
        dS = np.gradient(S, t[1] - t[0])
        ddS = np.gradient(dS, t[1] - t[0])
        
        bifurcation_points = []
        for i in range(1, len(ddS) - 1):
            if ddS[i-1] * ddS[i+1] < 0:
                bifurcation_points.append(t[i])
        
        return bifurcation_points

def plot_thermodynamic_economy():
    """Visualise la simulation thermodynamique."""
    params = ThermodynamicParams()
    economy = ThermodynamicEconomy(params)
    t, sol = economy.simulate((0, 100))
    
    S, E_exo, E_endo = sol.T
    viability = economy.compute_viability(t, sol)
    bifurcations = economy.detect_bifurcation(t, sol)
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Thermodynamique de l\'Économie\nEntropie, Énergie et Structures Dissipatives', fontsize=14)
    
    # Entropie
    axes[0, 0].plot(t, S, 'r-', linewidth=2, label='Entropie $S(t)$')
    axes[0, 0].axhline(y=params.sigma_max, color='g', linestyle='--', label='Capacité dissipative max')
    axes[0, 0].set_ylabel('Entropie')
    axes[0, 0].set_xlabel('Temps')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].legend()
    axes[0, 0].set_title('Production d\'Entropie')
    
    # Énergies
    axes[0, 1].plot(t, E_exo, 'b-', linewidth=2, label='Énergie exosomatique')
    axes[0, 1].plot(t, E_endo, 'g-', linewidth=2, label='Énergie endosomatique')
    axes[0, 1].set_ylabel('Énergie')
    axes[0, 1].set_xlabel('Temps')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    axes[0, 1].set_title('Évolution des Énergies')
    
    # Viabilité
    axes[1, 0].plot(t, viability, 'm-', linewidth=2, label='Indicateur de viabilité')
    axes[1, 0].axhline(y=0.5, color='r', linestyle='--', label='Seuil critique')
    axes[1, 0].set_ylabel('Viabilité')
    axes[1, 0].set_xlabel('Temps')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].legend()
    axes[1, 0].set_title('Viabilité Thermodynamique')
    
    # Bifurcations
    axes[1, 1].plot(t, S, 'r-', linewidth=1, alpha=0.5)
    for bp in bifurcations:
        axes[1, 1].axvline(x=bp, color='b', linestyle='--', alpha=0.7)
    axes[1, 1].set_ylabel('Entropie')
    axes[1, 1].set_xlabel('Temps')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_title(f'Points de Bifurcation (Structures Dissipatives)\n{bifurcations}')
    
    plt.tight_layout()
    plt.savefig('thermodynamic_economics.png', dpi=300)
    plt.show()
    
    print(f"\n=== RAPPORT THERMODYNAMIQUE ===")
    print(f"Entropie finale : {S[-1]:.3f}")
    print(f"Capacité dissipative max : {params.sigma_max:.3f}")
    print(f"Viabilité finale : {viability[-1]:.3f}")
    print(f"Nombre de bifurcations : {len(bifurcations)}")
    if viability[-1] > 0.5:
        print("✅ L'économie est viable thermodynamiquement.")
    else:
        print("⚠️ L'économie dépasse ses limites thermodynamiques.")
    
    return fig

if __name__ == "__main__":
    plot_thermodynamic_economy()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
agent_based_model.py

Modélisation multi-agents de l'économie islamique (pas d'usure,
zakat, guildes, awqaf).

Auteur : Marc Daghar
Licence : CC BY-SA 4.0
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class AgentParams:
    """Paramètres des agents économiques."""
    wealth: float = 100.0
    need: float = 0.5
    desire: float = 0.5
    trust: float = 0.7
    cooperation: float = 0.5
    zakat_rate: float = 0.025
    riba_aversion: float = 0.9

class IslamicAgent:
    """Agent économique islamique (pas d'usure, zakat, coopération)."""
    
    def __init__(self, params: AgentParams, agent_id: int):
        self.id = agent_id
        self.wealth = params.wealth
        self.need = params.need
        self.desire = params.desire
        self.trust = params.trust
        self.cooperation = params.cooperation
        self.zakat_rate = params.zakat_rate
        self.riba_aversion = params.riba_aversion
        
    def pay_zakat(self) -> float:
        """Paye la zakat (2.5% de la richesse)."""
        zakat = self.zakat_rate * self.wealth
        self.wealth -= zakat
        return zakat
    
    def cooperate(self, partner) -> float:
        """Coopération mutuelle (pas d'usure)."""
        if partner.trust > 0.5 and self.trust > 0.5:
            gain = 0.1 * (self.wealth + partner.wealth) * self.cooperation
            self.wealth += gain
            partner.wealth += gain
            return gain
        return 0.0
    
    def trade(self, partner, amount: float) -> bool:
        """Échange commercial sans usure."""
        if self.wealth >= amount:
            self.wealth -= amount
            partner.wealth += amount
            return True
        return False
    
    def invest_guild(self, guild) -> float:
        """Investissement dans une guilde (moyens de production en service)."""
        return guild.invest(self)

class Guild:
    """Guilde de production (moyens de production comme service)."""
    
    def __init__(self, name: str):
        self.name = name
        self.capital = 0.0
        self.members: List[IslamicAgent] = []
        
    def add_member(self, agent: IslamicAgent):
        self.members.append(agent)
        
    def invest(self, agent: IslamicAgent) -> float:
        """Investissement dans la guilde."""
        investment = agent.wealth * 0.1
        agent.wealth -= investment
        self.capital += investment
        return investment
    
    def produce(self) -> float:
        """Production collective de la guilde."""
        if len(self.members) == 0:
            return 0.0
        production = self.capital * 0.05 / len(self.members)
        for member in self.members:
            member.wealth += production
        return production * len(self.members)

class IslamicEconomy:
    """Système économique islamique multi-agents."""
    
    def __init__(self, n_agents: int = 50):
        self.n_agents = n_agents
        self.agents = self._initialize_agents()
        self.guilds = [Guild(f"Guilde_{i}") for i in range(5)]
        self.time = 0
        
    def _initialize_agents(self) -> List[IslamicAgent]:
        """Initialise les agents avec des paramètres aléatoires."""
        agents = []
        for i in range(self.n_agents):
            params = AgentParams(
                wealth=np.random.uniform(50, 150),
                need=np.random.uniform(0.3, 0.7),
                desire=np.random.uniform(0.3, 0.7),
                trust=np.random.uniform(0.4, 0.9),
                cooperation=np.random.uniform(0.3, 0.8),
                zakat_rate=0.025,
                riba_aversion=np.random.uniform(0.7, 1.0)
            )
            agents.append(IslamicAgent(params, i))
        return agents
    
    def step(self):
        """Une étape de simulation."""
        self.time += 1
        
        # 1. Paiement de la zakat
        for agent in self.agents:
            agent.pay_zakat()
        
        # 2. Coopération aléatoire
        for i in range(0, len(self.agents), 2):
            if i + 1 < len(self.agents):
                self.agents[i].cooperate(self.agents[i+1])
        
        # 3. Échanges commerciaux
        for i in range(len(self.agents)):
            j = np.random.randint(0, len(self.agents))
            if i != j:
                amount = np.random.uniform(1, 10)
                self.agents[i].trade(self.agents[j], amount)
        
        # 4. Investissement dans les guildes
        for agent in np.random.choice(self.agents, size=min(10, len(self.agents)), replace=False):
            guild = np.random.choice(self.guilds)
            agent.invest_guild(guild)
        
        # 5. Production des guildes
        for guild in self.guilds:
            guild.produce()
    
    def get_statistics(self) -> dict:
        """Retourne les statistiques du système."""
        wealths = [agent.wealth for agent in self.agents]
        trusts = [agent.trust for agent in self.agents]
        cooperations = [agent.cooperation for agent in self.agents]
        
        return {
            'total_wealth': sum(wealths),
            'mean_wealth': np.mean(wealths),
            'std_wealth': np.std(wealths),
            'gini_coefficient': self._gini_coefficient(wealths),
            'mean_trust': np.mean(trusts),
            'mean_cooperation': np.mean(cooperations),
            'guild_capital': sum(g.capital for g in self.guilds)
        }
    
    def _gini_coefficient(self, values: List[float]) -> float:
        """Calcule le coefficient de Gini."""
        sorted_values = np.sort(values)
        n = len(sorted_values)
        index = np.arange(1, n + 1)
        return (2 * np.sum(index * sorted_values)) / (n * np.sum(sorted_values)) - (n + 1) / n

def run_islamic_economy_simulation():
    """Exécute la simulation de l'économie islamique."""
    economy = IslamicEconomy(n_agents=100)
    n_steps = 200
    
    statistics = []
    
    for step in range(n_steps):
        economy.step()
        if step % 10 == 0:
            stats = economy.get_statistics()
            statistics.append(stats)
    
    # Affichage des résultats
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Simulation de l\'Économie Islamique\n(Aucune Usure, Zakat, Coopération)', fontsize=14)
    
    steps = np.arange(0, n_steps, 10)
    
    # Richesse totale
    axes[0, 0].plot(steps, [s['total_wealth'] for s in statistics], 'g-', linewidth=2)
    axes[0, 0].set_ylabel('Richesse Totale')
    axes[0, 0].set_xlabel('Temps')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_title('Croissance de la Richesse Totale')
    
    # Coefficient de Gini
    axes[0, 1].plot(steps, [s['gini_coefficient'] for s in statistics], 'b-', linewidth=2)
    axes[0, 1].axhline(y=0.3, color='r', linestyle='--', label='Seuil d\'inégalité')
    axes[0, 1].set_ylabel('Coefficient de Gini')
    axes[0, 1].set_xlabel('Temps')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    axes[0, 1].set_title('Réduction des Inégalités')
    
    # Confiance moyenne
    axes[1, 0].plot(steps, [s['mean_trust'] for s in statistics], 'm-', linewidth=2)
    axes[1, 0].set_ylabel('Confiance Moyenne')
    axes[1, 0].set_xlabel('Temps')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_title('Renforcement de la Confiance')
    
    # Capital des guildes
    axes[1, 1].plot(steps, [s['guild_capital'] for s in statistics], 'c-', linewidth=2)
    axes[1, 1].set_ylabel('Capital des Guildes')
    axes[1, 1].set_xlabel('Temps')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].set_title('Croissance du Capital Collectif')
    
    plt.tight_layout()
    plt.savefig('islamic_economy_simulation.png', dpi=300)
    plt.show()
    
    # Rapport final
    final_stats = statistics[-1]
    print(f"\n=== RAPPORT DE L'ÉCONOMIE ISLAMIQUE ===")
    print(f"Richesse totale : {final_stats['total_wealth']:.2f}")
    print(f"Richesse moyenne : {final_stats['mean_wealth']:.2f}")
    print(f"Coefficient de Gini : {final_stats['gini_coefficient']:.4f}")
    print(f"Confiance moyenne : {final_stats['mean_trust']:.3f}")
    print(f"Coopération moyenne : {final_stats['mean_cooperation']:.3f}")
    print(f"Capital des guildes : {final_stats['guild_capital']:.2f}")
    
    if final_stats['gini_coefficient'] < 0.3:
        print("✅ Les inégalités sont faibles, l'économie est équitable.")
    else:
        print("⚠️ Des inégalités persistent.")
    
    return fig

if __name__ == "__main__":
    run_islamic_economy_simulation()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
governance_model.py

Modélisation de la gouvernance économique :
- Régulation distribuée (rond-point) vs centralisée (feu de circulation)
- Dynamique de consensus

Auteur : Marc Daghar
Licence : CC BY-SA 4.0
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from typing import Tuple, List

class RoundaboutGovernance:
    """Gouvernance par rond-point (régulation distribuée)."""
    
    def __init__(self, n_agents: int = 50, coupling: float = 0.1):
        self.n_agents = n_agents
        self.coupling = coupling
        
    def consensus_dynamics(self, theta: np.ndarray, t: float) -> np.ndarray:
        """Dynamique de consensus (Kuramoto)."""
        dtheta_dt = np.zeros(self.n_agents)
        for i in range(self.n_agents):
            for j in range(self.n_agents):
                if i != j:
                    dtheta_dt[i] += self.coupling * np.sin(theta[j] - theta[i])
        return dtheta_dt
    
    def simulate(self, t_span: Tuple[float, float], n_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Simule la convergence vers un consensus."""
        t = np.linspace(t_span[0], t_span[1], n_points)
        theta0 = np.random.uniform(-np.pi, np.pi, self.n_agents)
        solution = odeint(self.consensus_dynamics, theta0, t)
        return t, solution
    
    def compute_order_parameter(self, theta: np.ndarray) -> float:
        """Calcule le paramètre d'ordre (consensus)."""
        r = np.abs(np.mean(np.exp(1j * theta)))
        return r

class TrafficLightGovernance:
    """Gouvernance par feu de circulation (régulation centralisée)."""
    
    def __init__(self, n_agents: int = 50, decision_rate: float = 0.1):
        self.n_agents = n_agents
        self.decision_rate = decision_rate
        self.state = np.zeros(n_agents)
        
    def step(self, central_command: float) -> np.ndarray:
        """Une étape de décision centralisée."""
        # Les agents suivent la commande centrale avec un délai
        self.state = self.state + self.decision_rate * (central_command - self.state)
        return self.state
    
    def simulate(self, t_span: Tuple[float, float], n_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """Simule la régulation centralisée."""
        t = np.linspace(t_span[0], t_span[1], n_points)
        states = np.zeros((n_points, self.n_agents))
        
        # Commandes centrales oscillantes
        for i, time in enumerate(t):
            central_command = 0.5 * np.sin(0.1 * time) + 0.5
            states[i] = self.step(central_command)
        
        return t, states

def plot_governance_comparison():
    """Compare les deux modes de gouvernance."""
    
    # 1. Rond-point
    roundabout = RoundaboutGovernance(n_agents=30, coupling=0.2)
    t_r, sol_r = roundabout.simulate((0, 50), 500)
    order_r = np.array([roundabout.compute_order_parameter(sol_r[i]) for i in range(len(sol_r))])
    
    # 2. Feu de circulation
    traffic = TrafficLightGovernance(n_agents=30, decision_rate=0.05)
    t_t, sol_t = traffic.simulate((0, 50), 500)
    order_t = np.array([np.std(sol_t[i]) for i in range(len(sol_t))])
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Gouvernance : Rond-Point vs Feu de Circulation\nRégulation Distribuée vs Centralisée', fontsize=14)
    
    # Trajectoires du rond-point
    axes[0, 0].plot(t_r, sol_r[:, :10], alpha=0.7)
    axes[0, 0].set_ylabel('Angle')
    axes[0, 0].set_xlabel('Temps')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].set_title('Rond-Point : Convergence des Agents')
    
    # Paramètre d'ordre du rond-point
    axes[0, 1].plot(t_r, order_r, 'g-', linewidth=2, label='Paramètre d\'ordre')
    axes[0, 1].axhline(y=0.9, color='r', linestyle='--', label='Seuil de consensus')
    axes[0, 1].set_ylabel('Consensus')
    axes[0, 1].set_xlabel('Temps')
    axes[0, 1].grid(True, alpha=0.3)
    axes[0, 1].legend()
    axes[0, 1].set_title('Rond-Point : Émergence du Consensus')
    
    # Trajectoires du feu de circulation
    axes[1, 0].plot(t_t, sol_t[:, :10], alpha=0.7)
    axes[1, 0].set_ylabel('État')
    axes[1, 0].set_xlabel('Temps')
    axes[1, 0].grid(True, alpha=0.3)
    axes[1, 0].set_title('Feu de Circulation : Réponse à la Commande Centrale')
    
    # Écart-type du feu de circulation
    axes[1, 1].plot(t_t, order_t, 'r-', linewidth=2, label='Écart-type')
    axes[1, 1].set_ylabel('Dispersion')
    axes[1, 1].set_xlabel('Temps')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].legend()
    axes[1, 1].set_title('Feu de Circulation : Dispersion des États')
    
    plt.tight_layout()
    plt.savefig('governance_comparison.png', dpi=300)
    plt.show()
    
    print(f"\n=== RAPPORT DE GOUVERNANCE ===")
    print(f"Consensus final (rond-point) : {order_r[-1]:.3f}")
    print(f"Dispersion finale (feu de circulation) : {order_t[-1]:.3f}")
    
    if order_r[-1] > 0.9:
        print("✅ Le rond-point permet une convergence efficace vers un consensus.")
    else:
        print("⚠️ Le rond-point n'atteint pas un consensus fort.")
    
    return fig

if __name__ == "__main__":
    plot_governance_comparison()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main_analysis.py

Script principal qui exécute toutes les simulations et génère
les visualisations pour l'article de Marc Daghar.

Auteur : Marc Daghar
Licence : CC BY-SA 4.0
"""

import os
import sys
import datetime
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Import des modules
from monetary_system_simulation import MonetarySystem, MonetaryParams, plot_system_simulation
from bimetallism_model import BimetallicSystem, BimetallicParams, plot_bimetallism
from confidence_network_model import ConfidenceNetwork, plot_confidence_network
from thermodynamic_economics import ThermodynamicEconomy, ThermodynamicParams, plot_thermodynamic_economy
from agent_based_model import IslamicEconomy, run_islamic_economy_simulation
from governance_model import RoundaboutGovernance, TrafficLightGovernance, plot_governance_comparison

def create_output_directory():
    """Crée le répertoire de sortie pour les figures."""
    output_dir = Path('results_daghar')
    output_dir.mkdir(exist_ok=True)
    return output_dir

def generate_all_simulations(output_dir: Path):
    """Génère toutes les simulations."""
    print("=" * 60)
    print("SIMULATION DU SYSTÈME MONÉTAIRE")
    print("Auteur : Marc Daghar")
    print("Date :", datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("Licence : CC BY-SA 4.0")
    print("=" * 60)
    
    # 1. Système monétaire usuraire
    print("\n[1/6] Simulation du système monétaire usuraire...")
    fig1 = plot_system_simulation()
    fig1.savefig(output_dir / '01_monetary_system.png', dpi=300)
    plt.close(fig1)
    print("✓ Terminé")
    
    # 2. Bimétallisme
    print("\n[2/6] Simulation du bimétallisme...")
    fig2 = plot_bimetallism()
    fig2.savefig(output_dir / '02_bimetallism.png', dpi=300)
    plt.close(fig2)
    print("✓ Terminé")
    
    # 3. Réseau de confiance
    print("\n[3/6] Simulation de la confiance monétaire...")
    fig3 = plot_confidence_network()
    fig3.savefig(output_dir / '03_confidence_network.png', dpi=300)
    plt.close(fig3)
    print("✓ Terminé")
    
    # 4. Thermodynamique
    print("\n[4/6] Simulation thermodynamique...")
    fig4 = plot_thermodynamic_economy()
    fig4.savefig(output_dir / '04_thermodynamic.png', dpi=300)
    plt.close(fig4)
    print("✓ Terminé")
    
    # 5. Économie islamique
    print("\n[5/6] Simulation de l'économie islamique...")
    fig5 = run_islamic_economy_simulation()
    fig5.savefig(output_dir / '05_islamic_economy.png', dpi=300)
    plt.close(fig5)
    print("✓ Terminé")
    
    # 6. Gouvernance
    print("\n[6/6] Simulation de la gouvernance...")
    fig6 = plot_governance_comparison()
    fig6.savefig(output_dir / '06_governance.png', dpi=300)
    plt.close(fig6)
    print("✓ Terminé")
    
    print("\n" + "=" * 60)
    print("TOUTES LES SIMULATIONS SONT TERMINÉES")
    print(f"Résultats sauvegardés dans : {output_dir.absolute()}")
    print("=" * 60)

def generate_report(output_dir: Path):
    """Génère un rapport HTML des résultats."""
    report_path = output_dir / 'report.html'
    
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Simulations - Marc Daghar</title>
    <style>
        body {{ font-family: 'Georgia', serif; max-width: 1200px; margin: auto; padding: 20px; }}
        h1, h2 {{ color: #2c3e50; }}
        .figure {{ border: 1px solid #ddd; margin: 20px 0; padding: 15px; }}
        .figure img {{ max-width: 100%; }}
        .footer {{ margin-top: 40px; border-top: 1px solid #ddd; padding-top: 20px; }}
        .license {{ color: #555; font-size: 0.9em; }}
    </style>
</head>
<body>
    <h1>Simulations Systémiques pour la Refondation Monétaire</h1>
    <p><strong>Auteur :</strong> Marc Daghar</p>
    <p><strong>Date :</strong> {datetime.datetime.now().strftime("%Y-%m-%d")}</p>
    <p><strong>Licence :</strong> CC BY-SA 4.0</p>
    <p><strong>Hébergement souverain :</strong> IMI - Université Renmin (Pékin) / ScienceData (CNKI)</p>
    
    <div class="figure">
        <h2>1. Système Monétaire Usuraire</h2>
        <img src="01_monetary_system.png" alt="Système monétaire">
        <p>Simulation des boucles rétroactives de la dette usuraire et des seuils d'effondrement.</p>
    </div>
    
    <div class="figure">
        <h2>2. Système Bimétallique (Or/Argent)</h2>
        <img src="02_bimetallism.png" alt="Bimétallisme">
        <p>Modélisation du bimétallisme avec mécanisme de Grondona résolvant la loi de Gresham.</p>
    </div>
    
    <div class="figure">
        <h2>3. Réseau de Confiance Monétaire</h2>
        <img src="03_confidence_network.png" alt="Confiance">
        <p>Dynamique de la confiance comme processus mimétique sur un réseau social.</p>
    </div>
    
    <div class="figure">
        <h2>4. Thermodynamique de l'Économie</h2>
        <img src="04_thermodynamic.png" alt="Thermodynamique">
        <p>Modélisation de l'entropie, des énergies exosomatiques/endosomatiques et des structures dissipatives.</p>
    </div>
    
    <div class="figure">
        <h2>5. Économie Islamique</h2>
        <img src="05_islamic_economy.png" alt="Économie islamique">
        <p>Simulation multi-agents d'une économie sans usure avec zakat, coopération et guildes.</p>
    </div>
    
    <div class="figure">
        <h2>6. Gouvernance : Rond-Point vs Feu de Circulation</h2>
        <img src="06_governance.png" alt="Gouvernance">
        <p>Comparaison entre régulation distribuée (consensus) et régulation centralisée (commande).</p>
    </div>
    
    <div class="footer">
        <p class="license">Cet œuvre est mise à disposition sous licence Creative Commons Attribution - Partage dans les mêmes conditions 4.0 International (CC BY-SA 4.0).</p>
        <p><em>"L'économie mondiale est telle un toxicomane au bord de l'overdose par l'usure. Il faut la sevrer pour qu'elle soit plus saine."</em> — Marc Daghar</p>
    </div>
</body>
</html>
"""
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Rapport HTML généré : {report_path.absolute()}")
    return report_path

if __name__ == "__main__":
    output_dir = create_output_directory()
    generate_all_simulations(output_dir)
    generate_report(output_dir)
    
    print("\n✅ Tous les fichiers ont été générés avec succès.")
    print(f"📁 Répertoire : {output_dir.absolute()}")
    print("\nPour exécuter les simulations individuellement :")
    print("  python monetary_system_simulation.py")
    print("  python bimetallism_model.py")
    print("  python confidence_network_model.py")
    print("  python thermodynamic_economics.py")
    print("  python agent_based_model.py")
    print("  python governance_model.py")

