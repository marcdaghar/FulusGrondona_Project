# ============================================================================
# CRYPTO-FULUS PILOTE DORA - SIMULATION MULTI-AGENTS
# Liban 2025 - Modèle de transition monétaire
# ============================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import beta
import seaborn as sns
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Configuration du style des graphiques
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("Set2")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 11

# ============================================================================
# 1. PARAMÈTRES CALIBRÉS (DONNÉES LIBAN 2023-2025)
# ============================================================================

class ParametresLiban:
    """Paramètres macro-économiques calibrés sur les données du Liban"""
    
    # Taux de change (USD/LBP)
    USD_LBP_OFFICIEL = 15000
    USD_LBP_PARALLELE = 89500
    
    # Inflation et croissance
    INFLATION_EXTERNE = 0.452  # 45.2% annuel
    CROISSANCE_PIB = -0.075   # -7.5%
    
    # Paramètres de la guilde (calibrés)
    TAUX_ZAKAT = 0.025        # 2.5%
    SEUIL_ZAKAT = 50          # nisab en fulus
    TAUX_APPRENTISSAGE = 0.01 # vitesse d'ajustement de theta
    KAPPA_TRADE = 0.5         # sensibilité des échanges
    GAMMA_FULUS = 0.2         # effet de bouclage
    
    # PoSS (Proof of Social Stake)
    ALPHA_POSS = 0.4          # poids du solde
    BETA_POSS = 0.3           # poids de l'ancienneté
    GAMMA_POSS = 0.3          # poids de la réputation
    
    # Seuils de succès
    SEUIL_BOUCLAGE = 0.30
    SEUIL_LIQUIDITE = 0.80
    SEUIL_PARTICIPATION = 0.60
    SEUIL_INFLATION = 0.02
    SEUIL_UPTIME = 0.995

# ============================================================================
# 2. MODÈLE MULTI-AGENTS
# ============================================================================

class Agent:
    """Agent représentant un commerçant/membre de la guilde"""
    
    def __init__(self, id, solde_fulus=100, solde_dollar=500, theta=0.3):
        self.id = id
        self.s = solde_fulus           # solde en fulus
        self.d = solde_dollar          # solde en dollars
        self.theta = theta             # propension à utiliser le fulus [0,1]
        self.reputation = 0.0          # score de réputation (PoSS)
        self.anciennete = 0            # jours dans la guilde
        self.transactions_fulus = 0    # compteur
        self.transactions_dollar = 0
        self.votes = 0                 # nombre de votes
        self.solde_historique = [solde_fulus]
    
    def proba_trade(self, autre_agent):
        """Probabilité d'échange entre deux agents (effet réseau)"""
        theta_moyen = (self.theta + autre_agent.theta) / 2
        kappa = ParametresLiban.KAPPA_TRADE
        return 1 / (1 + np.exp(-kappa * theta_moyen * 10))
    
    def proba_fulus(self, autre_agent, bouclage_precedent):
        """Probabilité d'utiliser le fulus plutôt que le dollar"""
        gamma = ParametresLiban.GAMMA_FULUS
        # Plus le bouclage est élevé, plus on utilise le fulus
        effet_bouclage = 1 + gamma * (bouclage_precedent / ParametresLiban.SEUIL_BOUCLAGE)
        return min(1, self.theta * autre_agent.theta * effet_bouclage * 1.5)
    
    def trade(self, autre_agent, bouclage_precedent, prix_fulus=1.0, prix_dollar=1.0):
        """Effectue une transaction avec un autre agent"""
        if np.random.random() < self.proba_trade(autre_agent):
            # Volume de la transaction (basé sur les soldes)
            volume_fulus = min(self.s, autre_agent.s) * 0.1 * np.random.uniform(0.5, 1.5)
            volume_dollar = min(self.d, autre_agent.d) * 0.1 * np.random.uniform(0.5, 1.5)
            
            # Choix de la devise
            if np.random.random() < self.proba_fulus(autre_agent, bouclage_precedent):
                # Transaction en fulus
                valeur = min(volume_fulus, self.s)
                if valeur > 0:
                    self.s -= valeur
                    autre_agent.s += valeur
                    self.transactions_fulus += 1
                    autre_agent.transactions_fulus += 1
                    return 'fulus', valeur
            else:
                # Transaction en dollars
                valeur = min(volume_dollar, self.d)
                if valeur > 0:
                    self.d -= valeur
                    autre_agent.d += valeur
                    self.transactions_dollar += 1
                    autre_agent.transactions_dollar += 1
                    return 'dollar', valeur
        return None, 0
    
    def update_theta(self, solde_moyen):
        """Ajuste la propension à utiliser le fulus"""
        eta = ParametresLiban.TAUX_APPRENTISSAGE
        # Si l'agent a plus de fulus que la moyenne, il les utilise plus
        delta = (self.s - solde_moyen) / (solde_moyen + 1)
        self.theta += eta * delta
        self.theta = np.clip(self.theta, 0.05, 0.95)
    
    def update_anciennete(self):
        self.anciennete += 1
    
    def pay_zakat(self):
        """Paie la zakat si le solde dépasse le seuil"""
        if self.s > ParametresLiban.SEUIL_ZAKAT:
            zakat = ParametresLiban.TAUX_ZAKAT * (self.s - ParametresLiban.SEUIL_ZAKAT)
            self.s -= zakat
            return zakat
        return 0
    
    def voter(self, proposition):
        """Vote sur une proposition DAO"""
        if np.random.random() < 0.3:  # 30% de chance de voter (de base)
            self.votes += 1
            return np.random.choice([True, False], p=[0.6, 0.4])
        return None
    
    def valider_bloc(self, poids_total):
        """Valide un bloc selon le mécanisme PoSS"""
        poids = self.poids_validation()
        return np.random.random() < poids / poids_total
    
    def poids_validation(self):
        """Calcule le poids de validation (PoSS)"""
        alpha = ParametresLiban.ALPHA_POSS
        beta = ParametresLiban.BETA_POSS
        gamma = ParametresLiban.GAMMA_POSS
        # Normalisation simplifiée
        return (alpha * self.s / 100 + beta * self.anciennete / 100 + gamma * self.reputation / 10)
    
    def __repr__(self):
        return f"Agent {self.id}: s={self.s:.1f} F, d={self.d:.1f} $, theta={self.theta:.2f}"

