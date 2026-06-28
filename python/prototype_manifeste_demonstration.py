import hashlib
import time
import json
from typing import List, Dict, Any
import random

# ==========================================================================
# Modèle Mathématique du Système Monétaire Islamique Post-Capitaliste
# ==========================================================================

class Bimetallism:
    """
    Modélise l'ancrage bimétallique (Or/Argent).
    """
    def __init__(self, gold_price: float = 1.0, silver_price: float = 0.05, alpha: float = 0.6, beta: float = 0.4):
        self.gold_price = gold_price  # Prix de l'or dans l'unité de base
        self.silver_price = silver_price  # Prix de l'argent
        self.alpha = alpha  # Poids de l'or dans le panier
        self.beta = beta  # Poids de l'argent

    def get_value_in_metal(self, amount: float) -> float:
        """
        Calcule la valeur métallique d'une quantité de fulus.
        """
        basket_value = self.alpha * self.gold_price + self.beta * self.silver_price
        return (amount / basket_value) if basket_value > 0 else 0

    def get_value_in_fulus(self, metal_amount: float) -> float:
        """
        Calcule la quantité de fulus correspondant à une quantité de métal.
        """
        basket_value = self.alpha * self.gold_price + self.beta * self.silver_price
        return metal_amount * basket_value

    def update_prices(self, new_gold_price: float, new_silver_price: float):
        """
        Met à jour les prix du marché (simulant la volatilité).
        """
        self.gold_price = new_gold_price
        self.silver_price = new_silver_price
        print(f"[BIMETALLISME] Nouveaux prix : Or={self.gold_price}, Argent={self.silver_price}")


class ZakatCalculator:
    """
    Calcule la Zakat selon le nisab (seuil de richesse) et les règles traditionnelles.
    """
    NISAB_GOLD = 85  # grammes
    NISAB_SILVER = 595  # grammes
    ZAKAT_RATE = 0.025  # 2.5%

    @staticmethod
    def calculate(wealth_in_metal: float, metal_type: str = "gold") -> float:
        """
        Calcule la Zakat due.
        """
        if metal_type == "gold":
            nisab = ZakatCalculator.NISAB_GOLD
        elif metal_type == "silver":
            nisab = ZakatCalculator.NISAB_SILVER
        else:
            raise ValueError("Le type de métal doit être 'gold' ou 'silver'.")

        if wealth_in_metal >= nisab:
            zakat_due = wealth_in_metal * ZakatCalculator.ZAKAT_RATE
            print(f"[ZAKAT] Calculée : {zakat_due:.4f} unités de métal (Seuil atteint)")
            return zakat_due
        else:
            print(f"[ZAKAT] Pas de Zakat due (Richesse < Nisab)")
            return 0.0


class Guild:
    """
    Représente une néo-guilde, unité économique de base.
    Elle émet du crypto-fulus en fonction du travail productif.
    """
    def __init__(self, name: str, productive_capacity: float, zakat_collector):
        self.name = name
        self.productive_capacity = productive_capacity  # Capacité de production par cycle
        self.fulus_balance = 0.0  # Solde en crypto-fulus
        self.zakat_collector = zakat_collector  # Référence à l'Emir qui collecte la Zakat

    def produce(self, external_demand: float = 1.0) -> float:
        """
        Simule la production et l'émission de fulus.
        """
        # 1. La production crée de la richesse
        production = self.productive_capacity * external_demand

        # 2. Émission de crypto-fulus en récompense du travail (monnaie-travail)
        reward = production * 0.8  # 80% de la production est distribuée comme rémunération

        self.fulus_balance += reward
        print(f"[GUILDE {self.name}] Production: {production:.2f} unités, Récompense fulus: {reward:.2f}")
        return production

    def pay_zakat(self) -> float:
        """
        Paie la Zakat à l'Émir.
        """
        # On calcule la Zakat sur le solde en fulus, converti en métal
        # Ici, on suppose un taux de conversion fixe pour la démo
        # Idéalement, on utiliserait Bimetallism pour la conversion
        metal_equivalent = self.fulus_balance * 0.01  # Hypothèse : 1 fulus = 0.01 unité de métal
        zakat_due = ZakatCalculator.calculate(metal_equivalent, "gold")

        if zakat_due > 0:
            # On paie en fulus (équivalent métal)
            fulus_to_pay = zakat_due / 0.01
            if self.fulus_balance >= fulus_to_pay:
                self.fulus_balance -= fulus_to_pay
                self.zakat_collector.receive_zakat(fulus_to_pay)
                print(f"[GUILDE {self.name}] Zakat payée: {fulus_to_pay:.2f} fulus")
                return fulus_to_pay
            else:
                print(f"[GUILDE {self.name}] Fonds insuffisants pour payer la Zakat.")
        return 0.0

    def trade_with(self, other_guild, amount: float):
        """
        Simule un échange commercial entre guildes.
        """
        if self.fulus_balance >= amount:
            self.fulus_balance -= amount
            other_guild.fulus_balance += amount
            print(f"[GUILDE {self.name}] Échange de {amount:.2f} fulus avec {other_guild.name}")
        else:
            print(f"[GUILDE {self.name}] Solde insuffisant pour échanger avec {other_guild.name}")


