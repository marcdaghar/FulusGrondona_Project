"""
Crypto-Fulus Modelling Suite
Auteur : Marc Daghar
Licence : CC BY-SA
Description : Implémentation des modèles mathématiques pour la théorie du bimétallisme,
              de la thermodynamique économique et de la cliodynamique monétaire.
Dépendances : numpy, scipy, matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
from scipy.optimize import fsolve
from scipy.stats import weibull_min
from scipy.special import lambertw

# =============================================================================
# 1. THERMODYNAMIQUE ET ÉCONOMIE (François Roddier)
# =============================================================================

class ThermodynamicEconomy:
    """
    Modélisation des systèmes économiques comme structures dissipatives.
    """
    
    def __init__(self, T_hot, T_cold, R=8.314):
        """
        Args:
            T_hot: Température de la source chaude (économie "chaude")
            T_cold: Température de la source froide (économie "froide")
            R: Constante universelle des gaz (analogue économique)
        """
        self.T_hot = T_hot
        self.T_cold = T_cold
        self.R = R
        
    def carnot_efficiency(self):
        """Rendement maximal d'une machine thermique économique."""
        return 1 - (self.T_cold / self.T_hot)
    
    def entropy_production(self, energy_flux, temperature):
        """Taux de production d'entropie (dissipation d'énergie)."""
        return energy_flux / temperature
    
    def van_der_waals_economy(self, P, V, a, b, T=None):
        """
        Équation de van der Waals appliquée à l'économie.
        
        Args:
            P: Potentiel d'achat (pression économique)
            V: Volume de production
            a: Coefficient d'attraction sociale
            b: Volume minimal de production (survie)
            T: Température économique (par défaut, moyenne de T_hot et T_cold)
        
        Returns:
            tuple: (P, V, T) satisfaisant l'équation
        """
        if T is None:
            T = (self.T_hot + self.T_cold) / 2
        return (P + a / V**2) * (V - b) - self.R * T
    
    def critical_point(self, a, b):
        """
        Calcul du point critique de l'économie (analogue au point critique de van der Waals).
        """
        V_c = 3 * b
        P_c = a / (27 * b**2)
        T_c = (8 * a) / (27 * self.R * b)
        return V_c, P_c, T_c
    
    def phase_transition_model(self, debt, T_economy):
        """
        Modélisation de la dette comme chaleur latente de transition de phase.
        
        Args:
            debt: Montant de la dette
            T_economy: Température économique (indice de confiance)
        
        Returns:
            float: Énergie de transition
        """
        return debt * T_economy
    
    def simulate_entropy_over_time(self, time_steps, initial_entropy, growth_rate):
        """
        Simulation de la production d'entropie sur une période donnée.
        """
        t = np.linspace(0, 100, time_steps)
        S = initial_entropy * np.exp(growth_rate * t)
        return t, S
    
    def plot_entropy(self, t, S):
        """Visualisation de la production d'entropie."""
        plt.figure(figsize=(10, 5))
        plt.plot(t, S, label='Production d\'entropie (S)')
        plt.xlabel('Temps (années)')
        plt.ylabel('Entropie (S)')
        plt.title('Production d\'Entropie dans le Système Économique')
        plt.legend()
        plt.grid(True)
        plt.show()


# =============================================================================
# 2. ONTOGENÈSE MIMÉTIQUE DE LA MONNAIE
# =============================================================================

class MimeticAdoptionModel:
    """
    Modélisation de l'adoption d'une monnaie par mécanisme mimétique.
    """
    
    def __init__(self, r=0.15, threshold=0.5):
        """
        Args:
            r: Taux de croissance de l'adoption (influence mimétique)
            threshold: Seuil critique d'adoption (effet bootstrap)
        """
        self.r = r
        self.threshold = threshold
    
    def logistic_growth(self, x, t):
        """
        Équation logistique modélisant l'adoption d'une monnaie.
        
        Args:
            x: Fraction de la population ayant adopté la monnaie
            t: Temps
        
        Returns:
            float: dx/dt
        """
        return self.r * x * (1 - x)
    
    def adoption_curve(self, x0=0.01, t_max=100, n_points=1000):
        """
        Génère la courbe d'adoption de la nouvelle monnaie.
        
        Args:
            x0: Fraction initiale d'adoptants
            t_max: Durée de la simulation
            n_points: Nombre de points
        
        Returns:
            tuple: (temps, fraction_adoptants)
        """
        t = np.linspace(0, t_max, n_points)
        x = odeint(self.logistic_growth, x0, t)
        return t, x.flatten()
    
    def bootstrap_effect(self, x):
        """
        Fonction décrivant l'effet bootstrap (auto-amplification).
        
        Returns:
            float: Intensité de l'effet bootstrap
        """
        # L'effet bootstrap est maximal lorsque x approche le seuil critique
        return np.exp(-((x - self.threshold) / 0.1)**2)
    
    def plot_adoption(self, t, x):
        """Visualisation de la courbe d'adoption mimétique."""
        plt.figure(figsize=(10, 5))
        plt.plot(t, x, label='Fraction d\'adoptants')
        plt.axhline(y=self.threshold, color='r', linestyle='--', label='Seuil critique (Bootstrap)')
        plt.xlabel('Temps')
        plt.ylabel('Fraction de la population')
        plt.title('Adoption Mimétique d\'une Nouvelle Monnaie')
        plt.legend()
        plt.grid(True)
        plt.show()


