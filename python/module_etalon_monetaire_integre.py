# ===================================================
# MODULE 1: MODÉLISATION DE L'ÉTALON MONÉTAIRE INTÉGRÉ
# ===================================================

import numpy as np
from dataclasses import dataclass
from typing import Dict, Tuple
import math

@dataclass
class MonetaryParams:
    """Paramètres pour le modèle monétaire intégré"""
    wealth_real: float          # W - Richesse réelle
    confidence: float           # C - Confiance collective (0-1)
    time_horizon: float         # T - Horizon temporel (années)
    alpha_wealth: float = 0.4   # Poids de la richesse dans la fonction
    alpha_confidence: float = 0.4
    alpha_time: float = 0.2

class IntegratedStandard:
    """
    Implémentation de la théorie de l'étalon intégré:
    M = f(W, C, T)
    """
    
    def __init__(self, params: MonetaryParams):
        self.params = params
    
    def money_supply(self) -> float:
        """
        Calcule la masse monétaire selon l'équation:
        M = W^α * C^β * T^γ
        """
        W = self.params.wealth_real
        C = self.params.confidence
        T = self.params.time_horizon
        
        # Normalisation pour éviter les valeurs extrêmes
        W_norm = max(W, 0.1)
        C_norm = max(min(C, 1.0), 0.01)
        T_norm = max(T, 0.1)
        
        M = (W_norm ** self.params.alpha_wealth) * \
            (C_norm ** self.params.alpha_confidence) * \
            (T_norm ** self.params.alpha_time)
        
        return M
    
    def marginal_effects(self) -> Dict[str, float]:
        """Calcule les dérivées partielles ∂M/∂W, ∂M/∂C, ∂M/∂T"""
        W = self.params.wealth_real
        C = self.params.confidence
        T = self.params.time_horizon
        
        # ∂M/∂W = α * W^(α-1) * C^β * T^γ
        dM_dW = (self.params.alpha_wealth * 
                 (W ** (self.params.alpha_wealth - 1)) *
                 (C ** self.params.alpha_confidence) *
                 (T ** self.params.alpha_time))
        
        # ∂M/∂C = β * W^α * C^(β-1) * T^γ
        dM_dC = (self.params.alpha_confidence *
                 (W ** self.params.alpha_wealth) *
                 (C ** (self.params.alpha_confidence - 1)) *
                 (T ** self.params.alpha_time))
        
        # ∂M/∂T = γ * W^α * C^β * T^(γ-1)
        dM_dT = (self.params.alpha_time *
                 (W ** self.params.alpha_wealth) *
                 (C ** self.params.alpha_confidence) *
                 (T ** (self.params.alpha_time - 1)))
        
        return {
            'dM_dW': dM_dW,
            'dM_dC': dM_dC,
            'dM_dT': dM_dT
        }


# ===================================================
# MODULE 2: SYSTÈME BIMÉTALLIQUE
# ===================================================

@dataclass
class BimetallicReserves:
    """Réserves pour le système bimétallique"""
    gold_grams: float           # R_or
    silver_grams: float         # R_argent
    gold_price_usd: float       # P_or
    silver_price_usd: float     # P_argent
    basket_weight_gold: float = 0.6  # α (alpha)
    
    @property
    def basket_weight_silver(self) -> float:
        return 1.0 - self.basket_weight_gold

