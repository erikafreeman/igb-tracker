#!/usr/bin/env python3
"""Self-contained weekly generator for the Awards & Funding Plan page (awards.html).
Runs in GitHub Actions: reads awards_funding.yaml, recomputes countdowns from TODAY,
and writes awards.html. No external project files needed."""
import datetime, html, re
import yaml

today = datetime.date.today()
ICON = {"funding":"💶","award":"🏆","paper":"📝","service":"🤝"}

def next_date(it):
    if it.get("rolling"): return None,"rolling"
    if "deadline" in it:
        s=str(it["deadline"]); s=s if len(s)==10 else (s+"-15" if len(s)==7 else s)
        d=datetime.date.fromisoformat(s); return d,d.isoformat()
    if "annual_month" in it:
        m=int(it["annual_month"]); y=today.year if (today.month,today.day)<=(m,15) else today.year+1
        d=datetime.date(y,m,15); return d,f"~{d.strftime('%b %Y')} (annual)"
    return None,"TBC"

items=yaml.safe_load(open("awards_funding.yaml"))["items"]
rows=[]
for it in items:
    d,lbl=next_date(it); rows.append({**it,"_d":d,"_l":lbl,"_n":((d-today).days if d else None)})

def rowhtml(r,days=True):
    ic=ICON.get(r["type"],"•"); nom=" <i>(nomination)</i>" if r.get("nomination") else ""
    st=f" — <i>{html.escape(str(r.get('status','')))}</i>" if r.get("status") else ""
    nt=f" — {html.escape(str(r['note']))}" if r.get("note") else ""
    dd=""
    if days and r["_n"] is not None:
        dd=f" <b>[{r['_n']}d]</b>" if r["_n"]>=0 else " <b>[PASSED]</b>"
    return f"<tr><td>{ic}</td><td><b>{html.escape(r['name'])}</b>{nom}</td><td>{html.escape(r['_l'])}{dd}</td><td>{html.escape(r['type'])}{st}{nt}</td></tr>"

def tbl(rs,days=True):
    if not rs: return "<p><i>(none)</i></p>"
    h="<tr><th></th><th>Item</th><th>Next date</th><th>Type / status / note</th></tr>"
    return '<div class="tw"><table>'+h+"".join(rowhtml(r,days) for r in rs)+"</table></div>"

dated=sorted([r for r in rows if r["_d"]],key=lambda r:r["_d"])
u14=[r for r in dated if r["_n"] is not None and 0<=r["_n"]<=14]
u90=[r for r in dated if r["_n"] is not None and 0<=r["_n"]<=90]
fund=sorted([r for r in rows if r["type"]=="funding"],key=lambda r:(r["_d"] or datetime.date(2999,1,1)))
awd=sorted([r for r in rows if r["type"]=="award"],key=lambda r:(r["_d"] or datetime.date(2999,1,1)))
roll=[r for r in rows if r["_d"] is None]

STYLE=""":root{--ink:#13415e;--accent:#1d6fa5;--line:#d6e2ec}*{box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;max-width:1100px;margin:0 auto;padding:24px 28px 60px;color:#1a2733;line-height:1.5}h1{font-size:1.7rem;color:var(--ink);border-bottom:3px solid var(--accent);padding-bottom:.3em}h2{font-size:1.2rem;color:var(--ink);margin-top:1.8em;border-bottom:1px solid var(--line);padding-bottom:.2em}.tw{overflow-x:auto;margin:1em 0}table{border-collapse:collapse;width:100%;font-size:.86rem;min-width:540px}th{background:var(--ink);color:#fff;text-align:left;padding:7px 9px}td{border:1px solid var(--line);padding:7px 9px;vertical-align:top}tr:nth-child(even) td{background:#f4f8fb}blockquote{background:#eaf4fb;border-left:4px solid var(--accent);margin:1em 0;padding:.7em 1em;border-radius:0 4px 4px 0}a{color:var(--accent)}.upd{display:inline-block;background:#e8f5e9;color:#1b5e20;border:1px solid #a5d6a7;border-radius:12px;padding:2px 10px;font-size:.78rem;font-weight:600}"""

doc=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>Awards &amp; Funding Plan — Dr. Erika C. Freeman</title><style>{STYLE}</style></head><body>
<span class="upd">AUTO-REFRESHED WEEKLY · last refreshed {today.isoformat()}</span>
<h1>Awards &amp; Funding Plan — Dr. Erika C. Freeman</h1>
<blockquote>Regenerated every Monday by a GitHub Action from <code>awards_funding.yaml</code>. <code>[Nd]</code> = days until deadline. Linked from the <a href="./">tracker</a>. Confirm every deadline on the funder's site.</blockquote>
<h2>⏰ Due in the next 14 days</h2>{tbl(u14)}
<h2>📅 Next 90 days</h2>{tbl(u90)}
<h2>💶 Funding pipeline (by next deadline)</h2>{tbl(fund)}
<h2>🏆 Awards &amp; prizes to pursue <small>(most need a nominator)</small></h2>{tbl(awd,False)}
<h2>🔁 Rolling / no fixed deadline</h2>{tbl(roll,False)}
</body></html>"""
open("awards.html","w",encoding="utf-8").write(doc)
print(f"wrote awards.html ({len(doc)} bytes; {len(u14)} due <=14d)")