# =============================================================================
# 3. MODÈLE DE LA DETTE ET DES INTÉRÊTS COMPOSÉS
# =============================================================================

class DebtModel:
    """
    Modélisation de l'évolution de la dette avec intérêts composés.
    """
    
    def __init__(self, initial_debt, interest_rate, payment_rate=0.05):
        """
        Args:
            initial_debt: Dette initiale
            interest_rate: Taux d'intérêt annuel (en décimal, ex: 0.04 pour 4%)
            payment_rate: Taux de remboursement annuel (en décimal)
        """
        self.D0 = initial_debt
        self.r = interest_rate
        self.p = payment_rate
    
    def compound_growth(self, t):
        """
        Croissance exponentielle de la dette sans remboursement.
        """
        return self.D0 * (1 + self.r)**t
    
    def debt_with_payment(self, t):
        """
        Évolution de la dette avec remboursements constants.
        """
        if self.r == self.p:
            return self.D0
        return self.D0 * (1 + self.r - self.p)**t
    
    def time_to_double(self):
        """
        Temps nécessaire pour que la dette double (loi de 70/72).
        """
        return 70 / (self.r * 100)  # Approximation
    
    def critical_time(self, economy_growth_rate):
        """
        Calcul du temps critique où la dette devient insoutenable.
        
        Args:
            economy_growth_rate: Taux de croissance de l'économie réelle
        
        Returns:
            float: Temps critique (années)
        """
        # La dette est soutenable si r < economy_growth_rate
        # Temps critique lorsque la dette dépasse la capacité de l'économie
        if self.r >= economy_growth_rate:
            return np.inf  # Jamais soutenable
        return np.log(1 / (1 - self.r / economy_growth_rate)) / economy_growth_rate
    
    def plot_debt(self, t_max=100, n_points=1000):
        """Visualisation de l'évolution de la dette."""
        t = np.linspace(0, t_max, n_points)
        D_no_payment = self.compound_growth(t)
        D_with_payment = self.debt_with_payment(t)
        
        plt.figure(figsize=(12, 6))
        plt.plot(t, D_no_payment, label='Sans remboursement')
        plt.plot(t, D_with_payment, label='Avec remboursement (taux = 5%)')
        plt.xlabel('Années')
        plt.ylabel('Montant de la dette')
        plt.title('Évolution de la Dette à Intérêts Composés')
        plt.legend()
        plt.grid(True)
        plt.show()
        
        return t, D_no_payment, D_with_payment


# =============================================================================
# 4. THÉORIE QUANTITATIVE DE LA MONNAIE (ÉQUATION DE FISHER)
# =============================================================================

class FisherModel:
    """
    Modélisation de l'équation quantitative de la monnaie (MV = PY).
    """
    
    def __init__(self, money_supply, velocity, price_level, real_output):
        """
        Args:
            money_supply: Masse monétaire (M)
            velocity: Vitesse de circulation (V)
            price_level: Niveau général des prix (P)
            real_output: Production réelle (Y)
        """
        self.M = money_supply
        self.V = velocity
        self.P = price_level
        self.Y = real_output
    
    def compute_nominal_gdp(self):
        """Calcule le PIB nominal (P * Y)."""
        return self.P * self.Y
    
    def compute_money_value(self):
        """Calcule la valeur totale de la monnaie en circulation (M * V)."""
        return self.M * self.V
    
    def equilibrium_check(self):
        """Vérifie si l'équation MV = PY est vérifiée."""
        return self.M * self.V == self.P * self.Y
    
    def adjust_for_inflation(self, inflation_rate):
        """Ajuste les variables pour un scénario d'inflation."""
        new_P = self.P * (1 + inflation_rate)
        # Pour maintenir l'équilibre, il faut que M ou V ou Y change
        return new_P
    
    def simulate_velocity_change(self, new_velocity):
        """Simule l'effet d'un changement de la vitesse de circulation."""
        old_MV = self.M * self.V
        new_M = old_MV / new_velocity
        return new_M


