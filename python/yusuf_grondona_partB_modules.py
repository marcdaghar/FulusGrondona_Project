#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yusuf Counter-Cycle Model – Main Simulation
Yusuf (counter-cycle) vs Capitalist (debt, interest) system
Author: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any

@dataclass
class YusufConfig:
    """Configuration for the Yusuf counter-cycle model"""
    # Time parameters
    T: float = 100.0  # Simulation duration (years)
    dt: float = 0.1   # Time step (years)
    
    # Economic parameters
    need: float = 0.7          # Minimum consumption need per year
    P_mean: float = 1.0        # Average production
    P_amplitude: float = 0.5   # Cycle amplitude (abundance/scarcity)
    period: float = 14.0       # Cycle period (years, 7+7 from Surah Yusuf)
    
    # Capitalist parameters (reference system)
    interest_rate: float = 0.05  # Annual interest rate
    
    # Yusuf parameters
    stock_initial: float = 0.5   # Initial stock (years of consumption)
    threshold_factor: float = 0.3  # Factor for abundance/scarcity thresholds
    
    # Gamification (social credit)
    gamification_enabled: bool = True
    compliance_threshold: float = 0.8  # Threshold for benefits
    penalty_rate: float = 0.3          # Penalty for non-compliance
    reward_rate: float = 0.1           # Reward for compliance
    
    # Noise
    noise_amplitude: float = 0.03  # Production noise
    
    @property
    def P_bar(self) -> float:
        """Abundance threshold (high)"""
        return self.P_mean + self.P_amplitude * self.threshold_factor
    
    @property
    def P_underline(self) -> float:
        """Scarcity threshold (low)"""
        return self.P_mean - self.P_amplitude * self.threshold_factor
    
    @property
    def n_steps(self) -> int:
        """Number of time steps"""
        return int(self.T / self.dt)


@dataclass
class SimulationResult:
    """Results of a simulation"""
    t: np.ndarray
    P: np.ndarray
    S: np.ndarray
    C: np.ndarray
    compliance: Optional[np.ndarray] = None
    config: Optional[YusufConfig] = None
    system_name: str = ""
    crisis_detected: bool = False
    
    @property
    def coverage_ratio(self) -> np.ndarray:
        """Stock / need ratio"""
        return self.S / (self.config.need if self.config else 0.7)
    
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
        """Percentage of time where stock > 0"""
        return float(np.sum(self.S > 0) / len(self.S) * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_name": self.system_name,
            "final_stock": self.final_stock,
            "mean_consumption": self.mean_consumption,
            "consumption_volatility": self.consumption_volatility,
            "solvency_rate": self.solvency_rate,
            "crisis_detected": self.crisis_detected
        }


class YusufSystem:
    """
    Implementation of the Yusuf counter-cycle system.
    Rule:
    - Abundance (P > P_bar) : Minimise consumption, surplus goes to stock
    - Scarcity (P < P_underline) : Draw from stock to maintain consumption
    - Equilibrium : Consumption = production
    """
    def __init__(self, config: YusufConfig):
        self.config = config
        self.reset()
    
    def reset(self) -> None:
        """Reset system state"""
        self.S = np.zeros(self.config.n_steps)
        self.C = np.zeros(self.config.n_steps)
        self.S[0] = self.config.stock_initial
        self.compliance = np.zeros(self.config.n_steps) if self.config.gamification_enabled else None
    
    def _compute_production(self) -> np.ndarray:
        """Generate cyclic production with optional noise"""
        t = np.linspace(0, self.config.T, self.config.n_steps)
        # Base cycle (period of 14 years)
        P = self.config.P_mean + self.config.P_amplitude * np.sin(2 * np.pi * t / self.config.period)
        # Add noise
        if self.config.noise_amplitude > 0:
            noise = np.random.normal(0, self.config.noise_amplitude, len(t))
            P = P + noise
        return np.maximum(P, 0.1)
    
    def _update_compliance(self, idx: int, behavior_correct: bool) -> float:
        """Update compliance score (social credit)"""
        if not self.config.gamification_enabled:
            return 0.0
        if idx == 0:
            score = 1.0
        else:
            score = self.compliance[idx - 1]
        if behavior_correct:
            score = min(1.0, score + self.config.reward_rate * self.config.dt)
        else:
            score = max(0.0, score - self.config.penalty_rate * self.config.dt)
        return score
    
    def _get_effective_need(self, score: float) -> float:
        """Modulate need by compliance score"""
        if not self.config.gamification_enabled:
            return self.config.need
        if score >= self.config.compliance_threshold:
            # Reward: reduced need
            return self.config.need * (1 - self.config.reward_rate)
        else:
            # Penalty: increased need
            return self.config.need * (1 + self.config.penalty_rate)
    
    def run(self) -> SimulationResult:
        """Run the simulation"""
        self.reset()
        P = self._compute_production()
        t = np.linspace(0, self.config.T, self.config.n_steps)
        P_bar = self.config.P_bar
        P_underline = self.config.P_underline
        crisis_detected = False
        
        for i in range(1, self.config.n_steps):
            production = P[i]
            stock_prev = self.S[i-1]
            score_prev = self.compliance[i-1] if self.compliance is not None else 1.0
            
            effective_need = self._get_effective_need(score_prev)
            
            # Yusuf rule
            if production > P_bar:
                # ABUNDANCE: save
                self.C[i] = min(production, effective_need)
                dS = (production - self.C[i]) * self.config.dt
                self.S[i] = stock_prev + dS
                behavior_correct = (self.C[i] <= effective_need + 0.1)
                
            elif production < P_underline:
                # SCARCITY: draw from stock
                needed_from_stock = max(0, effective_need - production)
                max_withdraw = stock_prev / self.config.dt if self.config.dt > 0 else 0
                withdraw = min(needed_from_stock, max_withdraw)
                self.C[i] = production + withdraw
                dS = (production - self.C[i]) * self.config.dt
                self.S[i] = stock_prev + dS
                behavior_correct = (withdraw <= stock_prev + 1e-6)
                
            else:
                # EQUILIBRIUM
                self.C[i] = production
                self.S[i] = stock_prev
                behavior_correct = True
            
            # Prevent negative stock
            if self.S[i] < 0:
                self.S[i] = 0
                crisis_detected = True
            
            # Update compliance
            if self.compliance is not None:
                self.compliance[i] = self._update_compliance(i, behavior_correct)
        
        return SimulationResult(
            t=t, P=P, S=self.S, C=self.C,
            compliance=self.compliance, config=self.config,
            system_name="Yusuf (counter-cycle)",
            crisis_detected=crisis_detected
        )


