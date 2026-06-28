// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title FulusToken
 * @dev Jeton ERC-20 représentant le crypto-fulus
 * Émission contrôlée par la DAO (guildDAO)
 * Pas de minting automatique - uniquement par décision de la DAO
 */
contract FulusToken is ERC20, ERC20Burnable, AccessControl, Pausable {
    bytes32 public constant DAO_ROLE = keccak256("DAO_ROLE");
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");

    uint256 public maxSupply;
    uint256 public mintingFee;  // Frais de minting (en wei)
    uint256 public transferFee; // Frais de transfert (en basis points, 1 = 0.01%)

    event MintingFeeUpdated(uint256 newFee);
    event TransferFeeUpdated(uint256 newFee);
    event MaxSupplyUpdated(uint256 newMaxSupply);

    constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply,
        uint256 _maxSupply
    ) ERC20(name, symbol) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(DAO_ROLE, msg.sender);
        _grantRole(EMERGENCY_ROLE, msg.sender);

        maxSupply = _maxSupply;
        require(initialSupply <= maxSupply, "Initial supply exceeds max supply");
        _mint(msg.sender, initialSupply);
    }

    /**
     * @dev Minting contrôlé par la DAO uniquement
     * Émission adossée à des réserves (or/argent)
     */
    function mint(address to, uint256 amount) external onlyRole(DAO_ROLE) whenNotPaused {
        require(totalSupply() + amount <= maxSupply, "Exceeds max supply");
        _mint(to, amount);
    }

    /**
     * @dev Brûlage des tokens (retrait du circuit)
     */
    function burn(uint256 amount) public override {
        super.burn(amount);
    }

    /**
     * @dev Transfert avec frais (contre-thésaurisation)
     */
    function transfer(address recipient, uint256 amount) public override whenNotPaused returns (bool) {
        if (transferFee > 0) {
            uint256 fee = (amount * transferFee) / 10000; // basis points
            uint256 amountAfterFee = amount - fee;
            _transfer(_msgSender(), recipient, amountAfterFee);
            _burn(_msgSender(), fee); // Les frais sont brûlés (déflation)
        } else {
            _transfer(_msgSender(), recipient, amount);
        }
        return true;
    }

    /**
     * @dev Paramètres ajustables par la DAO
     */
    function setMaxSupply(uint256 newMaxSupply) external onlyRole(DAO_ROLE) {
        require(newMaxSupply >= totalSupply(), "Cannot be less than current supply");
        maxSupply = newMaxSupply;
        emit MaxSupplyUpdated(newMaxSupply);
    }

    function setTransferFee(uint256 newFee) external onlyRole(DAO_ROLE) {
        require(newFee <= 1000, "Fee cannot exceed 10%");
        transferFee = newFee;
        emit TransferFeeUpdated(newFee);
    }

    function pause() external onlyRole(EMERGENCY_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(EMERGENCY_ROLE) {
        _unpause();
    }
}
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title GuildDAO
 * @dev DAO de guilde pour la gouvernance monétaire
 * Mécanisme DAV (Delayed Approval Voting)
 * Un membre = une voix (pondéré par réputation)
 */
