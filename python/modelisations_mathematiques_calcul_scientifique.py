# -*- coding: utf-8 -*-
"""
MODÉLISATIONS POUR LA THÈSE - CRYPTO-FULUS ET SYSTÈME USURAIRE
Auteur: [Votre Nom]
Date: 2026

Contenu:
1. Modélisation du déclin du système usuraire
2. Contrat Mudaraba (simulation)
3. Supériorité Mudaraba vs Marchés Financiers
4. Dynamique de déploiement des guildes (logistique)
5. Bifurcation du système monétaire
6. Optimisation de l'effort personnel
7. Visualisations
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.optimize import minimize
from scipy.stats import norm
import matplotlib
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['figure.figsize'] = (10, 6)

# Pour les accents dans les graphiques
plt.rcParams['axes.unicode_minus'] = False

# ============================================================================
# 1. MODÉLISATION DU DÉCLIN DU SYSTÈME USURAIRE
# ============================================================================

def decline_model(S, t, r, S_min):
    """
    Modèle de décroissance logistique avec seuil critique.
    dS/dt = -r * S * (1 - S/S_min)
    
    Paramètres:
    - S: santé du système usuraire (0 à 1)
    - t: temps
    - r: taux de déclin
    - S_min: seuil minimal (en dessous duquel effondrement)
    """
    return -r * S * (1 - S/S_min)

def simulate_decline(S0=1.0, r=0.08, S_min=0.01, t_max=100, n_points=1000):
    """
    Simule le déclin du système usuraire sur une période donnée.
    """
    t = np.linspace(0, t_max, n_points)
    S = odeint(decline_model, S0, t, args=(r, S_min))
    
    # Ajout de bruit (politiques de sauvetage)
    np.random.seed(42)
    noise = 0.02 * np.random.randn(n_points)
    S_noisy = S.flatten() + noise
    S_noisy = np.clip(S_noisy, 0, 1)
    
    return t, S_noisy

def long_tail_decline(S0=1.0, lam=0.03, t_max=100, n_points=1000):
    """
    Modèle de "longue traînée" - déclin exponentiel.
    S(t) = S0 * exp(-lambda * t)
    """
    t = np.linspace(0, t_max, n_points)
    S = S0 * np.exp(-lam * t)
    
    # Ajout de bruit
    np.random.seed(42)
    noise = 0.01 * np.random.randn(n_points)
    S_noisy = S + noise
    S_noisy = np.clip(S_noisy, 0, S0)
    
    return t, S_noisy


# ============================================================================
# 2. CONTRAT MUDARABA (SIMULATION)
# ============================================================================

class MudarabaContract:
    """
    Simulation d'un contrat Mudaraba authentique selon le Muwatta de Malik.
    """
    
    def __init__(self, capitals, alpha_shares, purchase_price, quantity):
        """
        Initialise le contrat.
        
        Paramètres:
        - capitals: liste des capitaux apportés par chaque commerçant [K1, K2, ...]
        - alpha_shares: liste des parts de profit [alpha1, alpha2, ...]
        - purchase_price: prix d'achat unitaire
        - quantity: quantité de marchandises
        """
        self.capitals = np.array(capitals)
        self.alpha_shares = np.array(alpha_shares)
        self.K = np.sum(self.capitals)
        self.beta_shares = self.capitals / self.K
        self.purchase_price = purchase_price
        self.quantity = quantity
        self.n = len(capitals)
        
        # Vérification des contraintes
        assert np.sum(self.alpha_shares) == 1.0, "Les parts de profit doivent sommer à 1"
        assert np.sum(self.beta_shares) == 1.0, "Les parts de capital doivent sommer à 1"
    
    def simulate_sale(self, sale_price, verbose=False):
        """
        Simule une vente à un prix donné.
        
        Retourne les gains/pertes pour chaque participant.
        """
        R = sale_price * self.quantity
        profits = R - self.K
        
        if profits >= 0:
            # Cas de profit
            gains = self.capitals + self.alpha_shares * profits
            if verbose:
                print(f"Profit: {profits:.2f}")
                for i, g in enumerate(gains):
                    print(f"  Participant {i+1}: gain = {g:.2f} (rendement: {(g/self.capitals[i]-1)*100:.1f}%)")
            return gains, profits
        else:
            # Cas de perte
            loss = -profits
            losses_share = self.beta_shares * loss
            gains = self.capitals - losses_share
            if verbose:
                print(f"Perte: {loss:.2f}")
                for i, g in enumerate(gains):
                    print(f"  Participant {i+1}: perte = {losses_share[i]:.2f}, gain = {g:.2f}")
            return gains, profits
    
    def expected_return(self, sale_price_dist, n_simulations=10000):
        """
        Calcule le rendement espéré pour chaque participant.
        
        Paramètres:
        - sale_price_dist: distribution du prix de vente (moyenne, écart-type)
        """
        mu, sigma = sale_price_dist
        sale_prices = np.random.normal(mu, sigma, n_simulations)
        
        all_gains = []
        for p in sale_prices:
            gains, _ = self.simulate_sale(p)
            all_gains.append(gains)
        
        all_gains = np.array(all_gains)
        expected_gains = np.mean(all_gains, axis=0)
        
        return expected_gains


# ============================================================================
# 3. SUPÉRIORITÉ MUDARABA vs MARCHÉS FINANCIERS
# ============================================================================

def financial_market_return(dividend=0.02, capital_gain_mean=0.05, capital_gain_std=0.15, 
                           fees=0.01, risk_premium=0.02, volatility=0.2, n_simulations=10000):
    """
    Simule le rendement d'un investissement sur les marchés financiers.
    R_m = delta + Delta_P - f - lambda * sigma_m
    """
    delta = dividend
    delta_P = np.random.normal(capital_gain_mean, capital_gain_std, n_simulations)
    f = fees
    lambda_risk = risk_premium
    sigma_m = volatility
    
    returns = delta + delta_P - f - lambda_risk * sigma_m
    return returns

def mudaraba_return(capitals, alpha_shares, purchase_price, quantity,
                    sale_price_mean, sale_price_std, fees=0.005, risk_premium=0.01, 
                    n_simulations=10000):
    """
    Simule le rendement d'un contrat Mudaraba.
    R_c = alpha * E[Pi] - beta * E[L] - f_c - lambda_c * sigma_c
    """
    contract = MudarabaContract(capitals, alpha_shares, purchase_price, quantity)
    
    # Distribution du prix de vente
    sale_prices = np.random.normal(sale_price_mean, sale_price_std, n_simulations)
    
    returns = []
    for p in sale_prices:
        gains, profits = contract.simulate_sale(p)
        # Rendement de l'investisseur principal (indice 0)
        return_investor = (gains[0] - capitals[0]) / capitals[0]
        returns.append(return_investor)
    
    returns = np.array(returns)
    # Ajustement pour les frais et le risque
    returns = returns - fees - risk_premium * np.std(returns)
    
    return returns

def compare_mudaraba_finance(capitals, alpha_shares, purchase_price, quantity,
                             sale_price_mean, sale_price_std,
                             dividend=0.02, capital_gain_mean=0.05, capital_gain_std=0.15,
                             n_simulations=10000):
    """
    Compare les rendements de la Mudaraba vs Marchés Financiers.
    """
    # Rendement Mudaraba
    mud_returns = mudaraba_return(capitals, alpha_shares, purchase_price, quantity,
                                  sale_price_mean, sale_price_std, n_simulations=n_simulations)
    
    # Rendement Marché Financier
    fin_returns = financial_market_return(dividend, capital_gain_mean, capital_gain_std,
                                          n_simulations=n_simulations)
    
    # Statistiques
    mud_mean = np.mean(mud_returns)
    mud_std = np.std(mud_returns)
    fin_mean = np.mean(fin_returns)
    fin_std = np.std(fin_returns)
    
    # Probabilité que Mudaraba soit supérieure
    prob_superior = np.mean(mud_returns > fin_returns)
    
    return {
        'mudaraba': {'mean': mud_mean, 'std': mud_std, 'returns': mud_returns},
        'financial': {'mean': fin_mean, 'std': fin_std, 'returns': fin_returns},
        'prob_superior': prob_superior,
        'diff_mean': mud_mean - fin_mean
    }


# ============================================================================
# 4. DYNAMIQUE DE DÉPLOIEMENT DES GUILDES (LOGISTIQUE)
# ============================================================================

def guild_growth(N, t, r, K):
    """
    Équation logistique de Verhulst pour la croissance des guildes.
    dN/dt = r * N * (1 - N/K)
    """
    return r * N * (1 - N/K)

def simulate_guild_growth(N0=1, r=0.5, K=500, t_max=20, n_points=1000):
    """
    Simule la croissance du nombre de guildes.
    """
    t = np.linspace(0, t_max, n_points)
    N = odeint(guild_growth, N0, t, args=(r, K))
    return t, N.flatten()


# ============================================================================
# 5. BIFURCATION DU SYSTÈME MONÉTAIRE
# ============================================================================

def bifurcation_model(x, t, mu):
    """
    Modèle de bifurcation: dx/dt = mu * x - x^3
    """
    return mu * x - x**3

def simulate_bifurcation(mu_values, x0=0.1, t_max=20, n_points=1000):
    """
    Simule la bifurcation pour différentes valeurs de mu (confiance).
    """
    t = np.linspace(0, t_max, n_points)
    trajectories = {}
    
    for mu in mu_values:
        x = odeint(bifurcation_model, x0, t, args=(mu,))
        trajectories[mu] = x.flatten()
    
    return t, trajectories

def critical_slowing_down(series, window=50):
    """
    Calcule le ralentissement critique (variance) comme signal précoce de bifurcation.
    """
    variance = []
    for i in range(len(series) - window):
        window_data = series[i:i+window]
        variance.append(np.var(window_data))
    return np.array(variance)


# ============================================================================
# 6. OPTIMISATION DE L'EFFORT PERSONNEL
# ============================================================================

def effort_rendement(E, t, M0=0.1, k=0.3, tc=15):
    """
    Rendement de l'effort en fonction de la maturité du système.
    R(E,t) = E * M(t) / (1 + exp(-k*(t-tc)))
    """
    M_t = M0 + (1 - M0) / (1 + np.exp(-k * (t - tc)))
    return E * M_t

def optimize_effort(T=30, Emax=40, Emin=5):
    """
    Optimise l'allocation de l'effort sur la période T.
    """
    def objective(E_values):
        t = np.linspace(0, T, len(E_values))
        return -np.sum(effort_rendement(E_values, t))
    
    # Contrainte: effort total limité
    def constraint(E_values):
        return np.sum(E_values) - T * 20  # moyenne 20h/semaine
    
    # Initialisation
    E0 = np.ones(30) * 20
    bounds = [(Emin, Emax) for _ in range(30)]
    
    result = minimize(objective, E0, method='SLSQP', 
                      constraints={'type': 'eq', 'fun': constraint},
                      bounds=bounds)
    
    return result.x


# ============================================================================
# 7. VISUALISATIONS
# ============================================================================

def plot_decline():
    """Visualise le déclin du système usuraire."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Modèle logistique
    t, S = simulate_decline(r=0.08, t_max=80)
    axes[0].plot(t, S, 'b-', linewidth=2, label='Déclin logistique')
    axes[0].axhline(y=0.1, color='r', linestyle='--', label='Seuil d\'effondrement (10%)')
    axes[0].set_xlabel('Années (depuis 1971)')
    axes[0].set_ylabel('Santé du système usuraire S(t)')
    axes[0].set_title('Déclin du Système Usuraire - Modèle Logistique')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Longue traînée
    t, S_lt = long_tail_decline(lam=0.03, t_max=120)
    axes[1].plot(t, S_lt, 'g-', linewidth=2, label='Longue traînée exponentielle')
    axes[1].set_xlabel('Années')
    axes[1].set_ylabel('Dominance résiduelle')
    axes[1].set_title('Longue Traînée vers 0')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].set_yscale('log')
    
    plt.tight_layout()
    plt.savefig('declin_systeme_usuraire.png', dpi=150)
    plt.show()
    return fig