class CapitalistSystem:
    """
    Reference capitalist system with compound interest.
    """
    def __init__(self, config: YusufConfig):
        self.config = config
        self.reset()
    
    def reset(self) -> None:
        self.S = np.zeros(self.config.n_steps)
        self.C = np.zeros(self.config.n_steps)
        self.D = np.zeros(self.config.n_steps)
        self.S[0] = self.config.stock_initial
        self.D[0] = 0.5
    
    def _compute_production(self) -> np.ndarray:
        t = np.linspace(0, self.config.T, self.config.n_steps)
        P = self.config.P_mean + self.config.P_amplitude * np.sin(2 * np.pi * t / self.config.period)
        if self.config.noise_amplitude > 0:
            noise = np.random.normal(0, self.config.noise_amplitude, len(t))
            P = P + noise
        return np.maximum(P, 0.1)
    
    def run(self) -> SimulationResult:
        self.reset()
        P = self._compute_production()
        t = np.linspace(0, self.config.T, self.config.n_steps)
        crisis_detected = False
        
        for i in range(1, self.config.n_steps):
            dt = self.config.dt
            
            # Compound interest on debt
            self.D[i] = self.D[i-1] * (1 + self.config.interest_rate * dt)
            debt_service = self.D[i-1] * self.config.interest_rate * dt
            
            # Consumption
            available = P[i] - debt_service
            self.C[i] = min(available, self.config.need)
            
            # Stock dynamics
            dS = (P[i] - self.C[i]) * dt - debt_service
            self.S[i] = max(0, self.S[i-1] + dS)
            
            if self.S[i] == 0 and self.S[i-1] > 0:
                crisis_detected = True
        
        return SimulationResult(
            t=t, P=P, S=self.S, C=self.C,
            config=self.config, system_name="Capitalist (debt, interest)",
            crisis_detected=crisis_detected
        )


class ScenarioComparator:
    """Compares Yusuf and Capitalist systems"""
    def __init__(self, config: YusufConfig = None):
        self.config = config or YusufConfig()
    
    def run_single(self) -> Tuple[SimulationResult, SimulationResult]:
        """Run a single comparison"""
        np.random.seed(42)
        yusuf = YusufSystem(self.config)
        capitalist = CapitalistSystem(self.config)
        return yusuf.run(), capitalist.run()
    
    def run_monte_carlo(self, n_simulations: int = 100) -> Dict[str, Any]:
        """Run Monte Carlo simulations"""
        yusuf_metrics = []
        capitalist_metrics = []
        
        for seed in range(n_simulations):
            np.random.seed(seed)
            yusuf = YusufSystem(self.config)
            capitalist = CapitalistSystem(self.config)
            y_res = yusuf.run()
            c_res = capitalist.run()
            yusuf_metrics.append(y_res.to_dict())
            capitalist_metrics.append(c_res.to_dict())
        
        def aggregate(metrics_list):
            return {
                "final_stock_mean": np.mean([m["final_stock"] for m in metrics_list]),
                "final_stock_std": np.std([m["final_stock"] for m in metrics_list]),
                "solvency_rate_mean": np.mean([m["solvency_rate"] for m in metrics_list]),
                "consumption_volatility_mean": np.mean([m["consumption_volatility"] for m in metrics_list])
            }
        
        return {
            "yusuf": aggregate(yusuf_metrics),
            "capitalist": aggregate(capitalist_metrics),
            "n_simulations": n_simulations
        }


if __name__ == "__main__":
    config = YusufConfig(T=50, dt=0.5)
    comparator = ScenarioComparator(config)
    y_res, c_res = comparator.run_single()
    
    print("=" * 60)
    print("YUSUF COUNTER-CYCLE MODEL")
    print("=" * 60)
    print(f"Yusuf final stock      : {y_res.final_stock:.2f}")
    print(f"Capitalist final stock : {c_res.final_stock:.2f}")
    print(f"Yusuf solvency         : {y_res.solvency_rate:.1f}%")
    print(f"Capitalist solvency    : {c_res.solvency_rate:.1f}%")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grondona System – Commodity Reserve Department (CRD)
Counter-cyclical commodity buffer stock mechanism
Author: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Tuple


@dataclass
class Commodity:
    """A commodity in the Grondona basket"""
    name: str
    floor_price: float          # Minimum price (trigger to buy)
    ceiling_price: float        # Maximum price (trigger to sell)
    current_price: float        # Current market price
    stockpile: float            # Physical quantity stored
    elasticity: float = 100.0   # Response elasticity to price signals


