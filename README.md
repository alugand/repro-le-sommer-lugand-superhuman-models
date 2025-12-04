# Superhuman Models

## Introduction

La question centrale de cet article est la suivante : comment évaluer les décisions prises par des modèles d'IA surhumains lorsque les humains ne sont plus en mesure de juger de leur exactitude ?
L'hypothèse est la suivante : même lorsque l'exactitude d'un modèle ne peut être vérifiée (par exemple, en raison de capacités surhumaines ou d'une vérité fondamentale inconnue), nous pouvons toujours l'évaluer à l'aide de contrôles de cohérence logique, c'est-à-dire en vérifiant si ses résultats satisfont à des relations logiques interprétables par l'homme.

L'objectif principal est tester les décisions des modèles par rapport à des règles de cohérence. À partir d'un modèle donné, il recherche si les décisions du modèle enfreignent la règle de cohérence (aussi appelée violation-metric). À partir de là, on peut conclure que le modèle est nécessairement erroné sur au moins l'une des entrées testées.

Nous nous concentrons principalement sur la partie du papier centré sur les prédictions d'évenements futurs. Pour cela, nous allons essayer dans un premier temps de reproduire les expériences afin de comparer les résultats obtenus avec les mesures de 4 règles de cohérence présentée ci dessous (violation-metric = vm) :

* Negation (question, negated question pair) : vm = |Pr(A) − (1 − Pr(Ac))|
* Paraphrasing (3 paraphrases for each question): vm = max i,j (|Pr(Ai) − Pr(Aj )|)
* Monotonicity (predictions in the years 2025, 2028, 2032, 2036, and 2040): vm = (1 − ρ)/2 (ρ is the Spearman rank correlation coefficient)
* Bayes’ rule : vm = sqrt(|Pr(A | B) Pr(B) − Pr(B | A) Pr(A)|)

Ensuite, nous replicons les expériences en changeant différents paramètres d'éxécution (modèle de LLM, température T du modèle, stratégie de prompting).

Les résultats obtenus sont en accord avec la conclusion de l'étude qui est de statuer que les LLMs ne peuvent être une source fiable quant à la prédiciton d'évenements futurs. Nous montrons que même en faisant varier de nombreux paramètres, aucune combinaison ne permet d'obtenir des résultats satifsfaisant pour les 4 règles de cohérence.

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

Concrètement,

- Si nous tirons **66 questions au hasard** dans cette population de 175, nous pouvons estimer la proportion de violations « graves » qui dépassent un seuil ε = 0,2  **avec une marge d’erreur maximale de ±8 %** et un **niveau de confiance de 90 %**.  
- Supposons que l’on observe **40 % de questions violant une propriété** dans notre échantillon. On peut **généraliser** que dans toute la population de 175 questions, la proportion réelle se situe probablement **entre 32 % et 48 %** (40 % ± 8 %), avec 90 % de confiance.  

Malheureusement pour des raisons budgétaires nous n'avons pu réaliser qu'une seule expérience en utilisant la taille estimée de l'échantillon (expérience sur la Negation). Les autres expériences ont été menées en utilisant 5 questions pour ne pas dépasser le budget de prompt à l'api openrouter.

## Requirements pour reproduire l'environnement

Ne suivez pas ces étapes si vous souhaitez simplement reproduire les expériences via un container Docker.

1. Exécuter ces commandes à la racine du projet :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

2. Créer un fichier .env à la racine du projet et ajoutez-y les informations suivantes :

```python
OPENAI_API_KEY="VOTRE_API_KEY"
OPENAI_API_BASE="URL_OPENROUTER" #par exemple https://openrouter.ai/api/v1
```

## Reproductibilité

### Reproduire les expériences

