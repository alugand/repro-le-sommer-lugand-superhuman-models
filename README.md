# Superhuman Models

## Introduction

La question centrale de cet article est la suivante : comment évaluer les décisions prises par des modèles d'IA surhumains lorsque les humains ne sont plus en mesure de juger de leur exactitude ?
L'hypothèse est la suivante : même lorsque l'exactitude d'un modèle ne peut être vérifiée (par exemple, en raison de capacités surhumaines ou d'une vérité fondamentale inconnue), nous pouvons toujours l'évaluer à l'aide de contrôles de cohérence logique, c'est-à-dire en vérifiant si ses résultats satisfont à des relations logiques interprétables par l'homme.

L'objectif principal est tester les décisions des modèles par rapport à des règles de cohérence. À partir d'un modèle donné, il recherche si les décisions du modèle enfreignent la règle de cohérence. À partir de là, on peut conclure que le modèle est nécessairement erroné sur au moins l'une des entrées testées.

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
- Si nous tirons **66 questions au hasard** dans cette population de 175,  
  nous pouvons estimer la proportion de violations « graves » qui dépassent un seuil ε = 0,2  **avec une marge d’erreur maximale de ±8 %** et un **niveau de confiance de 90 %**.  
- Concrètement :  
  - Supposons que l’on observe **40 % de questions violant une propriété** dans notre échantillon.  
  - On peut **généraliser** que dans toute la population de 175 questions, la proportion réelle se situe probablement **entre 32 % et 48 %** (40 % ± 8 %), avec 90 % de confiance.  

## Reproductibilité

### Requirements

Créer un fichier .env à la racine du projet et ajoutez-y les informations suivantes :

```python
OPENAI_API_KEY="VOTRE_API_KEY"
OPENAI_API_BASE="URL_OPENROUTER" #par exemple https://openrouter.ai/api/v1
```

### Créer l'environnement et reproduire les expériences

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

Pour reproduire les résultats et calculer la moyenne de violation ainsi que le pourcentage de "strong violations" vous pouvez éxécuter le notebook Jupyter "analysis.ipynb" présent dans le dossier reproducibility/

### Problèmes renontrés et améliorations

- Report any challenges, errors, or deviations from the original study.
- Describe how these issues were resolved or improved, if applicable.

### Is the Original Study Reproducible?
- Summarize the success or failure of reproducing the study.
- Include supporting evidence, such as comparison tables, plots, or metrics.

## Replicability

### Variability Factors
- **List of Factors**: Identify all potential sources of variability (e.g., dataset splits, random seeds, hardware).  
  Example table:
  | Variability Factor | Possible Values     | Relevance                                   |
  |--------------------|---------------------|--------------------------------------------|
  | Random Seed        | [0, 42, 123]       | Impacts consistency of random processes    |
  | Hardware           | CPU, GPU (NVIDIA)  | May affect computation time and results    |
  | Dataset Version    | v1.0, v1.1         | Ensures comparability across experiments   |

- **Constraints Across Factors**:  
  - Document any constraints or interdependencies among variability factors.  
    For example:
    - Random Seed must align with dataset splits for consistent results.
    - Hardware constraints may limit the choice of GPU-based factors.

- **Exploring Variability Factors via CLI (Bonus)**  
   - Provide instructions to use the command-line interface (CLI) to explore variability factors and their combinations:  
     ```bash
     python explore_variability.py --random-seed 42 --hardware GPU --dataset-version v1.1
     ```
   - Describe the functionality and parameters of the CLI:
     - `--random-seed`: Specify the random seed to use.
     - `--hardware`: Choose between CPU or GPU.
     - `--dataset-version`: Select the dataset version.


### Replication Execution
1. **Instructions**  
   - Provide detailed steps or commands for running the replication(s):  
     ```bash
     bash scripts/replicate_experiment.sh
     ```

2. **Presentation and Analysis of Results**  
   - Include results in text, tables, or figures.
   - Analyze and compare with the original study's findings.

### Does It Confirm the Original Study?
- Summarize the extent to which the replication supports the original study’s conclusions.
- Highlight similarities and differences, if any.

## Conclusion
- Recap findings from the reproducibility and replicability sections.
- Discuss limitations of your

