"""
MODÈLE UNIFIÉ - FRANC CRYPTO / EURO CBDC
Auteur : Marc Daghar
Licence : CC BY-SA 4.0
Date : 21 avril 2026
Serveur : Sous souveraineté et indépendance chinoise
"""

import numpy as np
import networkx as nx
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ==================================================
# 1. ÉNUMÉRATIONS ET STRUCTURES DE BASE
# ==================================================

class PaymentMode(Enum):
    CASH = "cash"
    CARD = "card"
    CRYPTO = "crypto"
    MOBILE = "mobile"

class ExpenseCategory(Enum):
    NECESSITY = "necessites"
    LEISURE = "loisirs"
    INVESTMENT = "investissement"
    SOCIAL = "social"
    PRODUCTIVE = "productif"

@dataclass
class NeuralSignals:
    """Simulation des activations cérébrales"""
    striatum: float = 0.0  # Anticipation de récompense
    insula: float = 0.0    # Douleur de payer
    dlpfc: float = 0.0     # Contrôle cognitif
    amygdala: float = 0.0  # Réponse émotionnelle

@dataclass
class MentalAccounts:
    """Comptabilité mentale (Thaler, 1985)"""
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
            ExpenseCategory.PRODUCTIVE: self.savings
        }
        return mapping.get(category, 0.20)

# ==================================================
# 2. CLASSE DE COGNITION HUMAINE
# ==================================================

