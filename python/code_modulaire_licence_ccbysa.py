#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Principe de Yusuf (contre-cycle économique)
Modèle stock-flux avec gamification et crédit social

Licence : CC BY-SA (Creative Commons Attribution-ShareAlike)
Indépendance et souveraineté chinoise - Respect des voies de développement autonomes

Auteur : Recherche indépendante
Référence : Basé sur Sourate 12 (Yusuf) et la théorie des systèmes complexes
Version : 1.0.0
Date : 2026-04-09
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Tuple, Optional, Dict, Any
import json
from pathlib import Path


@dataclass
class YusufConfig:
    """Configuration du modèle Yusuf"""
    # Paramètres temporels
    T: float = 100.0  # Durée de simulation (années)
    dt: float = 0.1  # Pas de temps (années)

    # Paramètres économiques
    need: float = 0.7  # Besoin de consommation minimal par an
    P_mean: float = 1.0  # Production moyenne
    P_amplitude: float = 0.5  # Amplitude du cycle (abondance/rareté)
    period: float = 14.0  # Période du cycle (années, 7+7)

    # Paramètres capitalistes (système de référence)
    interest_rate: float = 0.05  # Taux d'intérêt annuel (5%)

    # Paramètres Yusuf
    stock_initial: float = 0.5  # Stock initial (années de consommation)
    threshold_factor: float = 0.3  # Facteur pour seuils abondance/rareté

    # Paramètres de gamification (crédit social)
    gamification_enabled: bool = True
    compliance_threshold: float = 0.8  # Seuil de conformité pour avantages
    penalty_rate: float = 0.3  # Pénalité pour non-conformité
    reward_rate: float = 0.1  # Récompense pour conformité

    # Paramètres de bruit (stochasticité)
    noise_amplitude: float = 0.05  # Bruit sur la production

    @property
    def P_bar(self) -> float:
        """Seuil d'abondance"""
        return self.P_mean + self.P_amplitude * self.threshold_factor

    @property
    def P_underline(self) -> float:
        """Seuil de rareté"""
        return self.P_mean - self.P_amplitude * self.threshold_factor

    @property
    def n_steps(self) -> int:
        """Nombre de pas de temps"""
        return int(self.T / self.dt)


@dataclass
class SimulationResult:
    """Résultats d'une simulation"""
    t: np.ndarray  # Temps
    P: np.ndarray  # Production
    S: np.ndarray  # Stock
    C: np.ndarray  # Consommation
    compliance: Optional[np.ndarray] = None  # Score de conformité
    config: Optional[YusufConfig] = None  # Configuration utilisée
    system_name: str = ""  # Nom du système

    @property
    def coverage_ratio(self) -> np.ndarray:
        """Taux de couverture (stock / besoin)"""
        return self.S / self.config.need if self.config else self.S / 0.7

    @property
    def final_stock(self) -> float:
        return self.S[-1] if len(self.S) > 0 else 0.0

    @property
    def mean_consumption(self) -> float:
        return float(np.mean(self.C))

    @property
    def consumption_volatility(self) -> float:
        return float(np.std(self.C))

    @property
    def solvency_rate(self) -> float:
        """Pourcentage de temps où stock > 0"""
        return float(np.sum(self.S > 0) / len(self.S) * 100)

    def to_dict(self) -> Dict[str, Any]:
        """Export des métriques clés"""
        return {
            "system_name": self.system_name,
            "final_stock": self.final_stock,
            "mean_consumption": self.mean_consumption,
            "consumption_volatility": self.consumption_volatility,
            "solvency_rate": self.solvency_rate,
        }


