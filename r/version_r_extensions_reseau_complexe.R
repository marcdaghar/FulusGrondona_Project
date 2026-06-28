Réseau complexe avec communautés (clusters) et degrés de connectivité variables.
Feedback macro-micro : L'inflation et la crise affectent les décisions individuelles, qui en retour modifient les agrégats.
Règles de gouvernance : Élection sans candidat de l'Émir et gestion collective du waqf.

# ============================================================
# MODÈLE MONÉTAIRE MIMÉTIQUE AVEC RÉSEAU COMPLEXE, FEEDBACK MACRO-MICRO ET GOUVERNANCE
# ============================================================
# Thèse : Pour une alternative islamique au capitalisme
# Chapitre 2 : Une richesse nommée monnaie
# Concepts : Nuqud/Fulus, Nisab/Zakat, Désir Mimétique, Potentia Multitudinis
# ============================================================

# Chargement des bibliothèques
library(igraph)
library(ggplot2)
library(gridExtra)
library(reshape2)
library(dplyr)

# ============================================================
# 1. DÉFINITION DE LA CLASSE AGENT
# ============================================================

setClass(
  "Agent",
  slots = list(
    id = "numeric",
    wealth = "numeric",
    alpha = "numeric",
    nisab_threshold = "numeric",
    tau_zakat = "numeric",
    risk_aversion = "numeric",
    desire = "numeric",
    adoption_status = "numeric",
    wealth_history = "numeric",
    desire_history = "numeric",
    alpha_history = "numeric"
  )
)

create_agent <- function(id, wealth, alpha, nisab = 100, tau = 0.025) {
  new("Agent",
      id = id,
      wealth = wealth,
      alpha = alpha,
      nisab_threshold = nisab,
      tau_zakat = tau,
      risk_aversion = runif(1, 0.5, 1.5),
      desire = 0.5,
      adoption_status = ifelse(runif(1) < 0.2, 1, 0),
      wealth_history = numeric(),
      desire_history = numeric(),
      alpha_history = numeric()
  )
}

# ============================================================
# 2. CRÉATION DU RÉSEAU SOCIAL AVEC COMMUNAUTÉS
# ============================================================

create_complex_network <- function(num_agents = 150, num_communities = 5) {
  # Créer un réseau avec des communautés (clusters)
  # Utilisation du modèle de "block model" avec des probabilités de connexion différentes
  
  # Assigner chaque agent à une communauté
  community_assignments <- sample(1:num_communities, num_agents, replace = TRUE)
  
  # Matrice de probabilités de connexion entre communautés
  # Forte connectivité intra-communauté, faible inter-communauté
  prob_matrix <- matrix(0.05, nrow = num_communities, ncol = num_communities)
  diag(prob_matrix) <- 0.35  # Probabilité plus élevée à l'intérieur des communautés
  
  # Créer le graphe
  g <- make_empty_graph(n = num_agents, directed = FALSE)
  
  # Ajouter les arêtes selon les probabilités
  for (i in 1:(num_agents - 1)) {
    for (j in (i + 1):num_agents) {
      comm_i <- community_assignments[i]
      comm_j <- community_assignments[j]
      if (runif(1) < prob_matrix[comm_i, comm_j]) {
        g <- add_edges(g, c(i, j))
      }
    }
  }
  
  # Ajouter quelques arêtes aléatoires "small-world" pour connecter les communautés
  num_random_edges <- round(num_agents * 0.1)
  for (k in 1:num_random_edges) {
    i <- sample(1:num_agents, 1)
    j <- sample(1:num_agents, 1)
    if (i != j && !are_adjacent(g, i, j)) {
      g <- add_edges(g, c(i, j))
    }
  }
  
  # Stocker les communautés comme attributs des nœuds
  V(g)$community <- community_assignments
  V(g)$adoption_status <- rep(0, num_agents)
  
  return(g)
}