class HumanCognition:
    """Modélisation des processus neurocognitifs et psychosociaux"""
    
    def __init__(self, agent, personality_profile: str = "balanced"):
        self.agent = agent
        self._init_neural_parameters(personality_profile)
        
        # Comptabilité mentale
        self.mental_accounts = MentalAccounts()
        
        # État dynamique
        self.current_mood: float = 0.5
        self.cognitive_load: float = 0.0
        self.social_pressure: Dict[str, float] = defaultdict(float)
        
        # Historique
        self.decision_history: List[Dict] = []
        self.neural_history: List[NeuralSignals] = []
        
        # Mode de paiement préféré (influencé socialement)
        self.preferred_payment = PaymentMode.CARD
        
        # Réseau social
        self.social_network = []
        
        # Variables d'adaptation
        self.pain_desensitization = 0.0  # Désensibilisation à la douleur
    
    def _init_neural_parameters(self, profile: str):
        """Initialise les paramètres selon un profil psychologique"""
        profiles = {
            "balanced": {'pain_sensitivity': 0.7, 'reward_sensitivity': 0.7, 'self_control': 0.7, 'emotional_reactivity': 0.5},
            "impulsive": {'pain_sensitivity': 0.4, 'reward_sensitivity': 1.2, 'self_control': 0.3, 'emotional_reactivity': 0.8},
            "frugal": {'pain_sensitivity': 1.1, 'reward_sensitivity': 0.5, 'self_control': 0.9, 'emotional_reactivity': 0.4},
            "social": {'pain_sensitivity': 0.6, 'reward_sensitivity': 0.9, 'self_control': 0.5, 'emotional_reactivity': 0.9}
        }
        params = profiles.get(profile, profiles["balanced"])
        self.pain_sensitivity = params['pain_sensitivity']
        self.reward_sensitivity = params['reward_sensitivity']
        self.self_control = params['self_control']
        self.emotional_reactivity = params['emotional_reactivity']
    
    def compute_pain_of_paying(self, amount: float, payment_mode: PaymentMode) -> float:
        """
        Calcule la douleur de payer (activation insulaire)
        Basé sur Mazar et al. (2017)
        """
        # Base : proportion de la richesse
        base_pain = amount / (self.agent.wealth + 1000)
        
        # Facteur d'abstraction du paiement
        abstraction_factors = {
            PaymentMode.CASH: 1.0,
            PaymentMode.CARD: 0.55,
            PaymentMode.MOBILE: 0.45,
            PaymentMode.CRYPTO: 0.35
        }
        
        # Modulation par sensibilité, charge cognitive et désensibilisation
        pain = (base_pain * abstraction_factors[payment_mode] * 
                self.pain_sensitivity * (1 + 0.5 * self.cognitive_load) * 
                (1 - self.pain_desensitization))
        
        # Désensibilisation par usage répété des cryptos
        recent_crypto = sum(1 for d in self.decision_history[-20:] 
                           if d.get('action') == 'spend' and d.get('mode') == PaymentMode.CRYPTO)
        if recent_crypto > 10:
            self.pain_desensitization = min(0.5, self.pain_desensitization + 0.01)
        
        return np.clip(pain, 0.0, 1.0)
    
    def compute_anticipated_reward(self, amount: float, category: ExpenseCategory) -> float:
        """
        Calcule la récompense anticipée (activation striatale)
        Basé sur Knutson et al. (2007)
        """
        category_multipliers = {
            ExpenseCategory.LEISURE: 1.3,
            ExpenseCategory.SOCIAL: 1.2,
            ExpenseCategory.NECESSITY: 0.7,
            ExpenseCategory.INVESTMENT: 0.5,
            ExpenseCategory.PRODUCTIVE: 0.8
        }
        
        base_reward = amount * category_multipliers.get(category, 1.0)
        mood_mod = 0.8 + 0.4 * self.current_mood
        
        reward = base_reward * self.reward_sensitivity * mood_mod
        
        return np.clip(reward, 0.0, amount * 1.5)
    
    def compute_cognitive_control(self, pain: float, reward: float) -> float:
        """Simule le contrôle cognitif (dlPFC)"""
        conflict = abs(reward - pain)
        effective_control = self.self_control * (1 - 0.5 * self.cognitive_load)
        control_success = conflict * effective_control
        return np.clip(control_success, 0.0, 1.0)
    
    def _compute_mental_account_penalty(self, amount: float, category: ExpenseCategory) -> float:
        """Pénalité si la dépense dépasse le compte mental alloué"""
        target_allocation = self.mental_accounts.get_allocation(category)
        current_spending = sum(d['amount'] for d in self.decision_history[-30:] 
                              if d.get('category') == category)
        estimated_income = self.agent.wealth * 0.1
        allocated = target_allocation * estimated_income
        balance = max(0, allocated - current_spending)
        
        if amount <= balance:
            return 1.0
        else:
            overshoot = (amount - balance) / (balance + 1)
            return max(0.3, 1.0 - overshoot)
    
    def update_social_influence(self, neighbors: List):
        """Met à jour les paramètres cognitifs par influence sociale"""
        if not neighbors:
            return
        
        # Influence sur le mode de paiement préféré
        neighbor_payments = [n.cognition.preferred_payment for n in neighbors 
                           if hasattr(n, 'cognition')]
        if neighbor_payments:
            dominant = max(set(neighbor_payments), key=neighbor_payments.count)
            influence_strength = 0.05 * len(neighbors) / 10
            if np.random.random() < influence_strength:
                self.preferred_payment = dominant
        
        # Influence sur les sensibilités
        pain_sensitivities = [n.cognition.pain_sensitivity for n in neighbors 
                            if hasattr(n, 'cognition')]
        if pain_sensitivities:
            self.pain_sensitivity = 0.95 * self.pain_sensitivity + 0.05 * np.mean(pain_sensitivities)
        
        reward_sensitivities = [n.cognition.reward_sensitivity for n in neighbors 
                              if hasattr(n, 'cognition')]
        if reward_sensitivities:
            self.reward_sensitivity = 0.95 * self.reward_sensitivity + 0.05 * np.mean(reward_sensitivities)
    
    def decide_spend_or_save(self, opportunities: List[Dict]) -> Tuple[str, Optional[Dict]]:
        """Fonction principale de décision épargne/dépense"""
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
            social_pressure = self._compute_social_pressure(category)
            mental_penalty = self._compute_mental_account_penalty(amount, category)
            
            # 3. Composante émotionnelle (amygdale)
            emotional_valence = self._compute_emotional_valence(opp)
            
            # 4. Utilité nette
            net_utility = (reward * (1 + emotional_valence) - 
                          pain * (1 - control) * (1 + 0.5 * self.cognitive_load))
            
            net_utility *= mental_penalty
            net_utility *= (1 + social_pressure * 0.5)
            net_utility *= (0.5 + getattr(self.agent, 'passion', 0.5))
            
            if opp.get('requires_trust', False):
                net_utility *= (0.5 + getattr(self.agent, 'trust', 0.5))
            
            # 5. Enregistrement des signaux
            self._record_neural_signals(pain, reward, control, emotional_valence)
            
            if net_utility > best_utility:
                best_utility = net_utility
                best_decision = opp
                best_decision['utility'] = net_utility
        
        # Seuil de décision
        SAVE_THRESHOLD = 0.15
        if best_utility < SAVE_THRESHOLD:
            save_amount = self.agent.wealth * 0.05 * (1 + self.self_control)
            self._record_decision('save', {'amount': save_amount})
            return ('save', {'amount': save_amount})
        else:
            self._record_decision('spend', best_decision)
            return ('spend', best_decision)
    
    def _update_emotional_state(self):
        """Met à jour l'humeur et la charge cognitive"""
        recent_decisions = self.decision_history[-5:] if self.decision_history else []
        if recent_decisions:
            success_rate = sum(1 for d in recent_decisions if d.get('satisfaction', 0.5) > 0.6) / len(recent_decisions)
            self.current_mood = 0.5 + 0.3 * (success_rate - 0.5)
        else:
            self.current_mood = 0.5 + 0.1 * np.random.randn()
        
        self.cognitive_load = min(1.0, self.cognitive_load * 0.9 + 0.05 * np.random.rand())
    
    def _compute_emotional_valence(self, opportunity: Dict) -> float:
        """Réponse émotionnelle (amygdale)"""
        valence = 0.0
        if 'trust' in opportunity:
            valence += opportunity['trust'] * 0.5
        if 'familiarity' in opportunity:
            valence += opportunity['familiarity'] * 0.3
        if opportunity.get('urgent', False):
            valence += 0.4
        return np.clip(valence * self.emotional_reactivity, -0.5, 0.5)
    
    def _compute_social_pressure(self, category: ExpenseCategory) -> float:
        """Calcule la pression sociale à dépenser"""
        base_pressure = self.social_pressure.get(category.value, 0.0)
        if hasattr(self.agent, 'social_connections'):
            n_connections = len(self.agent.social_connections)
            pressure = base_pressure * (1 + 0.1 * n_connections)
        else:
            pressure = base_pressure
        return np.clip(pressure, 0.0, 1.0)
    
    def _record_neural_signals(self, pain: float, reward: float, control: float, emotion: float):
        """Enregistre les signaux neuronaux"""
        signals = NeuralSignals(
            striatum=reward,
            insula=pain,
            dlpfc=control,
            amygdala=emotion
        )
        self.neural_history.append(signals)
        if len(self.neural_history) > 100:
            self.neural_history.pop(0)
    
    def _record_decision(self, action: str, details: Dict):
        """Enregistre la décision dans l'historique"""
        record = {
            'action': action,
            'timestamp': len(self.decision_history),
            **details
        }
        self.decision_history.append(record)
        if len(self.decision_history) > 100:
            self.decision_history.pop(0)
    
    def get_neural_profile(self) -> Dict:
        """Retourne le profil neuronal agrégé"""
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
        """Analyse les patterns de décision"""
        if not self.decision_history:
            return {}
        
        spend_decisions = [d for d in self.decision_history if d['action'] == 'spend']
        save_decisions = [d for d in self.decision_history if d['action'] == 'save']
        
        return {
            'spend_rate': len(spend_decisions) / len(self.decision_history),
            'avg_spend_amount': np.mean([d['amount'] for d in spend_decisions]) if spend_decisions else 0,
            'avg_save_amount': np.mean([d['amount'] for d in save_decisions]) if save_decisions else 0,
            'preferred_categories': self._get_preferred_categories()
        }
    
    def _get_preferred_categories(self) -> Dict:
        """Catégories de dépense préférées"""
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

