"""
Modèle Intégrateur - Monnaie, Usure et Rupture
----------------------------------------------
Simulation d'un système monétaire alternatif (Franc-Jy) basé sur :
- Neurocognition (douleur de payer, récompense, contrôle)
- Psychologie sociale (contagion, comptabilité mentale)
- Gouvernance décentralisée (shura, guildes, zakat)
- Modélisation économique (vélocité monétaire, adoption mimétique)
- Dynamique des réseaux (Ricci flow sur réseaux de confiance)
"""

import numpy as np
import networkx as nx
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Any
from enum import Enum
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import random

# ============================================================
# 1. ÉNUMÉRATIONS ET STRUCTURES DE DONNÉES DE BASE
# ============================================================

class PaymentMode(Enum):
    """Modes de paiement avec différents niveaux d'abstraction."""
    CASH = "cash"          # Douleur de payer élevée
    CARD = "card"          # Douleur moyenne
    MOBILE = "mobile"      # Douleur faible
    CRYPTO = "crypto"      # Douleur très faible (abstraction maximale)

class ExpenseCategory(Enum):
    """Catégories de dépenses avec des valences émotionnelles différentes."""
    NECESSITY = "necessites"      # Faible récompense anticipée
    LEISURE = "loisirs"           # Forte récompense anticipée
    INVESTMENT = "investissement" # Gratification différée
    SOCIAL = "social"             # Valeur sociale élevée
    ZAKAT = "zakat"              # Prélèvement obligatoire (Zakat)

class Grade(Enum):
    """Grades au sein de la guilde (primo inter pares)."""
    APPRENTI = "apprenti"
    COMPAGNON = "compagnon"
    MAITRE_OFFICIER = "maitre_officier"
    MAITRE_EXECUTIF = "maitre_executif"
    MAITRE_SHEYKH = "maitre_sheykh"

# ============================================================
# 2. COUCHE NEUROCOGNITIVE (Psychologie sociale + Neuroéconomie)
# ============================================================

@dataclass
class NeuralSignals:
    """Simulation des activations cérébrales."""
    striatum: float = 0.0      # Récompense anticipée (désir d'achat)
    insula: float = 0.0        # Douleur de payer (aversion)
    dlpfc: float = 0.0         # Contrôle cognitif (arbitrage)
    amygdala: float = 0.0      # Réponse émotionnelle (peur/confiance)
    
    def to_dict(self) -> Dict[str, float]:
        return {
            'striatum': self.striatum,
            'insula': self.insula,
            'dlpfc': self.dlpfc,
            'amygdala': self.amygdala
        }

@dataclass
class MentalAccounts:
    """Comptabilité mentale (Thaler, 1985)."""
    necessities: float = 0.35
    leisure: float = 0.25
    savings: float = 0.30
    social: float = 0.10
    
    def get_allocation(self, category: ExpenseCategory) -> float:
        mapping = {
            ExpenseCategory.NECESSITY: self.necessities,
            ExpenseCategory.LEISURE: self.leisure,
            ExpenseCategory.INVESTMENT: self.savings,
            ExpenseCategory.SOCIAL: self.social,
            ExpenseCategory.ZAKAT: 0.0  # La Zakat n'est pas une dépense volontaire
        }
        return mapping.get(category, 0.20)

