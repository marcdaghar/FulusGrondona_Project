Modèles de Markov : Transitions d'état des agents (adoption/non-adoption) avec probabilités dépendantes du contexte.
Modèles de réseau temporel : Les connexions évoluent dans le temps, reflétant les changements d'allégeance communautaire.
Théorie des jeux : Interactions stratégiques entre agents pour modéliser la coordination monétaire.

%% ============================================================
% MODÈLE MONÉTAIRE MIMÉTIQUE AVEC MARKOV, RÉSEAU TEMPOREL ET THÉORIE DES JEUX
% ============================================================
% Thèse : Pour une alternative islamique au capitalisme
% Chapitre 2 : Une richesse nommée monnaie
% Concepts : Nuqud/Fulus, Nisab/Zakat, Désir Mimétique, Potentia Multitudinis
% ============================================================

% ============================================================
% 1. PARAMÈTRES GLOBAUX
% ============================================================

function run_simulation()
    % Paramètres de la simulation
    num_agents = 150;
    num_steps = 200;
    num_communities = 5;
    
    % Initialisation
    rng(42);  % Pour la reproductibilité
    
    % Création des agents
    agents = create_agents(num_agents);
    
    % Création du réseau initial
    [g, community_assignments] = create_complex_network(num_agents, num_communities);
    
    % Variables pour les modèles de Markov
    transition_matrix = zeros(2, 2);  % [non-adoptant -> adoptant, etc.]
    adoption_history = zeros(num_agents, num_steps);
    
    % Variables de réseau temporel
    network_history = cell(num_steps, 1);
    community_affiliation_history = zeros(num_agents, num_steps);
    
    % Variables macroéconomiques
    total_wealth_history = zeros(num_steps, 1);
    avg_alpha_history = zeros(num_steps, 1);
    avg_desire_history = zeros(num_steps, 1);
    gini_history = zeros(num_steps, 1);
    crisis_history = zeros(num_steps, 1);
    inflation_history = zeros(num_steps, 1);
    velocity_history = zeros(num_steps, 1);
    zakat_pool = 0;
    waqf_pool = 0;
    emir_index = 0;
    
    % ============================================================
    % 2. BOUCLE PRINCIPALE
    % ============================================================
    
    for step = 1:num_steps
        fprintf('Étape: %d\n', step);
        
        % ---- MACRO : Calcul des variables agrégées ----
        wealths = [agents.wealth];
        alphas = [agents.alpha];
        desires = [agents.desire];
        
        total_wealth = sum(wealths);
        avg_alpha = mean(alphas);
        avg_desire = mean(desires);
        
        % Coefficient de Gini
        sorted_wealth = sort(wealths);
        n = length(sorted_wealth);
        cumulative = cumsum(sorted_wealth);
        gini = (2 * sum((1:n) .* sorted_wealth) / (n * sum(sorted_wealth))) - (n + 1) / n;
        
        % Niveau de crise (dispersion du désir)
        desire_sd = std(desires);
        crisis_level = min(1, desire_sd * 2);
        
        % Inflation
        money_supply_growth = 0.03;
        economic_growth = 0.02;
        inflation_rate = max(0, money_supply_growth - economic_growth + crisis_level * 0.5);
        
        % Vélocité de la monnaie
        if crisis_level > 0
            velocity = 1.5 * exp(2 * crisis_level);
        else
            velocity = 1.5;
        end
        
        % ---- MICRO : Mises à jour individuelles ----
        for i = 1:num_agents
            agent = agents(i);
            
            % Calcul du désir avec influence des voisins
            neighbors_idx = neighbors(g, i);
            if ~isempty(neighbors_idx)
                neighbors_desire = [agents(neighbors_idx).desire];
                avg_neighbor_desire = mean(neighbors_desire);
            else
                avg_neighbor_desire = 0.5;
            end
            
            % Le désir est influencé par le contexte macro (feedback)
            agent.desire = compute_desire(agent, avg_neighbor_desire, inflation_rate);
            
            % Allocation de la richesse (avec bruit neuronal)
            agent.alpha = allocate_wealth(agent, inflation_rate, crisis_level);
            
            % Modèle de Markov : Transition d'état
            old_status = agent.adoption_status;
            agent.adoption_status = markov_transition(agent, avg_neighbor_desire, crisis_level);
            
            % Paiement de la Zakat
            if agent.wealth > agent.nisab_threshold
                zakat_amount = agent.tau_zakat * (agent.wealth - agent.nisab_threshold);
                agent.wealth = agent.wealth - zakat_amount;
                zakat_pool = zakat_pool + 0.8 * zakat_amount;
                waqf_pool = waqf_pool + 0.2 * zakat_amount;
            end
            
            % Échanges commerciaux
            trade_gain = randn(1) * 0.1;
            agent.wealth = agent.wealth + trade_gain;
            
            % Enregistrement pour les modèles de Markov
            adoption_history(i, step) = agent.adoption_status;
            if step > 1
                prev_status = adoption_history(i, step-1);
                transition_matrix(prev_status + 1, agent.adoption_status + 1) = ...
                    transition_matrix(prev_status + 1, agent.adoption_status + 1) + 1;
            end
            
            % Mise à jour de l'agent
            agents(i) = agent;
        end
        
        % ---- REDISTRIBUTION DE LA ZAKAT ----
        if zakat_pool > 0
            wealths_updated = [agents.wealth];
            poor_indices = find(wealths_updated < quantile(wealths_updated, 0.2));
            if ~isempty(poor_indices)
                zakat_per_agent = zakat_pool / length(poor_indices);
                for idx = poor_indices'
                    agents(idx).wealth = agents(idx).wealth + zakat_per_agent;
                end
            end
            zakat_pool = 0;
        end
        
        % ---- GOUVERNANCE : Élection de l'Émir et gestion du Waqf ----
        if mod(step, 30) == 0
            % Élection sans candidat
            emir_index = elect_emir(agents);
            
            % Gestion du Waqf
            if waqf_pool > 0
                [agents, waqf_pool] = manage_waqf(agents, g, emir_index, waqf_pool);
            end
        end
        
        % ---- MODÈLE DE RÉSEAU TEMPOREL ----
        % Les connexions évoluent en fonction des affinités communautaires
        g = update_network_temporal(g, agents, community_assignments, step, crisis_level);
        
        % Enregistrement de l'historique du réseau
        network_history{step} = g;
        community_affiliation_history(:, step) = community_assignments;
        
        % ---- ENREGISTREMENT DES DONNÉES AGRÉGÉES ----
        total_wealth_history(step) = total_wealth;
        avg_alpha_history(step) = avg_alpha;
        avg_desire_history(step) = avg_desire;
        gini_history(step) = gini;
        crisis_history(step) = crisis_level;
        inflation_history(step) = inflation_rate;
        velocity_history(step) = velocity;
    end
    
    % ============================================================
    % 3. VISUALISATION DES RÉSULTATS
    % ============================================================
    
    plot_results(total_wealth_history, avg_alpha_history, avg_desire_history, ...
                 gini_history, crisis_history, inflation_history, velocity_history);
    
    % Visualisation du réseau final
    plot_network_final(g, agents);
    
    % Visualisation de la matrice de transition de Markov
    plot_markov_matrix(transition_matrix);
    
    % Visualisation de l'évolution des communautés
    plot_community_evolution(community_affiliation_history, num_communities);