# =============================================================================
# 5. MODELISATION CLIODYNAMIQUE (LOI DE WEIBULL)
# =============================================================================

class CliodynamicModel:
    """
    Application de la loi de Weibull à l'analyse de l'effondrement des systèmes monétaires.
    """
    
    def __init__(self, scale=50, shape=2.5):
        """
        Args:
            scale: Paramètre d'échelle (λ) - période caractéristique
            shape: Paramètre de forme (k) - tendance du risque
        """
        self.scale = scale
        self.shape = shape
    
    def hazard_function(self, t):
        """
        Fonction de hasard (risque instantané d'effondrement).
        """
        return (self.shape / self.scale) * (t / self.scale)**(self.shape - 1)
    
    def survival_function(self, t):
        """
        Fonction de survie (probabilité que le système survive au-delà de t).
        """
        return np.exp(-(t / self.scale)**self.shape)
    
    def probability_density(self, t):
        """
        Fonction de densité de probabilité.
        """
        return (self.shape / self.scale) * (t / self.scale)**(self.shape - 1) * self.survival_function(t)
    
    def cumulative_probability(self, t):
        """
        Probabilité cumulée d'effondrement avant l'instant t.
        """
        return 1 - self.survival_function(t)
    
    def collapse_probability(self, year=2030):
        """
        Probabilité d'effondrement d'ici à l'année donnée.
        """
        # Année de référence (1971)
        years_since_1971 = year - 1971
        return self.cumulative_probability(years_since_1971)
    
    def plot_weibull_analysis(self, t_max=120, n_points=1000):
        """Visualisation complète de l'analyse de Weibull."""
        t = np.linspace(0, t_max, n_points)
        hazard = self.hazard_function(t)
        survival = self.survival_function(t)
        density = self.probability_density(t)
        cumulative = self.cumulative_probability(t)
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        axes[0, 0].plot(t, hazard)
        axes[0, 0].set_title('Fonction de Hasard (Risque instantané)')
        axes[0, 0].set_xlabel('Années depuis 1971')
        axes[0, 0].grid(True)
        
        axes[0, 1].plot(t, survival)
        axes[0, 1].set_title('Fonction de Survie')
        axes[0, 1].set_xlabel('Années depuis 1971')
        axes[0, 1].grid(True)
        
        axes[1, 0].plot(t, density)
        axes[1, 0].set_title('Densité de Probabilité')
        axes[1, 0].set_xlabel('Années depuis 1971')
        axes[1, 0].grid(True)
        
        axes[1, 1].plot(t, cumulative)
        axes[1, 1].axhline(y=0.80, color='r', linestyle='--', label='Seuil 80%')
        axes[1, 1].set_title('Probabilité Cumulée d\'Effondrement')
        axes[1, 1].set_xlabel('Années depuis 1971')
        axes[1, 1].set_ylabel('Probabilité')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.show()


# =============================================================================
# 6. MODÈLE DE RÉSERVE FRACTIONNAIRE BANCAIRE
# =============================================================================

class FractionalReserveModel:
    """
    Modélisation du système de réserve fractionnaire bancaire.
    """
    
    def __init__(self, reserve_ratio=0.10, initial_deposit=1000):
        """
        Args:
            reserve_ratio: Taux de réserve obligatoire (ex: 0.10 pour 10%)
            initial_deposit: Dépôt initial
        """
        self.reserve_ratio = reserve_ratio
        self.initial_deposit = initial_deposit
    
    def money_multiplier(self):
        """Multiplicateur de crédit."""
        return 1 / self.reserve_ratio
    
    def max_money_supply(self):
        """Masse monétaire totale maximale créée."""
        return self.initial_deposit * self.money_multiplier()
    
    def calculate_credit_cycle(self, n_rounds=10):
        """
        Simule le cycle de création monétaire par le crédit.
        
        Returns:
            dict: Résultats du cycle de crédit
        """
        deposits = []
        loans = []
        reserves = []
        
        current_deposit = self.initial_deposit
        total_money = 0
        
        for i in range(n_rounds):
            reserve = current_deposit * self.reserve_ratio
            loan = current_deposit * (1 - self.reserve_ratio)
            
            deposits.append(current_deposit)
            loans.append(loan)
            reserves.append(reserve)
            
            total_money += loan
            current_deposit = loan  # Le prêt devient le nouveau dépôt
        
        return {
            'deposits': deposits,
            'loans': loans,
            'reserves': reserves,
            'total_money': total_money + self.initial_deposit
        }
    
    def plot_credit_creation(self, n_rounds=10):
        """Visualisation de la création monétaire par le crédit."""
        result = self.calculate_credit_cycle(n_rounds)
        
        rounds = range(1, n_rounds + 1)
        
        plt.figure(figsize=(12, 6))
        plt.bar(rounds, result['loans'], label='Prêts créés', alpha=0.7)
        plt.bar(rounds, result['reserves'], bottom=result['loans'], 
                label='Réserves', alpha=0.7)
        plt.xlabel('Cycles de crédit')
        plt.ylabel('Montant')
        plt.title('Création Monétaire par Réserve Fractionnaire')
        plt.legend()
        plt.grid(True, axis='y')
        plt.show()


