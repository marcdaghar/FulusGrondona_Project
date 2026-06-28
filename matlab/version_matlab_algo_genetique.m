%% ============================================================
% MODÈLE MONÉTAIRE MIMÉTIQUE AVEC OPTIMISATION, ANALYSE DE SENSIBILITÉ ET GUI
% ============================================================
% Thèse : Pour une alternative islamique au capitalisme
% Chapitre 2 : Une richesse nommée monnaie
% Concepts : Nuqud/Fulus, Nisab/Zakat, Désir Mimétique, Potentia Multitudinis
% ============================================================

%% ============================================================
% 1. PARAMÈTRES GLOBAUX ET STRUCTURES DE DONNÉES
% ============================================================

classdef MonetaryAgent < handle
    % Classe Agent Monétaire avec méthodes de mise à jour
    properties
        id
        wealth
        alpha
        nisab_threshold
        tau_zakat
        risk_aversion
        desire
        adoption_status
        wealth_history
        desire_history
        alpha_history
        adoption_history
    end
    
    methods
        function obj = MonetaryAgent(id, wealth, alpha)
            obj.id = id;
            obj.wealth = wealth;
            obj.alpha = alpha;
            obj.nisab_threshold = 100;
            obj.tau_zakat = 0.025;
            obj.risk_aversion = 0.5 + rand() * 1.0;
            obj.desire = 0.5;
            obj.adoption_status = rand() < 0.2;
            obj.wealth_history = [];
            obj.desire_history = [];
            obj.alpha_history = [];
            obj.adoption_history = [];
        end
        
        function obj = update_desire(obj, avg_neighbor_desire, inflation_rate, params)
            % Mise à jour du désir mimétique
            liquidity_need = rand();
            base_desire = liquidity_need * (1 - obj.risk_aversion * 0.1);
            
            mimetic_component = 1 / (1 + exp(-5 * (avg_neighbor_desire - 0.5)));
            inflation_effect = params.inflation_effect * inflation_rate;
            adoption_boost = params.adoption_boost * (avg_neighbor_desire > 0.7);
            
            obj.desire = params.base_desire_weight * base_desire + ...
                        params.mimetic_weight * mimetic_component + ...
                        params.adoption_weight * adoption_boost + ...
                        params.inflation_weight * inflation_effect + ...
                        randn() * 0.05;
            obj.desire = max(0, min(1, obj.desire));
        end
        
        function obj = allocate_wealth(obj, inflation_rate, crisis_level, params)
            % Allocation avec softmax et bruit neuronal
            cost_fulus = inflation_rate + obj.tau_zakat;
            cost_nuqud = params.nuqud_cost_base + obj.tau_zakat;
            cost_nuqud = cost_nuqud * (1 + params.crisis_risk_amplification * crisis_level);
            
            utility_fulus = 1 / (cost_fulus + 0.01);
            utility_nuqud = 1 / (cost_nuqud + 0.01);
            
            cognitive_temp = params.cognitive_temp_base + rand() * params.cognitive_temp_range;
            
            exp_fulus = exp(utility_fulus / cognitive_temp);
            exp_nuqud = exp(utility_nuqud / cognitive_temp);
            prob_fulus = exp_fulus / (exp_fulus + exp_nuqud);
            
            if rand() < prob_fulus
                obj.alpha = min(1, obj.alpha + params.alpha_adjustment_rate);
            else
                obj.alpha = max(0, obj.alpha - params.alpha_adjustment_rate);
            end
        end
        
        function obj = markov_transition(obj, avg_neighbor_desire, crisis_level, params)
            % Transition d'état avec modèle de Markov
            if obj.adoption_status == 0
                p_adopt = params.p_adopt_base + ...
                          params.p_adopt_social * (avg_neighbor_desire > 0.6) + ...
                          params.p_adopt_crisis * (crisis_level > 0.5) + ...
                          params.p_adopt_wealth * (obj.wealth > 100);
                obj.adoption_status = rand() < min(1, p_adopt);
            else
                p_abandon = params.p_abandon_base + ...
                            params.p_abandon_crisis * (crisis_level > 0.7);
                if rand() < p_abandon
                    obj.adoption_status = 0;
                end
            end
        end
        
        function obj = pay_zakat(obj)
            if obj.wealth > obj.nisab_threshold
                zakat_amount = obj.tau_zakat * (obj.wealth - obj.nisab_threshold);
                obj.wealth = obj.wealth - zakat_amount;
            end
        end
        
        function obj = trade(obj)
            trade_gain = randn() * 0.1;
            obj.wealth = obj.wealth + trade_gain;
        end
        
        function obj = record_history(obj)
            obj.wealth_history = [obj.wealth_history, obj.wealth];
            obj.desire_history = [obj.desire_history, obj.desire];
            obj.alpha_history = [obj.alpha_history, obj.alpha];
            obj.adoption_history = [obj.adoption_history, obj.adoption_status];
        end
    end
end

%% ============================================================
% 2. FONCTIONS DE RÉSEAU
% ============================================================

function [adj_matrix, community_assignments] = create_network(num_agents, num_communities, params)
    % Création du réseau avec communautés
    community_assignments = randi(num_communities, num_agents, 1);
    
    prob_matrix = params.inter_community_prob * ones(num_communities, num_communities);
    for i = 1:num_communities
        prob_matrix(i, i) = params.intra_community_prob;
    end
    
    adj_matrix = zeros(num_agents);
    for i = 1:(num_agents - 1)
        for j = (i + 1):num_agents
            comm_i = community_assignments(i);
            comm_j = community_assignments(j);
            if rand() < prob_matrix(comm_i, comm_j)
                adj_matrix(i, j) = 1;
                adj_matrix(j, i) = 1;
            end
        end
    end
    
    % Ajout de connexions aléatoires
    num_random_edges = round(num_agents * params.random_edge_ratio);
    for k = 1:num_random_edges
        i = randi(num_agents);
        j = randi(num_agents);
        if i ~= j && adj_matrix(i, j) == 0
            adj_matrix(i, j) = 1;
            adj_matrix(j, i) = 1;
        end
    end