# ============================================================
# 3. FONCTIONS DE DÉCISION AVEC BRUIT NEURONAL (SOFTMAX)
# ============================================================

softmax_choice <- function(utility_fulus, utility_nuqud, cognitive_temp) {
  # Implémentation du softmax pour la décision d'allocation
  exp_fulus <- exp(utility_fulus / cognitive_temp)
  exp_nuqud <- exp(utility_nuqud / cognitive_temp)
  prob_fulus <- exp_fulus / (exp_fulus + exp_nuqud)
  
  return(prob_fulus)
}

compute_desire <- function(agent, neighbors_desire, inflation_rate) {
  # Calcul du désir mimétique avec influence sociale
  liquidity_need <- runif(1, 0, 1)
  base_desire <- liquidity_need * (1 - slot(agent, "risk_aversion") * 0.1)
  
  # Composante mimétique (influence du voisinage)
  avg_neighbor_desire <- mean(neighbors_desire)
  mimetic_component <- 1 / (1 + exp(-5 * (avg_neighbor_desire - 0.5)))
  
  # Effet de l'inflation sur le désir (feedback macro-micro)
  inflation_effect <- 0.1 * inflation_rate
  
  # Effet du statut d'adoption des voisins
  adoption_boost <- ifelse(any(neighbors_desire > 0.7), 0.3, 0)
  
  # Désir total avec bruit
  desire <- 0.3 * base_desire + 0.4 * mimetic_component + 
            0.2 * adoption_boost + 0.1 * inflation_effect + runif(1, -0.05, 0.05)
  
  return(max(0, min(1, desire)))
}

allocate_wealth <- function(agent, inflation_rate, crisis_level) {
  # Coût de détention du fulus
  cost_fulus <- inflation_rate + slot(agent, "tau_zakat")
  
  # Coût de détention du nuqud (incluant le coût d'opportunité)
  cost_nuqud <- 0.02 + slot(agent, "tau_zakat")
  
  # Feedback macro-micro : la crise augmente la perception du risque
  cost_nuqud <- cost_nuqud * (1 + 0.5 * crisis_level)
  
  # Utilités (inverse des coûts)
  utility_fulus <- 1 / (cost_fulus + 0.01)
  utility_nuqud <- 1 / (cost_nuqud + 0.01)
  
  # Température cognitive (bruit neuronal)
  cognitive_temp <- 0.5 + runif(1, 0, 0.5)
  
  # Softmax
  prob_fulus <- softmax_choice(utility_fulus, utility_nuqud, cognitive_temp)
  
  # Décision stochastique
  if (runif(1) < prob_fulus) {
    new_alpha <- min(1, slot(agent, "alpha") + 0.05)
  } else {
    new_alpha <- max(0, slot(agent, "alpha") - 0.05)
  }
  
  return(new_alpha)
}

# ============================================================
# 4. FONCTIONS DE GOUVERNANCE
# ============================================================

elect_emir <- function(agents, g) {
  # Élection sans candidat : l'Émir est choisi par un tirage au sort
  # pondéré par la richesse (les plus riches ont plus de "sagesse" ou d'influence)
  wealths <- sapply(agents, function(a) slot(a, "wealth"))
  prob_weights <- wealths / sum(wealths)
  emir_index <- sample(1:length(agents), 1, prob = prob_weights)
  
  return(emir_index)
}

manage_waqf <- function(agents, g, emir_index, waqf_pool) {
  # Gestion collective du waqf : l'Émir décide de l'allocation des fonds
  # 60% pour les projets communautaires, 40% pour la redistribution
  
  community_projects <- 0.6 * waqf_pool
  redistribution <- 0.4 * waqf_pool
  
  # Projets communautaires : investissement dans les agents les plus pauvres
  # ou dans les communautés les moins représentées
  wealths <- sapply(agents, function(a) slot(a, "wealth"))
  poor_agents <- which(wealths < quantile(wealths, 0.25))
  
  if (length(poor_agents) > 0) {
    investment_per_agent <- community_projects / length(poor_agents)
    for (idx in poor_agents) {
      new_wealth <- slot(agents[[idx]], "wealth") + investment_per_agent
      slot(agents[[idx]], "wealth") <- new_wealth
    }
  }
  
  # Redistribution directe aux plus pauvres
  if (redistribution > 0) {
    num_recipients <- min(round(0.2 * length(agents)), length(poor_agents))
    if (num_recipients > 0) {
      redist_per_agent <- redistribution / num_recipients
      recipients <- sample(poor_agents, num_recipients)
      for (idx in recipients) {
        new_wealth <- slot(agents[[idx]], "wealth") + redist_per_agent
        slot(agents[[idx]], "wealth") <- new_wealth
      }
    }
  }
  
  return(list(agents = agents, waqf_remaining = 0))
}

# ============================================================
# 5. PROPAGATION DE L'ADOPTION (ÉPIDÉMIE)
# ============================================================

spread_adoption <- function(agent, g, agent_idx) {
  # L'adoption se propage via le réseau social
  neighbors <- neighbors(g, agent_idx)
  if (length(neighbors) > 0) {
    # Proportion de voisins adoptants
    neighbors_adoption <- V(g)$adoption_status[neighbors]
    adoption_ratio <- mean(neighbors_adoption)
    
    # Probabilité d'adoption
    desire_level <- slot(agent, "desire")
    prob_adoption <- 0.1 * adoption_ratio + 0.3 * desire_level
    
    if (runif(1) < prob_adoption && slot(agent, "adoption_status") == 0) {
      slot(agent, "adoption_status") <- 1
      V(g)$adoption_status[agent_idx] <- 1
    }
  }
}

# ============================================================
# 6. SIMULATION PRINCIPALE
# ============================================================