contract GuildDAO is AccessControl, ReentrancyGuard {
    bytes32 public constant MEMBER_ROLE = keccak256("MEMBER_ROLE");
    bytes32 public constant EMIR_ROLE = keccak256("EMIR_ROLE");

    // Structure d'une proposition
    struct Proposal {
        uint256 id;
        address proposer;
        string description;  // Description technique
        uint256 parameter;   // Valeur du paramètre (θ)
        uint256 startTime;
        uint256 votingEndTime;
        uint256 quorum;      // Quorum requis (en %)
        uint256 threshold;   // Seuil d'approbation (en %)
        uint256 yesVotes;
        uint256 noVotes;
        bool executed;
        bool approved;
    }

    // Mapping des membres vers leur poids de réputation
    mapping(address => uint256) public reputationWeight;

    // Propositions
    Proposal[] public proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;

    // Paramètres de la guilde
    uint256 public votingPeriod = 7 days;
    uint256 public silencePeriod = 7 days;
    uint256 public defaultQuorum = 30; // 30%
    uint256 public defaultThreshold = 60; // 60%
    uint256 public minParticipation = 5; // 5% de la masse monétaire

    event ProposalCreated(uint256 indexed id, address proposer, string description, uint256 parameter);
    event VoteCast(uint256 indexed id, address voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 indexed id, bool approved);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(MEMBER_ROLE, msg.sender);
    }

    /**
     * @dev Créer une proposition (phase 1)
     */
    function createProposal(
        string memory _description,
        uint256 _parameter
    ) external onlyRole(MEMBER_ROLE) returns (uint256) {
        require(bytes(_description).length > 0, "Description cannot be empty");

        uint256 proposalId = proposals.length;
        proposals.push(Proposal({
            id: proposalId,
            proposer: msg.sender,
            description: _description,
            parameter: _parameter,
            startTime: block.timestamp + silencePeriod,
            votingEndTime: block.timestamp + silencePeriod + votingPeriod,
            quorum: defaultQuorum,
            threshold: defaultThreshold,
            yesVotes: 0,
            noVotes: 0,
            executed: false,
            approved: false
        }));

        emit ProposalCreated(proposalId, msg.sender, _description, _parameter);
        return proposalId;
    }

    /**
     * @dev Voter sur une proposition (phase 3 - approbation)
     */
    function vote(uint256 _proposalId, bool _support) external onlyRole(MEMBER_ROLE) nonReentrant {
        Proposal storage proposal = proposals[_proposalId];
        require(block.timestamp >= proposal.startTime, "Voting not started");
        require(block.timestamp <= proposal.votingEndTime, "Voting ended");
        require(!hasVoted[_proposalId][msg.sender], "Already voted");

        uint256 weight = reputationWeight[msg.sender];
        require(weight > 0, "Zero reputation weight");

        hasVoted[_proposalId][msg.sender] = true;

        if (_support) {
            proposal.yesVotes += weight;
        } else {
            proposal.noVotes += weight;
        }

        emit VoteCast(_proposalId, msg.sender, _support, weight);
    }

    /**
     * @dev Exécuter la proposition (phase 4)
     */
    function executeProposal(uint256 _proposalId) external onlyRole(EMIR_ROLE) nonReentrant {
        Proposal storage proposal = proposals[_proposalId];
        require(block.timestamp > proposal.votingEndTime, "Voting not ended");
        require(!proposal.executed, "Already executed");

        uint256 totalVotes = proposal.yesVotes + proposal.noVotes;
        uint256 totalWeight = getTotalReputation();

        // Vérification du quorum
        require((totalVotes * 100) / totalWeight >= proposal.quorum, "Quorum not reached");

        // Vérification du seuil d'approbation
        bool approved = (proposal.yesVotes * 100) / totalVotes >= proposal.threshold;

        // Vérification du seuil anti-fork (Oui - Non ≥ 5% de la masse monétaire)
        uint256 minDiff = getMinParticipation();
        require(proposal.yesVotes - proposal.noVotes >= minDiff, "Anti-fork threshold not met");

        proposal.approved = approved;
        proposal.executed = true;

        emit ProposalExecuted(_proposalId, approved);
    }

    /**
     * @dev Gérer la réputation (PoSS)
     */
    function updateReputation(address _member, uint256 _newWeight) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(_newWeight > 0, "Weight must be positive");
        reputationWeight[_member] = _newWeight;
    }

    /**
     * @dev Getters
     */
    function getTotalReputation() public view returns (uint256) {
        uint256 total = 0;
        // Dans une implémentation réelle, on itérerait sur les membres
        // Ici, on simule avec les poids stockés
        for (uint256 i = 0; i < 100; i++) {
            // Simulation
        }
        return total;
    }

    function getMinParticipation() public view returns (uint256) {
        // 5% de la masse monétaire totale
        // À implémenter avec le contrat FulusToken
        return minParticipation;
    }
}
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./FulusToken.sol";

/**
 * @title MudarabaContract
 * @dev Contrat de mudaraba (association capital-travail)
 * Financement sans intérêt (riba), partage des profits et pertes
 */