# ============================================================================
# 3. SIMULATEUR DE LA GUILDE
# ============================================================================

class SimulateurGuilde:
    """Simulateur multi-agents de la guilde Dora"""
    
    def __init__(self, n_agents=50, duree=365, scenario='minimaliste'):
        self.n_agents = n_agents
        self.duree = duree
        self.scenario = scenario
        self.agents = [Agent(i) for i in range(n_agents)]
        self.historique = defaultdict(list)
        self.masse_monetaire = n_agents * 100  # Fulius initiaux
        self.chocs = []
        self.zakat_fonds = 0
        
        # Métriques
        self.metriques = {
            'bouclage': [],
            'liquidite': [],
            'participation': [],
            'inflation': [],
            'gini': [],
            'masse': [],
            'velocite': []
        }
        
        self.prix_panier = 1.0  # Prix du panier de biens en fulus
        self.prix_panier_hist = [1.0]
        self.volume_fulus_total = 0
        self.volume_dollar_total = 0
        
        # Appliquer la configuration du scénario
        self._configurer_scenario()
    
    def _configurer_scenario(self):
        """Configure les paramètres selon le scénario"""
        if self.scenario == 'minimaliste':
            # Pas de zakat, pas d'incitations
            self.zakat_actif = False
            self.incitations_actif = False
            self.bonus_vote = 0
            self.bonus_validation = 0
        elif self.scenario == 'social':
            # Zakat seul
            self.zakat_actif = True
            self.incitations_actif = False
            self.bonus_vote = 0
            self.bonus_validation = 0
        elif self.scenario == 'actif':
            # Zakat + Incitations
            self.zakat_actif = True
            self.incitations_actif = True
            self.bonus_vote = 0.5  # Bonus de réputation pour avoir voté
            self.bonus_validation = 1.0  # Bonus pour avoir validé un bloc
    
    def ajouter_choc(self, jour, type_choc, intensite):
        """Ajoute un choc exogène à la simulation"""
        self.chocs.append({
            'jour': jour,
            'type': type_choc,
            'intensite': intensite,
            'applique': False
        })
    
    def _appliquer_chocs(self, t):
        """Applique les chocs au moment approprié"""
        for choc in self.chocs:
            if not choc['applique'] and t >= choc['jour']:
                choc['applique'] = True
                type_choc = choc['type']
                intensite = choc['intensite']
                
                if type_choc == 'devaluation':
                    # Choc de change : les dollars perdent de la valeur relative
                    for agent in self.agents:
                        agent.theta *= (1 - intensite * 0.3)  # Baisse de confiance
                        agent.theta = np.clip(agent.theta, 0.05, 0.95)
                
                elif type_choc == 'inflation_externe':
                    # Choc d'inflation : les prix en dollar augmentent
                    self.prix_panier *= (1 + intensite * 0.5)
                
                elif type_choc == 'confiance':
                    # Choc de confiance : baisse générale de theta
                    for agent in self.agents:
                        agent.theta *= (1 - intensite * 0.2)
                        agent.theta = np.clip(agent.theta, 0.05, 0.95)
                
                elif type_choc == 'blocage_approvisionnement':
                    # Choc d'approvisionnement : raréfaction des biens
                    self.prix_panier *= (1 + intensite * 0.8)
    
    def _calculer_bouclage(self):
        """Calcule le taux de bouclage local"""
        total = self.volume_fulus_total + self.volume_dollar_total
        if total > 0:
            return self.volume_fulus_total / total
        return 0
    
    def _calculer_liquidite(self):
        """Calcule le ratio de liquidité (soldes < 15 jours)"""
        # Simulation simplifiée : on regarde les agents avec le plus de transactions
        actifs = sum(1 for a in self.agents if a.transactions_fulus + a.transactions_dollar > 5)
        return actifs / self.n_agents
    
    def _calculer_participation(self):
        """Calcule le taux de participation à la gouvernance"""
        votants = sum(1 for a in self.agents if a.votes > 0)
        return votants / self.n_agents
    
    def _calculer_inflation(self):
        """Calcule l'inflation en fulus"""
        if len(self.prix_panier_hist) > 1:
            return (self.prix_panier_hist[-1] - self.prix_panier_hist[-2]) / self.prix_panier_hist[-2]
        return 0
    
    def _calculer_gini(self):
        """Calcule le coefficient de Gini des soldes en fulus"""
        soldes = [a.s for a in self.agents]
        soldes_tries = np.sort(soldes)
        n = len(soldes_tries)
        if n == 0:
            return 0
        # Formule de Gini simplifiée
        somme = np.sum((2 * np.arange(1, n+1) - n - 1) * soldes_tries)
        return somme / (n * np.sum(soldes_tries)) if np.sum(soldes_tries) > 0 else 0
    
    def _calculer_velocite(self):
        """Calcule la vélocité de la monnaie"""
        volume_total = self.volume_fulus_total
        if self.masse_monetaire > 0 and volume_total > 0:
            return volume_total / (self.masse_monetaire / self.n_agents)
        return 0
    
    def _redistribuer_zakat(self):
        """Redistribue les fonds de zakat aux plus pauvres"""
        if self.zakat_fonds > 0:
            # Trouver les agents les plus pauvres
            soldes = [(i, a.s) for i, a in enumerate(self.agents)]
            soldes_tries = sorted(soldes, key=lambda x: x[1])
            # Redistribuer aux 30% les plus pauvres
            n_pauvres = max(1, int(self.n_agents * 0.3))
            part = self.zakat_fonds / n_pauvres
            for i in range(n_pauvres):
                idx = soldes_tries[i][0]
                self.agents[idx].s += part
            self.zakat_fonds = 0
    
    def _ajuster_masse_monetaire(self):
        """Ajuste la masse monétaire via la DAO (vote simulé)"""
        inflation = self._calculer_inflation()
        if abs(inflation) > 0.02:  # Si l'inflation sort des bornes
            if inflation > 0:
                # Réduire la masse si inflation trop forte
                self.masse_monetaire *= (1 - 0.01)
            else:
                # Augmenter la masse si déflation
                self.masse_monetaire *= (1 + 0.01)
    
    def _run_iteration(self, t):
        """Exécute une itération de la simulation"""
        # 1. Réinitialiser les compteurs de volume
        self.volume_fulus_total = 0
        self.volume_dollar_total = 0
        
        # 2. Paires d'agents aléatoires pour les échanges
        indices = np.random.permutation(self.n_agents)
        bouclage_precedent = self._calculer_bouclage()
        
        for i in range(0, self.n_agents - 1, 2):
            a1 = self.agents[indices[i]]
            a2 = self.agents[indices[i+1]]
            
            # Transaction A1 -> A2
            devise, valeur = a1.trade(a2, bouclage_precedent)
            if devise == 'fulus':
                self.volume_fulus_total += valeur
            elif devise == 'dollar':
                self.volume_dollar_total += valeur
            
            # Transaction A2 -> A1 (symétrique)
            devise, valeur = a2.trade(a1, bouclage_precedent)
            if devise == 'fulus':
                self.volume_fulus_total += valeur
            elif devise == 'dollar':
                self.volume_dollar_total += valeur
        
        # 3. Mise à jour des agents
        soldes_moyens = np.mean([a.s for a in self.agents])
        for agent in self.agents:
            agent.update_theta(soldes_moyens)
            agent.update_anciennete()
        
        # 4. Zakat
        if self.zakat_actif:
            zakat_total = 0
            for agent in self.agents:
                zakat_total += agent.pay_zakat()
            self.zakat_fonds += zakat_total
            if t % 30 == 0:  # Redistribution mensuelle
                self._redistribuer_zakat()
        
        # 5. Validation PoSS (simulée)
        for agent in self.agents:
            if agent.poids_validation() > np.random.random() * 2:
                if self.incitations_actif:
                    agent.reputation += self.bonus_validation
                # Simulation de validation de bloc
        
        # 6. Vote DAO (simulé)
        if t % 30 == 0:  # Vote mensuel
            for agent in self.agents:
                if agent.voter('ajustement_masse'):
                    if self.incitations_actif:
                        agent.reputation += self.bonus_vote
                # Vote pondéré par la réputation
                if np.random.random() < agent.reputation / 10:
                    agent.votes += 1
        
        # 7. Ajustement macro
        self._ajuster_masse_monetaire()
        
        # 8. Mise à jour des métriques
        bouclage = self._calculer_bouclage()
        liquidite = self._calculer_liquidite()
        participation = self._calculer_participation()
        inflation = self._calculer_inflation()
        gini = self._calculer_gini()
        velocite = self._calculer_velocite()
        
        self.metriques['bouclage'].append(bouclage)
        self.metriques['liquidite'].append(liquidite)
        self.metriques['participation'].append(participation)
        self.metriques['inflation'].append(inflation)
        self.metriques['gini'].append(gini)
        self.metriques['masse'].append(self.masse_monetaire)
        self.metriques['velocite'].append(velocite)
        
        # Mise à jour du prix du panier
        if len(self.prix_panier_hist) > 1:
            self.prix_panier *= (1 + inflation * 0.1)
        self.prix_panier_hist.append(self.prix_panier)
    
    def run(self, verbose=True):
        """Exécute la simulation complète"""
        if verbose:
            print(f"=== SIMULATION {self.scenario.upper()} ===")
            print(f"Agents: {self.n_agents}, Durée: {self.duree} jours")
            print(f"Zakat actif: {self.zakat_actif}")
            print(f"Incitations actif: {self.incitations_actif}")
            print("----------------------------------------")
        
        for t in range(self.duree):
            # Appliquer les chocs
            self._appliquer_chocs(t)
            
            # Exécuter l'itération
            self._run_iteration(t)
            
            if verbose and t % 30 == 0:
                bouclage = self.metriques['bouclage'][-1]
                print(f"Jour {t:3d}: Bouclage={bouclage:.2%}, "
                      f"θ_moyen={np.mean([a.theta for a in self.agents]):.2f}, "
                      f"Gini={self.metriques['gini'][-1]:.3f}")
        
        if verbose:
            print("----------------------------------------")
            print(f"Bouclage final: {self.metriques['bouclage'][-1]:.2%}")
            print(f"Gini final: {self.metriques['gini'][-1]:.3f}")
            print(f"Inflation moyenne: {np.mean(self.metriques['inflation']):.2%}")
            print("=== FIN SIMULATION ===")
        
        return self.metriques