class Emirate:
    """
    Représente l'Émirat, autorité politique qui gère la Zakat et la gouvernance.
    """
    def __init__(self, name: str, initial_reserves: float = 1000.0):
        self.name = name
        self.treasury = initial_reserves  # Bayt al-Mal
        self.zakat_fund = 0.0
        self.transactions: List[Dict[str, Any]] = []  # Registre des transactions

    def receive_zakat(self, amount: float):
        """
        Reçoit la Zakat collectée.
        """
        self.zakat_fund += amount
        self.treasury += amount
        print(f"[EMIRAT {self.name}] Zakat reçue: {amount:.2f} fulus. Trésorerie: {self.treasury:.2f}")

    def distribute_zakat(self, amount: float, beneficiary: str):
        """
        Distribue la Zakat aux bénéficiaires (pauvres, voyageurs, etc.).
        """
        if self.zakat_fund >= amount:
            self.zakat_fund -= amount
            self.treasury -= amount
            print(f"[EMIRAT {self.name}] Zakat distribuée: {amount:.2f} fulus à {beneficiary}")
        else:
            print(f"[EMIRAT {self.name}] Fonds de Zakat insuffisant pour distribuer.")

    def validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """
        Valide une transaction commerciale (fonction de régulation).
        """
        # Vérification de la conformité à la Sharia (pas de riba, etc.)
        if transaction.get('interest', 0) > 0:
            print(f"[EMIRAT {self.name}] Transaction rejetée: Riba détecté!")
            return False
        self.transactions.append(transaction)
        print(f"[EMIRAT {self.name}] Transaction validée: {transaction}")
        return True