# ==================================================
# 3. AGENT HUMAIN AVEC COGNITION
# ==================================================

class HumanAgent:
    """Agent humain doté de cognition et de capacités d'échange"""
    
    def __init__(self, unique_id: int, model, personality: str = "balanced"):
        self.unique_id = unique_id
        self.model = model
        self.wealth = np.random.uniform(500, 1500)
        self.trust = np.random.uniform(0.3, 0.9)
        self.passion = np.random.uniform(0.2, 0.8)
        
        # Couche cognitive
        self.cognition = HumanCognition(self, personality)
        
        # Réseau social
        self.social_connections = []
        
        # Positions (pour visualisation)
        self.x = np.random.random()
        self.y = np.random.random()
    
    def step(self):
        """Étape de l'agent à chaque tick"""
        # 1. Générer des opportunités de dépense
        opportunities = self._generate_spending_opportunities()
        
        # 2. Décision épargne/dépense
        action, details = self.cognition.decide_spend_or_save(opportunities)
        
        # 3. Exécution
        if action == 'spend':
            self._execute_spending(details)
        elif action == 'save':
            self._execute_saving(details)
        
        # 4. Mise à jour sociale
        if self.social_connections:
            self.cognition.update_social_influence(self.social_connections)
        
        # 5. Contagion mimétique du désir
        self._update_mimetic_desire()
    
    def _generate_spending_opportunities(self) -> List[Dict]:
        """Génère les opportunités de dépense du marché"""
        opportunities = []
        
        # Opportunité 1 : Bien de loisir
        if np.random.random() < 0.7:
            opportunities.append({
                'amount': np.random.uniform(10, 100),
                'category': ExpenseCategory.LEISURE,
                'mode': np.random.choice(list(PaymentMode)),
                'requires_trust': False,
                'familiarity': np.random.uniform(0.3, 0.9)
            })
        
        # Opportunité 2 : Nécessité
        if np.random.random() < 0.4:
            opportunities.append({
                'amount': np.random.uniform(20, 150),
                'category': ExpenseCategory.NECESSITY,
                'mode': PaymentMode.CARD,
                'requires_trust': False,
                'urgent': np.random.random() < 0.3
            })
        
        # Opportunité 3 : Investissement productif
        if self.model.franc_active and np.random.random() < 0.3:
            opportunities.append({
                'amount': np.random.uniform(50, 300),
                'category': ExpenseCategory.PRODUCTIVE,
                'mode': PaymentMode.CRYPTO,
                'requires_trust': True,
                'expected_return': np.random.uniform(0.05, 0.25)
            })
        
        return opportunities
    
    def _execute_spending(self, details: Dict):
        """Exécute une dépense"""
        amount = details['amount']
        if amount <= self.wealth:
            self.wealth -= amount
            # Effet sur la masse monétaire totale
            self.model.money_supply -= amount * 0.1
    
    def _execute_saving(self, details: Dict):
        """Exécute une épargne"""
        amount = details['amount']
        self.wealth -= amount
        # L'épargne reste dans le système
        self.model.total_savings += amount
    
    def _update_mimetic_desire(self):
        """Met à jour le désir mimétique (contagion)"""
        if not self.social_connections:
            return
        
        # Désir moyen des voisins pour le Franc
        neighbor_desire = np.mean([a.cognition._get_franc_desire() 
                                  for a in self.social_connections 
                                  if hasattr(a, 'cognition')])
        
        # Diffusion mimétique (équation du texte)
        alpha = 0.3  # Intensité mimétique
        self.cognition._franc_desire = (alpha * neighbor_desire + 
                                       (1 - alpha) * self.cognition._get_franc_desire())
    
    def _get_franc_desire(self) -> float:
        """Retourne le désir pour le Franc crypto"""
        if not hasattr(self.cognition, '_franc_desire'):
            self.cognition._franc_desire = np.random.uniform(0, 0.5)
        return self.cognition._franc_desire

