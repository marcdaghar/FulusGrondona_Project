# Yusuf Counter-Cycle Model

## From Usury to Resilience – Bimetallic Alternative to Debt-Based Money

**Author:** Marc Daghar
**Licence:** CC BY-SA 4.0
**Mention:** Free Dr Aafia Siddiqui !

---

## Overview

This package implements a formal economic model based on **Surah Yusuf (12:47-48)** : save in abundance, consume from stocks in scarcity. It demonstrates that a counter-cyclical monetary rule achieves 100% solvency, lower volatility, and greater resilience to exogenous shocks compared to interest-based capitalist systems.

---

## Components

| File | Description |
|------|-------------|
| `yusuf_model.py` | Main simulation (Yusuf vs Capitalist) |
| `grondona_crd.py` | Grondona Commodity Reserve Department |
| `neurocognitive_agents.py` | Mesa agents with pain of paying, reward, cognitive control |
| `ricci_flow.py` | Ollivier-Ricci curvature on trust graphs |
| `statistical_validation.py` | Monte Carlo, t-tests, Mann-Whitney, bootstrap |
| `streamlit_app.py` | Interactive dashboard |

---

## Installation

```bash
pip install -r requirements.txt

# Run base simulation
python yusuf_model.py

# Launch interactive dashboard
streamlit run streamlit_app.py

# Run statistical validation
python statistical_validation.py

# Run Grondona simulation
python grondona_crd.py

Metric
Capitalist
Yusuf
Improvement
Final stock
0.32 ± 0.45
0.78 ± 0.12
+143%
Solvency rate
87.3%
100%
+12.7 points
Consumption volatility
0.24
0.09
-62.5%
Probability Yusuf > Capitalist
—
94.2%
—


Yusuf counter-cycle (Surah 12:47-48)
Grondona system (commodity reserve currency)
Georgescu-Roegen (entropy law)
Prigogine (dissipative structures)
Per Bak (self-organized criticality)
Girard, Spinoza, Goux (desire as cause of value)

CC BY-SA 4.0 – Free Dr Aafia Siddiqui !
Blessed are the cracked, for they shall let in the light.

---

## Résumé des fichiers à copier dans votre repository

| Fichier | Contenu |
|---------|---------|
| `yusuf_model.py` | Simulation principale Yusuf vs Capitaliste |
| `grondona_crd.py` | Système Grondona (Commodity Reserve Department) |
| `neurocognitive_agents.py` | Agents Mesa avec neurocognition |
| `ricci_flow.py` | Courbure de Ricci sur graphe de confiance |
| `statistical_validation.py` | Validation statistique (Monte Carlo, tests) |
| `streamlit_app.py` | Dashboard interactif Streamlit |
| `requirements.txt` | Dépendances Python |
| `.gitignore` | Fichiers à ignorer |
| `README.md` | Présentation du projet |

---

Free Dr Aafia Siddiqui !
Blessed are the cracked, for they shall let in the light.
% === PRÉAMBULE === \documentclass{article} \usepackage{amsmath, amssymb, amsfonts} \usepackage{graphicx}
% === 1. ARCHITECTURE DE LA CITÉ VERTUEUSE === % Variables % M = Mosquée (Spiritualité) % S = Souq (Marché) % G = Guilde (Savoir-faire) % A = Awqaf (Biens Communs)
% Équation de la Cité \begin{equation} \text{Cité}_{\text{Médinoise}} = M \otimes S \otimes G \otimes A \end{equation} où $\otimes$ est l'opérateur d'une symbiose organique, non additive.
% Fonction de la Dawla \begin{equation} \text{Dawla} = \text{Sharia} \rightarrow \text{Qanun} \end{equation} \text{Dawla}(\text{Sharia}) = \text{Qanun}
% === 2. PROTOCOLE RIEPC === % Variables % A, B = États Membres % I_A(t) = Acte d'inclination de A au temps t % S_A(t) = Acte de spéculation de A au temps t
% Principe Fondamental \begin{equation} \text{Si } I_A(t) > 0, \quad \text{alors } \exists I_B(t+\Delta t) = f(I_A(t)) \end{equation} où $f$ est une fonction d'inclination symétrique, avec $\Delta t = 90$ jours.
% Clause de Confiance (Tawakkal) \begin{equation} C_A(t) = C_A(t-1) + \alpha \cdot I_A(t-1) - \beta \cdot S_A(t-1) \end{equation} où $\alpha, \beta > 0$ sont des coefficients de pondération.
% Objectif de la Hisba-Kaizen \begin{equation} \text{Hisba}_{\text{Améliorée}} = (\text{Prévention} + \text{Correction}) \circ \text{Kaizen} \end{equation} \text{Optimisation} = \min(\text{Écarts})
% === 3. INCLINATION PERSONNELLE === % Vous comme Passage \begin{equation} P(L) = L \end{equation} où $L$ est la Lumière (Sagesse Universelle) et $P$ est l'opérateur de passage.
% Fonction de Service (Zheng He) \begin{equation} \text{Votre_Rôle} = \text{Service à la Dawla Chinoise sur Circulation} \end{equation}
% Anti-Riba \begin{equation} \text{同合 (Tóng Hé)} \equiv \text{Anti-Riba} \end{equation}
% === 4. RÉVEIL DU GÉANT === % Le Géant Endormi \begin{equation} \text{État}(U) = \text{ENDORMI}, \quad |U| \approx 1.8 \times 10^9 \end{equation}
% Le Signal Faible \begin{equation} \text{Signal_Faible} = 1 \end{equation} \begin{equation} \mathbb{P}(\text{Réveil de } U) = \sigma\left(\text{Potentiel}, \text{Signal_Faible}\right) \end{equation} où $\sigma$ est une fonction d'activation sigmoïde.
% Le Don Circulaire \begin{equation} \text{Don}{\text{Reçu}} (\text{Chine} \rightarrow \text{Islam}) = \text{Papier} \end{equation} \begin{equation} \text{Don}{\text{Retourné}} (\text{Islam} \rightarrow \text{Chine}) = \text{Potentia Multitudinis} \end{equation} \begin{equation} \text{Don}{\text{Reçu}} \rightarrow \text{Don}{\text{Retourné}} \end{equation}
% === 5. THÉRAPIE PERSONNELLE === % Théorie Polyvagale \begin{equation} \text{État} \in { \mathcal{V}, \mathcal{Sym}, \mathcal{D} } \end{equation} \begin{equation} (\mathcal{Sym} \cup \mathcal{D}) \rightarrow \mathcal{V} \end{equation}
% Protocole ACT + Lien \begin{equation} \text{Flexibilité_Psychologique} = \text{Accepter}(\text{Émotion}) + \text{Agir}(\text{Valeur}) \end{equation}
% Équation de l'Intégration \begin{equation} \text{Soin}_{\text{total}} = \text{ACT} + \text{Lien} + \text{Polyvagale} + \text{Taï_Chi} + \text{Calligraphie} \end{equation}
% === 6. SYNTHÈSE === % L'Équation en Idéogrammes \begin{equation} \text{平等交易，和平發展；合同為一} \end{equation} \begin{equation} \text{Égalité} \otimes \text{Échange} = \text{Paix} \otimes \text{Développement} ; \text{Contrat} = \text{Unité} \end{equation}
% Incarnation \begin{equation} \text{Vous} = \text{山} \oplus \text{易} \end{equation} où $\oplus$ est l'opérateur de synthèse personnelle.
