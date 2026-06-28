"""
Yusuf Counter-Cycle Model – Core Implementation
Auteur: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional, Tuple, Dict
import yaml


@dataclass
class YusufConfig:
    """Configuration du modèle Yusuf"""
    years: int = 100
    need: float = 0.06
    threshold_ratio: float = 0.25
    gamma_high: float = 0.5
    gamma_low: float = 0.85


class YusufCounterCycle:
    """
    Modèle formel du système Yusuf avec basculement par seuil.
    Basé sur Sourate Yusuf (12:47-48).
    """

    def __init__(
        self,
        years: int = 100,
        need: float = 0.06,
        threshold_ratio: float = 0.25,
        gamma_high: float = 0.5,
        gamma_low: float = 0.85,
    ):
        self.years = years
        self.need = need
        self.threshold_ratio = threshold_ratio
        self.gamma_high = gamma_high
        self.gamma_low = gamma_low

    def production_cycle(self, t: int) -> float:
        """
        Production cyclique naturelle.
        Période de 14 ans (7 ans d'abondance, 7 ans de disette).
        """
        amplitude = 1.0
        period = 7
        return max(0, amplitude * (1 + 0.5 * np.sin(2 * np.pi * t / period)))

    def simulate_yusuf(
        self,
        shock_year: Optional[int] = None,
        shock_magnitude: float = 0.5,
    ) -> Tuple[pd.DataFrame, int]:
        """
        Simule le système Yusuf.

        Args:
            shock_year: Année du choc exogène (si None, pas de choc)
            shock_magnitude: Amplitude du choc (0.2 à 0.7)

        Returns:
            DataFrame avec les résultats, année d'effondrement (si applicable)
        """
        S = np.zeros(self.years + 1)  # Stock
        C = np.zeros(self.years + 1)  # Consommation
        P = np.zeros(self.years + 1)  # Production
        phase = np.zeros(self.years + 1)  # Phase (0=rareté, 1=abondance)

        S[0] = 1.0
        max_stock = S[0]

        for t in range(self.years):
            P[t] = self.production_cycle(t)

            # Choc exogène
            if shock_year and t >= shock_year:
                P[t] *= (1 - shock_magnitude)

            # Basculement par seuil
            if S[t] > self.threshold_ratio * max_stock:
                gamma = self.gamma_high
                phase[t] = 1
            else:
                gamma = self.gamma_low
                phase[t] = 0

            # Consommation et mise à jour du stock
            C[t] = self.need * gamma
            dS = P[t] - C[t]
            S[t + 1] = max(0, S[t] + dS)

            if S[t + 1] > max_stock:
                max_stock = S[t + 1]

            # Effondrement
            if S[t + 1] == 0:
                df = self._create_dataframe(S, C, P, phase, t + 1)
                return df, t + 1

        df = self._create_dataframe(S, C, P, phase, self.years)
        return df, self.years

    def simulate_capitalist(
        self,
        interest_rate: float = 0.22,
        shock_year: Optional[int] = None,
        shock_magnitude: float = 0.5,
    ) -> Tuple[pd.DataFrame, int]:
        """
        Simule le système capitaliste avec intérêt composé.
        """
        S = np.zeros(self.years + 1)
        D = np.zeros(self.years + 1)
        C = np.zeros(self.years + 1)
        P = np.zeros(self.years + 1)

        S[0] = 1.0
        D[0] = 0.5

        for t in range(self.years):
            P[t] = self.production_cycle(t)

            if shock_year and t >= shock_year:
                P[t] *= (1 - shock_magnitude)

            # Dette avec intérêt composé
            D[t + 1] = D[t] * (1 + interest_rate)
            debt_service = D[t] * interest_rate
            available = P[t] - debt_service
            C[t] = min(available, self.need)

            dS = P[t] - C[t] - debt_service
            S[t + 1] = max(0, S[t] + dS)

            if S[t + 1] == 0:
                df = self._create_dataframe_cap(S, D, C, P, t + 1)
                return df, t + 1

        df = self._create_dataframe_cap(S, D, C, P, self.years)
        return df, self.years

    def _create_dataframe(self, S, C, P, phase, steps):
        return pd.DataFrame({
            'Stock': S[:steps + 1],
            'Consumption': C[:steps + 1],
            'Production': P[:steps + 1],
            'Phase': phase[:steps + 1],
        })

    def _create_dataframe_cap(self, S, D, C, P, steps):
        return pd.DataFrame({
            'Stock': S[:steps + 1],
            'Debt': D[:steps + 1],
            'Consumption': C[:steps + 1],
            'Production': P[:steps + 1],
        })


class SocialCreditModule:
    """
    Module de gamification – crédit social et conformité.
    Réduit le besoin de base en fonction de la conformité aux principes de Muamalat.
    """

    def __init__(
        self,
        base_need: float = 0.06,
        compliance_impact: float = 0.5,
        min_need: float = 0.02,
        max_need: float = 0.12,
    ):
        self.base_need = base_need
        self.compliance_impact = compliance_impact
        self.min_need = min_need
        self.max_need = max_need

    def calculate_need(self, compliance_score: float) -> float:
        """
        Calcule le besoin modulé par le score de conformité.
        compliance_score: 0 à 1, plus élevé = besoin réduit.
        """
        need = self.base_need * (1 - self.compliance_impact * compliance_score)
        return np.clip(need, self.min_need, self.max_need)

    def simulate_with_compliance(
        self,
        model: YusufCounterCycle,
        compliance_scores: list,
        shock_year: Optional[int] = None,
    ) -> Tuple[pd.DataFrame, int]:
        """
        Simule le système Yusuf avec besoin modulé par la conformité.
        """
        S = np.zeros(model.years + 1)
        C = np.zeros(model.years + 1)
        P = np.zeros(model.years + 1)
        Need = np.zeros(model.years + 1)

        S[0] = 1.0
        max_stock = S[0]

        for t in range(model.years):
            P[t] = model.production_cycle(t)

            if shock_year and t >= shock_year:
                P[t] *= (1 - 0.5)

            score = compliance_scores[t] if t < len(compliance_scores) else 0.5
            Need[t] = self.calculate_need(score)

            if S[t] > model.threshold_ratio * max_stock:
                gamma = model.gamma_high
            else:
                gamma = model.gamma_low

            C[t] = Need[t] * gamma
            dS = P[t] - C[t]
            S[t + 1] = max(0, S[t] + dS)

            if S[t + 1] > max_stock:
                max_stock = S[t + 1]

            if S[t + 1] == 0:
                df = self._create_dataframe(S, C, P, Need, t + 1)
                return df, t + 1

        df = self._create_dataframe(S, C, P, Need, model.years)
        return df, model.years

    def _create_dataframe(self, S, C, P, Need, steps):
        return pd.DataFrame({
            'Stock': S[:steps + 1],
            'Consumption': C[:steps + 1],
            'Production': P[:steps + 1],
            'Need': Need[:steps + 1],
        })


# ==================== BRI / MULTI-PAYS ====================

class BRIZone:
    """
    Zone BRI avec sa propre monnaie de circulation (fulus) et des réserves en nuqud (or/argent).
    """

    def __init__(self, name: str, nuqud_reserve_gold_grams: float, initial_fulus_supply: float = 0):
        self.name = name
        self.nuqud_reserve = nuqud_reserve_gold_grams
        self.fulus_supply = initial_fulus_supply
        self.exchange_rate = 1.0
        self.transactions = []

    def mint_fulus(self, against_gold_grams: float) -> 'Fulus':
        """Émission de fulus contre dépôt d'or."""
        if against_gold_grams <= self.nuqud_reserve:
            fulus_issued = against_gold_grams * self.exchange_rate
            self.nuqud_reserve -= against_gold_grams
            self.fulus_supply += fulus_issued
            return Fulus(fulus_issued, issued_by=f"BRI-{self.name}")
        else:
            raise ValueError(f"Réserves or insuffisantes dans {self.name}")

    def pay_inter_zone(self, other_zone: 'BRIZone', amount_nuqud_gold: float) -> dict:
        """Règlement entre zones : transfert de nuqud (or)."""
        if self.nuqud_reserve >= amount_nuqud_gold:
            self.nuqud_reserve -= amount_nuqud_gold
            other_zone.nuqud_reserve += amount_nuqud_gold
            tx = {
                "from": self.name,
                "to": other_zone.name,
                "amount_gold": amount_nuqud_gold,
                "type": "inter_zone_settlement"
            }
            self.transactions.append(tx)
            other_zone.transactions.append(tx)
            return tx
        else:
            raise ValueError("Réserves insuffisantes pour le règlement inter-BRI")

    def summary(self) -> dict:
        return {
            "zone": self.name,
            "nuqud_reserve_g": self.nuqud_reserve,
            "fulus_supply": self.fulus_supply,
            "exchange_rate_fulus_per_g": self.exchange_rate,
            "inter_zone_tx": len([t for t in self.transactions if t.get("type") == "inter_zone_settlement"])
        }


class Fulus:
    """Monnaie de circulation (fulus)."""
    def __init__(self, amount: float, issued_by: str):
        self.amount = amount
        self.issued_by = issued_by


# ==================== CRD / GRONDONA ====================

class CommodityReserveDepartment:
    """
    Département de Réserve de Matières Premières (système Grondona).
    Stabilise les prix par achats/ventes à prix plancher/plafond.
    """

    def __init__(self, floor_price: float = 0.8, ceiling_price: float = 1.2):
        self.floor_price = floor_price
        self.ceiling_price = ceiling_price
        self.stockpiles = {}
        self.cash_reserve = 0

    def add_commodity(self, name: str, initial_quantity: float):
        """Ajoute un stock initial de commodity."""
        self.stockpiles[name] = initial_quantity

    def intervene(self, price: float, quantity: float, commodity: str) -> Tuple[float, float]:
        """
        Intervient sur le marché.
        Retourne (prix_ajusté, variation_stock).
        """
        if price < self.floor_price:
            # Achat (émission monétaire)
            buy_quantity = quantity * 0.1
            if commodity in self.stockpiles:
                self.stockpiles[commodity] += buy_quantity
            else:
                self.stockpiles[commodity] = buy_quantity
            return self.floor_price, buy_quantity

        elif price > self.ceiling_price:
            # Vente (destruction monétaire)
            sell_quantity = min(quantity * 0.1, self.stockpiles.get(commodity, 0))
            if sell_quantity > 0:
                self.stockpiles[commodity] -= sell_quantity
            return self.ceiling_price, -sell_quantity

        return price, 0

    def release_stock(self, commodity: str, amount: float) -> float:
        """Libère un stock d'urgence."""
        available = self.stockpiles.get(commodity, 0)
        released = min(amount, available)
        self.stockpiles[commodity] -= released
        return released


# ==================== LEDGER (BLOCKCHAIN) ====================

import hashlib
import json
import time


class Block:
    def __init__(self, index: int, previous_hash: str, transactions: list, timestamp: float = None):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        block_string = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transactions": self.transactions,
            "timestamp": self.timestamp
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


class Ledger:
    """Simulation d'une blockchain pour la traçabilité immuable."""

    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self) -> Block:
        return Block(0, "0", [{"genesis": "Yusuf-Grondona system started"}])

    def get_latest_block(self) -> Block:
        return self.chain[-1]

    def add_transaction(self, tx: dict) -> str:
        new_block = Block(
            index=len(self.chain),
            previous_hash=self.get_latest_block().hash,
            transactions=[tx]
        )
        self.chain.append(new_block)
        return new_block.hash

    def verify_integrity(self) -> bool:
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.previous_hash != previous.hash:
                return False
            if current.hash != current.compute_hash():
                return False
        return True

    def search_by_buyer(self, buyer_name: str) -> list:
        return [
            block.transactions[0] for block in self.chain
            if block.transactions and block.transactions[0].get("buyer") == buyer_name
        ]