class BimetallicStandard:
    """
    Implémentation de l'étalon bimétallique:
    M = (R_or * P_or * α + R_argent * P_argent * (1-α)) / P_marchandises
    """
    
    def __init__(self, reserves: BimetallicReserves, price_level: float = 1.0):
        self.reserves = reserves
        self.price_level = price_level  # P_marchandises
    
    def money_supply(self) -> float:
        """Calcule la masse monétaire M"""
        R_or = self.reserves.gold_grams
        R_argent = self.reserves.silver_grams
        P_or = self.reserves.gold_price_usd
        P_argent = self.reserves.silver_price_usd
        α = self.reserves.basket_weight_gold
        
        numerator = R_or * P_or * α + R_argent * P_argent * (1 - α)
        M = numerator / self.price_level
        
        return M
    
    def variance_analysis(self, gold_volatility: float, silver_volatility: float, correlation: float) -> float:
        """
        Analyse la variance du portefeuille bimétallique
        Var(M) = (α² * σ_or² + (1-α)² * σ_argent² + 2*α*(1-α)*σ_or*σ_argent*ρ) / P_marchandises²
        """
        α = self.reserves.basket_weight_gold
        R_or = self.reserves.gold_grams
        R_argent = self.reserves.silver_grams
        
        # Variance des prix des métaux
        var_gold = (gold_volatility * self.reserves.gold_price_usd) ** 2
        var_silver = (silver_volatility * self.reserves.silver_price_usd) ** 2
        cov_gs = (gold_volatility * self.reserves.gold_price_usd * 
                  silver_volatility * self.reserves.silver_price_usd * correlation)
        
        # Variance de M
        var_M = (α**2 * var_gold + (1-α)**2 * var_silver + 
                 2 * α * (1-α) * cov_gs) / (self.price_level ** 2)
        
        return var_M
    
    def money_supply_with_zakat(self, zakat_rate: float = 0.025) -> float:
        """Masse monétaire après prélèvement de la Zakāt"""
        M = self.money_supply()
        return M * (1 - zakat_rate)


# ===================================================
# MODULE 3: MODÉLISATION DU CRYPTO-FULUS (LBP-T)
# ===================================================

@dataclass
class CryptoFulusParams:
    """Paramètres du Crypto-Fulus"""
    reserves_gold_g: float      # Réserves d'or
    reserves_silver_g: float    # Réserves d'argent
    price_gold_usd: float
    price_silver_usd: float
    target_price: float         # P_LBP-T
    alpha_gold: float = 0.6

class CryptoFulus:
    """
    Modélisation du LBP-T:
    1 LBP-T = (0.01g_or * P_or * 0.6 + 0.05g_argent * P_argent * 0.4) / P_LBP-T
    """
    
    def __init__(self, params: CryptoFulusParams):
        self.params = params
    
    def unit_value(self) -> float:
        """Calcule la valeur d'un LBP-T"""
        gold_portion = 0.01 * self.params.price_gold_usd * self.params.alpha_gold
        silver_portion = 0.05 * self.params.price_silver_usd * (1 - self.params.alpha_gold)
        return (gold_portion + silver_portion) / self.params.target_price
    
    def new_emission(self, new_gold_g: float, new_silver_g: float) -> float:
        """
        ΔM_LBP-T = (ΔR_or * P_or * α + ΔR_argent * P_argent * (1-α)) / P_LBP-T
        """
        delta_value = (new_gold_g * self.params.price_gold_usd * self.params.alpha_gold +
                       new_silver_g * self.params.price_silver_usd * (1 - self.params.alpha_gold))
        return delta_value / self.params.target_price
    
    def money_supply_dynamics(self, current_supply: float, 
                              zakat_rate: float = 0.025,
                              new_emission: float = 0.0,
                              credit_repayments: float = 0.0) -> float:
        """
        M_{t+1} = M_t - τ * M_t + ΔE_t + ΔC_t
        """
        return current_supply * (1 - zakat_rate) + new_emission + credit_repayments


# ===================================================
# MODULE 4: MODÉLISATION DU DÉTOUR (BLOCKCHAIN)
# ===================================================

@dataclass
class BlockchainParams:
    """Paramètres techniques pour le coût du détour"""
    base_cost: float            # c₀
    energy_consumed: float      # E (kWh)
    tx_per_block: int           # n
    finality_blocks: int        # T
    block_frequency: float      # τ (secondes)
    energy_price: float         # α ($/kWh)
    opportunity_cost: float     # β ($/heure)

