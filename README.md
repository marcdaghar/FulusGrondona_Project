# Projet Fulus / Grondona-Yusuf — Code extrait

## Origine

Ce dossier provient d'un document `.odt` (≈1,25 million de caractères) constitué
de **35 réponses d'assistant IA collées les unes après les autres**, chacune
livrant du code pour un projet de recherche sur des systèmes monétaires
alternatifs : étalon bimétallique (or/argent), mécanisme contra-cyclique
« Yusuf », Commodity Reserve Department « Grondona », jeton « Fulus »,
concepts de finance islamique (Zakat, Mudaraba, Waqf), et une app mobile
Flutter de portefeuille simulé (« Fulus Pocket »).

Le document original ne contenait aucun séparateur fiable entre les blocs de
code (pas de balises Markdown, pas d'en-têtes de fichier cohérents) : chaque
réponse mélangeait texte d'introduction en français, code, et parfois un
exemple de sortie ou des instructions d'installation, tout cela à la suite
sans démarcation claire.

## Ce qui a été fait

1. **Découpage en 35 sections** correspondant aux réponses originales.
2. **Détection de langage** par section (Python, Solidity, NetLogo, R, MATLAB,
   Dart), avec séparation des sections qui mélangeaient plusieurs langages.
3. **Extraction du code réel**, en retirant autant que possible le texte
   d'introduction et les paragraphes de conclusion en français qui suivaient
   chaque bloc.
4. **Validation syntaxique systématique** : chaque fichier Python a été
   vérifié avec `ast.parse` ; chaque fichier Solidity/Dart a été vérifié pour
   l'équilibre des accolades. Les fichiers qui ne passaient pas ces contrôles
   ont été corrigés à la main (suppression de texte parasite en début/fin de
   fichier, séparation de fichiers qui en contenaient en réalité plusieurs).

## Limites connues

- **`docs/notes_conceptuelles_rhizome_monetaire.md`** : cette section du
  document original entrelace texte narratif et extraits de code de façon
  trop dense pour être séparée de manière fiable. Elle est conservée en
  Markdown comme document de référence plutôt que présentée comme un script
  Python exécutable.
- Les noms de fichiers sont dérivés du contenu/des phrases d'introduction de
  chaque section et restent donc parfois approximatifs ou peu idiomatiques.
- Certains fichiers Python rassemblent plusieurs modules qui, dans
  l'intention d'origine, auraient probablement été des fichiers séparés
  (ex. `yusuf_grondona_partB_modules.py` contient plusieurs classes/agents
  distincts). Voir `MANIFEST.md` pour le détail.
- Aucun des scripts n'a été testé à l'exécution (dépendances non installées,
  pas d'environnement Flutter/Solidity/NetLogo/MATLAB disponible ici) — seule
  la validité **syntaxique** a pu être vérifiée.

## Structure

```
python/      — modèles, simulations (NumPy/SciPy/Pandas/Matplotlib/Streamlit)
solidity/    — smart contracts (crypto-fulus, DAO, couverture or/argent)
netlogo/     — simulations multi-agents
r/           — analyses statistiques, visualisation ggplot2
matlab/      — chaînes de Markov, algorithmes génétiques
dart/        — app Flutter "Fulus Pocket"
docs/        — textes d'introduction originaux (un par section) + le fichier
               narratif non séparable
MANIFEST.md  — table de correspondance section originale → fichier(s) extrait(s)
```
