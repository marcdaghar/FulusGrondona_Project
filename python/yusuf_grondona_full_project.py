"""
Modèle Yusuf-Grondona - Économie Bimétallique
=============================================
Modèle d'économie à deux monnaies basé sur la thermodynamique
de van der Waals, avec le principe contra-cyclique de Yusuf,
le système de Grondona et les cry-currencies.
"""

import numpy as np
from scipy.integrate import solve_ivp
from dataclasses import dataclass, field
from typing import Tuple, Dict, Optional, List
import yaml
import warnings
from pathlib import Path


@dataclass
class YusufGrondonaParams:
    """Paramètres du modèle Yusuf-Grondona."""
    
    # Paramètres thermodynamiques (van der Waals)
    a: float = 1.0       # Coefficient d'attraction économique
    b: float = 0.1       # Volume de survie minimum
    R: float = 1.0       # Constante économique
    
    # Paramètres de la production
    gamma: float = 0.5   # Coefficient de croissance
    delta: float = 0.3   # Coefficient d'amortissement
    
    # Régulation de Yusuf (température)
    mu: float = 0.4      # Sensibilité de l'offre à la production
    lambda_y: float = 0.8  # Force de rappel (Yusuf)
    sigma: float = 0.1   # Amplitude du bruit 1/f
    
    # Système de Grondona (stock)
    kappa: float = 0.3   # Coefficient d'accumulation du stock
    nu: float = 0.05     # Taux de dépréciation
    theta: float = 0.6   # Couplage stock ⇄ devise
    rho: float = 0.4     # Couplage température ⇄ devise
    
    # Dynamique de la devise (Yusuf)
    alpha: float = 0.7   # Force de régulation de la devise
    
    # Chocs exogènes
    shock_amplitude: float = 0.2
    shock_frequency: float = 0.02
    
    @property
    def Vc(self) -> float:
        """Volume critique (van der Waals)."""
        return 3.0 * self.b
    
    @property
    def Tc(self) -> float:
        """Température critique (van der Waals)."""
        return (8.0 * self.a) / (27.0 * self.R * self.b)
    
    @property
    def Pc(self) -> float:
        """Pression critique (van der Waals)."""
        return self.a / (27.0 * self.b * self.b)
    
    @property
    def stability_condition(self) -> bool:
        """Condition de stabilité : lambda_y > mu."""
        return self.lambda_y > self.mu


@dataclass
class YusufGrondonaState:
    """État du système économique."""
    
    V: float          # Volume de production
    T: float          # Température économique (offre)
    S: float          # Stock de monnaie tangible (Grondona)
    C: float          # Masse de devise symbolique (Yusuf)
    t: float = 0.0    # Temps
    
    @property
    def P(self) -> float:
        """Demande (pression) calculée par l'équation de van der Waals."""
        # (P + a/V²)(V - b) = R*T => P = R*T/(V - b) - a/V²
        V_eff = self.V - 0.01 * self.b  # Éviter division par zéro
        if V_eff <= 0:
            return 0.0
        return self.params.R * self.T / V_eff - self.params.a / (self.V * self.V)
    
    def to_array(self) -> np.ndarray:
        """Convertit l'état en tableau numpy."""
        return np.array([self.V, self.T, self.S, self.C])
    
    @classmethod
    def from_array(cls, arr: np.ndarray, t: float, params: YusufGrondonaParams):
        """Crée un état à partir d'un tableau."""
        return cls(V=arr[0], T=arr[1], S=arr[2], C=arr[3], t=t, params=params)