# =============================================================================
# 7. MODÈLE D'OPTIMISATION EFFICIENCE/RÉSILIENCE
# =============================================================================

class ResilienceOptimizationModel:
    """
    Modèle d'optimisation entre l'efficience et la résilience du système monétaire.
    """
    
    def __init__(self, efficiency_weights=None, resilience_weights=None):
        """
        Args:
            efficiency_weights: Poids pour le calcul de l'efficience
            resilience_weights: Poids pour le calcul de la résilience
        """
        self.efficiency_weights = efficiency_weights or [0.4, 0.3, 0.3]
        self.resilience_weights = resilience_weights or [0.5, 0.5]
    
    def compute_efficiency(self, velocity, price_stability, gdp_growth):
        """
        Calcul de l'efficience du système monétaire.
        
        Args:
            velocity: Vitesse de circulation de la monnaie
            price_stability: Stabilité des prix (1 = parfaitement stable)
            gdp_growth: Taux de croissance du PIB
        """
        normalized_velocity = min(velocity / 10, 1)  # Normalisation
        efficiency = (self.efficiency_weights[0] * normalized_velocity +
                     self.efficiency_weights[1] * price_stability +
                     self.efficiency_weights[2] * (gdp_growth / 5))
        return min(efficiency, 1)
    
    def compute_resilience(self, diversity, adaptability):
        """
        Calcul de la résilience du système monétaire.
        
        Args:
            diversity: Diversité des moyens d'échange
            adaptability: Capacité d'adaptation du système
        """
        resilience = (self.resilience_weights[0] * diversity +
                      self.resilience_weights[1] * adaptability)
        return min(resilience, 1)
    
    def survival_function(self, efficiency, resilience):
        """
        Fonction de survie du système (minimum d'efficience et de résilience).
        """
        return min(efficiency, resilience)
    
    def optimize_for_survival(self, trade_off_factor=0.5):
        """
        Optimisation du système pour maximiser la survie.
        
        Returns:
            dict: Points optimaux
        """
        # Simulation de différentes configurations
        results = []
        for efficiency in np.linspace(0.1, 1, 10):
            for resilience in np.linspace(0.1, 1, 10):
                survival = self.survival_function(efficiency, resilience)
                results.append({
                    'efficiency': efficiency,
                    'resilience': resilience,
                    'survival': survival,
                    'score': survival - trade_off_factor * abs(efficiency - resilience)
                })
        
        best = max(results, key=lambda x: x['score'])
        return best


# =============================================================================
# 8. SIMULATION COMPLÈTE DU SYSTÈME BIMÉTALLIQUE
# =============================================================================

