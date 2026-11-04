import re, json, sys
src = open(sys.argv[1], encoding='utf-8').read()

def table_by_label(label):
    i = src.index('\\label{%s}' % label)
    a = src.rfind('\\begin{table}', 0, i)
    b = src.index('\\end{table}', i)
    return src[a:b]

def clean(cell):
    c = cell.strip()
    c = re.sub(r'\\textBF\{\$?([^}$]*)\$?\}', r'\1', c)
    c = re.sub(r'\\underline\{([^}]*)\}', r'\1', c)
    c = re.sub(r'\$\^\{\\mathrm\{[vs]\}\}\$', '', c)
    c = re.sub(r'\\textit\{n/a\}', 'n/a', c)
    c = re.sub(r'\\texttt\{([^}]*)\}', r'\1', c)
    c = c.replace('$','').replace('{,}',',').replace('\\%','%')
    c = re.sub(r'\\multirow\{\d+\}\{\*\}\{([^}]*)\}', r'\1', c)
    c = re.sub(r'\\,\\tiny\{\[\\textsc\{(\w)\}\]\}', r' [\1]', c)
    c = c.replace('\\geq','>=').replace('$-$','-').replace('-',"-")
    return c.strip()

def rows(tex):
    # a LaTeX row ends at \\ (optionally followed by [..]), not at a newline
    a = tex.find(r'\begin{tabular}'); b = tex.find(r'\end{tabular}')
    body = tex[a:b] if a >= 0 and b > a else tex
    body = '\n'.join(re.sub(r'(?<!\\)%.*', '', l) for l in body.split('\n'))
    body = re.sub(r'\\(top|mid|bottom)rule|\\hline|\\cmidrule(\([^)]*\))?\{[^}]*\}', ' ', body)
    body = re.sub(r'^\\begin\{tabular\}\{(?:[^{}]|\{[^{}]*\})*\}', '', body)
    out=[]
    for chunk in re.split(r'\\\\(?:\[[^\]]*\])?', body):
        chunk = re.sub(r'\s+', ' ', chunk.replace(r'\newline', ' ')).strip()
        if '&' not in chunk: continue
        out.append([clean(x) for x in chunk.split('&')])
    return out

def num(x):
    y = x.replace('%','')
    if re.fullmatch(r'-?\d{1,3}(,\d{3})+(\.\d+)?', y): y = y.replace(',', '')
    try: return float(y)
    except ValueError: return x

labels = {
 'naive':'tab:naive','loss':'tab:abl_perda','gen1_arch':'tab:abl_arquitetura','gen1_backbone':'tab:abl_backbone',
 'hops_vector':'tab:sweep_hops_vector','alpha_vector':'tab:sweep_alpha_vector',
 'hops_vision':'tab:sweep_hops_vision','alpha_vision':'tab:sweep_alpha_vision',
 'gnn':'tab:gnn_gcn_gat','dedup':'tab:dedup','early_best':'tab:early_fusion','early_grid':'tab:early_grid',
 'late':'tab:late_fusion','vector_vs_vision':'tab:vetor_visao_ontologia',
 'test_BP':'tab:confronto_bp','test_CC':'tab:confronto_cc','test_MF':'tab:confronto_mf',
 'cost':'tab:custo','isolated_vs_connected':'tab:degree_isolated_connected',
 'degree_f1_BP':'tab:degree_f1_bp','degree_f1_CC':'tab:degree_f1_cc','degree_f1_MF':'tab:degree_f1_mf',
 'graph_gain_by_degree':'tab:degree_graph_gain','degree_correlation':'tab:degree_correlation',
 'coverage':'tab:cobertura','corpus':'tab:cafa5','label_space':'tab:rotulos','graph_topology':'tab:grafo',
 'multiplicity':'tab:multiplicidade','hyperparams':'tab:ape_hp','fusion_grid':'tab:ape_fusao_grade',
 'fusion_selected':'tab:ape_fusao_sel','cost_runs':'tab:ape_custo','baselines_cost_coverage':'tab:ape_custo_comp',
 'machines':'tab:ape_maquinas','baselines_adapt':'tab:ape_baselines',
}
out={}
for k,l in labels.items():
    t=table_by_label(l)
    cap=re.search(r'\\caption\{(.*?)\}\s*\n?\s*\\label',t,re.S)
    out[k]={'label':l,'caption':re.sub(r'\s+',' ',cap.group(1)) if cap else '', 'rows':[[num(c) for c in r] for r in rows(t)], 'raw':rows(t)}
json.dump(out, open(sys.argv[2],'w',encoding='utf-8'), indent=1, ensure_ascii=False)
print(len(out),'tables')
for k in ['test_BP','late','graph_gain_by_degree','coverage']:
    print(k); [print('  ',r) for r in out[k]['rows']]