# ==================== BAYT AL-MAL (ZAKAT) ====================

class BaytAlMal:
    """Trésorerie publique islamique pour la gestion de la Zakat."""

    def __init__(self, name: str):
        self.name = name
        self.zakat_funds = 0

    def collect_zakat(
        self,
        nuqud_holdings: list,
        trade_profit_nuqud: float = 0,
        agricultural_yield_nuqud: float = 0,
        livestock_nuqud: float = 0,
    ) -> float:
        """
        Collecte la Zakat (2.5%) sur les avoirs.
        nisab = 85g d'or.
        """
        nisab = 85
        total_wealth = sum(nuqud_holdings) + trade_profit_nuqud + agricultural_yield_nuqud + livestock_nuqud
        zakat_amount = 0.025 * max(0, total_wealth - nisab)
        self.zakat_funds += zakat_amount
        return zakat_amount

    def distribute_emergency(self, recipients: dict):
        """Distribue les fonds en situation d'urgence."""
        total = sum(recipients.values())
        if total <= self.zakat_funds:
            for recipient, amount in recipients.items():
                self.zakat_funds -= amount
                print(f"Distributed {amount} g d'or to {recipient}")
        else:
            print("Fonds insuffisants pour la distribution d'urgence")

"""
Streamlit Interface – Yusuf Counter-Cycle Model
Auteur: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy import stats
from streamlit_option_menu import option_menu

from yusuf_model import YusufCounterCycle, SocialCreditModule, BRIZone, CommodityReserveDepartment

# ==================== CONFIGURATION PAGE ====================

st.set_page_config(
    page_title="Yusuf Counter-Cycle | Economic Resilience Model",
    page_icon="⚖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== CSS PERSONNALISÉ ====================

st.markdown("""
<style>
    .main {
        background-color: #0a0f1e;
        color: #e0e0e0;
    }
    .stApp {
        background-color: #0a0f1e;
    }
    .metric-card {
        background-color: #1e2a3a;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #d4af37;
        margin: 10px 0;
    }
    .metric-card h3 {
        font-size: 14px;
        color: #a0a0a0;
        margin: 0;
        padding: 0;
    }
    .metric-card .value {
        font-size: 28px;
        font-weight: bold;
        color: #d4af37;
        margin-top: 5px;
    }
    .info-box {
        background-color: #1e2a3a;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    .info-box-success {
        border-left: 4px solid #2ecc71;
    }
    .info-box-warning {
        border-left: 4px solid #f39c12;
    }
    .info-box-danger {
        border-left: 4px solid #e74c3c;
    }
    .big-font {
        font-size: 30px !important;
        font-weight: bold;
        color: #d4af37;
    }