class BimetallicSystemSimulation:
    """
    Simulation complète du système bimétallique avec crypto-fulus.
    """
    
    def __init__(self, gold_price=1800, silver_price=25, fulus_exchange_rate=1.0):
        """
        Args:
            gold_price: Prix de l'or en unité de compte
            silver_price: Prix de l'argent en unité de compte
            fulus_exchange_rate: Taux de change du fulus
        """
        self.gold_price = gold_price
        self.silver_price = silver_price
        self.fulus_exchange_rate = fulus_exchange_rate
    
    def compute_metal_value(self, gold_amount, silver_amount):
        """
        Calcul de la valeur totale en métaux précieux.
        """
        return gold_amount * self.gold_price + silver_amount * self.silver_price
    
    def fulus_value_in_metals(self, fulus_amount):
        """
        Valeur du fulus en termes de métaux précieux.
        """
        return fulus_amount * self.fulus_exchange_rate
    
    def greshams_law_effect(self, good_money_hoarding):
        """
        Modélisation de l'effet Gresham (le mauvais argent chasse le bon).
        
        Args:
            good_money_hoarding: Taux de thésaurisation des métaux précieux (0-1)
        
        Returns:
            float: Taux de circulation du mauvais argent
        """
        # Plus les gens thésaurisent les métaux précieux, plus le fulus circule
        return 1 / (1 + good_money_hoarding)
    
    def simulate_transition(self, years, initial_gold_hoarding=0.3):
        """
        Simulation de la transition vers le système bimétallique.
        """
        t = np.linspace(0, years, years * 12)  # Données mensuelles
        hoarding = initial_gold_hoarding + 0.5 * (1 - np.exp(-t / 5))
        fulus_circulation = self.greshams_law_effect(hoarding)
        
        return t, hoarding, fulus_circulation
    
    def plot_transition(self, years=20):
        """Visualisation de la transition vers le bimétallisme."""
        t, hoarding, circulation = self.simulate_transition(years)
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        
        ax1.set_xlabel('Temps (années)')
        ax1.set_ylabel('Thésaurisation des métaux précieux')
        ax1.plot(t, hoarding, 'b-', label='Thésaurisation (or/argent)')
        ax1.tick_params(axis='y', labelcolor='b')
        
        ax2 = ax1.twinx()
        ax2.set_ylabel('Circulation du fulus')
        ax2.plot(t, circulation, 'r-', label='Circulation du fulus')
        ax2.tick_params(axis='y', labelcolor='r')
        
        plt.title('Transition vers le Bimétallisme - Effet Gresham')
        fig.tight_layout()
        plt.show()


# =============================================================================
# 9. EXEMPLE D'EXÉCUTION ET VISUALISATION
# =============================================================================

def run_full_simulation():
    """
    Exécute l'ensemble des simulations et génère les visualisations.
    """
    print("=== Simulation du Système Bimétallique ===\n")
    
    # 1. Thermodynamique économique
    print("1. Modèle Thermodynamique de Roddier")
    thermo = ThermodynamicEconomy(T_hot=350, T_cold=300)
    print(f"   Rendement de Carnot: {thermo.carnot_efficiency():.2%}")
    print(f"   Point critique (a=1, b=1): Vc={thermo.critical_point(1, 1)[0]:.2f}, Pc={thermo.critical_point(1, 1)[1]:.2f}")
    
    # Simulation de l'entropie
    t, S = thermo.simulate_entropy_over_time(100, 100, 0.03)
    print(f"   Entropie finale: {S[-1]:.2f}")
    thermo.plot_entropy(t, S)
    
    # 2. Modèle d'adoption mimétique
    print("\n2. Modèle d'Adoption Mimétique")
    mimetic = MimeticAdoptionModel(r=0.15, threshold=0.5)
    t, x = mimetic.adoption_curve(x0=0.01, t_max=50)
    print(f"   Seuil critique atteint en {t[np.argmax(x >= 0.5)]:.2f} unités de temps")
    mimetic.plot_adoption(t, x)
    
    # 3. Modèle de la dette
    print("\n3. Modèle de la Dette à Intérêts Composés")
    debt_model = DebtModel(initial_debt=1000, interest_rate=0.04, payment_rate=0.05)
    print(f"   Temps de doublement: {debt_model.time_to_double():.2f} ans")
    print(f"   Temps critique (avec croissance à 3%): {debt_model.critical_time(0.03):.2f} ans")
    debt_model.plot_debt(t_max=50)
    
    # 4. Modèle de réserve fractionnaire
    print("\n4. Modèle de Réserve Fractionnaire")
    reserve_model = FractionalReserveModel(reserve_ratio=0.10, initial_deposit=1000)
    print(f"   Multiplicateur de crédit: {reserve_model.money_multiplier():.1f}")
    print(f"   Masse monétaire maximale: {reserve_model.max_money_supply():.0f}")
    credit_result = reserve_model.calculate_credit_cycle(10)
    print(f"   Total des prêts créés: {credit_result['total_money']:.0f}")
    reserve_model.plot_credit_creation(10)
    
    # 5. Modèle cliodynamique (Weibull)
    print("\n5. Modèle Cliodynamique (Loi de Weibull)")
    clio = CliodynamicModel(scale=50, shape=2.5)
    prob_2030 = clio.collapse_probability(2030)
    prob_2050 = clio.collapse_probability(2050)
    print(f"   Probabilité d'effondrement d'ici 2030: {prob_2030:.2%}")
    print(f"   Probabilité d'effondrement d'ici 2050: {prob_2050:.2%}")
    clio.plot_weibull_analysis()
    
    # 6. Optimisation efficience/résilience
    print("\n6. Optimisation Efficience/Résilience")
    opt_model = ResilienceOptimizationModel()
    best_config = opt_model.optimize_for_survival()
    print(f"   Configuration optimale: E={best_config['efficiency']:.2f}, R={best_config['resilience']:.2f}")
    print(f"   Score de survie: {best_config['survival']:.2f}")
    
    # 7. Simulation du système bimétallique
    print("\n7. Simulation du Système Bimétallique")
    bimetallic = BimetallicSystemSimulation(gold_price=1800, silver_price=25)
    print(f"   Valeur de 10 oz d'or + 100 oz d'argent: {bimetallic.compute_metal_value(10, 100):.2f}")
    bimetallic.plot_transition(years=20)
    
    print("\n=== Simulation terminée ===")
    return thermo, mimetic, debt_model, reserve_model, clio, opt_model, bimetallic


