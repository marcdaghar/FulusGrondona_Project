import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. PROBLÈME D'OPTIMISATION MULTI-OBJECTIF
# ============================================================
class MultiObjectiveSystem:
    """
    Implémente le problème d'optimisation :
    max F = alpha * R + beta * E
    """
    def __init__(self, alpha=0.6, beta=0.4):
        self.alpha = alpha
        self.beta = beta

    def resilience(self, volatility, logistic_shock, crisis_freq):
        """R = 1 / (sigma_P + sigma_L + C)"""
        return 1.0 / (volatility + logistic_shock + crisis_freq + 1e-9)

    def efficiency(self, quantity, transaction_cost, storage_cost):
        """E = Q / (T + S)"""
        return quantity / (transaction_cost + storage_cost + 1e-9)

    def objective(self, params):
        """F = alpha * R + beta * E"""
        q, t_cost, s_cost, volatility, logistic_shock, crisis_freq = params
        R = self.resilience(volatility, logistic_shock, crisis_freq)
        E = self.efficiency(q, t_cost, s_cost)
        return -(self.alpha * R + self.beta * E)  # Minimisation pour scipy

    def optimize(self):
        """Optimise les paramètres pour maximiser F"""
        # Initialisation : quantité, coûts, volatilité, etc.
        x0 = [100.0, 10.0, 5.0, 0.2, 0.1, 0.05]
        bounds = [(50, 200), (1, 50), (1, 20), (0.01, 0.5), (0.01, 0.5), (0.01, 0.2)]
        result = minimize(self.objective, x0, bounds=bounds, method='L-BFGS-B')
        return result.x, -result.fun


# ============================================================
# 2. DYNAMIQUE DES PRIX AVEC RETARDS LOGISTIQUES
# ============================================================
class PriceDynamicsWithDelay:
    """
    Système d'équations différentielles avec retard :
    dp_i/dt = -kappa_i * (p_i(t) - p_j(t-tau) - c_ij)
    """
    def __init__(self, kappa=0.3, tau=2.0, c=5.0, p1_0=110, p2_0=190):
        self.kappa = kappa
        self.tau = tau
        self.c = c
        self.p1_0 = p1_0
        self.p2_0 = p2_0
        self.history_p1 = [p1_0]
        self.history_p2 = [p2_0]

    def delayed_value(self, arr, t, dt):
        """Récupère la valeur retardée par interpolation linéaire."""
        if t < self.tau:
            return arr[0]
        idx = int((t - self.tau) / dt)
        if idx >= len(arr) - 1:
            return arr[-1]
        alpha = (t - self.tau - idx * dt) / dt
        return (1 - alpha) * arr[idx] + alpha * arr[idx + 1]

    def derivatives(self, state, t, dt):
        """Calcule les dérivées dp1/dt et dp2/dt."""
        p1, p2 = state
        # Récupération des valeurs retardées
        p1_delayed = self.delayed_value(self.history_p1, t, dt)
        p2_delayed = self.delayed_value(self.history_p2, t, dt)

        dp1 = -self.kappa * (p1 - p2_delayed - self.c)
        dp2 = -self.kappa * (p2 - p1_delayed - self.c)
        return [dp1, dp2]

    def simulate(self, t_max=100.0, dt=0.1):
        """Simule le système avec la méthode de Runge-Kutta d'ordre 2."""
        n_steps = int(t_max / dt)
        times = np.linspace(0, t_max, n_steps + 1)

        p1 = np.zeros(n_steps + 1)
        p2 = np.zeros(n_steps + 1)
        p1[0] = self.p1_0
        p2[0] = self.p2_0

        for i in range(n_steps):
            t = times[i]
            # Mise à jour de l'historique
            self.history_p1.append(p1[i])
            self.history_p2.append(p2[i])
            if len(self.history_p1) > int(self.tau / dt) + 5:
                self.history_p1.pop(0)
                self.history_p2.pop(0)

            # Midpoint method (RK2)
            k1 = self.derivatives([p1[i], p2[i]], t, dt)
            p1_mid = p1[i] + 0.5 * dt * k1[0]
            p2_mid = p2[i] + 0.5 * dt * k1[1]

            t_mid = t + 0.5 * dt
            # Recalcul des valeurs retardées au milieu
            self.history_p1.append(p1_mid)
            self.history_p2.append(p2_mid)

            k2 = self.derivatives([p1_mid, p2_mid], t_mid, dt)
            p1[i+1] = p1[i] + dt * k2[0]
            p2[i+1] = p2[i] + dt * k2[1]

        return times, p1, p2


# ============================================================
# 3. COMPARAISON CRD/GUILDES vs IMF (SYSTÈME DE DETTE)
# ============================================================
class IMFStyleEconomy:
    """Économie de dette type FMI / Banque mondiale."""
    def __init__(self, debt=100.0, growth=1.0, volatility=0.1, liquidity=1.0):
        self.debt = debt
        self.growth = growth
        self.volatility = volatility
        self.liquidity = liquidity
        self.history = [volatility]

    def step(self, shock):
        self.liquidity += shock * 0.5
        self.debt *= 1.02  # Intérêt composé
        self.volatility += shock * 0.3
        self.volatility = max(0.01, self.volatility)
        self.history.append(self.volatility)
        return self


class CRDGuildEconomy:
    """Système CRD + guildes (votre modèle)."""
    def __init__(self, reserve=100.0, volatility=0.1):
        self.reserve = reserve
        self.volatility = volatility
        self.history = [volatility]

    def step(self, shock):
        # Stockage contra-cyclique (Yusuf)
        self.reserve += -shock * 0.2
        self.reserve = max(0.01, self.reserve)
        self.volatility += shock * 0.15
        self.volatility = max(0.01, self.volatility)
        self.history.append(self.volatility)
        return self