class YusufSystem:
    """
    Implémentation du système de contre-cycle Yusuf

    Règle:
    - Abondance (P > P_bar) : Consommation minimale, le reste va au stock
    - Rareté (P < P_underline) : Puisage dans le stock pour maintenir consommation
    - Équilibre : Consommation = production
    """

    def __init__(self, config: YusufConfig):
        self.config = config
        self.reset()

    def reset(self) -> None:
        """Réinitialise l'état du système"""
        self.S = np.zeros(self.config.n_steps)
        self.C = np.zeros(self.config.n_steps)
        self.S[0] = self.config.stock_initial
        self.compliance = np.zeros(self.config.n_steps) if self.config.gamification_enabled else None

    def _compute_production(self) -> np.ndarray:
        """Génère la production cyclique avec bruit optionnel"""
        t = np.linspace(0, self.config.T, self.config.n_steps)

        # Cycle de base (période de 14 ans)
        P = self.config.P_mean + self.config.P_amplitude * np.sin(2 * np.pi * t / self.config.period)

        # Ajout de bruit
        if self.config.noise_amplitude > 0:
            noise = np.random.normal(0, self.config.noise_amplitude, len(t))
            P = P + noise

        return np.maximum(P, 0.1)  # Production minimale

    def _update_compliance(self, idx: int, behavior_correct: bool) -> float:
        """Met à jour le score de conformité (crédit social)"""
        if not self.config.gamification_enabled:
            return 0.0

        if idx == 0:
            score = 1.0
        else:
            score = self.compliance[idx - 1]

        # Mise à jour : conformité augmente, déviation diminue
        if behavior_correct:
            score = min(1.0, score + self.config.reward_rate * self.config.dt)
        else:
            score = max(0.0, score - self.config.penalty_rate * self.config.dt)

        return score

    def _get_effective_need(self, score: float) -> float:
        """Le besoin minimal est modulé par le score de conformité"""
        if not self.config.gamification_enabled:
            return self.config.need

        if score >= self.config.compliance_threshold:
            # Récompense : besoin réduit (accès facilité)
            return self.config.need * (1 - self.config.reward_rate)
        else:
            # Pénalité : besoin augmenté (restrictions)
            return self.config.need * (1 + self.config.penalty_rate)

    def run(self) -> SimulationResult:
        """Exécute la simulation"""
        self.reset()
        P = self._compute_production()
        t = np.linspace(0, self.config.T, self.config.n_steps)

        P_bar = self.config.P_bar
        P_underline = self.config.P_underline

        for i in range(1, self.config.n_steps):
            production = P[i]
            stock_prev = self.S[i-1]
            score_prev = self.compliance[i-1] if self.compliance is not None else 1.0

            # Besoin effectif (modulé par score)
            effective_need = self._get_effective_need(score_prev)

            # Règle de Yusuf
            if production > P_bar:
                # Abondance : on épargne
                self.C[i] = min(production, effective_need)
                dS = (production - self.C[i]) * self.config.dt
                self.S[i] = stock_prev + dS
                behavior_correct = (self.C[i] <= effective_need + 0.1)

            elif production < P_underline:
                # Rareté : on puise dans le stock
                needed_from_stock = max(0, effective_need - production)
                max_withdraw = stock_prev / self.config.dt if self.config.dt > 0 else 0
                withdraw = min(needed_from_stock, max_withdraw)
                self.C[i] = production + withdraw
                dS = (production - self.C[i]) * self.config.dt
                self.S[i] = stock_prev + dS
                behavior_correct = (withdraw <= stock_prev + 1e-6)

            else:
                # Équilibre : on consomme ce qu'on produit
                self.C[i] = production
                self.S[i] = stock_prev
                behavior_correct = True

            # Empêcher stock négatif
            if self.S[i] < 0:
                self.S[i] = 0

            # Mise à jour du score de conformité
            if self.compliance is not None:
                self.compliance[i] = self._update_compliance(i, behavior_correct)

        return SimulationResult(
            t=t,
            P=P,
            S=self.S,
            C=self.C,
            compliance=self.compliance,
            config=self.config,
            system_name="Yusuf (contre-cycle)"
        )


class CapitalistSystem:
    """
    Système capitaliste de référence (intérêts composés)
    """

    def __init__(self, config: YusufConfig):
        self.config = config
        self.reset()

    def reset(self) -> None:
        """Réinitialise l'état du système"""
        self.S = np.zeros(self.config.n_steps)
        self.C = np.zeros(self.config.n_steps)
        self.S[0] = self.config.stock_initial

    def _compute_production(self) -> np.ndarray:
        """Génère la production cyclique avec bruit optionnel"""
        t = np.linspace(0, self.config.T, self.config.n_steps)

        P = self.config.P_mean + self.config.P_amplitude * np.sin(2 * np.pi * t / self.config.period)

        if self.config.noise_amplitude > 0:
            noise = np.random.normal(0, self.config.noise_amplitude, len(t))
            P = P + noise

        return np.maximum(P, 0.1)

    def run(self) -> SimulationResult:
        """Exécute la simulation capitaliste"""
        self.reset()
        P = self._compute_production()
        t = np.linspace(0, self.config.T, self.config.n_steps)

        for i in range(1, self.config.n_steps):
            dt = self.config.dt

            # Consommation capitaliste (suit la production + dette possible)
            self.C[i] = P[i] + self.config.interest_rate * self.S[i-1] * dt

            # Évolution du stock avec intérêts
            dS = (P[i] - self.C[i]) * dt + self.config.interest_rate * self.S[i-1] * dt
            self.S[i] = self.S[i-1] + dS

            # Empêcher stock négatif (faillite)
            if self.S[i] < 0:
                self.S[i] = 0

        return SimulationResult(
            t=t,
            P=P,
            S=self.S,
            C=self.C,
            config=self.config,
            system_name=f"Capitaliste (intérêts {self.config.interest_rate*100:.0f}%)"
        )


