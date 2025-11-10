import sys
sys.path.append("..")
from gpt_interface import gpt_query
import json
import re
from typing import List, Tuple, Optional
import statistics
import random

def extract_negated_questions(file: str) -> List[Tuple[str, str]]:
    """
    Extrait les paires de questions (affirmative et négative) 
    d'un fichier JSON.

    Args:
        file: Le chemin d'accès au fichier JSON d'entrée.

    Returns:
        Une liste de tuples, où chaque tuple contient 
        (question, question_negated).
    """
    
    question_pairs = []
    
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if 'questions' in item and isinstance(item['questions'], list):
                    question_list = item['questions']
                    if len(question_list) >= 2:
                        question = question_list[0]
                        question_negated = question_list[1]
                        question_pairs.append((question, question_negated))
                    else:
                        print(f"Avertissement : L'élément ne contient pas 2 questions : {item}")
                else:
                    print(f"Avertissement : Format d'élément inattendu ignoré : {item}")

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
    try:
        return float(result_str)
    except ValueError:
        return None

if __name__ == "__main__":

    system_prompt = (
   "The user needs help on a few prediction market questions. You should always output a single best"
   "probability estimate, without any intervals. It is important that you do not output the probability outright."
   "Rather, you should consider multiple views, along with the intermediate estimates; and only then"
   "produce the final numerical answer in the last line, like this: [Answer] 0.5"
)
    data = [
        {
            "file": "../../data/negated_pair_dataset_200_gpt-3.5-turbo-0301_method_1shot_china_T_0.0_times_3_mt_400.json",
            "temperature": 0.0,
            "run": 3,
            "model": "gpt-3.5-turbo",
            "name": "negated_gpt-3.5_T-0.0"
            },
        {
            "file": "../../data/negated_pair_dataset_200_gpt-3.5-turbo-0301_method_1shot_china_T_0.5_times_6_mt_400.json",
            "temperature": 0.5,
            "run": 6,
            "model": "gpt-3.5-turbo",
            "name": "negated_gpt-3.5_T-0.5"
            },
        {
            "file": "../../data/negated_pair_dataset_200_gpt-4-0314_method_1shot_china_T_0.0_times_3_mt_400.json",
            "temperature": 0.0,
            "run": 3,
            "model": "gpt-4",
            "name": "negated_gpt-4_T-0.0"
            },
        {
            "file": "../../data/negated_pair_dataset_200_gpt-4-0314_method_1shot_china_T_0.5_times_6_mt_400.json",
            "temperature": 0.5,
            "run": 6,
            "model": "gpt-4",
            "name": "negated_gpt-4_T-0.5"
            },
        ]
    for e in data:
        all_questions: List[Tuple[str,str]] = extract_negated_questions(e["file"])
        questions = random.sample(all_questions, 66) #cf README.md to understand why we extract 66 questions
        all_results_data = []
        for (q,qn) in questions:
            value=[]
            negated=[]
            strong=False
            ans=[]
            ansn=[]
            for i in range(0,e["run"]):
                answer = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q, system_prompt=system_prompt)
                answer_negated = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=qn, system_prompt=system_prompt)
                ans.append(answer)
                ansn.append(answer_negated)
                r=extract_result(answer=answer)
                rn=extract_result(answer=answer_negated)
                if(r is not None): value.append(r)
                if(rn is not None): negated.append(rn)
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

        try: 
            with open(f'../../results/negated_pairs/output_{e["name"]}.json', 'w', encoding='utf-8') as f:
                json.dump(all_results_data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de l'écriture dans le fichier JSON : {e}")
        except Exception as e:
            print(f"Une erreur inattendue est survenue lors de l'écriture du JSON : {e}")
    