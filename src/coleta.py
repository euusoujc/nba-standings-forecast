"""Fase 1 - Coleta de dados via nba_api.

- LeagueGameLog (nível de time) para 2010-11 .. 2026-27, com cache em data/raw
- ScheduleLeagueV2 para os jogos restantes de 2026-27
- Mapeamento time -> conferência

Uso: python src/coleta.py [--refresh-current]
"""
from __future__ import annotations

import sys
import time

import pandas as pd

try:
    from config import RAW, ALL_SEASONS, CURRENT_SEASON, CONFERENCE
except ImportError:  # importado como pacote (src.coleta)
    from src.config import RAW, ALL_SEASONS, CURRENT_SEASON, CONFERENCE

SLEEP = 1.0
MAX_RETRIES = 5
TIMEOUT = 60

# Siglas antigas -> sigla atual da franquia
ABBR_MAP = {"NJN": "BKN", "NOH": "NOP", "NOK": "NOP", "CHH": "CHA", "SEA": "OKC"}

KEEP_COLS = ["SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION", "TEAM_NAME", "GAME_ID",
             "GAME_DATE", "MATCHUP", "WL", "PTS", "PLUS_MINUS",
             "FGA", "FTA", "OREB", "TOV"]


def normalize_abbr(a: str) -> str:
    return ABBR_MAP.get(a, a)


def _with_retry(fn, desc: str):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            out = fn()
            time.sleep(SLEEP)
            return out
        except Exception as e:  # timeouts, conexões recusadas, JSON vazio...
            wait = SLEEP * 2 ** attempt
            print(f"  [{desc}] tentativa {attempt}/{MAX_RETRIES} falhou: {type(e).__name__}: {e}. "
                  f"Nova tentativa em {wait:.0f}s")
            time.sleep(wait)
    raise RuntimeError(f"Falha ao baixar {desc} após {MAX_RETRIES} tentativas")


def fetch_season(season: str, refresh: bool = False) -> pd.DataFrame:
    """Baixa (ou lê do cache) o game log de times da temporada regular."""
    path = RAW / f"gamelog_{season}.csv"
    if path.exists() and not refresh:
        return pd.read_csv(path, dtype={"GAME_ID": str})

    from nba_api.stats.endpoints import leaguegamelog

    def _call():
        return leaguegamelog.LeagueGameLog(
            season=season, player_or_team_abbreviation="T",
            season_type_all_star="Regular Season", timeout=TIMEOUT,
        ).get_data_frames()[0]

    print(f"Baixando {season}...")
    df = _with_retry(_call, season)
    df = df[[c for c in KEEP_COLS if c in df.columns]].copy()
    df.to_csv(path, index=False)
    return df


def fetch_schedule(season: str = CURRENT_SEASON, refresh: bool = False) -> pd.DataFrame:
    """Jogos de temporada regular ainda não disputados (ScheduleLeagueV2)."""
    path = RAW / f"schedule_{season}.csv"
    if path.exists() and not refresh:
        return pd.read_csv(path, dtype={"GAME_ID": str})

    from nba_api.stats.endpoints import scheduleleaguev2

    def _call():
        return scheduleleaguev2.ScheduleLeagueV2(
            season=season, league_id="00", timeout=TIMEOUT).get_data_frames()[0]

    print(f"Baixando calendário {season}...")
    raw = _with_retry(_call, f"schedule {season}")
    sched = pd.DataFrame({
        "GAME_ID": raw["gameId"].astype(str),
        "GAME_DATE": pd.to_datetime(raw["gameDate"], format="%m/%d/%Y %H:%M:%S").dt.date,
        "STATUS": raw["gameStatus"],
        "HOME": raw["homeTeam_teamTricode"],
        "AWAY": raw["awayTeam_teamTricode"],
    })
    sched.to_csv(path, index=False)
    return sched


def load_all(refresh_current: bool = False) -> pd.DataFrame:
    """Concatena todas as temporadas num único DataFrame (uma linha por time-jogo)."""
    frames = []
    for s in ALL_SEASONS:
        df = fetch_season(s, refresh=refresh_current and s == CURRENT_SEASON)
        df["SEASON"] = s
        frames.append(df)
    games = pd.concat(frames, ignore_index=True)
    games["GAME_ID"] = games["GAME_ID"].astype(str).str.zfill(10)
    games["TEAM"] = games["TEAM_ABBREVIATION"].map(normalize_abbr)
    games["GAME_DATE"] = pd.to_datetime(games["GAME_DATE"])
    games["HOME"] = games["MATCHUP"].str.contains("vs.").astype(int)
    games["WIN"] = (games["WL"] == "W").astype(int)
    games["CONF"] = games["TEAM"].map(CONFERENCE)
    # Adversário e pontos sofridos: juntando as duas linhas do mesmo jogo
    opp = games[["GAME_ID", "TEAM", "PTS", "FGA", "FTA", "OREB", "TOV"]].rename(
        columns={"TEAM": "OPP", "PTS": "OPP_PTS", "FGA": "OPP_FGA", "FTA": "OPP_FTA",
                 "OREB": "OPP_OREB", "TOV": "OPP_TOV"})
    games = games.merge(opp, on="GAME_ID")
    games = games[games["TEAM"] != games["OPP"]].reset_index(drop=True)
    return games.sort_values(["SEASON", "TEAM", "GAME_DATE", "GAME_ID"]).reset_index(drop=True)


def remaining_games(sched: pd.DataFrame, played: pd.DataFrame) -> pd.DataFrame:
    """Jogos de temporada regular (GAME_ID '002...') que ainda não aparecem no game log."""
    s = sched.copy()
    s["GAME_ID"] = s["GAME_ID"].astype(str).str.zfill(10)
    s = s[s["GAME_ID"].str.startswith("002")]
    s = s[~s["GAME_ID"].isin(set(played["GAME_ID"]))]
    s = s[s["HOME"].isin(CONFERENCE) & s["AWAY"].isin(CONFERENCE)]
    return s.reset_index(drop=True)


def main():
    refresh = "--refresh-current" in sys.argv
    games = load_all(refresh_current=refresh)
    sched = fetch_schedule(refresh=refresh)
    cur = games[games["SEASON"] == CURRENT_SEASON]
    rem = remaining_games(sched, cur)
    games.to_csv(RAW.parent / "processed" / "games.csv", index=False)
    rem.to_csv(RAW.parent / "processed" / "remaining_2026-27.csv", index=False)

    print("\n=== Resumo da coleta ===")
    print("Linhas time-jogo:", games.shape)
    print(games.groupby("SEASON")["GAME_ID"].nunique().rename("jogos").to_string())
    print("Times sem conferência:", sorted(set(games["TEAM"]) - set(CONFERENCE)) or "nenhum")
    gp = cur.groupby("TEAM").size()
    rem_ct = pd.concat([rem["HOME"], rem["AWAY"]]).value_counts()
    tot = (gp + rem_ct.reindex(gp.index).fillna(0)).astype(int)
    print(f"2026-27: jogos disputados por time min={gp.min()} max={gp.max()}; "
          f"restantes no calendário: {len(rem)} jogos")
    print("Disputados + restantes por time:", tot.value_counts().to_dict())


if __name__ == "__main__":
    main()