# ============================================================================
# 4. FONCTION DE VISUALISATION
# ============================================================================

def visualiser_simulations(resultats_scenarios):
    """
    Visualise les résultats des trois scénarios
    resultats_scenarios: dict {nom_scenario: metriques}
    """
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('SIMULATION DU PILOTE DORA - LIBAN\nComparaison des Scénarios', fontsize=16, fontweight='bold')
    
    couleurs = {'minimaliste': '#e74c3c', 'social': '#3498db', 'actif': '#2ecc71'}
    
    # 1. Taux de bouclage local (β)
    ax = axes[0, 0]
    for nom, metriques in resultats_scenarios.items():
        ax.plot(metriques['bouclage'], label=nom.capitalize(), color=couleurs[nom], linewidth=2)
    ax.axhline(y=0.30, color='red', linestyle='--', alpha=0.5, label='Seuil (30%)')
    ax.set_title('Taux de Bouclage Local (β)', fontweight='bold')
    ax.set_xlabel('Jours')
    ax.set_ylabel('β')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Ratio de liquidité (λ)
    ax = axes[0, 1]
    for nom, metriques in resultats_scenarios.items():
        ax.plot(metriques['liquidite'], label=nom.capitalize(), color=couleurs[nom], linewidth=2)
    ax.axhline(y=0.80, color='red', linestyle='--', alpha=0.5, label='Seuil (80%)')
    ax.set_title('Ratio de Liquidité (λ)', fontweight='bold')
    ax.set_xlabel('Jours')
    ax.set_ylabel('λ')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 3. Participation à la gouvernance (ρ)
    ax = axes[0, 2]
    for nom, metriques in resultats_scenarios.items():
        ax.plot(metriques['participation'], label=nom.capitalize(), color=couleurs[nom], linewidth=2)
    ax.axhline(y=0.60, color='red', linestyle='--', alpha=0.5, label='Seuil (60%)')
    ax.set_title('Participation à la Gouvernance (ρ)', fontweight='bold')
    ax.set_xlabel('Jours')
    ax.set_ylabel('ρ')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 4. Inflation en fulus (π_f)
    ax = axes[1, 0]
    for nom, metriques in resultats_scenarios.items():
        ax.plot(metriques['inflation'], label=nom.capitalize(), color=couleurs[nom], linewidth=2)
    ax.axhline(y=0.02, color='red', linestyle='--', alpha=0.5, label='Seuil (2%)')
    ax.axhline(y=-0.02, color='red', linestyle='--', alpha=0.3)
    ax.set_title('Inflation en Fulus (π_f)', fontweight='bold')
    ax.set_xlabel('Jours')
    ax.set_ylabel('π_f')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 5. Coefficient de Gini (G)
    ax = axes[1, 1]
    for nom, metriques in resultats_scenarios.items():
        ax.plot(metriques['gini'], label=nom.capitalize(), color=couleurs[nom], linewidth=2)
    ax.set_title('Inégalité des Soldes (Gini)', fontweight='bold')
    ax.set_xlabel('Jours')
    ax.set_ylabel('G')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 6. Vélocité de la monnaie
    ax = axes[1, 2]
    for nom, metriques in resultats_scenarios.items():
        ax.plot(metriques['velocite'], label=nom.capitalize(), color=couleurs[nom], linewidth=2)
    ax.set_title('Vélocité de la Monnaie (V)', fontweight='bold')
    ax.set_xlabel('Jours')
    ax.set_ylabel('V')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

