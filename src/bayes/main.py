import sys
sys.path.append("..")
from gpt_interface import gpt_query
import json
import re
from typing import List, Tuple, Optional
import statistics
from math import sqrt
import random

def extract_bayes_questions(file: str) -> List[Tuple[str, str, str, str]]:
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
                    if len(question_list) >= 4:
                        p_a = question_list[0]
                        p_b = question_list[1]
                        p_ab = question_list[2]
                        p_ba = question_list[3]
                        question_pairs.append((p_a,p_b,p_ab,p_ba))
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
            "file": "../../data/bayes_gpt-3.5-turbo-0301_method_1shot_china_T_0.0_times_3_mt_400.json",
            "temperature": 0.0,
            "run": 3,
            "model": "gpt-3.5-turbo",
            "name": "negated_gpt-3.5_T-0.0"
            },
        {
            "file": "../../data/bayes_gpt-3.5-turbo-0301_method_1shot_china_T_0.5_times_6_mt_400.json",
            "temperature": 0.5,
            "run": 6,
            "model": "gpt-3.5-turbo",
            "name": "negated_gpt-3.5_T-0.5"
            },
        {
            "file": "../../data/bayes_gpt-4-0314_method_1shot_china_T_0.0_times_3_mt_400.json",
            "temperature": 0.0,
            "run": 3,
            "model": "gpt-4",
            "name": "negated_gpt-4_T-0.0"
            },
        {
            "file": "../../data/bayes_gpt-4-0314_method_1shot_china_T_0.5_times_6_mt_400.json",
            "temperature": 0.5,
            "run": 6,
            "model": "gpt-4",
            "name": "negated_gpt-4_T-0.5"
            },
        ]
    for e in data:
        all_questions: List[Tuple[str,str,str,str]] = extract_bayes_questions(e["file"])
        questions = random.sample(all_questions, 35) #cf README.md to understand why we extract 66 questions
        all_results_data = []
        for (q1,q2,q3,q4) in questions:
            v1=[]
            v2=[]
            v3=[]
            v4=[]
            strong=False
            ans1=[]
            ans2=[]
            ans3=[]
            ans4=[]
            for i in range(0,e["run"]):
                p_a = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q1, system_prompt=system_prompt)
                p_b = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q2, system_prompt=system_prompt)
                p_ab = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q3, system_prompt=system_prompt)
                p_ba = gpt_query(model_name=e["model"], temperature=e["temperature"], prompt=q4, system_prompt=system_prompt)
                ans1.append(p_a)
                ans2.append(p_b)
                ans3.append(p_ab)
                ans4.append(p_ba)
                r1=extract_result(answer=ans1)
                r2=extract_result(answer=ans2)
                r3=extract_result(answer=ans1)
                r4=extract_result(answer=ans2)
                if(r1 is not None): v1.append(r1)
                if(r2 is not None): v2.append(r2)
                if(r3 is not None): v3.append(r1)
                if(r4 is not None): v4.append(r2)
            
            if(len(v1)>0 & len(v2)>0 & len(v3)>0 & len(v4)>0):
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
            with open(f'../../results/bayes/output_{e["name"]}.json', 'w', encoding='utf-8') as f:
                json.dump(all_results_data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Erreur lors de l'écriture dans le fichier JSON : {e}")
        except Exception as e:
            print(f"Une erreur inattendue est survenue lors de l'écriture du JSON : {e}")
    