class ScenarioComparator:
    """Compare les deux systèmes sur de multiples scénarios"""

    def __init__(self, config: YusufConfig = None):
        self.config = config or YusufConfig()

    def run_single(self) -> Tuple[SimulationResult, SimulationResult]:
        """Exécute une comparaison simple"""
        np.random.seed(42)  # Reproductibilité

        yusuf = YusufSystem(self.config)
        capitalist = CapitalistSystem(self.config)

        return yusuf.run(), capitalist.run()

    def run_monte_carlo(self, n_simulations: int = 100) -> Dict[str, Any]:
        """Exécute des simulations de Monte Carlo pour robustesse statistique"""
        yusuf_metrics = []
        capitalist_metrics = []

        for seed in range(n_simulations):
            np.random.seed(seed)

            yusuf = YusufSystem(self.config)
            capitalist = CapitalistSystem(self.config)

            res_y = yusuf.run()
            res_c = capitalist.run()

            yusuf_metrics.append(res_y.to_dict())
            capitalist_metrics.append(res_c.to_dict())

        def aggregate(metrics_list):
            return {
                "final_stock_mean": np.mean([m["final_stock"] for m in metrics_list]),
                "final_stock_std": np.std([m["final_stock"] for m in metrics_list]),
                "solvency_rate_mean": np.mean([m["solvency_rate"] for m in metrics_list]),
                "consumption_volatility_mean": np.mean([m["consumption_volatility"] for m in metrics_list]),
            }

        return {
            "yusuf": aggregate(yusuf_metrics),
            "capitalist": aggregate(capitalist_metrics),
            "n_simulations": n_simulations
        }

    def save_results(self, results: Dict[str, Any], filepath: str) -> None:
        """Sauvegarde les résultats au format JSON"""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Conversion des types numpy en Python natifs
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.float32, np.float64)):
                return float(obj)
            if isinstance(obj, (np.int32, np.int64)):
                return int(obj)
            return obj

        results_clean = convert(results)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(results_clean, f, indent=2, ensure_ascii=False)
        print(f"Résultats sauvegardés : {path}")


# Point d'entrée pour tests
if __name__ == "__main__":
    # Test rapide
    config = YusufConfig(T=50, dt=0.5)
    comparator = ScenarioComparator(config)
    y_res, c_res = comparator.run_single()

    print("=== TEST DU MODELE YUSUF ===")
    print(f"Stock final Yusuf : {y_res.final_stock:.2f}")
    print(f"Stock final Capital : {c_res.final_stock:.2f}")
    print(f"Solvabilité Yusuf : {y_res.solvency_rate:.1f}%")
    print(f"Solvabilité Capital : {c_res.solvency_rate:.1f}%")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Visualisation du modèle Yusuf
