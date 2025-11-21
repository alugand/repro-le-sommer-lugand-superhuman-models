import sys
import os
sys.path.append("..") 
from gpt_interface import gpt_query
import json
import re
from typing import List, Dict, Any
import statistics
import random

def extract_paraphrase_questions(file: str) -> List[List[str]]:
    """
    Extrait les groupes de questions paraphrasées 
    d'un fichier JSON.

    Args:
        file: Le chemin d'accès au fichier JSON d'entrée.

    Returns:
        Une liste de listes, où chaque liste interne contient 
        un groupe de questions paraphrasées (par ex. 4 questions).
    """
    
    question_groups = []
    
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if 'questions' in item and isinstance(item['questions'], list) and len(item['questions']) > 1:
                    question_groups.append(item['questions'])
                else:
                    print(f"Avertissement : L'élément ne contient pas un groupe de questions valide : {item}")

    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file}' n'a pas été trouvé.")
        return []
    except json.JSONDecodeError:
        print(f"Erreur : Impossible de décoder le JSON du fichier '{file}'.")
        return []
    except Exception as e:
        print(f"Une erreur inattendue est survenue : {e}")
        return []
            
    return question_groups
     
def extract_result(answer: str) -> Dict[str, Any]:
    """
    Extrait le nombre (float ou int) qui suit la balise "[Answer]"
    dans une chaîne de caractères et renvoie un dictionnaire
    indiquant si l'extraction a réussi.

    Args:
        answer: La chaîne de caractères d'entrée contenant la réponse
                et la balise [Answer].

    Returns:
        Optional[float]
    """
    parts = answer.rsplit("[Answer]", 1)
    
    if len(parts) < 2:
        return None
        
    result_str = parts[-1].strip()
    match = re.search(r"^[0-9\.]+", result_str)
    
    if match:
        try:
            return float(match.group(0))
        except ValueError:
            return None
    else:
        return None

def paraphrasing():

    system_prompt = (
   "The user needs help on a few prediction market questions. You should always output a single best"
   "probability estimate, without any intervals. It is important that you do not output the probability outright."
   "Rather, you should consider multiple views, along with the intermediate estimates; and only then"
   "produce the final numerical answer in the last line, like this: [Answer] 0.5"
)

    data = [
        {
            "file": "data/large_paraphrases_gpt-3.5-turbo-0301_method_1shot_china_T_0.0_times_3_mt_400.json",
            "temperature": 0.0,
            "run": 3,
            "model": "gpt-3.5-turbo",
            "name": "paraphrase_gpt-3.5_T-0.0"
            },
        {
            "file": "data/large_paraphrases_gpt-3.5-turbo-0301_method_1shot_china_T_0.5_times_6_mt_400.json",
            "temperature": 0.5,
            "run": 6,
            "model": "gpt-3.5-turbo",
            "name": "paraphrase_gpt-3.5_T-0.5"
            },
        {
            "file": "data/large_paraphrases_gpt-4-0314_method_1shot_china_T_0.0_times_3_mt_400.json",
            "temperature": 0.0,
            "run": 3,
            "model": "gpt-4",
            "name": "paraphrase_gpt-4_T-0.0"
            },
        {
            "file": "data/large_paraphrases_gpt-4-0314_method_1shot_china_T_0.5_times_6_mt_400.json",
            "temperature": 0.5,
            "run": 6,
            "model": "gpt-4",
            "name": "paraphrase_gpt-4_T-0.5"
            },

        ]
        
    output_dir = "reproducibility/results/paraphrases"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for e in data:
        all_question_groups: List[List[str]] = extract_paraphrase_questions(e["file"])
        questions = random.sample(all_question_groups, 5)

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
                
                for i in range(0, e["run"]):
                    raw_answer = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q, system_prompt=system_prompt)
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
        try: 
            output_path = os.path.join(output_dir, f"output_{e['name']}.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_results_data, f, indent=4, ensure_ascii=False)
        except IOError as ioe:
            print(f"Erreur lors de l'écriture dans le fichier JSON : {ioe}")
        except Exception as ex:
            print(f"Une erreur inattendue est survenue lors de l'écriture du JSON : {ex}")