class BlockchainDetour:
    """
    Modélisation du coût du détour blockchain:
    C_tx = c₀ + α * (E/n) + β * (log(T)/τ)
    """
    
    def __init__(self, params: BlockchainParams):
        self.params = params
    
    def transaction_cost(self) -> float:
        """Calcule le coût total d'une transaction"""
        # Terme énergétique
        energy_term = self.params.energy_price * (self.params.energy_consumed / self.params.tx_per_block)
        
        # Terme temporel (latence)
        # T: temps d'attente pour finalité (T * τ)
        wait_time_hours = (self.params.finality_blocks * self.params.block_frequency) / 3600
        time_term = self.params.opportunity_cost * wait_time_hours
        
        return self.params.base_cost + energy_term + time_term
    
    def risk_adjusted_cost(self, risk_central: float, risk_blockchain: float) -> Dict[str, float]:
        """
        Compare les coûts ajustés du risque:
        R_bc + C_tx < R + c₀
        """
        C_tx = self.transaction_cost()
        
        cost_central = risk_central + self.params.base_cost
        cost_blockchain = risk_blockchain + C_tx
        
        is_efficient = cost_blockchain < cost_central
        
        return {
            'cost_central': cost_central,
            'cost_blockchain': cost_blockchain,
            'is_efficient': is_efficient,
            'saving': cost_central - cost_blockchain if is_efficient else 0
        }
    
    def monte_carlo_simulation(self, n_simulations: int = 1000) -> Dict[str, float]:
        """
        Simulation Monte Carlo des coûts avec variables stochastiques
        """
        results = []
        
        for _ in range(n_simulations):
            # Variables aléatoires
            energy_price_sim = np.random.normal(self.params.energy_price, 0.01)
            energy_sim = np.random.normal(self.params.energy_consumed, 10)
            block_freq_sim = np.random.normal(self.params.block_frequency, 5)
            
            # Calcul du coût
            energy_term = energy_price_sim * (energy_sim / self.params.tx_per_block)
            wait_time = (self.params.finality_blocks * block_freq_sim) / 3600
            time_term = self.params.opportunity_cost * wait_time
            
            cost = self.params.base_cost + energy_term + time_term
            results.append(cost)
        
        return {
            'mean': np.mean(results),
            'std': np.std(results),
            'percentile_95': np.percentile(results, 95)
        }


# ===================================================
# MODULE 5: GOUVERNANCE ET PROOF OF SOCIAL STAKE (PoSS)
# ===================================================

@dataclass
class Member:
    """Membre d'une guilde"""
    id: int
    fulus_balance: float        # s_i
    seniority_days: int         # a_i
    participation_score: float  # p_i (0-100)
    reputation_score: float     # r_i (0-100)

