
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.pyplot import figure

from hr_ranking_langchain.models.candidate import (
    CandidateInfo,
)
from hr_ranking_langchain.config import cfg

from pathlib import Path
import numpy as np

import time

from typing import List


def create_barchart(candidate_infos: List[CandidateInfo]) -> Path:
    x_axis = [ci.candidate_info_response.name for ci in candidate_infos]
    y_axis = [ci.score for ci in candidate_infos]
    fig = figure(figsize=(18, 10), dpi=80)
    fig.subplots_adjust(bottom=0.2)
    font = {"size": 22}

    matplotlib.rc("font", **font)
    plt.bar(x_axis, y_axis)
    plt.title("Candidate Ranking")
    plt.xlabel("Candidate name")
    plt.ylabel("Score")
    plt.xticks(rotation=25)

    time_millis = round(time.time() * 1000)

    ranking_plot = cfg.temp_doc_location / f"{time_millis}_ranking.png"
    plt.savefig(ranking_plot)
    return ranking_plot