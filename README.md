# Superhuman Models

## Échantillonnage et justification statistique

### Pourquoi ne pas utiliser la population complète ?

L’expérience complète comprend plusieurs centaines de questions et donc évaluer tous les cas serait trop coûteux en temps et en ressources.  
Nous adoptons donc une approche **d’échantillonnage représentatif**, c’est-à-dire que nous testons un sous-ensemble de questions, tout en conservant une précision statistique contrôlée. Plus la taille de l’échantillon est grande, plus les estimations (moyenne, proportion, etc.) sont précises, mais plus le coût est élevé.

### Calcul de la taille d’échantillon
Nous utilisons la **formule standard d’estimation d’une proportion** (cas le plus défavorable), issue de la loi normale. Pour une population finie de taille N, la taille de l’échantillon n est donnée par :


$$
n = \frac{N \cdot z^2 \cdot p(1 - p)}{e^2 (N - 1) + z^2 \cdot p(1 - p)}
$$


où :
- \(N\) = taille de la population
- \(Z\) = score Z correspondant au niveau de confiance choisi (1.645 pour 90 %, 1.96 pour 95 %, 2.576 pour 99 %)
- \(p\) = proportion estimée d’un certain résultat (par défaut 0.5 si inconnue)
- \(e\) = marge d’erreur souhaitée (ex. ±5 % → 0.05)

| Taille de la population (N) | Niveau de confiance | z    | Marge d’erreur (e) | Taille estimée de l’échantillon (n) |
|-----------------------------:|--------------------:|:----:|--------------------:|------------------------------------:|
| 175                         | 90%                | 1.645 | 8%                  | 66 |
| 104                         | 90%                | 1.645 | 8%                  | 53 |
| 50                         | 90%                | 1.645 | 8%                  | 34 |
| 51                        | 90%                | 1.645 | 8%                  | 35 |