contract MudarabaContract is AccessControl, ReentrancyGuard {
    bytes32 public constant INVESTOR_ROLE = keccak256("INVESTOR_ROLE");
    bytes32 public constant MUDARIB_ROLE = keccak256("MUDARIB_ROLE");
    bytes32 public constant ARBITRATOR_ROLE = keccak256("ARBITRATOR_ROLE");

    FulusToken public fulusToken;

    struct Mudaraba {
        uint256 id;
        address rabbAlMal;    // Investisseur (capital)
        address mudarib;       // Entrepreneur (travail)
        uint256 capital;       // Capital en fulus
        uint256 startTime;
        uint256 duration;      // Durée en jours
        uint256 profitShare;   // Part du profit pour le mudarib (en %)
        uint256 capitalReturned;
        uint256 profitAccrued;
        bool active;
        bool settled;
    }

    Mudaraba[] public mudarabas;
    mapping(uint256 => mapping(address => bool)) public hasVotedOnSettlement;

    event MudarabaCreated(uint256 indexed id, address rabbAlMal, address mudarib, uint256 capital);
    event MudarabaSettled(uint256 indexed id, uint256 capitalReturned, uint256 profitAccrued);
    event ProfitDistributed(uint256 indexed id, address indexed recipient, uint256 amount);

    constructor(address _fulusToken) {
        fulusToken = FulusToken(_fulusToken);
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    /**
     * @dev Créer une mudaraba
     */
    function createMudaraba(
        address _mudarib,
        uint256 _capital,
        uint256 _duration,
        uint256 _profitShare
    ) external onlyRole(INVESTOR_ROLE) nonReentrant returns (uint256) {
        require(_capital > 0, "Capital must be positive");
        require(_duration > 0, "Duration must be positive");
        require(_profitShare > 0 && _profitShare <= 100, "Profit share must be between 1 and 100");
        require(fulusToken.balanceOf(msg.sender) >= _capital, "Insufficient balance");

        // Transfert du capital de l'investisseur vers le contrat
        fulusToken.transferFrom(msg.sender, address(this), _capital);

        uint256 id = mudarabas.length;
        mudarabas.push(Mudaraba({
            id: id,
            rabbAlMal: msg.sender,
            mudarib: _mudarib,
            capital: _capital,
            startTime: block.timestamp,
            duration: _duration,
            profitShare: _profitShare,
            capitalReturned: 0,
            profitAccrued: 0,
            active: true,
            settled: false
        }));

        emit MudarabaCreated(id, msg.sender, _mudarib, _capital);
        return id;
    }

    /**
     * @dev Règlement de la mudaraba (partage des profits)
     */
    function settleMudaraba(
        uint256 _id,
        uint256 _capitalReturned,
        uint256 _profitAccrued
    ) external onlyRole(MUDARIB_ROLE) nonReentrant {
        Mudaraba storage m = mudarabas[_id];
        require(m.active, "Mudaraba not active");
        require(!m.settled, "Already settled");
        require(block.timestamp >= m.startTime + m.duration * 1 days, "Duration not elapsed");

        // Calcul des parts
        uint256 mudaribShare = (_profitAccrued * m.profitShare) / 100;
        uint256 investorShare = _profitAccrued - mudaribShare;

        // Transfert des montants
        if (_capitalReturned > 0) {
            fulusToken.transfer(m.rabbAlMal, _capitalReturned);
            m.capitalReturned = _capitalReturned;
        }

        if (investorShare > 0) {
            fulusToken.transfer(m.rabbAlMal, investorShare);
        }

        if (mudaribShare > 0) {
            fulusToken.transfer(m.mudarib, mudaribShare);
        }

        m.profitAccrued = _profitAccrued;
        m.settled = true;
        m.active = false;

        emit MudarabaSettled(_id, _capitalReturned, _profitAccrued);
    }

    /**
     * @dev Forcer la liquidation en cas de litige (arbitrage)
     */
    function forceSettlement(
        uint256 _id,
        uint256 _capitalReturned,
        uint256 _profitAccrued,
        bool _inFavorOfRabAlMal
    ) external onlyRole(ARBITRATOR_ROLE) nonReentrant {
        Mudaraba storage m = mudarabas[_id];
        require(m.active, "Mudaraba not active");
        require(!m.settled, "Already settled");

        // Règlement forcé selon l'arbitrage
        // ... (logique simplifiée)
        m.settled = true;
        m.active = false;
    }
}

# -*- coding: utf-8 -*-
"""
Simulation du pilote Dora (Beyrouth, Liban)
Zone industrielle de Dora - 30 à 50 PME
Modèle de transition vers le crypto-fulus
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt