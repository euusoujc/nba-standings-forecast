"""Fase 2 - Features usando só os N primeiros jogos de cada time.

N = menor número de jogos disputados por um time em 2026-27 hoje.
Nada é calculado com informação posterior ao N-ésimo jogo do time
(exceto o alvo, que é o aproveitamento final da temporada).

Uso: python src/features.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd

try:
    from config import PROCESSED, CURRENT_SEASON, HIST_SEASONS, CONFERENCE
    from coleta import load_all, fetch_season, normalize_abbr
except ImportError:
    from src.config import PROCESSED, CURRENT_SEASON, HIST_SEASONS, CONFERENCE
    from src.coleta import load_all, fetch_season, normalize_abbr

PYTH_EXP = 14
FEATURES = ["win_pct", "pd_pg", "net_rtg", "pyth", "sos", "prev_win_pct"]


def current_n(games: pd.DataFrame) -> int:
    cur = games[games["SEASON"] == CURRENT_SEASON]
    return int(cur.groupby("TEAM").size().min())


def _possessions(fga, fta, oreb, tov):
    return fga + 0.44 * fta - oreb + tov


def _prev_season_pct(games: pd.DataFrame) -> pd.DataFrame:
    """Aproveitamento final da temporada anterior (inclui 2009-10 para 2010-11)."""
    final = games.groupby(["SEASON", "TEAM"])["WIN"].mean().rename("final").reset_index()
    pre = fetch_season("2009-10")
    pre["TEAM"] = pre["TEAM_ABBREVIATION"].map(normalize_abbr)
    pre_final = (pre.assign(WIN=(pre["WL"] == "W").astype(int))
                 .groupby("TEAM")["WIN"].mean().rename("final").reset_index())
    pre_final["SEASON"] = "2009-10"
    final = pd.concat([pre_final, final], ignore_index=True)
    final["NEXT"] = final["SEASON"].map(lambda s: f"{int(s[:4]) + 1}-{str(int(s[:4]) + 2)[-2:]}")
    return final.rename(columns={"final": "prev_win_pct"})[["NEXT", "TEAM", "prev_win_pct"]] \
                .rename(columns={"NEXT": "SEASON"})


def build_features(games: pd.DataFrame, n: int) -> pd.DataFrame:
    g = games.sort_values(["SEASON", "TEAM", "GAME_DATE", "GAME_ID"]).copy()
    g["k"] = g.groupby(["SEASON", "TEAM"]).cumcount() + 1  # índice do jogo do time
    first = g[g["k"] <= n].copy()

    # Data de corte de cada time-temporada: data do N-ésimo jogo
    cutoff = first.groupby(["SEASON", "TEAM"])["GAME_DATE"].max().rename("cutoff")

    first["poss"] = 0.5 * (_possessions(first.FGA, first.FTA, first.OREB, first.TOV)
                           + _possessions(first.OPP_FGA, first.OPP_FTA, first.OPP_OREB, first.OPP_TOV))
    agg = first.groupby(["SEASON", "TEAM"]).agg(
        gp=("WIN", "size"), wins=("WIN", "sum"),
        pf=("PTS", "sum"), pa=("OPP_PTS", "sum"), poss=("poss", "sum"))
    agg["win_pct"] = agg.wins / agg.gp
    agg["pd_pg"] = (agg.pf - agg.pa) / agg.gp
    agg["net_rtg"] = 100 * (agg.pf - agg.pa) / agg.poss
    # PF^14/(PF^14+PA^14) escrito como 1/(1+(PA/PF)^14) para evitar overflow
    agg["pyth"] = 1.0 / (1.0 + (agg.pa.astype(float) / agg.pf.astype(float)) ** PYTH_EXP)

    # Força de tabela: aproveitamento dos adversários em jogos até a data de corte
    # do time (sem contar os jogos contra o próprio time, para não ficar circular).
    sos_rows = []
    for (season, team), grp in first.groupby(["SEASON", "TEAM"]):
        cd = cutoff.loc[(season, team)]
        pool = g[(g.SEASON == season) & (g.GAME_DATE <= cd) & (g.OPP != team)]
        rec = pool.groupby("TEAM")["WIN"].agg(["sum", "size"])
        opps = grp["OPP"]
        w = rec.reindex(opps)["sum"].sum()
        t = rec.reindex(opps)["size"].sum()
        sos_rows.append((season, team, w / t if t else 0.5))
    sos = pd.DataFrame(sos_rows, columns=["SEASON", "TEAM", "sos"]).set_index(["SEASON", "TEAM"])

    feats = agg.join(sos).join(cutoff).reset_index()
    feats = feats.merge(_prev_season_pct(games), on=["SEASON", "TEAM"], how="left")

    # Alvo: aproveitamento final (só para temporadas encerradas)
    final = games.groupby(["SEASON", "TEAM"]).agg(final_gp=("WIN", "size"),
                                                  final_win_pct=("WIN", "mean")).reset_index()
    feats = feats.merge(final, on=["SEASON", "TEAM"], how="left")
    feats.loc[feats.SEASON == CURRENT_SEASON, ["final_win_pct"]] = np.nan
    feats["CONF"] = feats["TEAM"].map(CONFERENCE)
    return feats


def main():
    games = load_all()
    n = current_n(games)
    feats = build_features(games, n)
    hist = feats[feats.SEASON.isin(HIST_SEASONS)].reset_index(drop=True)
    cur = feats[feats.SEASON == CURRENT_SEASON].reset_index(drop=True)
    hist.to_csv(PROCESSED / "features_hist.csv", index=False)
    cur.to_csv(PROCESSED / "features_2026-27.csv", index=False)

    print(f"N = {n} jogos")
    print("Histórico:", hist.shape, "| Atual:", cur.shape)
    print("NaN por coluna (hist):", hist[FEATURES + ["final_win_pct"]].isna().sum().to_dict())
    assert (hist.gp == n).all() and (cur.gp == n).all(), "time com menos de N jogos!"
    print("\nCorrelação com o aproveitamento final (histórico):")
    print(hist[FEATURES + ["final_win_pct"]].corr()["final_win_pct"].round(3).to_string())
    print("\nDesvio-padrão: win_pct após N jogos = %.3f | final = %.3f"
          % (hist.win_pct.std(), hist.final_win_pct.std()))
    print("\n2026-27 (top 5 por win_pct):")
    print(cur.sort_values("win_pct", ascending=False)[["TEAM", "CONF"] + FEATURES].head().round(3).to_string(index=False))


if __name__ == "__main__":
    main()