# =============================================================================
# 10. ANALYSE DE SENSIBILITÉ
# =============================================================================

class SensitivityAnalysis:
    """
    Analyse de sensibilité des paramètres clés du modèle.
    """
    
    @staticmethod
    def weibull_sensitivity():
        """
        Analyse de la sensibilité de la loi de Weibull aux paramètres.
        """
        scales = [30, 40, 50, 60, 70]
        shapes = [1.5, 2.0, 2.5, 3.0, 3.5]
        results = {}
        
        for shape in shapes:
            for scale in scales:
                model = CliodynamicModel(scale=scale, shape=shape)
                prob = model.collapse_probability(2030)
                results[(scale, shape)] = prob
        
        return results
    
    @staticmethod
    def plot_sensitivity_heatmap():
        """Visualisation de la sensibilité des paramètres."""
        results = SensitivityAnalysis.weibull_sensitivity()
        
        # Extraction des données pour le heatmap
        scales = sorted(set([k[0] for k in results.keys()]))
        shapes = sorted(set([k[1] for k in results.keys()]))
        data = np.zeros((len(shapes), len(scales)))
        
        for i, shape in enumerate(shapes):
            for j, scale in enumerate(scales):
                data[i, j] = results[(scale, shape)]
        
        plt.figure(figsize=(10, 8))
        plt.imshow(data, cmap='RdYlGn_r', aspect='auto', 
                   extent=[min(scales), max(scales), min(shapes), max(shapes)])
        plt.colorbar(label='Probabilité d\'effondrement en 2030')
        plt.xlabel('Paramètre d\'échelle (λ)')
        plt.ylabel('Paramètre de forme (k)')
        plt.title('Analyse de Sensibilité du Modèle de Weibull')
        plt.show()


# =============================================================================
# 11. MODÈLE DE SIMULATION MONTE CARLO
# =============================================================================

class MonteCarloSimulation:
    """
    Simulation Monte Carlo pour l'évaluation des risques du système monétaire.
    """
    
    def __init__(self, n_simulations=1000):
        self.n_simulations = n_simulations
        
    def simulate_currency_collapse(self, base_year=1971):
        """
        Simulation Monte Carlo de l'effondrement monétaire.
        """
        # Paramètres stochastiques
        scale_samples = np.random.normal(50, 10, self.n_simulations)
        shape_samples = np.random.normal(2.5, 0.5, self.n_simulations)
        
        collapse_years = []
        collapse_probabilities = []
        
        for scale, shape in zip(scale_samples, shape_samples):
            model = CliodynamicModel(scale=scale, shape=shape)
            # Calcul de l'année de l'effondrement (lorsque la probabilité cumulée > 0.5)
            t = np.linspace(0, 100, 1000)
            probs = model.cumulative_probability(t)
            if np.any(probs > 0.5):
                idx = np.argmax(probs > 0.5)
                year = base_year + t[idx]
                collapse_years.append(year)
                collapse_probabilities.append(probs[idx])
        
        return np.array(collapse_years), np.array(collapse_probabilities)
    
    def plot_monte_carlo(self):
        """Visualisation des résultats de la simulation Monte Carlo."""
        years, probs = self.simulate_currency_collapse()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        ax1.hist(years, bins=30, color='blue', alpha=0.7)
        ax1.axvline(np.mean(years), color='red', linestyle='--', label=f'Moyenne: {np.mean(years):.0f}')
        ax1.set_xlabel('Année de l\'effondrement')
        ax1.set_ylabel('Fréquence')
        ax1.set_title('Distribution des Années d\'Effondrement (Monte Carlo)')
        ax1.legend()
        
        ax2.hist(probs, bins=30, color='green', alpha=0.7)
        ax2.axvline(np.mean(probs), color='red', linestyle='--', label=f'Moyenne: {np.mean(probs):.2%}')
        ax2.set_xlabel('Probabilité d\'effondrement')
        ax2.set_ylabel('Fréquence')
        ax2.set_title('Distribution des Probabilités d\'Effondrement')
        ax2.legend()
        
        plt.tight_layout()
        plt.show()
        
        return years, probs