run_simulation <- function(num_agents = 150, num_steps = 200, num_communities = 5) {
  # 6.1 Initialisation
  set.seed(42)
  
  # Créer les agents
  agents <- list()
  for (i in 1:num_agents) {
    wealth <- (20 * (1 / runif(1))^(1/1.5)) + 10
    wealth <- min(wealth, 500)
    alpha <- runif(1, 0.2, 0.8)
    agents[[i]] <- create_agent(i, wealth, alpha)
  }
  
  # Créer le réseau
  g <- create_complex_network(num_agents, num_communities)
  
  # 6.2 Variables globales
  total_wealth_history <- numeric()
  avg_alpha_history <- numeric()
  avg_desire_history <- numeric()
  gini_history <- numeric()
  crisis_history <- numeric()
  inflation_history <- numeric()
  velocity_history <- numeric()
  zakat_pool <- 0
  waqf_pool <- 0
  emir_index <- NULL
  
  # 6.3 Boucle principale
  for (step in 1:num_steps) {
    cat("Étape:", step, "\n")
    
    # ---- MACRO : Calcul des variables agrégées ----
    wealths <- sapply(agents, function(a) slot(a, "wealth"))
    alphas <- sapply(agents, function(a) slot(a, "alpha"))
    desires <- sapply(agents, function(a) slot(a, "desire"))
    
    total_wealth <- sum(wealths)
    avg_alpha <- mean(alphas)
    avg_desire <- mean(desires)
    
    # Coefficient de Gini
    sorted_wealth <- sort(wealths)
    n <- length(sorted_wealth)
    cumulative <- cumsum(sorted_wealth)
    gini <- (2 * sum((1:n) * sorted_wealth) / (n * sum(sorted_wealth))) - (n + 1) / n
    
    # Niveau de crise (dispersion du désir)
    desire_sd <- sd(desires)
    crisis_level <- min(1, desire_sd * 2)
    
    # Inflation
    money_supply_growth <- 0.03
    economic_growth <- 0.02
    inflation_rate <- max(0, money_supply_growth - economic_growth + crisis_level * 0.5)
    
    # Vélocité de la monnaie
    if (crisis_level > 0) {
      velocity <- 1.5 * exp(2 * crisis_level)
    } else {
      velocity <- 1.5
    }
    
    # ---- MICRO : Mises à jour individuelles ----
    for (i in 1:num_agents) {
      agent <- agents[[i]]
      
      # Calcul du désir avec influence des voisins
      neighbors_idx <- neighbors(g, i)
      if (length(neighbors_idx) > 0) {
        neighbors_desire <- sapply(neighbors_idx, function(idx) slot(agents[[idx]], "desire"))
        avg_neighbor_desire <- mean(neighbors_desire)
      } else {
        avg_neighbor_desire <- 0.5
      }
      
      # Le désir est influencé par le contexte macro (feedback)
      new_desire <- compute_desire(agent, rep(avg_neighbor_desire, 3), inflation_rate)
      slot(agent, "desire") <- new_desire
      
      # Allocation de la richesse (avec bruit neuronal)
      new_alpha <- allocate_wealth(agent, inflation_rate, crisis_level)
      slot(agent, "alpha") <- new_alpha
      
      # Propagation de l'adoption via le réseau
      spread_adoption(agent, g, i)
      
      # Paiement de la Zakat
      if (slot(agent, "wealth") > slot(agent, "nisab_threshold")) {
        zakat_amount <- slot(agent, "tau_zakat") * (slot(agent, "wealth") - slot(agent, "nisab_threshold"))
        new_wealth <- slot(agent, "wealth") - zakat_amount
        slot(agent, "wealth") <- new_wealth
        zakat_pool <- zakat_pool + 0.8 * zakat_amount
        waqf_pool <- waqf_pool + 0.2 * zakat_amount
      }
      
      # Échanges commerciaux
      trade_gain <- rnorm(1, 0, 1) * 0.1
      slot(agent, "wealth") <- slot(agent, "wealth") + trade_gain
      
      # Enregistrement de l'historique
      slot(agent, "wealth_history") <- c(slot(agent, "wealth_history"), slot(agent, "wealth"))
      slot(agent, "desire_history") <- c(slot(agent, "desire_history"), slot(agent, "desire"))
      slot(agent, "alpha_history") <- c(slot(agent, "alpha_history"), slot(agent, "alpha"))
    }
    
    # ---- REDISTRIBUTION DE LA ZAKAT ----
    if (zakat_pool > 0) {
      wealths_updated <- sapply(agents, function(a) slot(a, "wealth"))
      poor_indices <- which(wealths_updated < quantile(wealths_updated, 0.2))
      if (length(poor_indices) > 0) {
        zakat_per_agent <- zakat_pool / length(poor_indices)
        for (idx in poor_indices) {
          new_wealth <- slot(agents[[idx]], "wealth") + zakat_per_agent
          slot(agents[[idx]], "wealth") <- new_wealth
        }
      }
      zakat_pool <- 0
    }
    
    # ---- GOUVERNANCE : Élection de l'Émir et gestion du Waqf ----
    if (step %% 30 == 0) {
      # Élection sans candidat
      emir_index <- elect_emir(agents, g)
      
      # Gestion du Waqf
      if (waqf_pool > 0) {
        result <- manage_waqf(agents, g, emir_index, waqf_pool)
        agents <- result$agents
        waqf_pool <- result$waqf_remaining
      }
    }
    
    # ---- ENREGISTREMENT DES DONNÉES AGRÉGÉES ----
    total_wealth_history <- c(total_wealth_history, total_wealth)
    avg_alpha_history <- c(avg_alpha_history, avg_alpha)
    avg_desire_history <- c(avg_desire_history, avg_desire)
    gini_history <- c(gini_history, gini)
    crisis_history <- c(crisis_history, crisis_level)
    inflation_history <- c(inflation_history, inflation_rate)
    velocity_history <- c(velocity_history, velocity)
  }
  
  # ---- RÉSULTATS ----
  results <- list(
    total_wealth = total_wealth_history,
    avg_alpha = avg_alpha_history,
    avg_desire = avg_desire_history,
    gini = gini_history,
    crisis = crisis_history,
    inflation = inflation_history,
    velocity = velocity_history,
    agents = agents,
    network = g
  )
  
  return(results)
}

