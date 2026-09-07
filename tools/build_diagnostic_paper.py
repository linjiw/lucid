"""Render the working Markdown to public HTML and an anonymous IEEE source."""
from pathlib import Path
import re
import shutil
import markdown

ROOT=Path(__file__).resolve().parents[1]
s=(ROOT/'paper/when-training-gets-easier.md').read_text()
html=markdown.markdown(s,extensions=['tables','fenced_code'])
(ROOT/'site/paper.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>When Training Gets Easier — working manuscript</title><style>body{max-width:960px;margin:3rem auto;padding:0 1.5rem;font:18px/1.6 Georgia,serif;color:#202c32}table{border-collapse:collapse;font:14px/1.4 sans-serif;width:100%}td,th{border:1px solid #ccd5d8;padding:.5rem}h1,h2,h3{line-height:1.2}pre{overflow:auto}a{color:#176b7b}</style></head><body><nav><a href="./">Project overview</a></nav>'''+html+'</body></html>')
# Escape text while preserving authored math and simple inline formatting.
def inline(text):
    stash=[]
    def hold(match):
        stash.append(match.group());return f'ZZMATH{len(stash)-1}ZZ'
    text=re.sub(r'\$[^$]+\$',hold,text)
    changes={'\\':r'\textbackslash{}','&':r'\&','%':r'\%','_':r'\_','#':r'\#','{':r'\{','}':r'\}',
             'λ':r'$\lambda$','≤':r'$\leq$','≥':r'$\geq$','∈':r'$\in$','×':r'$\times$','→':r'$\rightarrow$','−':'-','–':'--','—':'---','’':"'",'“':'``','”':"''"}
    text=''.join(changes.get(c,c) for c in text)
    text=re.sub(r'\*\*(.*?)\*\*',r'\\textbf{\1}',text)
    text=re.sub(r'`(.*?)`',r'\\texttt{\1}',text)
    text=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'\\emph{\1}',text)
    for i,value in enumerate(stash):text=text.replace(f'ZZMATH{i}ZZ',value)
    return text
figures={
 '9.':('mujoco_ladder','Historical exported policies in independently randomized MuJoCo, without pushes. Each point is a pass count over 32 physics draws; these are not 32 training seeds. At scale 2, paired fixed and never-shrink each pass 12/32, collapsed 5/32, and no DR 1/32. These are not the R1 checkpoints.'),
 '4.':('return_inversion','Terminal return versus frontier success AUC for twelve historical runs. Each point is one trained policy; the two collapsed runs have the highest returns. Descriptive Spearman correlation: -0.73.'),
 '5.':('paired_seeds','Three paired training seeds. The never-shrink versus fixed difference averages +0.60 points (SD 2.25); the empirical tolerance pass does not establish equivalence.'),
 '6.':('signal_audit','Fixed-difficulty signal audit. Dots are run-level rank correlations with iteration; horizontal marks are their means. Correlation with progress is not a recovery or fidelity guarantee.'),
 '8.':('retention_trajectory','One-origin, one-motion development continuation. Left: nominal global-error trajectories. Right: hard tracking qualification versus nominal error increase. Dashed lines mark the empirical 10 percent nominal budget only; the full retention gate also checks local error and original-envelope conditions. Each point uses 512 aliases per condition; trajectories are not independent training replicates.')}
s=re.sub(r'(?<=\S)\n(?=[A-Za-z$*])', ' ', s)
lines=s.splitlines();out=[];i=0;abstract=False;refs=False;pending_caption=None
while i<len(lines):
    line=lines[i]
    if line.startswith('# '):title=line[2:];i+=1;continue
    if line.startswith('**Working manuscript'):i+=1;continue
    if line=='## Abstract':out.append(r'\begin{abstract}');abstract=True;i+=1;continue
    if line.startswith('## '):
        if abstract:out.append(r'\end{abstract}');abstract=False
        heading=line[3:]
        if heading=='References':out.append(r'\section*{References}\small');refs=True
        else:
            out.append(r'\section{'+inline(re.sub(r'^\d+\.\s*','',heading))+'}')
            key=heading.split()[0]
            if key in figures:
                name,caption=figures[key];wide=name=='retention_trajectory';env='figure*' if wide else 'figure'
                out.append(r'\begin{'+env+r'}[t]\centering\includegraphics[width=\linewidth]{figures/'+name+r'.pdf}\caption{'+inline(caption)+r'}\end{'+env+'}')
        i+=1;continue
    if line.startswith('### '):out.append(r'\subsection{'+inline(re.sub(r'^\d+\.\d+\s*','',line[4:]))+'}');i+=1;continue
    if line.startswith('**Table '):
        pending_caption=inline(line);i+=1;continue
    if line.startswith('|'):
        rows=[]
        while i<len(lines) and lines[i].startswith('|'):
            r=[x.strip() for x in lines[i].strip('|').split('|')]
            if not all(re.fullmatch('[-: ]+',x) for x in r):rows.append(r)
            i+=1
        count=len(rows[0]);env='table*' if count>3 else 'table'
        out.append(r'\begin{'+env+r'}[t]\small')
        if pending_caption:
            out.append(pending_caption+r'\par\medskip');pending_caption=None
        out.append(r'\begin{tabularx}{\linewidth}{'+('X'*count)+r'}\hline')
        for j,row in enumerate(rows):out.append(' & '.join(inline(x) for x in row)+r' \\'+(r'\hline' if j==0 else ''))
        out.append(r'\hline\end{tabularx}\end{'+env+'}')
        continue
    if re.match(r'^\d+\. ',line):out.append(r'\noindent '+inline(line)+r'\par');i+=1;continue
    if refs and line.startswith('['):out.append(r'\noindent '+inline(line)+r'\par\medskip');i+=1;continue
    out.append(inline(line));i+=1
header=r'''\documentclass[letterpaper,10pt,conference]{ieeeconf}
\overrideIEEEmargins
\usepackage{amsmath,amssymb,graphicx,tabularx}
\usepackage{times}
\title{'''+inline(title)+r'''}
\author{Anonymous authors}
\begin{document}
\maketitle
\thispagestyle{empty}\pagestyle{empty}
'''
(ROOT/'paper/anonymous.tex').write_text(header+'\n'.join(out)+'\n'+r'\end{document}'+'\n')
print('Rendered working HTML and anonymous.tex')