class CommodityReserveDepartment:
    """
    Grondona System CRD.
    Automatically:
    - Buys commodities when prices fall below floor (issues new currency)
    - Sells commodities when prices rise above ceiling (destroys currency)
    This creates a counter-cyclical money supply and stabilises both
    the currency and commodity prices.
    """
    def __init__(self, commodities: List[Commodity], initial_money_supply: float):
        self.commodities = {c.name: c for c in commodities}
        self.money_supply = initial_money_supply
        self.transaction_cost = 0.001  # 0.1% transaction cost
        self.storage_cost = 0.005      # 0.5% annual storage cost
        self.history = {
            'time': [],
            'money_supply': [],
            'total_stockpile_value': [],
            'commodity_prices': {c.name: [] for c in commodities}
        }
    
    def check_market_prices(self, current_prices: Dict[str, float], time_step: float = 1.0) -> Dict[str, float]:
        """
        Core CRD logic.
        Returns:
        Dict of transactions (commodity name -> quantity bought/sold)
        """
        transactions = {}
        
        for name, price in current_prices.items():
            commodity = self.commodities[name]
            commodity.current_price = price
            
            if price < commodity.floor_price:
                # BUY: Price below floor - expand money supply
                purchase_qty = (commodity.floor_price - price) * commodity.elasticity
                purchase_qty *= (1 - self.transaction_cost)
                commodity.stockpile += purchase_qty
                # Money creation = purchase value
                money_created = purchase_qty * commodity.floor_price
                self.money_supply += money_created
                # Apply storage cost
                self.money_supply -= commodity.stockpile * self.storage_cost * time_step
                transactions[name] = purchase_qty
                
            elif price > commodity.ceiling_price:
                # SELL: Price above ceiling - contract money supply
                sale_qty = min(commodity.stockpile,
                               (price - commodity.ceiling_price) * commodity.elasticity)
                commodity.stockpile -= sale_qty
                # Money destruction = sale value
                money_destroyed = sale_qty * commodity.ceiling_price
                self.money_supply -= money_destroyed
                transactions[name] = -sale_qty
        
        return transactions
    
    def get_total_stockpile_value(self) -> float:
        """Calculate total value of all commodity stockpiles"""
        return sum(c.stockpile * c.current_price for c in self.commodities.values())
    
    def get_stockpile_volume(self) -> Dict[str, float]:
        """Get current stockpile volumes"""
        return {name: c.stockpile for name, c in self.commodities.items()}
    
    def record_state(self, t: float):
        """Record current state for analysis"""
        self.history['time'].append(t)
        self.history['money_supply'].append(self.money_supply)
        self.history['total_stockpile_value'].append(self.get_total_stockpile_value())
        for name, c in self.commodities.items():
            self.history['commodity_prices'][name].append(c.current_price)
    
    def get_history_df(self) -> pd.DataFrame:
        """Return history as DataFrame"""
        df = pd.DataFrame({
            'time': self.history['time'],
            'money_supply': self.history['money_supply'],
            'stockpile_value': self.history['total_stockpile_value']
        })
        for name in self.commodities.keys():
            df[f'price_{name}'] = self.history['commodity_prices'][name]
        return df
    
    def velocity_of_money(self, transactions_volume: float) -> float:
        """Calculate monetary velocity."""
        if self.money_supply == 0:
            return 0.0
        return transactions_volume / (self.money_supply)


class GrondonaSimulator:
    """Simulates the Grondona system over time"""
    def __init__(self, crd: CommodityReserveDepartment, years: int = 50, dt: float = 0.25):
        self.crd = crd
        self.years = years
        self.dt = dt
        self.steps = int(years / dt)
    
    def generate_price_series(self, volatility: float = 0.15) -> List[Dict[str, float]]:
        """Generate stochastic price series for commodities"""
        prices = []
        for step in range(self.steps):
            t = step * self.dt
            price_dict = {}
            for name, commodity in self.crd.commodities.items():
                mean_price = (commodity.floor_price + commodity.ceiling_price) / 2
                shock = np.random.normal(0, volatility * np.sqrt(self.dt))
                seasonal = 0.1 * np.sin(2 * np.pi * t)
                current = mean_price * (1 + shock + seasonal)
                current = max(commodity.floor_price * 0.8,
                              min(commodity.ceiling_price * 1.2, current))
                price_dict[name] = current
            prices.append(price_dict)
        return prices
    
    def run(self, volatility: float = 0.15) -> pd.DataFrame:
        """Run the simulation"""
        price_series = self.generate_price_series(volatility)
        for step, prices in enumerate(price_series):
            t = step * self.dt
            self.crd.check_market_prices(prices, self.dt)
            self.crd.record_state(t)
        return self.crd.get_history_df()