# ============================================================
# 7. VISUALISATION DES RÉSULTATS
# ============================================================

plot_results <- function(results) {
  # Créer un dataframe pour ggplot
  df <- data.frame(
    step = 1:length(results$total_wealth),
    total_wealth = results$total_wealth,
    avg_alpha = results$avg_alpha,
    avg_desire = results$avg_desire,
    gini = results$gini,
    crisis = results$crisis,
    inflation = results$inflation,
    velocity = results$velocity
  )
  
  # 1. Richesse totale
  p1 <- ggplot(df, aes(x = step, y = total_wealth)) +
    geom_line(color = "darkgreen", size = 1) +
    labs(title = "Richesse Totale", x = "Temps", y = "Richesse") +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5))
  
  # 2. Allocation (Alpha)
  p2 <- ggplot(df, aes(x = step, y = avg_alpha)) +
    geom_line(color = "blue", size = 1) +
    labs(title = "Allocation Moyenne (Fulus/Nuqud)", x = "Temps", y = "Alpha") +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5))
  
  # 3. Désir mimétique
  p3 <- ggplot(df, aes(x = step, y = avg_desire)) +
    geom_line(color = "brown", size = 1) +
    labs(title = "Désir Mimétique Collectif", x = "Temps", y = "Désir") +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5))
  
  # 4. Crise et Inflation
  df_crisis <- melt(df[, c("step", "crisis", "inflation", "velocity")], id.vars = "step")
  p4 <- ggplot(df_crisis, aes(x = step, y = value, color = variable)) +
    geom_line(size = 1) +
    labs(title = "Crise, Inflation et Vélocité", x = "Temps", y = "Valeur") +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5), legend.position = "top")
  
  # 5. Coefficient de Gini
  p5 <- ggplot(df, aes(x = step, y = gini)) +
    geom_line(color = "black", size = 1) +
    labs(title = "Coefficient de Gini (Inégalité)", x = "Temps", y = "Gini") +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5))
  
  # Disposition des graphiques
  grid.arrange(p1, p2, p3, p4, p5, ncol = 2, nrow = 3)
}

# ============================================================
# 8. VISUALISATION DU RÉSEAU
# ============================================================

plot_network <- function(g, agents) {
  # Couleurs des nœuds en fonction du statut d'adoption
  adoption_status <- sapply(agents, function(a) slot(a, "adoption_status"))
  V(g)$color <- ifelse(adoption_status == 1, "green", "blue")
  
  # Taille des nœuds en fonction de la richesse (log)
  wealths <- sapply(agents, function(a) slot(a, "wealth"))
  V(g)$size <- 5 + log(wealths + 1)
  
  # Visualisation du réseau
  plot(g, 
       vertex.label = NA,
       vertex.size = V(g)$size,
       vertex.color = V(g)$color,
       main = "Réseau Social avec Communautés et Statut d'Adoption")
  
  # Légende
  legend("bottomright", 
         legend = c("Non-Adoptant", "Adoptant"),
         col = c("blue", "green"),
         pch = 19,
         title = "Statut")
}

# ============================================================
# 9. EXÉCUTION DE LA SIMULATION
# ============================================================

# Exécuter la simulation
cat("Démarrage de la simulation...\n")
results <- run_simulation(num_agents = 150, num_steps = 150, num_communities = 5)

# Afficher les graphiques
cat("Visualisation des résultats...\n")
plot_results(results)

# Visualisation du réseau final
cat("Visualisation du réseau...\n")
plot_network(results$network, results$agents)

# ============================================================
# 10. STATISTIQUES FINALES
# ============================================================