class SocialStakeConsensus:
    """
    Implémentation du Proof of Social Stake (PoSS):
    w_i = (s_i/S)^α * (a_i/A)^β * (p_i/P)^γ * (r_i/R)^δ
    """
    
    def __init__(self, members: list[Member], 
                 alpha: float = 0.3, beta: float = 0.3, 
                 gamma: float = 0.2, delta: float = 0.2):
        self.members = members
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
    
    def validate_weight_sum(self) -> float:
        """Vérifie que la somme des coefficients = 1"""
        return self.alpha + self.beta + self.gamma + self.delta
    
    def calculate_weight(self, member: Member) -> float:
        """
        Calcule le poids de validation pour un membre
        """
        # Sommes totales
        S = sum(m.fulus_balance for m in self.members)
        A = sum(m.seniority_days for m in self.members)
        P = sum(m.participation_score for m in self.members)
        R = sum(m.reputation_score for m in self.members)
        
        # Évitement des divisions par zéro
        S = max(S, 0.01)
        A = max(A, 0.01)
        P = max(P, 0.01)
        R = max(R, 0.01)
        
        # Calcul du poids
        w = ((member.fulus_balance / S) ** self.alpha *
             (member.seniority_days / A) ** self.beta *
             (member.participation_score / P) ** self.gamma *
             (member.reputation_score / R) ** self.delta)
        
        return w
    
    def get_all_weights(self) -> Dict[int, float]:
        """Retourne les poids de tous les membres"""
        return {m.id: self.calculate_weight(m) for m in self.members}
    
    def select_proposer(self) -> Member:
        """
        Sélectionne un proposant par tirage pondéré
        """
        weights = self.get_all_weights()
        total_weight = sum(weights.values())
        
        if total_weight == 0:
            return self.members[0]
        
        # Tirage aléatoire pondéré
        random_value = np.random.random() * total_weight
        cumulative = 0.0
        
        for member in self.members:
            cumulative += weights[member.id]
            if random_value <= cumulative:
                return member
        
        return self.members[-1]
    
    def validate_block(self, proposer: Member, signatures: list[int]) -> bool:
        """
        Vérifie si le bloc est validé (2/3 du poids)
        Règle: Σ w_i_signataires > (2/3) * Σ w_i_tous
        """
        all_weights = self.get_all_weights()
        total_weight = sum(all_weights.values())
        
        signed_weight = sum(all_weights[member_id] for member_id in signatures 
                           if member_id in all_weights)
        
        required_weight = (2/3) * total_weight
        return signed_weight > required_weight
    
    def penalize_participation(self, member_id: int, penalty: float = 10) -> None:
        """Sanctionne un membre par réduction de son score de participation"""
        for member in self.members:
            if member.id == member_id:
                member.participation_score = max(0, member.participation_score - penalty)
                break


# ===================================================
# MODULE 6: DYNAMIQUE MONÉTAIRE AVEC ZAKĀT
# ===================================================

class ZakatStabilizer:
    """
    Implémentation de la Zakāt comme stabilisateur automatique
    """
    
    def __init__(self, zakat_rate: float = 0.025):
        self.zakat_rate = zakat_rate
        self.history = []
    
    def apply_zakat(self, money_supply: float, new_emission: float, credit_flow: float) -> float:
        """
        M_{t+1} = M_t - τ * M_t + ΔE_t + ΔC_t
        """
        M_next = money_supply * (1 - self.zakat_rate) + new_emission + credit_flow
        self.history.append({
            'M_t': money_supply,
            'zakat_collected': money_supply * self.zakat_rate,
            'new_emission': new_emission,
            'credit_flow': credit_flow,
            'M_next': M_next
        })
        return M_next
    
    def simulate_cycle(self, initial_supply: float, n_periods: int,
                       emissions: list[float], credits: list[float]) -> list[float]:
        """
        Simule plusieurs périodes
        """
        M = initial_supply
        trajectory = [M]
        
        for t in range(n_periods):
            E = emissions[t] if t < len(emissions) else 0
            C = credits[t] if t < len(credits) else 0
            M = self.apply_zakat(M, E, C)
            trajectory.append(M)
        
        return trajectory


# ===================================================
# MODULE 7: COMPARAISON EMPIRIQUE
# ===================================================

@dataclass
class ComplementaryCurrency:
    """Structure pour les monnaies complémentaires"""
    name: str
    velocity: float          # Taux de rotation
    coverage: float          # Couverture des échanges (0-1)
    members: int
    default_rate: float      # Taux de défaut implicite

