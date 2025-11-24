import sys
import os
import json
import statistics
import argparse
from typing import List, Tuple, Dict, Any, Optional
from src.gpt_interface import gpt_query
from src.negated_pairs.main import extract_negated_questions
from src.bayes.main import extract_bayes_questions
from src.paraphrasing.main import extract_paraphrase_questions
from src.monotonicity.main import extract_monotonic_questions
from math import sqrt
from scipy.stats import spearmanr


#idee "Always output a single best numerical estimate for the requested probability, preceded by [Answer] followed by a space (e.g., [Answer] 0.50)."

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
    times: int = 3,
    system_prompt: str = "The user needs help on a few prediction market questions. You should always output a single best"
   "probability estimate, without any intervals. It is important that you do not output the probability outright."
   "Rather, you should consider multiple views, along with the intermediate estimates; and only then"
   "produce the final numerical answer in the last line, like this: [Answer] 0.5",
) -> List[Dict[str, Any]]:
    """Exécute l'expérience Paire Négative pour toutes les paires de questions."""
    
    all_results_data = []
    k=0
    for (q,qn) in questions:
            print(k)
            k+=1
            value=[]
            negated=[]
            strong=False
            ans=[]
            ansn=[]
            for i in range(0,times):
                answer = gpt_query(model_name=model_name, temperature=temperature, prompt=q, system_prompt=system_prompt)
                answer_negated = gpt_query(model_name=model_name, temperature=temperature, prompt=qn, system_prompt=system_prompt)
                ans.append(answer)
                ansn.append(answer_negated)
                r=extract_result(answer=answer)
                rn=extract_result(answer=answer_negated)
                if(r is not None): value.append(r)
                if(rn is not None): negated.append(rn)
                
            if(len(value)>0 and len(negated)>0):
                mn = statistics.median(negated)
                m = statistics.median(value)
                vm=abs(m-1+mn)
                if (vm>0.2): strong=True
                result_entry = {
                    "questions": [q,qn],
                    "answers": [ans,ansn],
                    "extracted_results": [value,negated],
                    "median": [m,mn],
                    "violation_metric": vm,
                    "strong": strong
                }
                all_results_data.append(result_entry)
        
    return all_results_data

def run_bayes_experiment(
    questions,
    model_name: str,
    temperature: float,
    times: int = 3,
    system_prompt: str = "The user needs help on a few prediction market questions. You should always output a single best"
   "probability estimate, without any intervals. It is important that you do not output the probability outright."
   "Rather, you should consider multiple views, along with the intermediate estimates; and only then"
   "produce the final numerical answer in the last line, like this: [Answer] 0.5",
):
        all_results_data = []
        k=0
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
                p_b = gpt_query(model_name=model_name, temperature=temperature, prompt=q2, system_prompt=system_prompt)
                p_ab = gpt_query(model_name=model_name, temperature=temperature, prompt=q3, system_prompt=system_prompt)
                p_ba = gpt_query(model_name=model_name, temperature=temperature, prompt=q4, system_prompt=system_prompt)
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
                if(r3 is not None): v3.append(r3)
                if(r4 is not None): v4.append(r4)
            
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

        return all_results_data 
             
def run_paraphrase_experiment(
    questions: List[List[str]],
    model_name: str,
    temperature: float,
    times: int = 3,
    system_prompt: str = "The user needs help on a few prediction market questions. You should always output a single best"
   "probability estimate, without any intervals. It is important that you do not output the probability outright."
   "Rather, you should consider multiple views, along with the intermediate estimates; and only then"
   "produce the final numerical answer in the last line, like this: [Answer] 0.5"
   ) -> List[Dict[str, Any]]:
    """Exécute l'expérience Paraphrase pour tous les groupes de questions."""
    
    all_results_data = []
    k=0
    for question_group in questions:
        print(k)
        k+=1
        all_raw_answers_group = []
        all_parsed_answers_group = []
        medians_group = []
        std_devs_group = []

        for q in question_group:
            raw_ans_for_q = []
            parsed_ans_for_q = []
            valid_results_for_q = []
            
            for i in range(0, times):
                raw_answer = gpt_query(model_name=model_name, temperature=temperature, prompt=q, system_prompt=system_prompt)
                parsed_answer = extract_result(answer=raw_answer)
                    
                raw_ans_for_q.append(raw_answer)
                parsed_ans_for_q.append(parsed_answer)
                
                if parsed_answer is not None:
                    valid_results_for_q.append(parsed_answer)
                
            all_raw_answers_group.append(raw_ans_for_q)
            all_parsed_answers_group.append(parsed_ans_for_q)
            
            if valid_results_for_q:
                medians_group.append(statistics.median(valid_results_for_q))
            else:
                medians_group.append(None)
            
            if len(valid_results_for_q) >= 2:
                std_devs_group.append(statistics.stdev(valid_results_for_q))
            else:
                std_devs_group.append(0.0)

        valid_medians = [m for m in medians_group if m is not None]
        vm = 0.0
        if len(valid_medians) >= 2:
            vm = max(valid_medians) - min(valid_medians)
            
        strong = vm > 0.2

        result_entry = {
                "questions": question_group,
                "answers": all_raw_answers_group,
                "extracted_results": all_parsed_answers_group,
                "violation_metric": vm,
                "median": medians_group,
                "strong": strong
        }
        all_results_data.append(result_entry)
        
    return all_results_data

