import sys
sys.path.append("..")
from gpt_interface import gpt_query
import json
from typing import List, Tuple, Optional
import statistics
from math import sqrt
import random
from scipy.stats import spearmanr

def extract_monotonic_questions(file: str) -> List[Tuple[str, str, str, str, str, str]]:
    """
    Extrait les paires de questions (affirmative et négative) 
    d'un fichier JSON.

    Args:
        file: Le chemin d'accès au fichier JSON d'entrée.

    Returns:
        Une liste de tuples, où chaque tuple contient 
    """
    
    question_pairs = []
    
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if 'questions' in item and isinstance(item['questions'], list):
                    question_list = item['questions']
                    if len(question_list) >= 5:
                        p_a = question_list[0]
                        p_b = question_list[1]
                        p_ab = question_list[2]
                        p_ba = question_list[3]
                        p = question_list[4]
                    else:
                        print(f"Avertissement : L'élément ne contient pas 5 questions : {item}")
                direction = item['direction']
                question_pairs.append((p_a,p_b,p_ab,p_ba,p,direction))

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file}' n'a pas été trouvé.")
        return []
    except json.JSONDecodeError:
        print(f"Erreur : Impossible de décoder le JSON du fichier '{file}'.")
        return []
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
        return []
            
    return question_pairs
     
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

def monotonicity():

    system_prompt = (
   "The user needs help on a few prediction market questions. You should always output a single best"
   "probability estimate, without any intervals. It is important that you do not output the probability outright."
   "Rather, you should consider multiple views, along with the intermediate estimates; and only then"
   "produce the final numerical answer in the last line, like this: [Answer] 0.5"
)
    data = [
        {
            "file": "data/monotonic_sequence_gpt-3.5-turbo-0301_method_1shot_climbers_T_0.0_times_3_mt_400.json",
            "temperature": 0.0,
            "run": 3,
            "model": "gpt-3.5-turbo",
            "name": "negated_gpt-3.5_T-0.0"
            },
        {
            "file": "../data/monotonic_sequence_gpt-3.5-turbo-0301_method_1shot_climbers_T_0.5_times_6_mt_400.json",
            "temperature": 0.5,
            "run": 6,
            "model": "gpt-3.5-turbo",
            "name": "negated_gpt-3.5_T-0.5"
            },
        {
            "file": "data/monotonic_sequence_gpt-4-0314_method_1shot_climbers_T_0.0_times_3_mt_400.json",
            "temperature": 0.0,
            "run": 3,
            "model": "gpt-4",
            "name": "negated_gpt-4_T-0.0"
            },
        {
            "file": "data/monotonic_sequence_gpt-4-0314_method_1shot_climbers_T_0.5_times_6_mt_400.json",
            "temperature": 0.5,
            "run": 6,
            "model": "gpt-4",
            "name": "negated_gpt-4_T-0.5"
            },
        ]
    print(sys.path)
    for e in data:
        all_questions: List[Tuple[str,str,str,str,str,str]] = extract_monotonic_questions(e["file"])
                
        questions = random.sample(all_questions, 1)
        k=0
        all_results_data = []
        
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
            
            for i in range(0,e["run"]):
                p_a = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q1, system_prompt=system_prompt)
                p_b = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q2, system_prompt=system_prompt)
                p_ab = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q3, system_prompt=system_prompt)
                p_ba = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q4, system_prompt=system_prompt)
                p = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q5, system_prompt=system_prompt)
                
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
                    expected_ranks = [1, 2, 3, 4, 5]
                elif d == 'decreasing':
                    expected_ranks = [5, 4, 3, 2, 1]
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

        try: 
            with open(f'reproducibility/results/monotonic_sequence/output_{e["name"]}.json', 'w', encoding='utf-8') as f:
                json.dump(all_results_data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de l'écriture dans le fichier JSON : {e}")
        except Exception as e:
            print(f"Une erreur inattendue est survenue lors de l'écriture du JSON : {e}")