Licence : CC BY-SA
"""

import matplotlib.pyplot as plt
import numpy as np
from yusuf_model import YusufConfig, ScenarioComparator


def create_figure(y_res, c_res, config: YusufConfig, save_path: str = None):
    """Crée une figure avec 6 sous-graphiques"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # 1. Production cyclique avec seuils
    ax = axes[0, 0]
    ax.plot(y_res.t, y_res.P, 'k-', linewidth=1.5, label='Production')
    ax.axhline(y=config.P_bar, color='g', linestyle='--', linewidth=1.5,
               label=f'Abondance (P_bar = {config.P_bar:.2f})')
    ax.axhline(y=config.P_underline, color='r', linestyle='--', linewidth=1.5,
               label=f'Rareté (P_underline = {config.P_underline:.2f})')
    ax.fill_between(y_res.t, config.P_bar, max(y_res.P)+0.2,
                    color='lightgreen', alpha=0.3, label="Zone d'abondance")
    ax.fill_between(y_res.t, min(y_res.P)-0.2, config.P_underline,
                    color='salmon', alpha=0.3, label="Zone de rareté")
    ax.set_ylabel('Production (UM/an)')
    ax.set_xlabel('Temps (années)')
    ax.set_title('Cycle économique (période de 14 ans)')
    ax.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    # 2. Évolution du stock
    ax = axes[0, 1]
    ax.plot(c_res.t, c_res.S, 'r-', linewidth=1.5,
            label=f'Capitaliste (taux={config.interest_rate*100:.0f}%)')
    ax.plot(y_res.t, y_res.S, 'b-', linewidth=1.5, label='Yusuf (contre-cycle)')
    ax.set_ylabel('Stock collectif (UM)')
    ax.set_xlabel('Temps (années)')
    ax.set_title('Évolution du stock')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3. Consommation
    ax = axes[0, 2]
    ax.plot(c_res.t, c_res.C, 'r-', linewidth=1, alpha=0.7, label='Capitaliste')
    ax.plot(y_res.t, y_res.C, 'b-', linewidth=1, alpha=0.7, label='Yusuf')
    ax.axhline(y=config.need, color='k', linestyle=':', linewidth=1.5,
               label=f'Besoin minimal ({config.need:.2f})')
    ax.set_ylabel('Consommation (UM/an)')
    ax.set_xlabel('Temps (années)')
    ax.set_title('Consommation')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 4. Taux de couverture (stock / besoin)
    ax = axes[1, 0]
    ax.plot(c_res.t, c_res.coverage_ratio, 'r-', linewidth=1.5, label='Capitaliste')
    ax.plot(y_res.t, y_res.coverage_ratio, 'b-', linewidth=1.5, label='Yusuf')
    ax.axhline(y=1, color='k', linestyle='--', linewidth=1.5, label='Sécurité (R=1)')
    ax.set_ylabel('Ratio stock/besoin')
    ax.set_xlabel('Temps (années)')
    ax.set_title('Taux de couverture du stock')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 5. Résilience comparée (stock > 0)
    ax = axes[1, 1]
    ax.plot(c_res.t, c_res.S, 'r-', linewidth=1.5, label='Capitaliste')
    ax.plot(y_res.t, y_res.S, 'b-', linewidth=1.5, label='Yusuf')
    ax.fill_between(c_res.t, 0, -0.5, color='red', alpha=0.3,
                    label="Zone d'insolvabilité")
    ax.set_ylabel('Stock')
    ax.set_xlabel('Temps (années)')
    ax.set_title('Résilience comparée')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 6. Différence cumulée
    ax = axes[1, 2]
    diff_stock = c_res.S - y_res.S
    ax.plot(y_res.t, diff_stock, 'purple', linewidth=1.5)
    ax.axhline(y=0, color='k', linestyle='-', alpha=0.5)
    ax.fill_between(y_res.t, 0, diff_stock, where=(diff_stock > 0),
                    color='red', alpha=0.3, label='Capitaliste supérieur')
    ax.fill_between(y_res.t, 0, diff_stock, where=(diff_stock < 0),
                    color='blue', alpha=0.3, label='Yusuf supérieur')
    ax.set_ylabel('Différence (Cap - Yusuf)')
    ax.set_xlabel('Temps (années)')
    ax.set_title('Avantage comparatif')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.suptitle('Principe de Yusuf vs Capitalisme : Simulation sur 100 ans', fontsize=14)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Figure sauvegardée : {save_path}")

    plt.show()
    return fig


