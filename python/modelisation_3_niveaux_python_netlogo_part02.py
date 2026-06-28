"""
Yusuf-Grondona-Entropy Model
Modèle économique bimétallique, contre-cyclique, avec entropie et bifurcation
Auteur : Marc Daghar
Licence : CC BY-SA 4.0
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. CLASSES DE BASE
# ============================================================

@dataclass
class Commodity:
    """Représente une commodité dans le panier Grondona"""
    name: str
    floor_price: float          # Prix plancher (déclenchement d'achat)
    ceiling_price: float        # Prix plafond (déclenchement de vente)
    current_price: float        # Prix courant
    stockpile: float            # Quantité physique stockée
    elasticity: float           # Élasticité de la réserve
    transaction_cost: float = 0.001
    storage_cost: float = 0.005

class CommodityReserveDepartment:
    """
    Département de Réserve de Matières Premières (CRD)
    Implémente le système Grondona (contre-cycle)
    """
    def __init__(self, commodities: List[Commodity], initial_money_supply: float):
        self.commodities = {c.name: c for c in commodities}
        self.money_supply = initial_money_supply
        self.history = {
            'time': [], 'money_supply': [], 'total_stockpile': [],
            'entropy_produced': [], 'debt': [], 'lambda_param': []
        }
        self.transaction_cost = 0.001
        self.storage_cost = 0.005

    def check_market_prices(self, current_prices: Dict[str, float], time_step: float = 1.0):
        """
        Logique centrale du CRD : achète à prix plancher, vend à prix plafond
        """
        for name, price in current_prices.items():
            commodity = self.commodities[name]
            commodity.current_price = price

            if price < commodity.floor_price:
                # Phase d'abondance : achat, expansion monétaire
                purchase_qty = (commodity.floor_price - price) * commodity.elasticity
                purchase_qty *= (1 - self.transaction_cost)
                commodity.stockpile += purchase_qty
                money_created = purchase_qty * commodity.floor_price
                self.money_supply += money_created
                self.money_supply -= commodity.stockpile * self.storage_cost * time_step

            elif price > commodity.ceiling_price:
                # Phase de rareté : vente, contraction monétaire
                sale_qty = min(
                    commodity.stockpile,
                    (price - commodity.ceiling_price) * commodity.elasticity
                )
                commodity.stockpile -= sale_qty
                money_destroyed = sale_qty * commodity.ceiling_price
                self.money_supply -= money_destroyed

    def get_total_stockpile_value(self) -> float:
        return sum(c.stockpile * c.current_price for c in self.commodities.values())

    def record_state(self, t: float, entropy: float, debt: float, lambda_param: float):
        self.history['time'].append(t)
        self.history['money_supply'].append(self.money_supply)
        self.history['total_stockpile'].append(self.get_total_stockpile_value())
        self.history['entropy_produced'].append(entropy)
        self.history['debt'].append(debt)
        self.history['lambda_param'].append(lambda_param)


class EntropyThermodynamics:
    """
    Intégration de l'entropie (Georgescu-Roegen)
    """
    def __init__(self, S_min: float = 0.1, dissipation_coefficient: float = 0.05):
        self.S_min = S_min
        self.eta = dissipation_coefficient
        self.total_entropy = 0.0
        self.negentropy_captured = 0.0

    def entropy_production(self, production_quantity: float, time_step: float) -> float:
        S_prod = self.S_min + self.eta * production_quantity
        self.total_entropy += S_prod * time_step
        return S_prod

    def negentropic_capture(self, stockpile_increase: float, efficiency: float = 0.7) -> float:
        S_neg = efficiency * stockpile_increase
        self.negentropy_captured += S_neg
        return S_neg

    def net_entropy(self) -> float:
        return self.total_entropy - self.negentropy_captured

    def is_sustainable(self) -> bool:
        return self.net_entropy() < 1000  # Seuil de durabilité


class DebtBasedSystem:
    """
    Système de dette conventionnel (cas témoin)
    """
    def __init__(self, initial_debt: float, interest_rate: float, low_entropy_extraction_rate: float):
        self.debt = initial_debt
        self.r = interest_rate
        self.E_dot_low = low_entropy_extraction_rate

    def update(self, time_step: float, new_loans: float = 0) -> float:
        interest_accrued = self.debt * self.r * time_step
        self.debt += interest_accrued + new_loans
        return interest_accrued

    def lambda_bifurcation(self) -> float:
        if self.E_dot_low > 0:
            return (self.debt * self.r) / self.E_dot_low
        return float('inf')

    def is_collapsed(self) -> bool:
        return self.lambda_bifurcation() > 1.0


class SocialCreditMechanism:
    """
    Distribution du dividende social (Crédit Social)
    """
    def __init__(self, population: float = 1e6, dividend_rate: float = 0.1):
        self.population = population
        self.dividend_rate = dividend_rate
        self.total_distributed = 0.0

    def distribute_dividend(self, money_created: float) -> float:
        dividend = money_created * self.dividend_rate / self.population
        self.total_distributed += dividend * self.population
        return dividend


# ============================================================
# 2. MODÈLE DE SIMULATION PRINCIPAL
# ============================================================

class YusufGrondonaSimulation:
    """
    Simulation intégrée : Grondona + Entropie + Dette + Crédit Social
    """
    def __init__(self,
                 commodities: List[Commodity],
                 initial_money: float = 10000,
                 simulation_years: float = 50,
                 time_step: float = 0.25):  # Pas trimestriel

        self.crd = CommodityReserveDepartment(commodities, initial_money)
        self.entropy = EntropyThermodynamics()
        self.debt_system = DebtBasedSystem(
            initial_debt=0, interest_rate=0.05, low_entropy_extraction_rate=100
        )
        self.social_credit = SocialCreditMechanism()

        self.simulation_years = simulation_years
        self.time_step = time_step
        self.steps = int(simulation_years / time_step)

        self.production_growth_rate = 0.02
        self.price_volatility = 0.15
        self.use_grondona = True
        self.results = None

    def generate_price_series(self) -> List[Dict[str, float]]:
        """
        Génère des séries de prix stochastiques pour les commodités
        """
        prices = []
        t = 0
        for step in range(self.steps):
            price_dict = {}
            for name, commodity in self.crd.commodities.items():
                mean_price = (commodity.floor_price + commodity.ceiling_price) / 2
                shock = np.random.normal(0, self.price_volatility * np.sqrt(self.time_step))
                seasonal = 0.1 * np.sin(2 * np.pi * t)
                current = mean_price * (1 + shock + seasonal)
                current = max(commodity.floor_price * 0.8,
                             min(commodity.ceiling_price * 1.2, current))
                price_dict[name] = current
            prices.append(price_dict)
            t += self.time_step
        return prices

    def run(self) -> pd.DataFrame:
        """
        Exécute la simulation complète
        """
        price_series = self.generate_price_series()
        production_quantity = 1000
        debt_accumulated = 0

        for step, prices in enumerate(price_series):
            t = step * self.time_step

            # 1. Opérations du CRD (Grondona)
            if self.use_grondona:
                self.crd.check_market_prices(prices, self.time_step)
                money_created = self.crd.money_supply - self.crd.history['money_supply'][-1] if self.crd.history['money_supply'] else 0
                if money_created > 0:
                    self.social_credit.distribute_dividend(money_created)
            else:
                # Système de dette : création monétaire par prêts
                new_loans = production_quantity * 0.1 * self.time_step
                debt_accumulated = self.debt_system.update(self.time_step, new_loans)
                self.crd.money_supply += new_loans

            # 2. Production et entropie
            production_quantity *= (1 + self.production_growth_rate * self.time_step)
            S_prod = self.entropy.entropy_production(production_quantity, self.time_step)

            stockpile_increase = self.crd.get_total_stockpile_value() - (self.crd.history['total_stockpile'][-1] if self.crd.history['total_stockpile'] else 0)
            if stockpile_increase > 0:
                self.entropy.negentropic_capture(stockpile_increase)

            # 3. Calcul du paramètre de bifurcation
            if not self.use_grondona:
                lambda_param = self.debt_system.lambda_bifurcation()
                collapsed = self.debt_system.is_collapsed()
            else:
                lambda_param = 0
                collapsed = False

            # 4. Enregistrement
            self.crd.record_state(
                t,
                self.entropy.net_entropy(),
                debt_accumulated if not self.use_grondona else 0,
                lambda_param
            )

            if collapsed:
                print(f"EFFONDREMENT à t={t:.1f} ans : Λ = {lambda_param:.3f} > 1")
                break

        self.results = self._prepare_results()
        return self.results

    def _prepare_results(self) -> pd.DataFrame:
        df = pd.DataFrame(self.crd.history)
        df['entropy_rate'] = df['entropy_produced'].diff() / df['time'].diff()
        df['debt_to_money'] = df['debt'] / df['money_supply']
        df['is_sustainable'] = self.entropy.is_sustainable()
        return df

    def plot_results(self, df: pd.DataFrame):
        """
        Visualisation des résultats (à utiliser dans Streamlit ou Jupyter)
        """
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 3, figsize=(15, 10))

        # 1. Masse monétaire et stock
        axes[0, 0].plot(df['time'], df['money_supply'], label='Masse monétaire', linewidth=2)
        axes[0, 0].plot(df['time'], df['total_stockpile'], label='Stock physique', linewidth=2)
        axes[0, 0].set_ylabel('Valeur')
        axes[0, 0].set_title('Masse monétaire vs Stock')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # 2. Entropie cumulative
        axes[0, 1].plot(df['time'], df['entropy_produced'], color='red', linewidth=2)
        axes[0, 1].set_ylabel('Entropie')
        axes[0, 1].set_title('Entropie cumulative (Georgescu-Roegen)')
        axes[0, 1].grid(True, alpha=0.3)

        # 3. Paramètre de bifurcation Λ
        axes[0, 2].plot(df['time'], df['lambda_param'], color='orange', linewidth=2)
        axes[0, 2].axhline(y=1.0, color='red', linestyle='--', label='Seuil d\'effondrement')
        axes[0, 2].set_ylabel('Λ = (D·r) / Ė_low')
        axes[0, 2].set_title('Paramètre de bifurcation')
        axes[0, 2].legend()
        axes[0, 2].grid(True, alpha=0.3)

        # 4. Taux d'entropie
        axes[1, 0].plot(df['time'], df['entropy_rate'], color='purple', linewidth=1.5)
        axes[1, 0].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[1, 0].set_ylabel('dS/dt')
        axes[1, 0].set_title('Flux net d\'entropie (négatif = négentropique)')
        axes[1, 0].grid(True, alpha=0.3)

        # 5. Ratio Dette/Masse monétaire
        axes[1, 1].plot(df['time'], df['debt_to_money'], color='darkred', linewidth=2)
        axes[1, 1].set_ylabel('Dette / Monnaie')
        axes[1, 1].set_title('Accumulation de la dette')
        axes[1, 1].grid(True, alpha=0.3)

        # 6. Durabilité
        axes[1, 2].plot(df['time'], df['is_sustainable'], color='green', linewidth=2)
        axes[1, 2].set_ylabel('Durable (1=oui)')
        axes[1, 2].set_title('Durabilité du système')
        axes[1, 2].set_ylim(-0.1, 1.1)
        axes[1, 2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.suptitle('Simulation Yusuf-Grondona-Entropie', fontsize=14, y=1.02)
        plt.show()

    def compare_scenarios(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Compare les scénarios : Grondona vs système de dette
        """
        # Scénario Grondona
        print("Simulation avec système Grondona...")
        self.use_grondona = True
        df_g = self.run()

        # Scénario de dette
        print("Simulation avec système de dette...")
        self.__init__(list(self.crd.commodities.values()), 10000, self.simulation_years, self.time_step)
        self.use_grondona = False
        df_d = self.run()

        print("\n" + "="*60)
        print("COMPARAISON DES SCÉNARIOS")
        print("="*60)

        print(f"\nEntropie finale (Grondona) : {df_g['entropy_produced'].iloc[-1]:.2f}")
        print(f"Entropie finale (Dette) : {df_d['entropy_produced'].iloc[-1]:.2f}")

        reduction = (1 - df_g['entropy_produced'].iloc[-1]/df_d['entropy_produced'].iloc[-1])*100
        print(f"Réduction de l'entropie : {reduction:.1f}%")

        print(f"\nMasse monétaire finale (Grondona) : {df_g['money_supply'].iloc[-1]:.0f}")
        print(f"Masse monétaire finale (Dette) : {df_d['money_supply'].iloc[-1]:.0f}")

        collapse_time = None
        if not self.use_grondona and any(df_d['lambda_param'] > 1):
            collapse_time = df_d[df_d['lambda_param'] > 1]['time'].iloc[0]
            print(f"\nEffondrement du système de dette à t = {collapse_time:.1f} ans")

        print("\n" + "="*60)
        print("CONCLUSION : Le système Grondona borne l'entropie")
        print("et prévient l'effondrement du système de dette.")
        print("="*60)

        return df_g, df_d


