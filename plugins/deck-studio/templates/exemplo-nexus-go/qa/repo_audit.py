"""Fact audit: dissertation tables (thesis_tables.json) vs repo and 178-run CSV.
Usage: python -I audit.py <kit_dir> <repo_dir> <poscc_dir> <out_md>
Read-only on all inputs; writes only <out_md>."""
import csv, json, re, sys, statistics as st
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

KIT, REPO, POS, OUT = map(Path, sys.argv[1:5])
T = json.load(open(KIT / 'data/thesis_tables.json', encoding='utf-8'))
ONTS = ['BP', 'CC', 'MF']
CHECKS = []  # (section, item, diss, source, value, status)


def rhu(x, d):
    return float(Decimal(repr(x)).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP))


def check(section, item, diss, source, val, dec=2):
    if val is None:
        CHECKS.append((section, item, diss, source, None, 'ausente'))
        return 'ausente'
    r = rhu(val, dec)
    if abs(r - diss) < 1e-9:
        s = 'concorda'
    elif abs(val - diss) <= 0.5 * 10 ** -dec + 1e-9:
        s = 'arredondamento'
    else:
        s = 'diverge'
    CHECKS.append((section, item, diss, source, val, s))
    return s


def check_avg(section, item, dv, source, vals):
    # dissertation AVG may be the mean of the already-rounded cells
    s = check(section, item, dv, source, st.mean(vals))
    mr = (sum(Decimal(repr(rhu(v, 2))) for v in vals) / len(vals)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    if s == 'diverge' and abs(float(mr) - dv) < 1e-9:
        CHECKS[-1] = CHECKS[-1][:5] + ('arredondamento',)
        s = 'arredondamento'
    return s


def num(s):
    return float(s.replace('*', '').replace(',', '.').strip())


def md_table_after(text, heading, stop=None):
    """Rows (list of cells) of the first markdown table after `heading`."""
    i = text.index(heading)
    rows = []
    started = False
    for line in text[i:].splitlines()[1:]:
        if line.startswith('|'):
            started = True
            cells = [c.strip() for c in line.strip().strip('|').split('|')]
            if not set(cells[0]) <= set('-'):
                rows.append(cells)
        elif started:
            break
    return rows[1:]  # drop header


# ---------------------------------------------------------------- CSV 178
rows = list(csv.DictReader(open(POS / 'tabelas/results_all_178runs.csv', encoding='utf-8')))
SUPERSEDED = {
    # hybrid CC runs at the pre-update champion configs (h2 a0.7 vector, h5 a0.5 vision),
    # no provenance suffix, 2026-08-03/04; rerun on 2026-08-14 at h2 a0.8 / h6 a0.5
    'cc_hybrid_add_gat_mlp_h2_a07_thr010_dedupmax',
    'cc_hybrid_add_gcn_mlp_h2_a07_thr010_dedupmax',
    'cc_hybrid_concat_gat_mlp_h2_a07_thr010_dedupmax',
    'cc_hybrid_concat_gcn_mlp_h2_a07_thr010_dedupmax',
    'cc_hybrid_add_gat_vision_h5_a05_thr010_dedupmax',
    'cc_hybrid_add_gcn_vision_h5_a05_thr010_dedupmax',
    # alpha sweep of the vision route at the pre-update best depth T=5 (GTX 1080 Ti);
    # replaced by the alpha sweep at T=6 (RTX A5500, 2026-08-14)
    'cc_fixed_vision_h5_a03_thr010_dedupmax',
    'cc_fixed_vision_h5_a07_thr010_dedupmax',
}
assert all(any(r['tag'] == t for r in rows) for t in SUPERSEDED)
for r in rows:
    for k in ('fmax', 'fmax_star', 'wfmax', 'smin', 'auprc', 'iauprc', 'hops', 'alpha_init',
              'wall_seconds', 'peak_vram_mb', 'sec_per_epoch', 'best_epoch', 'epochs_run'):
        r[k] = float(r[k])
    r['prov'] = 'mlp' if '_mlp_dedup' in r['gnn_emb_path'] else ('vision' if '_vision_dedup' in r['gnn_emb_path'] else '')
    r['gpu'] = 'GTX 1080 Ti' if (r['method'] == 'fixed' and r['classifier_type'] == 'vision'
                                 and r['sec_per_epoch'] > 100) else 'RTX A5500'
camp = [r for r in rows if r['tag'] not in SUPERSEDED]
val = {r['tag']: r for r in camp if r['split'] == 'val'}
test = {r['tag']: r for r in camp if r['split'] == 'test'}
assert len(val) == len(test) == 170


def runs(**kw):
    return [r for r in val.values() if all(r[k] == v for k, v in kw.items())]


def best(**kw):
    return max(runs(**kw), key=lambda r: r['wfmax'])


def one(**kw):
    c = runs(**kw)
    assert len(c) == 1, (kw, [r['tag'] for r in c])
    return c[0]


out = []
w = out.append

# ---------------------------------------------------------------- campaign accounting
fam = {}
for r in val.values():
    fam.setdefault((r['method'], r['classifier_type'], r['gpu']), []).append(r)
h = lambda rs: sum(r['wall_seconds'] for r in rs) / 3600
allr = list(val.values())
rtx = [r for r in allr if r['gpu'] == 'RTX A5500']
gtx = [r for r in allr if r['gpu'] != 'RTX A5500']
route = lambda m: [r for r in allr if r['method'] == m]
S = 'Campanha (texto, A.7 / FACTS §8)'
check(S, 'runs na campanha', 170, 'CSV 170', len(allr), 0)
check(S, 'GPU-horas da campanha', 136.3, 'CSV 170', h(allr), 1)
check(S, 'runs RTX A5500', 147, 'CSV 170', len(rtx), 0)
check(S, 'horas RTX A5500', 103.0, 'CSV 170', h(rtx), 1)
check(S, 'runs GTX 1080 Ti', 23, 'CSV 170', len(gtx), 0)
check(S, 'horas GTX 1080 Ti', 33.3, 'CSV 170', h(gtx), 1)
check(S, 'rota fixa: runs', 98, 'CSV 170', len(route('fixed')), 0)
check(S, 'rota fixa: horas', 52.9, 'CSV 170', h(route('fixed')), 1)
check(S, 'rota aprendida: runs', 12, 'CSV 170', len(route('gnn')), 0)
check(S, 'rota aprendida: horas', 70.0, 'CSV 170', h(route('gnn')), 1)
check(S, 'early fusion: runs', 60, 'CSV 170', len(route('hybrid')), 0)
check(S, 'early fusion: horas', 13.4, 'CSV 170', h(route('hybrid')), 1)
gm = lambda g: [r for r in allr if r['method'] == 'gnn' and r['gnn_type'] == g and r['classifier_type'] == 'mlp']
check(S, 'GCN (vetor) s/época, mediana 3 ont.', 68.76, 'CSV 170', st.median(r['sec_per_epoch'] for r in gm('gcn')))
check(S, 'GCN (vetor) VRAM GiB, pico 3 ont.', 14.1, 'CSV 170', max(r['peak_vram_mb'] for r in gm('gcn')) / 1024, 1)
check(S, 'GAT (vetor) s/época, mediana 3 ont.', 161.41, 'CSV 170', st.median(r['sec_per_epoch'] for r in gm('gat')))
check(S, 'GAT (vetor) VRAM GiB, pico 3 ont.', 20.7, 'CSV 170', max(r['peak_vram_mb'] for r in gm('gat')) / 1024, 1)
bpg = {g: one(domain='bp', method='gnn', gnn_type=g, classifier_type='mlp') for g in ('gcn', 'gat')}
check(S, 'GAT/GCN memória, BP vetor (+%)', 46, 'CSV 170', 100 * (bpg['gat']['peak_vram_mb'] / bpg['gcn']['peak_vram_mb'] - 1), 0)
check(S, 'GAT/GCN tempo, BP vetor (+%)', 55, 'CSV 170', 100 * (bpg['gat']['wall_seconds'] / bpg['gcn']['wall_seconds'] - 1), 0)

# ---------------------------------------------------------------- cost table (tab:custo)
FAMS = [('Fixed propagation + vector head', 'fixed', 'mlp'), ('Fixed propagation + vision head', 'fixed', 'vision'),
        ('End-to-end GNN + vector head', 'gnn', 'mlp'), ('End-to-end GNN + vision head', 'gnn', 'vision'),
        ('Early fusion + vector head', 'hybrid', 'mlp'), ('Early fusion + vision head', 'hybrid', 'vision')]
REPO01 = (REPO / 'results/chapter6/01_TABELAS_dedupmax.md').read_text(encoding='utf-8')
POS01 = (POS / 'tabelas/01_TABELAS_dedupmax.md').read_text(encoding='utf-8')
repo_cost = {c[0]: c for c in md_table_after(REPO01, '### Tabela 6.16')}
REPOKEY = {('fixed', 'mlp'): 'fixed + mlp', ('fixed', 'vision'): 'fixed + vision', ('gnn', 'mlp'): 'gnn + mlp',
           ('gnn', 'vision'): 'gnn + vision', ('hybrid', 'mlp'): 'hybrid + mlp', ('hybrid', 'vision'): 'hybrid + vision'}
cost_rows = []
S = 'Custo (tab:custo)'
for (name, m, hd), drow in zip(FAMS, T['cost']['rows'][1:7]):
    assert drow[0] == name
    rs = fam[(m, hd, 'RTX A5500')]
    calc = [len(rs), st.median(r['sec_per_epoch'] for r in rs), st.median(r['wall_seconds'] for r in rs) / 3600,
            h(rs), max(r['peak_vram_mb'] for r in rs) / 1024, st.median(r['epochs_run'] for r in rs)]
    rc = repo_cost[REPOKEY[(m, hd)]]
    repo = [num(rc[1]), None, num(rc[2]), num(rc[3]), num(rc[4].replace('GB', '')), num(rc[5])]
    cols = ['Runs', 's/epoch', 'h/run', 'Total h', 'VRAM (GiB)', 'Epochs']
    decs = [0, 2, 2, 1, 1, 0]
    cells = []
    for c, d, dv, cv, rv in zip(cols, decs, drow[1:], calc, repo):
        sc = check(S, f'{name} | {c}', dv, 'CSV 170 (RTX)', cv, d)
        sr = check(S, f'{name} | {c}', dv, 'repo 01 Tab. 6.16', rv, d)
        cells.append((dv, cv, sc, rv, sr, d))
    cost_rows.append((name, cells))
check(S, 'Total | Runs', 147, 'CSV 170 (RTX)', len(rtx), 0)
check(S, 'Total | Total h', 103.0, 'CSV 170 (RTX)', h(rtx), 1)
repo_total = re.search(r'Total da campanha: ([\d,]+) GPU-horas em (\d+) runs', REPO01)
check(S, 'Total | Runs', 147, 'repo 01 Tab. 6.16', float(repo_total.group(2)), 0)
check(S, 'Total | Total h', 103.0, 'repo 01 Tab. 6.16', num(repo_total.group(1)), 1)

# ---------------------------------------------------------------- tab:ape_custo (cost_runs), values from the tex
S = 'Custo por família/run (tab:ape_custo)'
APE = [('Fixed, vector head', 'fixed', 'mlp', 'RTX A5500', 49, 6602, 0.35, 0.38, 230, 81, 250),
       ('Fixed, vision head', 'fixed', 'vision', 'RTX A5500', 26, 6602, 0.17, 0.22, 14, 9, 20),
       ('Fixed, vision head', 'fixed', 'vision', 'GTX 1080 Ti', 23, 6602, 1.39, 2.00, 13, 9, 24),
       ('Early fusion, vector head', 'hybrid', 'mlp', 'RTX A5500', 40, 6602, 0.27, 0.38, 184, 30, 250),
       ('Early fusion, vision head', 'hybrid', 'vision', 'RTX A5500', 20, 6602, 0.16, 0.19, 9, 7, 13)]
ape_rows = []
for name, m, hd, g, n, mem, wmed, wmax, emed, emin, emax in APE:
    rs = fam[(m, hd, g)]
    calc = [len(rs), max(r['peak_vram_mb'] for r in rs), st.median(r['wall_seconds'] for r in rs) / 3600,
            max(r['wall_seconds'] for r in rs) / 3600, st.median(r['best_epoch'] for r in rs),
            min(r['best_epoch'] for r in rs), max(r['best_epoch'] for r in rs)]
    ref = [n, mem, wmed, wmax, emed, emin, emax]
    decs = [0, 0, 2, 2, 0, 0, 0]
    labs = ['Runs', 'Peak MiB', 'Wall med.', 'Wall máx.', 'Sel. ep. med.', 'Sel. ep. mín.', 'Sel. ep. máx.']
    st_ = [check(S, f'{name} {g} | {l}', rv, 'CSV 170', cv, d) for l, rv, cv, d in zip(labs, ref, calc, decs)]
    ape_rows.append((f'{name} ({g})', ref, calc, st_, decs))
for name, gt, hd, mem, wall, ep in [('GCN, vector head', 'gcn', 'mlp', 12953, 4.77, 234), ('GAT, vector head', 'gat', 'mlp', 18864, 7.40, 144),
                                     ('GCN, vision head', 'gcn', 'vision', 13355, 1.96, 73), ('GAT, vision head', 'gat', 'vision', 19267, 9.72, 186)]:
    r = one(domain='bp', method='gnn', gnn_type=gt, classifier_type=hd)
    calc = [1, r['peak_vram_mb'], r['wall_seconds'] / 3600, None, r['best_epoch'], None, None]
    ref = [1, mem, wall, None, ep, None, None]
    st_ = [check(S, f'{name} BP | Peak MiB', mem, 'CSV 170', r['peak_vram_mb'], 0) if i == 1 else
           check(S, f'{name} BP | Wall h', wall, 'CSV 170', r['wall_seconds'] / 3600, 2) if i == 2 else
           check(S, f'{name} BP | Sel. epoch', ep, 'CSV 170', r['best_epoch'], 0) if i == 4 else None
           for i in range(7)]
    ape_rows.append((f'{name} (BP, run único)', ref, calc, st_, [0, 0, 2, 2, 0, 0, 0]))

# ---------------------------------------------------------------- late fusion
RULES = {'Linear interpolation (\\gamma)': 'linear', 'Maximum': 'max', 'Minimum': 'min', 'IC sigmoid': 'ic_sigmoid',
         'Degree sigmoid': 'degree_sigmoid', 'Master equation': 'master', 'Stacking (decision tree)': 'stacking_dt',
         'Stacking (logistic regression)': 'stacking_lr', 'Stacking (MLP)': 'stacking_mlp',
         'Stacking (random forest)': 'stacking_rf', 'Stacking (gradient boosting)': 'stacking_gb'}


def late_from_md(text):
    d = {}
    for c in md_table_after(text, '### Tabela 6.13'):
        d[(c[0], c[1].strip('*'))] = (num(c[2]), num(c[3]), c[4])
    return d


late_repo = late_from_md(REPO01)
late_pos01 = late_from_md(POS01)
LOG = (POS / 'late_fusion/ensemble_cc_novo.log').read_text(encoding='utf-8')
late_log = {}
for m in re.finditer(r'^\s+(\w+)\s+wfmax_val=([\d.]+)\s+wfmax_test=([\d.]+)\s+params=(.*)$', LOG.split('=== RESUMO')[1], re.M):
    late_log[m.group(1)] = (float(m.group(2)), float(m.group(3)), m.group(4))
assert len(late_log) == 11
late_cur = {}
for (o, k), v in late_repo.items():
    if o in ('BP', 'MF'):
        late_cur[(o, k)] = v
for k, v in late_log.items():
    late_cur[('CC', k)] = v
late_rows = []
S = 'Late fusion (tab:late_fusion)'
for drow in T['late']['rows'][1:]:
    k = RULES[drow[0]]
    cells = []
    for i, o in enumerate(ONTS):
        dv = drow[1 + i]
        rv = late_repo[(o, k)][0] * 100
        cv = late_cur[(o, k)][0] * 100
        src = 'log CC novo' if o == 'CC' else 'repo 01 Tab. 6.13'
        sr = check(S, f'{drow[0]} | {o}', dv, 'repo 01 Tab. 6.13', rv)
        sc = check(S, f'{drow[0]} | {o}', dv, 'atual (' + src + ')', cv) if o == 'CC' else sr
        cells.append((dv, rv, sr, cv, sc))
    dv = drow[4]
    rl = [late_repo[(o, k)][0] * 100 for o in ONTS]
    cl = [late_cur[(o, k)][0] * 100 for o in ONTS]
    rv, cv = st.mean(rl), st.mean(cl)
    sr = check_avg(S, f'{drow[0]} | AVG', dv, 'média repo', rl)
    sc = check_avg(S, f'{drow[0]} | AVG', dv, 'média atual (BP/MF repo + CC log)', cl)
    cells.append((dv, rv, sr, cv, sc))
    late_rows.append((drow[0], cells))
# post-CC 01 vs log consistency (CC), and vs repo (BP/MF)
pos_consistent = all(abs(late_pos01[('CC', k)][0] - late_log[k][0]) < 1e-9 and abs(late_pos01[('CC', k)][1] - late_log[k][1]) < 1e-9 for k in late_log) \
    and all(late_pos01[(o, k)][:2] == late_repo[(o, k)][:2] for o in ('BP', 'MF') for k in late_log)
# selected coefficients (tab:ape_fusao_sel)
S = 'Coeficientes selecionados (tab:ape_fusao_sel)'
fsel = T['fusion_selected']['rows'][1:]


def params(o, src):
    p = src[(o, 'linear')][2], src[(o, 'master')][2]
    return p


coef_rows = []
for o_i, o in enumerate(ONTS):
    for srcname, src in (('repo 01', late_repo), ('atual', late_cur)):
        lin = src[(o, 'linear')][2]
        mas = src[(o, 'master')][2]
        g = float(re.search(r"gamma'?[=:]\s*([\d.]+)", lin).group(1))
        lam = float(re.search(r"alpha'?[=:]\s*([\d.]+)", mas).group(1))
        ic = float(re.search(r"ic_thr'?[=:]\s*([\d.]+)", mas).group(1))
        kic = float(re.search(r"k_ic'?[=:]\s*([\d.]+)", mas).group(1))
        dthr = float(re.search(r"d_thr'?[=:]\s*([\d.]+)", mas).group(1))
        kdeg = float(re.search(r"k_deg'?[=:]\s*([\d.]+)", mas).group(1))
        vals = [g, ic, kic, dthr, kdeg, lam]
        names = ['gamma', 'IC_thr', 'k_IC', 'd_thr', 'k_deg', 'lambda']
        sts = [check(S, f'{n} | {o}', fsel[i][2 + o_i], srcname, v) for i, (n, v) in enumerate(zip(names, vals))]
        coef_rows.append((o, srcname, [fsel[i][2 + o_i] for i in range(6)], vals, sts))

# ---------------------------------------------------------------- test tables
REPO07 = (REPO / 'results/chapter6/07_CONFRONTO_FINAL.md').read_text(encoding='utf-8')
POS07 = (POS / 'tabelas/07_CONFRONTO_FINAL.md').read_text(encoding='utf-8')


def conf07(text):
    d = {}
    t = text.split('## TESTE')[1]
    for o in ONTS:
        for c in md_table_after(t, f'### {o}'):
            d[(o, c[1])] = [num(x) for x in c[2:8]]
    return d


r07, p07 = conf07(REPO07), conf07(POS07)
M07 = {'First Generation': 'PPI-only (topologia pura)', 'ProtT5 baseline': 'ProtT5 puro (h=0)',
       'NEXUS-GO/Fixed': 'SPMM fixo + MLP', 'NEXUS-GO/GNN': 'GNN E2E + MLP', 'NEXUS-GO/Early': 'Early Fusion + MLP',
       'NEXUS-GO/Late': 'Late Fusion (linear)', 'DeepGraphGO': 'DeepGraphGO', 'SEGT-GO': 'SEGT-GO', 'Mashup': 'Mashup',
       'MELISSA': 'MELISSA', 'deepNF': 'DeepNF'}
abl = list(csv.DictReader(open(REPO / 'results/ppi_only/ABLATIONS_summary.csv', encoding='utf-8')))
MK = ['fmax', 'fmax_star', 'wfmax', 'auprc', 'iauprc', 'smin']
SC = [100, 100, 100, 100, 100, 1]


def first_gen(o):
    v = max((r for r in abl if r['domain'] == o.lower() and r['split'] == 'val'), key=lambda r: float(r['wfmax']))
    t = next(r for r in abl if r['tag'] == v['tag'] and r['split'] == 'test')
    return [float(t[k]) for k in MK], v['tag']


def csv_test(method, o):
    o_ = o.lower()
    if method == 'ProtT5 baseline':
        r = one(domain=o_, method='fixed', classifier_type='mlp', hops=0.0)
    elif method == 'NEXUS-GO/Fixed':
        r = best(domain=o_, method='fixed', classifier_type='mlp')
    elif method == 'NEXUS-GO/GNN':
        r = best(domain=o_, method='gnn', classifier_type='mlp')
    elif method == 'NEXUS-GO/Early':
        r = best(domain=o_, method='hybrid', classifier_type='mlp')
    else:
        return None, None
    t = test[r['tag']]
    return [t[k] for k in MK], r['tag']


test_mats = {}
champ_tags = {}
for o in ONTS:
    tab = T[f'test_{o}']['rows']
    S = f'Teste {o} (tab:confronto_{o.lower()})'
    mat = []
    for drow in tab[1:]:
        meth = drow[0]
        rv = r07.get((o, M07.get(meth)))
        pv = p07.get((o, M07.get(meth)))
        cv, tag = csv_test(meth, o)
        csrc = 'CSV 170'
        if meth == 'First Generation':
            cv, tag = first_gen(o)
            csrc = 'repo ABLATIONS_summary.csv'
        if meth == 'NEXUS-GO/Late':
            lv = late_log['linear'][1] if o == 'CC' else late_repo[(o, 'linear')][1]
            cv = [None, None, lv, None, None, None]
            csrc = 'log CC novo' if o == 'CC' else 'repo 01 Tab. 6.13 (teste)'
        if tag:
            champ_tags[(o, meth)] = tag
        cells = []
        for j in range(6):
            dv = drow[1 + j]
            # repo 07 / pós-CC 07: fractions for metrics, bits for Smin
            sr = check(S, f'{meth} | {MK[j]}', dv, 'repo 07', None if rv is None else rv[j] * SC[j])
            sp = check(S, f'{meth} | {MK[j]}', dv, 'pós-CC 07', None if pv is None else pv[j] * SC[j])
            if cv is None or cv[j] is None:
                sc = check(S, f'{meth} | {MK[j]}', dv, csrc, None)
                cval = None
            else:
                cval = cv[j] * SC[j]
                sc = check(S, f'{meth} | {MK[j]}', dv, csrc, cval)
            cells.append((dv, None if rv is None else rv[j] * SC[j], sr, None if pv is None else pv[j] * SC[j], sp, cval, sc))
        mat.append((meth, cells))
    test_mats[o] = mat

# ---------------------------------------------------------------- context tables (validation, CSV 170)
ctx = []  # (table, cell, diss, csv, status)


def cx(table, cell, dv, cv, dec=2):
    if isinstance(cv, list):
        s = check_avg('Contexto ' + table, cell, dv, 'CSV 170', cv)
        cv = st.mean(cv)
    else:
        s = check('Contexto ' + table, cell, dv, 'CSV 170', cv, dec)
    if s != 'concorda':
        ctx.append((table, cell, dv, cv, s))


def fixed_val(o, hd, T_, a):
    return one(domain=o.lower(), method='fixed', classifier_type=hd, hops=float(T_), alpha_init=a)['wfmax'] * 100


for key, hd in (('hops_vector', 'mlp'), ('hops_vision', 'vision')):
    for row in T[key]['rows'][1:]:
        vs = [fixed_val(o, hd, row[0], 0.5) for o in ONTS]
        for o, dv, v in zip(ONTS, row[1:4], vs):
            cx(key, f'T={int(row[0])} {o}', dv, v)
        cx(key, f'T={int(row[0])} AVG', row[4], vs)
for key, hd, bt in (('alpha_vector', 'mlp', {'BP': 1, 'CC': 2, 'MF': 0}), ('alpha_vision', 'vision', {'BP': 7, 'CC': 6, 'MF': 0})):
    for row in T[key]['rows'][1:]:
        vs = []
        for o, dv in zip(ONTS, row[1:4]):
            if dv == 'n/a':
                continue
            v = fixed_val(o, hd, bt[o] if o != 'MF' else 0, row[0])
            cx(key, f'alpha={row[0]} {o}', dv, v)
            if o != 'MF':
                vs.append(v)
        cx(key, f'alpha={row[0]} AVG(BP,CC)', row[4], vs)
g = T['gnn']['rows'][1:]
for row, (gt, hd) in zip(g, [('gcn', 'mlp'), ('gcn', 'vision'), ('gat', 'mlp'), ('gat', 'vision')]):
    vs = [one(domain=o.lower(), method='gnn', gnn_type=gt, classifier_type=hd)['wfmax'] * 100 for o in ONTS]
    for o, dv, v in zip(ONTS, row[2:5], vs):
        cx('gnn', f'{gt}/{hd} {o}', dv, v)
    cx('gnn', f'{gt}/{hd} AVG', row[5], vs)
SRC = {'vector': {'BP': (1, 0.7), 'CC': (2, 0.8), 'MF': (0, 0.5)}, 'vision': {'BP': (7, 0.5), 'CC': (6, 0.5), 'MF': None}}


def hyb(o, fusion, enc, hd, prov, src):
    s = SRC[src][o]
    if s is None:
        return None
    prov_ = 'mlp' if prov == 'vector' else 'vision'
    return one(domain=o.lower(), method='hybrid', hybrid_fusion=fusion, gnn_type=enc, classifier_type=hd,
               hops=float(s[0]), alpha_init=s[1], prov=prov_)['wfmax'] * 100


eg = T['early_grid']['rows'][1:]
for i, row in enumerate(eg):
    hd = 'mlp' if i < 8 else 'vision'
    for o, dv in zip(ONTS, row[4:7]):
        if dv == 'n/a':
            continue
        cx('early_grid', f'{hd} {row[1]} prov={row[2]} src={row[3]} {o}', dv, hyb(o, row[1], 'gcn', hd, row[2], row[3]))
for row in T['early_best']['rows'][1:]:
    if row[3] == 'n/a' or row[1] == 'GCN / GAT':
        continue
    hd = 'mlp' if row[2] == 'Vector' else 'vision'
    vs = []
    for o, dv in zip(ONTS, row[3:6]):
        c = [r['wfmax'] * 100 for r in runs(domain=o.lower(), method='hybrid', hybrid_fusion=row[0], gnn_type=row[1].lower(), classifier_type=hd)]
        vs.append(max(c))
        cx('early_best', f'{row[0]} {row[1]} {row[2]} {o}', dv, max(c))
    cx('early_best', f'{row[0]} {row[1]} {row[2]} AVG', row[6], vs)
vv = T['vector_vs_vision']['rows'][1:]
stage = None
for row in vv:
    stage = row[0] or stage
    hd = row[1]
    vs = []
    for o, dv in zip(ONTS, row[2:5]):
        if stage == 'First Generation':
            pool = [r for r in abl if r['domain'] == o.lower() and r['split'] == 'val'
                    and ((r['model'] in ('mlp', 'cnn1d')) == (hd == 'Vector'))]
            v = max(float(r['wfmax']) for r in pool) * 100
        else:
            m = {'Fixed propagation': 'fixed', 'End-to-end GNN': 'gnn', 'Early fusion': 'hybrid'}[stage]
            v = best(domain=o.lower(), method=m, classifier_type='mlp' if hd == 'Vector' else 'vision')['wfmax'] * 100
        vs.append(v)
        cx('vector_vs_vision', f'{stage} {hd} {o}', dv, v)
    cx('vector_vs_vision', f'{stage} {hd} AVG', row[5], vs)

# ---------------------------------------------------------------- render markdown
F = lambda x, d=2: 'n/d' if x is None else f'{x:.{d}f}'
MARK = {'concorda': '=', 'arredondamento': '≈', 'diverge': '≠', 'ausente': '-'}

counts = {}
for c in CHECKS:
    counts.setdefault(c[3], {}).setdefault(c[5], 0)
    counts[c[3]][c[5]] += 1
tot = {}
for c in CHECKS:
    tot[c[5]] = tot.get(c[5], 0) + 1

w('<!-- gerado por audit.py; não editar à mão -->')
RANK = {'concorda': 0, 'arredondamento': 1, 'diverge': 2, 'ausente': 3}
uniq = {}
for c in CHECKS:
    k = (c[0], c[1])
    if k not in uniq or RANK[c[5]] < RANK[uniq[k]]:
        uniq[k] = c[5]
uc = {}
for v in uniq.values():
    uc[v] = uc.get(v, 0) + 1
w(f"Valores distintos da tese conferidos: **{len(uniq)}**. Melhor resultado em pelo menos uma fonte: "
  f"concorda {uc.get('concorda', 0)}, só arredondamento {uc.get('arredondamento', 0)}, "
  f"diverge em todas as fontes {uc.get('diverge', 0)}, sem fonte {uc.get('ausente', 0)}.")
w('')
for k, v in uniq.items():
    if v in ('diverge', 'ausente'):
        w(f'- sem confirmação ({v}): {k[0]} / {k[1]}')
w('')
w('### Contagem por fonte\n')
w('| Fonte | comparações | concorda | arredondamento | diverge | ausente |')
w('|---|---|---|---|---|---|')
for src, d in sorted(counts.items()):
    n = sum(d.values())
    w(f"| {src} | {n} | {d.get('concorda', 0)} | {d.get('arredondamento', 0)} | {d.get('diverge', 0)} | {d.get('ausente', 0)} |")
n = sum(tot.values())
w(f"| **Total** | **{n}** | **{tot.get('concorda', 0)}** | **{tot.get('arredondamento', 0)}** | **{tot.get('diverge', 0)}** | **{tot.get('ausente', 0)}** |")
w('')

# late fusion
w('### 1.3 Late fusion (tab:late_fusion, wFmax de validação, %)\n')
w('Fonte "repo": `source/nexus-go/results/chapter6/01_TABELAS_dedupmax.md`, Tabela 6.13 (campanha de 96 runs). '
  'Fonte "atual": BP e MF do mesmo arquivo do repo; CC de `late_fusion/ensemble_cc_novo.log` (bloco RESUMO). '
  'AVG recalculado como média simples de BP, CC e MF com os valores de 4 casas da fonte. '
  'Legenda: `=` concorda a 2 casas, `≈` difere só por arredondamento, `≠` diverge, `-` ausente.\n')
w('| Regra | BP tese | BP repo | CC tese | CC repo | CC log novo | MF tese | MF repo | AVG tese | AVG repo | AVG atual |')
w('|---|---|---|---|---|---|---|---|---|---|---|')
for name, c in late_rows:
    name = name.replace('\\gamma', 'γ')
    bp, cc, mf, av = c
    w(f'| {name} | {F(bp[0])} | {F(bp[1])} {MARK[bp[2]]} | {F(cc[0])} | {F(cc[1])} {MARK[cc[2]]} | {F(cc[3])} {MARK[cc[4]]} | '
      f'{F(mf[0])} | {F(mf[1])} {MARK[mf[2]]} | {F(av[0])} | {F(av[1])} {MARK[av[2]]} | {F(av[3])} {MARK[av[4]]} |')
w('')
w(f'Consistência interna: `resultados_novos_pos_CC_update/tabelas/01_TABELAS_dedupmax.md` (Tabela 6.13) '
  f'{"reproduz exatamente" if pos_consistent else "NÃO reproduz"} o log de CC e os valores BP/MF do repo, em validação e teste.\n')
w('Coeficientes selecionados (tab:ape_fusao_sel): γ, IC_thr, κ_IC, d_thr, κ_deg, λ (λ = `alpha` da regra mestra).\n')
w('| Ont | Fonte | tese | fonte | status |')
w('|---|---|---|---|---|')
for o, srcname, dv, vals, sts in coef_rows:
    w(f"| {o} | {srcname} | {', '.join(f'{x:g}' for x in dv)} | {', '.join(f'{x:g}' for x in vals)} | {' '.join(MARK[s] for s in sts)} |")
w('')

# test tables
w('### 1.4 Tabelas de teste (tab:confronto_bp/cc/mf)\n')
w('Fontes: "repo 07" = `source/nexus-go/results/chapter6/07_CONFRONTO_FINAL.md` (seção TESTE); '
  '"pós-CC 07" = `resultados_novos_pos_CC_update/tabelas/07_CONFRONTO_FINAL.md` (suplementar, mesma pasta do CSV); '
  '"CSV" = linha de teste do CSV de 170 runs para o campeão escolhido pelo wFmax de validação '
  '(First Generation: `results/ppi_only/ABLATIONS_summary.csv` do repo; Late: só wFmax de teste, do log de CC e da Tabela 6.13 do repo). '
  'Métricas ×100, Smin em bits. Cada célula mostra três marcas na ordem repo 07 / pós-CC 07 / CSV.\n')
for o in ONTS:
    w(f'**{o}**\n')
    w('| Método | Fmax | F*max | wFmax | AuPRC | IAuPRC | Smin |')
    w('|---|---|---|---|---|---|---|')
    for meth, cells in test_mats[o]:
        w(f'| {meth} | ' + ' | '.join(f'{F(c[0])} `{MARK[c[2]]}{MARK[c[4]]}{MARK[c[6]]}`' for c in cells) + ' |')
    w('')
w('Campeões (escolhidos em validação) usados na coluna CSV:\n')
for (o, meth), tag in champ_tags.items():
    w(f'- {o} {meth}: `{tag}`')
w('')

# cost
w('### 1.5 Custo (tab:custo, 147 runs na RTX A5500)\n')
w('CSV: famílias das 147 runs RTX A5500 do CSV de 170; s/época = mediana de `sec_per_epoch`; h/run = mediana de `wall_seconds`/3600; '
  'Total h = soma; VRAM = máximo de `peak_vram_mb`/1024; Épocas = mediana de `epochs_run`. '
  'Repo: Tabela 6.16 de `results/chapter6/01_TABELAS_dedupmax.md` (96 runs, mistura as duas GPUs, sem coluna s/época).\n')
w('| Família | Runs tese / CSV / repo | s/época tese / CSV | h/run tese / CSV / repo | Total h tese / CSV / repo | VRAM tese / CSV / repo | Épocas tese / CSV / repo |')
w('|---|---|---|---|---|---|---|')
for name, cells in cost_rows:
    parts = []
    for i, (dv, cv, sc, rv, sr, d) in enumerate(cells):
        if i == 1:
            parts.append(f'{F(dv, d)} / {F(cv, d)} {MARK[sc]}')
        else:
            parts.append(f'{F(dv, d)} / {F(cv, d)} {MARK[sc]} / {F(rv, d)} {MARK[sr]}')
    w(f'| {name} | ' + ' | '.join(parts) + ' |')
w(f'| Total | 147 / {len(rtx)} / {repo_total.group(2)} | | | 103.0 / {h(rtx):.1f} / {repo_total.group(1)} | | |')
w('')
w('Tabela A.6 (tab:ape_custo), CSV de 170 runs; `best_epoch` = época selecionada. Pico em MiB, wall em horas.\n')
w('| Família ou run | Runs | Pico MiB | Wall mediana | Wall máx. | Época sel. mediana | mín. | máx. |')
w('|---|---|---|---|---|---|---|---|')
for name, ref, calc, sts, decs in ape_rows:
    cells = []
    for rv, cv, s, d in zip(ref, calc, sts, decs):
        cells.append('' if rv is None else f'{F(rv, d)} / {F(cv, d if float(cv).is_integer() else max(d, 1))} {MARK[s] if s else ""}')
    w(f'| {name} | ' + ' | '.join(cells) + ' |')
w('')

# campaign accounting
w('### 1.6 Totais da campanha (texto da Seção 6 e Apêndice A.7)\n')
w('| Item | tese | CSV 170 | status |')
w('|---|---|---|---|')
for c in CHECKS:
    if c[0].startswith('Campanha'):
        w(f'| {c[1]} | {c[2]:g} | {c[4]:.2f} | {MARK[c[5]]} |')
w('')

# context
nctx = sum(1 for c in CHECKS if c[0].startswith('Contexto'))
w('### 1.7 Tabelas de contexto (validação), CSV de 170 runs\n')
w(f'Tabelas `hops_vector`, `hops_vision`, `alpha_vector`, `alpha_vision`, `gnn`, `early_grid`, `early_best`, `vector_vs_vision` '
  f'(células e colunas AVG): {nctx} valores conferidos. Exceções:\n')
if ctx:
    w('| Tabela | Célula | tese | CSV | status |')
    w('|---|---|---|---|---|')
    for t_, cell, dv, cv, s in ctx:
        w(f'| {t_} | {cell} | {dv} | {cv:.4f} | {MARK[s]} |')
else:
    w('nenhuma.')
w('')

# disagreement list
w('### 1.8 Lista completa de divergências e arredondamentos\n')
w('| Seção | Item | tese | Fonte | valor da fonte | status |')
w('|---|---|---|---|---|---|')
for c in CHECKS:
    if c[5] in ('diverge', 'arredondamento'):
        w(f"| {c[0]} | {c[1].replace(' | ', ' / ').replace(chr(92) + 'gamma', 'γ')} | {c[2]:g} | {c[3]} | {c[4]:.4f} | {c[5]} |")
w('')
w('Ausentes (sem valor na fonte):\n')
miss = {}
for c in CHECKS:
    if c[5] == 'ausente':
        miss.setdefault((c[3], c[0]), []).append(c[1])
for (src, sec), items in miss.items():
    meths = sorted({i.split(' | ')[0] for i in items})
    w(f'- {src}, {sec}: {len(items)} valores ({", ".join(meths)})')

OUT.write_text('\n'.join(out) + '\n', encoding='utf-8')