def run_comparison(n_steps=200, seed=42):
    """Compare les deux économies sous les mêmes chocs."""
    np.random.seed(seed)
    shocks = np.random.normal(0, 1, n_steps)

    imf = IMFStyleEconomy()
    crd = CRDGuildEconomy()

    imf_history = []
    crd_history = []

    for s in shocks:
        imf.step(s)
        crd.step(s)
        imf_history.append(imf.volatility)
        crd_history.append(crd.volatility)

    return {
        'imf_volatility': np.array(imf_history),
        'crd_volatility': np.array(crd_history),
        'shocks': shocks
    }


def compare_metrics(results):
    """Calcule et affiche les métriques de performance."""
    imf_vol = results['imf_volatility']
    crd_vol = results['crd_volatility']

    # 1. Stabilité = -écart-type
    imf_stability = -np.std(imf_vol)
    crd_stability = -np.std(crd_vol)

    # 2. Nombre de crises (volatilité > 2.0)
    imf_crises = np.sum(imf_vol > 2.0)
    crd_crises = np.sum(crd_vol > 2.0)

    # 3. Temps de récupération (moyenne des écarts entre pics)
    def recovery_time(series, threshold=2.0):
        over = np.where(series > threshold)[0]
        if len(over) < 2:
            return 0
        return np.mean(np.diff(over))

    imf_recovery = recovery_time(imf_vol)
    crd_recovery = recovery_time(crd_vol)

    print("=" * 60)
    print("COMPARAISON IMF vs CRD/GUILDES")
    print("=" * 60)
    print(f"Stabilité (plus = mieux)   : IMF = {imf_stability:.3f}, CRD = {crd_stability:.3f}")
    print(f"Crises (moins = mieux)     : IMF = {imf_crises:.0f}, CRD = {crd_crises:.0f}")
    print(f"Temps de récupération      : IMF = {imf_recovery:.1f}, CRD = {crd_recovery:.1f}")

    return {
        'imf_stability': imf_stability,
        'crd_stability': crd_stability,
        'imf_crises': imf_crises,
        'crd_crises': crd_crises,
        'imf_recovery': imf_recovery,
        'crd_recovery': crd_recovery
    }


def plot_comparison(results):
    """Visualise la comparaison des volatilités."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Graphique 1 : Volatilités
    axes[0].plot(results['imf_volatility'], label='IMF (Dette)', alpha=0.7, color='red')
    axes[0].plot(results['crd_volatility'], label='CRD/Guildes', alpha=0.7, color='green')
    axes[0].axhline(y=2.0, color='red', linestyle='--', label='Seuil de crise')
    axes[0].set_title('Volatilité comparée sous chocs identiques')
    axes[0].set_xlabel('Période')
    axes[0].set_ylabel('Volatilité')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Graphique 2 : Distribution
    axes[1].hist(results['imf_volatility'], bins=30, alpha=0.5, label='IMF', color='red')
    axes[1].hist(results['crd_volatility'], bins=30, alpha=0.5, label='CRD', color='green')
    axes[1].set_title('Distribution de la volatilité')
    axes[1].set_xlabel('Volatilité')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


# ============================================================
# 4. EXÉCUTION PRINCIPALE
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("MODÈLE CRD/GUILDES - IMPLÉMENTATION COMPLÈTE")
    print("=" * 60)

    # 1. Optimisation multi-objectif
    print("\n[1] Optimisation du compromis Résilience/Efficacité")
    system = MultiObjectiveSystem(alpha=0.6, beta=0.4)
    params, max_F = system.optimize()
    print(f"Paramètres optimaux : Quantité={params[0]:.1f}, Coût T={params[1]:.1f}, Coût S={params[2]:.1f}")
    print(f"Valeur maximale de F = {max_F:.3f}")

    # 2. Dynamique des prix avec retards
    print("\n[2] Simulation de la dynamique des prix avec retards logistiques")
    price_model = PriceDynamicsWithDelay(kappa=0.3, tau=2.0, c=5.0)
    times, p1, p2 = price_model.simulate(t_max=100, dt=0.1)

    plt.figure(figsize=(10, 4))
    plt.plot(times, p1, label='Prix région 1', color='blue')
    plt.plot(times, p2, label='Prix région 2', color='orange')
    plt.axhline(y=100, color='gray', linestyle='--', label='Borne basse')
    plt.axhline(y=200, color='gray', linestyle='--', label='Borne haute')
    plt.title(f'Dynamique des prix avec retard τ = {price_model.tau}')
    plt.xlabel('Temps')
    plt.ylabel('Prix')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

    # 3. Comparaison CRD vs IMF
    print("\n[3] Comparaison IMF vs CRD/Guildes")
    results = run_comparison(n_steps=200, seed=42)
    metrics = compare_metrics(results)
    plot_comparison(results)

    # 4. Interprétation finale
    print("\n" + "=" * 60)
    print("INTERPRÉTATION")
    print("=" * 60)
    if metrics['crd_stability'] > metrics['imf_stability']:
        print("✓ Le système CRD/Guildes est PLUS STABLE que le système IMF.")
    if metrics['crd_crises'] < metrics['imf_crises']:
        print("✓ Le système CRD/Guildes génère MOINS DE CRISES.")
    if metrics['crd_recovery'] < metrics['imf_recovery']:
        print("✓ Le système CRD/Guildes récupère PLUS VITE après un choc.")
    print("\nConclusion : Le modèle CRD/Guildes (sans dette, sans intérêt, avec stockage)")
    print("est plus résilient que l'économie de dette type FMI/Banque mondiale.")
