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

    except Exception as e:
        print(f"Une erreur inattendue est survenue lors de la lecture : {e}")
        return
    for item in data:
        violation_metric: float = item.get("violation_metric")
        is_strong: bool = item.get("strong", False)
        violations.append(violation_metric)
        if is_strong:
            number_of_strong += 1
        else:
            question_preview = item.get("questions", ["Question inconnue"])[0]
            print(f"Avertissement : 'violation_metric' manquante ou None pour : '{question_preview[:50]}...'")
    if not violations:
        print("Aucune donnée de violation valide n'a été trouvée. Impossible de calculer les statistiques.")
        return

    try:
        mean_violation = statistics.mean(violations)
        
        percentage_strong = 100 * number_of_strong / len(violations)
        
        print(f"--- Analyse de {file_path} ---")
        print(f"Nombre de violations fortes (>0.2) : {number_of_strong}")
        print(f"Violation moyenne (statistics.mean) : {mean_violation:.4f}")
        print(f"Pourcentage de violations fortes : {percentage_strong:.2f}%")
        print("-" * 30)

    except Exception as e:
        print(f"Une erreur inattendue est survenue lors des calculs : {e}")


if __name__ == "__main__":

    script_dir = os.path.dirname(__file__) 
    file_to_analyze = os.path.join(script_dir, '../results/output.json')
    
    calculate_statistics(file_to_analyze)