cat("\n--- STATISTIQUES FINALES ---\n")
cat("Richesse Totale Finale:", tail(results$total_wealth, 1), "\n")
cat("Gini Final:", tail(results$gini, 1), "\n")
cat("Alpha Moyen Final:", tail(results$avg_alpha, 1), "\n")
cat("Inflation Moyenne:", mean(results$inflation), "\n")
cat("Crise Moyenne:", mean(results$crisis), "\n")

# --- FIN DU CODE R ---

Le réseau est construit avec des communautés (clusters) qui ont une forte connectivité interne et une faible connectivité externe. Cela simule des groupes d'agents partageant des croyances ou des pratiques communes.
prob_matrix <- matrix(0.05, nrow = num_communities, ncol = num_communities)
diag(prob_matrix) <- 0.35  # Connectivité intra-communauté plus élevée
Chaque agent appartient à une communauté, et la probabilité de connexion avec un agent d'une autre communauté est plus faible. Cela crée un effet de "bulle" qui ralentit la propagation de l'adoption et des idées, mais peut aussi la concentrer.
L'influence se fait dans les deux sens :
Macro → Micro : L'inflation et la crise affectent les décisions individuelles.
# L'inflation augmente le désir d'argent
inflation_effect <- 0.1 * inflation_rate

# La crise augmente la perception du risque du nuqud
cost_nuqud <- cost_nuqud * (1 + 0.5 * crisis_level)
Micro → Macro : Les décisions individuelles (allocations, désir) modifient les agrégats.
# Le désir moyen influence le niveau de crise
desire_sd <- sd(desires)
crisis_level <- min(1, desire_sd * 2)
Ce feedback crée des cycles (pro-cycliques ou contra-cycliques) qui peuvent générer des bulles ou des krachs endogènes.
elect_emir <- function(agents, g) {
  wealths <- sapply(agents, function(a) slot(a, "wealth"))
  prob_weights <- wealths / sum(wealths)
  emir_index <- sample(1:length(agents), 1, prob = prob_weights)
  return(emir_index)
}
L'Émir est choisi par un tirage au sort pondéré par la richesse (les plus riches ont plus d'"influence"). C'est une forme de sortition qui évite les luttes de pouvoir et reflète la notion islamique de "meilleur d'entre vous" (khayrukum).
manage_waqf <- function(agents, g, emir_index, waqf_pool) {
  community_projects <- 0.6 * waqf_pool
  redistribution <- 0.4 * waqf_pool
  
  # Investissement dans les plus pauvres et dans les communautés
  # ...
}
Le waqf est géré collectivement : l'Émir décide de l'allocation, mais selon des règles prédéfinies :
60% pour des projets communautaires (infrastructure, éducation, santé).
40% pour la redistribution directe aux plus pauvres.
Cela crée un stabilisateur automatique qui réduit les inégalités et maintient la cohésion sociale.

Aspect
Python
NetLogo
R
Objectif
Analyse quantitative
Visualisation dynamique
Analyse avancée + visualisation
Réseau
Implicite (moyenne)
Explicit (petit monde)
Complexe (communautés)
Feedback macro-micro
Partiel
Partiel
Complet
Gouvernance
Non implémenté
Non implémenté
Émir + Waqf
Visualisation
Statique (Matplotlib)
Animée (interface)
Statique + Réseau (ggplot2/igraph)
Performance
Rapide
Modérée
Rapide


Modèles de Markov : Pour capturer les transitions d'état des agents (adoption/non-adoption) avec des probabilités dépendantes du contexte.
Modèles de réseau temporel : Les connexions peuvent évoluer dans le temps, reflétant les changements d'allégeance communautaire.
Théorie des jeux : Introduire des interactions stratégiques entre agents pour modéliser la coordination monétaire.
Calibration sur données réelles : Utiliser des données de transactions monétaires ou de comportement économique pour ajuster les paramètres.

Souhaitez-vous que je développe l'une de ces extensions, ou que je fournisse une version du code en MATLAB ?
