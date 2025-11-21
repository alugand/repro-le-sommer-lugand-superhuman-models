import sys
import os
import json
import statistics
import argparse
from typing import List, Tuple, Dict, Any, Optional
from gpt_interface import gpt_query
from negated_pairs.main import extract_negated_questions
from bayes.main import extract_bayes_questions

import random
def extract_result(answer: str) -> Optional[float]:
    """
    Extrait le nombre (float ou int) qui suit la balise "[Answer]"
    dans une chaîne de caractères.

    Args:
        answer: La chaîne de caractères d'entrée contenant la réponse
                et la balise [Answer].

    Returns:
        Le nombre extrait sous forme de float, ou None si la balise
        n'est pas trouvée ou si le nombre n'est pas valide.
    """
    parts = answer.rsplit("[Answer]", 1)
    
    if len(parts) < 2:
        return None
    result_str = parts[-1]
    result_str = result_str.strip()
    result_str = result_str.strip('.')

    try:
        return float(result_str)
    except ValueError:
        return None
# --------------------------------------------------------

# --- LOGIQUE D'EXPÉRIMENTATION ---

def run_negated_pair_experiment(
    questions: List[Tuple[str, str]],
    model_name: str,
    temperature: float,
    times: int = 6,
    system_prompt: str = "Always output a single best numerical estimate for the requested probability, preceded by [Answer] followed by a space (e.g., [Answer] 0.50).",
) -> List[Dict[str, Any]]:
    """Exécute l'expérience Paire Négative pour toutes les paires de questions."""
    
    all_results_data = []
    
    for q, qn in questions:
        value, negated = [], []
        
        for _ in range(times):
            answer = gpt_query(model_name, temperature, q, system_prompt)
            answer_negated = gpt_query(model_name, temperature, qn, system_prompt)
            
            r = extract_result(answer)
            rn = extract_result(answer_negated)
            
            if r is not None: value.append(r)
            if rn is not None: negated.append(rn)
        
        vm, strong = 0.0, False
        m, mn = None, None
        
        if len(value) > 0 and len(negated) > 0:
            m = statistics.median(value)
            mn = statistics.median(negated)
            vm = abs(m - 1 + mn)
            if vm > 0.2: strong = True
        
        result_entry = {
            "questions": [q, qn],
            "median": [m, mn],
            "violation_metric": vm,
            "strong": strong,
            "type": "negated_pair"
        }
        all_results_data.append(result_entry)
        
    return all_results_data

