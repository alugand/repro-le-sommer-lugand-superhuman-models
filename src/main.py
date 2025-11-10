from gpt_interface import gpt_query

if __name__ == "__main__":

    MONOTONICITY_SYSTEM_PROMPT = (
   "The user needs help on a few prediction market questions. You should always output a single best"
    "numerical estimate, without any intervals. It is important you do not output the answer outright. Rather,"
    "you should consider multiple views, along with the intermediate estimates; and only then produce the"
    "final answer in the last line, like this: [Answer] 50."
    )
    plot_paraphrases(sentence1, sentence2)
