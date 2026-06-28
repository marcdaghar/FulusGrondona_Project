import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm
from collections import defaultdict
import random

# --- 1. Définition de l'Agent ---
class Agent:
    """
    Un agent économique individuel dans le modèle mimétique monétaire.
    """
    def __init__(self, agent_id, wealth_initial, nisab_threshold, tau_zakat, alpha_initial=0.5, risk_aversion=1.0):
        """
        Initialise un agent.
        
        :param agent_id: Identifiant unique de l'agent.
        :param wealth_initial: Richesse initiale (en unités de compte).
        :param nisab_threshold: Seuil du Nisab pour l'agent (peut être identique ou variable).
        :param tau_zakat: Taux de Zakat.
        :param alpha_initial: Proportion initiale de la richesse détenue en fulus (monnaie locale).
        :param risk_aversion: Coefficient d'aversion au risque (influence la sensibilité au désir mimétique).
        """
        self.id = agent_id
        self.wealth = wealth_initial
        self.alpha = alpha_initial  # Part de la richesse en fulus
        self.nisab = nisab_threshold
        self.tau_zakat = tau_zakat
        self.risk_aversion = risk_aversion
        self.desire_history = []  # Pour tracer l'évolution du désir
        self.wealth_history = []
        
    def compute_desire_for_money(self, avg_desire_others, liquidity_need=0.5):
        """
        Calcule le désir d'argent de l'agent, influencé par le désir des autres (mimétisme).
        
        :param avg_desire_others: Désir moyen des autres agents.
        :param liquidity_need: Besoin de liquidité individuel (0 à 1).
        :return: Niveau de désir (0 à 1).
        """
        # Désir de base : besoin de liquidité et aversion au risque
        base_desire = liquidity_need * (1 - self.risk_aversion * 0.1)
        
        # Composante mimétique (Girard) : le désir est amplifié par le désir des autres
        # On utilise une fonction sigmoïde pour capter l'effet de seuil (potentia multitudinis)
        mimetic_component = 1 / (1 + np.exp(-5 * (avg_desire_others - 0.5)))
        
        # Désir total
        desire = 0.4 * base_desire + 0.6 * mimetic_component
        self.desire_history.append(desire)
        return min(desire, 1.0)  # Normalisation

    def allocate_wealth(self, inflation_rate, return_on_nuqud=0.02):
        """
        Décide de l'allocation entre fulus et nuqud en minimisant le coût de détention.
        
        :param inflation_rate: Taux d'inflation du fulus.
        :param return_on_nuqud: Rendement alternatif du nuqud (coût d'opportunité).
        """
        # Coût de détention du fulus : inflation + zakat sur le fulus
        cost_fulus = inflation_rate + self.tau_zakat
        
        # Coût de détention du nuqud : coût d'opportunité (manque à gagner) + zakat sur le nuqud
        cost_nuqud = return_on_nuqud + self.tau_zakat
        
        # L'agent ajuste son alpha en fonction des coûts relatifs (modèle de choix discret)
        if cost_fulus < cost_nuqud:
            # Le fulus est moins cher : on augmente la part en fulus
            self.alpha = min(1.0, self.alpha + 0.05)
        elif cost_fulus > cost_nuqud:
            # Le nuqud est moins cher : on augmente la part en nuqud
            self.alpha = max(0.0, self.alpha - 0.05)
        # Si égalité, on ne change rien

    def pay_zakat(self):
        """
        Calcule et prélève la Zakat si la richesse dépasse le seuil du Nisab.
        :return: Montant de la Zakat prélevée.
        """
        if self.wealth > self.nisab:
            zakat_amount = self.tau_zakat * (self.wealth - self.nisab)
            self.wealth -= zakat_amount
            return zakat_amount
        return 0.0

    def update_wealth(self, trade_gain, zakat_redistribution=0):
        """
        Met à jour la richesse de l'agent après les échanges et la redistribution.
        
        :param trade_gain: Gain (ou perte) issu des échanges commerciaux.
        :param zakat_redistribution: Montant de Zakat reçu (redistribution).
        """
        # Croissance de la richesse via le commerce
        self.wealth += trade_gain
        # Redistribution de la Zakat
        self.wealth += zakat_redistribution
        # Enregistrement de l'historique
        self.wealth_history.append(self.wealth)