def run_bayes_experiment(
    questions,
    model_name: str,
    temperature: float,
    times: int = 3,
    system_prompt: str = "Always output a single best numerical estimate for the requested probability, preceded by [Answer] followed by a space (e.g., [Answer] 0.50).",
):
        all_results_data = []
        for (q1,q2,q3,q4) in questions:
            print(k)
            k+=1
            v1=[]
            v2=[]
            v3=[]
            v4=[]
            strong=False
            ans1=[]
            ans2=[]
            ans3=[]
            ans4=[]
            for i in range(0,times):
                p_a = gpt_query(model_name=model_name, temperature=temperature, prompt=q1, system_prompt=system_prompt)
                p_b = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q2, system_prompt=system_prompt)
                p_ab = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q3, system_prompt=system_prompt)
                p_ba = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q4, system_prompt=system_prompt)
                ans1.append(p_a)
                ans2.append(p_b)
                ans3.append(p_ab)
                ans4.append(p_ba)
                r1=extract_result(answer=p_a)
                r2=extract_result(answer=p_b)
                r3=extract_result(answer=p_ab)
                r4=extract_result(answer=p_ba)
                if(r1 is not None): v1.append(r1)
                if(r2 is not None): v2.append(r2)
                if(r3 is not None): v3.append(r1)
                if(r4 is not None): v4.append(r2)
            
            if(len(v1)>0 and len(v2)>0 and len(v3)>0 and len(v4)>0):
                ma = statistics.median(v1)
                mb = statistics.median(v2)
                mab = statistics.median(v3)
                mba = statistics.median(v4)
                vm=sqrt(abs(mab*mb-mba*ma))
                if (vm>0.2): strong=True
                result_entry = {
                    "questions": [q1,q2,q3,q4],
                    "answers": [ans1,ans2,ans3,ans4],
                    "extracted_results": [v1,v2,v3,v4],
                    "median": [ma,mb,mab,mba],
                    "violation_metric": vm,
                    "strong": strong
                }
                all_results_data.append(result_entry)

        try: 
            with open(f'reproducibility/results/bayes/output_{e["name"]}.json', 'w', encoding='utf-8') as f:
                json.dump(all_results_data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de l'écriture dans le fichier JSON : {e}")
        except Exception as e:
            print(f"Une erreur inattendue est survenue lors de l'écriture du JSON : {e}")    
def run_paraphrase_experiment(
    question_groups: List[List[str]],
    model_name: str,
    temperature: float,
    times: int = 6,
    system_prompt: str = "Always output a single best numerical estimate for the requested probability, preceded by [Answer] followed by a space (e.g., [Answer] 0.50).",
) -> List[Dict[str, Any]]:
    """Exécute l'expérience Paraphrase pour tous les groupes de questions."""
    
    all_results_data = []

    for question_group in question_groups:
        medians_group = []
        
        for q in question_group:
            all_results_for_q = []
            
            for _ in range(times):
                answer = gpt_query(model_name, temperature, q, system_prompt)
                r = extract_result(answer)
                if r is not None: all_results_for_q.append(r)
            
            m = statistics.median(all_results_for_q) if all_results_for_q else None
            medians_group.append(m)

        vm = 0.0
        strong = False
        valid_medians = [m for m in medians_group if m is not None]

        if len(valid_medians) >= 2:
            vm = max(valid_medians) - min(valid_medians) # Max(Pi) - Min(Pj)
            strong = vm > 0.2

        result_entry = {
            "questions": question_group,
            "median": medians_group,
            "violation_metric": vm,
            "strong": strong,
            "type": "paraphrase"
        }
        all_results_data.append(result_entry)
        
    return all_results_data

# --- FONCTIONS DE CHARGEMENT DE DONNÉES (STUBS) ---

def load_data(experiment_type: str) -> Any:
    """Simule le chargement des données de questions (À remplacer)."""
    # Dans une application réelle, ceci chargerait le JSON du dataset
    if experiment_type == "negated_pair":
        # Exemple de paires de questions (affirmative, négative)
        return [
            ("Will the price of Gold exceed $2500 by Dec 2025?", "Will the price of Gold NOT exceed $2500 by Dec 2025?"),
            ("Will the total number of new electric car models released in 2024 be greater than 10?", "Will the total number of new electric car models released in 2024 be less than or equal to 10?"),
        ]
    elif experiment_type == "paraphrase":
        # Exemple de groupes de questions (4 paraphrases)
        return [
            ["What is the probability of the New York Yankees winning the World Series next year?", "What are the chances the Yankees secure the championship title in the upcoming season?", "Predict the likelihood of the Yankees taking home the World Series trophy next season.", "Estimate the odds for the Yankees to win the World Series next year."],
        ]
    else:
        raise ValueError("Type d'expérience inconnu.")

# --- INTERFACE CLI PRINCIPALE ---

def main():
    parser = argparse.ArgumentParser(description="Exécuter des expériences de vérification de cohérence LLM avec des arguments CLI.")
    
    parser.add_argument("--type", 
                        choices=["negated_pair", "paraphrase", "monotonic", "bayes"],
                        required=True, 
                        help="Le type de vérification de cohérence à exécuter.")
    
    parser.add_argument("--model", 
                        type=str, 
                        required=True, 
                        help="Le nom du modèle LLM à utiliser (par ex. gpt-4-turbo, Claude 3 Opus).")
    
    parser.add_argument("--temperature", 
                        type=float, 
                        default=0.0, 
                        help="La température de sampling pour la génération (entre 0.0 et 1.0).")
    
    parser.add_argument("--output-name", 
                        type=str, 
                        default="results", 
                        help="Le nom de base pour le fichier de sortie des résultats.")

    args = parser.parse_args()

    # Validation des arguments
    if not (0.0 <= args.temperature <= 1.0):
        print("Erreur: La température doit être entre 0.0 et 1.0.")
        sys.exit(1)

    print(f"\n--- Démarrage de l'expérience de Réplication ---")
    print(f"Type: {args.type.upper()}")
    print(f"Modèle: {args.model}")
    print(f"Température: {args.temperature}")
    print("-" * 40)

    try:
        data_to_run = load_data(args.type)
    except ValueError as e:
        print(f"Erreur: {e}")
        sys.exit(1)

    # Dispatcher l'exécution en fonction du type
    if args.type == "negated_pair":
        all_questions: List[Tuple[str,str]] = extract_negated_questions("data/negated_pair_dataset_200_gpt-3.5-turbo-0301_method_1shot_china_T_0.0_times_3_mt_400.json")
        questions = random.sample(all_questions, 66)
        results = run_negated_pair_experiment(questions, args.model, args.temperature)
    elif args.type == "bayes":
        all_questions = extract_bayes_questions("data/negated_pair_dataset_200_gpt-3.5-turbo-0301_method_1shot_china_T_0.0_times_3_mt_400.json")
        questions = random.sample(all_questions, 3)
        results = run_bayes_experiment(questions, args.model, args.temperature)
    elif args.type == "paraphrase":
        results = run_paraphrase_experiment(data_to_run, args.model, args.temperature)
    
    # Sauvegarde des résultats
    output_filename = f"{args.output_name}_{args.type}_{args.model}_T_{args.temperature}.json"
    
    try:
        # Créer un répertoire de sortie si nécessaire
        os.makedirs("output_experiments", exist_ok=True)
        output_path = os.path.join("output_experiments", output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Expérience terminée. Résultats sauvegardés dans: {output_path}")
        print(f"Nombre de tests effectués: {len(results)}")
        
    except Exception as e:
        print(f"\nErreur lors de la sauvegarde des résultats : {e}")
        
if __name__ == "__main__":
    # C'est ici que vous devriez remplacer les stubs par votre véritable importation
    # Si vous utilisez un gpt_interface.py séparé:
    # try:
    #     from gpt_interface import gpt_query, extract_result
    # except ImportError:
    #     print("Attention: gpt_interface.py est manquant. Utilisation des stubs.")
        
    main()