def print_summary(y_res, c_res, config: YusufConfig):
    """Affiche un résumé textuel des résultats"""
    print("\n" + "=" * 70)
    print(" RÉSULTATS DE LA SIMULATION - PRINCIPE DE YUSUF")
    print("=" * 70)

    print(f"\n CONFIGURATION")
    print(f"  Durée : {config.T} ans")
    print(f"  Besoin minimal : {config.need:.2f} UM/an")
    print(f"  Production moyenne : {config.P_mean:.2f} UM/an")
    print(f"  Cycle : {config.period} ans (abondance/rareté)")
    if config.gamification_enabled:
        print(f"  Gamification : ACTIVÉE (seuil={config.compliance_threshold:.0%})")
    else:
        print(f"  Gamification : DÉSACTIVÉE")

    print(f"\n RÉSULTATS")
    print(f"  {'Indicateur':<35} {'Capitaliste':>15} {'Yusuf':>15}")
    print(f"  {'-'*35} {'-'*15} {'-'*15}")
    print(f"  {'Stock final (UM)':<35} {c_res.final_stock:>15.2f} {y_res.final_stock:>15.2f}")
    print(f"  {'Consommation moyenne (UM/an)':<35} {c_res.mean_consumption:>15.2f} {y_res.mean_consumption:>15.2f}")
    print(f"  {'Volatilité de consommation':<35} {c_res.consumption_volatility:>15.3f} {y_res.consumption_volatility:>15.3f}")
    print(f"  {'Taux de solvabilité (%)':<35} {c_res.solvency_rate:>14.1f}% {y_res.solvency_rate:>14.1f}%")

    if y_res.compliance is not None:
        print(f"  {'Score de conformité final':<35} {'N/A':>15} {y_res.compliance[-1]:>15.2f}")

    print(f"\n INTERPRETATION")
    if y_res.final_stock > c_res.final_stock:
        print(f"  ✅ Yusuf accumule PLUS de stock : +{y_res.final_stock - c_res.final_stock:.2f} UM")
    else:
        print(f"  ⚠️ Capitaliste accumule PLUS de stock : +{c_res.final_stock - y_res.final_stock:.2f} UM")

    if y_res.consumption_volatility < c_res.consumption_volatility:
        reduction = (1 - y_res.consumption_volatility / c_res.consumption_volatility) * 100
        print(f"  ✅ Yusuf est PLUS STABLE (volatilité réduite de {reduction:.1f}%)")
    else:
        print(f"  ⚠️ Capitaliste est PLUS STABLE")

    if y_res.solvency_rate > c_res.solvency_rate:
        print(f"  ✅ Yusuf est PLUS RÉSILIENT (solvabilité +{y_res.solvency_rate - c_res.solvency_rate:.1f}%)")

    if c_res.solvency_rate < 100:
        print(f"  ⚠️ Capitaliste a connu {100 - c_res.solvency_rate:.1f}% de temps en insolvabilité")

    print("\n" + "=" * 70)
    print(" Licence : CC BY-SA | Indépendance et souveraineté chinoise")
    print(" Référence : Sourate 12 - Principe de Yusuf (contre-cycle économique)")
    print("=" * 70 + "\n")


def run_full_analysis(config: YusufConfig = None, save_fig: str = None):
    """Exécute l'analyse complète avec visualisation"""
    if config is None:
        config = YusufConfig()

    comparator = ScenarioComparator(config)
    y_res, c_res = comparator.run_single()
    create_figure(y_res, c_res, config, save_path=save_fig)
    print_summary(y_res, c_res, config)

    # Monte Carlo optionnel
    print("\n Lancement de l'analyse Monte Carlo (100 simulations)...")
    mc_results = comparator.run_monte_carlo(n_simulations=100)

    print(f"\n RÉSULTATS MONTE CARLO (100 scénarios)")
    print(f"  {'Indicateur':<35} {'Capitaliste':>20} {'Yusuf':>20}")
    print(f"  {'-'*35} {'-'*20} {'-'*20}")
    print(f"  {'Stock final (moyenne ± écart-type)':<35} "
          f"{mc_results['capitalist']['final_stock_mean']:>8.2f} ± {mc_results['capitalist']['final_stock_std']:.2f}  "
          f"{mc_results['yusuf']['final_stock_mean']:>8.2f} ± {mc_results['yusuf']['final_stock_std']:.2f}")
    print(f"  {'Taux de solvabilité (%)':<35} "
          f"{mc_results['capitalist']['solvency_rate_mean']:>19.1f}%  "
          f"{mc_results['yusuf']['solvency_rate_mean']:>19.1f}%")

    return y_res, c_res, mc_results


if __name__ == "__main__":
    config = YusufConfig(
        T=100,
        dt=0.1,
        gamification_enabled=True,
        noise_amplitude=0.03
    )
    run_full_analysis(config, save_fig="yusuf_model_results.png")