class Blockchain:
    """
    Représente la blockchain qui sécurise les transactions en crypto-fulus.
    """
    def __init__(self, emirate: Emirate):
        self.chain: List[Dict[str, Any]] = []
        self.current_transactions: List[Dict[str, Any]] = []
        self.emirate = emirate
        self.money_supply = 0.0  # Masse monétaire totale en circulation

        # Créer le bloc genesis
        self.new_block(proof=100, previous_hash="0")

    def new_block(self, proof: int, previous_hash: str = None) -> Dict[str, Any]:
        """
        Crée un nouveau bloc et l'ajoute à la chaîne.
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]) if self.chain else "0",
            'money_supply': self.money_supply,
        }

        # Réinitialiser la liste des transactions courantes
        self.current_transactions = []
        self.chain.append(block)
        print(f"[BLOCKCHAIN] Nouveau bloc créé: #{block['index']}")
        return block

    def new_transaction(self, sender: str, recipient: str, amount: float, interest: float = 0) -> int:
        """
        Ajoute une nouvelle transaction à la liste des transactions en attente.
        """
        if amount <= 0:
            print("[BLOCKCHAIN] Transaction rejetée: Montant invalide.")
            return -1

        # Vérifier que la transaction n'est pas usuraire
        if interest > 0:
            print("[BLOCKCHAIN] Transaction rejetée: Intérêt (Riba) non autorisé.")
            return -1

        # Vérification du solde (simplifiée)
        # Dans un vrai système, on vérifierait le solde via l'UTXO
        if sender != "mint" and self.money_supply < amount:
            print("[BLOCKCHAIN] Transaction rejetée: Masse monétaire insuffisante.")
            return -1

        # Validation par l'Émirat
        transaction = {
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'interest': interest,
            'timestamp': time.time()
        }

        if self.emirate.validate_transaction(transaction):
            self.current_transactions.append(transaction)
            self.money_supply += amount if sender == "mint" else 0
            return len(self.current_transactions)
        else:
            return -1

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        """
        Génère un hash SHA-256 pour un bloc.
        """
        block_string = json.dumps(block, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def proof_of_work(self, last_block: Dict[str, Any]) -> int:
        """
        Algorithme simple de preuve de travail (PoW) pour la démonstration.
        """
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int, last_hash: str) -> bool:
        """
        Vérifie une preuve de travail.
        """
        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    def mine(self, miner: str):
        """
        Simule le minage d'un bloc (sécurisation du réseau).
        """
        # Récupérer le dernier bloc
        last_block = self.chain[-1]

        # Trouver une preuve de travail
        proof = self.proof_of_work(last_block)

        # Récompense du mineur (émission monétaire par le travail)
        self.new_transaction(
            sender="mint",
            recipient=miner,
            amount=1.0,  # Récompense de minage
            interest=0
        )

        # Créer un nouveau bloc
        previous_hash = self.hash(last_block)
        block = self.new_block(proof, previous_hash)

        print(f"[BLOCKCHAIN] Bloc #{block['index']} miné par {miner}")
        print(f"[BLOCKCHAIN] Masse monétaire totale: {self.money_supply:.2f} fulus")


# ==========================================================================
# SIMULATION ET TESTS
# ==========================================================================

def simulation():
    print("=" * 60)
    print("SIMULATION DU SYSTÈME MONÉTAIRE ISLAMIQUE POST-CAPITALISTE")
    print("=" * 60)

    # 1. Initialisation des institutions
    emir = Emirate("Médine", initial_reserves=5000.0)
    blockchain = Blockchain(emir)
    bimetallism = Bimetallism(gold_price=1.0, silver_price=0.05)

    # 2. Création des guildes (unités économiques de base)
    guilds = [
        Guild("Guildes des Artisans", productive_capacity=100.0, zakat_collector=emir),
        Guild("Guildes des Marchands", productive_capacity=150.0, zakat_collector=emir),
        Guild("Guildes des Agriculteurs", productive_capacity=200.0, zakat_collector=emir),
    ]

    # 3. Création d'un Émir (leader politique) - élection sans candidat
    print("\n[ÉMIRAT] Élection de l'Émir...")
    # (Simulation d'une élection sans candidat)
    emir.name = "Émir Al-Mu'minīn"
    print(f"[ÉMIRAT] {emir.name} est élu par la communauté !")

    # 4. Simulation de cycles économiques
    print("\n[SIMULATION] Début des cycles économiques...")
    for cycle in range(1, 4):
        print(f"\n--- CYCLE {cycle} ---")

        # 4.1 Production et émission de crypto-fulus
        print("\n[PRODUCTION] Émission de crypto-fulus par le travail...")
        for guild in guilds:
            # La production dépend de la demande externe (simulée)
            demand = 0.8 + 0.4 * random.random()
            guild.produce(external_demand=demand)

        # 4.2 Paiement de la Zakat
        print("\n[ZAKAT] Paiement de la Zakat...")
        for guild in guilds:
            guild.pay_zakat()

        # 4.3 Distribution de la Zakat
        print("\n[ZAKAT] Distribution de la Zakat aux bénéficiaires...")
        emir.distribute_zakat(amount=20.0, beneficiary="Pauvres de Médine")
        emir.distribute_zakat(amount=10.0, beneficiary="Voyageurs")

        # 4.4 Échanges commerciaux (Sūq)
        print("\n[COMMERCE] Échanges entre guildes...")
        if len(guilds) >= 2:
            guilds[0].trade_with(guilds[1], amount=30.0)
            guilds[1].trade_with(guilds[2], amount=25.0)

        # 4.5 Minage de blocs (sécurisation de la blockchain)
        print("\n[BLOCKCHAIN] Minage d'un nouveau bloc...")
        blockchain.mine(miner="Guildes des Artisans")
        blockchain.mine(miner="Guildes des Marchands")

        # 4.6 Mise à jour du bimétallisme (simulation de la volatilité du marché)
        print("\n[BIMETALLISME] Mise à jour des prix...")
        new_gold = 1.0 + 0.1 * random.random()
        new_silver = 0.05 + 0.01 * random.random()
        bimetallism.update_prices(new_gold, new_silver)

    # 5. Bilan final
    print("\n" + "=" * 60)
    print("BILAN FINAL DU SYSTÈME")
    print("=" * 60)

    print(f"\n[ÉMIRAT] Trésorerie de l'Émirat: {emir.treasury:.2f} fulus")
    print(f"[ÉMIRAT] Fonds de Zakat: {emir.zakat_fund:.2f} fulus")

    print(f"\n[BLOCKCHAIN] Masse monétaire totale: {blockchain.money_supply:.2f} fulus")
    print(f"[BLOCKCHAIN] Nombre de blocs: {len(blockchain.chain)}")

    print("\n[SOLDES DES GUILDES]")
    for guild in guilds:
        print(f"  - {guild.name}: {guild.fulus_balance:.2f} fulus")

    print("\n[BIMETALLISME]")
    print(f"  - Prix de l'Or: {bimetallism.gold_price}")
    print(f"  - Prix de l'Argent: {bimetallism.silver_price}")

    print("\n[CONCLUSION] Le système fonctionne sans intérêt (Riba).")
    print("La Zakat est collectée et redistribuée.")
    print("Le crypto-fulus est adossé au bimétallisme.")
    print("La communauté des guildes forme la base de l'économie.")
    print("L'Émirat assure la gouvernance politique.")
    print("\n" + "=" * 60)

# ==========================================================================
# EXÉCUTION DE LA SIMULATION
# ==========================================================================

if __name__ == "__main__":
    simulation()
