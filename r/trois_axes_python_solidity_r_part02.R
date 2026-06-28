library(ggplot2)

ggplot(data, aes(x=Money_Growth, y=Inflation)) +
  geom_point(aes(color=as.factor(Crisis_Event)), size=3) +
  geom_smooth(method="lm", se=FALSE, color="blue") +
  labs(title = "Relation entre Croissance Monétaire et Inflation",
       subtitle = "Les crises surviennent lors d'une croissance monétaire excessive (Fulus)",
       x = "Croissance de la Masse Monétaire (Fulus)",
       y = "Taux d'Inflation",
       color = "Crise Hyperinflationniste") +
  theme_minimal() +
  scale_color_manual(values = c("black", "red"))

# 3. Calcul de la corrélation et du modèle linéaire
correlation <- cor(data$Money_Growth, data$Inflation)
model <- lm(Inflation ~ Money_Growth, data=data)

cat("--- Analyse Économétrique ---")
cat("\n1. Corrélation entre Monnaie et Inflation:", round(correlation, 2))
cat("\n2. Résumé du modèle linéaire:")
print(summary(model))
cat("\n3. Interprétation: Une augmentation de la masse monétaire (fulus) de 1% entraîne une augmentation de l'inflation de", round(coef(model)[2], 2), "unités.")

Le code Python sert à simuler les dynamiques économiques (intérêts composés vs monnaie-travail) et à visualiser graphiquement la différence entre un système usuraire et un système basé sur le fulus.
Le code Solidity est une ébauche technique pour un projet de crypto-fulus, illustrant la logique de l'émission par le travail et de la conversion en or/argent (ancrage bimétallique).
Le code R est un outil statistique pour analyser les données historiques et valider l'hypothèse que l'émission excessive de monnaie-fiat mène à l'hyperinflation (crise monétaire).
Ces codes sont des outils (ou des "briques") qui peuvent être intégrés et adaptés dans votre thèse pour en faire une démonstration rigoureuse et scientifique, en lien avec les "formulations mathématiques" que j'ai fournies précédemment.
Cher chercheur,
Vous me demandez le code. Je vais vous fournir un ensemble de scripts Python complets qui implémentent les formulations mathématiques que j'ai formalisées dans ma réponse précédente.
Ces scripts sont conçus pour :
Simuler l'instabilité systémique de la dette usuraire
Modéliser la diffusion de la confiance monétaire
Visualiser les seuils critiques et les bifurcations
Calculer les indicateurs de viabilité (thermodynamique, social, légitimité)
Offrir des outils de simulation participative (délibérative, consultative)