class YusufGrondonaModel:
    """Modèle d'économie bimétallique Yusuf-Grondona."""
    
    def __init__(self, params: YusufGrondonaParams, config: Optional[Dict] = None):
        """
        Initialise le modèle.
        
        Args:
            params: Paramètres du modèle
            config: Configuration supplémentaire (optionnel)
        """
        self.params = params
        self.config = config or {}
        self.rng = np.random.RandomState(self.config.get('seed', 42))
        self._state_history = []
        self._time_history = []
        
    def _compute_derivatives(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Calcule les dérivées du système d'équations.
        
        Args:
            t: Temps courant
            state: État [V, T, S, C]
            
        Returns:
            Dérivées [dV/dt, dT/dt, dS/dt, dC/dt]
        """
        V, T, S, C = state
        p = self.params
        
        # Éviter les divisions par zéro
        V_safe = max(V, 0.01 * p.b)
        V_eff = V_safe - p.b
        if V_eff <= 0:
            V_eff = 0.01 * p.b
        
        # Équation de van der Waals : P = R*T/(V - b) - a/V²
        P = p.R * T / V_eff - p.a / (V_safe * V_safe)
        
        # 1. Dynamique de la production (volume)
        # dV/dt = gamma * (V - b) * (R*T/(V-b) - a/V²) - delta * (V - Vc)/Vc
        growth_term = p.gamma * (V_safe - p.b) * P
        damping_term = p.delta * (V_safe - p.Vc) / p.Vc
        dV_dt = growth_term - damping_term
        
        # 2. Dynamique de la température (offre) - Principe de Yusuf
        # dT/dt = mu * T * (V - Vc)/Vc - lambda_y * (T - Tc) + bruit 1/f
        bruit = self._generate_1f_noise(t) * p.sigma
        dT_dt = (p.mu * T * (V_safe - p.Vc) / p.Vc 
                 - p.lambda_y * (T - p.Tc) 
                 + bruit)
        
        # 3. Dynamique du stock de monnaie (Grondona)
        # dS/dt = kappa * (T - Tc) - nu * S
        dS_dt = p.kappa * (T - p.Tc) - p.nu * S
        
        # 4. Dynamique de la devise (Yusuf)
        # dC/dt = -theta * dS/dt + rho * (T - Tc)
        dC_dt = -p.theta * dS_dt + p.rho * (T - p.Tc)
        
        # Application d'un choc exogène sur la production
        shock = self._generate_shock(t)
        dV_dt += shock * p.shock_amplitude * V_safe
        
        return np.array([dV_dt, dT_dt, dS_dt, dC_dt])
    
    def _generate_1f_noise(self, t: float) -> float:
        """Génère du bruit en 1/f (simulation d'auto-correlation)."""
        # Utilisation d'un processus d'Ornstein-Uhlenbeck pour approximer 1/f
        # avec une mémoire longue
        if not hasattr(self, '_noise_state'):
            self._noise_state = 0.0
            self._noise_tau = 0.1  # Temps de corrélation
        
        # Évolution du bruit
        dt = 0.01  # Pas de temps fixe
        self._noise_state = (self._noise_state 
                             * (1 - dt / self._noise_tau) 
                             + self.rng.randn() * np.sqrt(2 * dt / self._noise_tau))
        return self._noise_state
    
    def _generate_shock(self, t: float) -> float:
        """Génère un choc exogène périodique."""
        if self.params.shock_frequency > 0:
            return np.sin(2 * np.pi * self.params.shock_frequency * t)
        return 0.0
    
    def simulate(self, 
                 t_span: Tuple[float, float] = (0, 100),
                 dt: float = 0.01,
                 verbose: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simule le modèle sur une période donnée.
        
        Args:
            t_span: Intervalle de temps (début, fin)
            dt: Pas de temps
            verbose: Afficher la progression
            
        Returns:
            Tuple (temps, historique des états)
        """
        # Conditions initiales
        init_state = np.array([
            self.config.get('V0', 0.35),
            self.config.get('T0', 2.8),
            self.config.get('S0', 0.0),
            self.config.get('C0', 1.0)
        ])
        
        # Résolution numérique
        t_eval = np.arange(t_span[0], t_span[1], dt)
        
        # Utiliser solve_ivp pour une intégration robuste
        sol = solve_ivp(
            fun=lambda t, y: self._compute_derivatives(t, y),
            t_span=t_span,
            y0=init_state,
            t_eval=t_eval,
            method='LSODA',
            rtol=1e-6,
            atol=1e-8
        )
        
        if not sol.success:
            warnings.warn(f"La simulation a échoué: {sol.message}")
        
        # Stockage de l'historique
        self._time_history = sol.t
        self._state_history = sol.y.T
        
        if verbose:
            print(f"Simulation terminée: {len(sol.t)} pas de temps")
            print(f"État final: V={sol.y[0,-1]:.3f}, T={sol.y[1,-1]:.3f}, "
                  f"S={sol.y[2,-1]:.3f}, C={sol.y[3,-1]:.3f}")
        
        return sol.t, sol.y.T
    
    def get_demande(self) -> np.ndarray:
        """Calcule la demande (pression) sur tout l'historique."""
        if len(self._state_history) == 0:
            return np.array([])
        
        V = self._state_history[:, 0]
        T = self._state_history[:, 1]
        p = self.params
        
        V_safe = np.maximum(V, 0.01 * p.b)
        V_eff = V_safe - p.b
        V_eff = np.maximum(V_eff, 0.01 * p.b)
        
        P = p.R * T / V_eff - p.a / (V_safe * V_safe)
        return P
    
    def compute_metrics(self) -> Dict[str, float]:
        """Calcule les métriques économiques."""
        if len(self._state_history) == 0:
            return {}
        
        V = self._state_history[:, 0]
        T = self._state_history[:, 1]
        S = self._state_history[:, 2]
        C = self._state_history[:, 3]
        
        P = self.get_demande()
        
        # Métriques
        metrics = {
            'V_mean': np.mean(V),
            'V_std': np.std(V),
            'T_mean': np.mean(T),
            'T_std': np.std(T),
            'P_mean': np.mean(P),
            'P_std': np.std(P),
            'S_mean': np.mean(S),
            'S_std': np.std(S),
            'C_mean': np.mean(C),
            'C_std': np.std(C),
            'V_min': np.min(V),
            'V_max': np.max(V),
            'T_min': np.min(T),
            'T_max': np.max(T),
            'stability': self._compute_stability_metric(),
        }
        
        # Dette relative (S + C par rapport à la production)
        metrics['debt_ratio'] = (np.mean(np.abs(S) + np.abs(C)) / metrics['V_mean'])
        
        return metrics
    
    def _compute_stability_metric(self) -> float:
        """Calcule une métrique de stabilité du système."""
        if len(self._state_history) < 10:
            return 0.0
        
        V = self._state_history[:, 0]
        T = self._state_history[:, 1]
        p = self.params
        
        # Stabilité = écart quadratique moyen au point critique
        v_std = np.std(V - p.Vc)
        t_std = np.std(T - p.Tc)
        
        # Normalisation
        stability = 1.0 / (1.0 + v_std + t_std)
        return float(stability)
    
    def get_cycle_phases(self) -> List[str]:
        """Identifie les phases du cycle économique."""
        if len(self._state_history) < 4:
            return []
        
        V = self._state_history[:, 0]
        dV = np.gradient(V)
        d2V = np.gradient(dV)
        
        phases = []
        for i in range(len(V)):
            if dV[i] > 0 and d2V[i] > 0:
                phases.append('expansion')
            elif dV[i] > 0 and d2V[i] < 0:
                phases.append('stagflation')
            elif dV[i] < 0 and d2V[i] < 0:
                phases.append('crisis')
            else:
                phases.append('depression')
        
        return phases


def load_config(config_path: str = 'config.yaml') -> Dict:
    """Charge la configuration depuis un fichier YAML."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_model_from_config(config_path: str = 'config.yaml') -> YusufGrondonaModel:
    """Crée un modèle à partir d'un fichier de configuration."""
    config = load_config(config_path)
    params_dict = config.get('parameters', {})
    params = YusufGrondonaParams(**params_dict)
    
    sim_config = config.get('simulation', {})
    init_conditions = config.get('initial_conditions', {})
    
    full_config = {**sim_config, **init_conditions}
    
    return YusufGrondonaModel(params, full_config)


# Exemple d'utilisation
if __name__ == "__main__":
    # Création et simulation du modèle
    model = create_model_from_config('config.yaml')
    t, states = model.simulate(t_span=(0, 100), dt=0.01)
    
    # Calcul des métriques
    metrics = model.compute_metrics()
    print("\nMétriques économiques:")
    for key, value in metrics.items():
        print(f"  {key}: {value:.4f}")
    
    # Affichage des phases du cycle
    phases = model.get_cycle_phases()
    if phases:
        phase_counts = {p: phases.count(p) for p in set(phases)}
        print("\nPhases du cycle:")
        for phase, count in phase_counts.items():
            print(f"  {phase}: {count/len(phases)*100:.1f}%")
"""
Visualisation du modèle Yusuf-Grondona
======================================
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import rcParams
import warnings
from typing import Optional, Tuple, List, Dict
from pathlib import Path

# Configuration du style
plt.style.use('ggplot')
rcParams['figure.dpi'] = 150
rcParams['font.size'] = 10
rcParams['axes.labelsize'] = 11
rcParams['axes.titlesize'] = 12
rcParams['legend.fontsize'] = 9


def plot_phase_portrait(model, 
                        title: str = "Portrait de Phase du Modèle Yusuf-Grondona",
                        save_path: Optional[str] = None,
                        figsize: Tuple[int, int] = (12, 10)):
    """
    Trace le portrait de phase du système.
    
    Args:
        model: Instance du modèle
        title: Titre du graphique
        save_path: Chemin pour sauvegarder (optionnel)
        figsize: Taille de la figure
    """
    if len(model._state_history) == 0:
        raise ValueError("Le modèle doit être simulé avant la visualisation")
    
    states = model._state_history
    t = model._time_history
    p = model.params
    
    # Création de la figure
    fig = plt.figure(figsize=figsize)
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Évolution temporelle - Production et température
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(t, states[:, 0], 'b-', label='Production $V(t)$', linewidth=1.5)
    ax1.axhline(y=p.Vc, color='r', linestyle='--', label=f'$V_c$ = {p.Vc:.3f}', alpha=0.7)
    ax1.set_xlabel('Temps $t$')
    ax1.set_ylabel('Production $V$')
    ax1.set_title('Dynamique de la Production')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t, states[:, 1], 'g-', label='Offre $T(t)$', linewidth=1.5)
    ax2.axhline(y=p.Tc, color='r', linestyle='--', label=f'$T_c$ = {p.Tc:.3f}', alpha=0.7)
    ax2.set_xlabel('Temps $t$')
    ax2.set_ylabel('Offre $T$')
    ax2.set_title('Dynamique de l\'Offre')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 2. Stock de monnaie et devise
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.plot(t, states[:, 2], 'orange', label='Stock $S(t)$ (Grondona)', linewidth=1.5)
    ax3.plot(t, states[:, 3], 'purple', label='Devise $C(t)$ (Yusuf)', linewidth=1.5)
    ax3.set_xlabel('Temps $t$')
    ax3.set_ylabel('Valeur')
    ax3.set_title('Dynamique des Cry-Currencies')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 3. Portrait de phase (V, T)
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.plot(states[:, 0], states[:, 1], 'b-', alpha=0.8, linewidth=0.8)
    ax4.plot(states[0, 0], states[0, 1], 'go', label='Départ', markersize=10)
    ax4.plot(states[-1, 0], states[-1, 1], 'rs', label='Arrivée', markersize=10)
    ax4.plot(p.Vc, p.Tc, 'r*', label='Point critique', markersize=15, markeredgecolor='k')
    ax4.set_xlabel('Production $V$')
    ax4.set_ylabel('Offre $T$')
    ax4.set_title('Portrait de Phase $(V, T)$')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=14, fontweight='bold')
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Figure sauvegardée: {save_path}")
    
    plt.show()


def plot_van_der_waals_surface(model,
                               title: str = "Surface de van der Waals pour l'Économie",
                               save_path: Optional[str] = None,
                               figsize: Tuple[int, int] = (10, 8)):
    """
    Trace la surface de van der Waals avec la trajectoire du système.
    """
    from mpl_toolkits.mplot3d import Axes3D
    
    p = model.params
    
    # Création de la grille
    V_range = np.linspace(p.b * 1.1, p.b * 5, 50)
    T_range = np.linspace(p.Tc * 0.5, p.Tc * 2, 50)
    V_grid, T_grid = np.meshgrid(V_range, T_range)
    
    # Calcul de P (demande) via van der Waals
    V_eff = V_grid - p.b
    V_eff = np.maximum(V_eff, 0.01)
    P_grid = p.R * T_grid / V_eff - p.a / (V_grid * V_grid)
    P_grid = np.clip(P_grid, -5, 10)  # Éviter les divergences
    
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection='3d')
    
    # Surface de van der Waals
    surf = ax.plot_surface(V_grid, T_grid, P_grid, 
                          cmap='coolwarm', alpha=0.7, 
                          linewidth=0, antialiased=True)
    
    # Trajectoire du système
    if len(model._state_history) > 0:
        V = model._state_history[:, 0]
        T = model._state_history[:, 1]
        P = model.get_demande()
        
        ax.plot(V, T, P, 'k-', linewidth=2, label='Trajectoire')
        ax.scatter(V[0], T[0], P[0], color='green', s=80, label='Départ')
        ax.scatter(V[-1], T[-1], P[-1], color='red', s=80, label='Arrivée')
        
        # Point critique
        ax.scatter(p.Vc, p.Tc, p.Pc, color='gold', s=120, 
                  label='Point critique', marker='*')
    
    ax.set_xlabel('Volume $V$')
    ax.set_ylabel('Offre $T$')
    ax.set_zlabel('Demande $P$')
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.legend()
    
    # Ajustement de la vue
    ax.view_init(elev=25, azim=-60)
    
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Demande $P$')
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Figure sauvegardée: {save_path}")
    
    plt.show()


def plot_economic_cycles(model,
                         title: str = "Cycles Économiques et Phases de Transition",
                         save_path: Optional[str] = None,
                         figsize: Tuple[int, int] = (14, 6)):
    """
    Visualise les cycles économiques et les phases de transition.
    """
    if len(model._state_history) == 0:
        raise ValueError("Le modèle doit être simulé avant la visualisation")
    
    states = model._state_history
    t = model._time_history
    p = model.params
    
    V = states[:, 0]
    T = states[:, 1]
    S = states[:, 2]
    C = states[:, 3]
    
    # Identification des phases
    phases = model.get_cycle_phases()
    phase_colors = {
        'expansion': 'green',
        'stagflation': 'orange',
        'crisis': 'red',
        'depression': 'blue'
    }
    
    # Tracer les phases sur le portrait de phase
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # 1. Trajectoire colorée par phase
    if phases:
        for i, phase in enumerate(set(phases)):
            mask = np.array(phases) == phase
            if np.any(mask):
                ax1.plot(V[mask], T[mask], '.', color=phase_colors.get(phase, 'gray'), 
                        alpha=0.6, label=phase.capitalize(), markersize=1)
    
    ax1.plot(V, T, 'k-', alpha=0.3, linewidth=0.8)
    ax1.plot(p.Vc, p.Tc, 'r*', markersize=15, label='Point critique')
    ax1.set_xlabel('Production $V$')
    ax1.set_ylabel('Offre $T$')
    ax1.set_title('Cycle Économique - Portrait de Phase')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Indicateurs de stabilité
    ax2.plot(t, V, 'b-', label='Production', linewidth=1.5)
    ax2.plot(t, T, 'g-', label='Offre', linewidth=1.5)
    ax2.axhline(y=p.Vc, color='b', linestyle='--', alpha=0.5)
    ax2.axhline(y=p.Tc, color='g', linestyle='--', alpha=0.5)
    
    # Ajout des zones de récession (crisis)
    if phases:
        for i, phase in enumerate(phases):
            if phase == 'crisis' and i > 0 and phases[i-1] != 'crisis':
                # Début d'une crise
                start = t[i]
                # Trouver la fin de la crise
                j = i
                while j < len(phases) and phases[j] == 'crisis':
                    j += 1
                if j < len(phases):
                    end = t[j-1]
                    ax2.axvspan(start, end, alpha=0.2, color='red')
    
    ax2.set_xlabel('Temps $t$')
    ax2.set_ylabel('Valeur')
    ax2.set_title('Crises et Régulation')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=14, fontweight='bold')
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Figure sauvegardée: {save_path}")
    
    plt.show()


def plot_wealth_distribution(model,
                             title: str = "Distribution des Richesses (Loi de Pareto)",
                             save_path: Optional[str] = None,
                             figsize: Tuple[int, int] = (10, 6)):
    """
    Visualise la distribution des richesses selon la loi de Pareto.
    """
    # Simulation de la distribution des richesses
    # Basée sur les fluctuations du système
    if len(model._state_history) == 0:
        raise ValueError("Le modèle doit être simulé avant la visualisation")
    
    states = model._state_history
    p = model.params
    
    # Génération d'une distribution de Pareto à partir des fluctuations
    V = states[:, 0]
    T = states[:, 1]
    
    # Les fluctuations de production et d'offre génèrent une distribution de richesses
    wealth = np.abs(V - p.Vc) * np.abs(T - p.Tc)
    wealth = wealth / np.sum(wealth) * 1000  # Normalisation
    
    # Trier par ordre décroissant
    wealth_sorted = np.sort(wealth)[::-1]
    
    # Sélection des plus riches (seuil)
    threshold = 0.8  # Les 80% plus pauvres
    n_rich = int(len(wealth_sorted) * (1 - threshold))
    rich_wealth = wealth_sorted[:n_rich]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # 1. Distribution des richesses
    ax1.hist(wealth, bins=50, density=True, alpha=0.7, color='blue', edgecolor='black')
    ax1.set_xlabel('Richesse')
    ax1.set_ylabel('Densité de probabilité')
    ax1.set_title('Distribution des Richesses')
    ax1.set_yscale('log')
    ax1.grid(True, alpha=0.3)
    
    # 2. Courbe de Lorenz et coefficient de Gini
    # Tri cumulatif
    wealth_cum = np.cumsum(wealth_sorted)
    wealth_cum = wealth_cum / wealth_cum[-1]
    population = np.linspace(0, 1, len(wealth_cum))
    
    ax2.plot(population, wealth_cum, 'b-', linewidth=2, label='Courbe de Lorenz')
    ax2.plot([0, 1], [0, 1], 'r--', alpha=0.5, label='Égalité parfaite')
    
    # Calcul du coefficient de Gini (approximatif)
    gini = 1 - 2 * np.trapz(wealth_cum, population)
    
    ax2.set_xlabel('Population cumulée')
    ax2.set_ylabel('Richesse cumulée')
    ax2.set_title(f'Courbe de Lorenz - Gini = {gini:.3f}')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=14, fontweight='bold')
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Figure sauvegardée: {save_path}")
    
    plt.show()


def plot_all(model, save_dir: Optional[str] = None):
    """
    Génère toutes les visualisations principales.
    
    Args:
        model: Instance du modèle
        save_dir: Répertoire pour sauvegarder les figures (optionnel)
    """
    if save_dir:
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Portrait de phase
    plot_phase_portrait(
        model,
        save_path=str(save_dir / 'phase_portrait.png') if save_dir else None
    )
    
    # 2. Surface de van der Waals
    plot_van_der_waals_surface(
        model,
        save_path=str(save_dir / 'van_der_waals_surface.png') if save_dir else None
    )
    
    # 3. Cycles économiques
    plot_economic_cycles(
        model,
        save_path=str(save_dir / 'economic_cycles.png') if save_dir else None
    )
    
    # 4. Distribution des richesses
    plot_wealth_distribution(
        model,
        save_path=str(save_dir / 'wealth_distribution.png') if save_dir else None
    )


if __name__ == "__main__":
    # Test de la visualisation
    from yusuf_model import create_model_from_config
    
    model = create_model_from_config('config.yaml')
    model.simulate(t_span=(0, 100), dt=0.01)
    
    # Génération des figures
    plot_all(model, save_dir='results')
"""
Application Streamlit pour le modèle Yusuf-Grondona
==================================================
Interface interactive pour simuler et visualiser le modèle.
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yaml
from pathlib import Path

from yusuf_model import YusufGrondonaParams, YusufGrondonaModel


def main():
    st.set_page_config(
        page_title="Modèle Yusuf-Grondona",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("🏦 Modèle d'Économie Bimétallique Yusuf-Grondona")
    st.markdown("""
    Simulation d'une économie à deux monnaies basée sur la thermodynamique,
    avec le principe contra-cyclique de Yusuf, le système de Grondona,
    et les cry-currencies.
    """)
    
    # Sidebar - Paramètres
    st.sidebar.header("⚙️ Paramètres du Modèle")
    
    # Paramètres thermodynamiques
    st.sidebar.subheader("Thermodynamique (van der Waals)")
    a = st.sidebar.slider("a (attraction)", 0.1, 3.0, 1.0, 0.1)
    b = st.sidebar.slider("b (volume survie)", 0.01, 0.5, 0.1, 0.01)
    R = st.sidebar.slider("R (constante)", 0.5, 2.0, 1.0, 0.1)
    
    # Paramètres de régulation
    st.sidebar.subheader("Régulation")
    lambda_y = st.sidebar.slider("λ (Yusuf)", 0.1, 2.0, 0.8, 0.1)
    kappa = st.sidebar.slider("κ (Grondona)", 0.1, 1.0, 0.3, 0.05)
    theta = st.sidebar.slider("θ (couplage)", 0.1, 1.5, 0.6, 0.05)
    
    # Paramètres de simulation
    st.sidebar.subheader("Simulation")
    t_max = st.sidebar.slider("Durée", 10, 200, 100, 10)
    dt = st.sidebar.slider("Pas de temps", 0.005, 0.05, 0.01, 0.005)
    
    # Conditions initiales
    st.sidebar.subheader("Conditions Initiales")
    V0 = st.sidebar.slider("V₀ (production)", 0.1, 1.0, 0.35, 0.05)
    T0 = st.sidebar.slider("T₀ (offre)", 1.0, 5.0, 2.8, 0.1)
    
    # Bouton de simulation
    if st.sidebar.button("🚀 Lancer la simulation", type="primary"):
        run_simulation(a, b, R, lambda_y, kappa, theta, V0, T0, t_max, dt)
    
    # Information sur le modèle
    with st.sidebar.expander("📖 À propos"):
        st.markdown("""
        **Modèle Yusuf-Grondona**
        
        Ce modèle simule une économie bimétallique avec:
        - **Monnaie tangible** (réserve de valeur) → Grondona
        - **Devise symbolique** (intermédiaire) → Yusuf
        - **Cry-currencies** (régulation contra-cyclique)
        
        **Équations principales:**
        - Van der Waals: (P + a/V²)(V - b) = R·T
        - Yusuf: dT/dt = μ·T·(V-Vc)/Vc - λ·(T-Tc)
        - Grondona: dS/dt = κ·(T-Tc) - ν·S
        """
        )


def run_simulation(a, b, R, lambda_y, kappa, theta, V0, T0, t_max, dt):
    """Exécute et affiche la simulation."""
    
    # Création des paramètres
    params = YusufGrondonaParams(
        a=a, b=b, R=R,
        lambda_y=lambda_y,
        kappa=kappa,
        theta=theta
    )
    
    # Configuration
    config = {
        'V0': V0,
        'T0': T0,
        'S0': 0.0,
        'C0': 1.0,
        'dt': dt
    }
    
    # Simulation
    with st.spinner("Simulation en cours..."):
        model = YusufGrondonaModel(params, config)
        t, states = model.simulate(t_span=(0, t_max), dt=dt, verbose=False)
    
    # Affichage des métriques
    st.subheader("📊 Métriques Économiques")
    metrics = model.compute_metrics()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Production moyenne", f"{metrics['V_mean']:.3f}", 
                f"±{metrics['V_std']:.3f}")
    col2.metric("Offre moyenne", f"{metrics['T_mean']:.3f}", 
                f"±{metrics['T_std']:.3f}")
    col3.metric("Stabilité", f"{metrics['stability']:.3f}")
    col4.metric("Dette relative", f"{metrics['debt_ratio']:.3f}")
    
    # Graphiques interactifs avec Plotly
    st.subheader("📈 Dynamique du Système")
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Production V(t)', 'Offre T(t)',
                       'Stock et Devise', 'Portrait de Phase (V,T)'),
        vertical_spacing=0.15,
        horizontal_spacing=0.15
    )
    
    # 1. Production
    fig.add_trace(
        go.Scatter(x=t, y=states[:, 0], 
                  name='Production V(t)', 
                  line=dict(color='blue', width=2)),
        row=1, col=1
    )
    fig.add_hline(y=model.params.Vc, line_dash="dash", 
                  line_color="red", row=1, col=1,
                  annotation_text=f"Vc = {model.params.Vc:.3f}")
    
    # 2. Offre
    fig.add_trace(
        go.Scatter(x=t, y=states[:, 1], 
                  name='Offre T(t)',
                  line=dict(color='green', width=2)),
        row=1, col=2
    )
    fig.add_hline(y=model.params.Tc, line_dash="dash", 
                  line_color="red", row=1, col=2,
                  annotation_text=f"Tc = {model.params.Tc:.3f}")
    
    # 3. Stock et Devise
    fig.add_trace(
        go.Scatter(x=t, y=states[:, 2], 
                  name='Stock S (Grondona)',
                  line=dict(color='orange', width=2)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=t, y=states[:, 3], 
                  name='Devise C (Yusuf)',
                  line=dict(color='purple', width=2)),
        row=2, col=1
    )
    
    # 4. Portrait de phase
    fig.add_trace(
        go.Scatter(x=states[:, 0], y=states[:, 1],
                  name='Trajectoire (V,T)',
                  mode='lines',
                  line=dict(color='darkblue', width=1.5),
                  showlegend=True),
        row=2, col=2
    )
    fig.add_trace(
        go.Scatter(x=[model.params.Vc], y=[model.params.Tc],
                  name='Point critique',
                  mode='markers',
                  marker=dict(size=12, color='red', symbol='star'),
                  showlegend=True),
        row=2, col=2
    )
    
    # Mise à jour des axes
    fig.update_xaxes(title_text="Temps t", row=1, col=1)
    fig.update_xaxes(title_text="Temps t", row=1, col=2)
    fig.update_xaxes(title_text="Temps t", row=2, col=1)
    fig.update_xaxes(title_text="Production V", row=2, col=2)
    
    fig.update_yaxes(title_text="V", row=1, col=1)
    fig.update_yaxes(title_text="T", row=1, col=2)
    fig.update_yaxes(title_text="Valeur", row=2, col=1)
    fig.update_yaxes(title_text="Offre T", row=2, col=2)
    
    fig.update_layout(height=700, showlegend=True, 
                     title_font_size=14, hovermode='x unified')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse des cycles
    st.subheader("🔄 Phases du Cycle Économique")
    phases = model.get_cycle_phases()
    
    if phases:
        phase_counts = {}
        for p in phases:
            phase_counts[p] = phase_counts.get(p, 0) + 1
        
        # Barres de distribution
        fig_phases = go.Figure(data=[
            go.Bar(x=list(phase_counts.keys()), 
                   y=list(phase_counts.values()),
                   marker_color=['green', 'orange', 'red', 'blue'])
        ])
        fig_phases.update_layout(
            title="Distribution des Phases",
            xaxis_title="Phase",
            yaxis_title="Fréquence",
            height=300
        )
        st.plotly_chart(fig_phases, use_container_width=True)
    
    # Téléchargement des données
    st.subheader("📥 Téléchargement")
    df = pd.DataFrame({
        'temps': t,
        'production': states[:, 0],
        'offre': states[:, 1],
        'stock': states[:, 2],
        'devise': states[:, 3]
    })
    
    csv = df.to_csv(index=False)
    st.download_button(
        label="📊 Télécharger les données (CSV)",
        data=csv,
        file_name="yusuf_grondona_results.csv",
        mime="text/csv"
    )


if __name__ == "__main__":
    main()
"""
Script d'exécution unifié du modèle Yusuf-Grondona
==================================================
"""

import sys
from pathlib import Path
import logging
from datetime import datetime

# Ajout du chemin pour les imports
sys.path.append(str(Path(__file__).parent))

from yusuf_model import create_model_from_config
from visualize import plot_all
import streamlit as st


def setup_logging():
    """Configure le système de logging."""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f'yusuf_model_{datetime.now():%Y%m%d_%H%M%S}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def main():
    """Point d'entrée principal."""
    logger = setup_logging()
    logger.info("Démarrage du modèle Yusuf-Grondona")
    
    # Création du modèle
    logger.info("Chargement de la configuration...")
    model = create_model_from_config('config.yaml')
    
    # Simulation
    logger.info("Exécution de la simulation...")
    t, states = model.simulate(t_span=(0, 100), dt=0.01)
    
    # Affichage des métriques
    metrics = model.compute_metrics()
    logger.info("Métriques économiques:")
    for key, value in metrics.items():
        logger.info(f"  {key}: {value:.4f}")
    
    # Génération des visualisations
    logger.info("Génération des visualisations...")
    plot_all(model, save_dir='results')
    
    logger.info("Simulation terminée avec succès!")
    
    # Lancement de l'interface Streamlit (optionnel)
    print("\n" + "="*50)
    print("Modèle Yusuf-Grondona - Simulation terminée")
    print("="*50)
    print("Pour lancer l'interface interactive:")
    print("  streamlit run streamlit_app.py")
    print("="*50)


if __name__ == "__main__":
    main()
