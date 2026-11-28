#!/usr/bin/env python3
# Formale Pruefung: gueltiges JSON, alle zitierten Quellen vorhanden, Abbildungen vollstaendig, kein ungenutzter Code.
# Laeuft bei jeder Aenderung automatisch (GitHub Actions); Fehler werden im Lauf angezeigt.
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fehler = []

def keys_in(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == 's' and isinstance(v, list):
                yield from (x for x in v if isinstance(x, str))
            elif k != 'cite':
                yield from keys_in(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from keys_in(v)

for sub in ('topics', 'screening', 'kandidaten'):
    d = os.path.join(ROOT, 'data', sub)
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        if not f.endswith('.json'):
            continue
        p = os.path.join(d, f)
        try:
            j = json.load(open(p))
        except Exception as e:
            fehler.append(f'{sub}/{f}: kein gültiges JSON ({e})'); continue
        if sub != 'topics':
            continue
        src = j.get('sources', {})
        for k in set(keys_in({x: j.get(x) for x in ('rx', 'takeaways', 'vars', 'timeline', 'def')})):
            if k not in src:
                fehler.append(f'{sub}/{f}: Quelle "{k}" wird zitiert, fehlt aber in sources')
        for k, s in src.items():
            if not s.get('apa'):
                fehler.append(f'{sub}/{f}: Quelle "{k}" ohne APA-Angabe')
        for fg in j.get('trend', []):
            for pt in fg.get('data', []):
                if pt.get('s') not in src: fehler.append(f'{sub}/{f}: Verlaufsdiagramm "{fg.get("id")}" zitiert fehlende Quelle "{pt.get("s")}"')
        vids = {v['id'] for v in j.get('vars', [])}
        for g in j.get('matrix', []):
            for k in ('bereich', 'ziel', 'kat', 'items'):
                if k not in g: fehler.append(f'{sub}/{f}: Matrix-Gruppe ohne Feld "{k}"')
            if g.get('bereich') not in ('Leistung', 'Regeneration', 'Gesundheit'):
                fehler.append(f'{sub}/{f}: Matrix-Gruppe "{g.get("ziel")}" mit unbekanntem Bereich')
            for it in g.get('items', []):
                n = it.get('n', '?')
                if it.get('g') not in ('A', 'B', 'C', 'D', '0'): fehler.append(f'{sub}/{f}: Wirkung "{n}" ohne gültigen Grad')
                if it.get('m') not in (None, -1, 0, 1, 2, 3, 4): fehler.append(f'{sub}/{f}: Wirkung "{n}" mit ungültiger Effektgröße')
                if it.get('m') not in (0, None) and it.get('d') not in ('auf', 'ab'): fehler.append(f'{sub}/{f}: Wirkung "{n}" ohne Richtung')
                if it.get('b') not in ('nutzen', 'schaden', 'neutral'): fehler.append(f'{sub}/{f}: Wirkung "{n}" ohne Bewertung')
                if it.get('v') not in vids: fehler.append(f'{sub}/{f}: Wirkung "{n}" verweist auf unbekannten Abschnitt')
                if it.get('pop', 'alle') not in ('alle', 'einsteiger', 'trainiert', 'aelter'): fehler.append(f'{sub}/{f}: Wirkung "{n}" mit unbekannter Zielgruppe "{it.get("pop")}"')
                if 'w' in it and not str(it['w']).strip(): fehler.append(f'{sub}/{f}: Wirkung "{n}" mit leerem Oberbegriff')
                for k in it.get('s', []):
                    if k not in src: fehler.append(f'{sub}/{f}: Wirkung "{n}" zitiert fehlende Quelle "{k}"')
        for v in j.get('vars', []):
            for fig in v.get('figs', []):
                if not fig.get('data'):
                    fehler.append(f'{sub}/{f}: Abbildung "{fig.get("id")}" ohne Daten')

for m in json.load(open(os.path.join(ROOT, 'data', 'mythen.json')))['items']:
    tp = os.path.join(ROOT, 'data', 'topics', m['topic'] + '.json')
    src = json.load(open(tp))['sources'] if os.path.exists(tp) else {}
    for k in m['s']:
        if k not in src: fehler.append(f'mythen.json: „{m["m"][:40]}…“ zitiert fehlende Quelle "{k}" ({m["topic"]})')

ww = json.load(open(os.path.join(ROOT, 'data', 'wechselwirkungen.json')))
for i in ww['items']:
    nm = f'wechselwirkungen.json: {i["a"]} + {i["b"]}'
    for t in (i['a'], i['b']):
        if not os.path.exists(os.path.join(ROOT, 'data', 'topics', t + '.json')): fehler.append(f'{nm}: unbekanntes Thema "{t}"')
    if i.get('art') not in ('ergaenzt', 'kein', 'achtung', 'hemmt', 'unklar'): fehler.append(f'{nm}: unbekannte Art "{i.get("art")}"')
    if i.get('ev') not in ('hoch', 'moderat', 'niedrig'): fehler.append(f'{nm}: unbekannte Evidenz "{i.get("ev")}"')
    for k in i['s']:
        if k not in ww['sources']: fehler.append(f'{nm}: zitiert fehlende Quelle "{k}"')
    for x in i['t']:
        for sh in re.findall(r'\(([^()]*?, \d{4})\)', x):
            if not any(ww['sources'][k]['short'].replace('&', '&amp;') == sh or ww['sources'][k]['short'] == sh for k in i['s']): fehler.append(f'{nm}: Zitat "({sh})" ohne passende Quelle')

html = open(os.path.join(ROOT, 'index.html')).read()
m = re.search(r'const AVAILABLE = \[(.*?)\]', html)
if m:
    for t in re.findall(r'"([^"]+)"', m.group(1)):
        if not os.path.exists(os.path.join(ROOT, 'data', 'topics', t + '.json')):
            fehler.append(f'index.html: Thema "{t}" freigeschaltet, aber data/topics/{t}.json fehlt')

# Ungenutzter Code in index.html: Funktionen/Konstanten, die nur deklariert, und CSS-Klassen, die nirgends verwendet werden.
# Klassen, die per Vorlage zusammengesetzt werden (z. B. `lv${n}`, `e${x}`), stehen in DYN.
DYN = re.compile(r'^(e[0-4m]|lv\d|chart-\w+|tag-\w+|ev-\w+)$')
css = '\n'.join(re.findall(r'<style>(.*?)</style>', html, re.S))
rest = re.sub(r'<style>.*?</style>', '', html, flags=re.S)
daten = ''.join(open(os.path.join(ROOT, 'data', 'topics', f)).read() for f in os.listdir(os.path.join(ROOT, 'data', 'topics')))
for n in sorted(set(re.findall(r'(?:function\s+|(?:const|let)\s+)([A-Za-z_$][\w$]*)', rest))):
    if len(re.findall(r'(?<![\w$])(?<![\w$)\]]\.)' + re.escape(n) + r'(?![\w$])', rest)) < 2:
        fehler.append(f'index.html: "{n}" wird deklariert, aber nirgends verwendet')
for c in sorted(set(re.findall(r'\.([a-zA-Z][\w-]*)', re.sub(r'\d+\.\d+|url\([^)]*\)', '', css)))):
    if not DYN.match(c) and not re.search(r'(?<![\w-])' + re.escape(c) + r'(?![\w-])', rest + daten):
        fehler.append(f'index.html: CSS-Klasse ".{c}" wird nirgends verwendet')

if fehler:
    print('\n'.join(fehler)); sys.exit(1)
print('Alle Daten formal in Ordnung.')
