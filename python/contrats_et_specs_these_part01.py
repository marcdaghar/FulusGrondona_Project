import hashlib
import time
from dataclasses import dataclass
from typing import List, Dict, Tuple

@dataclass
class GuildMember:
    """Représentation d'un membre de la guilde pour le PoSS"""
    address: str
    balance: float  # s_i en fulus
    seniority: int  # a_i en jours (max 365)
    participation: float  # p_i (0-100)
    reputation: float  # r_i (0-100)
    is_validator: bool = False
    
    @property
    def weight(self) -> float:
        """Calcul du poids de validation w_i selon la formule PoSS"""
        # Paramètres (à calibrer)
        ALPHA, BETA, GAMMA, DELTA = 0.3, 0.3, 0.2, 0.2
        
        # Normalisation (valeurs maximales)
        S_MAX = 10000  # Balance max
        A_MAX = 365    # Ancienneté max (1 an)
        P_MAX = 100    # Participation max
        R_MAX = 100    # Réputation max
        
        w = (ALPHA * self.balance / S_MAX + 
             BETA * self.seniority / A_MAX + 
             GAMMA * self.participation / P_MAX + 
             DELTA * self.reputation / R_MAX)
        
        return w

class PoSSValidator:
    """Système de validation Proof of Social Stake"""
    
    def __init__(self):
        self.members: Dict[str, GuildMember] = {}
        self.validators: List[str] = []
        self.block_time = 60  # secondes
        
    def register_member(self, member: GuildMember):
        """Enregistrement d'un nouveau membre"""
        self.members[member.address] = member
        
    def select_validator_set(self, num_validators: int = 5) -> List[str]:
        """Sélection des validateurs par tirage au sort pondéré"""
        # Calcul des poids
        weights = {}
        total_weight = 0
        
        for addr, member in self.members.items():
            w = member.weight
            weights[addr] = w
            total_weight += w
            
        # Tirage au sort (sans remise)
        selected = []
        remaining_weights = dict(weights)
        
        for _ in range(min(num_validators, len(self.members))):
            # Tirage pondéré
            rand = np.random.random() * total_weight
            cumulative = 0
            
            for addr, w in remaining_weights.items():
                cumulative += w
                if cumulative >= rand:
                    selected.append(addr)
                    total_weight -= w
                    del remaining_weights[addr]
                    break
        
        self.validators = selected
        return selected
    
    def validate_block(self, block_data: bytes, validator: str) -> bool:
        """Validation d'un bloc par un validateur"""
        if validator not in self.validators:
            return False
            
        # Simulation de validation (hash + vérification)
        block_hash = hashlib.sha256(block_data).hexdigest()
        
        # Validation basée sur la réputation (simplifiée)
        member = self.members[validator]
        validation_score = member.weight * np.random.normal(1.0, 0.1)
        
        return validation_score > 0.5  # Seuil de validation
    
    def get_consensus(self, block_data: bytes) -> Tuple[bool, int]:
        """Obtention du consensus (PoSS)"""
        validators = self.select_validator_set()
        valid_votes = 0
        
        for validator in validators:
            if self.validate_block(block_data, validator):
                valid_votes += 1
        
        # Consensus si > 2/3 des validateurs sont d'accord
        consensus = valid_votes >= (2 * len(validators) // 3)
        return consensus, valid_votes

# ================================================================
# SIMULATION
# ================================================================

def run_simulation():
    """Simulation du système PoSS"""
    print("=" * 60)
    print("SIMULATION PoSS (Proof of Social Stake)")
    print("=" * 60)
    
    validator = PoSSValidator()
    
    # Création de 20 membres
    for i in range(20):
        member = GuildMember(
            address=f"0x{i:040x}",
            balance=np.random.uniform(100, 10000),
            seniority=np.random.randint(1, 365),
            participation=np.random.uniform(10, 95),
            reputation=np.random.uniform(20, 90)
        )
        validator.register_member(member)
    
    # Affichage des membres
    print("\n--- Membres enregistrés ---")
    for addr, member in validator.members.items():
        print(f"Member {addr[:10]}... | Balance: {member.balance:.0f} | Poids: {member.weight:.3f}")
    
    # Sélection des validateurs
    print(f"\n--- Sélection des validateurs ---")
    validators = validator.select_validator_set(num_validators=5)
    print(f"Validateurs sélectionnés: {[v[:10] + '...' for v in validators]}")
    
    # Simulation de validation
    print("\n--- Simulation de validation ---")
    for i in range(10):
        block_data = f"Block #{i} - {time.time()}".encode()
        consensus, votes = validator.get_consensus(block_data)
        
        print(f"Bloc {i}: Consensus = {consensus} ({votes} votes)")

if __name__ == "__main__":
    run_simulation()