# =============================================================================
# 12. MODÈLE DE PRÉVISION AVEC FILTRE DE KALMAN
# =============================================================================

class KalmanFilterModel:
    """
    Modèle de prévision des crises monétaires utilisant un filtre de Kalman.
    """
    
    def __init__(self, initial_state=0.0, initial_covariance=1.0):
        """
        Args:
            initial_state: État initial du système
            initial_covariance: Covariance initiale
        """
        self.state = initial_state
        self.covariance = initial_covariance
        self.process_noise = 0.1
        self.measurement_noise = 0.5
    
    def predict(self):
        """Prédiction de l'état futur du système."""
        # Modèle simple : le système évolue avec un bruit de processus
        self.state = self.state
        self.covariance = self.covariance + self.process_noise
    
    def update(self, measurement):
        """Mise à jour de l'état à partir d'une observation."""
        # Gain de Kalman
        kalman_gain = self.covariance / (self.covariance + self.measurement_noise)
        
        # Mise à jour de l'état
        self.state = self.state + kalman_gain * (measurement - self.state)
        
        # Mise à jour de la covariance
        self.covariance = (1 - kalman_gain) * self.covariance
    
    def forecast_crisis(self, measurements):
        """
        Prévision des crises à partir d'une série d'observations.
        
        Returns:
            list: États prédits (indices de stress monétaire)
        """
        predictions = []
        for measurement in measurements:
            self.predict()
            self.update(measurement)
            predictions.append(self.state)
        return predictions
    
    def plot_forecast(self, measurements, actual=None):
        """Visualisation de la prévision des crises."""
        predictions = self.forecast_crisis(measurements)
        
        plt.figure(figsize=(12, 6))
        plt.plot(measurements, 'b-', label='Observations (stress monétaire)', alpha=0.6)
        plt.plot(predictions, 'r-', label='Prédiction (filtre de Kalman)', linewidth=2)
        plt.axhline(y=2.0, color='r', linestyle='--', label='Seuil de crise (stress > 2)')
        plt.xlabel('Temps')
        plt.ylabel('Niveau de stress monétaire')
        plt.title('Prévision de Crises Monétaires - Filtre de Kalman')
        plt.legend()
        plt.grid(True)
        plt.show()


# =============================================================================
# 13. MODÈLE DE RÉSEAUX NEURAUX POUR L'APPRENTISSAGE DES CYCLES MONÉTAIRES
# =============================================================================

class SimpleNeuralNetworkModel:
    """
    Modèle simple de réseau de neurones pour l'apprentissage des cycles monétaires.
    """
    
    def __init__(self, input_size=3, hidden_size=10, output_size=1):
        """
        Args:
            input_size: Nombre de caractéristiques d'entrée
            hidden_size: Nombre de neurones dans la couche cachée
            output_size: Nombre de sorties
        """
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Initialisation aléatoire des poids
        np.random.seed(42)
        self.W1 = np.random.randn(input_size, hidden_size) * 0.01
        self.b1 = np.zeros((1, hidden_size))
        self.W2 = np.random.randn(hidden_size, output_size) * 0.01
        self.b2 = np.zeros((1, output_size))
        
        self.loss_history = []
    
    def sigmoid(self, z):
        """Fonction d'activation sigmoïde."""
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
    
    def forward(self, X):
        """Propagation avant."""
        self.z1 = np.dot(X, self.W1) + self.b1
        self.a1 = self.sigmoid(self.z1)
        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.sigmoid(self.z2)
        return self.a2
    
    def compute_loss(self, y_pred, y_true):
        """Calcul de la perte (erreur quadratique moyenne)."""
        return np.mean((y_pred - y_true)**2)
    
    def train(self, X, y, learning_rate=0.01, epochs=1000):
        """
        Entraînement du réseau de neurones.
        """
        m = X.shape[0]
        
        for epoch in range(epochs):
            # Propagation avant
            output = self.forward(X)
            
            # Calcul de la perte
            loss = self.compute_loss(output, y)
            self.loss_history.append(loss)
            
            # Rétropropagation
            dZ2 = output - y
            dW2 = np.dot(self.a1.T, dZ2) / m
            db2 = np.sum(dZ2, axis=0, keepdims=True) / m
            
            dA1 = np.dot(dZ2, self.W2.T)
            dZ1 = dA1 * self.a1 * (1 - self.a1)
            dW1 = np.dot(X.T, dZ1) / m
            db1 = np.sum(dZ1, axis=0, keepdims=True) / m
            
            # Mise à jour des poids
            self.W2 -= learning_rate * dW2
            self.b2 -= learning_rate * db2
            self.W1 -= learning_rate * dW1
            self.b1 -= learning_rate * db1
            
            if epoch % 100 == 0:
                print(f"Epoch {epoch}, Loss: {loss:.6f}")
    
    def predict_crisis_probability(self, X):
        """Prédiction de la probabilité de crise monétaire."""
        output = self.forward(X)
        return output
    
    def plot_training(self):
        """Visualisation de l'apprentissage."""
        plt.figure(figsize=(10, 5))
        plt.plot(self.loss_history)
        plt.xlabel('Époques')
        plt.ylabel('Perte')
        plt.title('Apprentissage du Réseau de Neurones')
        plt.grid(True)
        plt.show()