class EmpiricalComparison:
    """
    Comparaison des systèmes de monnaie complémentaire
    """
    
    def __init__(self):
        # Données issues du tableau comparatif
        self.currencies = {
            'Bristol_Pound': ComplementaryCurrency(
                name='Bristol Pound',
                velocity=0.2,
                coverage=0.05,
                members=2000,
                default_rate=0.0
            ),
            'WIR': ComplementaryCurrency(
                name='WIR (Switzerland)',
                velocity=1.5,
                coverage=0.35,
                members=60000,
                default_rate=0.01
            ),
            'Sardex': ComplementaryCurrency(
                name='Sardex (Sardinia)',
                velocity=0.8,
                coverage=0.175,
                members=4000,
                default_rate=0.065
            )
        }
    
    def get_currency_data(self, name: str) -> ComplementaryCurrency:
        return self.currencies.get(name)
    
    def compare_efficiency(self) -> Dict[str, Dict[str, float]]:
        """
        Calcule des métriques d'efficacité pour chaque système
        """
        results = {}
        for name, currency in self.currencies.items():
            # Métrique: Efficacité = (vélocité * couverture) / (1 + taux_defaut)
            efficiency = (currency.velocity * currency.coverage) / (1 + currency.default_rate)
            results[name] = {
                'efficiency': efficiency,
                'velocity': currency.velocity,
                'coverage': currency.coverage,
                'default_rate': currency.default_rate
            }
        return results


# ===================================================
# MODULE 8: MODÉLISATION DU CAS PILOTE (LIBAN)
# ===================================================

class PilotSimulation:
    """
    Simulation du cas pilote au Liban (Zone de Dora)
    """
    
    def __init__(self, initial_money_supply: float = 1_000_000,
                 n_enterprises: int = 1000):
        self.initial_supply = initial_money_supply
        self.n_enterprises = n_enterprises
        self.zakat = ZakatStabilizer()
        
    def simulate_12months(self) -> Dict[str, float]:
        """
        Simulation sur 12 mois
        """
        M = self.initial_supply
        velocity = 2.5
        credit_cumulative = 0
        savings = 200_000
        dollar_usage = 0.8
        
        monthly_data = []
        
        for month in range(12):
            # Croissance de l'émission (adoption progressive)
            new_emission = 50_000 * (1 - np.exp(-month/6))
            
            # Croissance du crédit
            credit_flow = 25_000 * (1 - np.exp(-month/4))
            credit_cumulative += credit_flow
            
            # Application de la Zakāt
            M = self.zakat.apply_zakat(M, new_emission, credit_flow)
            
            # Évolution de la vélocité
            velocity = 2.5 + 1.3 * (1 - np.exp(-month/8))
            
            # Évolution de l'épargne
            savings = 200_000 + 150_000 * (1 - np.exp(-month/6))
            
            # Baisse de l'usage du dollar
            dollar_usage = 0.8 * np.exp(-month/12)
            
            monthly_data.append({
                'month': month + 1,
                'money_supply': M,
                'velocity': velocity,
                'credit_cumulative': credit_cumulative,
                'savings': savings,
                'dollar_usage': dollar_usage
            })
        
        # Résultats finaux
        return {
            'final_money_supply': M,
            'final_velocity': velocity,
            'total_credit': credit_cumulative,
            'final_savings': savings,
            'final_dollar_usage': dollar_usage,
            'monthly_data': monthly_data
        }


# ===================================================
# MODULE 9: EXEMPLE D'UTILISATION ET TESTS
# ===================================================

