"""Configurações globais do projeto (caminhos, temporadas, seed)."""
from pathlib import Path
import random

import numpy as np

SEED = 42

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"

for _p in (RAW, PROCESSED, FIGURES, RESULTS):
    _p.mkdir(parents=True, exist_ok=True)


def season_str(start_year: int) -> str:
    """2010 -> '2010-11'."""
    return f"{start_year}-{str(start_year + 1)[-2:]}"


HIST_SEASONS = [season_str(y) for y in range(2010, 2026)]  # 2010-11 .. 2025-26
CURRENT_SEASON = season_str(2026)                          # 2026-27
ALL_SEASONS = HIST_SEASONS + [CURRENT_SEASON]

# Times atuais (abreviação da NBA) -> conferência.
# Franquias que mudaram de sigla no período (NJN->BKN, NOH->NOP, CHA/CHA)
# são normalizadas em coleta.normalize_abbr.
CONFERENCE = {
    # Leste
    "ATL": "Leste", "BOS": "Leste", "BKN": "Leste", "CHA": "Leste", "CHI": "Leste",
    "CLE": "Leste", "DET": "Leste", "IND": "Leste", "MIA": "Leste", "MIL": "Leste",
    "NYK": "Leste", "ORL": "Leste", "PHI": "Leste", "TOR": "Leste", "WAS": "Leste",
    # Oeste
    "DAL": "Oeste", "DEN": "Oeste", "GSW": "Oeste", "HOU": "Oeste", "LAC": "Oeste",
    "LAL": "Oeste", "MEM": "Oeste", "MIN": "Oeste", "NOP": "Oeste", "OKC": "Oeste",
    "PHX": "Oeste", "POR": "Oeste", "SAC": "Oeste", "SAS": "Oeste", "UTA": "Oeste",
}


def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)


set_seed()
