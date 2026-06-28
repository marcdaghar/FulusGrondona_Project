import numpy as np
import matplotlib.pyplot as plt

def calculate_debt_growth(principal, rate, years, compounding_periods=1):
    """
    Calcule la croissance de la dette avec intérêts composés.
    
    Args:
        principal (float): Montant initial de la dette
        rate (float): Taux d'intérêt annuel (ex: 0.05 pour 5%)
        years (int): Nombre d'années
        compounding_periods (int): Nombre de capitalisations par an
    
    Returns:
        tuple: (années, montants de la dette)
    """
    periods = years * compounding_periods
    time = np.linspace(0, years, periods + 1)
    debt = principal * (1 + rate/compounding_periods) ** (compounding_periods * time)
    return time, debt

def debt_doubling_time(rate):
    """Calcule le temps de doublement d'une dette (règle de 72)."""
    return 72 / (rate * 100)

# Exemple : Dette de 1000€ à 5% sur 30 ans
principal = 1000
rate = 0.05
years = 30

time, debt = calculate_debt_growth(principal, rate, years)

print(f"Dette initiale : {principal:.2f}€")
print(f"Taux : {rate*100:.1f}%")
print(f"Temps de doublement : {debt_doubling_time(rate):.1f} ans")
print(f"Dette après {years} ans : {debt[-1]:.2f}€")