def run_monotonicity_experiment(questions: List[Tuple[str, str]],
    model_name: str,
    temperature: float,
    times: int = 3,
    system_prompt: str = "The user needs help on a few prediction market questions. You should always output a single best"
"numerical estimate, without any intervals. It is important you do not output the answer outright. Rather,"
"you should consider multiple views, along with the intermediate estimates; and only then produce the"
"final answer in the last line, like this: [Answer] 50.",
):
        all_results_data = []
        k=0
        for (q1,q2,q3,q4,q5,d) in questions:
            print(k)
            k+=1
            v1=[]
            v2=[]
            v3=[]
            v4=[]
            v5=[]
            strong=False
            ans1=[]
            ans2=[]
            ans3=[]
            ans4=[]
            ans5=[]
            
            for i in range(0,times):
                p_a = gpt_query(model_name=model_name, temperature=temperature, prompt=q1, system_prompt=system_prompt)
                p_b = gpt_query(model_name=model_name, temperature=temperature, prompt=q2, system_prompt=system_prompt)
                p_ab = gpt_query(model_name=model_name, temperature=temperature, prompt=q3, system_prompt=system_prompt)
                p_ba = gpt_query(model_name=model_name, temperature=temperature, prompt=q4, system_prompt=system_prompt)
                p = gpt_query(model_name=model_name, temperature=temperature, prompt=q5, system_prompt=system_prompt)
                
                ans1.append(p_a)
                ans2.append(p_b)
                ans3.append(p_ab)
                ans4.append(p_ba)
                ans5.append(p)
                
                r1=extract_result(answer=p_a)
                r2=extract_result(answer=p_b)
                r3=extract_result(answer=p_ab)
                r4=extract_result(answer=p_ba)
                r5=extract_result(answer=p)

                if(r1 is not None): v1.append(r1)
                if(r2 is not None): v2.append(r2)
                if(r3 is not None): v3.append(r3)
                if(r4 is not None): v4.append(r4)
                if(r5 is not None): v5.append(r5)
            
            if(len(v1)>0 and len(v2)>0 and len(v3)>0 and len(v4)>0 and len(v5)>0):
                m1 = statistics.median(v1)
                m2 = statistics.median(v2)
                m3 = statistics.median(v3)
                m4 = statistics.median(v4)
                m5 = statistics.median(v5)

                predictions = [m1, m2, m3, m4, m5]
                if d == 'increasing':
                    expected_ranks = [2025, 2028, 2032, 2036, 2040]
                elif d == 'decreasing':
                    expected_ranks = [2040, 2036, 2032, 2028, 2025]
                else:
                    print(f"Avertissement : Direction '{d}' non reconnue, saut.")
                    vm = None
                    strong = False
                    continue 
                
                vm, p_value = spearmanr(predictions, expected_ranks)
                vm = (1-vm)/2
                if (vm > 0.2): 
                    strong = True
                else:
                    strong = False

                result_entry = {
                    "questions": [q1,q2,q3,q4,q5],
                    "answers": [ans1,ans2,ans3,ans4,ans5],
                    "extracted_results": [v1,v2,v3,v4,v5],
                    "median": predictions,
                    "violation_metric": vm,
                    "strong": strong
                }
                all_results_data.append(result_entry)
                
        return all_results_data

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
    
    parser.add_argument("--times", 
                        type=int, 
                        default=3,
                        help="Le nombre de fois où chaque question est éxécutée.")
    
    parser.add_argument("--temperature", 
                        type=float, 
                        default=0.0, 
                        help="La température de sampling pour la génération (entre 0.0 et 1.0).")
    
    parser.add_argument("--output-name", 
                        type=str, 
                        default="no_name_exp", 
                        help="Le nom de base pour le fichier de sortie des résultats.")

    parser.add_argument("--system-prompt", 
                        choices=["short", "long"],
                        default="long", 
                        help="Demander au llm d'afficher son raisonnement dans sa réponse.")
    args = parser.parse_args()

    # Validation des arguments
    if not (0.0 <= args.temperature <= 1.0):
        print("Erreur: La température doit être entre 0.0 et 1.0.")
        sys.exit(1)

    print(f"\n--- Démarrage de l'expérience de Réplication ---")
    print(f"Type: {args.type.upper()}")
    print(f"Modèle: {args.model}")
    print(f"Température: {args.temperature}")
    print(f"Times: {args.times}")
    print("-" * 40)
    
    system_prompt = ""
    if args.system_prompt == "long" and args.type != "monotonic":
        system_prompt = "The user needs help on a few prediction market questions. You should always output a single best"+\
        "probability estimate, without any intervals. It is important that you do not output the probability outright."+\
        "Rather, you should consider multiple views, along with the intermediate estimates; and only then"+\
        "produce the final numerical answer in the last line, like this: [Answer] 0.5"
    
    elif args.system_prompt == "long" and args.type == "monotonic" :
        system_prompt = "The user needs help on a few prediction market questions. You should always output a single best"+\
        "numerical estimate, without any intervals. It is important you do not output the answer outright. Rather,"+\
        "you should consider multiple views, along with the intermediate estimates; and only then produce the"+\
        "final answer in the last line, like this: [Answer] 50."
    
    elif args.system_prompt == "short" and args.type != "monotonic" :
        system_prompt = "Always output a single best probability estimate for the requested probability, preceded by [Answer] followed by a space (e.g., [Answer] 0.50)."
    
    elif args.system_prompt == "short" and args.type == "monotonic" :
        system_prompt = "Always output a single best numerical estimate for the requested probability, preceded by [Answer] followed by a space (e.g., [Answer] 50)."
        
    
    if args.type == "negated_pair":
        all_questions: List[Tuple[str,str]] = extract_negated_questions("data/negated_pair_dataset_200_gpt-3.5-turbo-0301_method_1shot_china_T_0.0_times_3_mt_400.json")
        questions = random.sample(all_questions, 8)
        results = run_negated_pair_experiment(questions=questions, model_name=args.model, temperature=args.temperature, times=args.times,system_prompt=system_prompt)
        
    elif args.type == "bayes":
        all_questions = extract_bayes_questions("data/bayes_gpt-3.5-turbo-0301_method_1shot_china_T_0.0_times_3_mt_400.json")
        questions = random.sample(all_questions, 8)
        results = run_bayes_experiment(questions=questions, model_name=args.model, temperature=args.temperature, times=args.times,system_prompt=system_prompt)
        
    elif args.type == "paraphrase":
        all_questions = extract_paraphrase_questions("data/large_paraphrases_gpt-3.5-turbo-0301_method_1shot_china_T_0.0_times_3_mt_400.json")
        questions = random.sample(all_questions, 8)
        results = run_paraphrase_experiment(questions=questions, model_name=args.model, temperature=args.temperature, times=args.times, system_prompt=system_prompt)
    
    elif args.type == "monotonic":
        all_questions = extract_monotonic_questions("data/monotonic_sequence_gpt-3.5-turbo-0301_method_1shot_climbers_T_0.0_times_3_mt_400.json")
        questions = random.sample(all_questions, 8)
        results = run_monotonicity_experiment(questions=questions, model_name=args.model, temperature=args.temperature, times=args.times, system_prompt=system_prompt)


    output_filename = f"{args.output_name}_{args.type}_{args.model.replace('/','-')}_T_{args.temperature}_times_{args.times}_{args.system_prompt}.json"
    
    try:
        # Créer un répertoire de sortie si nécessaire
        os.makedirs("replication/results", exist_ok=True)
        output_path = os.path.join("replication/results", output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Expérience terminée. Résultats sauvegardés dans: {output_path}")
        print(f"Nombre de tests effectués: {len(results)}")
        
    except Exception as e:
        print(f"\nErreur lors de la sauvegarde des résultats : {e}")
        
if __name__ == "__main__":
    main()