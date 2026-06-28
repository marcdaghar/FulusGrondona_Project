# Project manifest — mapping original document order to extracted files

Source: code.odt (1790 paragraphs, ~1.25M characters)

Extraction note: the original document is a sequence of pasted AI-assistant answers,
each containing one or more code blocks, mixed with French prose (introductions,
sample outputs, closing remarks) with no reliable delimiters between them. The French
intro sentence for each section was extracted into a matching `docs/*.intro.txt`
sidecar where non-trivial. Mixed-language sections were split at the language
boundary. Every Python file was verified with `ast.parse`; Solidity/Dart files were
checked for brace balance. See `README.md` for known limitations.


## Section 00 — App Flutter 'Fulus Pocket' (wallet mobile simulé) + fonctions clés CRD Grondona-Yusuf
- `dart/fulus_pocket_wallet_app_part00.dart`
- `python/fulus_pocket_wallet_app_part01.py`
  - Original intro text saved to `docs/fulus_pocket_wallet_app.intro.txt`

## Section 01 — Annexe technique : modèle agent-based de vélocité monétaire
- `python/annexe_modele_velocite_monetaire_part00.py`
- `solidity/annexe_modele_velocite_monetaire_part01.sol`
- `python/annexe_modele_velocite_monetaire_part02.py`
  - Original intro text saved to `docs/annexe_modele_velocite_monetaire.intro.txt`

## Section 02 — Code complet basé sur les spécifications techniques de la thèse (Solidity + Python + Dart)
- `solidity/contrats_et_specs_these_part00.sol`
- `python/contrats_et_specs_these_part01.py`
- `dart/contrats_et_specs_these_part02.dart`
  - Original intro text saved to `docs/contrats_et_specs_these.intro.txt`

## Section 03 — Modélisation de l'étalon monétaire intégré, organisé en modules fonctionnels
- `python/module_etalon_monetaire_integre.py`
  - Original intro text saved to `docs/module_etalon_monetaire_integre.intro.txt`

## Section 04 — Architecture logicielle du projet 'Geometric Ricci Networks' (GRN) : contre-cycle Yusuf, système Grondona, bimétallisme, gamification, étude de cas Dora
- `python/grn_geometric_ricci_networks.py`
  - Original intro text saved to `docs/grn_geometric_ricci_networks.intro.txt`

## Section 05 — Modèle théorique de monnaie (Euro/Franc) et sa dynamique
- `python/modele_theorique_euro_franc.py`
  - Original intro text saved to `docs/modele_theorique_euro_franc.intro.txt`

## Section 06 — Modèles mathématiques et simulations (debt_model et modules associés)
- `python/debt_model_et_simulations.py`
  - Original intro text saved to `docs/debt_model_et_simulations.intro.txt`

## Section 07 — Modélisations mathématiques avec bibliothèques de calcul scientifique
- `python/modelisations_mathematiques_calcul_scientifique.py`
  - Original intro text saved to `docs/modelisations_mathematiques_calcul_scientifique.intro.txt`

## Section 08 — Crypto-Fulus Modelling Suite : modèles mathématiques par théorie
- `python/crypto_fulus_modelling_suite.py`
  - Original intro text saved to `docs/crypto_fulus_modelling_suite.intro.txt`

## Section 09 — Script autonome : optimisation multi-objectif, comparaison système IMF, dynamique des prix avec retards
- `python/optimisation_multiobjectif_imf.py`
  - Original intro text saved to `docs/optimisation_multiobjectif_imf.intro.txt`

## Section 10 — Modèle complet bimétallique Yusuf-Grondona : config, simulation, visualisation, app Streamlit, run_all
Cette section contenait en réalité **deux livraisons distinctes** l'une après l'autre :
- Partie A (les « six fichiers » du modèle Yusuf-Grondona) :
  - `python/yusuf_grondona_requirements.txt`
  - `python/yusuf_grondona_config.yaml`
  - `python/yusuf_grondona_full_project.py` (yusuf_model.py, visualize.py, streamlit_app.py, run_all.py)
- Partie B (modules complémentaires découverts à la suite, avec leur propre README/.gitignore) :
  - `python/yusuf_grondona_partB_requirements.txt`
  - `python/yusuf_grondona_partB.gitignore`
  - `python/yusuf_grondona_partB_modules.py` (neurocognitive agents, Ricci flow, validation statistique, dashboard Streamlit)
  - `docs/yusuf_grondona_partB_README.md`
  - Original intro text saved to `docs/yusuf_grondona_full_project.intro.txt`

## Section 11 — Modèles mathématiques, simulations, projections, visualisations
- `python/modeles_mathematiques_projections.py`
  - Original intro text saved to `docs/modeles_mathematiques_projections.intro.txt`

## Section 12 — Système monétaire bimétallique avec crypto-fulus : simulation et visualisation
- `python/systeme_bimetallique_crypto_fulus_viz.py`
  - Original intro text saved to `docs/systeme_bimetallique_crypto_fulus_viz.intro.txt`

## Section 13 — Formulations mathématiques organisées par thème
- `python/formulations_mathematiques_par_theme.py`
  - Original intro text saved to `docs/formulations_mathematiques_par_theme.intro.txt`

## Section 14 — Prototype : système bimétallique ('rond-point') vs système de dette centralisée ('feu de circulation')
- `python/prototype_rondpoint_vs_feu_circulation.py`
  - Original intro text saved to `docs/prototype_rondpoint_vs_feu_circulation.intro.txt`

## Section 15 — Prototype de démonstration des concepts mathématiques et structurels du manifeste
- `python/prototype_manifeste_demonstration.py`
  - Original intro text saved to `docs/prototype_manifeste_demonstration.intro.txt`