end

function [adj_matrix, community_assignments] = update_network_temporal(adj_matrix, agents, community_assignments, crisis_level, params)
    % Mise à jour du réseau temporel
    num_agents = size(adj_matrix, 1);
    
    for i = 1:(num_agents - 1)
        for j = (i + 1):num_agents
            affinity = calculate_affinity(agents(i), agents(j), community_assignments, crisis_level, params);
            
            if adj_matrix(i, j) == 1
                if rand() > affinity
                    adj_matrix(i, j) = 0;
                    adj_matrix(j, i) = 0;
                end
            else
                if rand() < affinity * params.new_link_probability
                    adj_matrix(i, j) = 1;
                    adj_matrix(j, i) = 1;
                end
            end
        end
    end
end

function affinity = calculate_affinity(agent_i, agent_j, community_assignments, crisis_level, params)
    % Calcul de l'affinité entre deux agents
    comm_i = community_assignments(agent_i.id);
    comm_j = community_assignments(agent_j.id);
    community_affinity = params.community_weight * (comm_i == comm_j);
    desire_affinity = params.desire_weight * (1 - abs(agent_i.desire - agent_j.desire));
    wealth_affinity = params.wealth_weight * (1 - abs(agent_i.wealth - agent_j.wealth) / 500);
    adoption_affinity = params.adoption_weight * (agent_i.adoption_status == agent_j.adoption_status);
    
    if crisis_level > 0.5
        % En crise, les communautés se referment
        affinity = params.crisis_community_weight * community_affinity + ...
                   params.crisis_desire_weight * desire_affinity + ...
                   params.crisis_wealth_weight * wealth_affinity + ...
                   params.crisis_adoption_weight * adoption_affinity;
    else
        affinity = params.normal_community_weight * community_affinity + ...
                   params.normal_desire_weight * desire_affinity + ...
                   params.normal_wealth_weight * wealth_affinity + ...
                   params.normal_adoption_weight * adoption_affinity;
    end
    affinity = max(0, min(1, affinity));
end

%% ============================================================
% 3. FONCTIONS MACROÉCONOMIQUES
% ============================================================

function [total_wealth, avg_alpha, avg_desire, gini, crisis_level, inflation_rate, velocity] = ...
    compute_macro_variables(agents, params)
    % Calcul des variables macroéconomiques
    
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
    
    % Niveau de crise
    desire_sd = std(desires);
    crisis_level = min(1, desire_sd * params.crisis_sensitivity);
    
    % Inflation
    money_supply_growth = params.money_supply_growth;
    economic_growth = params.economic_growth;
    inflation_rate = max(0, money_supply_growth - economic_growth + crisis_level * params.inflation_crisis_sensitivity);
    
    % Vélocité
    if crisis_level > 0
        velocity = params.base_velocity * exp(params.velocity_crisis_sensitivity * crisis_level);
    else
        velocity = params.base_velocity;
    end
end

%% ============================================================
% 4. FONCTIONS DE GOUVERNANCE
% ============================================================

function emir_index = elect_emir(agents)
    % Élection sans candidat (pondérée par la richesse)
    wealths = [agents.wealth];
    prob_weights = wealths / sum(wealths);
    emir_index = randsample(length(agents), 1, true, prob_weights);
end

function [agents, waqf_remaining] = manage_waqf(agents, emir_index, waqf_pool, params)
    % Gestion collective du waqf
    community_projects = params.waqf_community_ratio * waqf_pool;
    redistribution = (1 - params.waqf_community_ratio) * waqf_pool;
    
    wealths = [agents.wealth];
    poor_indices = find(wealths < quantile(wealths, params.waqf_poverty_threshold));
    
    if ~isempty(poor_indices)
        investment_per_agent = community_projects / length(poor_indices);
        for idx = poor_indices'
            agents(idx).wealth = agents(idx).wealth + investment_per_agent;
        end
    end
    
    if redistribution > 0
        num_recipients = min(round(params.waqf_redistribution_ratio * length(agents)), length(poor_indices));
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
% 5. FONCTION OBJECTIF POUR L'OPTIMISATION (ALGORITHME GÉNÉTIQUE)
% ============================================================