end

%% ============================================================
% 4. FONCTIONS DE CRÉATION DES AGENTS
% ============================================================

function agents = create_agents(num_agents)
    agents = struct('id', [], 'wealth', [], 'alpha', [], ...
                    'nisab_threshold', [], 'tau_zakat', [], ...
                    'risk_aversion', [], 'desire', [], 'adoption_status', []);
    
    for i = 1:num_agents
        wealth = (20 * (1 / rand())^(1/1.5)) + 10;
        wealth = min(wealth, 500);
        alpha = rand(1) * 0.6 + 0.2;
        
        agents(i).id = i;
        agents(i).wealth = wealth;
        agents(i).alpha = alpha;
        agents(i).nisab_threshold = 100;
        agents(i).tau_zakat = 0.025;
        agents(i).risk_aversion = rand(1) * 1.0 + 0.5;
        agents(i).desire = 0.5;
        agents(i).adoption_status = rand(1) < 0.2;  % 20% initialement adoptants
    end
end

%% ============================================================
% 5. CRÉATION DU RÉSEAU AVEC COMMUNAUTÉS
% ============================================================

function [g, community_assignments] = create_complex_network(num_agents, num_communities)
    % Assigner chaque agent à une communauté
    community_assignments = randi(num_communities, num_agents, 1);
    
    % Matrice de probabilités de connexion
    prob_matrix = 0.05 * ones(num_communities, num_communities);
    for i = 1:num_communities
        prob_matrix(i, i) = 0.35;
    end
    
    % Créer la matrice d'adjacence
    adj_matrix = zeros(num_agents);
    
    for i = 1:(num_agents - 1)
        for j = (i + 1):num_agents
            comm_i = community_assignments(i);
            comm_j = community_assignments(j);
            if rand(1) < prob_matrix(comm_i, comm_j)
                adj_matrix(i, j) = 1;
                adj_matrix(j, i) = 1;
            end
        end
    end
    
    % Ajouter quelques arêtes aléatoires
    num_random_edges = round(num_agents * 0.1);
    for k = 1:num_random_edges
        i = randi(num_agents);
        j = randi(num_agents);
        if i ~= j && adj_matrix(i, j) == 0
            adj_matrix(i, j) = 1;
            adj_matrix(j, i) = 1;
        end
    end
    
    % Créer le graphe
    g = graph(adj_matrix);
