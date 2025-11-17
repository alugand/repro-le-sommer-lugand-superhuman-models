import json
import statistics
import os
from typing import List, Dict, Any

def calculate_statistics(file_path: str):
    
    violations: List[float] = []
    number_of_strong: int = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data: List[Dict[str, Any]] = json.load(f)

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file_path}' n'a pas été trouvé.")
        return
    except json.JSONDecodeError:
        print(f"Erreur : Impossible de décoder le JSON du fichier '{file_path}'.")
        return
    except Exception as e:
        print(f"Une erreur inattendue est survenue lors de la lecture : {e}")
        return
        
    for item in data:
        # Mettre à jour la clé pour lire 'violation' au lieu de 'violation_metric'
        violation_metric: Optional[float] = item.get("violation") 
        is_strong: bool = item.get("strong", False) # 'strong' est déjà calculé par main.py
        
        if violation_metric is not None:
            violations.append(violation_metric)
            if is_strong:
                number_of_strong += 1
        else:
            question_preview = item.get("questions", ["Question inconnue"])[0]
            print(f"Avertissement : 'violation' manquante ou None pour : '{question_preview[:50]}...'")
    
    if not violations:
        print("Aucune donnée de violation valide n'a été trouvée. Impossible de calculer les statistiques.")
        return

    try:
        mean_violation = statistics.mean(violations)
        
        percentage_strong = 100 * number_of_strong / len(violations)
        
        print(f"--- Analyse de {file_path} ---")
        print(f"Nombre total d'éléments analysés : {len(violations)}")
        print(f"Nombre de violations fortes (>0.2) : {number_of_strong}")
        print(f"Violation moyenne (statistics.mean) : {mean_violation:.4f}")
        print(f"Pourcentage de violations fortes : {percentage_strong:.2f}%")
        print("-" * 30)

    except Exception as e:
        print(f"Une erreur inattendue est survenue lors des calculs : {e}")


if __name__ == "__main__":

    # Mettre à jour les noms de fichiers et le chemin pour les résultats des paraphrases
    files = [
        "paraphrase_gpt-3.5_T-0.0",
        "paraphrase_gpt-3.5_T-0.5",
        "paraphrase_gpt-4_T-0.0",
        "paraphrase_gpt-4_T-0.5"
    ]
    
    results_dir = "../../results/paraphrases"
    
    for f_name in files:
        file_path = os.path.join(results_dir, f"output_{f_name}.json")
        if os.path.exists(file_path):
            calculate_statistics(file_path)
        else:
            print(f"Avertissement : Le fichier '{file_path}' n'a pas été trouvé. L'analyse est ignorée.")