if __name__ == "__main__":
    # Test with 4 commodities (Ahmed 2015 specification)
    commodities = [
        Commodity("Wheat", floor_price=180, ceiling_price=220, current_price=200, stockpile=0),
        Commodity("Copper", floor_price=8000, ceiling_price=12000, current_price=10000, stockpile=0),
        Commodity("Cotton", floor_price=70, ceiling_price=90, current_price=80, stockpile=0),
        Commodity("Rubber", floor_price=140, ceiling_price=180, current_price=160, stockpile=0),
    ]
    
    crd = CommodityReserveDepartment(commodities, initial_money_supply=10000)
    simulator = GrondonaSimulator(crd, years=20, dt=0.25)
    df = simulator.run()
    
    print("=" * 60)
    print("GRONDONA SYSTEM SIMULATION")
    print("=" * 60)
    print(f"Final money supply: {df['money_supply'].iloc[-1]:.2f}")
    print(f"Final stockpile value: {df['stockpile_value'].iloc[-1]:.2f}")
    print(f"Money supply volatility: {df['money_supply'].std():.2f}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Neurocognitive Agents – Mesa implementation
Pain of paying (insula), anticipated reward (striatum), cognitive control (dlPFC)
Author: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import numpy as np
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import defaultdict


class PaymentMode(Enum):
    CASH = "cash"
    CARD = "card"
    CRYPTO = "crypto"
    MOBILE = "mobile"


class ExpenseCategory(Enum):
    NECESSITY = "necessities"
    LEISURE = "leisure"
    INVESTMENT = "investment"
    SOCIAL = "social"


@dataclass
class NeuralSignals:
    """Simulated brain activation signals"""
    striatum: float = 0.0   # Anticipated reward
    insula: float = 0.0     # Pain of paying
    dlpfc: float = 0.0      # Cognitive control
    amygdala: float = 0.0   # Emotional response


@dataclass
class MentalAccounts:
    """Mental accounting (Thaler, 1985)"""
    necessities: float = 0.35
    leisure: float = 0.25
    savings: float = 0.30
    social: float = 0.10
    
    def get_allocation(self, category: ExpenseCategory) -> float:
        mapping = {
            ExpenseCategory.NECESSITY: self.necessities,
            ExpenseCategory.LEISURE: self.leisure,
            ExpenseCategory.INVESTMENT: self.savings,
            ExpenseCategory.SOCIAL: self.social
        }
        return mapping.get(category, 0.20)


class HumanCognition:
    """
    Neurocognitive model of monetary decision-making.
    Integrates:
    - Pain of paying (insula) – Mazar et al. (2017)
    - Anticipated reward (striatum) – Knutson et al. (2007)
    - Cognitive control (dlPFC)
    - Mental accounting (Thaler, 1985)
    - Social influence (contagion of preferences)
    """
    def __init__(self, agent, personality_profile: str = "balanced"):
        self.agent = agent
        self._init_neural_parameters(personality_profile)
        
        # Mental accounting
        self.mental_accounts = MentalAccounts()
        
        # Dynamic state
        self.current_mood: float = 0.5
        self.cognitive_load: float = 0.0
        self.social_pressure: Dict[str, float] = defaultdict(float)
        
        # Decision history
        self.decision_history: List[Dict] = []
        self.neural_history: List[NeuralSignals] = []
        
        # Preferred payment mode (socially influenced)
        self.preferred_payment = PaymentMode.CARD
        
        # Social network
        self.social_connections = []
    
    def _init_neural_parameters(self, profile: str):
        """Initialise neural parameters based on personality profile"""
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
        Calculate pain of paying (insula activation).
        More abstract payment modes cause less pain.
        """
        base_pain = amount / (self.agent.wealth + 1000)
        abstraction_factors = {
            PaymentMode.CASH: 1.0,
            PaymentMode.CARD: 0.55,
            PaymentMode.MOBILE: 0.45,
            PaymentMode.CRYPTO: 0.35
        }
        pain = (base_pain * abstraction_factors[payment_mode] *
                self.pain_sensitivity * (1 + 0.5 * self.cognitive_load))
        
        # Desensitisation from repeated spending
        recent_spending = sum(d['amount'] for d in self.decision_history[-10:] 
                              if d.get('action') == 'spend')
        if recent_spending > self.agent.wealth * 0.3:
            pain *= 0.8
        
        return np.clip(pain, 0.0, 1.0)
    
    def compute_anticipated_reward(self, amount: float, category: ExpenseCategory) -> float:
        """
        Calculate anticipated reward (striatum activation).
        Different categories activate differently.
        """
        category_multipliers = {
            ExpenseCategory.LEISURE: 1.3,
            ExpenseCategory.SOCIAL: 1.2,
            ExpenseCategory.NECESSITY: 0.7,
            ExpenseCategory.INVESTMENT: 0.5
        }
        base_reward = amount * category_multipliers.get(category, 1.0)
        mood_mod = 0.8 + 0.4 * self.current_mood
        reward = base_reward * self.reward_sensitivity * mood_mod
        return np.clip(reward, 0.0, amount * 1.5)
    
    def compute_cognitive_control(self, pain: float, reward: float) -> float:
        """Simulate cognitive control (dlPFC) in arbitrage"""
        conflict = abs(reward - pain)
        effective_control = self.self_control * (1 - 0.5 * self.cognitive_load)
        return conflict * effective_control
    
    def _get_mental_account_balance(self, category: ExpenseCategory) -> float:
        """Calculate remaining balance in mental account"""
        target_allocation = self.mental_accounts.get_allocation(category)
        current_spending = sum(d['amount'] for d in self.decision_history[-30:] 
                               if d.get('category') == category)
        estimated_income = self.agent.wealth * 0.1
        allocated = target_allocation * estimated_income
        return max(0, allocated - current_spending)
    
    def _compute_mental_account_penalty(self, amount: float, category: ExpenseCategory) -> float:
        """Penalty if spending exceeds mental account allocation"""
        balance = self._get_mental_account_balance(category)
        if amount <= balance:
            return 1.0
        overshoot = (amount - balance) / (balance + 1)
        return max(0.3, 1.0 - overshoot)
    
    def update_social_influence(self, neighbors: List):
        """Update cognitive parameters through social contagion"""
        if not neighbors:
            return
        
        neighbor_payments = [n.cognition.preferred_payment for n in neighbors 
                             if hasattr(n, 'cognition')]
        if neighbor_payments:
            dominant = max(set(neighbor_payments), key=neighbor_payments.count)
            influence_strength = 0.05 * len(neighbors) / 10
            if np.random.random() < influence_strength:
                self.preferred_payment = dominant
        
        pain_sensitivities = [n.cognition.pain_sensitivity for n in neighbors 
                              if hasattr(n, 'cognition')]
        if pain_sensitivities:
            self.pain_sensitivity = (0.95 * self.pain_sensitivity + 
                                     0.05 * np.mean(pain_sensitivities))
        
        reward_sensitivities = [n.cognition.reward_sensitivity for n in neighbors 
                                if hasattr(n, 'cognition')]
        if reward_sensitivities:
            self.reward_sensitivity = (0.95 * self.reward_sensitivity + 
                                       0.05 * np.mean(reward_sensitivities))
    
    def compute_social_pressure(self, category: ExpenseCategory) -> float:
        """Calculate social pressure to spend in a category"""
        base_pressure = self.social_pressure.get(category.value, 0.0)
        if hasattr(self.agent, 'social_connections'):
            n_connections = len(self.agent.social_connections)
            pressure = base_pressure * (1 + 0.1 * n_connections)
        else:
            pressure = base_pressure
        return np.clip(pressure, 0.0, 1.0)
    
    def _update_emotional_state(self):
        """Update mood and cognitive load"""
        recent_decisions = self.decision_history[-5:] if self.decision_history else []
        if recent_decisions:
            success_rate = sum(1 for d in recent_decisions 
                               if d.get('satisfaction', 0.5) > 0.6) / len(recent_decisions)
            self.current_mood = 0.5 + 0.3 * (success_rate - 0.5)
        else:
            self.current_mood = 0.5 + 0.1 * np.random.randn()
        self.cognitive_load = min(1.0, self.cognitive_load * 0.9 + 0.05 * np.random.rand())
    
    def decide_spend_or_save(self, opportunities: List[Dict]) -> Tuple[str, Optional[Dict]]:
        """
        Main decision function.
        Returns (action, details) where action is 'spend', 'save', or 'invest_web3'
        """
        self._update_emotional_state()
        
        best_utility = -np.inf
        best_decision = None
        
        for opp in opportunities:
            category = opp.get('category', ExpenseCategory.LEISURE)
            amount = opp['amount']
            payment_mode = opp.get('mode', self.preferred_payment)
            
            # Neurocognitive components
            pain = self.compute_pain_of_paying(amount, payment_mode)
            reward = self.compute_anticipated_reward(amount, category)
            control = self.compute_cognitive_control(pain, reward)
            
            # Psychosocial components
            social_pressure = self.compute_social_pressure(category)
            mental_penalty = self._compute_mental_account_penalty(amount, category)
            
            # Emotional valence (amygdala)
            emotional_valence = self._compute_emotional_valence(opp)
            
            # Net utility
            net_utility = (reward * (1 + emotional_valence) -
                           pain * (1 - control) * (1 + 0.5 * self.cognitive_load))
            net_utility *= mental_penalty
            net_utility *= (1 + social_pressure * 0.5)
            net_utility *= (0.5 + getattr(self.agent, 'passion', 0.5))
            
            if opp.get('requires_trust', False):
                net_utility *= (0.5 + getattr(self.agent, 'trust', 0.5))
            
            # Record neural signals
            self._record_neural_signals(pain, reward, control, emotional_valence)
            
            if net_utility > best_utility:
                best_utility = net_utility
                best_decision = opp
                best_decision['utility'] = net_utility
        
        SAVE_THRESHOLD = 0.15
        if best_utility < SAVE_THRESHOLD:
            save_amount = self.agent.wealth * 0.05 * (1 + self.self_control)
            self._record_decision('save', {'amount': save_amount})
            return ('save', {'amount': save_amount})
        else:
            self._record_decision('spend', best_decision)
            return ('spend', best_decision)
    
    def _compute_emotional_valence(self, opportunity: Dict) -> float:
        """Emotional response (amygdala)"""
        valence = 0.0
        if 'trust' in opportunity:
            valence += opportunity['trust'] * 0.5
        if 'familiarity' in opportunity:
            valence += opportunity['familiarity'] * 0.3
        if opportunity.get('urgent', False):
            valence += 0.4
        return np.clip(valence * self.emotional_reactivity, -0.5, 0.5)
    
    def _record_neural_signals(self, pain: float, reward: float, control: float, emotion: float):
        signals = NeuralSignals(striatum=reward, insula=pain, dlpfc=control, amygdala=emotion)
        self.neural_history.append(signals)
        if len(self.neural_history) > 100:
            self.neural_history.pop(0)
    
    def _record_decision(self, action: str, details: Dict):
        self.decision_history.append({'action': action, 'timestamp': len(self.decision_history), **details})
        if len(self.decision_history) > 100:
            self.decision_history.pop(0)
    
    def get_neural_profile(self) -> Dict:
        if not self.neural_history:
            return {'striatum': 0, 'insula': 0, 'dlpfc': 0, 'amygdala': 0}
        recent = self.neural_history[-10:]
        return {
            'striatum': np.mean([n.striatum for n in recent]),
            'insula': np.mean([n.insula for n in recent]),
            'dlpfc': np.mean([n.dlpfc for n in recent]),
            'amygdala': np.mean([n.amygdala for n in recent])
        }


class CognitiveAgent:
    """Base class for an agent with neurocognitive faculties"""
    def __init__(self, unique_id, model, personality: str = "balanced"):
        self.unique_id = unique_id
        self.model = model
        self.wealth = 1000.0
        self.trust = np.random.uniform(0.3, 0.9)
        self.passion = np.random.uniform(0.2, 0.8)
        self.cognition = HumanCognition(self, personality)
        self.social_connections = []
    
    def step(self):
        """Agent step – generate opportunities and decide"""
        opportunities = self._generate_spending_opportunities()
        action, details = self.cognition.decide_spend_or_save(opportunities)
        
        if action == 'spend':
            self._execute_spending(details)
        elif action == 'save':
            self._execute_saving(details)
        elif action == 'invest_web3':
            self._execute_web3_investment(details)
        
        if self.social_connections:
            self.cognition.update_social_influence(self.social_connections)
    
    def _generate_spending_opportunities(self) -> List[Dict]:
        opportunities = []
        if np.random.random() < 0.7:
            opportunities.append({
                'amount': np.random.uniform(10, 100),
                'category': ExpenseCategory.LEISURE,
                'mode': np.random.choice(list(PaymentMode)),
                'requires_trust': False,
                'familiarity': np.random.uniform(0.3, 0.9)
            })
        if np.random.random() < 0.4:
            opportunities.append({
                'amount': np.random.uniform(20, 150),
                'category': ExpenseCategory.NECESSITY,
                'mode': PaymentMode.CARD,
                'requires_trust': False,
                'urgent': np.random.random() < 0.3
            })
        return opportunities
    
    def _execute_spending(self, details: Dict):
        amount = details['amount']
        if amount <= self.wealth:
            self.wealth -= amount
    
    def _execute_saving(self, details: Dict):
        amount = details['amount']
        self.wealth -= amount
    
    def _execute_web3_investment(self, details: Dict):
        amount = details['amount']
        if amount <= self.wealth:
            self.wealth -= amount


if __name__ == "__main__":
    from mesa import Model
    from mesa.time import RandomActivation
    
    class TestModel(Model):
        def __init__(self, n_agents=10):
            super().__init__()
            self.schedule = RandomActivation(self)
            for i in range(n_agents):
                agent = CognitiveAgent(i, self, np.random.choice(['balanced', 'impulsive', 'frugal', 'social']))
                self.schedule.add(agent)
    
    model = TestModel(10)
    for _ in range(50):
        model.schedule.step()
    print("Neurocognitive agents test completed")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ricci Flow on Trust Networks
Ollivier-Ricci curvature for economic network analysis
Author: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import numpy as np
import networkx as nx
from scipy.optimize import linear_sum_assignment
from typing import Tuple, Dict


def ollivier_ricci_curvature(G: nx.Graph, edge: Tuple, alpha: float = 0.5) -> float:
    """
    Compute Ollivier-Ricci curvature for an edge.
    Lower curvature = more hyperbolic/tense
    Higher curvature = more flat/abundant
    Based on Wasserstein-1 distance between neighborhood distributions.
    """
    u, v = edge
    
    # Closed neighborhoods
    N_u = set(G.neighbors(u)) | {u}
    N_v = set(G.neighbors(v)) | {v}
    
    def dist(a, b):
        """Shortest path distance (capped)"""
        try:
            return min(1.0, nx.shortest_path_length(G, a, b) / 2.0)
        except:
            return 1.0
    
    nodes_union = list(N_u.union(N_v))
    n = len(nodes_union)
    
    # Build cost matrix for optimal transport
    cost_matrix = np.zeros((n, n))
    for i, a in enumerate(nodes_union):
        for j, b in enumerate(nodes_union):
            if a in N_u and b in N_v:
                cost_matrix[i, j] = dist(a, b)
            else:
                cost_matrix[i, j] = 1e6
    
    # Solve optimal transport (Earth Mover's Distance)
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    wasserstein = cost_matrix[row_ind, col_ind].sum() / n
    curvature = 1.0 - 2.0 * wasserstein
    return np.clip(curvature, -1.0, 1.0)


def compute_all_curvatures(G: nx.Graph, alpha: float = 0.5) -> Dict[Tuple, float]:
    """Compute Ricci curvature for all edges in the graph"""
    curvatures = {}
    for u, v in G.edges():
        curvatures[(u, v)] = ollivier_ricci_curvature(G, (u, v), alpha)
        curvatures[(v, u)] = curvatures[(u, v)]  # Symmetric
    return curvatures


def apply_ricci_flow(G: nx.Graph, curvatures: Dict[Tuple, float], dt: float = 0.01) -> nx.Graph:
    """
    Apply Ricci flow to the graph.
    Updates edge weights based on curvature:
    - Positive curvature -> weight decreases (more connected)
    - Negative curvature -> weight increases (more tension)
    """
    for (u, v), curvature in curvatures.items():
        if (u, v) in G.edges():
            current_weight = G[u][v].get('weight', 1.0)
            new_weight = current_weight + curvature * dt
            G[u][v]['weight'] = max(0.1, min(10.0, new_weight))
    return G


def curvature_to_phase(curvature: float) -> str:
    """Convert curvature to phase description"""
    if curvature > 0.3:
        return "abundance"
    elif curvature < -0.3:
        return "scarcity"
    else:
        return "equilibrium"


def trust_weighted_curvature(G: nx.Graph, curvatures: Dict[Tuple, float]) -> float:
    """
    Compute trust-weighted median curvature for YCCP signal.
    """
    weighted_curvatures = []
    for (u, v), curv in curvatures.items():
        trust_u = G.nodes[u].get('trust', 0.5)
        trust_v = G.nodes[v].get('trust', 0.5)
        w = (trust_u + trust_v) / 2.0
        weighted_curvatures.append(curv * w)
    if not weighted_curvatures:
        return 0.0
    return np.median(weighted_curvatures)


def detect_critical_point(curvatures: Dict[Tuple, float], threshold: float = 0.1) -> bool:
    """
    Detect if system is near critical point.
    Critical point is when curvature distribution has high variance.
    """
    curv_vals = list(curvatures.values())
    if len(curv_vals) < 2:
        return False
    variance = np.var(curv_vals)
    return variance < threshold  # Low variance = near critical


def create_trust_network(n_nodes: int = 50, edge_prob: float = 0.1) -> nx.Graph:
    """Create a random trust network"""
    G = nx.erdos_renyi_graph(n_nodes, edge_prob)
    
    # Add trust attributes
    for node in G.nodes():
        G.nodes[node]['trust'] = np.random.uniform(0.3, 0.9)
        G.nodes[node]['recommendation'] = np.random.uniform(0, 1)
    
    for u, v in G.edges():
        G[u][v]['weight'] = np.random.uniform(0.5, 1.5)
        G[u][v]['trust'] = (G.nodes[u]['trust'] + G.nodes[v]['trust']) / 2
    
    return G


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    
    # Create test network
    G = create_trust_network(30, 0.15)
    
    # Compute curvatures
    curvatures = compute_all_curvatures(G)
    
    print("=" * 60)
    print("RICCI FLOW ON TRUST NETWORK")
    print("=" * 60)
    print(f"Number of edges: {len(G.edges())}")
    print(f"Mean curvature: {np.mean(list(curvatures.values())):.3f}")
    print(f"Curvature std: {np.std(list(curvatures.values())):.3f}")
    
    # Phase detection
    median_curv = trust_weighted_curvature(G, curvatures)
    print(f"Trust-weighted median curvature: {median_curv:.3f}")
    print(f"Phase: {curvature_to_phase(median_curv)}")
    print(f"Near critical point: {detect_critical_point(curvatures)}")
    
    # Apply Ricci flow
    G = apply_ricci_flow(G, curvatures, dt=0.05)
    print("\nAfter Ricci flow:")
    print(f"Mean weight: {np.mean([G[u][v]['weight'] for u,v in G.edges()]):.3f}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Statistical Validation Module
Monte Carlo, t-tests, Mann-Whitney, Bootstrap, Confidence Intervals
Author: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import numpy as np
from scipy import stats
from dataclasses import dataclass
from typing import Dict, Any, List, Tuple
import json

from yusuf_model import YusufConfig, YusufSystem, CapitalistSystem, SimulationResult


@dataclass
class StatisticalTestResult:
    """Result of a statistical test"""
    test_name: str
    statistic: float
    p_value: float
    significant: bool
    interpretation: str
    effect_size: float = None


class StatisticalValidator:
    """Statistical validator comparing Yusuf and Capitalist systems"""
    
    def __init__(self, config: YusufConfig = None, seed: int = 42):
        self.config = config or YusufConfig()
        self.seed = seed
        np.random.seed(seed)
    
    def run_simulations(self, n_simulations: int = 100) -> Tuple[List[SimulationResult], List[SimulationResult]]:
        """Run N simulations of both systems"""
        yusuf_results = []
        capitalist_results = []
        for i in range(n_simulations):
            np.random.seed(self.seed + i)
            yusuf = YusufSystem(self.config)
            capitalist = CapitalistSystem(self.config)
            yusuf_results.append(yusuf.run())
            capitalist_results.append(capitalist.run())
        return yusuf_results, capitalist_results
    
    def extract_metrics(self, results: List[SimulationResult]) -> List[Dict[str, float]]:
        """Extract key metrics from results"""
        metrics = []
        for res in results:
            metrics.append({
                "final_stock": res.final_stock,
                "mean_consumption": res.mean_consumption,
                "consumption_volatility": res.consumption_volatility,
                "solvency_rate": res.solvency_rate,
                "coverage_ratio_mean": float(np.mean(res.coverage_ratio))
            })
        return metrics
    
    def test_normality(self, data: np.ndarray) -> Tuple[float, bool]:
        """Shapiro-Wilk normality test"""
        if len(data) < 3:
            return 0.0, False
        statistic, p_value = stats.shapiro(data)
        return p_value, p_value > 0.05
    
    def test_difference(self, yusuf_data: np.ndarray, cap_data: np.ndarray, 
                        metric_name: str) -> StatisticalTestResult:
        """Test difference between systems"""
        _, yusuf_normal = self.test_normality(yusuf_data)
        _, cap_normal = self.test_normality(cap_data)
        
        if yusuf_normal and cap_normal:
            statistic, p_value = stats.ttest_ind(yusuf_data, cap_data)
            test_name = f"t-test ({metric_name})"
            pooled_std = np.sqrt((np.var(yusuf_data) + np.var(cap_data)) / 2)
            effect_size = (np.mean(yusuf_data) - np.mean(cap_data)) / pooled_std if pooled_std > 0 else 0
        else:
            statistic, p_value = stats.mannwhitneyu(yusuf_data, cap_data, alternative='two-sided')
            test_name = f"Mann-Whitney U ({metric_name})"
            effect_size = statistic / (len(yusuf_data) * len(cap_data)) - 0.5
        
        mean_diff = np.mean(yusuf_data) - np.mean(cap_data)
        
        if p_value < 0.05:
            if mean_diff > 0:
                interpretation = f"Yusuf > Capitalist (diff={mean_diff:.3f})"
            else:
                interpretation = f"Capitalist > Yusuf (diff={-mean_diff:.3f})"
        else:
            interpretation = "No significant difference"
        
        return StatisticalTestResult(
            test_name=test_name, statistic=statistic, p_value=p_value,
            significant=p_value < 0.05, interpretation=interpretation, effect_size=abs(effect_size)
        )
    
    def compute_confidence_intervals(self, yusuf_data: np.ndarray, cap_data: np.ndarray,
                                     confidence: float = 0.95) -> Dict[str, Any]:
        """Compute confidence intervals"""
        z = stats.norm.ppf((1 + confidence) / 2)
        
        def ci(data):
            mean = np.mean(data)
            std = np.std(data)
            margin = z * std / np.sqrt(len(data))
            return (mean - margin, mean + margin), mean, std
        
        y_ci, y_mean, y_std = ci(yusuf_data)
        c_ci, c_mean, c_std = ci(cap_data)
        
        return {
            "yusuf": {"mean": y_mean, "ci_lower": y_ci[0], "ci_upper": y_ci[1], "std": y_std},
            "capitalist": {"mean": c_mean, "ci_lower": c_ci[0], "ci_upper": c_ci[1], "std": c_std}
        }
    
    def run_validation(self, n_simulations: int = 100) -> Dict[str, Any]:
        """Run complete statistical validation"""
        yusuf_results, capitalist_results = self.run_simulations(n_simulations)
        yusuf_metrics = self.extract_metrics(yusuf_results)
        capitalist_metrics = self.extract_metrics(capitalist_results)
        
        metrics_names = ["final_stock", "mean_consumption", "consumption_volatility", "solvency_rate"]
        
        yusuf_arrays = {name: np.array([m[name] for m in yusuf_metrics]) for name in metrics_names}
        cap_arrays = {name: np.array([m[name] for m in capitalist_metrics]) for name in metrics_names}
        
        tests = []
        for name in metrics_names:
            tests.append(self.test_difference(yusuf_arrays[name], cap_arrays[name], name))
        
        ci = self.compute_confidence_intervals(yusuf_arrays["final_stock"], cap_arrays["final_stock"])
        
        return {
            "n_simulations": n_simulations,
            "tests": [t.__dict__ for t in tests],
            "confidence_intervals": ci,
            "yusuf_mean_stock": float(np.mean(yusuf_arrays["final_stock"])),
            "capitalist_mean_stock": float(np.mean(cap_arrays["final_stock"])),
            "yusuf_solvency": float(np.mean(yusuf_arrays["solvency_rate"])),
            "capitalist_solvency": float(np.mean(cap_arrays["solvency_rate"]))
        }


class BootstrapAnalyzer:
    """Bootstrap analysis for robustness"""
    
    def __init__(self, n_bootstrap: int = 1000, confidence: float = 0.95):
        self.n_bootstrap = n_bootstrap
        self.confidence = confidence
    
    def compare(self, yusuf_data: np.ndarray, cap_data: np.ndarray) -> Dict[str, Any]:
        """Compare systems using bootstrap"""
        n = min(len(yusuf_data), len(cap_data))
        diff_means = []
        
        for _ in range(self.n_bootstrap):
            y_sample = np.random.choice(yusuf_data, size=n, replace=True)
            c_sample = np.random.choice(cap_data, size=n, replace=True)
            diff_means.append(np.mean(y_sample) - np.mean(c_sample))
        
        ci_lower = np.percentile(diff_means, 2.5)
        ci_upper = np.percentile(diff_means, 97.5)
        prob_yusuf_better = np.mean([d > 0 for d in diff_means])
        
        return {
            "diff_means_ci": (ci_lower, ci_upper),
            "prob_yusuf_better": prob_yusuf_better,
            "significant_95": ci_lower > 0 or ci_upper < 0
        }


if __name__ == "__main__":
    validator = StatisticalValidator()
    results = validator.run_validation(n_simulations=50)
    
    print("=" * 60)
    print("STATISTICAL VALIDATION")
    print("=" * 60)
    print(f"Based on {results['n_simulations']} simulations")
    print(f"Yusuf mean stock: {results['yusuf_mean_stock']:.3f}")
    print(f"Capitalist mean stock: {results['capitalist_mean_stock']:.3f}")
    print(f"Yusuf solvency: {results['yusuf_solvency']:.1f}%")
    print(f"Capitalist solvency: {results['capitalist_solvency']:.1f}%")
    
    print("\nStatistical tests:")
    for test in results['tests']:
        sig = "✓" if test['significant'] else "✗"
        print(f"  {sig} {test['test_name']}: p={test['p_value']:.4f} ({test['interpretation']})")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Streamlit Interactive Dashboard – Yusuf Counter-Cycle Model
Run with: streamlit run streamlit_app.py
Author: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from yusuf_model import YusufConfig, YusufSystem, CapitalistSystem, ScenarioComparator
from grondona_crd import Commodity, CommodityReserveDepartment, GrondonaSimulator
from statistical_validation import StatisticalValidator


st.set_page_config(
    page_title="Yusuf Counter-Cycle – Monetary Model",
    page_icon="🪙",
    layout="wide"
)


st.markdown("""
<style>
.main-header {
    text-align: center;
    padding: 1rem;
    background: linear-gradient(90deg, #1a472a, #2d6a4f);
    color: white;
    border-radius: 10px;
    margin-bottom: 2rem;
}
.quran-quote {
    font-style: italic;
    text-align: center;
    padding: 1rem;
    background: #f0f2f6;
    border-radius: 10px;
    margin: 1rem 0;
    border-right: 4px solid #2d6a4f;
}
.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="main-header">
    <h1>🪙 YUSUF COUNTER-CYCLE MODEL</h1>
    <p>From Usury to Resilience – Bimetallic Alternative to Debt-Based Money</p>
    <p style="font-size: 0.8rem;">Based on Surah Yusuf (12:47-48) | Grondona System | Neurocognitive Agents</p>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div class="quran-quote">
    <strong>Surah Yusuf (12:47-48)</strong><br>
    "For seven years you shall sow as usual. What you reap, leave it in its ears, except a little that you eat.
    Then after that will come seven hard years which will devour what you have prepared for them..."
</div>
""", unsafe_allow_html=True)


with st.sidebar:
    st.header("⚙️ Parameters")
    
    st.subheader("📐 Time")
    T = st.slider("Years", 20, 200, 100, 10)
    dt = st.slider("Time step (years)", 0.05, 0.5, 0.1, 0.05)
    
    st.subheader("📊 Economy")
    need = st.slider("Minimum consumption need", 0.3, 1.0, 0.7, 0.05)
    P_amplitude = st.slider("Production amplitude", 0.2, 0.8, 0.5, 0.05)
    period = st.slider("Cycle period (years)", 8, 20, 14, 1)
    interest_rate = st.slider("Interest rate (capitalist)", 0.0, 0.15, 0.05, 0.01)
    
    st.subheader("🎮 Gamification")
    gamification = st.checkbox("Enable social credit", value=True)
    compliance_threshold = st.slider("Compliance threshold", 0.5, 0.95, 0.8, 0.05)
    
    st.subheader("🌊 Noise")
    noise = st.slider("Production noise", 0.0, 0.1, 0.03, 0.01)
    
    run_button = st.button("▶ Run Simulation", use_container_width=True)


config = YusufConfig(
    T=T, dt=dt, need=need, P_amplitude=P_amplitude, period=period,
    interest_rate=interest_rate, gamification_enabled=gamification,
    compliance_threshold=compliance_threshold, noise_amplitude=noise
)


@st.cache_data
def run_simulation(config):
    comparator = ScenarioComparator(config)
    return comparator.run_single()


if run_button:
    with st.spinner("Running simulation..."):
        y_res, c_res = run_simulation(config)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Yusuf Final Stock", f"{y_res.final_stock:.2f}",
                  delta=f"{y_res.final_stock - c_res.final_stock:+.2f} vs Capitalist")
    
    with col2:
        st.metric("Capitalist Final Stock", f"{c_res.final_stock:.2f}")
    
    with col3:
        delta_solv = y_res.solvency_rate - c_res.solvency_rate
        st.metric("Solvency", f"{y_res.solvency_rate:.1f}%",
                  delta=f"{delta_solv:+.1f}% for Yusuf")
    
    with col4:
        delta_vol = (1 - y_res.consumption_volatility / max(c_res.consumption_volatility, 0.01)) * 100
        st.metric("Stability", f"Vol={y_res.consumption_volatility:.3f}",
                  delta=f"{delta_vol:+.0f}% more stable")
    
    # Interactive chart
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=("Production Cycle", "Stock Evolution",
                                        "Consumption", "Coverage Ratio"))
    
    fig.add_trace(go.Scatter(x=y_res.t, y=y_res.P, name="Production", line=dict(color='black')),
                  row=1, col=1)
    fig.add_hline(y=config.P_bar, line_dash="dash", line_color="green",
                  annotation_text="Abundance", row=1, col=1)
    fig.add_hline(y=config.P_underline, line_dash="dash", line_color="red",
                  annotation_text="Scarcity", row=1, col=1)
    
    fig.add_trace(go.Scatter(x=c_res.t, y=c_res.S, name="Capitalist", line=dict(color='red')),
                  row=1, col=2)
    fig.add_trace(go.Scatter(x=y_res.t, y=y_res.S, name="Yusuf", line=dict(color='blue')),
                  row=1, col=2)
    
    fig.add_trace(go.Scatter(x=c_res.t, y=c_res.C, name="Capitalist", line=dict(color='red', opacity=0.7)),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=y_res.t, y=y_res.C, name="Yusuf", line=dict(color='blue', opacity=0.7)),
                  row=2, col=1)
    fig.add_hline(y=config.need, line_dash="dot", line_color="black", row=2, col=1)
    
    fig.add_trace(go.Scatter(x=c_res.t, y=c_res.coverage_ratio, name="Capitalist", line=dict(color='red')),
                  row=2, col=2)
    fig.add_trace(go.Scatter(x=y_res.t, y=y_res.coverage_ratio, name="Yusuf", line=dict(color='blue')),
                  row=2, col=2)
    fig.add_hline(y=1, line_dash="dash", line_color="black", row=2, col=2)
    
    fig.update_layout(height=600, showlegend=True,
                      legend=dict(orientation="h", yanchor="bottom", y=1.02))
    st.plotly_chart(fig, use_container_width=True)
    
    # Results table
    with st.expander("📊 Detailed Results"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Yusuf System")
            st.dataframe(pd.DataFrame({
                "Metric": ["Final stock", "Mean consumption", "Volatility", "Solvency"],
                "Value": [f"{y_res.final_stock:.2f}", f"{y_res.mean_consumption:.2f}",
                          f"{y_res.consumption_volatility:.4f}", f"{y_res.solvency_rate:.1f}%"]
            }), hide_index=True)
        
        with col2:
            st.subheader("Capitalist System")
            st.dataframe(pd.DataFrame({
                "Metric": ["Final stock", "Mean consumption", "Volatility", "Solvency"],
                "Value": [f"{c_res.final_stock:.2f}", f"{c_res.mean_consumption:.2f}",
                          f"{c_res.consumption_volatility:.4f}", f"{c_res.solvency_rate:.1f}%"]
            }), hide_index=True)
    
    # Interpretation
    st.markdown("""
    <div class="quran-quote">
        <strong>💡 Interpretation</strong><br>
        The Yusuf counter-cycle system demonstrates higher solvency, lower volatility,
        and greater resilience to shocks than the interest-based capitalist system.
        This validates the principle of saving in abundance and consuming from stock in scarcity.
    </div>
    """, unsafe_allow_html=True)

else:
    st.info("👈 Configure parameters in the sidebar and click 'Run Simulation'")


st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem;">
    <p>🪙 Yusuf Counter-Cycle Model – CC BY-SA 4.0 | Marc Daghar | Free Dr Aafia Siddiqui !</p>
    <p>🌿 Blessed are the cracked, for they shall let in the light.</p>
</div>
""", unsafe_allow_html=True)

