#!/usr/bin/env python3
# Validar URLs
import sys
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
"""
Valida URLs en data/ofertas.csv.
- Comprueba status HTTP de cada URL.
- Si URL inválida, intenta encontrar reemplazo buscando en Bing por título (site:indeed.com "titulo").
- Si encuentra reemplazo válido, lo sustituye; si no, marca el registro como 'simulated' y limpia la URL.
- Guarda backup antes de sobrescribir el CSV.
"""
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import quote_plus
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "data" / "ofertas.csv"
BACKUP_PATH = BASE / "data" / f"ofertas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
TIMEOUT = 10
SLEEP = 1


def check_url(url: str) -> int:
    try:
        if not url or not str(url).strip():
            return 0
        # Hacer HEAD primero
        resp = requests.head(url, headers=HEADERS, allow_redirects=True, timeout=TIMEOUT)
        return resp.status_code
    except Exception:
        try:
            resp = requests.get(url, headers=HEADERS, allow_redirects=True, timeout=TIMEOUT)
            return resp.status_code
        except Exception:
            return 0


def search_bing_for_indeed(title: str, limit: int = 5) -> list:
    """Busca en Bing resultados que contengan indeed.com y devuelva URLs candidatas"""
    q = quote_plus(f"site:indeed.com {title}")
    url = f"https://www.bing.com/search?q={q}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'indeed.com' in href and ('/viewjob' in href or '/jobs' in href):
                # limpiar parámetros
                links.append(href.split('?')[0] if '?' in href else href)
                if len(links) >= limit:
                    break
        return links
    except Exception:
        return []


def main():
    if not CSV_PATH.exists():
        print(f"CSV no encontrado en {CSV_PATH}")
        return

    df = pd.read_csv(CSV_PATH)
    df_backup = df.copy()
    df_backup.to_csv(BACKUP_PATH, index=False)
    print(f"Backup guardado en: {BACKUP_PATH}")

    # Asegurar columnas de control
    if 'simulated' not in df.columns:
        df['simulated'] = False
    if 'note' not in df.columns:
        df['note'] = ''

    total = len(df)
    fixed = 0
    invalid = 0

    for idx, row in df.iterrows():
        url = row.get('url', '')
        title = row.get('titulo', '')

        status = check_url(url)
        print(f"[{idx+1}/{total}] Evaluando URL: {url} -> status {status}")

        if status == 200:
            # URL válida
            continue

        # URL inválida o no responde
        print(f"  -> URL inválida. Intentando buscar reemplazo en Bing por título: {title}")
        candidates = search_bing_for_indeed(title)
        time.sleep(SLEEP)

        replaced = False
        for cand in candidates:
            st = check_url(cand)
            print(f"    - candidato: {cand} status {st}")
            if st == 200:
                df.at[idx, 'url'] = cand
                df.at[idx, 'note'] = 'replaced_via_bing'
                replaced = True
                fixed += 1
                break
            time.sleep(0.5)

        if not replaced:
            # No se encontró reemplazo; marcar como simulado y limpiar url
            df.at[idx, 'simulated'] = True
            df.at[idx, 'note'] = 'simulated_or_unavailable'
            df.at[idx, 'url'] = ''
            invalid += 1

    # Guardar CSV actualizado
    df.to_csv(CSV_PATH, index=False)
    print(f"Proceso finalizado. Total: {total}, Reemplazadas: {fixed}, Marcadas como invalidas/simuladas: {invalid}")
    print(f"CSV actualizado: {CSV_PATH}")


if __name__ == '__main__':
    main()