end

%% ============================================================
% 6. FONCTIONS DE DÉCISION (SOFTMAX ET DÉSIR)
% ============================================================

function desire = compute_desire(agent, avg_neighbor_desire, inflation_rate)
    liquidity_need = rand(1);
    base_desire = liquidity_need * (1 - agent.risk_aversion * 0.1);
    
    % Composante mimétique
    mimetic_component = 1 / (1 + exp(-5 * (avg_neighbor_desire - 0.5)));
    
    % Effet de l'inflation (feedback macro-micro)
    inflation_effect = 0.1 * inflation_rate;
    
    % Effet du statut d'adoption
    adoption_boost = 0.3 * (avg_neighbor_desire > 0.7);
    
    % Désir total avec bruit
    desire = 0.3 * base_desire + 0.4 * mimetic_component + ...
             0.2 * adoption_boost + 0.1 * inflation_effect + randn(1) * 0.05;
    desire = max(0, min(1, desire));
end

function new_alpha = allocate_wealth(agent, inflation_rate, crisis_level)
    % Coût de détention du fulus
    cost_fulus = inflation_rate + agent.tau_zakat;
    
    % Coût de détention du nuqud (avec feedback de la crise)
    cost_nuqud = 0.02 + agent.tau_zakat;
    cost_nuqud = cost_nuqud * (1 + 0.5 * crisis_level);
    
    % Utilités
    utility_fulus = 1 / (cost_fulus + 0.01);
    utility_nuqud = 1 / (cost_nuqud + 0.01);
    
    % Température cognitive (bruit neuronal)
    cognitive_temp = 0.5 + rand(1) * 0.5;
    
    % Softmax
    exp_fulus = exp(utility_fulus / cognitive_temp);
    exp_nuqud = exp(utility_nuqud / cognitive_temp);
    prob_fulus = exp_fulus / (exp_fulus + exp_nuqud);
    
    % Décision stochastique
    if rand(1) < prob_fulus
        new_alpha = min(1, agent.alpha + 0.05);
    else
        new_alpha = max(0, agent.alpha - 0.05);
    end
end

%% ============================================================
% 7. MODÈLE DE MARKOV POUR LES TRANSITIONS D'ÉTAT
% ============================================================