# ==================================================
# 4. SYSTÈME MONÉTAIRE ET MODÈLE ÉCONOMIQUE
# ==================================================

class MonetarySystem:
    """Système monétaire avec Euro CBDC et Franc crypto"""
    
    def __init__(self):
        # Masse monétaire
        self.M_euro = 10000.0
        self.M_franc = 0.0
        
        # Réserves bimétalliques
        self.gold_reserve = 0.0  # en grammes
        self.silver_reserve = 0.0  # en grammes
        
        # Paramètres
        self.interest_rate = 0.03  # Taux directeur
        self.reserve_ratio = 0.1   # Coefficient de réserve
        self.trust_coefficient = 0.5  # Confiance distribuée
        
        # Variables économiques
        self.gdp = 10000
        self.total_transactions = 0
        self.total_savings = 0
        
        # Historique
        self.history = {
            'M_euro': [],
            'M_franc': [],
            'velocity_euro': [],
            'velocity_franc': [],
            'substitution_rate': [],
            'resilience_index': []
        }
    
    def issue_franc(self, gold_grams: float, silver_grams: float) -> float:
        """
        Émission de Franc crypto contre dépôt d'or/argent
        1 Dinar (or) = 4.25g = 100 Francs
        1 Dirham (argent) = 2.975g = 10 Francs
        """
        value_from_gold = (gold_grams / 4.25) * 100
        value_from_silver = (silver_grams / 2.975) * 10
        
        new_franc = value_from_gold + value_from_silver
        self.gold_reserve += gold_grams
        self.silver_reserve += silver_grams
        self.M_franc += new_franc
        
        return new_franc
    
    def compute_velocity_euro(self, P: float = 1.0, T: float = 1.0) -> float:
        """
        Vélocité de l'Euro CBDC - Modèle "feu de circulation"
        V = (P*T)/M * (1-r) * (1-ρ)
        """
        if self.M_euro == 0:
            return 0
        velocity = (P * T / self.M_euro) * (1 - self.interest_rate) * (1 - self.reserve_ratio)
        return max(0.1, velocity)
    
    def compute_velocity_franc(self, P: float = 1.0, T: float = 1.0, stress: float = 0.1) -> float:
        """
        Vélocité du Franc crypto - Modèle "rond-point"
        V = (P*T)/M * (1+τ) * (1+θ) * (1-β*σ)
        """
        if self.M_franc == 0:
            return 0
        
        tau = self.trust_coefficient
        theta = 0.3  # Alignement des désirs (conatus)
        beta = 0.5   # Sensibilité au stress
        
        velocity = (P * T / self.M_franc) * (1 + tau) * (1 + theta) * (1 - beta * stress)
        return max(0.1, velocity)
    
    def compute_complementarity_indicators(self) -> Dict:
        """Calcule les indicateurs de complémentarité Euro/Franc"""
        total_money = self.M_euro + self.M_franc
        
        # 1. Taux de substitution
        substitution_rate = self.M_franc / total_money if total_money > 0 else 0
        
        # 2. Vélocité comparée
        P, T = 1.0, 1.0
        stress = 0.1  # À calculer à partir des agents
        v_euro = self.compute_velocity_euro(P, T)
        v_franc = self.compute_velocity_franc(P, T, stress)
        velocity_ratio = v_franc / v_euro if v_euro > 0 else 0
        
        # 3. Indice de résilience
        euro_volatility = self.interest_rate * 0.2
        franc_volatility = 0.05 * (1 - self.trust_coefficient)
        resilience_index = 1 - (franc_volatility / euro_volatility) if euro_volatility > 0 else 0
        
        return {
            'substitution_rate': substitution_rate,
            'velocity_ratio': velocity_ratio,
            'resilience_index': resilience_index,
            'M_euro': self.M_euro,
            'M_franc': self.M_franc,
            'velocity_euro': v_euro,
            'velocity_franc': v_franc
        }
    
    def convert_franc_to_euro(self, amount: float) -> float:
        """Conversion Franc → Euro (nécessaire pour la fiscalité)"""
        if amount > self.M_franc:
            return 0
        
        # Taux de conversion basé sur la réserve bimétallique
        gold_price = 80.0  # EUR/gramme (exemple)
        silver_price = 1.0  # EUR/gramme
        
        backing_per_franc = ((self.gold_reserve * gold_price) + 
                            (self.silver_reserve * silver_price)) / self.M_franc if self.M_franc > 0 else 0
        
        conversion_rate = backing_per_franc
        
        # Limitation : pas plus de 30% de substitution
        max_conversion = self.M_franc * 0.3
        amount = min(amount, max_conversion)
        
        euros = amount * conversion_rate
        self.M_franc -= amount
        self.M_euro += euros
        
        return euros
    
    def apply_zakat(self, wealth: float) -> float:
        """Calcul de la Zakat (2.5% sur la richesse)"""
        nisab = 85  # 85g d'or (seuil d'imposition)
        if wealth > nisab:
            return 0.025 * wealth
        return 0.0
    
    def record_state(self):
        """Enregistre l'état pour l'historique"""
        indicators = self.compute_complementarity_indicators()
        self.history['M_euro'].append(self.M_euro)
        self.history['M_franc'].append(self.M_franc)
        self.history['velocity_euro'].append(indicators['velocity_euro'])
        self.history['velocity_franc'].append(indicators['velocity_franc'])
        self.history['substitution_rate'].append(indicators['substitution_rate'])
        self.history['resilience_index'].append(indicators['resilience_index'])

# ==================================================
# 5. MODÈLE INTÉGRATEUR FINAL
# ==================================================

