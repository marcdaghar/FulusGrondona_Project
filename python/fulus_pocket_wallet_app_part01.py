def detect_absurdity(financial_price, physical_value, logistics_cost):
    """
    Détecte les prix impossibles dans l'économie réelle.
    """
    if financial_price < 0 and physical_value >= 0:
        return "CATASTROPHIC : prix négatif pour un bien physique utile"
    
    real_spread = abs(financial_price - physical_value)
    if real_spread > logistics_cost * 2:
        return "HIGH : écart supérieur au coût logistique"
    
    return "NONE"
class CommodityReserveDepartment:
    def __init__(self, floor_price, ceiling_price, stock=0):
        self.floor_price = floor_price
        self.ceiling_price = ceiling_price
        self.stock = stock  # en unités physiques
        self.reserve_currency = 0  # en fulus

    def update_price(self, market_price):
        """
        Applique le mécanisme Grondona :
        - Si prix < plancher : le CRD achète, le prix remonte au plancher.
        - Si prix > plafond : le CRD vend, le prix redescend au plafond.
        """
        if market_price < self.floor_price:
            # Le CRD achète pour soutenir le prix
            self.stock += 1  # achète 1 unité
            self.reserve_currency -= self.floor_price
            return self.floor_price
        
        elif market_price > self.ceiling_price:
            # Le CRD vend pour faire baisser le prix
            if self.stock > 0:
                self.stock -= 1  # vend 1 unité
                self.reserve_currency += self.ceiling_price
            return self.ceiling_price
        
        else:
            return market_price

    def get_reserve_ratio(self):
        """Ratio de couverture des réserves en stock."""
        if self.stock > 0:
            return self.reserve_currency / self.stock
        return 0
import random
from dataclasses import dataclass
from typing import List

@dataclass
class Agent:
    id: int
    fulus_balance: float
    goods_inventory: float
    trust_score: float  # 0 à 1

class GuildEconomy:
    def __init__(self, agents: List[Agent], crd: CommodityReserveDepartment):
        self.agents = agents
        self.crd = crd
        self.price_history = []

    def run_step(self):
        """Simule un pas de temps de l'économie de guilde."""
        total_demand = sum(a.fulus_balance for a in self.agents)
        total_supply = sum(a.goods_inventory for a in self.agents)
        
        if total_supply == 0:
            market_price = self.crd.floor_price
        else:
            market_price = total_demand / total_supply
        
        # Application du CRD
        stable_price = self.crd.update_price(market_price)
        self.price_history.append(stable_price)
        
        # Transactions entre agents
        for i, buyer in enumerate(self.agents):
            for j, seller in enumerate(self.agents):
                if i != j and buyer.fulus_balance > 0 and seller.goods_inventory > 0:
                    # Transaction directe (main à main)
                    trade_volume = min(buyer.fulus_balance * 0.1, seller.goods_inventory * 0.1)
                    price = stable_price * (1 + random.uniform(-0.05, 0.05))  # variation locale
                    
                    if buyer.trust_score > 0.5 and seller.trust_score > 0.5:
                        # Échange de confiance
                        buyer.fulus_balance -= trade_volume * price
                        buyer.goods_inventory += trade_volume
                        seller.fulus_balance += trade_volume * price
                        seller.goods_inventory -= trade_volume
                        buyer.trust_score = min(1.0, buyer.trust_score + 0.01)
                        seller.trust_score = min(1.0, seller.trust_score + 0.01)

    def detect_crisis(self):
        """Détection des signaux faibles (Bassira)."""
        if len(self.price_history) < 10:
            return "RAS"
        
        recent = self.price_history[-10:]
        volatility = max(recent) - min(recent)
        if volatility > self.crd.ceiling_price - self.crd.floor_price:
            return "ALERTE : Volatilité excessive détectée"
        if self.crd.stock == 0 and self.crd.reserve_currency < 0:
            return "ALERTE : Réserves CRD épuisées"
        return "RAS"

# Exemple d'exécution
if __name__ == "__main__":
    # Création de 10 agents
    agents = [
        Agent(id=i, fulus_balance=random.uniform(10, 100), 
              goods_inventory=random.uniform(5, 50), 
              trust_score=random.uniform(0.3, 0.9))
        for i in range(10)
    ]
    
    # CRD avec prix plancher 10, plafond 20
    crd = CommodityReserveDepartment(floor_price=10, ceiling_price=20, stock=100)
    
    # Simulation
    economy = GuildEconomy(agents, crd)
    for step in range(100):
        economy.run_step()
        alert = economy.detect_crisis()
        if alert != "RAS":
            print(f"Étape {step}: {alert}")
    
    print(f"Prix final: {economy.price_history[-1]:.2f}")
    print(f"Réserves CRD: {crd.stock} unités, {crd.reserve_currency:.2f} fulus")

# Fulus Pocket – Modélisation d’un wallet mobile bimétallique