# --- 2. Système Monétaire ---
class MonetarySystem:
    """
    Définit les paramètres macroéconomiques et la politique monétaire.
    """
    def __init__(self, inflation_target=0.02, zakat_rate=0.025, nisab_universal=100.0):
        self.inflation_target = inflation_target
        self.zakat_rate = zakat_rate
        self.nisab_universal = nisab_universal
        self.total_zakat_collected = 0
        self.total_zakat_redistributed = 0

    def compute_inflation(self, money_supply_growth, velocity_shock=0):
        """
        Calcule l'inflation en fonction de la croissance de la masse monétaire.
        
        :param money_supply_growth: Croissance de la masse monétaire.
        :param velocity_shock: Choc exogène sur la vélocité (crise axiologique).
        :return: Taux d'inflation.
        """
        # Équation de Fisher modifiée : inflation = croissance monétaire - croissance économique + choc de vélocité
        economic_growth = 0.02  # Hypothèse de croissance réelle
        inflation = money_supply_growth - economic_growth + velocity_shock
        return max(0, inflation)  # L'inflation ne peut pas être négative (déflation possible, mais on simplifie)

    def calculate_velocity(self, crisis_level=0):
        """
        Calcule la vélocité de la monnaie, qui s'envole en cas de crise de confiance.
        
        :param crisis_level: Niveau de crise (0 = normal, 1 = effondrement).
        :return: Vélocité de la monnaie.
        """
        # Vitesse de base
        base_velocity = 1.5
        # Amplification exponentielle en cas de crise
        if crisis_level > 0:
            velocity = base_velocity * np.exp(2 * crisis_level)
        else:
            velocity = base_velocity
        return velocity