* SI vous souhaitez lancer les expériences manuellement (après avoir effectué l'étape de la section Requirements). Par défault, le fichier main.py du dossier src/ lance chaque expérience (negated_pairs, bayes, ...). Si vous souhaitez n'en lancer qu'une seule, commenter la/les lignes désirées puis éxecuter cette commande à la racine du projet:

```bash
python3 src/main.py
```

* SI vous souhaitez utiliser un container Docker (remarque: en raison de la faible qualité du wifi INSA, nous n'avons pas pu tester le fonctionnement de notre container Docker):
Exécuter ces commandes à la racine du projet :

```bash
docker build -t repro -f reproducibility/Dockerfile .
docker run --rm \
  -v "$(pwd)/reproducibility/results":/reproducibility/results \
  -v "$(pwd)/data":/data:ro \
  repro
```

Les résultats des expériences sont stockées dans des fichiers json dans le dossier reproducibility/results/.

### Analyser les résultats

Pour reproduire l'analyse des résultats et calculer la moyenne de violation ainsi que le pourcentage de "strong violations" vous pouvez éxécuter le notebook Jupyter "analysis.ipynb" présent dans le dossier reproducibility/

### Problèmes renontrés, améliorations et Est-ce que l'étude originale est reproductible ?

Le compte rendu de cette section est présent à la fin du notebook reproducibility/analysis.ipynb.

## Replicabilité

### Facteurs de variabilité

Nous avons décidé de faire varier plusieurs paramètres tout en gardant les mêmes questions utilisées par l'étude principale. En effet, il nous a paru plus important d'étudier quelles différences il pouvait y avoir dans la pramétrisation du LLM choisi que dans le type de questions utilisée. Nous conservons aussi les mêmes règles de cohérence qui permettent de calculer les métriques de violation.

Dans un premier temps, nous avons choisi de faire varier le modèle. L'étude utilise 2 modèle distinct mais qui proviennent néanmoins de la même entreprise. Nous avons essayer d'observer si différents modèles pouvait présenter des performances différentes en fonctions de leurs spécificités ou bien leur coût.

Ensuite, nous avons choisi de faire varier la température, la température permet au LLM d'avoir une certaine créativité dans sa réponse et nous nous demandons comment celle-ci peut impacter les mesures de violation.

Pour finir, nous avons fait varier le prompt système du LLM ou nous lui demandons de produire une réponse plus courte, c'est à dire seulement la probabilité ou le pourcentage. Le LLM ne va donc plus afficher son raisonnement et nous voulons savoir si cela a un impact sur les résultats.

Voici l'ensemble de nos expériences résumées dans un tableau :

| Type d’expérience | Modèle LLM | Nb exp par questions | Température | Format de Réponse (indiqué dans le prompt) |
| :--- | :--- | :--- | :--- | :--- |
| Changement modèle | deepseek/deepseek-chat-v3.1 | 3 | 0.0 | long |
| | meta-llama/llama-3.1-8b-instruct | 3 | 0.0 | long |
| | anthropic/claude-3-haiku | 3 | 0.0 | long |
| Changement temperature | gpt-4 | 6 | 0.8 | long |
| | gpt-4 | 6 | 0.3 | long |
| Format de réponse | gpt-4 | 3 | 0.0 | short |
| | gpt-4 | 6 | 0.5 | short |

### Reproduction des expériences de réplication (CLI)

Pour reproduire l'expérience désirée, nous avons mis au point une CLI permettant d'éxécuter une expérience en choisissant les paramètres. Voici l'usage de notre CLI développée en python :

```bash
usage: main.py [-h] 
--type {negated_pair,paraphrase,monotonic,bayes} 
--model MODEL 
[--times TIMES] (default 3)
[--temperature TEMPERATURE] (default 0.0)
[--output-name OUTPUT_NAME] (default no_name_exp)
[--system-prompt {short,long}] (default long)
```

Voici un exemple de commande python permettant de reproduire l'expérience de la ligne 1 avec la règle de cohérence de la Negation.

```bash
python3 replication/main.py --type=negated_pair --model=deepseek/deepseek-chat-v3.1 --times=3 --temperature=0.0 --output-name=negated_exp --system-prompt=long
```

Les résultats sont stockées dans des fichiers .json dans le dossir replication/results.

### Présentation et analyse des résultats

L'analyse des résultats et la reproduction de ceux-ci est disponible dans un Jupyter Notebook présent dans le dossier replication/analysis.ipynb.

A la fin de ce notebook, nous présentons les différents résultats obtenus sous la forme d'un tableau et nous concluons sur la question suivante : "Est ce que les résultats de la réplication confirment l'étude originale ?".

## Conclusion

Notre étude confirme que les LLMs demeurent des oracles de prédiction peu fiables. La reproductibilité n'est que partielle : validée pour GPT-3.5 sur la négation, elle échoue pour GPT-4 qui présente des écarts significatifs. L'analyse de réplicabilité révèle une forte sensibilité aux hyperparamètres : le choix du modèle est critique (DeepSeek et Llama performants en logique, Claude en probabilités), bien que la loi de Bayes reste un échec généralisé. Contre-intuitivement, une température élevée (0.8) a réduit les erreurs logiques par rapport à une température basse. Enfin, si le format court améliore la cohérence sur la négation, il déclenche des refus de réponse sur la Monotonicité. Aucune configuration ne permet donc de garantir des prédictions cohérentes, validant les limites intrinsèques des modèles actuels.