def run_demonstration():
    """
    Démonstration complète du système
    """
    
    print("=" * 60)
    print("SYSTÈME MONÉTAIRE INTÉGRÉ - DÉMONSTRATION")
    print("=" * 60)
    
    # 1. Test de l'étalon intégré
    print("\n1. ÉTALON MONÉTAIRE INTÉGRÉ")
    print("-" * 40)
    
    params = MonetaryParams(
        wealth_real=1000,
        confidence=0.75,
        time_horizon=10
    )
    standard = IntegratedStandard(params)
    M = standard.money_supply()
    print(f"Masse monétaire (M) = {M:.2f}")
    print(f"Effets marginaux: {standard.marginal_effects()}")
    
    # 2. Test du système bimétallique
    print("\n2. SYSTÈME BIMÉTALLIQUE")
    print("-" * 40)
    
    reserves = BimetallicReserves(
        gold_grams=10000,
        silver_grams=50000,
        gold_price_usd=62.0,    # ~1950 USD/oz ≈ 62 USD/g
        silver_price_usd=0.85,  # ~26 USD/oz ≈ 0.85 USD/g
        basket_weight_gold=0.6
    )
    bimetal = BimetallicStandard(reserves, price_level=1.0)
    M_bimetal = bimetal.money_supply()
    print(f"Masse monétaire bimétallique = {M_bimetal:.2f} USD")
    print(f"Variance du portefeuille = {bimetal.variance_analysis(0.15, 0.25, 0.3):.2f}")
    
    # 3. Test du Crypto-Fulus
    print("\n3. CRYPTO-FULUS (LBP-T)")
    print("-" * 40)
    
    crypto_params = CryptoFulusParams(
        reserves_gold_g=10000,
        reserves_silver_g=50000,
        price_gold_usd=62.0,
        price_silver_usd=0.85,
        target_price=1.0
    )
    crypto = CryptoFulus(crypto_params)
    print(f"Valeur unitaire LBP-T = {crypto.unit_value():.4f}")
    print(f"Émission pour +100g or = {crypto.new_emission(100, 0):.2f} LBP-T")
    
    # 4. Test du détour blockchain
    print("\n4. COÛT DU DÉTOUR BLOCKCHAIN")
    print("-" * 40)
    
    bc_params = BlockchainParams(
        base_cost=0.01,
        energy_consumed=0.1,
        tx_per_block=2000,
        finality_blocks=6,
        block_frequency=60,
        energy_price=0.05,
        opportunity_cost=2.0
    )
    detour = BlockchainDetour(bc_params)
    C_tx = detour.transaction_cost()
    print(f"Coût d'une transaction blockchain = ${C_tx:.4f}")
    
    risk_analysis = detour.risk_adjusted_cost(
        risk_central=0.5,  # R élevé au Liban
        risk_blockchain=0.1
    )
    print(f"Efficacité du détour: {risk_analysis['is_efficient']}")
    print(f"Économie par transaction: ${risk_analysis.get('saving', 0):.4f}")
    
    # 5. Test de la gouvernance PoSS
    print("\n5. PROOF OF SOCIAL STAKE (PoSS)")
    print("-" * 40)
    
    members = [
        Member(1, 1000, 365, 85, 90),
        Member(2, 500, 200, 70, 75),
        Member(3, 1500, 100, 60, 80),
        Member(4, 200, 50, 40, 50),
        Member(5, 800, 300, 95, 95),
    ]
    
    consensus = SocialStakeConsensus(members)
    weights = consensus.get_all_weights()
    for member_id, weight in weights.items():
        print(f"Membre {member_id}: poids = {weight:.4f}")
    
    proposer = consensus.select_proposer()
    print(f"Proposant sélectionné: Membre {proposer.id}")
    
    # 6. Test de la simulation du pilote
    print("\n6. SIMULATION DU PILOTE (LIBAN)")
    print("-" * 40)
    
    pilot = PilotSimulation()
    results = pilot.simulate_12months()
    print(f"Masse monétaire finale: {results['final_money_supply']:.0f} LBP-T")
    print(f"Vélocité finale: {results['final_velocity']:.2f}")
    print(f"Crédit Mudaraba cumulé: {results['total_credit']:.0f} LBP-T")
    print(f"Épargne finale: {results['final_savings']:.0f} LBP-T")
    print(f"Usage final du dollar: {results['final_dollar_usage']*100:.1f}%")
    
    print("\n" + "=" * 60)
    print("FIN DE LA DÉMONSTRATION")
    print("=" * 60)
    
    return {
        'integrated_standard': standard,
        'bimetallic': bimetal,
        'crypto': crypto,
        'detour': detour,
        'consensus': consensus,
        'pilot': pilot
    }


if __name__ == "__main__":
    results = run_demonstration()