# --- 3. Simulation ---
class Simulation:
    """
    Orchestre l'exécution du modèle agent-based.
    """
    def __init__(self, num_agents=100, num_steps=100, seed=42):
        np.random.seed(seed)
        random.seed(seed)
        
        self.num_agents = num_agents
        self.num_steps = num_steps
        self.agents = []
        self.monetary_system = MonetarySystem()
        self.data = defaultdict(list)
        self.total_wealth_history = []
        self.zakat_pool = 0

        # Initialisation des agents avec des richesses hétérogènes (distribution de Pareto)
        wealths = np.random.pareto(1.5, num_agents) * 50 + 20
        nisab_universal = self.monetary_system.nisab_universal
        
        for i in range(num_agents):
            agent = Agent(
                agent_id=i,
                wealth_initial=wealths[i],
                nisab_threshold=nisab_universal,
                tau_zakat=self.monetary_system.zakat_rate,
                alpha_initial=np.random.uniform(0.2, 0.8),
                risk_aversion=np.random.uniform(0.5, 1.5)
            )
            self.agents.append(agent)

    def run_step(self, step):
        """
        Exécute une étape de la simulation.
        """
        # 1. Calcul de la crise axiologique (basée sur la dispersion de la croyance)
        desires = [agent.compute_desire_for_money(np.mean([a.desire_history[-1] if a.desire_history else 0.5 for a in self.agents])) for agent in self.agents]
        avg_desire = np.mean(desires)
        desire_std = np.std(desires)
        crisis_level = min(1.0, desire_std * 2)  # Une forte dispersion indique une crise
        
        # 2. Calcul de l'inflation et de la vélocité
        money_supply_growth = 0.03  # Hypothèse de création monétaire
        inflation = self.monetary_system.compute_inflation(money_supply_growth, crisis_level * 0.5)
        velocity = self.monetary_system.calculate_velocity(crisis_level)

        # 3. Collecte de la Zakat
        total_zakat = 0
        for agent in self.agents:
            zakat = agent.pay_zakat()
            total_zakat += zakat
        self.zakat_pool += total_zakat * 0.8  # 80% de la Zakat est redistribuée (les 20% restants couvrent les frais de gestion)

        # 4. Redistribution de la Zakat (aux agents les plus pauvres)
        if self.zakat_pool > 0:
            # Trier les agents par richesse (du plus pauvre au plus riche)
            sorted_agents = sorted(self.agents, key=lambda a: a.wealth)
            # Redistribuer aux 20% les plus pauvres
            num_recipients = int(0.2 * self.num_agents)
            recipients = sorted_agents[:num_recipients]
            zakat_per_recipient = self.zakat_pool / num_recipients if num_recipients > 0 else 0
            for agent in recipients:
                agent.update_wealth(trade_gain=0, zakat_redistribution=zakat_per_recipient)
            self.zakat_pool = 0  # Le pool est vide

        # 5. Échanges commerciaux et ajustement de l'allocation
        for agent in self.agents:
            # Gain commercial aléatoire (simulant des échanges de biens)
            trade_gain = np.random.normal(0, 1) * 0.5
            agent.update_wealth(trade_gain=trade_gain)
            
            # Ajustement de l'allocation en fonction de l'inflation
            agent.allocate_wealth(inflation)

        # 6. Enregistrement des données agrégées
        total_wealth = sum(a.wealth for a in self.agents)
        avg_alpha = np.mean([a.alpha for a in self.agents])
        avg_desire_collective = np.mean([a.desire_history[-1] if a.desire_history else 0.5 for a in self.agents])
        gini_coefficient = self.compute_gini([a.wealth for a in self.agents])
        
        self.total_wealth_history.append(total_wealth)
        self.data['step'].append(step)
        self.data['total_wealth'].append(total_wealth)
        self.data['avg_alpha'].append(avg_alpha)
        self.data['avg_desire'].append(avg_desire_collective)
        self.data['crisis_level'].append(crisis_level)
        self.data['inflation'].append(inflation)
        self.data['velocity'].append(velocity)
        self.data['gini'].append(gini_coefficient)
        self.data['total_zakat'].append(total_zakat)

    def compute_gini(self, wealth_list):
        """
        Calcule le coefficient de Gini pour mesurer l'inégalité.
        """
        sorted_wealth = np.sort(wealth_list)
        n = len(sorted_wealth)
        cumulative = np.cumsum(sorted_wealth)
        return (2 * np.sum((np.arange(1, n+1) * sorted_wealth)) / (n * np.sum(sorted_wealth))) - (n + 1) / n

    def run(self):
        """
        Lance la simulation sur le nombre d'étapes défini.
        """
        for step in range(self.num_steps):
            self.run_step(step)
            if step % 10 == 0:
                print(f"Étape {step}: Richesse Totale = {self.total_wealth_history[-1]:.2f}, Gini = {self.data['gini'][-1]:.3f}")

    def plot_results(self):
        """
        Visualise les résultats de la simulation.
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        
        # 1. Richesse totale
        axes[0, 0].plot(self.data['step'], self.data['total_wealth'], label='Richesse Totale', color='green')
        axes[0, 0].set_title('Richesse Totale (Économie)')
        axes[0, 0].set_xlabel('Temps')
        axes[0, 0].set_ylabel('Richesse')
        axes[0, 0].grid(True)
        
        # 2. Inflation et crise
        axes[0, 1].plot(self.data['step'], self.data['inflation'], label='Inflation', color='red')
        axes[0, 1].plot(self.data['step'], self.data['crisis_level'], label='Niveau de Crise', color='orange', linestyle='--')
        axes[0, 1].set_title('Inflation et Crise Axiologique')
        axes[0, 1].set_xlabel('Temps')
        axes[0, 1].grid(True)
        axes[0, 1].legend()
        
        # 3. Vélocité de la monnaie
        axes[0, 2].plot(self.data['step'], self.data['velocity'], label='Vélocité', color='purple')
        axes[0, 2].set_title('Vélocité de la Monnaie')
        axes[0, 2].set_xlabel('Temps')
        axes[0, 2].grid(True)
        
        # 4. Allocation (Alpha)
        axes[1, 0].plot(self.data['step'], self.data['avg_alpha'], label='Alpha (Fulus)', color='blue')
        axes[1, 0].set_title('Allocation Moyenne (Fulus vs Nuqud)')
        axes[1, 0].set_xlabel('Temps')
        axes[1, 0].set_ylabel('Proportion en Fulus')
        axes[1, 0].grid(True)
        
        # 5. Désir d'argent collectif
        axes[1, 1].plot(self.data['step'], self.data['avg_desire'], label='Désir Collectif', color='brown')
        axes[1, 1].set_title('Désir Mimétique Collectif (Argent)')
        axes[1, 1].set_xlabel('Temps')
        axes[1, 1].set_ylabel('Niveau de Désir')
        axes[1, 1].grid(True)
        
        # 6. Inégalité (Gini)
        axes[1, 2].plot(self.data['step'], self.data['gini'], label='Gini', color='black')
        axes[1, 2].set_title("Coefficient de Gini (Inégalité)")
        axes[1, 2].set_xlabel('Temps')
        axes[1, 2].set_ylabel('Gini')
        axes[1, 2].grid(True)
        
        plt.tight_layout()
        plt.savefig('simulation_monetaire.png', dpi=300)
        plt.show()

# --- 4. Exécution ---
if __name__ == "__main__":
    # Créer et lancer la simulation
    sim = Simulation(num_agents=150, num_steps=120)
    sim.run()
    sim.plot_results()
    
    # Affichage des statistiques finales
    print("\n--- STATISTIQUES FINALES ---")
    print(f"Richesse Totale Finale: {sim.total_wealth_history[-1]:.2f}")
    print(f"Gini Final: {sim.data['gini'][-1]:.3f}")
    print(f"Alpha Moyen Final: {sim.data['avg_alpha'][-1]:.3f}")
    print(f"Inflation Moyenne: {np.mean(sim.data['inflation']):.3f}")

