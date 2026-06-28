// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract CryptoFulus {
    // Le propriétaire est la guilde ou le muhtassib
    address public owner;
    string public name = "Crypto-Fulus";
    string public symbol = "FUL";

    // Mapping des soldes des travailleurs
    mapping(address => uint256) public balances;
    // Mapping des certificats de travail (preuve de travail)
    mapping(address => bool) public hasWorkCertificate;

    // Événements pour la traçabilité
    event WorkCertified(address indexed worker, uint256 amount);
    event FulusTransfered(address indexed from, address indexed to, uint256 amount);

    // Modificateur pour le propriétaire (la guilde)
    modifier onlyOwner() {
        require(msg.sender == owner, "Seul le proprietaire peut certifier le travail.");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    // 1. Fonction de certification du travail (émission de fulus)
    // Le propriétaire (guilde) certifie que le travailleur a produit une valeur
    function certifyWork(address _worker, uint256 _hoursWorked) public onlyOwner {
        require(_worker != address(0), "Adresse invalide.");
        // L'émission est basée sur une unité de travail (ex: 10 FUL par heure)
        uint256 emissionRate = 10;
        uint256 fulusToMint = _hoursWorked * emissionRate;

        // Émettre les nouveaux fulus (monnaie-travail)
        balances[_worker] += fulusToMint;
        // Enregistrer le certificat de travail
        hasWorkCertificate[_worker] = true;

        emit WorkCertified(_worker, fulusToMint);
    }

    // 2. Fonction de transfert (échange de biens et services)
    function transferFulus(address _to, uint256 _amount) public {
        require(_to != address(0), "Adresse invalide.");
        require(balances[msg.sender] >= _amount, "Solde insuffisant.");

        balances[msg.sender] -= _amount;
        balances[_to] += _amount;

        emit FulusTransfered(msg.sender, _to, _amount);
    }

    // 3. Fonction de conversion en Dinar/Dirham (ancrage bimétallique)
    // Cette fonction serait appelée par un oracle qui donne le prix de l'or/argent
    function convertToDinar(uint256 _fulusAmount) public view returns (uint256) {
        // Taux de change fixe (ex: 1 Dinar = 100 Fulus)
        uint256 exchangeRate = 100;
        return _fulusAmount / exchangeRate;
    }

    // 4. Récupérer le solde
    function getBalance(address _user) public view returns (uint256) {
        return balances[_user];
    }
}

Ce code R permet de valider l'hypothèse selon laquelle les périodes de monnaie-fiat (fulus) non convertible sont corrélées à des crises hyperinflationnistes, comme celles décrites par Al-Maqrîzî.
# Données historiques simulées (Mamelouks, Allemagne, etc.)
# colonnes: Year, Money_Supply_Growth, Inflation, Crisis_Event

# 1. Créer un jeu de données simulé
set.seed(123)
Years <- seq(1200, 1300, by=1)
Money_Growth <- rnorm(length(Years), mean=0.05, sd=0.02) # Croissance monétaire
Inflation <- 0.5 + 2 * Money_Growth + rnorm(length(Years), sd=0.1) # Inflation corrélée
Crisis_Event <- ifelse(Inflation > 2.5, 1, 0) # Hyperinflation > 250%

data <- data.frame(Years, Money_Growth, Inflation, Crisis_Event)

# 2. Visualiser la relation