class HumanCognition:
    """
    Modélise les processus neurocognitifs et psychosociaux influençant
    les décisions d'épargne et de dépense.
    """
    
    def __init__(self, agent, personality_profile: str = "balanced"):
        self.agent = agent
        self.personality_profile = personality_profile
        
        # Paramètres neurocognitifs initiaux (influencés par la génétique/expérience)
        self._init_neural_parameters(personality_profile)
        
        # Comptabilité mentale
        self.mental_accounts = MentalAccounts()
        
        # État dynamique
        self.current_mood: float = 0.5      # 0 = négatif, 1 = positif
        self.cognitive_load: float = 0.0    # 0 = repos, 1 = surcharge
        self.social_pressure: Dict[str, float] = defaultdict(float)
        
        # Historique des décisions pour adaptation
        self.decision_history: List[Dict] = []
        self.neural_history: List[NeuralSignals] = []
        
        # Mode de paiement préféré (influencé socialement)
        self.preferred_payment = PaymentMode.CARD
        
        # Réseau social (pour influence)
        self.social_network = []
        
        # État de confiance dans le système
        self.system_trust = 0.5
        
    def _init_neural_parameters(self, profile: str):
        """Initialise les paramètres selon un profil psychologique."""
        profiles = {
            "balanced": {
                'pain_sensitivity': 0.7,
                'reward_sensitivity': 0.7,
                'self_control': 0.7,
                'emotional_reactivity': 0.5,
                'social_conformity': 0.5
            },
            "impulsive": {
                'pain_sensitivity': 0.4,
                'reward_sensitivity': 1.2,
                'self_control': 0.3,
                'emotional_reactivity': 0.8,
                'social_conformity': 0.7
            },
            "frugal": {
                'pain_sensitivity': 1.1,
                'reward_sensitivity': 0.5,
                'self_control': 0.9,
                'emotional_reactivity': 0.4,
                'social_conformity': 0.3
            },
            "social": {
                'pain_sensitivity': 0.6,
                'reward_sensitivity': 0.9,
                'self_control': 0.5,
                'emotional_reactivity': 0.9,
                'social_conformity': 0.9
            },
            "ascetic": {
                'pain_sensitivity': 0.8,
                'reward_sensitivity': 0.3,
                'self_control': 0.9,
                'emotional_reactivity': 0.3,
                'social_conformity': 0.2
            }
        }
        params = profiles.get(profile, profiles["balanced"])
        self.pain_sensitivity = params['pain_sensitivity']
        self.reward_sensitivity = params['reward_sensitivity']
        self.self_control = params['self_control']
        self.emotional_reactivity = params['emotional_reactivity']
        self.social_conformity = params['social_conformity']
    
    def compute_pain_of_paying(self, amount: float, payment_mode: PaymentMode) -> float:
        """
        Calcule la douleur de payer (activation insulaire).
        Basé sur Mazar et al. (2017) : les paiements abstraits réduisent la douleur.
        """
        # Base : proportion de la richesse
        base_pain = amount / (self.agent.wealth + 1000)
        
        # Facteur d'abstraction du paiement (plus abstrait = moins de douleur)
        abstraction_factors = {
            PaymentMode.CASH: 1.0,
            PaymentMode.CARD: 0.55,
            PaymentMode.MOBILE: 0.45,
            PaymentMode.CRYPTO: 0.35
        }
        
        # Modulation par sensibilité individuelle et contexte émotionnel
        pain = (base_pain * abstraction_factors[payment_mode] * 
                self.pain_sensitivity * (1 + 0.5 * self.cognitive_load))
        
        # Effet "déjà dépensé" : les dépenses répétées désensibilisent
        recent_spending = sum(d['amount'] for d in self.decision_history[-10:] 
                            if d.get('action') == 'spend')
        if recent_spending > self.agent.wealth * 0.3:
            pain *= 0.8  # Désensibilisation partielle
        
        return np.clip(pain, 0.0, 1.0)
    
    def compute_anticipated_reward(self, amount: float, category: ExpenseCategory) -> float:
        """
        Calcule la récompense anticipée (activation striatale).
        Basé sur Knutson et al. (2007) : anticipation d'achat.
        """
        # Les différentes catégories activent différemment le striatum
        category_multipliers = {
            ExpenseCategory.LEISURE: 1.3,      # Plaisir immédiat fort
            ExpenseCategory.SOCIAL: 1.2,       # Valeur sociale
            ExpenseCategory.NECESSITY: 0.7,    # Utilité mais faible plaisir
            ExpenseCategory.INVESTMENT: 0.5,   # Gratification différée
            ExpenseCategory.ZAKAT: 0.1         # La Zakat active peu le striatum
        }
        
        base_reward = amount * category_multipliers.get(category, 1.0)
        
        # Modulation par l'humeur et la sensibilité à la récompense
        mood_mod = 0.8 + 0.4 * self.current_mood
        reward = base_reward * self.reward_sensitivity * mood_mod
        
        # Effet de rareté : les biens perçus comme rares augmentent la récompense anticipée
        if category == ExpenseCategory.LEISURE and self._perceive_scarcity():
            reward *= 1.3
        
        return np.clip(reward, 0.0, amount * 1.5)
    
    def compute_cognitive_control(self, pain: float, reward: float) -> float:
        """
        Simule le contrôle cognitif (dlPFC) dans l'arbitrage.
        """
        # Conflit entre douleur et récompense
        conflict = abs(reward - pain)
        
        # Capacité de contrôle réduite par la charge cognitive
        effective_control = self.self_control * (1 - 0.5 * self.cognitive_load)
        
        # Le contrôle permet de surmonter le conflit
        control_success = conflict * effective_control
        return np.clip(control_success, 0.0, 1.0)
    
    def _get_mental_account_balance(self, category: ExpenseCategory) -> float:
        """Calcule le solde d'un compte mental."""
        target_allocation = self.mental_accounts.get_allocation(category)
        current_spending = sum(d['amount'] for d in self.decision_history[-30:] 
                              if d.get('category') == category)
        
        # Revenu approximatif sur la période
        estimated_income = self.agent.wealth * 0.1
        allocated = target_allocation * estimated_income
        return max(0, allocated - current_spending)
    
    def _compute_mental_account_penalty(self, amount: float, category: ExpenseCategory) -> float:
        """
        Pénalité si la dépense dépasse le compte mental alloué.
        """
        balance = self._get_mental_account_balance(category)
        if amount <= balance:
            return 1.0  # Pas de pénalité
        else:
            # Pénalité proportionnelle au dépassement
            overshoot = (amount - balance) / (balance + 1)
            return max(0.3, 1.0 - overshoot)
    
    def update_social_influence(self, neighbors: List):
        """
        Met à jour les paramètres cognitifs par influence sociale.
        Implémente la contagion des préférences de paiement et des biais.
        """
        if not neighbors:
            return
        
        # Influence sur le mode de paiement préféré
        neighbor_payments = [n.cognition.preferred_payment for n in neighbors 
                            if hasattr(n, 'cognition')]
        if neighbor_payments:
            # Convergence partielle vers le mode dominant
            dominant = max(set(neighbor_payments), key=neighbor_payments.count)
            influence_strength = 0.05 * len(neighbors) / 10
            if np.random.random() < influence_strength:
                self.preferred_payment = dominant
        
        # Influence sur la sensibilité à la douleur (conformité sociale)
        pain_sensitivities = [n.cognition.pain_sensitivity for n in neighbors 
                            if hasattr(n, 'cognition')]
        if pain_sensitivities:
            avg_pain = np.mean(pain_sensitivities)
            # Convergence lente vers la moyenne sociale
            self.pain_sensitivity = (0.95 * self.pain_sensitivity + 
                                    0.05 * avg_pain)
        
        # Influence sur la sensibilité à la récompense
        reward_sensitivities = [n.cognition.reward_sensitivity for n in neighbors 
                               if hasattr(n, 'cognition')]
        if reward_sensitivities:
            avg_reward = np.mean(reward_sensitivities)
            self.reward_sensitivity = (0.95 * self.reward_sensitivity + 
                                      0.05 * avg_reward)
        
        # Influence sur la confiance dans le système
        trust_levels = [n.cognition.system_trust for n in neighbors 
                       if hasattr(n, 'cognition')]
        if trust_levels:
            avg_trust = np.mean(trust_levels)
            self.system_trust = (0.97 * self.system_trust + 
                                0.03 * avg_trust)
    
    def compute_social_pressure(self, expense_category: ExpenseCategory) -> float:
        """
        Calcule la pression sociale à dépenser dans une catégorie.
        Effet "keep up with the Joneses".
        """
        base_pressure = self.social_pressure.get(expense_category.value, 0.0)
        
        # Modulation par la connectivité sociale et la conformité
        if hasattr(self.agent, 'social_connections'):
            n_connections = len(self.agent.social_connections)
            pressure = base_pressure * (1 + 0.1 * n_connections) * self.social_conformity
        else:
            pressure = base_pressure
        
        return np.clip(pressure, 0.0, 1.0)
    
    def _update_emotional_state(self):
        """Met à jour l'humeur et la charge cognitive."""
        # L'humeur évolue avec les décisions récentes
        recent_decisions = self.decision_history[-5:] if self.decision_history else []
        if recent_decisions:
            success_rate = sum(1 for d in recent_decisions 
                             if d.get('satisfaction', 0.5) > 0.6) / len(recent_decisions)
            self.current_mood = 0.5 + 0.3 * (success_rate - 0.5)
        else:
            self.current_mood = 0.5 + 0.1 * np.random.randn()
        
        # Charge cognitive influencée par la complexité des décisions récentes
        self.cognitive_load = min(1.0, self.cognitive_load * 0.9 + 0.05 * np.random.rand())
        
        # La confiance dans le système est stable mais peut fluctuer
        self.system_trust = np.clip(self.system_trust + 0.01 * np.random.randn(), 0.1, 0.9)
    
    def _compute_emotional_valence(self, opportunity: Dict) -> float:
        """
        Réponse émotionnelle à l'opportunité (amygdale).
        Influencée par la confiance, la familiarité, et l'urgence.
        """
        valence = 0.0
        
        # Confiance (si applicable)
        if 'trust' in opportunity:
            valence += opportunity['trust'] * 0.5
        
        # Familiarité du bien/service
        if 'familiarity' in opportunity:
            valence += opportunity['familiarity'] * 0.3
        
        # Urgence (les dépenses urgentes génèrent une émotion plus forte)
        if opportunity.get('urgent', False):
            valence += 0.4
        
        # Modulation par la réactivité émotionnelle
        return np.clip(valence * self.emotional_reactivity, -0.5, 0.5)
    
    def _record_neural_signals(self, pain: float, reward: float, control: float, emotion: float):
        """Enregistre les signaux neuronaux pour analyse ultérieure."""
        signals = NeuralSignals(
            striatum=reward,
            insula=pain,
            dlpfc=control,
            amygdala=emotion
        )
        self.neural_history.append(signals)
        # Garder historique limité
        if len(self.neural_history) > 100:
            self.neural_history.pop(0)
    
    def _record_decision(self, action: str, details: Dict):
        """Enregistre la décision pour l'historique et l'apprentissage."""
        record = {
            'action': action,
            'timestamp': len(self.decision_history),
            **details
        }
        self.decision_history.append(record)
        if len(self.decision_history) > 100:
            self.decision_history.pop(0)
    
    def _perceive_scarcity(self) -> bool:
        """Perception de rareté (biais cognitif de disponibilité)."""
        # Simule un biais de disponibilité : les biens rares sont perçus comme plus désirables
        return np.random.random() < 0.3
    
    def decide_spend_or_save(self, opportunities: List[Dict]) -> Tuple[str, Optional[Dict]]:
        """
        Fonction principale de décision.
        Retourne (action, details)
        actions: 'spend', 'save', 'invest_web3', 'pay_zakat'
        """
        # Mise à jour de l'état émotionnel
        self._update_emotional_state()
        
        best_utility = -np.inf
        best_decision = None
        
        for opp in opportunities:
            category = opp.get('category', ExpenseCategory.LEISURE)
            amount = opp['amount']
            payment_mode = opp.get('mode', self.preferred_payment)
            
            # 1. Composante neurocognitive
            pain = self.compute_pain_of_paying(amount, payment_mode)
            reward = self.compute_anticipated_reward(amount, category)
            control = self.compute_cognitive_control(pain, reward)
            
            # 2. Composante psychosociale
            social_pressure = self.compute_social_pressure(category)
            mental_penalty = self._compute_mental_account_penalty(amount, category)
            
            # 3. Composante émotionnelle (amygdale)
            emotional_valence = self._compute_emotional_valence(opp)
            
            # 4. Composante de confiance systémique
            trust_factor = self.system_trust if opp.get('requires_trust', False) else 1.0
            
            # 5. Intégration dans l'utilité nette
            # Le dlPFC module le conflit entre récompense et douleur
            net_utility = (reward * (1 + emotional_valence) - 
                          pain * (1 - control) * (1 + 0.5 * self.cognitive_load))
            
            # Application des biais psychologiques
            net_utility *= mental_penalty
            net_utility *= (1 + social_pressure * 0.5)
            
            # Biais de passion et confiance
            net_utility *= (0.5 + getattr(self.agent, 'passion', 0.5))
            net_utility *= trust_factor
            
            # 6. Enregistrement des signaux neuronaux
            self._record_neural_signals(pain, reward, control, emotional_valence)
            
            if net_utility > best_utility:
                best_utility = net_utility
                best_decision = opp
                best_decision['utility'] = net_utility
                best_decision['neural'] = {'pain': pain, 'reward': reward, 'control': control}
        
        # Seuil de décision : si utilité trop faible, épargne
        SAVE_THRESHOLD = 0.15
        if best_utility < SAVE_THRESHOLD:
            # Décision d'épargne
            save_amount = self.agent.wealth * 0.05 * (1 + self.self_control)
            self._record_decision('save', {'amount': save_amount})
            return ('save', {'amount': save_amount})
        else:
            # Décision de dépense
            self._record_decision('spend', best_decision)
            return ('spend', best_decision)
    
    def get_neural_profile(self) -> Dict:
        """Retourne le profil neuronal agrégé."""
        if not self.neural_history:
            return {'striatum': 0, 'insula': 0, 'dlpfc': 0, 'amygdala': 0}
        
        recent = self.neural_history[-10:]
        return {
            'striatum': np.mean([n.striatum for n in recent]),
            'insula': np.mean([n.insula for n in recent]),
            'dlpfc': np.mean([n.dlpfc for n in recent]),
            'amygdala': np.mean([n.amygdala for n in recent])
        }
    
    def get_decision_patterns(self) -> Dict:
        """Analyse les patterns de décision."""
        if not self.decision_history:
            return {}
        
        spend_decisions = [d for d in self.decision_history if d['action'] == 'spend']
        save_decisions = [d for d in self.decision_history if d['action'] == 'save']
        
        return {
            'spend_rate': len(spend_decisions) / len(self.decision_history) if self.decision_history else 0,
            'avg_spend_amount': np.mean([d['amount'] for d in spend_decisions]) if spend_decisions else 0,
            'avg_save_amount': np.mean([d['amount'] for d in save_decisions]) if save_decisions else 0,
            'preferred_categories': self._get_preferred_categories()
        }
    
    def _get_preferred_categories(self) -> Dict:
        """Catégories de dépense préférées."""
        spend_decisions = [d for d in self.decision_history if d['action'] == 'spend']
        if not spend_decisions:
            return {}
        
        categories = {}
        for d in spend_decisions:
            cat = d.get('category', ExpenseCategory.LEISURE)
            cat_name = cat.value if hasattr(cat, 'value') else str(cat)
            categories[cat_name] = categories.get(cat_name, 0) + 1
        
        total = sum(categories.values())
        return {k: v/total for k, v in categories.items()}


# ============================================================
# 3. AGENT DE BASE AVEC COGNITION
# ============================================================

class Agent:
    """
    Agent économique doté d'une cognition neuro-sociale.
    """
    
    def __init__(self, unique_id: int, model, personality: str = "balanced"):
        self.unique_id = unique_id
        self.model = model
        
        # Caractéristiques de base
        self.wealth = np.random.uniform(500, 2000)
        self.trust = np.random.uniform(0.3, 0.9)
        self.passion = np.random.uniform(0.2, 0.8)
        
        # Grade (primo inter pares)
        self.grade = Grade.APPRENTI
        
        # Couche cognitive
        self.cognition = HumanCognition(self, personality)
        
        # Réseau social (sera rempli par le modèle)
        self.social_connections = []
        
        # Adoption du Franc-Jy
        self.fulus_holdings = 0.0  # En Francs-Jy
        self.fulus_desire = np.random.uniform(0.0, 0.3)  # Désir pour la monnaie alternative
        
        # Compteur de parrainages de hisba (travail utile)
        self.hisba_hours = 0.0
        
        # Zakat payée
        self.zakat_paid = 0.0
        
        # État de la croyance monétaire
        self.belief_in_system = 0.5  # 0 = confiance dans le Franc-Jy, 1 = confiance dans la monnaie-dette
        
    def step(self):
        """
        Étape de l'agent (à appeler à chaque tick).
        """
        # 1. Générer des opportunités de dépense
        opportunities = self._generate_spending_opportunities()
        
        # 2. Prendre la décision épargne/dépense
        action, details = self.cognition.decide_spend_or_save(opportunities)
        
        # 3. Exécuter la décision
        if action == 'spend':
            self._execute_spending(details)
        elif action == 'save':
            self._execute_saving(details)
        elif action == 'invest_web3':
            self._execute_web3_investment(details)
        elif action == 'pay_zakat':
            self._execute_zakat_payment(details)
        
        # 4. Mettre à jour l'influence sociale
        if self.social_connections:
            self.cognition.update_social_influence(self.social_connections)
        
        # 5. Mettre à jour le désir pour le Franc-Jy (mimétique)
        self._update_fulus_desire()
        
        # 6. Gagner des heures de hisba (travail utile)
        if np.random.random() < 0.2:  # 20% de chance de travailler
            self.hisba_hours += np.random.uniform(0.5, 2.0)
    
    def _generate_spending_opportunities(self) -> List[Dict]:
        """
        Génère les opportunités de dépense du marché.
        """
        opportunities = []
        
        # Opportunité 1 : bien de loisir
        if np.random.random() < 0.7:
            opportunities.append({
                'amount': np.random.uniform(10, 100),
                'category': ExpenseCategory.LEISURE,
                'mode': np.random.choice(list(PaymentMode)),
                'requires_trust': False,
                'familiarity': np.random.uniform(0.3, 0.9)
            })
        
        # Opportunité 2 : nécessité
        if np.random.random() < 0.4:
            opportunities.append({
                'amount': np.random.uniform(20, 150),
                'category': ExpenseCategory.NECESSITY,
                'mode': PaymentMode.CARD,
                'requires_trust': False,
                'urgent': np.random.random() < 0.3
            })
        
        # Opportunité 3 : investissement Web3 (nécessite confiance)
        if self.model.web3_active and np.random.random() < 0.3:
            opportunities.append({
                'amount': np.random.uniform(50, 300),
                'category': ExpenseCategory.INVESTMENT,
                'mode': PaymentMode.CRYPTO,
                'requires_trust': True,
                'expected_return': np.random.uniform(0.05, 0.25),
                'trust': self.trust
            })
        
        # Opportunité 4 : Zakat (prélèvement obligatoire pour les Compagnons et plus)
        if self.grade != Grade.APPRENTI and np.random.random() < 0.1:
            opportunities.append({
                'amount': self.wealth * 0.025,  # 2.5% de Zakat
                'category': ExpenseCategory.ZAKAT,
                'mode': PaymentMode.CRYPTO,
                'requires_trust': True,
                'urgent': False,
                'trust': 0.8
            })
        
        return opportunities
    
    def _execute_spending(self, details: Dict):
        """Exécute une dépense."""
        amount = details['amount']
        if amount <= self.wealth:
            self.wealth -= amount
            # Impact sur l'économie locale
            self.model.total_consumption += amount
            
            # Si la dépense est en Franc-Jy, augmenter l'adoption
            if details.get('mode') == PaymentMode.CRYPTO:
                self.fulus_holdings += amount * 0.1  # Conversion partielle en FJ
    
    def _execute_saving(self, details: Dict):
        """Exécute une épargne."""
        amount = details['amount']
        self.wealth -= amount
        self.model.total_savings += amount
    
    def _execute_web3_investment(self, details: Dict):
        """Investit dans un mécanisme Web3."""
        amount = details['amount']
        if amount <= self.wealth:
            self.wealth -= amount
            # Ajouter au DAO
            if hasattr(self.model, 'dao'):
                self.model.dao.stake(self.unique_id, amount)
    
    def _execute_zakat_payment(self, details: Dict):
        """Exécute un paiement de Zakat."""
        amount = details['amount']
        if amount <= self.wealth:
            self.wealth -= amount
            self.zakat_paid += amount
            # La Zakat alimente les awqaf
            if hasattr(self.model, 'awqaf'):
                self.model.awqaf.add_funds(amount)
    
    def _update_fulus_desire(self):
        """
        Met à jour le désir pour le Franc-Jy selon l'équation maîtresse.
        """
        # Calcul de l'influence sociale moyenne
        if self.social_connections:
            mean_fulus_desire = np.mean([a.fulus_desire for a in self.social_connections])
        else:
            mean_fulus_desire = self.model.mean_fulus_desire
        
        # Calcul de la dette externe perçue
        perceived_debt = self.model.global_debt / 10000  # Normalisation
        
        # Effet de la confiance dans le système
        trust_effect = 1 - self.cognition.system_trust
        
        # Équation d'adoption
        # d⟨f⟩/dt = α * ⟨f⟩ * (1 - ⟨f⟩) * (⟨s⟩ - seuil) + β * (d_ext - d) + η * S_hisba
        alpha = 0.1 * self.cognition.social_conformity
        beta = 0.05 * self.cognition.system_trust
        eta = 0.02
        
        seuil = 0.4
        S_hisba = np.log(1 + self.hisba_hours) / 10  # Normalisation
        
        # Variation du désir
        delta_f = (alpha * self.fulus_desire * (1 - self.fulus_desire) * 
                   (mean_fulus_desire - seuil) +
                   beta * (perceived_debt - self.belief_in_system) +
                   eta * S_hisba)
        
        # Actualisation
        self.fulus_desire = np.clip(self.fulus_desire + delta_f * 0.1, 0.0, 1.0)
        
        # Mise à jour de la croyance
        self.belief_in_system = 1 - self.fulus_desire


