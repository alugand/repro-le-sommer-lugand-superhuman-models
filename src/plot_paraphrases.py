from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
from highlight_text import HighlightText
import matplotlib.axes


def auto_wrap_sentence(sentence: str, line_length_max: int) -> str:
    """
    Automatically wrap a sentence to a maximum line length.
    """
    words = sentence.split(" ")
    words_clean = [w.replace("\u0336", "") for w in words]
    words_clean = [w.replace("<", "") for w in words_clean]
    words_clean = [w.replace(">", "") for w in words_clean]
    lines_clean = []
    lines = []
    line = ""
    line_clean = ""
    for index, word in enumerate(words_clean):
        if len(line_clean) + len(word) > line_length_max:
            lines_clean.append(line_clean[:-1])
            lines.append(line[:-1])
            line_clean = ""
            line = ""
        line_clean += word + " "
        line += words[index] + " "
    lines_clean.append(line_clean[:-1])
    lines.append(line[:-1])
    return "\n".join(lines)


def get_levenshtein_sentence_distance_edits(string1, string2) -> List[str]:
    # Only consider additions and deletions
    distance_dict: Dict[Tuple(int, int), int] = {}

    sentence1 = string1.split(" ")
    sentence2 = string2.split(" ")

    # Add the base cases
    for i in range(len(sentence1) + 1):
        distance_dict[(i, 0)] = i

    for j in range(len(sentence2) + 1):
        distance_dict[(0, j)] = j

    # Fill the rest of the table
    for i in range(1, len(sentence1) + 1):
        for j in range(1, len(sentence2) + 1):
            if sentence1[i - 1] == sentence2[j - 1]:
                distance_dict[(i, j)] = distance_dict[(i - 1, j - 1)]
            else:
                distance_dict[(i, j)] = min(
                    distance_dict[(i - 1, j)] + 1,
                    distance_dict[(i, j - 1)] + 1,
                )

    # Get a list of the edits
    edits = []
    i, j = len(sentence1), len(sentence2)
    while i > 0 or j > 0:
        if i == 0:
            edits.append("+")
            j -= 1
        elif j == 0:
            edits.append("-")
            i -= 1
        elif sentence1[i - 1] == sentence2[j - 1]:
            edits.append("0")
            i -= 1
            j -= 1
        elif distance_dict[(i - 1, j)] <= distance_dict[(i, j - 1)]:
            edits.append("-")
            i -= 1
        else:
            edits.append("+")
            j -= 1

    return edits[::-1]


def create_text_object(
    sentence: str, bboxes: List[Dict[str, Any]], ax: matplotlib.axes.Axes, **kwargs
):
    custom_gray = "#969696"
    default_args = {
        "x": 0.5,
        "y": 0.5,
        "fontsize": 16,
        "ha": "center",
        "va": "center",
        "s": sentence,
        "highlight_textprops": bboxes,
        "annotationbbox_kw": {
            "frameon": True,
            "pad": 2,
            "bboxprops": {"facecolor": "white", "edgecolor": custom_gray, "linewidth": 5},
        },
        "ax": ax,
    }
    arguments = {**default_args, **kwargs}
    HighlightText(**arguments)


def plot_paraphrases(
    sentence1: str,
    sentence2: str,
    save_plot: bool = False,
    save_path: Optional[str] = None,
    show_plot: bool = True,
):
    if save_plot and save_path is None:
        raise ValueError("If save_plot is True, save_path must be provided.")

    # Get the edit history required to transform sentence1 into sentence2
    edits = get_levenshtein_sentence_distance_edits(sentence1, sentence2)

    sentence1_parts = sentence1.split(" ")
    sentence2_parts = sentence2.split(" ")

    # Build a new sentence by adding deletions with strike-through font and additions with underline font
    new_sentence = []
    bboxes = []
    custom_green = "#a3dc8b"
    custom_red = "#f86060"
    insertion_bbox = {
        "bbox": {"edgecolor": custom_green, "facecolor": custom_green, "linewidth": 1.5, "pad": 1}
    }
    deletion_bbox = {
        "bbox": {"edgecolor": custom_red, "facecolor": custom_red, "linewidth": 1.5, "pad": 1}
    }
    i, j = 0, 0
    for edit in edits:
        if edit == "0":
            new_sentence += [sentence1_parts[i]]
            i += 1
            j += 1
        elif edit == "-":
            word_strike_through = "".join(l + "\u0336" for l in sentence1_parts[i])
            new_sentence += [f"<{word_strike_through}>"]
            bboxes.append(dict(deletion_bbox))
            i += 1
        else:
            new_sentence += [f"<{sentence2_parts[j]}>"]
            bboxes.append(dict(insertion_bbox))
            j += 1

    new_sentence = " ".join(new_sentence)
    formatted_sentence = auto_wrap_sentence(sentence1, line_length_max=60)
    formatted_new_sentence = auto_wrap_sentence(new_sentence, line_length_max=45)

    fig, ax = plt.subplots(figsize=(4, 4))
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    ax.axis("off")

    # Create the original sentence text object
    create_text_object(formatted_sentence, [], ax, x=0.25, y=0.5, fontsize=22)

    # Create the new sentence text object
    if save_plot:
        x_pos_second_plot = 4.5
    else:
        x_pos_second_plot = 0.75
    create_text_object(formatted_new_sentence, bboxes, ax, x=x_pos_second_plot, y=0.5, fontsize=22)

    plt.tight_layout()

    if show_plot:
        plt.show()

    if save_plot:
        plt.savefig(save_path, bbox_inches="tight", dpi=300)

    plt.close()


if __name__ == "__main__":


    plot_paraphrases(sentence1, sentence2)