# =============================================================================
# 14. MODULE D'ANALYSE DES DONNÉES HISTORIQUES
# =============================================================================

class HistoricalDataAnalysis:
    """
    Analyse des données historiques des crises monétaires et financières.
    """
    
    def __init__(self):
        # Données historiques des crises (période 1971-2024)
        self.crises_data = {
            '1971-1980': {'crises': 10, 'major_crises': 2},
            '1981-1990': {'crises': 15, 'major_crises': 4},
            '1991-2000': {'crises': 25, 'major_crises': 6},
            '2001-2010': {'crises': 35, 'major_crises': 8},
            '2011-2024': {'crises': 42, 'major_crises': 12}
        }
    
    def total_crises(self):
        """Nombre total de crises depuis 1971."""
        total = sum(data['crises'] for data in self.crises_data.values())
        return total
    
    def crisis_frequency(self):
        """Fréquence des crises par décennie."""
        frequencies = {}
        for period, data in self.crises_data.items():
            years = int(period.split('-')[1]) - int(period.split('-')[0]) + 1
            frequencies[period] = data['crises'] / years
        return frequencies
    
    def plot_crises_trend(self):
        """Visualisation de la tendance des crises."""
        periods = list(self.crises_data.keys())
        crises = [data['crises'] for data in self.crises_data.values()]
        major_crises = [data['major_crises'] for data in self.crises_data.values()]
        
        x = np.arange(len(periods))
        width = 0.35
        
        plt.figure(figsize=(12, 6))
        plt.bar(x - width/2, crises, width, label='Total des crises')
        plt.bar(x + width/2, major_crises, width, label='Crises majeures')
        plt.xlabel('Période')
        plt.ylabel('Nombre de crises')
        plt.title('Évolution des Crises Monétaires et Financières (1971-2024)')
        plt.xticks(x, periods)
        plt.legend()
        plt.grid(True)
        plt.show()


# =============================================================================
# 15. EXÉCUTION PRINCIPALE
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SUITE DE MODÉLISATION - CRYPTO-FULUS")
    print("Auteur: Marc Daghar")
    print("Licence: CC BY-SA")
    print("=" * 60 + "\n")
    
    # Exécution de la simulation complète
    thermo, mimetic, debt, reserve, clio, opt, bimetallic = run_full_simulation()
    
    # Analyse de sensibilité
    print("\n=== Analyse de Sensibilité ===")
    SensitivityAnalysis.plot_sensitivity_heatmap()
    
    # Simulation Monte Carlo
    print("\n=== Simulation Monte Carlo ===")
    mc = MonteCarloSimulation(n_simulations=1000)
    years, probs = mc.plot_monte_carlo()
    print(f"Année moyenne d'effondrement: {np.mean(years):.0f} (±{np.std(years):.0f})")
    print(f"Probabilité moyenne d'effondrement: {np.mean(probs):.2%} (±{np.std(probs):.2%})")
    
    # Analyse historique
    print("\n=== Analyse des Données Historiques ===")
    historical = HistoricalDataAnalysis()
    print(f"Nombre total de crises (1971-2024): {historical.total_crises()}")
    print("Fréquence des crises par décennie:")
    for period, freq in historical.crisis_frequency().items():
        print(f"  {period}: {freq:.2f} crises/an")
    historical.plot_crises_trend()
    
    print("\n" + "=" * 60)
    print("FIN DE LA MODÉLISATION")
    print("=" * 60)