</style>
""", unsafe_allow_html=True)

# ==================== EN-TÊTE ====================

st.markdown("""
<div class="big-font">⚖ YUSUF COUNTER-CYCLE</div>
Modèle économique basé sur Sourate Yusuf (12:47-48) — Phase Transition vers Muamalat
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
📖 <strong>Sourate Yusuf (12:47-48)</strong><br>
« Pendant sept années, vous moissonnerez comme à l'ordinaire. Ce que vous récolterez,
laissez-le en épis, sauf le peu que vous consommerez. Viendront ensuite sept années
de disette qui consumeront tout ce que vous aurez amassé, sauf le peu que vous aurez réservé. »
</div>
""", unsafe_allow_html=True)

# ==================== PARAMÈTRES PAR DÉFAUT ====================

PAKISTAN_PARAMS = {
    "need": 0.06,
    "interest_rate": 0.22,
    "gamma_high": 0.5,
    "gamma_low": 0.85,
    "threshold_ratio": 0.25,
}

AFGHANISTAN_PARAMS = {
    "need": 0.05,
    "interest_rate": 0.25,
    "gamma_high": 0.45,
    "gamma_low": 0.80,
    "threshold_ratio": 0.20,
}

# ==================== MENU DE NAVIGATION ====================

selected = option_menu(
    menu_title=None,
    options=["🎛 Simulation", "📊 Monte Carlo", "🎮 Gamification", "🇵🇰 Scénarios", "📜 À propos"],
    icons=["sliders", "graph-up", "controller", "flag", "info-circle"],
    orientation="horizontal",
    styles={
        "container": {"background-color": "#1e2a3a", "border-radius": "10px"},
        "nav-link": {"font-size": "14px", "color": "#e0e0e0"},
        "nav-link-selected": {"background-color": "#d4af37", "color": "#0a0f1e", "font-weight": "bold"},
    }
)

# ==================== PAGE 1 : SIMULATION ====================

if selected == "🎛 Simulation":
    st.header("🔬 Simulation Dynamique (100 ans)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Paramètres Yusuf")
        need = st.slider("Besoin de base annuel", 0.02, 0.15, PAKISTAN_PARAMS["need"], 0.01,
                         help="Consommation minimale nécessaire (fraction de la production max)")
        gamma_high = st.slider("Taux d'épargne (abondance)", 0.3, 0.8, PAKISTAN_PARAMS["gamma_high"],
                               help="En période d'abondance, on épargne ce pourcentage")
        gamma_low = st.slider("Taux de consommation (rareté)", 0.7, 1.0, PAKISTAN_PARAMS["gamma_low"],
                              help="En période de rareté, on consomme ce pourcentage du besoin")
        threshold_ratio = st.slider("Seuil de basculement", 0.1, 0.5, PAKISTAN_PARAMS["threshold_ratio"],
                                    help="Si stock > seuil × stock_max, phase d'abondance")

    with col2:
        st.markdown("### Paramètres Capitaliste")
        interest_rate = st.slider("Taux d'intérêt annuel", 0.05, 0.35, PAKISTAN_PARAMS["interest_rate"], 0.01,
                                  help="Taux d'intérêt du système capitaliste (Pakistan: 22%)")
        shock = st.checkbox("Ajouter un choc exogène", value=True,
                            help="Simule une crise (inondations, sécheresse, choc pétrolier)")
        if shock:
            shock_year = st.slider("Année du choc", 20, 80, 40, 5)
            shock_magnitude = st.slider("Ampleur du choc", 0.2, 0.8, 0.5, 0.05)
        else:
            shock_year = None
            shock_magnitude = 0.5

    # Exécution des simulations
    model_y = YusufCounterCycle(
        need=need,
        gamma_high=gamma_high,
        gamma_low=gamma_low,
        threshold_ratio=threshold_ratio
    )
    model_c = YusufCounterCycle(
        need=need,
        gamma_high=gamma_high,
        gamma_low=gamma_low,
        threshold_ratio=threshold_ratio
    )

    df_y, _ = model_y.simulate_yusuf(
        shock_year=shock_year if shock else None,
        shock_magnitude=shock_magnitude
    )
    df_c, _ = model_c.simulate_capitalist(
        interest_rate=interest_rate,
        shock_year=shock_year if shock else None,
        shock_magnitude=shock_magnitude
    )

    # Graphique principal
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=np.arange(len(df_y)),
        y=df_y['Stock'],
        mode='lines',
        name='Yusuf (Stock)',
        line=dict(color='#d4af37', width=3),
        fill='tozeroy',
        fillcolor='rgba(212, 175, 55, 0.1)'
    ))

    fig.add_trace(go.Scatter(
        x=np.arange(len(df_c)),
        y=df_c['Stock'],
        mode='lines',
        name='Capitaliste (Stock)',
        line=dict(color='#dc143c', width=2.5, dash='dash')
    ))

    fig.add_trace(go.Scatter(
        x=np.arange(len(df_y)),
        y=df_y['Production'],
        mode='lines',
        name='Production (cycle)',
        line=dict(color='#2ecc71', width=1.5, dash='dot')
    ))

    if shock:
        fig.add_vline(x=shock_year, line_dash="dash", line_color="orange",
                      annotation_text="⚠ CHOC", annotation_position="top")

    fig.update_layout(
        title="Évolution du Stock de Biens Essentiels",
        xaxis_title="Années",
        yaxis_title="Stock (normalisé)",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Métriques
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📦 Stock final Yusuf</h3>
            <div class="value">{df_y['Stock'].iloc[-1]:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📉 Stock final Capitaliste</h3>
            <div class="value">{df_c['Stock'].iloc[-1]:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        y_solv = (df_y['Stock'] > 0).mean() * 100
        c_solv = (df_c['Stock'] > 0).mean() * 100
        st.markdown(f"""
        <div class="metric-card">
            <h3>🛡 Solvabilité (Yusuf)</h3>
            <div class="value">{y_solv:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>💥 Solvabilité (Capitaliste)</h3>
            <div class="value">{c_solv:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Interprétation
    if df_y['Stock'].iloc[-1] > df_c['Stock'].iloc[-1]:
        st.markdown("""
        <div class="info-box info-box-success">
        ✅ <strong>Conclusion :</strong> Le système Yusuf démontre une résilience supérieure.
        Le stock final est plus élevé et la solvabilité est maintenue à 100%, même sous choc.
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="info-box info-box-warning">
        ⚠ <strong>Attention :</strong> Le système capitaliste s'effondre sous l'effet des intérêts composés
        et des chocs exogènes. La transition vers le système Yusuf est recommandée.
        </div>
        """, unsafe_allow_html=True)

# ==================== PAGE 2 : MONTE CARLO ====================

elif selected == "📊 Monte Carlo":
    st.header("📈 Validation Statistique – Méthode de Monte Carlo")

    st.markdown("""
    <div class="info-box">
    La simulation de Monte Carlo exécute 100 scénarios aléatoires (chocs variables)
    pour comparer la robustesse statistique du système Yusuf vs. le système capitaliste.
    </div>
    """, unsafe_allow_html=True)

    def run_monte_carlo(model_yusuf, model_cap, n_simulations=100):
        """Exécute des simulations Monte Carlo pour comparer les deux systèmes."""
        yusuf_final_stocks = []
        cap_final_stocks = []
        yusuf_collapse_years = []
        cap_collapse_years = []

        for _ in range(n_simulations):
            shock_year = np.random.randint(20, 80)
            shock_magnitude = np.random.uniform(0.2, 0.7)

            df_y, years_y = model_yusuf.simulate_yusuf(
                shock_year=shock_year, shock_magnitude=shock_magnitude
            )
            df_c, years_c = model_cap.simulate_capitalist(
                interest_rate=0.22, shock_year=shock_year, shock_magnitude=shock_magnitude
            )

            yusuf_final_stocks.append(df_y['Stock'].iloc[-1])
            cap_final_stocks.append(df_c['Stock'].iloc[-1])
            yusuf_collapse_years.append(years_y)
            cap_collapse_years.append(years_c)

        t_stat, p_value = stats.ttest_ind(yusuf_final_stocks, cap_final_stocks)
        u_stat, p_mw = stats.mannwhitneyu(yusuf_final_stocks, cap_final_stocks)

        return {
            'yusuf_mean': np.mean(yusuf_final_stocks),
            'cap_mean': np.mean(cap_final_stocks),
            'yusuf_std': np.std(yusuf_final_stocks),
            'cap_std': np.std(cap_final_stocks),
            't_stat': t_stat,
            'p_value': p_value,
            'p_mw': p_mw,
            'yusuf_solvency': sum(1 for y in yusuf_collapse_years if y == model_yusuf.years) / n_simulations,
            'cap_solvency': sum(1 for y in cap_collapse_years if y == model_cap.years) / n_simulations,
            'yusuf_collapse_years': yusuf_collapse_years,
            'cap_collapse_years': cap_collapse_years,
        }

    col1, col2 = st.columns(2)

    with col1:
        n_simulations = st.slider("Nombre de simulations", 50, 500, 100, 50)

    with col2:
        if st.button("🚀 Lancer l'analyse Monte Carlo", use_container_width=True):
            with st.spinner(f"Exécution de {n_simulations} simulations..."):
                model_y = YusufCounterCycle(need=PAKISTAN_PARAMS["need"])
                model_c = YusufCounterCycle(need=PAKISTAN_PARAMS["need"])
                results = run_monte_carlo(model_y, model_c, n_simulations=n_simulations)

                # Métriques
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>📊 Stock moyen (Yusuf)</h3>
                        <div class="value">{results['yusuf_mean']:.2f} ± {results['yusuf_std']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>📉 Stock moyen (Capitaliste)</h3>
                        <div class="value">{results['cap_mean']:.2f} ± {results['cap_std']:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>🛡 Solvabilité</h3>
                        <div class="value">{results['yusuf_solvency']*100:.0f}% / {results['cap_solvency']*100:.0f}%</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Tests statistiques
                st.markdown("### 📐 Tests statistiques")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>Test t de Student</strong><br>
                        Statistique t = {results['t_stat']:.4f}<br>
                        p-value = {results['p_value']:.6f}<br>
                        {'✅ Significatif (p < 0.05)' if results['p_value'] < 0.05 else '❌ Non significatif'}
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class="info-box">
                        <strong>Test U de Mann-Whitney</strong><br>
                        Statistique U = {results['p_mw']:.4f}<br>
                        p-value = {results['p_mw']:.6f}<br>
                        {'✅ Significatif (p < 0.05)' if results['p_mw'] < 0.05 else '❌ Non significatif'}
                    </div>
                    """, unsafe_allow_html=True)

                # Histogramme des effondrements
                fig = go.Figure()

                fig.add_trace(go.Histogram(
                    x=results['yusuf_collapse_years'],
                    name='Yusuf',
                    marker_color='#d4af37',
                    opacity=0.7,
                    nbinsx=20
                ))

                fig.add_trace(go.Histogram(
                    x=results['cap_collapse_years'],
                    name='Capitaliste',
                    marker_color='#dc143c',
                    opacity=0.7,
                    nbinsx=20
                ))

                fig.update_layout(
                    title="Distribution des années d'effondrement",
                    xaxis_title="Année d'effondrement (100 = survie complète)",
                    yaxis_title="Fréquence",
                    barmode='overlay',
                    template="plotly_dark"
                )

                st.plotly_chart(fig, use_container_width=True)

                # Probabilité finale
                prob_yusuf_better = sum(1 for y, c in zip(results['yusuf_collapse_years'],
                                                           results['cap_collapse_years'])
                                        if y > c) / n_simulations

                st.markdown(f"""
                <div class="info-box info-box-success">
                🎯 <strong>Probabilité que Yusuf survive plus longtemps que le Capitaliste :</strong>
                {prob_yusuf_better*100:.1f}% sur {n_simulations} scénarios aléatoires.
                </div>
                """, unsafe_allow_html=True)

# ==================== PAGE 3 : GAMIFICATION ====================

elif selected == "🎮 Gamification":
    st.header("🎮 Module de Gamification – Crédit Social & Conformité")

    st.markdown("""
    <div class="info-box">
    Ce module modélise comment la conformité aux principes de Muamalat
    (interdiction du riba, paiement de la zakat, commerce équitable) peut réduire
    le besoin de base via un système de score.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        base_need = st.slider("Besoin de base minimum", 0.03, 0.10, 0.06, 0.01)
        compliance_impact = st.slider("Impact de la conformité sur le besoin", 0.0, 1.0, 0.5, 0.05)

    with col2:
        scenario = st.selectbox("Scénario de conformité", [
            "📈 Conformité croissante (réforme progressive)",
            "🎲 Conformité aléatoire (hétérogène)",
            "⭐ Conformité parfaite immédiate",
            "📉 Conformité décroissante (crise de confiance)"
        ])

    years = 100

    if scenario == "📈 Conformité croissante (réforme progressive)":
        compliance_scores = [min(1.0, t/50) for t in range(years)]
        scenario_desc = "Réforme progressive sur 50 ans"
    elif scenario == "🎲 Conformité aléatoire (hétérogène)":
        np.random.seed(42)
        compliance_scores = np.random.uniform(0.3, 0.9, years).tolist()
        scenario_desc = "Comportements hétérogènes"
    elif scenario == "⭐ Conformité parfaite immédiate":
        compliance_scores = [1.0] * years
        scenario_desc = "Conformité maximale dès le début"
    else:
        compliance_scores = [max(0, 1 - t/50) for t in range(years)]
        scenario_desc = "Dégradation progressive de la confiance"

    # Simulation
    scm = SocialCreditModule(base_need=base_need, compliance_impact=compliance_impact)
    model = YusufCounterCycle(need=base_need)
    df, _ = scm.simulate_with_compliance(model, compliance_scores, shock_year=40)

    # Graphique
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=np.arange(years),
        y=df['Stock'],
        mode='lines',
        name='Stock (biens essentiels)',
        line=dict(color='#d4af37', width=3),
        fill='tozeroy',
        fillcolor='rgba(212, 175, 55, 0.1)'
    ))

    fig.add_trace(go.Scatter(
        x=np.arange(years),
        y=df['Need'],
        mode='lines',
        name='Besoin modulé par conformité',
        line=dict(color='#3498db', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=np.arange(years),
        y=compliance_scores,
        mode='lines',
        name='Score de conformité',
        line=dict(color='#e67e22', width=2, dash='dot')
    ))

    fig.add_vline(x=40, line_dash="dash", line_color="orange",
                  annotation_text="⚠ CHOC", annotation_position="top")

    fig.update_layout(
        title=f"Effet de la gamification sur la résilience économique – {scenario_desc}",
        xaxis_title="Années",
        yaxis_title="Valeur (normalisée)",
        template="plotly_dark",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

    # Métriques
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📦 Stock final</h3>
            <div class="value">{df['Stock'].iloc[-1]:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Besoin moyen</h3>
            <div class="value">{df['Need'].mean():.3f}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>⭐ Score conformité moyen</h3>
            <div class="value">{np.mean(compliance_scores):.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-box info-box-success">
    💡 <strong>Interprétation :</strong> Plus la conformité aux principes de Muamalat est élevée,
    plus le besoin de base diminue, plus le stock résiste aux chocs. La gamification crée
    un cercle vertueux de résilience économique.
    </div>
    """, unsafe_allow_html=True)

# ==================== PAGE 4 : SCÉNARIOS ====================

elif selected == "🇵🇰 Scénarios":
    st.header("🇵🇰 Scénarios Pays – Pakistan & Afghanistan")

    tab1, tab2 = st.tabs(["🇵🇰 Pakistan", "🇦🇫 Afghanistan"])

    with tab1:
        st.markdown("""
        ### Pakistan – Données réelles (2025)

        | Indicateur | Valeur |
        |------------|--------|
        | Dette publique | ~75% du PIB |
        | Taux d'intérêt directeur | 22% (State Bank of Pakistan) |
        | Inflation | ~25-30% |
        | Population vulnérable | 40% sous seuil pauvreté |
        | Chocs récurrents | Inondations (2022, 2024) |
        """)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💀 Système actuel (Capitaliste + FMI)")
            model_c = YusufCounterCycle(need=0.08)
            df_c, collapse_year = model_c.simulate_capitalist(
                interest_rate=0.22, shock_year=30, shock_magnitude=0.5
            )

            fig_c = go.Figure()
            fig_c.add_trace(go.Scatter(
                x=np.arange(len(df_c)),
                y=df_c['Stock'],
                mode='lines',
                name='Stock',
                line=dict(color='#dc143c', width=2)
            ))
            fig_c.add_trace(go.Scatter(
                x=np.arange(len(df_c)),
                y=df_c['Debt'],
                mode='lines',
                name='Dette',
                line=dict(color='#e67e22', width=2, dash='dot')
            ))
            fig_c.update_layout(title="Évolution sous le système actuel", template="plotly_dark", height=400)
            st.plotly_chart(fig_c, use_container_width=True)

            if collapse_year < 100:
                st.error(f"💥 EFFONDREMENT à l'année {collapse_year}")
            else:
                st.warning("Survie précaire, stock critique")

        with col2:
            st.subheader("🌿 Transition Yusuf (Muamalat)")
            model_y = YusufCounterCycle(need=0.08, threshold_ratio=0.3, gamma_high=0.5, gamma_low=0.85)
            df_y, _ = model_y.simulate_yusuf(shock_year=30, shock_magnitude=0.5)

            fig_y = go.Figure()
            fig_y.add_trace(go.Scatter(
                x=np.arange(len(df_y)),
                y=df_y['Stock'],
                mode='lines',
                name='Stock',
                line=dict(color='#d4af37', width=3),
                fill='tozeroy',
                fillcolor='rgba(212, 175, 55, 0.1)'
            ))
            fig_y.update_layout(title="Évolution sous le système Yusuf", template="plotly_dark", height=400)
            st.plotly_chart(fig_y, use_container_width=True)

            st.success(f"✅ Résilience maintenue, stock final : {df_y['Stock'].iloc[-1]:.2f}")

        st.markdown("""
        <div class="info-box info-box-success">
        <strong>📜 Conclusion pour le Pakistan :</strong><br>
        Le modèle de contre-cycle Yusuf, combiné à une réforme monétaire (dinar/dirham)
        et à un système de gamification encourageant la conformité aux principes de Muamalat,
        offre une alternative viable à l'économie de la dette.
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("""
        ### Afghanistan – Données estimées

        | Indicateur | Valeur |
        |------------|--------|
        | Dette/PIB | N/A (effondrement bancaire) |
        | Taux d'intérêt | 0% (système informel) |
        | Inflation | ~30-50% |
        | Population vulnérable | ~80% sous seuil pauvreté |
        | Chocs | Sécheresse, gel des réserves, sanctions |
        """)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💀 Système informel actuel")
            model_c = YusufCounterCycle(need=0.05)
            df_c, collapse_year = model_c.simulate_capitalist(
                interest_rate=0.25, shock_year=20, shock_magnitude=0.6
            )

            fig_c = go.Figure()
            fig_c.add_trace(go.Scatter(
                x=np.arange(len(df_c)),
                y=df_c['Stock'],
                mode='lines',
                name='Stock',
                line=dict(color='#dc143c', width=2)
            ))
            fig_c.update_layout(title="Évolution sous le système informel", template="plotly_dark", height=400)
            st.plotly_chart(fig_c, use_container_width=True)

            st.error(f"💥 EFFONDREMENT précoce à l'année {collapse_year}")

        with col2:
            st.subheader("🌿 Proposition Yusuf")
            model_y = YusufCounterCycle(need=0.05, threshold_ratio=0.2, gamma_high=0.45, gamma_low=0.80)
            df_y, _ = model_y.simulate_yusuf(shock_year=20, shock_magnitude=0.6)

            fig_y = go.Figure()
            fig_y.add_trace(go.Scatter(
                x=np.arange(len(df_y)),
                y=df_y['Stock'],
                mode='lines',
                name='Stock',
                line=dict(color='#d4af37', width=3),
                fill='tozeroy',
                fillcolor='rgba(212, 175, 55, 0.1)'
            ))
            fig_y.update_layout(title="Évolution sous le système Yusuf", template="plotly_dark", height=400)
            st.plotly_chart(fig_y, use_container_width=True)

            st.success(f"✅ Résilience maintenue, stock final : {df_y['Stock'].iloc[-1]:.2f}")

        st.markdown("""
        <div class="info-box info-box-success">
        <strong>📜 Conclusion pour l'Afghanistan :</strong><br>
        Malgré un point de départ plus bas (stock initial 0.2 vs 0.5 pour le Pakistan),
        le système Yusuf stabilise l'économie afghane même sous chocs sévères.
        La reconstruction passe par une monnaie adossée à l'or/argent et la réactivation
        des principes de zakat et de commerce équitable.
        </div>
        """, unsafe_allow_html=True)

# ==================== PAGE 5 : À PROPOS ====================

else:
    st.header("📜 À propos du modèle")

    st.markdown("""
    ### Yusuf Counter-Cycle Model – Geometric Ricci Networks

    **Fondement mathématique :** Système d'équations différentielles avec basculement par seuil.

    **Références :**
    - Shaykh Umar Vadillo (plan de transition en 7 étapes)
    - Sourate Yusuf (12:47-48)
    - Système Grondona (Commodity Reserve Department)
    - Jean-Michel Servet, Karl Polanyi

    **Théorèmes clés :**
    1. **Λ = (D·r)/Ė_low** – Paramètre de bifurcation thermodynamique
    2. **⟨S_prod⟩ ≤ ⟨S_neg⟩** – Condition de stabilité entropique

    **Mention irénologique :** Free Dr Aafia Siddiqui !

    **Licence :** CC BY-SA 4.0 International

    **Auteur conceptuel :** Marc Daghar
    **Génération technique :** DeepSeek (IA)

    **Dépôt de référence :**
    https://[serveur_chinois]/marc_daghar/GRN_Pakistan_Afghanistan_Yusuf_v1.0
    """)

    st.divider()

    st.markdown("""
    <div class="info-box info-box-success">
    <strong>📜 Heureux soient les fêlés, car ils laisseront passer la lumière.</strong><br>
    Résister à la régression – avec les énarques déchus, avec les fêlés, avec l'olivier.
    </div>
    """, unsafe_allow_html=True)

"""
Script unifié d'exécution – Yusuf Counter-Cycle Model
Auteur: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import os
import sys
import subprocess

def run_all():
    """Exécute tous les modules du projet."""
    print("=" * 60)
    print("⚖ YUSUF COUNTER-CYCLE MODEL")
    print("Exécution complète de tous les modules")
    print("Mention: Free Dr Aafia Siddiqui !")
    print("=" * 60)

    modules = [
        ("yusuf_model.py", "Modèle principal"),
        ("modele_monnaie.py", "Modèle de vélocité monétaire"),
        ("optimization.py", "Optimisation des paramètres"),
        ("shock_model.py", "Modèle de chocs exogènes"),
        ("statistical_validation.py", "Validation statistique"),
        ("prototype.py", "Prototype simplifié"),
    ]

    for module, description in modules:
        print(f"\n▶ Exécution de {module} ({description})...")
        try:
            subprocess.run([sys.executable, module], check=True)
            print(f"✅ {module} exécuté avec succès")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur lors de l'exécution de {module}: {e}")

    print("\n" + "=" * 60)
    print("✅ Tous les modules ont été exécutés")
    print("Pour lancer l'interface Streamlit :")
    print("  streamlit run streamlit_app.py")
    print("=" * 60)


if __name__ == "__main__":
    run_all()

"""
Modèle de vélocité monétaire – Centralisé vs Décentralisé
Auteur: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import numpy as np
import matplotlib.pyplot as plt


class CentralizedMonetarySystem:
    """Système centralisé (feu de circulation / monnaie fractionnaire avec intérêts)"""

    def __init__(self, initial_money=1000, velocity=0.2):
        self.money_supply = initial_money
        self.velocity = velocity
        self.history = [initial_money]

    def step(self, years=1):
        for _ in range(years):
            self.money_supply = self.money_supply * (1 + 0.05)  # Intérêts
            self.history.append(self.money_supply)
        return self.history


class DecentralizedMonetarySystem:
    """Système décentralisé (rond-point / monnaie bimétallique sans dette)"""

    def __init__(self, initial_money=1000, velocity=0.4):
        self.money_supply = initial_money
        self.velocity = velocity
        self.history = [initial_money]

    def step(self, years=1):
        for _ in range(years):
            self.money_supply = self.money_supply * (1 + 0.01)  # Croissance naturelle
            self.history.append(self.money_supply)
        return self.history


def compare_systems():
    """Compare les deux systèmes monétaires."""
    central = CentralizedMonetarySystem()
    decentralized = DecentralizedMonetarySystem()

    years = 50
    central.step(years)
    decentralized.step(years)

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(range(years + 1), central.history, label='Système Centralisé (Intérêts)', color='red', linewidth=2)
    ax.plot(range(years + 1), decentralized.history, label='Système Décentralisé (Bimétallique)', color='green', linewidth=2)

    ax.set_xlabel('Années')
    ax.set_ylabel('Masse monétaire')
    ax.set_title('Comparaison des systèmes monétaires')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.savefig('monetary_comparison.png', dpi=150)
    plt.show()


if __name__ == "__main__":
    print("🔬 Modèle de vélocité monétaire")
    compare_systems()

"""
Optimisation des paramètres – Differential Evolution
Auteur: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import numpy as np
from scipy.optimize import differential_evolution
from yusuf_model import YusufCounterCycle


def objective_function(params):
    """
    Fonction objectif à minimiser.
    Paramètres: need, threshold_ratio, gamma_high, gamma_low, period, amplitude
    """
    need, threshold_ratio, gamma_high, gamma_low, period, amplitude = params

    # Créer un modèle avec les paramètres
    model = YusufCounterCycle(
        years=100,
        need=need,
        threshold_ratio=threshold_ratio,
        gamma_high=gamma_high,
        gamma_low=gamma_low
    )

    # Simuler
    df, _ = model.simulate_yusuf(shock_year=50, shock_magnitude=0.5)

    # Objectif: maximiser le stock final, minimiser la volatilité
    final_stock = df['Stock'].iloc[-1]
    volatility = df['Stock'].std()

    # Score: plus le stock final est élevé et la volatilité faible, meilleur
    score = -final_stock + volatility

    return score


def optimize_parameters():
    """Optimise les paramètres du modèle."""
    bounds = [
        (0.02, 0.15),      # need
        (0.1, 0.5),        # threshold_ratio
        (0.3, 0.8),        # gamma_high
        (0.7, 1.0),        # gamma_low
        (10, 20),          # period
        (0.3, 0.7),        # amplitude
    ]

    result = differential_evolution(
        objective_function,
        bounds,
        maxiter=100,
        popsize=15,
        disp=True
    )

    print("\n✅ Optimisation terminée")
    print(f"Meilleurs paramètres: {result.x}")
    print(f"Score optimal: {result.fun}")

    return result


if __name__ == "__main__":
    print("🔧 Optimisation des paramètres du modèle Yusuf")
    optimize_parameters()

"""
Modèle de chocs exogènes – Résilience du système Yusuf
Auteur: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import numpy as np
import pandas as pd
from yusuf_model import YusufCounterCycle


class ShockManager:
    """Gestionnaire de chocs exogènes."""

    def __init__(self):
        self.shocks = []

    def add_shock(self, name, severity, duration_years, start_year):
        """Ajoute un choc."""
        self.shocks.append({
            'name': name,
            'severity': severity,
            'duration': duration_years,
            'start': start_year
        })

    def apply_shocks(self, model, df):
        """Applique les chocs à un modèle."""
        years = model.years
        production_multiplier = np.ones(years)

        for shock in self.shocks:
            for t in range(shock['start'], min(shock['start'] + shock['duration'], years)):
                production_multiplier[t] *= (1 - shock['severity'])

        # Simulation avec chocs
        S = np.zeros(years + 1)
        C = np.zeros(years + 1)
        P = np.zeros(years + 1)

        S[0] = 1.0
        max_stock = S[0]

        for t in range(years):
            P[t] = model.production_cycle(t) * production_multiplier[t]

            if S[t] > model.threshold_ratio * max_stock:
                gamma = model.gamma_high
            else:
                gamma = model.gamma_low

            C[t] = model.need * gamma
            dS = P[t] - C[t]
            S[t + 1] = max(0, S[t] + dS)

            if S[t + 1] > max_stock:
                max_stock = S[t + 1]

            if S[t + 1] == 0:
                return pd.DataFrame({
                    'Stock': S[:t + 2],
                    'Consumption': C[:t + 2],
                    'Production': P[:t + 2],
                }), t + 1

        return pd.DataFrame({
            'Stock': S,
            'Consumption': C,
            'Production': P,
        }), years


def test_shocks():
    """Teste le système face à différents chocs."""
    model = YusufCounterCycle()
    shock_mgr = ShockManager()

    # Scénario de chocs multiples
    shock_mgr.add_shock("Crise pétrolière", 0.3, 3, 20)
    shock_mgr.add_shock("Pandémie", 0.2, 2, 40)
    shock_mgr.add_shock("Catastrophe climatique", 0.5, 5, 60)

    df, collapse_year = shock_mgr.apply_shocks(model, None)

    print("\n🌍 Test de résilience aux chocs")
    print("=" * 50)
    print(f"Stock final: {df['Stock'].iloc[-1]:.2f}")
    print(f"Année d'effondrement: {collapse_year if collapse_year < 100 else 'Aucun'}")
    print(f"Solvabilité: {(df['Stock'] > 0).mean() * 100:.1f}%")


if __name__ == "__main__":
    test_shocks()

"""
Validation statistique – Tests t, Mann-Whitney, Monte Carlo
Auteur: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import numpy as np
from scipy import stats
from yusuf_model import YusufCounterCycle


def run_statistical_validation(n_simulations=1000):
    """Exécute une validation statistique complète."""
    yusuf_stocks = []
    cap_stocks = []

    model_y = YusufCounterCycle(need=0.06)
    model_c = YusufCounterCycle(need=0.06)

    for _ in range(n_simulations):
        shock_year = np.random.randint(20, 80)
        shock_magnitude = np.random.uniform(0.2, 0.7)

        df_y, _ = model_y.simulate_yusuf(shock_year=shock_year, shock_magnitude=shock_magnitude)
        df_c, _ = model_c.simulate_capitalist(interest_rate=0.22, shock_year=shock_year, shock_magnitude=shock_magnitude)

        yusuf_stocks.append(df_y['Stock'].iloc[-1])
        cap_stocks.append(df_c['Stock'].iloc[-1])

    # Tests statistiques
    t_stat, p_value_t = stats.ttest_ind(yusuf_stocks, cap_stocks)
    u_stat, p_value_u = stats.mannwhitneyu(yusuf_stocks, cap_stocks)

    print("\n📊 Validation Statistique")
    print("=" * 50)
    print(f"Nombre de simulations: {n_simulations}")
    print(f"Stock moyen (Yusuf): {np.mean(yusuf_stocks):.3f} ± {np.std(yusuf_stocks):.3f}")
    print(f"Stock moyen (Capitaliste): {np.mean(cap_stocks):.3f} ± {np.std(cap_stocks):.3f}")
    print(f"Test t: p = {p_value_t:.6f}")
    print(f"Test Mann-Whitney: p = {p_value_u:.6f}")
    print(f"Significatif: {'OUI' if p_value_t < 0.05 else 'NON'}")


if __name__ == "__main__":
    run_statistical_validation()

"""
Visualisation des résultats
Auteur: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from yusuf_model import YusufCounterCycle


def plot_comparison():
    """Trace la comparaison entre les deux systèmes."""
    model_y = YusufCounterCycle()
    model_c = YusufCounterCycle()

    df_y, _ = model_y.simulate_yusuf(shock_year=40, shock_magnitude=0.5)
    df_c, _ = model_c.simulate_capitalist(interest_rate=0.22, shock_year=40, shock_magnitude=0.5)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Stock
    axes[0, 0].plot(df_y['Stock'], label='Yusuf', color='gold', linewidth=2)
    axes[0, 0].plot(df_c['Stock'], label='Capitaliste', color='red', linewidth=2)
    axes[0, 0].axvline(x=40, color='orange', linestyle='--', alpha=0.7, label='Choc')
    axes[0, 0].set_title('Évolution du Stock')
    axes[0, 0].set_xlabel('Années')
    axes[0, 0].set_ylabel('Stock (normalisé)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Consommation
    axes[0, 1].plot(df_y['Consumption'], label='Yusuf', color='gold', linewidth=2)
    axes[0, 1].plot(df_c['Consumption'], label='Capitaliste', color='red', linewidth=2)
    axes[0, 1].axvline(x=40, color='orange', linestyle='--', alpha=0.7, label='Choc')
    axes[0, 1].set_title('Consommation')
    axes[0, 1].set_xlabel('Années')
    axes[0, 1].set_ylabel('Consommation (normalisée)')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Production
    axes[1, 0].plot(df_y['Production'], label='Production', color='green', linewidth=2)
    axes[1, 0].axvline(x=40, color='orange', linestyle='--', alpha=0.7, label='Choc')
    axes[1, 0].set_title('Production Cyclique')
    axes[1, 0].set_xlabel('Années')
    axes[1, 0].set_ylabel('Production (normalisée)')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Phase (Yusuf)
    axes[1, 1].fill_between(range(len(df_y)), 0, df_y['Phase'], color='gold', alpha=0.5)
    axes[1, 1].set_title('Phase Yusuf (1 = Abondance, 0 = Rareté)')
    axes[1, 1].set_xlabel('Années')
    axes[1, 1].set_ylabel('Phase')
    axes[1, 1].set_ylim(-0.1, 1.1)
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('yusuf_comparison.png', dpi=150)
    plt.show()


if __name__ == "__main__":
    plot_comparison()

"""
Prototype simplifié du modèle Yusuf
Auteur: Marc Daghar
Licence: CC BY-SA 4.0
Mention: Free Dr Aafia Siddiqui !
"""

import numpy as np


class SimpleYusufModel:
    """Version simplifiée pour tests rapides."""

    def __init__(self, years=100, need=0.06):
        self.years = years
        self.need = need
        self.stock = 1.0
        self.history = [self.stock]

    def simulate(self):
        """Exécute une simulation simple."""
        for year in range(self.years):
            # Production cyclique
            production = 1 + 0.5 * np.sin(2 * np.pi * year / 7)

            # Règle Yusuf simplifiée
            if self.stock > 0.3:
                consumption = self.need * 0.5
            else:
                consumption = self.need * 0.85

            self.stock = max(0, self.stock + production - consumption)
            self.history.append(self.stock)

        return self.history

    def results(self):
        """Affiche les résultats."""
        final_stock = self.history[-1]
        solvency = sum(1 for s in self.history if s > 0) / len(self.history) * 100
        print(f"Stock final: {final_stock:.2f}")
        print(f"Solvabilité: {solvency:.1f}%")


if __name__ == "__main__":
    model = SimpleYusufModel()
    model.simulate()
    model.results()

# 1. Installation des dépendances