function new_status = markov_transition(agent, avg_neighbor_desire, crisis_level)
    % Matrice de transition dépendante du contexte
    % P(adoption | contexte)
    
    % Probabilités de transition de base
    p_stay_non_adoptant = 0.85;
    p_adopt = 0.15;
    
    % Ajustement en fonction du contexte
    if avg_neighbor_desire > 0.6
        p_adopt = p_adopt + 0.2;  % Influence sociale forte
    end
    
    if crisis_level > 0.5
        p_adopt = p_adopt + 0.15;  % La crise favorise l'adoption
    end
    
    if agent.wealth > 100
        p_adopt = p_adopt + 0.1;  % Les riches adoptent plus facilement
    end
    
    % Probabilité de rester adoptant
    p_stay_adoptant = 0.9;
    p_abandon = 0.1;
    
    % Effectuer la transition
    if agent.adoption_status == 0
        % Non-adoptant -> adoptant
        if rand(1) < p_adopt
            new_status = 1;
        else
            new_status = 0;
        end
    else
        % Adoptant -> non-adoptant
        if rand(1) < p_abandon
            new_status = 0;
        else
            new_status = 1;
        end
    end
end

%% ============================================================
% 8. MODÈLE DE RÉSEAU TEMPOREL
% ============================================================

function new_g = update_network_temporal(g, agents, community_assignments, step, crisis_level)
    % Les connexions évoluent en fonction des affinités et du contexte
    
    num_agents = numnodes(g);
    adj_matrix = adjacency(g);
    adj_matrix = full(adj_matrix);
    
    % Probabilité de reconnecter un lien en fonction des affinités
    for i = 1:(num_agents - 1)
        for j = (i + 1):num_agents
            % Calculer l'affinité entre i et j
            affinity = calculate_affinity(agents(i), agents(j), community_assignments, crisis_level);
            
            % Probabilité de conserver ou d'ajouter un lien
            if adj_matrix(i, j) == 1
                % Probabilité de conserver le lien
                if rand(1) > affinity
                    adj_matrix(i, j) = 0;
                    adj_matrix(j, i) = 0;
                end
            else
                % Probabilité d'ajouter un lien
                if rand(1) < affinity * 0.5
                    adj_matrix(i, j) = 1;
                    adj_matrix(j, i) = 1;
                end
            end
        end
    end
    
    % Créer le nouveau graphe
    new_g = graph(adj_matrix);
end

function affinity = calculate_affinity(agent_i, agent_j, community_assignments, crisis_level)
    % Calculer l'affinité entre deux agents
    
    % 1. Communauté commune (forte affinité)
    comm_i = community_assignments(agent_i.id);
    comm_j = community_assignments(agent_j.id);
    community_affinity = (comm_i == comm_j);
    
    % 2. Similarité de désir (mimétisme)
    desire_affinity = 1 - abs(agent_i.desire - agent_j.desire);
    
    % 3. Différence de richesse (les pauvres se regroupent, les riches aussi)
    wealth_affinity = 1 - abs(agent_i.wealth - agent_j.wealth) / 500;
    
    % 4. Similarité d'adoption (les adoptants se regroupent)
    adoption_affinity = (agent_i.adoption_status == agent_j.adoption_status);
    
    % Pondération selon le contexte de crise
    if crisis_level > 0.5
        % En crise, les communautés se referment
        affinity = 0.4 * community_affinity + 0.3 * desire_affinity + ...
                   0.2 * wealth_affinity + 0.1 * adoption_affinity;
    else
        % En temps normal, plus d'ouverture
        affinity = 0.2 * community_affinity + 0.3 * desire_affinity + ...
                   0.2 * wealth_affinity + 0.3 * adoption_affinity;
    end
end

%% ============================================================
% 9. THÉORIE DES JEUX : INTERACTIONS STRATÉGIQUES
% ============================================================

