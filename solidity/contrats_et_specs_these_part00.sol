// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Pausable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

/**
 * @title FulusToken
 * @dev ERC-20 Token représentant le crypto-fulus
 * Caractéristiques: Burnable, Pausable, AccessControl (Roles)
 */
contract FulusToken is 
    ERC20, 
    ERC20Burnable, 
    ERC20Pausable, 
    AccessControl, 
    ERC20Permit 
{
    // === RÔLES ===
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
    
    // === VARIABLES D'ÉTAT ===
    uint256 public maxSupply;
    uint256 public mintingRate; // Taux d'émission annuel (en basis points)
    uint256 public lastMintTimestamp;
    
    // === ÉVÉNEMENTS ===
    event MaxSupplyUpdated(uint256 newMaxSupply);
    event MintingRateUpdated(uint256 newRate);
    event TokensMinted(address indexed to, uint256 amount);
    
    // === CONSTRUCTEUR ===
    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply,
        uint256 _maxSupply,
        address governance
    ) 
        ERC20(name, symbol) 
        ERC20Permit(name) 
    {
        _grantRole(DEFAULT_ADMIN_ROLE, governance);
        _grantRole(GOVERNANCE_ROLE, governance);
        _grantRole(MINTER_ROLE, governance);
        _grantRole(PAUSER_ROLE, governance);
        
        maxSupply = _maxSupply;
        mintingRate = 100; // 1% par an par défaut (en basis points)
        lastMintTimestamp = block.timestamp;
        
        // Mint initial
        require(initialSupply <= maxSupply, "Initial supply exceeds max");
        _mint(governance, initialSupply);
    }
    
    // === FONCTIONS DE MINTING (DAO Controlé) ===
    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        require(totalSupply() + amount <= maxSupply, "Exceeds max supply");
        _mint(to, amount);
        emit TokensMinted(to, amount);
    }
    
    // === MINTING AUTOMATIQUE (Inflation contrôlée) ===
    function autoMint() external onlyRole(GOVERNANCE_ROLE) {
        uint256 timeElapsed = block.timestamp - lastMintTimestamp;
        uint256 annualRate = mintingRate; // en basis points
        uint256 newSupply = totalSupply() * annualRate * timeElapsed / (10000 * 365 days);
        
        require(totalSupply() + newSupply <= maxSupply, "Exceeds max supply");
        
        _mint(address(this), newSupply);
        lastMintTimestamp = block.timestamp;
        emit TokensMinted(address(this), newSupply);
    }
    
    // === FONCTIONS DE GOUVERNANCE ===
    function setMaxSupply(uint256 newMaxSupply) external onlyRole(GOVERNANCE_ROLE) {
        require(newMaxSupply >= totalSupply(), "New max below current supply");
        maxSupply = newMaxSupply;
        emit MaxSupplyUpdated(newMaxSupply);
    }
    
    function setMintingRate(uint256 newRate) external onlyRole(GOVERNANCE_ROLE) {
        require(newRate <= 500, "Rate too high (max 5%)"); // Max 5% par an
        mintingRate = newRate;
        emit MintingRateUpdated(newRate);
    }
    
    // === PAUSE / UNPAUSE ===
    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }
    
    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }
    
    // === OVERRIDES NÉCESSAIRES ===
    function _update(address from, address to, uint256 value) 
        internal 
        override(ERC20, ERC20Pausable) 
    {
        super._update(from, to, value);
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/**
 * @title GuildDAO
 * @dev Implémentation du mécanisme DAV (Delayed Approval Voting)
 * Élection sans candidat - Vote sur des propositions techniques
 */
contract GuildDAO is AccessControl {
    using SafeMath for uint256;
    
    // === STRUCTURES ===
    struct Proposal {
        uint256 id;
        address proposer;
        string description;
        bytes32 parameterHash; // Hash du paramètre technique
        uint256[] votesYes; // Poids de réputation des votants "Oui"
        uint256[] votesNo;  // Poids de réputation des votants "Non"
        uint256 totalWeightYes;
        uint256 totalWeightNo;
        uint256 startTime;
        uint256 endTime;
        uint256 silenceEndTime; // Fin de la phase de silence
        bool executed;
        bool passed;
        ProposalStatus status;
    }
    
    enum ProposalStatus { Pending, Silenced, Active, Executed, Rejected }
    
    struct Member {
        address account;
        uint256 reputationScore; // PoSS combiné
        uint256 joinedAt;
        bool isActive;
    }
    
    // === VARIABLES D'ÉTAT ===
    mapping(address => Member) public members;
    mapping(uint256 => Proposal) public proposals;
    mapping(address => mapping(uint256 => bool)) public hasVoted;
    
    uint256 public proposalCounter;
    uint256 public quorumPercent = 30; // 30% de participation
    uint256 public approvalThreshold = 60; // 60% des voix pondérées
    uint256 public antiForkThreshold = 5; // 5% de la masse de réputation totale
    
    uint256 public constant SILENCE_DURATION = 7 days;
    uint256 public constant VOTING_DURATION = 7 days;
    
    // === ÉVÉNEMENTS ===
    event ProposalCreated(uint256 indexed id, address proposer, string description);
    event VoteCast(uint256 indexed id, address voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 indexed id, bool passed);
    event MemberAdded(address indexed member, uint256 reputation);
    event MemberRemoved(address indexed member);
    
    // === MODIFIERS ===
    modifier onlyActiveMember() {
        require(members[msg.sender].isActive, "Not an active member");
        _;
    }
    
    modifier proposalExists(uint256 proposalId) {
        require(proposals[proposalId].id != 0, "Proposal does not exist");
        _;
    }
    
    // === CONSTRUCTEUR ===
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }
    
    // === GESTION DES MEMBRES ===
    function addMember(address account, uint256 initialReputation) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(!members[account].isActive, "Member already exists");
        members[account] = Member({
            account: account,
            reputationScore: initialReputation,
            joinedAt: block.timestamp,
            isActive: true
        });
        emit MemberAdded(account, initialReputation);
    }
    
    function updateReputation(address account, uint256 newScore) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(members[account].isActive, "Member not active");
        members[account].reputationScore = newScore;
    }
    
    function removeMember(address account) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(members[account].isActive, "Member not active");
        members[account].isActive = false;
        emit MemberRemoved(account);
    }
    
    // === CRÉATION DE PROPOSITION (Phase 1: Proposition) ===
    function createProposal(string memory description, bytes32 parameterHash) 
        external 
        onlyActiveMember 
        returns (uint256) 
    {
        proposalCounter++;
        
        proposals[proposalCounter] = Proposal({
            id: proposalCounter,
            proposer: msg.sender,
            description: description,
            parameterHash: parameterHash,
            votesYes: new uint256[](0),
            votesNo: new uint256[](0),
            totalWeightYes: 0,
            totalWeightNo: 0,
            startTime: block.timestamp + SILENCE_DURATION,
            endTime: block.timestamp + SILENCE_DURATION + VOTING_DURATION,
            silenceEndTime: block.timestamp + SILENCE_DURATION,
            executed: false,
            passed: false,
            status: ProposalStatus.Pending
        });
        
        emit ProposalCreated(proposalCounter, msg.sender, description);
        return proposalCounter;
    }
    
    // === VOTE (Phase 3: Approbation) ===
    function vote(uint256 proposalId, bool support) 
        external 
        onlyActiveMember 
        proposalExists(proposalId) 
    {
        Proposal storage proposal = proposals[proposalId];
        
        require(block.timestamp >= proposal.startTime, "Voting not started");
        require(block.timestamp <= proposal.endTime, "Voting ended");
        require(!hasVoted[msg.sender][proposalId], "Already voted");
        
        hasVoted[msg.sender][proposalId] = true;
        uint256 voterWeight = members[msg.sender].reputationScore;
        
        if (support) {
            proposal.votesYes.push(voterWeight);
            proposal.totalWeightYes = proposal.totalWeightYes.add(voterWeight);
        } else {
            proposal.votesNo.push(voterWeight);
            proposal.totalWeightNo = proposal.totalWeightNo.add(voterWeight);
        }
        
        emit VoteCast(proposalId, msg.sender, support, voterWeight);
    }
    
    // === EXÉCUTION DE LA PROPOSITION (Phase 4: Dépouillement) ===
    function executeProposal(uint256 proposalId) 
        external 
        onlyActiveMember 
        proposalExists(proposalId) 
    {
        Proposal storage proposal = proposals[proposalId];
        
        require(block.timestamp >= proposal.endTime, "Voting not finished");
        require(!proposal.executed, "Proposal already executed");
        require(proposal.status == ProposalStatus.Pending || proposal.status == ProposalStatus.Active, 
                "Invalid proposal status");
        
        uint256 totalWeight = proposal.totalWeightYes.add(proposal.totalWeightNo);
        uint256 totalReputation = getTotalReputation();
        
        // 1. Vérification du Quorum (30%)
        bool quorumMet = totalWeight >= (totalReputation * quorumPercent / 100);
        
        // 2. Vérification du seuil d'approbation (60%)
        bool approvalMet = proposal.totalWeightYes >= (totalWeight * approvalThreshold / 100);
        
        // 3. Vérification du seuil anti-fork (5% de la masse totale)
        bool antiForkMet = proposal.totalWeightYes >= (totalReputation * antiForkThreshold / 100);
        
        proposal.passed = quorumMet && approvalMet && antiForkMet;
        proposal.executed = true;
        proposal.status = proposal.passed ? ProposalStatus.Executed : ProposalStatus.Rejected;
        
        emit ProposalExecuted(proposalId, proposal.passed);
    }
    
    // === FONCTIONS DE VUE ===
    function getTotalReputation() public view returns (uint256 total) {
        total = 0;
        // Note: Dans une implémentation réelle, il faudrait itérer sur les membres
        // ou maintenir un total mis à jour
        return total;
    }
    
    function getProposalStatus(uint256 proposalId) external view returns (ProposalStatus) {
        Proposal storage proposal = proposals[proposalId];
        if (proposal.executed) {
            return proposal.passed ? ProposalStatus.Executed : ProposalStatus.Rejected;
        }
        if (block.timestamp < proposal.silenceEndTime) {
            return ProposalStatus.Silenced;
        }
        if (block.timestamp < proposal.endTime) {
            return ProposalStatus.Active;
        }
        return ProposalStatus.Pending;
    }
    
    function getVoteCounts(uint256 proposalId) external view returns (uint256 yes, uint256 no, uint256 total) {
        Proposal storage proposal = proposals[proposalId];
        return (proposal.totalWeightYes, proposal.totalWeightNo, 
                proposal.totalWeightYes.add(proposal.totalWeightNo));
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./FulusToken.sol";

/**
 * @title MudarabaContract
 * @dev Contrat de mudaraba (partage profits/pertes) sans riba
 * L'investisseur (rabb al-mal) fournit le capital, l'entrepreneur (mudarib) gère le projet
 */
contract MudarabaContract is AccessControl, ReentrancyGuard {
    
    // === STRUCTURES ===
    struct MudarabaAgreement {
        uint256 id;
        address investor;      // Rabb al-mal
        address entrepreneur;  // Mudarib
        uint256 capitalAmount; // En fulus
        uint256 profitShareRatio; // Part de l'entrepreneur (en basis points, ex: 3000 = 30%)
        uint256 startTime;
        uint256 endTime;
        uint256 principalReturned;
        uint256 profitDistributed;
        MudarabaStatus status;
        string projectDescription;
    }
    
    enum MudarabaStatus { Active, Completed, Defaulted, Liquidated }
    
    // === VARIABLES D'ÉTAT ===
    FulusToken public fulusToken;
    mapping(uint256 => MudarabaAgreement) public agreements;
    uint256 public agreementCounter;
    
    // === ÉVÉNEMENTS ===
    event AgreementCreated(uint256 indexed id, address investor, address entrepreneur, uint256 amount);
    event CapitalReturned(uint256 indexed id, uint256 amount);
    event ProfitDistributed(uint256 indexed id, uint256 amount);
    event AgreementSettled(uint256 indexed id, MudarabaStatus status);
    
    // === MODIFIERS ===
    modifier agreementExists(uint256 agreementId) {
        require(agreements[agreementId].id != 0, "Agreement does not exist");
        _;
    }
    
    modifier onlyActiveAgreement(uint256 agreementId) {
        require(agreements[agreementId].status == MudarabaStatus.Active, "Agreement not active");
        _;
    }
    
    // === CONSTRUCTEUR ===
    constructor(address _tokenAddress) {
        fulusToken = FulusToken(_tokenAddress);
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }
    
    // === CRÉATION D'UN CONTRAT DE MUDARABA ===
    function createAgreement(
        address entrepreneur,
        uint256 capitalAmount,
        uint256 profitShareRatio,
        uint256 duration,
        string memory description
    ) external returns (uint256) {
        require(capitalAmount > 0, "Capital must be > 0");
        require(profitShareRatio <= 5000, "Profit share must be <= 50%"); // Max 50%
        require(duration > 0 && duration <= 365 days, "Invalid duration");
        
        // Transfert du capital vers le contrat
        require(fulusToken.transferFrom(msg.sender, address(this), capitalAmount), "Transfer failed");
        
        agreementCounter++;
        
        agreements[agreementCounter] = MudarabaAgreement({
            id: agreementCounter,
            investor: msg.sender,
            entrepreneur: entrepreneur,
            capitalAmount: capitalAmount,
            profitShareRatio: profitShareRatio,
            startTime: block.timestamp,
            endTime: block.timestamp + duration,
            principalReturned: 0,
            profitDistributed: 0,
            status: MudarabaStatus.Active,
            projectDescription: description
        });
        
        // Transfert du capital à l'entrepreneur
        require(fulusToken.transfer(entrepreneur, capitalAmount), "Transfer to entrepreneur failed");
        
        emit AgreementCreated(agreementCounter, msg.sender, entrepreneur, capitalAmount);
        return agreementCounter;
    }
    
    // === RETOUR DU CAPITAL (PAR L'ENTREPRENEUR) ===
    function returnCapital(uint256 agreementId, uint256 amount) 
        external 
        agreementExists(agreementId)
        onlyActiveAgreement(agreementId)
        nonReentrant 
    {
        MudarabaAgreement storage agreement = agreements[agreementId];
        require(msg.sender == agreement.entrepreneur, "Only entrepreneur can return capital");
        require(agreement.principalReturned + amount <= agreement.capitalAmount, "Exceeds principal");
        
        require(fulusToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        agreement.principalReturned += amount;
        
        // Transfert à l'investisseur
        require(fulusToken.transfer(agreement.investor, amount), "Transfer to investor failed");
        
        emit CapitalReturned(agreementId, amount);
        
        // Vérification si le contrat est complètement remboursé
        if (agreement.principalReturned >= agreement.capitalAmount) {
            agreement.status = MudarabaStatus.Completed;
            emit AgreementSettled(agreementId, MudarabaStatus.Completed);
        }
    }
    
    // === DISTRIBUTION DES PROFITS ===
    function distributeProfit(uint256 agreementId, uint256 totalProfit) 
        external 
        agreementExists(agreementId)
        onlyActiveAgreement(agreementId)
        nonReentrant 
    {
        MudarabaAgreement storage agreement = agreements[agreementId];
        require(msg.sender == agreement.entrepreneur, "Only entrepreneur can distribute profit");
        
        uint256 investorShare = totalProfit * (10000 - agreement.profitShareRatio) / 10000;
        uint256 entrepreneurShare = totalProfit * agreement.profitShareRatio / 10000;
        
        require(fulusToken.transferFrom(msg.sender, agreement.investor, investorShare), "Transfer failed");
        require(fulusToken.transferFrom(msg.sender, msg.sender, entrepreneurShare), "Transfer failed");
        
        agreement.profitDistributed += totalProfit;
        
        emit ProfitDistributed(agreementId, totalProfit);
    }
    
    // === LIQUIDATION (EN CAS DE DÉFAUT) ===
    function liquidate(uint256 agreementId) external agreementExists(agreementId) {
        MudarabaAgreement storage agreement = agreements[agreementId];
        require(block.timestamp > agreement.endTime, "Agreement not matured");
        require(agreement.principalReturned < agreement.capitalAmount, "Already completed");
        require(agreement.status == MudarabaStatus.Active, "Not active");
        
        // Note: La liquidation dépend du collateral ou des garanties
        // Version simplifiée : le contrat passe en statut Defaulted
        agreement.status = MudarabaStatus.Defaulted;
        emit AgreementSettled(agreementId, MudarabaStatus.Defaulted);
    }
    
    // === FONCTIONS DE VUE ===
    function getAgreementStatus(uint256 agreementId) external view returns (MudarabaStatus) {
        return agreements[agreementId].status;
    }
    
    function getRemainingPrincipal(uint256 agreementId) external view returns (uint256) {
        MudarabaAgreement storage agreement = agreements[agreementId];
        return agreement.capitalAmount - agreement.principalReturned;
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./FulusToken.sol";

/**
 * @title BridgeContract
 * @dev Pont entre Ethereum Mainnet et BSN Sidechain
 * Permet le verrouillage/déverrouillage des tokens
 */
contract BridgeContract is AccessControl, ReentrancyGuard {
    
    // === STRUCTURES ===
    struct BridgeTransaction {
        uint256 id;
        address user;
        uint256 amount;
        address destinationChain; // Adresse du contrat sur la sidechain
        bool isLocked;
        bool isReleased;
        uint256 timestamp;
        bytes32 merkleProof; // Preuve de l'état de la sidechain
    }
    
    struct BatchSettlement {
        uint256 id;
        bytes32 merkleRoot;
        uint256 timestamp;
        bool finalized;
    }
    
    // === VARIABLES D'ÉTAT ===
    FulusToken public fulusToken;
    mapping(uint256 => BridgeTransaction) public bridgeTransactions;
    mapping(bytes32 => bool) public processedRoots;
    
    uint256 public transactionCounter;
    uint256 public batchCounter;
    
    // Adresses autorisées (oracles / validateurs BSN)
    mapping(address => bool) public validators;
    uint256 public requiredValidatorSignatures = 3;
    
    // === ÉVÉNEMENTS ===
    event TokensLocked(uint256 indexed id, address user, uint256 amount, bytes32 merkleProof);
    event TokensReleased(uint256 indexed id, address user, uint256 amount);
    event BatchSubmitted(uint256 indexed batchId, bytes32 merkleRoot);
    event BatchFinalized(uint256 indexed batchId);
    
    // === MODIFIERS ===
    modifier onlyValidator() {
        require(validators[msg.sender], "Not a validator");
        _;
    }
    
    // === CONSTRUCTEUR ===
    constructor(address _tokenAddress) {
        fulusToken = FulusToken(_tokenAddress);
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }
    
    // === GESTION DES VALIDATEURS ===
    function addValidator(address validator) external onlyRole(DEFAULT_ADMIN_ROLE) {
        validators[validator] = true;
    }
    
    function removeValidator(address validator) external onlyRole(DEFAULT_ADMIN_ROLE) {
        validators[validator] = false;
    }
    
    // === VERROUILLAGE DES TOKENS (Utilisateur → Pont) ===
    function lockTokens(uint256 amount, address destinationChain) 
        external 
        nonReentrant 
        returns (uint256) 
    {
        require(amount > 0, "Amount must be > 0");
        require(destinationChain != address(0), "Invalid destination");
        
        // Transfert des tokens vers le contrat (verrouillage)
        require(fulusToken.transferFrom(msg.sender, address(this), amount), "Transfer failed");
        
        transactionCounter++;
        bytes32 merkleProof = keccak256(abi.encodePacked(transactionCounter, msg.sender, amount, block.timestamp));
        
        bridgeTransactions[transactionCounter] = BridgeTransaction({
            id: transactionCounter,
            user: msg.sender,
            amount: amount,
            destinationChain: destinationChain,
            isLocked: true,
            isReleased: false,
            timestamp: block.timestamp,
            merkleProof: merkleProof
        });
        
        emit TokensLocked(transactionCounter, msg.sender, amount, merkleProof);
        return transactionCounter;
    }
    
    // === DÉVERROUILLAGE DES TOKENS (Pont → Utilisateur) ===
    function releaseTokens(uint256 transactionId) 
        external 
        onlyValidator 
        nonReentrant 
    {
        BridgeTransaction storage tx = bridgeTransactions[transactionId];
        require(tx.isLocked, "Transaction not locked");
        require(!tx.isReleased, "Already released");
        require(tx.user == msg.sender || validators[msg.sender], "Unauthorized");
        
        tx.isReleased = true;
        
        // Transfert des tokens de l'utilisateur
        require(fulusToken.transfer(tx.user, tx.amount), "Transfer failed");
        
        emit TokensReleased(transactionId, tx.user, tx.amount);
    }
    
    // === SOUMISSION DE BATCH (BSN Sidechain → Ethereum) ===
    function submitBatch(bytes32 merkleRoot) external onlyValidator returns (uint256) {
        require(!processedRoots[merkleRoot], "Root already processed");
        
        batchCounter++;
        processedRoots[merkleRoot] = true;
        
        emit BatchSubmitted(batchCounter, merkleRoot);
        return batchCounter;
    }
    
    // === VÉRIFICATION DE PREUVE MERKLE ===
    function verifyMerkleProof(
        bytes32 merkleRoot,
        bytes32 leaf,
        bytes32[] memory proof
    ) public pure returns (bool) {
        bytes32 computedHash = leaf;
        for (uint256 i = 0; i < proof.length; i++) {
            bytes32 proofElement = proof[i];
            if (computedHash < proofElement) {
                computedHash = keccak256(abi.encodePacked(computedHash, proofElement));
            } else {
                computedHash = keccak256(abi.encodePacked(proofElement, computedHash));
            }
        }
        return computedHash == merkleRoot;
    }
    
    // === FONCTIONS DE VUE ===
    function getBridgeTransaction(uint256 id) external view returns (BridgeTransaction memory) {
        return bridgeTransactions[id];
    }
    
    function getTotalLocked() external view returns (uint256) {
        return fulusToken.balanceOf(address(this));
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title WaqfVault
 * @dev Multisig détenant les réserves (or/argent/stablecoins)
 * Hérite du pattern Gnosis Safe avec 5/9 signatures
 */
contract WaqfVault {
    
    // === STRUCTURES ===
    struct Transaction {
        uint256 id;
        address to;
        uint256 value;
        bytes data;
        bool executed;
        uint256 confirmations;
        mapping(address => bool) confirmationsMap;
    }
    
    // === VARIABLES D'ÉTAT ===
    address[] public owners;
    mapping(address => bool) public isOwner;
    uint256 public requiredSignatures;
    
    uint256 public transactionCount;
    mapping(uint256 => Transaction) public transactions;
    
    // === ÉVÉNEMENTS ===
    event TransactionSubmitted(uint256 indexed id, address indexed to, uint256 value);
    event TransactionConfirmed(uint256 indexed id, address indexed owner);
    event TransactionExecuted(uint256 indexed id);
    
    // === MODIFIERS ===
    modifier onlyOwner() {
        require(isOwner[msg.sender], "Not an owner");
        _;
    }
    
    modifier transactionExists(uint256 transactionId) {
        require(transactions[transactionId].id != 0, "Transaction does not exist");
        _;
    }
    
    // === CONSTRUCTEUR ===
    constructor(address[] memory _owners, uint256 _requiredSignatures) {
        require(_owners.length > 0, "Owners required");
        require(_requiredSignatures > 0 && _requiredSignatures <= _owners.length, 
                "Invalid required signatures");
        
        for (uint256 i = 0; i < _owners.length; i++) {
            require(_owners[i] != address(0), "Invalid owner");
            require(!isOwner[_owners[i]], "Duplicate owner");
            
            isOwner[_owners[i]] = true;
            owners.push(_owners[i]);
        }
        
        requiredSignatures = _requiredSignatures;
    }
    
    // === SOUMISSION DE TRANSACTION ===
    function submitTransaction(address to, uint256 value, bytes memory data) 
        external 
        onlyOwner 
        returns (uint256) 
    {
        transactionCount++;
        Transaction storage tx = transactions[transactionCount];
        tx.id = transactionCount;
        tx.to = to;
        tx.value = value;
        tx.data = data;
        tx.executed = false;
        tx.confirmations = 0;
        
        emit TransactionSubmitted(transactionCount, to, value);
        return transactionCount;
    }
    
    // === CONFIRMATION DE TRANSACTION ===
    function confirmTransaction(uint256 transactionId) 
        external 
        onlyOwner 
        transactionExists(transactionId) 
    {
        Transaction storage tx = transactions[transactionId];
        require(!tx.executed, "Transaction already executed");
        require(!tx.confirmationsMap[msg.sender], "Already confirmed");
        
        tx.confirmationsMap[msg.sender] = true;
        tx.confirmations++;
        
        emit TransactionConfirmed(transactionId, msg.sender);
        
        // Exécution automatique si le seuil est atteint
        if (tx.confirmations >= requiredSignatures) {
            executeTransaction(transactionId);
        }
    }
    
    // === EXÉCUTION DE TRANSACTION ===
    function executeTransaction(uint256 transactionId) 
        internal 
        transactionExists(transactionId) 
    {
        Transaction storage tx = transactions[transactionId];
        require(!tx.executed, "Transaction already executed");
        require(tx.confirmations >= requiredSignatures, "Not enough confirmations");
        
        tx.executed = true;
        
        // Exécution de la transaction
        (bool success, ) = tx.to.call{value: tx.value}(tx.data);
        require(success, "Transaction execution failed");
        
        emit TransactionExecuted(transactionId);
    }
    
    // === RÉVOCATION DE CONFIRMATION ===
    function revokeConfirmation(uint256 transactionId) 
        external 
        onlyOwner 
        transactionExists(transactionId) 
    {
        Transaction storage tx = transactions[transactionId];
        require(!tx.executed, "Transaction already executed");
        require(tx.confirmationsMap[msg.sender], "Not confirmed");
        
        tx.confirmationsMap[msg.sender] = false;
        tx.confirmations--;
    }
    
    // === FONCTIONS DE VUE ===
    function getTransaction(uint256 transactionId) 
        external 
        view 
        returns (address to, uint256 value, bytes memory data, bool executed, uint256 confirmations) 
    {
        Transaction storage tx = transactions[transactionId];
        return (tx.to, tx.value, tx.data, tx.executed, tx.confirmations);
    }
    
    function getOwners() external view returns (address[] memory) {
        return owners;
    }
}

# ================================================================
# ANNEXE TECHNIQUE: Modèle de Validation PoSS (Proof of Social Stake)
# ================================================================

import numpy as np