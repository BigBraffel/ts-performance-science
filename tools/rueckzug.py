#!/usr/bin/env python3
# Prueft alle zitierten Quellen (data/topics/*.json und data/wechselwirkungen.json) bei PubMed auf Rueckzug, Korrektur oder Bedenken
# und schreibt Treffer nach data/kandidaten/_rueckzuege.json. Laeuft mit der PubMed-Abfrage (scan_all.py).
import json, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pubmed_update import summaries, FLAGPT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    zit = {}  # pmid -> [(thema, schluessel)]
    tdir = os.path.join(ROOT, 'data', 'topics')
    for f in sorted(os.listdir(tdir)):
        if f.endswith('.json'):
            for k, s in json.load(open(os.path.join(tdir, f))).get('sources', {}).items():
                if s.get('pmid'):
                    zit.setdefault(str(s['pmid']), []).append((f[:-5], k))
    for k, s in json.load(open(os.path.join(ROOT, 'data', 'wechselwirkungen.json'))).get('sources', {}).items():
        if s.get('pmid'):
            zit.setdefault(str(s['pmid']), []).append(('wechselwirkungen', k))
    info = summaries(sorted(zit))
    treffer = [dict(pmid=p, titel=x['t'], hinweis=sorted(set(x['pt']) & FLAGPT), zitiert=[dict(thema=t, quelle=k) for t, k in zit[p]])
               for p, x in info.items() if set(x['pt']) & FLAGPT]
    os.makedirs(os.path.join(ROOT, 'data', 'kandidaten'), exist_ok=True)
    json.dump(dict(datum=datetime.date.today().isoformat(), geprueft=len(zit), treffer=treffer),
              open(os.path.join(ROOT, 'data', 'kandidaten', '_rueckzuege.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'{len(zit)} zitierte Arbeiten geprüft, {len(treffer)} mit Rückzug/Korrektur/Bedenken.')

if __name__ == '__main__':
    main()