function [action_i, action_j] = strategic_interaction(agent_i, agent_j, g, step)
    % Modélisation des interactions stratégiques entre agents
    % Jeu de coordination monétaire : choisir entre fulus et nuqud
    
    % Payoffs (matrice de jeu)
    %           Agent j
    %           Fulus   Nuqud
    % Agent i   (a, a)  (b, c)
    % Agent j   (c, b)  (d, d)
    
    a = 2;   % Coordination sur fulus
    b = 1;   % Agent i joue fulus, agent j joue nuqud
    c = 0;   % Agent i joue nuqud, agent j joue fulus
    d = 1.5; % Coordination sur nuqud
    
    % Probabilité que l'agent i choisisse fulus
    prob_i_fulus = agent_i.alpha;  % Proportion actuelle en fulus
    
    % Calculer les utilités attendues pour l'agent i
    u_i_fulus = prob_i_fulus * a + (1 - prob_i_fulus) * b;
    u_i_nuqud = prob_i_fulus * c + (1 - prob_i_fulus) * d;
    
    % Choix optimal (théorie des jeux)
    if u_i_fulus > u_i_nuqud
        action_i = 1;  % Choisir fulus
    else
        action_i = 0;  % Choisir nuqud
    end
    
    % Stratégie mixte (bruit neuronal)
    if rand(1) < 0.3
        action_i = randi([0, 1]);  % Exploration
    end
    
    % Ajuster l'alpha en fonction de la stratégie
    if action_i == 1
        new_alpha = min(1, agent_i.alpha + 0.02);
    else
        new_alpha = max(0, agent_i.alpha - 0.02);
    end
    
    action_j = 1 - action_i;  % L'autre joue la stratégie opposée (cas simplifié)
end

%% ============================================================
% 10. FONCTIONS DE GOUVERNANCE
% ============================================================

function emir_index = elect_emir(agents)
    % Élection sans candidat (tirage au sort pondéré par la richesse)
    wealths = [agents.wealth];
    prob_weights = wealths / sum(wealths);
    emir_index = randsample(length(agents), 1, true, prob_weights);
end

function [agents, waqf_remaining] = manage_waqf(agents, g, emir_index, waqf_pool)
    % Gestion collective du waqf
    
    community_projects = 0.6 * waqf_pool;
    redistribution = 0.4 * waqf_pool;
    
    % Projets communautaires : investissement dans les plus pauvres
    wealths = [agents.wealth];
    poor_indices = find(wealths < quantile(wealths, 0.25));
    
    if ~isempty(poor_indices)
        investment_per_agent = community_projects / length(poor_indices);
        for idx = poor_indices'
            agents(idx).wealth = agents(idx).wealth + investment_per_agent;
        end
    end
    
    % Redistribution directe
    if redistribution > 0
        num_recipients = min(round(0.2 * length(agents)), length(poor_indices));
        if num_recipients > 0
            recipients = randsample(poor_indices, num_recipients);
            redist_per_agent = redistribution / num_recipients;
            for idx = recipients'
                agents(idx).wealth = agents(idx).wealth + redist_per_agent;
            end
        end
    end
    
    waqf_remaining = 0;
end

%% ============================================================
% 11. VISUALISATION
% ============================================================