## Section 16 — Modèle hybride : agent-based modeling (NetLogo), théorie de la complexité, blockchain (Solidity), Python
- `netlogo/ecosysteme_monetaire_islamique_hybride_part00.nls`
- `solidity/ecosysteme_monetaire_islamique_hybride_part01.sol`
- `python/ecosysteme_monetaire_islamique_hybride_part02.py`
  - Original intro text saved to `docs/ecosysteme_monetaire_islamique_hybride.intro.txt`

## Section 17 — Formulations mathématiques de la thèse appliquées au système monétaire islamique
- `python/simulation_monnaie_islamique.py`
  - Original intro text saved to `docs/simulation_monnaie_islamique.intro.txt`

## Section 18 — Trois approches : Python, Solidity (smart contract), R (visualisation)
- `python/trois_axes_python_solidity_r_part00.py` (intro française en tête de fichier déplacée vers `docs/trois_axes_python_solidity_r_part00.intro.txt`)
- `solidity/trois_axes_python_solidity_r_part01.sol`
- `r/trois_axes_python_solidity_r_part02.R` (texte de conclusion en français retiré de la fin du fichier)
- `python/trois_axes_python_solidity_r_part03.py`
  - Original intro text saved to `docs/trois_axes_python_solidity_r.intro.txt`

## Section 19 — Approche en trois niveaux : modélisation mathématique (Python), simulation multi-agents (NetLogo), visualisation
- `python/modelisation_3_niveaux_python_netlogo_part00.py`
- `netlogo/modelisation_3_niveaux_python_netlogo_part01.nls`
- `python/modelisation_3_niveaux_python_netlogo_part02.py`
  - Original intro text saved to `docs/modelisation_3_niveaux_python_netlogo.intro.txt`

## Section 20 — Formulations mathématiques avec fonctions de simulation et de visualisation
- `python/formulations_simulation_visualisation.py`
  - Original intro text saved to `docs/formulations_simulation_visualisation.intro.txt`

## Section 21 — Simulation Python (malgré l'intitulé "smart contract" donné dans la réponse originale, le code livré ici est du Python, pas du Solidity) : couverture monétaire or/argent et modèle économique
- `python/smart_contract_or_argent_couverture_part1.py` (simulation de la création monétaire / ratio de couverture)
- `python/smart_contract_or_argent_couverture_part2_economie.py` (classe `Economie`)
  - Original intro text saved to `docs/smart_contract_or_argent_couverture.intro.txt`

## Section 22 — Smart contract Solidity (version 2) : monnaie adossée à l'or et l'argent
- `solidity/smart_contract_or_argent_v2.sol`
  - Original intro text saved to `docs/smart_contract_or_argent_v2.intro.txt`

## Section 23 — Modèle NetLogo : bimétallisme et main invisible, coordination du marché
- `netlogo/netlogo_bimetallisme_main_invisible.nls` (initialement classé par erreur comme R ; corrigé)
  - Original intro text saved to `docs/netlogo_bimetallisme_main_invisible.intro.txt`

## Section 24 — Code structuré en modules, chacun implémentant un aspect clé du modèle
- `python/modules_par_aspect_cle.py`
  - Original intro text saved to `docs/modules_par_aspect_cle.intro.txt`

## Section 25 — Quatre contrats Solidity 'production' pour Ethereum
- `solidity/quatre_contrats_solidity_production_part00.sol`
  - Original intro text saved to `docs/quatre_contrats_solidity_production.intro.txt`

## Section 26 — Modèle académique : reproductibilité, paramétrage, visualisation
- `python/modele_recherche_academique.py`
  - Original intro text saved to `docs/modele_recherche_academique.intro.txt`

## Section 27 — Modèle NetLogo : bruit neuronal, décision stochastique softmax
- `netlogo/netlogo_bruit_neuronal_softmax.nls`
  - Original intro text saved to `docs/netlogo_bruit_neuronal_softmax.intro.txt`

## Section 28 — Version R : réseau complexe avec communautés, feedback macro-économique
- `r/version_r_extensions_reseau_complexe.R`
  - Original intro text saved to `docs/version_r_extensions_reseau_complexe.intro.txt`

## Section 29 — Version MATLAB : chaînes de Markov, transitions d'état des agents
- `matlab/version_matlab_chaines_markov.m`
  - Original intro text saved to `docs/version_matlab_chaines_markov.intro.txt`

## Section 30 — Version MATLAB : optimisation par algorithmes génétiques, analyse de sensibilité
- `matlab/version_matlab_algo_genetique.m`
  - Original intro text saved to `docs/version_matlab_algo_genetique.intro.txt`

## Section 31 — Modèle intégrateur : dynamiques neurocognitives, sociales et monétaires
- `python/modele_integrateur_neurocognitif.py`
  - Original intro text saved to `docs/modele_integrateur_neurocognitif.intro.txt`

## Section 32 — Code modulaire complet, licence CC BY-SA avec clause de souveraineté
- `python/code_modulaire_licence_ccbysa.py`
  - Original intro text saved to `docs/code_modulaire_licence_ccbysa.intro.txt`

## Section 33 — Simulation du pilote Dora : trois scénarios, chocs exogènes, visualisations
- `python/pilote_dora_scenarios_chocs.py`
  - Original intro text saved to `docs/pilote_dora_scenarios_chocs.intro.txt`

## Section 34 — Notes conceptuelles (texte, peu de code) : infiltration rhizomique, blockchain comme technologie de confiance
- `docs/notes_conceptuelles_rhizome_monetaire.md` (converti en Markdown : texte et code Python y sont trop imbriqués pour être séparés de façon fiable — voir la note en tête de ce fichier)
  - Original intro text saved to `docs/notes_conceptuelles_rhizome_monetaire.intro.txt`