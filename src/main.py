from negated_pairs.main import negated_pairs
from bayes.main import bayes
from monotonicity.main import monotonicity
from paraphrasing.main import paraphrasing

if __name__=="__main__":
    print("début des expériences de reproductibilité")
    print("-------------")
    print("negated_pairs")
    negated_pairs()
    print("-------------")
    print("bayes")
    bayes()
    print("-------------")
    print("monotonicity")
    monotonicity()
    print("-------------")
    print("paraphrasing")
    paraphrasing()
    print("fin des expériences de reproductibilité")