# ============================================================
# 4. DAO ET GOUVERNANCE DÉCENTRALISÉE (WEB3)
# ============================================================

class DAOContract:
    """
    Simulation de mécanismes de gouvernance décentralisée (Web3).
    """
    
    def __init__(self):
        self.tokens: Dict[int, float] = {}  # Agent ID -> Tokens détenus
        self.proposals: List[Dict] = []
        self.stakes: Dict[int, float] = {}  # Agent ID -> Montant staké
        self.voting_power: Dict[int, float] = {}
        self.total_supply = 0
        self.governance_pool = 0
        
    def mint_tokens(self, agent_id: int, amount: float):
        """Émet des tokens pour un agent (seigneuriage)."""
        self.tokens[agent_id] = self.tokens.get(agent_id, 0) + amount
        self.total_supply += amount
        
    def stake(self, agent_id: int, amount: float):
        """Stake des tokens pour la gouvernance."""
        if self.tokens.get(agent_id, 0) >= amount:
            self.tokens[agent_id] -= amount
            self.stakes[agent_id] = self.stakes.get(agent_id, 0) + amount
            self.governance_pool += amount
            
    def get_voting_power(self, agent_id: int) -> float:
        """Retourne le pouvoir de vote d'un agent (proportionnel au stake)."""
        stake = self.stakes.get(agent_id, 0)
        if self.governance_pool > 0:
            return stake / self.governance_pool
        return 0
    
    def create_proposal(self, proposer_id: int, description: str, amount: float):
        """Crée une proposition de financement par la communauté."""
        proposal = {
            'id': len(self.proposals),
            'proposer': proposer_id,
            'description': description,
            'amount': amount,
            'votes_for': 0.0,
            'votes_against': 0.0,
            'status': 'pending',
            'quorum_reached': False
        }
        self.proposals.append(proposal)
        return proposal['id']
    
    def vote(self, proposal_id: int, agent_id: int, vote_for: bool):
        """Vote sur une proposition."""
        if proposal_id >= len(self.proposals):
            return False
        
        proposal = self.proposals[proposal_id]
        if proposal['status'] != 'pending':
            return False
        
        voting_power = self.get_voting_power(agent_id)
        if voting_power > 0:
            if vote_for:
                proposal['votes_for'] += voting_power
            else:
                proposal['votes_against'] += voting_power
        
        # Vérifier si le quorum est atteint
        total_votes = proposal['votes_for'] + proposal['votes_against']
        if total_votes > 0.3:  # Quorum de 30%
            proposal['quorum_reached'] = True
            if proposal['votes_for'] > proposal['votes_against']:
                proposal['status'] = 'approved'
                return True
            else:
                proposal['status'] = 'rejected'
        return False
    
    def process_votes(self):
        """Traite les votes en attente."""
        for proposal in self.proposals:
            if proposal['status'] == 'pending' and proposal['quorum_reached']:
                if proposal['votes_for'] > proposal['votes_against']:
                    proposal['status'] = 'approved'
                else:
                    proposal['status'] = 'rejected'