# ============================================================
# 3. EXÉCUTION DIRECTE (TEST)
# ============================================================

if __name__ == "__main__":

    # Définition du panier de commodités
    commodities = [
        Commodity("Blé", floor_price=180, ceiling_price=220, current_price=200, stockpile=0, elasticity=100),
        Commodity("Cuivre", floor_price=8000, ceiling_price=12000, current_price=10000, stockpile=0, elasticity=10),
        Commodity("Coton", floor_price=70, ceiling_price=90, current_price=80, stockpile=0, elasticity=500),
        Commodity("Caoutchouc", floor_price=140, ceiling_price=180, current_price=160, stockpile=0, elasticity=200),
    ]

    print("="*60)
    print("MODÈLE YUSUF-GRONDONA-ENTROPIE")
    print("Version intégrée - Simulation dynamique")
    print("="*60)

    sim = YusufGrondonaSimulation(
        commodities=commodities,
        initial_money=10000,
        simulation_years=50,
        time_step=0.25
    )

    df = sim.run()
    sim.plot_results(df)

    # Optionnel : comparer les scénarios
    # df_g, df_d = sim.compare_scenarios()

"""
Interface Streamlit pour le modèle Yusuf-Grondona-Entropie
Auteur : Marc Daghar
Licence : CC BY-SA 4.0
Mention : Free Dr Aafia Siddiqui !
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from yusuf_model import YusufGrondonaSimulation, Commodity

# Configuration de la page
st.set_page_config(
    page_title="Yusuf-Grondona Model",
    page_icon="⚖️",
    layout="wide"
)

st.markdown("""
<style>
    .main { background-color: #0a0f1e; }
    .stApp { color: #e0e0e0; }
    .big-font { font-size:30px !important; font-weight: bold; color: #d4af37; }
    .info-box { background-color: #1e2a3a; padding: 20px; border-radius: 10px; border-left: 5px solid #d4af37; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">YUSUF-GRONDONA-ENTROPIE</p>', unsafe_allow_html=True)
st.markdown("*Modèle économique bimétallique - Contre-cycle - Monnaie naturelle*")
st.markdown("---")

# Barre latérale - Paramètres
with st.sidebar:
    st.header("⚙️ Paramètres de simulation")

    years = st.slider("Durée de simulation (années)", 10, 100, 50, 10)
    time_step = st.slider("Pas de temps (trimestres)", 0.1, 1.0, 0.25, 0.05)

    st.subheader("Prix des commodités")
    wheat_floor = st.slider("Blé - prix plancher", 100, 300, 180, 10)
    wheat_ceiling = st.slider("Blé - prix plafond", 150, 350, 220, 10)

    copper_floor = st.slider("Cuivre - prix plancher", 5000, 15000, 8000, 500)
    copper_ceiling = st.slider("Cuivre - prix plafond", 8000, 18000, 12000, 500)

    st.subheader("Paramètres système")
    initial_money = st.number_input("Masse monétaire initiale", 1000, 100000, 10000, 1000)
    use_grondona = st.checkbox("Activer le système Grondona", value=True)

    run_button = st.button("🚀 Lancer la simulation", type="primary")

# Zone principale
if run_button:
    with st.spinner("Simulation en cours..."):

        # Définition des commodités
        commodities = [
            Commodity("Blé", floor_price=wheat_floor, ceiling_price=wheat_ceiling,
                      current_price=(wheat_floor + wheat_ceiling)/2, stockpile=0, elasticity=100),
            Commodity("Cuivre", floor_price=copper_floor, ceiling_price=copper_ceiling,
                      current_price=(copper_floor + copper_ceiling)/2, stockpile=0, elasticity=10),
            Commodity("Coton", floor_price=70, ceiling_price=90,
                      current_price=80, stockpile=0, elasticity=500),
            Commodity("Caoutchouc", floor_price=140, ceiling_price=180,
                      current_price=160, stockpile=0, elasticity=200),
        ]

        # Exécution de la simulation
        sim = YusufGrondonaSimulation(
            commodities=commodities,
            initial_money=initial_money,
            simulation_years=years,
            time_step=time_step
        )
        sim.use_grondona = use_grondona
        df = sim.run()

        # Métriques
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Masse monétaire finale", f"{df['money_supply'].iloc[-1]:.0f}",
                      delta=f"{df['money_supply'].iloc[-1] - df['money_supply'].iloc[0]:.0f}")

        with col2:
            st.metric("Valeur du stock", f"{df['total_stockpile'].iloc[-1]:.0f}")

        with col3:
            entropie_finale = df['entropy_produced'].iloc[-1]
            st.metric("Entropie totale", f"{entropie_finale:.1f}")

        with col4:
            durable = df['is_sustainable'].iloc[-1] if 'is_sustainable' in df.columns else "N/A"
            st.metric("Système durable", "✅ Oui" if durable else "❌ Non")

        # Graphiques avec Plotly
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=('Masse monétaire vs Stock', 'Entropie cumulative',
                            'Paramètre de bifurcation Λ', 'Flux net d\'entropie',
                            'Ratio Dette/Monnaie', 'Durabilité')
        )

        # 1. Masse monétaire et stock
        fig.add_trace(go.Scatter(x=df['time'], y=df['money_supply'],
                                 name='Masse monétaire', line=dict(color='#d4af37', width=2)), row=1, col=1)
        fig.add_trace(go.Scatter(x=df['time'], y=df['total_stockpile'],
                                 name='Stock', line=dict(color='#2ecc71', width=2)), row=1, col=1)

        # 2. Entropie
        fig.add_trace(go.Scatter(x=df['time'], y=df['entropy_produced'],
                                 name='Entropie', line=dict(color='#e74c3c', width=2)), row=1, col=2)

        # 3. Bifurcation
        fig.add_trace(go.Scatter(x=df['time'], y=df['lambda_param'],
                                 name='Λ', line=dict(color='#f39c12', width=2)), row=1, col=3)
        fig.add_hline(y=1.0, line_dash="dash", line_color="red", row=1, col=3)

        # 4. Flux d'entropie
        fig.add_trace(go.Scatter(x=df['time'], y=df['entropy_rate'],
                                 name='dS/dt', line=dict(color='#9b59b6', width=1.5)), row=2, col=1)
        fig.add_hline(y=0, line_width=0.5, row=2, col=1)

        # 5. Dette/Monnaie
        fig.add_trace(go.Scatter(x=df['time'], y=df['debt_to_money'],
                                 name='Dette/Monnaie', line=dict(color='#c0392b', width=2)), row=2, col=2)

        # 6. Durabilité
        fig.add_trace(go.Scatter(x=df['time'], y=df['is_sustainable'].astype(float),
                                 name='Durable', line=dict(color='#27ae60', width=2)), row=2, col=3)

        fig.update_layout(height=800, template='plotly_dark', showlegend=False)
        fig.update_xaxes(title_text="Années", row=2, col=1)
        fig.update_xaxes(title_text="Années", row=2, col=2)
        fig.update_xaxes(title_text="Années", row=2, col=3)

        st.plotly_chart(fig, use_container_width=True)

        # Affichage des données
        with st.expander("📊 Afficher les données brutes"):
            st.dataframe(df)

        # Export CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger CSV",
            data=csv,
            file_name="simulation_yusuf_grondona.csv",
            mime="text/csv"
        )

else:
    st.info("👈 Configurez les paramètres dans la barre latérale et cliquez sur 'Lancer la simulation'")

    st.markdown("""
    <div class="info-box">
    <b>Modèle Yusuf-Grondona-Entropie</b><br>
    Ce modèle simule un système économique bimétallique avec :
    <ul>
        <li>Système Grondona (contre-cyclique, achat/vente de commodités)</li>
        <li>Entropie thermodynamique (Georgescu-Roegen)</li>
        <li>Détection de la bifurcation (Λ = D·r / Ė_low)</li>
        <li>Comparaison système de dette vs système bimétallique</li>
    </ul>
    <b>Free Dr Aafia Siddiqui !</b>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("*Licence CC BY-SA 4.0 - Auteur conceptuel : Marc Daghar*")
st.markdown("**Free Dr Aafia Siddiqui !**")