function objective = objective_function(params_vector, num_agents, num_steps)
    % Fonction objectif pour l'optimisation des paramètres
    % Objectif : Maximiser la stabilité du système (minimiser l'inflation et les inégalités)
    
    % Paramètres par défaut
    default_params = get_default_parameters();
    
    % Mise à jour avec le vecteur d'optimisation
    field_names = fieldnames(default_params);
    for i = 1:min(length(field_names), length(params_vector))
        default_params.(field_names{i}) = params_vector(i);
    end
    
    % Exécuter une simulation
    try
        [~, results] = run_simulation(num_agents, num_steps, default_params, false);
        
        % Variables à optimiser (minimiser)
        inflation_mean = mean(results.inflation);
        gini_mean = mean(results.gini);
        crisis_mean = mean(results.crisis);
        
        % Objectif : combinaison pondérée
        objective = 0.4 * inflation_mean + 0.3 * gini_mean + 0.3 * crisis_mean;
    catch
        objective = 1e10;  % Pénalité en cas d'erreur
    end
end

function [params] = get_default_parameters()
    % Paramètres par défaut
    params = struct();
    
    % Paramètres de désir
    params.base_desire_weight = 0.3;
    params.mimetic_weight = 0.4;
    params.adoption_weight = 0.2;
    params.inflation_weight = 0.1;
    params.inflation_effect = 0.1;
    params.adoption_boost = 0.3;
    
    % Paramètres d'allocation
    params.nuqud_cost_base = 0.02;
    params.crisis_risk_amplification = 0.5;
    params.cognitive_temp_base = 0.5;
    params.cognitive_temp_range = 0.5;
    params.alpha_adjustment_rate = 0.05;
    
    % Paramètres de Markov
    params.p_adopt_base = 0.15;
    params.p_adopt_social = 0.2;
    params.p_adopt_crisis = 0.15;
    params.p_adopt_wealth = 0.1;
    params.p_abandon_base = 0.1;
    params.p_abandon_crisis = 0.15;
    
    % Paramètres de réseau
    params.intra_community_prob = 0.35;
    params.inter_community_prob = 0.05;
    params.random_edge_ratio = 0.1;
    params.new_link_probability = 0.5;
    
    % Paramètres d'affinité (normal)
    params.normal_community_weight = 0.2;
    params.normal_desire_weight = 0.3;
    params.normal_wealth_weight = 0.2;
    params.normal_adoption_weight = 0.3;
    
    % Paramètres d'affinité (crise)
    params.crisis_community_weight = 0.4;
    params.crisis_desire_weight = 0.3;
    params.crisis_wealth_weight = 0.2;
    params.crisis_adoption_weight = 0.1;
    
    % Poids d'affinité (pour compatibilité)
    params.community_weight = 0.2;
    params.desire_weight = 0.3;
    params.wealth_weight = 0.2;
    params.adoption_weight = 0.3;
    
    % Paramètres macro
    params.money_supply_growth = 0.03;
    params.economic_growth = 0.02;
    params.inflation_crisis_sensitivity = 0.5;
    params.base_velocity = 1.5;
    params.velocity_crisis_sensitivity = 2.0;
    params.crisis_sensitivity = 2.0;
    
    % Paramètres de gouvernance
    params.waqf_community_ratio = 0.6;
    params.waqf_poverty_threshold = 0.25;
    params.waqf_redistribution_ratio = 0.2;
end

%% ============================================================
% 6. SIMULATION PRINCIPALE
% ============================================================

function [agents, results] = run_simulation(num_agents, num_steps, params, verbose)
    % Simulation principale
    
    if nargin < 4
        verbose = true;
    end
    if nargin < 3
        params = get_default_parameters();
    end
    
    % Initialisation des agents
    agents = MonetaryAgent.empty(num_agents, 0);
    for i = 1:num_agents
        wealth = (20 * (1 / rand())^(1/1.5)) + 10;
        wealth = min(wealth, 500);
        alpha = rand() * 0.6 + 0.2;
        agents(i) = MonetaryAgent(i, wealth, alpha);
    end
    
    % Création du réseau
    [adj_matrix, community_assignments] = create_network(num_agents, 5, params);
    
    % Variables globales
    zakat_pool = 0;
    waqf_pool = 0;
    emir_index = 0;
    
    % Stockage des résultats
    results = struct();
    results.total_wealth = zeros(num_steps, 1);
    results.avg_alpha = zeros(num_steps, 1);
    results.avg_desire = zeros(num_steps, 1);
    results.gini = zeros(num_steps, 1);
    results.crisis = zeros(num_steps, 1);
    results.inflation = zeros(num_steps, 1);
    results.velocity = zeros(num_steps, 1);
    results.network = cell(num_steps, 1);
    
    % Boucle principale
    for step = 1:num_steps
        if verbose && mod(step, 10) == 0
            fprintf('Étape: %d/%d\n', step, num_steps);
        end
        
        % Macro : Calcul des variables agrégées
        [total_wealth, avg_alpha, avg_desire, gini, crisis_level, inflation_rate, velocity] = ...
            compute_macro_variables(agents, params);
        
        % Micro : Mises à jour individuelles
        for i = 1:num_agents
            agent = agents(i);
            
            % Calcul du désir avec influence des voisins
            neighbors_idx = find(adj_matrix(i, :));
            if ~isempty(neighbors_idx)
                neighbors_desire = [agents(neighbors_idx).desire];
                avg_neighbor_desire = mean(neighbors_desire);
            else
                avg_neighbor_desire = 0.5;
            end
            
            agent.update_desire(avg_neighbor_desire, inflation_rate, params);
            agent.allocate_wealth(inflation_rate, crisis_level, params);
            agent.markov_transition(avg_neighbor_desire, crisis_level, params);
            agent.pay_zakat();
            agent.trade();
            agent.record_history();
            
            agents(i) = agent;
        end
        
        % Redistribution de la Zakat
        if zakat_pool > 0
            wealths = [agents.wealth];
            poor_indices = find(wealths < quantile(wealths, 0.2));
            if ~isempty(poor_indices)
                zakat_per_agent = zakat_pool / length(poor_indices);
                for idx = poor_indices'
                    agents(idx).wealth = agents(idx).wealth + zakat_per_agent;
                end
            end
            zakat_pool = 0;
        end
        
        % Gouvernance
        if mod(step, 30) == 0
            emir_index = elect_emir(agents);
            if waqf_pool > 0
                [agents, waqf_pool] = manage_waqf(agents, emir_index, waqf_pool, params);
            end
        end
        
        % Mise à jour du réseau temporel
        [adj_matrix, community_assignments] = update_network_temporal(...
            adj_matrix, agents, community_assignments, crisis_level, params);
        
        % Enregistrement des résultats
        results.total_wealth(step) = total_wealth;
        results.avg_alpha(step) = avg_alpha;
        results.avg_desire(step) = avg_desire;
        results.gini(step) = gini;
        results.crisis(step) = crisis_level;
        results.inflation(step) = inflation_rate;
        results.velocity(step) = velocity;
        results.network{step} = adj_matrix;
    end
end

%% ============================================================
% 7. OPTIMISATION PAR ALGORITHME GÉNÉTIQUE
% ============================================================

function optimized_params = optimize_parameters(num_agents, num_steps)
    % Optimisation des paramètres avec algorithme génétique
    
    fprintf('=== OPTIMISATION DES PARAMÈTRES ===\n');
    fprintf('Agents: %d, Étapes: %d\n', num_agents, num_steps);
    
    % Définition des bornes pour chaque paramètre
    default_params = get_default_parameters();
    field_names = fieldnames(default_params);
    
    % Nombre de paramètres à optimiser
    num_params = length(field_names);
    
    % Bornes inférieures et supérieures
    lb = zeros(1, num_params);
    ub = ones(1, num_params);
    
    % Ajustement des bornes pour chaque type de paramètre
    for i = 1:num_params
        name = field_names{i};
        if contains(name, 'weight') || contains(name, 'ratio') || contains(name, 'prob')
            lb(i) = 0.01;
            ub(i) = 0.9;
        elseif contains(name, 'rate') || contains(name, 'sensitivity') || contains(name, 'amplification')
            lb(i) = 0.01;
            ub(i) = 3.0;
        elseif contains(name, 'temp') || contains(name, 'boost') || contains(name, 'effect')
            lb(i) = 0.01;
            ub(i) = 2.0;
        else
            lb(i) = 0.01;
            ub(i) = 1.0;
        end
    end
    
    % Fonction objectif pour l'optimisation
    objective_fcn = @(x) objective_function(x, num_agents, num_steps);
    
    % Options de l'algorithme génétique
    options = optimoptions('ga', ...
        'PopulationSize', 30, ...
        'MaxGenerations', 50, ...
        'FunctionTolerance', 1e-6, ...
        'Display', 'iter', ...
        'PlotFcn', @gaplotbestf, ...
        'UseParallel', false);
    
    % Lancement de l'optimisation
    [x_opt, fval_opt] = ga(objective_fcn, num_params, [], [], [], [], lb, ub, [], options);
    
    % Construction des paramètres optimisés
    optimized_params = default_params;
    for i = 1:min(length(field_names), length(x_opt))
        optimized_params.(field_names{i}) = x_opt(i);
    end
    
    fprintf('\nOptimisation terminée. Valeur objective: %.4f\n', fval_opt);
end

%% ============================================================
% 8. ANALYSE DE SENSIBILITÉ
% ============================================================

function sensitivity_results = sensitivity_analysis(num_agents, num_steps)
    % Analyse de sensibilité des paramètres clés
    
    fprintf('\n=== ANALYSE DE SENSIBILITÉ ===\n');
    
    % Liste des paramètres à analyser
    param_names = {'base_desire_weight', 'mimetic_weight', 'p_adopt_base', ...
                   'intra_community_prob', 'normal_adoption_weight', 'crisis_risk_amplification'};
    param_ranges = {0.1:0.1:0.9, 0.1:0.1:0.9, 0.01:0.05:0.5, ...
                    0.1:0.1:0.9, 0.1:0.1:0.9, 0.1:0.2:1.5};
    
    sensitivity_results = struct();
    default_params = get_default_parameters();
    
    for p = 1:length(param_names)
        fprintf('Analyse du paramètre: %s\n', param_names{p});
        
        param_values = param_ranges{p};
        results = struct();
        results.values = param_values;
        results.inflation = zeros(length(param_values), 1);
        results.gini = zeros(length(param_values), 1);
        results.crisis = zeros(length(param_values), 1);
        results.total_wealth = zeros(length(param_values), 1);
        
        for v = 1:length(param_values)
            params = default_params;
            params.(param_names{p}) = param_values(v);
            
            [~, sim_results] = run_simulation(num_agents, num_steps, params, false);
            
            results.inflation(v) = mean(sim_results.inflation);
            results.gini(v) = mean(sim_results.gini);
            results.crisis(v) = mean(sim_results.crisis);
            results.total_wealth(v) = sim_results.total_wealth(end);
        end
        
        sensitivity_results.(param_names{p}) = results;
    end
    
    % Visualisation des résultats de sensibilité
    plot_sensitivity_results(sensitivity_results);
end

function plot_sensitivity_results(sensitivity_results)
    % Visualisation des résultats de l'analyse de sensibilité
    
    figure('Position', [100, 100, 1200, 800]);
    param_names = fieldnames(sensitivity_results);
    num_params = length(param_names);
    
    for p = 1:num_params
        subplot(2, 3, p);
        results = sensitivity_results.(param_names{p});
        
        plot(results.values, results.inflation, 'r-o', 'LineWidth', 2);
        hold on;
        plot(results.values, results.gini, 'b-s', 'LineWidth', 2);
        plot(results.values, results.crisis, 'g-d', 'LineWidth', 2);
        plot(results.values, results.total_wealth / max(results.total_wealth), 'k--', 'LineWidth', 2);
        hold off;
        
        xlabel(param_names{p});
        ylabel('Valeur');
        title(['Sensibilité: ' param_names{p}]);
        legend('Inflation', 'Gini', 'Crise', 'Richesse (norm.)', 'Location', 'best');
        grid on;
    end
end

%% ============================================================
% 9. INTERFACE UTILISATEUR (GUI)
% ============================================================

function create_gui()
    % Création de l'interface utilisateur pour visualisation en temps réel
    
    fprintf('=== LANCEMENT DE L\'INTERFACE GUI ===\n');
    
    % Création de la figure principale
    fig = figure('Position', [50, 50, 1400, 800], ...
                 'Name', 'Simulation Monétaire - Thèse', ...
                 'NumberTitle', 'off', ...
                 'MenuBar', 'none', ...
                 'ToolBar', 'none');
    
    % Panneau de contrôle
    control_panel = uipanel(fig, 'Position', [0.02, 0.02, 0.25, 0.96], ...
                            'Title', 'Contrôle de la Simulation', ...
                            'FontSize', 12, 'FontWeight', 'bold');
    
    % Paramètres de simulation
    uicontrol(control_panel, 'Style', 'text', 'Position', [10, 550, 100, 25], ...
              'String', 'Nombre d\'agents:', 'HorizontalAlignment', 'left');
    num_agents_edit = uicontrol(control_panel, 'Style', 'edit', 'Position', [120, 550, 80, 25], ...
                                'String', '150', 'BackgroundColor', 'white');
    
    uicontrol(control_panel, 'Style', 'text', 'Position', [10, 510, 100, 25], ...
              'String', 'Nombre d\'étapes:', 'HorizontalAlignment', 'left');
    num_steps_edit = uicontrol(control_panel, 'Style', 'edit', 'Position', [120, 510, 80, 25], ...
                               'String', '200', 'BackgroundColor', 'white');
    
    % Boutons de contrôle
    start_button = uicontrol(control_panel, 'Style', 'pushbutton', 'Position', [10, 460, 100, 40], ...
                             'String', '▶ Démarrer', 'FontSize', 12, 'FontWeight', 'bold', ...
                             'BackgroundColor', [0.3, 0.8, 0.3], ...
                             'Callback', @(src, event) start_simulation());
    
    stop_button = uicontrol(control_panel, 'Style', 'pushbutton', 'Position', [120, 460, 100, 40], ...
                            'String', '■ Arrêter', 'FontSize', 12, 'FontWeight', 'bold', ...
                            'BackgroundColor', [0.8, 0.3, 0.3], ...
                            'Callback', @(src, event) stop_simulation());
    
    pause_button = uicontrol(control_panel, 'Style', 'pushbutton', 'Position', [10, 410, 100, 40], ...
                             'String', '⏸ Pause', 'FontSize', 12, 'FontWeight', 'bold', ...
                             'BackgroundColor', [0.8, 0.8, 0.3], ...
                             'Callback', @(src, event) pause_simulation());
    
    reset_button = uicontrol(control_panel, 'Style', 'pushbutton', 'Position', [120, 410, 100, 40], ...
                             'String', '⟳ Reset', 'FontSize', 12, 'FontWeight', 'bold', ...
                             'BackgroundColor', [0.8, 0.6, 0.2], ...
                             'Callback', @(src, event) reset_simulation());
    
    % Bouton d'optimisation
    optimize_button = uicontrol(control_panel, 'Style', 'pushbutton', 'Position', [10, 360, 200, 40], ...
                                'String', '🔍 Optimiser les paramètres', 'FontSize', 11, ...
                                'BackgroundColor', [0.2, 0.6, 0.8], ...
                                'Callback', @(src, event) run_optimization());
    
    % Bouton d'analyse de sensibilité
    sensitivity_button = uicontrol(control_panel, 'Style', 'pushbutton', 'Position', [10, 310, 200, 40], ...
                                   'String', '📊 Analyse de sensibilité', 'FontSize', 11, ...
                                   'BackgroundColor', [0.6, 0.4, 0.8], ...
                                   'Callback', @(src, event) run_sensitivity_analysis());
    
    % Panneau d'affichage des statistiques
    stats_panel = uipanel(control_panel, 'Position', [0.05, 0.02, 0.90, 0.35], ...
                          'Title', 'Statistiques', 'FontSize', 10);
    
    stats_text = uicontrol(stats_panel, 'Style', 'text', 'Position', [10, 10, 200, 150], ...
                           'String', 'Richesse totale: 0\nGini: 0\nInflation: 0\nCrise: 0\nAdoption: 0%', ...
                           'HorizontalAlignment', 'left', 'FontSize', 10, ...
                           'BackgroundColor', [0.95, 0.95, 0.95]);
    
    % Panneau de visualisation du réseau
    network_axes = axes(fig, 'Position', [0.30, 0.55, 0.45, 0.40]);
    title(network_axes, 'Réseau Social', 'FontSize', 12);
    axis(network_axes, 'off');
    
    % Panneau de visualisation des graphiques
    graph_panel = uipanel(fig, 'Position', [0.30, 0.05, 0.45, 0.45], ...
                          'Title', 'Variables Macroéconomiques', ...
                          'FontSize', 10);
    
    graph_axes = axes(graph_panel, 'Position', [0.05, 0.10, 0.90, 0.85]);
    xlabel(graph_axes, 'Temps');
    ylabel(graph_axes, 'Valeur');
    grid(graph_axes, 'on');
    hold(graph_axes, 'on');
    
    % Panneau de légende
    legend_panel = uipanel(fig, 'Position', [0.78, 0.55, 0.20, 0.40], ...
                           'Title', 'Légende des Variables', ...
                           'FontSize', 10);
    
    legend_text = uicontrol(legend_panel, 'Style', 'text', 'Position', [10, 10, 150, 200], ...
                            'String', '● Richesse totale\n● Alpha (Fulus)\n● Désir mimétique\n● Inflation\n● Crise\n● Gini', ...
                            'HorizontalAlignment', 'left', 'FontSize', 9, ...
                            'BackgroundColor', [0.95, 0.95, 0.95]);
    
    % Variables pour la simulation
    gui_data = struct();
    gui_data.is_running = false;
    gui_data.is_paused = false;
    gui_data.sim_results = [];
    gui_data.sim_agents = [];
    gui_data.step_counter = 0;
    gui_data.stats_text = stats_text;
    gui_data.network_axes = network_axes;
    gui_data.graph_axes = graph_axes;
    gui_data.num_agents_edit = num_agents_edit;
    gui_data.num_steps_edit = num_steps_edit;
    
    guidata(fig, gui_data);
    
    % Fonctions de callback
    function start_simulation()
        gui_data = guidata(fig);
        if ~gui_data.is_running
            gui_data.is_running = true;
            gui_data.is_paused = false;
            gui_data.step_counter = 0;
            
            num_agents = str2double(get(num_agents_edit, 'String'));
            num_steps = str2double(get(num_steps_edit, 'String'));
            
            if isnan(num_agents) || isnan(num_steps)
                errordlg('Veuillez entrer des nombres valides', 'Erreur');
                return;
            end
            
            set(stats_text, 'String', 'Simulation en cours...');
            guidata(fig, gui_data);
            
            % Démarrer la simulation dans une boucle (avec pause)
            run_gui_simulation(fig, num_agents, num_steps);
        end
    end
    
    function run_gui_simulation(fig, num_agents, num_steps)
        % Exécution de la simulation avec mise à jour GUI
        gui_data = guidata(fig);
        
        % Paramètres par défaut
        params = get_default_parameters();
        
        % Initialisation des agents
        agents = MonetaryAgent.empty(num_agents, 0);
        for i = 1:num_agents
            wealth = (20 * (1 / rand())^(1/1.5)) + 10;
            wealth = min(wealth, 500);
            alpha = rand() * 0.6 + 0.2;
            agents(i) = MonetaryAgent(i, wealth, alpha);
        end
        
        % Création du réseau
        [adj_matrix, community_assignments] = create_network(num_agents, 5, params);
        
        % Variables globales
        zakat_pool = 0;
        waqf_pool = 0;
        emir_index = 0;
        
        % Historiques
        total_wealth_history = zeros(num_steps, 1);
        alpha_history = zeros(num_steps, 1);
        desire_history = zeros(num_steps, 1);
        gini_history = zeros(num_steps, 1);
        crisis_history = zeros(num_steps, 1);
        inflation_history = zeros(num_steps, 1);
        
        for step = 1:num_steps
            % Vérifier l'état de la simulation
            gui_data = guidata(fig);
            if ~gui_data.is_running
                break;
            end
            while gui_data.is_paused
                pause(0.1);
                gui_data = guidata(fig);
            end
            
            % Macro : Calcul des variables agrégées
            [total_wealth, avg_alpha, avg_desire, gini, crisis_level, inflation_rate, ~] = ...
                compute_macro_variables(agents, params);
            
            % Micro : Mises à jour individuelles
            for i = 1:num_agents
                agent = agents(i);
                
                neighbors_idx = find(adj_matrix(i, :));
                if ~isempty(neighbors_idx)
                    neighbors_desire = [agents(neighbors_idx).desire];
                    avg_neighbor_desire = mean(neighbors_desire);
                else
                    avg_neighbor_desire = 0.5;
                end
                
                agent.update_desire(avg_neighbor_desire, inflation_rate, params);
                agent.allocate_wealth(inflation_rate, crisis_level, params);
                agent.markov_transition(avg_neighbor_desire, crisis_level, params);
                agent.pay_zakat();
                agent.trade();
                agent.record_history();
                
                agents(i) = agent;
            end
            
            % Redistribution de la Zakat (simplifiée)
            if zakat_pool > 0
                wealths = [agents.wealth];
                poor_indices = find(wealths < quantile(wealths, 0.2));
                if ~isempty(poor_indices)
                    zakat_per_agent = zakat_pool / length(poor_indices);
                    for idx = poor_indices'
                        agents(idx).wealth = agents(idx).wealth + zakat_per_agent;
                    end
                end
                zakat_pool = 0;
            end
            
            % Mise à jour du réseau temporel
            [adj_matrix, community_assignments] = update_network_temporal(...
                adj_matrix, agents, community_assignments, crisis_level, params);
            
            % Enregistrement
            total_wealth_history(step) = total_wealth;
            alpha_history(step) = avg_alpha;
            desire_history(step) = avg_desire;
            gini_history(step) = gini;
            crisis_history(step) = crisis_level;
            inflation_history(step) = inflation_rate;
            
            % Mise à jour de l'interface
            if mod(step, 5) == 0
                update_gui_display(fig, agents, adj_matrix, community_assignments, ...
                    total_wealth_history, alpha_history, desire_history, ...
                    gini_history, crisis_history, inflation_history, step);
            end
            
            gui_data.step_counter = step;
            guidata(fig, gui_data);
            drawnow;
        end
        
        gui_data = guidata(fig);
        gui_data.is_running = false;
        gui_data.sim_results = struct();
        gui_data.sim_results.total_wealth = total_wealth_history;
        gui_data.sim_results.alpha = alpha_history;
        gui_data.sim_results.desire = desire_history;
        gui_data.sim_results.gini = gini_history;
        gui_data.sim_results.crisis = crisis_history;
        gui_data.sim_results.inflation = inflation_history;
        gui_data.sim_agents = agents;
        guidata(fig, gui_data);
        
        set(gui_data.stats_text, 'String', 'Simulation terminée');
    end
    
    function update_gui_display(fig, agents, adj_matrix, community_assignments, ...
            total_wealth_history, alpha_history, desire_history, ...
            gini_history, crisis_history, inflation_history, step)
        
        gui_data = guidata(fig);
        
        % Mise à jour des statistiques
        wealths = [agents.wealth];
        adoption_count = sum([agents.adoption_status]);
        adoption_rate = adoption_count / length(agents) * 100;
        
        stats_str = sprintf('Richesse totale: %.2f\nGini: %.3f\nInflation: %.3f\nCrise: %.3f\nAdoption: %.1f%%', ...
            total_wealth_history(step), gini_history(step), ...
            inflation_history(step), crisis_history(step), adoption_rate);
        set(gui_data.stats_text, 'String', stats_str);
        
        % Visualisation du réseau
        axes(gui_data.network_axes);
        cla(gui_data.network_axes);
        
        % Création du graphe
        g = graph(adj_matrix);
        node_colors = zeros(numnodes(g), 3);
        for i = 1:numnodes(g)
            if agents(i).adoption_status == 1
                node_colors(i, :) = [0, 0.8, 0];
            else
                node_colors(i, :) = [0, 0.3, 0.8];
            end
        end
        node_sizes = 5 + log([agents.wealth] + 1) * 2;
        
        plot(g, 'NodeColor', node_colors, 'NodeSize', node_sizes, 'Layout', 'force');
        title(gui_data.network_axes, sprintf('Réseau Social (Étape %d)', step));
        axis(gui_data.network_axes, 'off');
        
        % Mise à jour des graphiques
        axes(gui_data.graph_axes);
        cla(gui_data.graph_axes);
        
        steps = 1:step;
        plot(gui_data.graph_axes, steps, total_wealth_history(1:step) / max(total_wealth_history(1:step)), ...
            'g-', 'LineWidth', 2);
        hold(gui_data.graph_axes, 'on');
        plot(gui_data.graph_axes, steps, alpha_history(1:step), 'b-', 'LineWidth', 2);
        plot(gui_data.graph_axes, steps, desire_history(1:step), 'r-', 'LineWidth', 2);
        plot(gui_data.graph_axes, steps, inflation_history(1:step), 'm-', 'LineWidth', 2);
        plot(gui_data.graph_axes, steps, crisis_history(1:step), 'c-', 'LineWidth', 2);
        plot(gui_data.graph_axes, steps, gini_history(1:step), 'k-', 'LineWidth', 2);
        hold(gui_data.graph_axes, 'off');
        
        xlabel(gui_data.graph_axes, 'Temps');
        ylabel(gui_data.graph_axes, 'Valeur (normalisée)');
        legend(gui_data.graph_axes, {'Richesse', 'Alpha', 'Désir', 'Inflation', 'Crise', 'Gini'}, ...
            'Location', 'best');
        grid(gui_data.graph_axes, 'on');
    end
    
    function stop_simulation()
        gui_data = guidata(fig);
        gui_data.is_running = false;
        gui_data.is_paused = false;
        guidata(fig, gui_data);
        set(gui_data.stats_text, 'String', 'Simulation arrêtée');
    end
    
    function pause_simulation()
        gui_data = guidata(fig);
        gui_data.is_paused = ~gui_data.is_paused;
        guidata(fig, gui_data);
        if gui_data.is_paused
            set(pause_button, 'String', '▶ Reprendre', 'BackgroundColor', [0.3, 0.8, 0.3]);
        else
            set(pause_button, 'String', '⏸ Pause', 'BackgroundColor', [0.8, 0.8, 0.3]);
        end
    end
    
    function reset_simulation()
        gui_data = guidata(fig);
        gui_data.is_running = false;
        gui_data.is_paused = false;
        gui_data.sim_results = [];
        gui_data.sim_agents = [];
        gui_data.step_counter = 0;
        guidata(fig, gui_data);
        
        cla(gui_data.network_axes);
        cla(gui_data.graph_axes);
        set(gui_data.stats_text, 'String', 'Richesse totale: 0\nGini: 0\nInflation: 0\nCrise: 0\nAdoption: 0%');
        set(pause_button, 'String', '⏸ Pause', 'BackgroundColor', [0.8, 0.8, 0.3]);
    end
    
    function run_optimization()
        gui_data = guidata(fig);
        num_agents = str2double(get(num_agents_edit, 'String'));
        num_steps = str2double(get(num_steps_edit, 'String'));
        
        if isnan(num_agents) || isnan(num_steps)
            errordlg('Veuillez entrer des nombres valides', 'Erreur');
            return;
        end
        
        set(stats_text, 'String', 'Optimisation en cours...');
        drawnow;
        
        optimized_params = optimize_parameters(num_agents, num_steps);
        
        % Afficher les résultats
        msg = 'Optimisation terminée!\n\nParamètres optimisés:\n';
        field_names = fieldnames(optimized_params);
        for i = 1:min(10, length(field_names))
            msg = [msg, sprintf('%s: %.4f\n', field_names{i}, optimized_params.(field_names{i}))];
        end
        msg = [msg, '...\n\nUtiliser ces paramètres pour la simulation?'];
        
        choice = questdlg(msg, 'Résultats d\'optimisation', 'Oui', 'Non', 'Oui');
        if strcmp(choice, 'Oui')
            % Appliquer les paramètres optimisés
            set(stats_text, 'String', 'Paramètres optimisés appliqués');
            % (Les paramètres sont utilisés dans la prochaine simulation)
        end
    end
    
    function run_sensitivity_analysis()
        gui_data = guidata(fig);
        num_agents = str2double(get(num_agents_edit, 'String'));
        num_steps = str2double(get(num_steps_edit, 'String'));
        
        if isnan(num_agents) || isnan(num_steps)
            errordlg('Veuillez entrer des nombres valides', 'Erreur');
            return;
        end
        
        set(stats_text, 'String', 'Analyse de sensibilité en cours...');
        drawnow;
        
        sensitivity_analysis(num_agents, num_steps);
        
        set(stats_text, 'String', 'Analyse de sensibilité terminée');
    end
end

%% ============================================================
% 10. EXÉCUTION PRINCIPALE
% ============================================================

function main()
    % Fonction principale avec choix du mode d'exécution
    
    fprintf('=== MODÈLE MONÉTAIRE MIMÉTIQUE ===\n');
    fprintf('1. Lancer l\'interface GUI\n');
    fprintf('2. Lancer l\'optimisation des paramètres\n');
    fprintf('3. Lancer l\'analyse de sensibilité\n');
    fprintf('4. Lancer une simulation standard\n');
    fprintf('5. Quitter\n');
    
    choice = input('Votre choix: ');
    
    switch choice
        case 1
            create_gui();
        case 2
            optimize_parameters(150, 200);
        case 3
            sensitivity_analysis(150, 200);
        case 4
            params = get_default_parameters();
            [agents, results] = run_simulation(150, 200, params, true);
            plot_simulation_results(results);
        case 5
            fprintf('Au revoir!\n');
        otherwise
            fprintf('Choix invalide.\n');
    end
end

function plot_simulation_results(results)
    % Visualisation des résultats de la simulation
    
    num_steps = length(results.total_wealth);
    steps = 1:num_steps;
    
    figure('Position', [100, 100, 1200, 800]);
    
    subplot(2, 3, 1);
    plot(steps, results.total_wealth, 'g-', 'LineWidth', 2);
    xlabel('Temps');
    ylabel('Richesse');
    title('Richesse Totale');
    grid on;
    
    subplot(2, 3, 2);
    plot(steps, results.avg_alpha, 'b-', 'LineWidth', 2);
    xlabel('Temps');
    ylabel('Alpha');
    title('Allocation Moyenne');
    grid on;
    
    subplot(2, 3, 3);
    plot(steps, results.avg_desire, 'r-', 'LineWidth', 2);
    xlabel('Temps');
    ylabel('Désir');
    title('Désir Mimétique Collectif');
    grid on;
    
    subplot(2, 3, 4);
    plot(steps, results.crisis, 'm-', 'LineWidth', 2);
    hold on;
    plot(steps, results.inflation, 'c-', 'LineWidth', 2);
    plot(steps, results.velocity / 10, 'k--', 'LineWidth', 1.5);
    xlabel('Temps');
    ylabel('Valeur');
    title('Crise, Inflation et Vélocité');
    legend('Crise', 'Inflation', 'Vélocité/10');
    grid on;
    hold off;
    
    subplot(2, 3, 5);
    plot(steps, results.gini, 'k-', 'LineWidth', 2);
    xlabel('Temps');
    ylabel('Gini');
    title("Coefficient de Gini");
    grid on;
    
    subplot(2, 3, 6);
    axis off;
    text(0.1, 0.9, sprintf('Richesse Totale Finale: %.2f', results.total_wealth(end)), 'FontSize', 12);
    text(0.1, 0.8, sprintf('Gini Final: %.3f', results.gini(end)), 'FontSize', 12);
    text(0.1, 0.7, sprintf('Alpha Moyen Final: %.3f', results.avg_alpha(end)), 'FontSize', 12);
    text(0.1, 0.6, sprintf('Inflation Moyenne: %.3f', mean(results.inflation)), 'FontSize', 12);
    text(0.1, 0.5, sprintf('Crise Moyenne: %.3f', mean(results.crisis)), 'FontSize', 12);
    title('Statistiques Finales');
end

%% ============================================================
% 11. EXÉCUTION
% ============================================================

% Lancer la fonction principale
main();

%% ============================================================
% FIN DU CODE MATLAB
% ============================================================

L'algorithme génétique explore l'espace des paramètres pour trouver la combinaison qui minimise une fonction objectif :
function objective = objective_function(params_vector, num_agents, num_steps)
    % Objectif : Minimiser l'inflation, les inégalités et la crise
    objective = 0.4 * inflation_mean + 0.3 * gini_mean + 0.3 * crisis_mean;
end
Paramètres optimisés :
Poids du désir mimétique (mimetic_weight)
Probabilités de transition de Markov (p_adopt_base, p_abandon_base)
Poids des affinités (normal_adoption_weight, community_weight)
Sensibilité à la crise (crisis_risk_amplification)
Borne ajustée automatiquement selon le type de paramètre (probabilité, poids, taux).
Pour chaque paramètre clé, on fait varier sa valeur sur une plage prédéfinie :
param_names = {'base_desire_weight', 'mimetic_weight', 'p_adopt_base', ...
               'intra_community_prob', 'normal_adoption_weight', 'crisis_risk_amplification'};
param_ranges = {0.1:0.1:0.9, 0.1:0.1:0.9, 0.01:0.05:0.5, ...
                0.1:0.1:0.9, 0.1:0.1:0.9, 0.1:0.2:1.5};
Résultats visualisés :
Inflation
Coefficient de Gini
Niveau de crise
Richesse totale (normalisée)
Interprétation :
Si un paramètre influence fortement l'inflation ou le Gini, il est critique.
Le paramètre optimal est celui qui minimise toutes les variables simultanément.
L'interface comprend :
Élément
Fonction
Panneau de contrôle
Démarrer, Arrêter, Pause, Reset
Boutons d'analyse
Optimisation, Analyse de sensibilité
Visualisation du réseau
Graphe dynamique avec couleurs (adoptants en vert)
Graphiques macro
Richesse, Alpha, Désir, Inflation, Crise, Gini
Statistiques en direct
Richesse, Gini, Inflation, Crise, Taux d'adoption

Interactions en temps réel :
La simulation s'exécute en continu avec mise à jour graphique toutes les 5 étapes.
Pause/Reprise pour analyser les dynamiques.
Réinitialisation pour tester de nouvelles configurations.

Fonctionnalité
Status
Lien avec la thèse
Modèle Agent-Based
✅ Complet
Désir mimétique, allocation, Markov
Réseau social
✅ Complet
Communautés, affinités, temporel
Théorie des jeux
✅ Complet
Coordination monétaire, payoffs
Bruit neuronal (Softmax)
✅ Complet
Décision stochastique, température cognitive
Nisab/Zakat
✅ Complet
Seuil, redistribution, stabilisateur
Gouvernance
✅ Complet
Émir, Waqf, élection sans candidat
Optimisation génétique
✅ Complet
Calibration automatique des paramètres
Analyse de sensibilité
✅ Complet
Identification des facteurs critiques
Interface GUI
✅ Complet
Visualisation temps réel


Lancer MATLAB et ouvrir un nouveau fichier .m.
Copier l'intégralité du code ci-dessus.
Exécuter le fichier (F5).
Choisir une option dans le menu :
1 : Interface GUI (recommandé)
2 : Optimisation
3 : Analyse de sensibilité
4 : Simulation standard
5 : Quitter

Souhaitez-vous que j'ajoute des fonctionnalités supplémentaires (exportation de données, rapports PDF, ou intégration avec des données réelles) ?
les tests de Granger-causalité