# Visualisation
plt.figure(figsize=(12, 6))
plt.plot(time, debt, 'b-', linewidth=2, label='Dette avec intérêts composés')
plt.axhline(y=principal*2, color='r', linestyle='--', label='Doublement')
plt.xlabel('Années')
plt.ylabel('Montant de la dette (€)')
plt.title('Croissance exponentielle de la dette (Usure)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

def public_debt_dynamics(initial_debt, spending, taxes, interest_rate, years):
    """
    Simule l'évolution de la dette publique.
    
    Args:
        initial_debt (float): Dette initiale
        spending (float): Dépenses publiques annuelles (hors intérêts)
        taxes (float): Recettes fiscales annuelles
        interest_rate (float): Taux d'intérêt moyen sur la dette
        years (int): Nombre d'années
    
    Returns:
        tuple: (années, niveaux de dette)
    """
    debt = np.zeros(years + 1)
    debt[0] = initial_debt
    
    for t in range(1, years + 1):
        interest_payment = interest_rate * debt[t-1]
        debt[t] = debt[t-1] + spending + interest_payment - taxes
    
    return np.arange(years + 1), debt

# Exemple
initial_debt = 3000  # en milliards d'euros
spending = 500       # dépenses annuelles
taxes = 450          # recettes annuelles
interest_rate = 0.03 # 3%

years, debt = public_debt_dynamics(initial_debt, spending, taxes, interest_rate, 30)

print(f"Dette initiale : {initial_debt:.0f} milliards €")
print(f"Dette après 30 ans : {debt[-1]:.0f} milliards €")
print(f"Augmentation : {((debt[-1]/initial_debt)-1)*100:.1f}%")

# Visualisation
plt.figure(figsize=(12, 6))
plt.plot(years, debt, 'r-', linewidth=2, label='Dette publique')
plt.xlabel('Années')
plt.ylabel('Dette (milliards €)')
plt.title('Dynamique de la dette publique')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

def vectorial_power_model(d_vector, f_vector):
    """
    Calcule la puissance résultante V = D · F
    
    Args:
        d_vector (np.array): Vecteur du "droit maître"
        f_vector (np.array): Vecteur du "conatus"
    
    Returns:
        tuple: (norme de V, angle en degrés, projection)
    """
    # Produit scalaire
    dot_product = np.dot(d_vector, f_vector)
    
    # Normes
    norm_d = np.linalg.norm(d_vector)
    norm_f = np.linalg.norm(f_vector)
    
    # Cosinus de l'angle
    if norm_d > 0 and norm_f > 0:
        cos_alpha = dot_product / (norm_d * norm_f)
    else:
        cos_alpha = 0
    
    # Angle en degrés
    angle = np.arccos(np.clip(cos_alpha, -1, 1)) * 180 / np.pi
    
    return dot_product, angle, cos_alpha

def simulate_conflict_scenarios():
    """Simule différents scénarios de conflit."""
    # Scénario 1 : Forces alignées (harmonie)
    d1 = np.array([1, 0])
    f1 = np.array([1, 0])
    
    # Scénario 2 : Forces opposées (conflit)
    d2 = np.array([1, 0])
    f2 = np.array([-1, 0])
    
    # Scénario 3 : Forces perpendiculaires (impasse)
    d3 = np.array([1, 0])
    f3 = np.array([0, 1])
    
    scenarios = [
        ("Harmonie", d1, f1),
        ("Conflit", d2, f2),
        ("Impasse", d3, f3)
    ]
    
    print("Analyse de la puissance V = D · F")
    print("-" * 50)
    
    for name, d, f in scenarios:
        V, angle, cos = vectorial_power_model(d, f)
        print(f"\n{name}:")
        print(f"  D = {d}, F = {f}")
        print(f"  V = {V:.2f}")
        print(f"  Angle = {angle:.1f}°")
        print(f"  cos(α) = {cos:.2f}")
        if angle == 0:
            print("  → Puissance maximale (alignement parfait)")
        elif angle == 180:
            print("  → Puissance négative (conflit total)")
        elif angle == 90:
            print("  → Puissance nulle (forces perpendiculaires)")

simulate_conflict_scenarios()

def grondona_system(price_real, price_fixed, adjustment_rate=0.1, steps=100):
    """
    Simule un système Grondona de régulation monétaire.
    
    Args:
        price_real (float): Prix réel du panier de commodities
        price_fixed (float): Prix fixe (ancrage)
        adjustment_rate (float): Vitesse d'ajustement monétaire
        steps (int): Nombre d'itérations
    
    Returns:
        tuple: (étapes, taux d'ajustement)
    """
    money_supply = 100  # Masse monétaire initiale
    price_history = []
    adjustment_history = []
    
    for step in range(steps):
        price_history.append(price_real)
        
        # Écart entre le prix réel et le prix fixe
        gap = price_real - price_fixed
        
        # Ajustement de la masse monétaire
        adjustment = -adjustment_rate * gap
        money_supply += adjustment
        adjustment_history.append(adjustment)
        
        # Mise à jour du prix réel (simplifié : relation inverse avec la masse monétaire)
        price_real = price_fixed + gap / (1 + 0.01 * money_supply)
    
    return np.arange(steps), np.array(price_history), np.array(adjustment_history)

# Simulation
price_fixed = 100
price_real_initial = 120  # Prix initial supérieur
steps = 200

steps_arr, prices, adjustments = grondona_system(price_real_initial, price_fixed)

print(f"Prix fixe : {price_fixed:.2f}")
print(f"Prix initial : {price_real_initial:.2f}")
print(f"Prix final : {prices[-1]:.2f}")
print(f"Écart final : {prices[-1] - price_fixed:.2f}")

# Visualisation
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

ax1.plot(steps_arr, prices, 'g-', linewidth=2)
ax1.axhline(y=price_fixed, color='r', linestyle='--', label='Prix fixe (ancrage)')
ax1.set_xlabel('Étapes')
ax1.set_ylabel('Prix du panier')
ax1.set_title('Régulation par système Grondona')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(steps_arr, adjustments, 'b-', linewidth=2)
ax2.axhline(y=0, color='k', linestyle='-', alpha=0.5)
ax2.set_xlabel('Étapes')
ax2.set_ylabel('Ajustement monétaire')
ax2.set_title('Ajustement de la masse monétaire')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

class IslamicContract:
    """Classe de base pour les contrats islamiques non usuraires."""
    
    def __init__(self, capital, labor, profit_sharing_ratio=0.5):
        self.capital = capital
        self.labor = labor
        self.profit_sharing_ratio = profit_sharing_ratio
        self.contract_type = "Comenda/Mudaraba"
    
    def calculate_return(self, actual_profit):
        """
        Calcule le retour sur investissement selon le partage des profits.
        
        Args:
            actual_profit (float): Profit réel réalisé
        
        Returns:
            dict: Répartition des profits
        """
        if actual_profit <= 0:
            return {
                "capital_share": 0,
                "labor_share": 0,
                "total_return": actual_profit,
                "message": "Pas de profit, pas de retour (conformément au contrat)"
            }
        
        capital_share = actual_profit * self.profit_sharing_ratio
        labor_share = actual_profit * (1 - self.profit_sharing_ratio)
        
        return {
            "capital_share": capital_share,
            "labor_share": labor_share,
            "total_return": actual_profit,
            "profit_sharing_ratio": self.profit_sharing_ratio
        }

class MusaqatContract(IslamicContract):
    """Contrat Musāqāt (colonat paritaire) pour l'agriculture."""
    
    def __init__(self, land, water, seeds, labor, profit_sharing_ratio=0.5):
        super().__init__(capital=0, labor=labor, profit_sharing_ratio=profit_sharing_ratio)
        self.land = land
        self.water = water
        self.seeds = seeds
        self.contract_type = "Musāqāt"
    
    def calculate_return(self, harvest_value, operational_costs):
        """Calcule le partage des récoltes."""
        actual_profit = harvest_value - operational_costs
        return super().calculate_return(actual_profit)

def simulate_contract_comparison():
    """Compare un contrat islamique avec un prêt usuraire."""
    
    # Contrat islamique (Comenda)
    capital = 10000  # Capital investi
    labor = 5000     # Travail fourni
    profit_sharing = 0.5  # 50/50
    
    islamic_contract = IslamicContract(capital, labor, profit_sharing)
    
    # Prêt usuraire (banque)
    interest_rate = 0.10  # 10% d'intérêt
    
    profits = np.linspace(-5000, 30000, 100)
    islamic_returns = []
    usury_returns = []
    
    for profit in profits:
        # Retour islamique
        result = islamic_contract.calculate_return(profit)
        islamic_returns.append(result['capital_share'])
        
        # Retour usuraire (le capital est garanti)
        usury_return = capital * (1 + interest_rate)
        usury_returns.append(usury_return)
    
    plt.figure(figsize=(12, 6))
    plt.plot(profits, islamic_returns, 'g-', linewidth=2, label='Contrat Islamique (Comenda)')
    plt.plot(profits, usury_returns, 'r-', linewidth=2, label='Prêt Usuraire (10%)')
    plt.axhline(y=capital, color='b', linestyle='--', alpha=0.5, label='Capital initial')
    plt.xlabel('Profit réel du projet')
    plt.ylabel('Retour pour l\'investisseur')
    plt.title('Comparaison des contrats : Islamique vs Usuraire')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

simulate_contract_comparison()

def resource_depletion(initial_resource, extraction_rate, growth_rate, years):
    """
    Simule l'épuisement des ressources avec croissance exponentielle.
    
    Args:
        initial_resource (float): Quantité initiale de ressource
        extraction_rate (float): Taux d'extraction initial
        growth_rate (float): Taux de croissance de l'extraction
        years (int): Nombre d'années
    
    Returns:
        tuple: (années, ressources restantes, consommation cumulée)
    """
    resources = np.zeros(years + 1)
    consumption = np.zeros(years + 1)
    resources[0] = initial_resource
    
    for t in range(1, years + 1):
        extraction = extraction_rate * (1 + growth_rate) ** t
        consumption[t] = extraction
        resources[t] = max(0, resources[t-1] - extraction)
    
    return np.arange(years + 1), resources, consumption

def entropy_production(consumption, efficiency_coefficient=0.1):
    """Calcule la production d'entropie associée à la consommation."""
    return efficiency_coefficient * consumption

# Simulation
initial_resource = 1000  # Unités
extraction_rate = 10     # Extraction initiale
growth_rate = 0.03       # 3% de croissance annuelle
years = 50

years_arr, resources, consumption = resource_depletion(
    initial_resource, extraction_rate, growth_rate, years
)

entropy = entropy_production(consumption)

print(f"Ressources initiales : {initial_resource:.0f} unités")
print(f"Ressources après {years} ans : {resources[-1]:.0f} unités")
print(f"Consommation totale : {consumption.sum():.0f} unités")
print(f"Entropie totale produite : {entropy.sum():.2f}")

# Visualisation
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

ax1.plot(years_arr, resources, 'g-', linewidth=2, label='Ressources restantes')
ax1.plot(years_arr, consumption, 'r-', linewidth=2, label='Consommation')
ax1.set_xlabel('Années')
ax1.set_ylabel('Unités de ressource')
ax1.set_title('Épuisement des ressources et dépassement')
ax1.legend()
ax1.grid(True, alpha=0.3)

ax2.plot(years_arr, entropy, 'b-', linewidth=2, label='Production d\'entropie')
ax2.set_xlabel('Années')
ax2.set_ylabel('Entropie produite')
ax2.set_title('Deuxième principe de la thermodynamique (Georgescu-Roegen)')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

class CryptoFulusSystem:
    """
    Système monétaire unifié : Crypto-Fulus 
    (Bimétallisme + Grondona + Chartalisme + Blockchain)
    """
    
    def __init__(self):
        self.money_supply = 0
        self.gold_reserves = 0
        self.silver_reserves = 0
        self.commodity_prices = {"petroleum": 80, "wheat": 200, "copper": 4}
        self.commodity_weights = {"petroleum": 0.3, "wheat": 0.4, "copper": 0.3}
        self.anchor_price = 100  # Prix fixe de référence
    
    def calculate_commodity_index(self):
        """Calcule l'indice du panier de commodities (Grondona)."""
        index = 0
        for commodity, price in self.commodity_prices.items():
            weight = self.commodity_weights.get(commodity, 0)
            index += weight * price / self.anchor_price
        return index
    
    def adjust_money_supply(self, gap):
        """Ajuste la masse monétaire en fonction de l'écart (Grondona)."""
        adjustment_rate = 0.1
        adjustment = -adjustment_rate * gap
        self.money_supply += adjustment
        return adjustment
    
    def mint_currency(self, gold_quantity, silver_quantity):
        """Émission de crypto-fulus adossé au bimétallisme."""
        gold_price = 1800  # Prix de l'once d'or
        silver_price = 25  # Prix de l'once d'argent
        
        base_value = (gold_quantity * gold_price) + (silver_quantity * silver_price)
        
        # L'émission de monnaie ne peut dépasser la valeur des réserves
        new_money = base_value * 0.8  # Ratio de couverture de 80%
        self.money_supply += new_money
        self.gold_reserves += gold_quantity
        self.silver_reserves += silver_quantity
        
        return new_money
    
    def execute_smart_contract(self, contract_type, capital, labor, actual_profit):
        """Exécute un smart contract non usuraire."""
        if contract_type == "comenda":
            sharing_ratio = 0.5
            capital_return = actual_profit * sharing_ratio
            labor_return = actual_profit * (1 - sharing_ratio)
            return {"type": "Comenda", "capital": capital_return, "labor": labor_return}
        elif contract_type == "musaqat":
            land_share = actual_profit * 0.6
            labor_share = actual_profit * 0.4
            return {"type": "Musāqāt", "land": land_share, "labor": labor_share}
        else:
            return {"error": "Contrat non reconnu"}
    
    def get_system_status(self):
        """Retourne l'état du système."""
        return {
            "money_supply": self.money_supply,
            "gold_reserves": self.gold_reserves,
            "silver_reserves": self.silver_reserves,
            "commodity_index": self.calculate_commodity_index()
        }

# Simulation du système unifié
system = CryptoFulusSystem()

print("== SYSTÈME MONÉTAIRE UNIFIÉ : CRYPTO-FULUS ==")
print("-" * 50)

# Étape 1 : Émission initiale
gold = 10  # 10 onces d'or
silver = 100  # 100 onces d'argent
emission = system.mint_currency(gold, silver)
print(f"\n1. Émission de {emission:.2f} Fulii")
print(f"   Réserves : {system.gold_reserves:.1f} onces d'or, {system.silver_reserves:.1f} onces d'argent")
print(f"   Masse monétaire totale : {system.money_supply:.2f} Fulii")

# Étape 2 : Régulation Grondona
gap = system.calculate_commodity_index() - 1
adjustment = system.adjust_money_supply(gap)
print(f"\n2. Régulation Grondona :")
print(f"   Indice des commodities : {system.calculate_commodity_index():.3f}")
print(f"   Écart par rapport à l'ancrage : {gap:.3f}")
print(f"   Ajustement monétaire : {adjustment:.2f} Fulii")
print(f"   Nouvelle masse monétaire : {system.money_supply:.2f} Fulii")

# Étape 3 : Smart contract (Comenda)
profit = 5000
contract_result = system.execute_smart_contract("comenda", 10000, 5000, profit)
print(f"\n3. Smart Contract (Comenda) :")
print(f"   Profit réalisé : {profit:.2f} Fulii")
print(f"   Part du capital : {contract_result['capital']:.2f} Fulii")
print(f"   Part du travail : {contract_result['labor']:.2f} Fulii")
print("   ✅ Aucun intérêt, partage des profits et des pertes")

# Étape 4 : Smart contract (Musāqāt)
farm_profit = 3000
farm_result = system.execute_smart_contract("musaqat", 0, 100, farm_profit)
print(f"\n4. Smart Contract (Musāqāt) :")
print(f"   Production agricole : {farm_profit:.2f} Fulii")
print(f"   Part du propriétaire foncier : {farm_result['land']:.2f} Fulii")
print(f"   Part du travailleur : {farm_result['labor']:.2f} Fulii")
print("   ✅ Contrat agricole non usuraire")

print("\n" + "="*50)
print("SYSTÈME STABLE - FINANCE ISLAMIQUE OPÉRATIONNELLE")