# ============================================================
# 5. AWQAF (BIENS DE MAINMORTE)
# ============================================================

class WaqfSystem:
    """
    Système de waqfs (biens de mainmorte) pour financer les biens communs.
    """
    
    def __init__(self):
        self.waqfs = {
            'media': {'funds': 0.0, 'description': 'Presse indépendante sans publicité'},
            'formation': {'funds': 0.0, 'description': 'Écoles de la blockchain et des métiers'},
            'resilience': {'funds': 0.0, 'description': 'Réserve bimétallique d\'urgence'},
            'mosquee': {'funds': 0.0, 'description': 'Entretien des mosquées'},
            'inter_guildes': {'funds': 0.0, 'description': 'Fonds de solidarité entre guildes'}
        }
        self.total_funds = 0
        
    def add_funds(self, amount: float, destination: str = 'inter_guildes'):
        """Ajoute des fonds à un waqf."""
        if destination in self.waqfs:
            self.waqfs[destination]['funds'] += amount
            self.total_funds += amount
            
    def allocate_funds(self, destination: str, amount: float) -> bool:
        """Alloue des fonds d'un waqf."""
        if destination in self.waqfs and self.waqfs[destination]['funds'] >= amount:
            self.waqfs[destination]['funds'] -= amount
            self.total_funds -= amount
            return True
        return False
    
    def get_balance(self, destination: str) -> float:
        """Retourne le solde d'un waqf."""
        return self.waqfs.get(destination, {}).get('funds', 0.0)
    
    def get_total_funds(self) -> float:
        return self.total_funds