function plot_results(total_wealth_history, avg_alpha_history, avg_desire_history, ...
                      gini_history, crisis_history, inflation_history, velocity_history)
    
    num_steps = length(total_wealth_history);
    steps = 1:num_steps;
    
    figure('Position', [100, 100, 1200, 800]);
    
    % 1. Richesse totale
    subplot(2, 3, 1);
    plot(steps, total_wealth_history, 'g-', 'LineWidth', 2);
    xlabel('Temps');
    ylabel('Richesse');
    title('Richesse Totale');
    grid on;
    
    % 2. Allocation (Alpha)
    subplot(2, 3, 2);
    plot(steps, avg_alpha_history, 'b-', 'LineWidth', 2);
    xlabel('Temps');
    ylabel('Alpha');
    title('Allocation Moyenne (Fulus/Nuqud)');
    grid on;
    
    % 3. Désir mimétique
    subplot(2, 3, 3);
    plot(steps, avg_desire_history, 'r-', 'LineWidth', 2);
    xlabel('Temps');
    ylabel('Désir');
    title('Désir Mimétique Collectif');
    grid on;
    
    % 4. Crise et Inflation
    subplot(2, 3, 4);
    plot(steps, crisis_history, 'm-', 'LineWidth', 2);
    hold on;
    plot(steps, inflation_history, 'c-', 'LineWidth', 2);
    plot(steps, velocity_history / 10, 'k--', 'LineWidth', 1.5);
    xlabel('Temps');
    ylabel('Valeur');
    title('Crise, Inflation et Vélocité');
    legend('Crise', 'Inflation', 'Vélocité/10');
    grid on;
    hold off;
    
    % 5. Coefficient de Gini
    subplot(2, 3, 5);
    plot(steps, gini_history, 'k-', 'LineWidth', 2);
    xlabel('Temps');
    ylabel('Gini');
    title("Coefficient de Gini");
    grid on;
    
    % 6. Statistiques finales
    subplot(2, 3, 6);
    axis off;
    text(0.1, 0.9, sprintf('Richesse Totale Finale: %.2f', total_wealth_history(end)), 'FontSize', 12);
    text(0.1, 0.8, sprintf('Gini Final: %.3f', gini_history(end)), 'FontSize', 12);
    text(0.1, 0.7, sprintf('Alpha Moyen Final: %.3f', avg_alpha_history(end)), 'FontSize', 12);
    text(0.1, 0.6, sprintf('Inflation Moyenne: %.3f', mean(inflation_history)), 'FontSize', 12);
    text(0.1, 0.5, sprintf('Crise Moyenne: %.3f', mean(crisis_history)), 'FontSize', 12);
    title('Statistiques Finales');
end

function plot_network_final(g, agents)
    figure('Position', [100, 100, 800, 600]);
    
    % Couleurs des nœuds en fonction du statut d'adoption
    adoption_status = [agents.adoption_status];
    node_colors = zeros(numnodes(g), 3);
    for i = 1:numnodes(g)
        if adoption_status(i) == 1
            node_colors(i, :) = [0, 1, 0];  % Vert (adoptant)
        else
            node_colors(i, :) = [0, 0, 1];  % Bleu (non-adoptant)
        end
    end
    
    % Taille des nœuds en fonction de la richesse
    wealths = [agents.wealth];
    node_sizes = 5 + log(wealths + 1) * 2;
    
    % Visualisation
    plot(g, 'NodeColor', node_colors, 'NodeSize', node_sizes, 'Layout', 'force');
    title('Réseau Social Final (Vert = Adoptant, Bleu = Non-Adoptant)');
end

function plot_markov_matrix(transition_matrix)
    figure('Position', [100, 100, 600, 500]);
    
    % Normaliser la matrice de transition
    for i = 1:2
        if sum(transition_matrix(i, :)) > 0
            transition_matrix(i, :) = transition_matrix(i, :) / sum(transition_matrix(i, :));
        end
    end
    
    imagesc(transition_matrix);
    colorbar;
    colormap('hot');
    
    set(gca, 'XTick', 1:2, 'XTickLabel', {'Non-Adoptant', 'Adoptant'});
    set(gca, 'YTick', 1:2, 'YTickLabel', {'Non-Adoptant', 'Adoptant'});
    xlabel('État Final');
    ylabel('État Initial');
    title('Matrice de Transition de Markov');
    
    % Ajouter les valeurs
    for i = 1:2
        for j = 1:2
            text(j, i, sprintf('%.2f', transition_matrix(i, j)), ...
                 'HorizontalAlignment', 'center', 'Color', 'white', 'FontSize', 14);
        end
    end
end