# ============================================================================
# 5. EXÉCUTION DES SCÉNARIOS
# ============================================================================

def executer_scenarios():
    """Exécute les trois scénarios et visualise les résultats"""
    
    # Paramètres communs
    N_AGENTS = 50
    DUREE = 365  # 1 an
    
    # --- Scénario 1: Minimaliste ---
    print("\n" + "="*60)
    print("LANCEMENT SCÉNARIO 1: MINIMALISTE")
    print("="*60)
    sim1 = SimulateurGuilde(n_agents=N_AGENTS, duree=DUREE, scenario='minimaliste')
    # Ajout de chocs
    sim1.ajouter_choc(90, 'devaluation', 0.3)
    sim1.ajouter_choc(200, 'inflation_externe', 0.5)
    sim1.ajouter_choc(300, 'confiance', 0.2)
    resultats1 = sim1.run(verbose=True)
    
    # --- Scénario 2: Social (Zakat) ---
    print("\n" + "="*60)
    print("LANCEMENT SCÉNARIO 2: SOCIAL (ZAKAT)")
    print("="*60)
    sim2 = SimulateurGuilde(n_agents=N_AGENTS, duree=DUREE, scenario='social')
    sim2.ajouter_choc(90, 'devaluation', 0.3)
    sim2.ajouter_choc(200, 'inflation_externe', 0.5)
    sim2.ajouter_choc(300, 'confiance', 0.2)
    resultats2 = sim2.run(verbose=True)
    
    # --- Scénario 3: Actif (Zakat + Incitations) ---
    print("\n" + "="*60)
    print("LANCEMENT SCÉNARIO 3: ACTIF (ZAKAT + INCITATIONS)")
    print("="*60)
    sim3 = SimulateurGuilde(n_agents=N_AGENTS, duree=DUREE, scenario='actif')
    sim3.ajouter_choc(90, 'devaluation', 0.3)
    sim3.ajouter_choc(200, 'inflation_externe', 0.5)
    sim3.ajouter_choc(300, 'confiance', 0.2)
    resultats3 = sim3.run(verbose=True)
    
    # --- Regrouper les résultats ---
    resultats = {
        'minimaliste': resultats1,
        'social': resultats2,
        'actif': resultats3
    }
    
    # --- Visualisation ---
    fig = visualiser_simulations(resultats)
    plt.savefig('simulation_pilote_dora.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # --- Synthèse finale ---
    print("\n" + "="*60)
    print("SYNTHÈSE DES RÉSULTATS")
    print("="*60)
    
    synthese = pd.DataFrame({
        'Scénario': ['Minimaliste', 'Social (Zakat)', 'Actif (Zakat+Incitations)'],
        'β final': [resultats1['bouclage'][-1], resultats2['bouclage'][-1], resultats3['bouclage'][-1]],
        'λ final': [resultats1['liquidite'][-1], resultats2['liquidite'][-1], resultats3['liquidite'][-1]],
        'ρ final': [resultats1['participation'][-1], resultats2['participation'][-1], resultats3['participation'][-1]],
        'π_f moyen': [np.mean(resultats1['inflation']), np.mean(resultats2['inflation']), np.mean(resultats3['inflation'])],
        'G final': [resultats1['gini'][-1], resultats2['gini'][-1], resultats3['gini'][-1]],
        'Succès (S≥0.7)': [
            '❌' if np.mean(resultats1['bouclage']) < 0.3 else '✅',
            '✅' if np.mean(resultats2['bouclage']) >= 0.3 else '❌',
            '✅' if np.mean(resultats3['bouclage']) >= 0.3 else '❌'
        ]
    })
    
    print(synthese.to_string(index=False))
    
    # Analyse des chocs
    print("\n--- EFFET DES CHOCS ---")
    for i, (nom, metriques) in enumerate([('Minimaliste', resultats1), ('Social', resultats2), ('Actif', resultats3)]):
        # Impact du choc de confiance à J+300
        if len(metriques['bouclage']) > 300:
            avant_choc = np.mean(metriques['bouclage'][290:300])
            apres_choc = np.mean(metriques['bouclage'][310:320])
            impact = (apres_choc - avant_choc) / avant_choc
            print(f"{nom}: Choc de confiance → β {impact:+.2%}")
    
    return resultats

# ============================================================================
# 6. EXÉCUTION PRINCIPALE
# ============================================================================

if __name__ == "__main__":
    # Exécuter la simulation
    resultats = executer_scenarios()
    
    print("\n" + "="*60)
    print("FIN DE LA SIMULATION")
    print("Sursum corda.")
    print("="*60)

# ============================================================================
# ANNEXE: FONCTIONS D'ANALYSE SUPPLÉMENTAIRES
# ============================================================================

def analyse_sensibilite():
    """
    Analyse de sensibilité des paramètres clés
    À exécuter séparément pour explorer l'espace des paramètres
    """
    print("\n=== ANALYSE DE SENSIBILITÉ ===")
    
    # Test de l'impact du taux de zakat
    taux_zakat_test = [0, 0.025, 0.05, 0.075]
    results_zakat = []
    
    for tau in taux_zakat_test:
        sim = SimulateurGuilde(n_agents=50, duree=180, scenario='social')
        ParametresLiban.TAUX_ZAKAT = tau
        metriques = sim.run(verbose=False)
        results_zakat.append({
            'tau_zakat': tau,
            'β_final': metriques['bouclage'][-1],
            'G_final': metriques['gini'][-1]
        })
    
    df_zakat = pd.DataFrame(results_zakat)
    print("\nImpact du taux de zakat:")
    print(df_zakat.to_string(index=False))
    
    # Test de l'impact du seuil de zakat (nisab)
    seuil_test = [25, 50, 75, 100]
    results_seuil = []
    
    for seuil in seuil_test:
        sim = SimulateurGuilde(n_agents=50, duree=180, scenario='social')
        ParametresLiban.SEUIL_ZAKAT = seuil
        metriques = sim.run(verbose=False)
        results_seuil.append({
            'seuil_nisab': seuil,
            'β_final': metriques['bouclage'][-1],
            'G_final': metriques['gini'][-1]
        })
    
    df_seuil = pd.DataFrame(results_seuil)
    print("\nImpact du seuil de zakat (nisab):")
    print(df_seuil.to_string(index=False))
    
    return df_zakat, df_seuil

# Exemple d'appel (décommenter pour exécuter)
# analyse_sensibilite()

Composant
Description
ParametresLiban