# ============================================================
# 6. MODÈLE INTÉGRATEUR PRINCIPAL
# ============================================================

class EconomicModel:
    """
    Modèle intégrateur complet combinant :
    - Neurocognition individuelle
    - Psychologie sociale
    - Web3 (DAO)
    - Awqaf
    - Dynamique monétaire
    - Ricci flow sur réseaux sociaux
    """
    
    def __init__(self, n_agents: int = 50, n_guildes: int = 5):
        # Paramètres de base
        self.n_agents = n_agents
        self.n_guildes = n_guildes
        self.time_step = 0
        
        # Composants
        self.dao = DAOContract()
        self.awqaf = WaqfSystem()
        self.web3_active = True
        
        # Variables macro-économiques
        self.total_wealth = 0
        self.total_consumption = 0
        self.total_savings = 0
        self.monetary_velocity = 0
        self.global_debt = 1000  # Dette externe (normalisée)
        self.mean_fulus_desire = 0
        
        # Création des agents
        personalities = ['balanced', 'impulsive', 'frugal', 'social', 'ascetic']
        self.agents: List[Agent] = []
        for i in range(n_agents):
            personality = np.random.choice(personalities)
            agent = Agent(i, self, personality)
            self.agents.append(agent)
        
        # Attribution des grades
        self._assign_grades()
        
        # Création du réseau social
        self._build_social_network()
        
        # Création des guildes
        self._create_guildes()
        
        # Métriques de suivi
        self.history = {
            'mean_wealth': [],
            'mean_fulus_desire': [],
            'monetary_velocity': [],
            'total_consumption': [],
            'total_savings': [],
            'trust_mean': []
        }
        
        # État du système (bascule)
        self.system_state = 'debt_currency'  # 'debt_currency' ou 'fulus'
        
    def _assign_grades(self):
        """Attribue les grades initiaux (primo inter pares)."""
        # Trier par richesse pour simuler une hiérarchie initiale
        sorted_agents = sorted(self.agents, key=lambda a: a.wealth, reverse=True)
        
        # Les 10% les plus riches sont Maîtres exécutifs
        n_executifs = max(1, int(self.n_agents * 0.1))
        for i in range(n_executifs):
            if i < len(sorted_agents):
                sorted_agents[i].grade = Grade.MAITRE_EXECUTIF
        
        # Les 20% suivants sont Maîtres officiers
        n_officiers = max(2, int(self.n_agents * 0.2))
        for i in range(n_executifs, min(n_executifs + n_officiers, len(sorted_agents))):
            sorted_agents[i].grade = Grade.MAITRE_OFFICIER
        
        # Les 30% suivants sont Compagnons
        n_compagnons = max(5, int(self.n_agents * 0.3))
        for i in range(n_executifs + n_officiers, 
                       min(n_executifs + n_officiers + n_compagnons, len(sorted_agents))):
            sorted_agents[i].grade = Grade.COMPAGNON
        
        # Le reste Apprentis
        for i in range(n_executifs + n_officiers + n_compagnons, len(sorted_agents)):
            sorted_agents[i].grade = Grade.APPRENTI
        
        # Le Maître Sheykh est le plus riche (primo inter pares)
        if len(sorted_agents) > 0:
            sorted_agents[0].grade = Grade.MAITRE_SHEYKH
    
    def _build_social_network(self):
        """Construit un réseau social pour la contagion (small-world)."""
        G = nx.watts_strogatz_graph(self.n_agents, 4, 0.1, seed=42)
        
        for i, agent in enumerate(self.agents):
            neighbors_idx = list(G.neighbors(i))
            agent.social_connections = [self.agents[j] for j in neighbors_idx]
            
            # Ajuster la confiance selon la proximité dans le réseau
            for neighbor in agent.social_connections:
                # La confiance est plus élevée entre agents proches
                trust_value = np.random.uniform(0.3, 0.9)
                agent.trust = (agent.trust + trust_value) / 2
        
        # Enregistrer le réseau pour visualisation
        self.social_graph = G
    
    def _create_guildes(self):
        """Crée des guildes (groupes d'agents partageant des intérêts)."""
        self.guildes = {}
        guild_names = [
            'Marchands et Artisans',
            'Codeurs et Développeurs',
            'Agriculteurs et Producteurs',
            'Enseignants et Érudits',
            'Guilde de la Monnaie'
        ]
        
        # Assigner chaque agent à une guilde
        for i, agent in enumerate(self.agents):
            guild_id = i % self.n_guildes
            guild_name = guild_names[guild_id % len(guild_names)]
            if guild_name not in self.guildes:
                self.guildes[guild_name] = []
            self.guildes[guild_name].append(agent)
            agent.guild = guild_name
    
    def _apply_ricci_flow(self, dt: float = 0.01):
        """
        Applique le Ricci flow sur le réseau de confiance.
        Lisse les courbures négatives (méfiance, entropie).
        """
        G = self.social_graph
        
        # Calcul de la courbure sur chaque arête
        for u, v in G.edges():
            # Courbure simplifiée : différence de confiance
            agent_u = self.agents[u]
            agent_v = self.agents[v]
            
            # La confiance mutuelle détermine la courbure
            trust_u_v = agent_u.cognition.system_trust
            trust_v_u = agent_v.cognition.system_trust
            
            # Courbure = divergence de confiance
            curvature = trust_u_v - trust_v_u
            
            # Lissage : réduire la divergence
            if curvature > 0:
                # Réduire l'écart
                agent_u.cognition.system_trust -= curvature * dt * 0.1
                agent_v.cognition.system_trust += curvature * dt * 0.1
            
            # Augmentation de la confiance mutuelle (lien positif)
            if np.random.random() < 0.01 * dt:
                # Renforcement des liens de confiance
                agent_u.trust = min(1.0, agent_u.trust + 0.01)
                agent_v.trust = min(1.0, agent_v.trust + 0.01)
        
        # Mise à jour de la confiance système moyenne
        trust_mean = np.mean([a.cognition.system_trust for a in self.agents])
        self.history['trust_mean'].append(trust_mean)
        
        return trust_mean
    
    def _compute_monetary_velocity(self) -> float:
        """
        Calcule la vélocité monétaire.
        Vélocité_rond-point > Vélocité_feu selon la métaphore.
        """
        # Dans le système actuel (feu de circulation), la vélocité est limitée
        if self.system_state == 'debt_currency':
            base_velocity = self.total_consumption / (self.total_wealth + 1)
            penalty = 0.3  # Pénalité due à l'intermédiation
            trust_factor = np.mean([a.trust for a in self.agents])
            velocity = base_velocity * (1 - penalty) * (0.5 + 0.5 * trust_factor)
        else:
            # Dans le système rond-point, la vélocité est maximisée
            base_velocity = self.total_consumption / (self.total_wealth + 1)
            trust_effect = 1 + np.mean([a.trust for a in self.agents])
            desire_alignment = 1 + self.mean_fulus_desire
            velocity = base_velocity * trust_effect * desire_alignment
        
        self.monetary_velocity = velocity
        return velocity
    
    def _update_macro_economics(self):
        """Met à jour les variables macroéconomiques."""
        self.total_wealth = sum(a.wealth for a in self.agents)
        self.mean_fulus_desire = np.mean([a.fulus_desire for a in self.agents])
        
        # Mise à jour de la dette externe (décroissance lente)
        self.global_debt = max(0, self.global_debt * (1 - 0.001 * self.time_step))
        
        # Détection du basculement
        if self.mean_fulus_desire > 0.6:
            self.system_state = 'fulus'
    
    def _update_awqaf_from_zakat(self):
        """Alimente les awqaf à partir de la Zakat payée."""
        total_zakat = sum(a.zakat_paid for a in self.agents)
        if total_zakat > 0:
            # Répartition de la Zakat
            self.awqaf.add_funds(total_zakat * 0.3, 'media')
            self.awqaf.add_funds(total_zakat * 0.25, 'formation')
            self.awqaf.add_funds(total_zakat * 0.25, 'resilience')
            self.awqaf.add_funds(total_zakat * 0.1, 'mosquee')
            self.awqaf.add_funds(total_zakat * 0.1, 'inter_guildes')
    
    def step(self):
        """Avance d'une étape temporelle."""
        self.time_step += 1
        
        # 1. Tous les agents prennent leurs décisions
        for agent in self.agents:
            agent.step()
        
        # 2. Mise à jour des dynamiques collectives
        self._update_macro_economics()
        self._update_awqaf_from_zakat()
        
        # 3. Application du Ricci flow (tous les 10 pas)
        if self.time_step % 10 == 0:
            self._apply_ricci_flow()
        
        # 4. Calcul de la vélocité monétaire
        velocity = self._compute_monetary_velocity()
        
        # 5. Traitement des votes DAO (tous les 20 pas)
        if self.time_step % 20 == 0 and self.web3_active:
            self.dao.process_votes()
        
        # 6. Seigneuriage : distribution des tokens (tous les 30 pas)
        if self.time_step % 30 == 0:
            # Le seigneuriage alimente les awqaf
            seigneuriage = self.total_consumption * 0.02
            self.awqaf.add_funds(seigneuriage, 'inter_guildes')
        
        # 7. Enregistrement des métriques
        self.history['mean_wealth'].append(np.mean([a.wealth for a in self.agents]))
        self.history['mean_fulus_desire'].append(self.mean_fulus_desire)
        self.history['monetary_velocity'].append(self.monetary_velocity)
        self.history['total_consumption'].append(self.total_consumption)
        self.history['total_savings'].append(self.total_savings)
    
    def get_state(self) -> Dict:
        """Retourne l'état actuel du modèle."""
        return {
            'time': self.time_step,
            'system_state': self.system_state,
            'mean_wealth': np.mean([a.wealth for a in self.agents]),
            'mean_fulus_desire': self.mean_fulus_desire,
            'monetary_velocity': self.monetary_velocity,
            'total_consumption': self.total_consumption,
            'total_savings': self.total_savings,
            'global_debt': self.global_debt,
            'awqaf_total': self.awqaf.get_total_funds(),
            'grades_distribution': {
                grade.value: sum(1 for a in self.agents if a.grade == grade)
                for grade in Grade
            }
        }
    
    def get_agent_stats(self) -> Dict:
        """Retourne les statistiques par agent."""
        return {
            'wealth_distribution': [a.wealth for a in self.agents],
            'fulus_desire_distribution': [a.fulus_desire for a in self.agents],
            'trust_distribution': [a.cognition.system_trust for a in self.agents],
            'hisba_hours': [a.hisba_hours for a in self.agents],
            'zakat_paid': [a.zakat_paid for a in self.agents]
        }


