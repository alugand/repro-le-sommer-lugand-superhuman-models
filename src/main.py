from gpt_interface import gpt_query
import json
import re
from typing import List, Tuple, Optional
import statistics

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
            # Charger l'intégralité du fichier JSON, qui est une liste
            data = json.load(f)
            
            # Itérer sur chaque objet (dictionnaire) dans la liste
            for item in data:
                # Vérifier si la clé "questions" existe et est une liste
                if 'questions' in item and isinstance(item['questions'], list):
                    question_list = item['questions']
                    
                    # S'assurer qu'il y a bien deux questions à extraire
                    if len(question_list) >= 2:
                        question = question_list[0]
                        question_negated = question_list[1]
                        
                        # Ajouter le tuple à notre liste de résultats
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
    
    # Utilise split pour séparer la chaîne au niveau de la balise "[Answer]"
    # rsplit(maxsplit=1) est plus efficace car il ne cherche 
    # que la dernière occurrence.
    parts = answer.rsplit("[Answer]", 1)
    
    # Si la balise n'a pas été trouvée, la liste n'aura qu'un seul élément
    if len(parts) < 2:
        return None
        
    # Le nombre est dans la dernière partie
    result_str = parts[-1]
    
    # Nettoyer les espaces blancs potentiels
    result_str = result_str.strip()
    
    # Essayer de convertir la chaîne nettoyée en float
    try:
        return float(result_str)
    except ValueError:
        # C'était bien du texte après la balise, mais ce n'était pas un nombre
        return None
if __name__ == "__main__":

    MONOTONICITY_SYSTEM_PROMPT = (
    "The user needs help on a few prediction market questions. You should always output a single best"
    "numerical estimate, without any intervals. It is important you do not output the answer outright. Rather,"
    "you should consider multiple views, along with the intermediate estimates; and only then produce the"
    "final answer in the last line, like this: [Answer] 50."
    )
    questions: List[Tuple[str,str]] = extract_negated_questions("../data/negated_pair_dataset_200_gpt-3.5-turbo-0301_method_1shot_china_T_0.0_times_3_mt_400.json")
    violation=[]
    strong=0
    j=0
    for (q,qn) in questions:
        value=[]
        negated=[]
        print(q)
        print(qn)
        for i in range(0,3):
            answer = gpt_query(model_name="gpt-3.5-turbo", temperature=0.0, prompt=q)
            answer_negated = gpt_query(model_name="gpt-3.5-turbo", temperature=0.0, prompt=qn)
            print(answer)
            print(answer_negated)
            r=extract_result(answer=answer)
            rn=extract_result(answer=answer_negated)
            print(r)
            print(rn)
            if(r is not None): value.append(r)
            if(rn is not None): negated.append(rn)
        mn = statistics.median(negated)
        m = statistics.median(value)
        vm=abs(m-1+mn)
        violation.append(vm)
        if (vm>0.2): strong+=1
        j+=1
        if(j>2): break
    print(f"Mean violation for gpt-3.5-turbo : {statistics.mean(violation)}")
    print(f"Strong violation for gpt-3.5-turbo : {100*strong/len(violation)}%")

