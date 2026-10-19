#!/usr/bin/env python3
"""OSM leads.json -> leads.clean.json (full, goes to Firestore) + leads-preview.json (public, 5 masked rows).
Usage: python clean_leads.py leads.json"""
import json, math, re, sys, unicodedata, collections

SRC = sys.argv[1] if len(sys.argv) > 1 else 'leads.json'
DROP = {'Place Of Worship', 'School', 'Kindergarten', 'College', 'University', 'Bank', 'Atm', 'Post Office',
        'Police', 'Townhall', 'Parking', 'Prison', 'Courthouse', 'Library', 'Ferry Terminal', 'Community Centre', 'Theatre', 'Marketplace', 'Bus Station', 'Drinking Water', 'Fountain', 'Fuel', 'Hospital', 'Mall'}
TIER_A = {'Dentist', 'Clinic', 'Motel', 'Chalet', 'Lawyer', 'Estate Agent', 'Travel Agent', 'Accountant', 'Insurance', 'Restaurant', 'Hotel', 'Hostel', 'Guest House', 'Apartment', 'Car Repair', 'Hairdresser',
          'Beauty', 'Travel Agency', 'Furniture', 'Car', 'Car Parts', 'Tyres', 'Massage', 'Cosmetics',
          'Driving School', 'Electrical', 'Lighting', 'Doityourself'}
TIER_B = {'Cafe', 'Bar', 'Pub', 'Bakery', 'Pastry', 'Fast Food', 'Pharmacy', 'Clothes', 'Boutique', 'Jewelry',
          'Florist', 'Tattoo', 'Car Wash', 'Electronics', 'Computer', 'Mobile Phone', 'Appliance', 'Shoes',
          'Sports', 'Wholesale', 'Nightclub', 'Butcher', 'Deli'}


def norm(s):
    s = unicodedata.normalize('NFD', (s or '').lower())
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').strip()


def parse_phones(raw):
    """-> [(+355..., is_mobile)], mobiles first. Splits joined numbers, drops invalid ones."""
    out = []
    for part in re.split(r'[;,/]|(?<=\d)\s*(?=\+)', str(raw or '')):
        d = re.sub(r'\D', '', part)
        if d.startswith('00'):
            d = d[2:]
        if d.startswith('355'):
            d = d[3:]
        elif d.startswith('0'):
            d = d[1:]
        if len(d) == 9 and d[:2] in ('66', '67', '68', '69'):
            out.append(('+355' + d, True))
        elif len(d) == 8 and d[0] in '2345':
            out.append(('+355' + d, False))
    return sorted(out, key=lambda p: not p[1])


src = json.load(open(SRC, encoding='utf-8'))
rows = [b for b in src['businesses'] if b['category'] not in DROP]
print('input', len(src['businesses']), '| after dropping non-target categories', len(rows))

# --- cities: merge spellings, treat "Albania" as unknown, infer from nearest labelled neighbour (<4 km)
ALIAS = {'tirane': 'tirana'}
key = lambda c: ALIAS.get(norm(c), norm(c))
known = lambda c: bool(c) and norm(c) != 'albania'
counts = collections.defaultdict(collections.Counter)
for b in rows:
    c = (b['city'] or '').strip()
    if known(c):
        counts[key(c)][c] += 1
display = {k: v.most_common(1)[0][0] for k, v in counts.items()}
for b in rows:
    c = (b['city'] or '').strip()
    b['_city'] = display[key(c)] if known(c) else None

cell = lambda la, ln: (int(la * 20), int(ln * 20))
grid = collections.defaultdict(list)
for b in rows:
    if b['_city'] and b['lng'] is not None:
        grid[cell(b['lat'], b['lng'])].append(b)


def nearest(b):
    la, ln = b['lat'], b['lng']
    ci, cj = cell(la, ln)
    best = (4.0, None)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            for o in grid.get((ci + di, cj + dj), ()):
                d = math.hypot((o['lat'] - la) * 110.6, (o['lng'] - ln) * 111.3 * math.cos(math.radians(la)))
                if d < best[0]:
                    best = (d, o['_city'])
    return best[1]


guessed = 0
for b in rows:
    if not b['_city'] and b['lng'] is not None:
        c = nearest(b)
        if c:
            b['_city'], b['_cg'] = c, 1
            guessed += 1

# --- normalise phones, score, shape
out = []
for b in rows:
    name = (b['name'] or '').strip()
    if len(name) > 1 and name[0] == name[-1] == '"':
        name = name[1:-1].strip()
    if not name:
        continue
    ph = parse_phones(b['phone'])
    mobile = bool(ph) and ph[0][1]
    score = (25 + (35 if mobile else 20 if ph else 0)
             + (25 if b['category'] in TIER_A else 12 if b['category'] in TIER_B else 0)
             + (10 if b['_city'] else 0))
    r = {'id': b['id'], 'name': name, 'category': b['category'], 'city': b['_city'] or '',
         'phone': ph[0][0] if ph else None, 'mobile': mobile, 'lat': round(b['lat'], 5),
         'lng': round(b['lng'], 5) if b['lng'] is not None else None, 'score': score}
    if len(ph) > 1:
        r['phone2'] = ph[1][0]
    if b.get('_cg'):
        r['cg'] = 1
    out.append(r)

# --- dedupe: same name at the same spot, or same phone (best score wins)
out.sort(key=lambda r: -r['score'])
seen, seen_ph, final = set(), set(), []
for r in out:
    k = (norm(r['name']), round(r['lat'], 3), round(r['lng'], 3) if r['lng'] is not None else r['city'])
    if k in seen or (r['phone'] and r['phone'] in seen_ph):
        continue
    seen.add(k)
    if r['phone']:
        seen_ph.add(r['phone'])
    final.append(r)

stats = {'leads': len(final), 'cities': len({r['city'] for r in final if r['city']}),
         'avg': round(sum(r['score'] for r in final) / len(final))}
meta = {'source': 'live', 'generated': src.get('generated'), 'provider': 'OpenStreetMap',
        'license': 'ODbL, (c) OpenStreetMap contributors', 'stats': stats}


def mask(p):
    d = p[4:]
    return f'+355 {d[:2]} {d[2]}\u2022\u2022 \u2022\u2022{d[-2:]}'


preview, cats = [], set()
for r in final:
    if r['mobile'] and r['category'] in TIER_A and r['city'] and not r.get('cg') and r['category'] not in cats:
        cats.add(r['category'])
        p = {k: v for k, v in r.items() if k not in ('phone', 'phone2', 'mobile')}
        p.update(phone=None, phone_masked=mask(r['phone']), mobile=False)
        preview.append(p)
        if len(preview) == 5:
            break

dump = lambda o, f: json.dump(o, open(f, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
dump({**meta, 'count': len(final), 'businesses': final}, 'leads.clean.json')
dump({**meta, 'count': len(preview), 'businesses': preview}, 'leads-preview.json')

print('final', len(final), '| city inferred', guessed, '| with phone', sum(1 for r in final if r['phone']),
      '| mobile', sum(1 for r in final if r['mobile']), '| no city', sum(1 for r in final if not r['city']))
print('stats', stats)
print('score spread', sorted(collections.Counter(r['score'] for r in final).items()))
print('categories', collections.Counter(r['category'] for r in final).most_common(80))