# ============================================================
# 7. VISUALISATION ET ANALYSE
# ============================================================

def visualize_model(model: EconomicModel, save_path: str = None):
    """
    Visualise l'évolution du modèle.
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # 1. Évolution de la richesse moyenne
    axes[0, 0].plot(model.history['mean_wealth'])
    axes[0, 0].set_title('Richesse Moyenne')
    axes[0, 0].set_xlabel('Temps')
    axes[0, 0].set_ylabel('Richesse (unités)')
    
    # 2. Désir moyen pour le Franc-Jy
    axes[0, 1].plot(model.history['mean_fulus_desire'])
    axes[0, 1].axhline(y=0.6, color='r', linestyle='--', label='Seuil de bascule (60%)')
    axes[0, 1].set_title('Désir Moyen pour le Franc-Jy')
    axes[0, 1].set_xlabel('Temps')
    axes[0, 1].set_ylabel('Désir (0-1)')
    axes[0, 1].legend()
    
    # 3. Vélocité monétaire
    axes[0, 2].plot(model.history['monetary_velocity'])
    axes[0, 2].set_title('Vélocité Monétaire')
    axes[0, 2].set_xlabel('Temps')
    axes[0, 2].set_ylabel('Vélocité')
    
    # 4. Consommation vs Épargne
    axes[1, 0].plot(model.history['total_consumption'], label='Consommation')
    axes[1, 0].plot(model.history['total_savings'], label='Épargne')
    axes[1, 0].set_title('Consommation vs Épargne')
    axes[1, 0].set_xlabel('Temps')
    axes[1, 0].set_ylabel('Montant')
    axes[1, 0].legend()
    
    # 5. Distribution des désirs (dernière étape)
    desires = model.get_agent_stats()['fulus_desire_distribution']
    axes[1, 1].hist(desires, bins=20, alpha=0.7)
    axes[1, 1].axvline(x=0.6, color='r', linestyle='--', label='Seuil de bascule')
    axes[1, 1].set_title('Distribution du Désir pour le Franc-Jy')
    axes[1, 1].set_xlabel('Désir (0-1)')
    axes[1, 1].set_ylabel('Nombre d\'agents')
    axes[1, 1].legend()
    
    # 6. État du système
    state_colors = {'debt_currency': 'red', 'fulus': 'green'}
    axes[1, 2].text(0.5, 0.5, f"État du système : {model.system_state}", 
                   ha='center', va='center', fontsize=20,
                   color=state_colors.get(model.system_state, 'black'))
    axes[1, 2].set_title('État du Système Monétaire')
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.show()


def run_simulation(n_agents: int = 100, n_steps: int = 500, visualize: bool = True):
    """
    Exécute une simulation complète.
    """
    print(f"Initialisation du modèle avec {n_agents} agents...")
    model = EconomicModel(n_agents=n_agents)
    
    print(f"Simulation de {n_steps} pas de temps...")
    for step in range(n_steps):
        model.step()
        
        # Affichage périodique
        if step % 100 == 0:
            state = model.get_state()
            print(f"Step {step}: Désir FJ = {state['mean_fulus_desire']:.3f}, "
                  f"État = {state['system_state']}, "
                  f"Vélocité = {state['monetary_velocity']:.3f}")
    
    print("Simulation terminée.")
    
    if visualize:
        visualize_model(model)
    
    return model


# ============================================================
# 8. EXEMPLE D'EXÉCUTION
# ============================================================

if __name__ == "__main__":
    # Simulation de base
    model = run_simulation(n_agents=100, n_steps=500, visualize=True)
    
    # Affichage des statistiques finales
    print("\n" + "="*50)
    print("STATISTIQUES FINALES")
    print("="*50)
    state = model.get_state()
    stats = model.get_agent_stats()
    
    print(f"État du système : {state['system_state']}")
    print(f"Désir moyen pour le Franc-Jy : {state['mean_fulus_desire']:.3f}")
    print(f"Vélocité monétaire : {state['monetary_velocity']:.3f}")
    print(f"Richesse moyenne : {state['mean_wealth']:.2f}")
    print(f"Consommation totale : {state['total_consumption']:.2f}")
    print(f"Total des awqaf : {state['awqaf_total']:.2f}")
    print(f"Agents ayant adopté le Franc-Jy : {sum(1 for d in stats['fulus_desire_distribution'] if d > 0.6)}")
    print(f"Heures de hisba totales : {sum(stats['hisba_hours']):.1f}")
    print(f"Zakat totale payée : {sum(stats['zakat_paid']):.2f}")