function plot_community_evolution(community_affiliation_history, num_communities)
    figure('Position', [100, 100, 800, 400]);
    
    num_steps = size(community_affiliation_history, 2);
    steps = 1:num_steps;
    
    % Utiliser des couleurs différentes pour chaque communauté
    colors = lines(num_communities);
    
    % Compter la proportion d'agents dans chaque communauté
    community_proportions = zeros(num_communities, num_steps);
    for t = 1:num_steps
        for c = 1:num_communities
            community_proportions(c, t) = sum(community_affiliation_history(:, t) == c) / ...
                                          size(community_affiliation_history, 1);
        end
    end
    
    % Visualisation
    area(steps, community_proportions', 'LineWidth', 1);
    xlabel('Temps');
    ylabel('Proportion');
    title('Évolution des Communautés');
    legend(arrayfun(@(c) sprintf('Communaute %d', c), 1:num_communities, 'UniformOutput', false));
    grid on;
end

%% ============================================================
% 12. EXÉCUTION
% ============================================================

% Lancer la simulation
run_simulation();

%% ============================================================
% FIN DU CODE MATLAB
% ============================================================

Les agents passent d'un état (adoptant/non-adoptant) à un autre selon des probabilités dépendantes du contexte :
function new_status = markov_transition(agent, avg_neighbor_desire, crisis_level)
    % Probabilités de transition ajustées
    p_adopt = 0.15 + 0.2*(avg_neighbor_desire > 0.6) + 0.15*(crisis_level > 0.5);
    p_abandon = 0.1;
    % ...
end
Variables clés :
Influence sociale (avg_neighbor_desire)
Niveau de crise (crisis_level)
Richesse de l'agent (wealth)
La matrice de transition est ensuite visualisée pour analyser les dynamiques d'adoption.
Les connexions évoluent dans le temps selon une fonction d'affinité qui prend en compte :
function affinity = calculate_affinity(agent_i, agent_j, community_assignments, crisis_level)
    % 4 facteurs d'affinité
    community_affinity = (comm_i == comm_j);  % Même communauté
    desire_affinity = 1 - abs(agent_i.desire - agent_j.desire);  % Désirs similaires
    wealth_affinity = 1 - abs(agent_i.wealth - agent_j.wealth) / 500;  % Richesse similaire
    adoption_affinity = (agent_i.adoption_status == agent_j.adoption_status);  % Même statut
    % ...
end
En temps de crise, les communautés se referment (community_affinity pondéré à 0.4).
En temps normal, les affinités de désir et d'adoption sont plus importantes.
Les agents interagissent stratégiquement pour choisir entre fulus et nuqud :
function [action_i, action_j] = strategic_interaction(agent_i, agent_j, g, step)
    % Matrice de payoff (jeu de coordination)
    %           Agent j
    %           Fulus   Nuqud
    % Agent i   (2, 2)  (1, 0)
    % Agent j   (0, 1)  (1.5, 1.5)
    % ...
end
Résultats attendus :
Coordination sur le fulus si la croyance collective est forte (équilibre de Nash).
Coordination sur le nuqud si la confiance s'effondre.
Stratégies mixtes introduites par du bruit neuronal (exploration).

Aspect
Python
NetLogo
R
MATLAB
Objectif
Analyse quantitative
Visualisation dynamique
Analyse avancée
Modélisation complète
Markov
Non implémenté
Non implémenté
Non implémenté
Oui (complet)
Réseau temporel
Non implémenté
Non implémenté
Partiel
Oui (complet)
Théorie des jeux
Non implémenté
Non implémenté
Non implémenté
Oui (complet)
Gouvernance
Non implémenté
Non implémenté
Émir + Waqf
Émir + Waqf
Performance
Rapide
Modérée
Rapide
Rapide
Visualisation
Statique
Animée
Statique + Réseau
Statique + Animations


Optimisation des paramètres : Utiliser des algorithmes génétiques pour calibrer les paramètres du modèle (probabilités de Markov, affinités, payoffs).
Validation empirique : Importer des données réelles (transactions, enquêtes) et comparer les sorties du modèle.
Analyse de sensibilité : Faire varier les paramètres clés pour identifier les facteurs critiques de stabilité du système monétaire.
Interfaces GUI : Créer une interface utilisateur pour visualiser en temps réel l'évolution du réseau et des variables macroéconomiques.

Souhaitez-vous que je développe l'une de ces extensions, ou que je fournisse une documentation plus détaillée sur les modèles mathématiques sous-jacents ?