def plot_mudaraba_simulation():
    """Visualise une simulation de contrat Mudaraba."""
    # Paramètres du contrat
    capitals = [100, 200, 300]
    alpha_shares = [0.2, 0.3, 0.5]
    purchase_price = 1.0
    quantity = 600
    
    contract = MudarabaContract(capitals, alpha_shares, purchase_price, quantity)
    
    # Simulation sur une gamme de prix de vente
    sale_prices = np.linspace(0.5, 1.8, 50)
    gains_all = []
    
    for p in sale_prices:
        gains, _ = contract.simulate_sale(p)
        gains_all.append(gains)
    
    gains_all = np.array(gains_all)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Gains par participant
    for i in range(3):
        axes[0].plot(sale_prices, gains_all[:, i], linewidth=2, 
                    label=f'Participant {i+1} (K={capitals[i]})')
    axes[0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    axes[0].axvline(x=purchase_price, color='red', linestyle='--', label='Prix d\'achat')
    axes[0].set_xlabel('Prix de vente unitaire')
    axes[0].set_ylabel('Gain du participant')
    axes[0].set_title('Mudaraba - Gains par Participant')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Rendements par participant
    returns = (gains_all / np.array(capitals) - 1) * 100
    for i in range(3):
        axes[1].plot(sale_prices, returns[:, i], linewidth=2, 
                    label=f'Participant {i+1}')
    axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    axes[1].axvline(x=purchase_price, color='red', linestyle='--', label='Prix d\'achat')
    axes[1].set_xlabel('Prix de vente unitaire')
    axes[1].set_ylabel('Rendement (%)')
    axes[1].set_title('Mudaraba - Rendements par Participant')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('mudaraba_simulation.png', dpi=150)
    plt.show()
    return fig

def plot_comparison_mudaraba_finance():
    """Compare les rendements Mudaraba vs Marchés Financiers."""
    # Paramètres
    capitals = [100, 200, 300]
    alpha_shares = [0.2, 0.3, 0.5]
    purchase_price = 1.0
    quantity = 600
    
    results = compare_mudaraba_finance(
        capitals, alpha_shares, purchase_price, quantity,
        sale_price_mean=1.2, sale_price_std=0.15,
        n_simulations=5000
    )
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Distribution des rendements
    mud_returns = results['mudaraba']['returns']
    fin_returns = results['financial']['returns']
    
    axes[0].hist(mud_returns, bins=50, alpha=0.5, label='Mudaraba', color='green', density=True)
    axes[0].hist(fin_returns, bins=50, alpha=0.5, label='Marchés Financiers', color='blue', density=True)
    axes[0].axvline(x=0, color='black', linestyle='-', linewidth=0.5)
    axes[0].set_xlabel('Rendement')
    axes[0].set_ylabel('Densité de probabilité')
    axes[0].set_title(f'Comparaison des Rendements\nProbabilité Mudaraba > Marché: {results["prob_superior"]*100:.1f}%')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Boîtes à moustaches
    data_to_plot = [mud_returns, fin_returns]
    bp = axes[1].boxplot(data_to_plot, labels=['Mudaraba', 'Marchés Financiers'], patch_artist=True)
    bp['boxes'][0].set_facecolor('green')
    bp['boxes'][1].set_facecolor('blue')
    axes[1].set_ylabel('Rendement')
    axes[1].set_title('Distribution des Rendements')
    axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('comparaison_mudaraba_finance.png', dpi=150)
    plt.show()
    return results

def plot_guild_growth():
    """Visualise la croissance logistique des guildes."""
    t, N = simulate_guild_growth(N0=1, r=0.5, K=500, t_max=30)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(t, N, 'b-', linewidth=2)
    ax.axhline(y=10, color='r', linestyle='--', label='Seuil d\'effet réseau (Nc=10)')
    ax.axhline(y=500, color='g', linestyle='--', label='Capacité maximale (K=500)')
    ax.set_xlabel('Années')
    ax.set_ylabel('Nombre de guildes actives')
    ax.set_title('Dynamique de Déploiement des Guildes - Modèle Logistique')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('guild_growth.png', dpi=150)
    plt.show()
    return fig

def plot_bifurcation():
    """Visualise la bifurcation du système monétaire."""
    mu_values = [-0.5, -0.2, 0.0, 0.2, 0.5]
    t, trajectories = simulate_bifurcation(mu_values)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Trajectoires
    for mu, x in trajectories.items():
        axes[0].plot(t, x, linewidth=2, label=f'μ = {mu}')
    axes[0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    axes[0].set_xlabel('Temps')
    axes[0].set_ylabel('Adoption du crypto-fulus x(t)')
    axes[0].set_title('Bifurcation du Système Monétaire')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Diagramme de bifurcation
    mu_range = np.linspace(-0.8, 0.8, 200)
    x_equilibre = []
    
    for mu in mu_range:
        if mu <= 0:
            x_equilibre.append(0.0)
        else:
            x_equilibre.append(np.sqrt(mu))
    
    axes[1].plot(mu_range, x_equilibre, 'b-', linewidth=2)
    axes[1].plot(mu_range, -np.array(x_equilibre), 'b--', linewidth=2, label='Branche instable')
    axes[1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    axes[1].axvline(x=0, color='r', linestyle='--', label='Seuil critique μc=0')
    axes[1].set_xlabel('Paramètre de confiance μ')
    axes[1].set_ylabel('État d\'équilibre x*')
    axes[1].set_title('Diagramme de Bifurcation')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('bifurcation_monetaire.png', dpi=150)
    plt.show()
    return fig

def plot_effort_optimization():
    """Visualise l'optimisation de l'effort personnel."""
    E_opt = optimize_effort(T=30)
    t = np.linspace(0, 30, len(E_opt))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(t, E_opt, 'b-', linewidth=2, label='Effort optimal')
    
    # Maturité du système
    M_t = 0.1 + 0.9 / (1 + np.exp(-0.3 * (t - 15)))
    ax2 = ax.twinx()
    ax2.plot(t, M_t, 'r--', linewidth=2, label='Maturité du système M(t)')
    ax2.set_ylabel('Maturité M(t)', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    
    ax.set_xlabel('Années')
    ax.set_ylabel('Effort (heures/semaine)')
    ax.set_title('Optimisation de l\'Effort Personnel')
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('effort_optimization.png', dpi=150)
    plt.show()
    return fig


# ============================================================================
# 8. FONCTION PRINCIPALE - EXÉCUTION
# ============================================================================

def run_all_simulations():
    """Exécute toutes les simulations et affiche les résultats."""
    print("=" * 60)
    print("SIMULATIONS POUR LA THÈSE - CRYPTO-FULUS")
    print("=" * 60)
    
    # 1. Déclin du système usuraire
    print("\n[1] Modélisation du déclin du système usuraire...")
    plot_decline()
    
    # 2. Simulation Mudaraba
    print("\n[2] Simulation du contrat Mudaraba...")
    plot_mudaraba_simulation()
    
    # 3. Comparaison Mudaraba vs Marchés Financiers
    print("\n[3] Comparaison Mudaraba vs Marchés Financiers...")
    results = plot_comparison_mudaraba_finance()
    print(f"    - Rendement moyen Mudaraba: {results['mudaraba']['mean']*100:.2f}%")
    print(f"    - Rendement moyen Marché: {results['financial']['mean']*100:.2f}%")
    print(f"    - Probabilité Mudaraba > Marché: {results['prob_superior']*100:.1f}%")
    print(f"    - Différence de rendement: {results['diff_mean']*100:.2f}%")
    
    # 4. Croissance des guildes
    print("\n[4] Modélisation de la croissance des guildes...")
    plot_guild_growth()
    
    # 5. Bifurcation
    print("\n[5] Modélisation de la bifurcation monétaire...")
    plot_bifurcation()
    
    # 6. Optimisation de l'effort
    print("\n[6] Optimisation de l'effort personnel...")
    plot_effort_optimization()
    
    print("\n" + "=" * 60)
    print("Toutes les simulations sont terminées.")
    print("Les graphiques ont été sauvegardés en format PNG.")
    print("=" * 60)


# ============================================================================
# 9. EXÉCUTION STANDALONE
# ============================================================================

if __name__ == "__main__":
    run_all_simulations()
    
    # Exemple d'utilisation de la classe MudarabaContract
    print("\n" + "=" * 60)
    print("EXEMPLE D'UTILISATION DE LA CLASSE MUDARABA")
    print("=" * 60)
    
    # Création d'un contrat
    capitals = [100, 200, 300]
    alpha_shares = [0.2, 0.3, 0.5]
    contract = MudarabaContract(capitals, alpha_shares, 1.0, 600)
    
    # Simulation d'une vente à profit
    print("\nCas de profit (prix de vente = 1.2):")
    gains, profits = contract.simulate_sale(1.2, verbose=True)
    
    # Simulation d'une vente à perte
    print("\nCas de perte (prix de vente = 0.8):")
    gains, profits = contract.simulate_sale(0.8, verbose=True)
    
    # Calcul du rendement espéré
    print("\nRendement espéré (distribution normale):")
    expected_gains = contract.expected_return((1.2, 0.15), n_simulations=10000)
    for i, g in enumerate(expected_gains):
        print(f"  Participant {i+1}: gain espéré = {g:.2f} (rendement: {(g/capitals[i]-1)*100:.1f}%)")

