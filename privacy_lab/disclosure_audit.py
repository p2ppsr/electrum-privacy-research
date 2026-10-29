"""Bounded English-language source and first-party messaging inventory, not a user study."""
import argparse
from datetime import datetime,timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import urllib.request

PIN="672df8f4512f6adf16a3c99146baa6be9b93d86f"
LATEST="35b92ec9ddb7575d453e35ed018fe106d9169b54"
TERMS=re.compile(r"privacy|surveillance|anonym|consent|disclos|retention|third.party",re.I)
REVIEWED={
    "README.rst":[(1,25),(40,65),(90,110)],
    "electrumsv/gui/qt/network_dialog.py":[(65,85),(270,307),(360,366),(581,589)],
    "electrumsv/data/text/misc/network-dialog.html":[(1,18)],
    "electrumsv/gui/qt/dialogs.py":[(131,157)],
    "electrumsv/gui/qt/wallet_wizard.py":[(64,76)],
    "electrumsv/gui/qt/account_wizard.py":[(147,198),(222,247)],
    "electrumsv/gui/qt/preferences.py":[(438,465)],
    "electrumsv/gui/qt/seed_dialog.py":[(48,64)],
    "electrumsv/gui/qt/app.py":[(394,420)],
    "electrumsv/data/text/wallet-wizard/release-notes.html":[(1,22)],
    "docs/standalone/index.rst":[(28,42)],
    "docs/standalone/getting-started/creating-a-wallet.rst":[(1,18),(37,58)],
    "docs/standalone/getting-started/receiving-a-payment.rst":[(1,38)],
    "electrumsv/network.py":[(1886,1909),(2006,2010)],
    "electrumsv/verification_utils.py":[(335,362),(380,405)],
    "electrumsv/exchange_rate.py":[(64,77)],
    "electrumsv/daemon.py":[(143,161)],
    "electrumsv/main.py":[(295,323)],
}


class Text(HTMLParser):
    def __init__(self):
        super().__init__();self.parts=[];self.hidden=0;self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag in ["script","style"]:self.hidden+=1
        if tag=="a":
            self.links.extend(v for k,v in attrs if k=="href")
    def handle_endtag(self,tag):
        if tag in ["script","style"]:self.hidden=max(0,self.hidden-1)
    def handle_data(self,text):
        if not self.hidden and text.strip():self.parts.append(text.strip())


def git(source,*args):
    return subprocess.check_output(["git","-C",str(source),*args])


def collect(source,output):
    output.mkdir(parents=True,exist_ok=False)
    result=dict(collected_at=datetime.now(timezone.utc).isoformat(),release_commit=PIN,
                latest_public_master_observed=LATEST,
                scope="English consumer docs, UI strings and relevant source; no packaged GUI usability study, interviews or awareness survey")
    paths=git(source,"ls-tree","-r","--name-only",PIN).decode().splitlines()
    paths=[p for p in paths if p=="README.rst" or p=="RELEASE-NOTES" or
           (p.startswith(("docs/standalone/","docs/website/content/","electrumsv/data/text/","electrumsv/gui/qt/")) and p.endswith((".rst",".md",".html",".py")))]
    hits=[]
    for path in paths:
        text=git(source,"show",f"{PIN}:{path}").decode()
        for n,line in enumerate(text.splitlines(),1):
            if TERMS.search(line):hits.append(dict(path=path,line=n,text=line[:400]))
    result.update(searched_source_file_count=len(paths),searched_paths=paths,term_pattern=TERMS.pattern,term_hits=hits)
    receipts=[]
    for path,ranges in REVIEWED.items():
        raw=git(source,"show",f"{PIN}:{path}")
        latest=git(source,"show",f"{LATEST}:{path}")
        lines=raw.decode().splitlines()
        receipts.append(dict(path=path,release_sha256=hashlib.sha256(raw).hexdigest(),
            latest_sha256=hashlib.sha256(latest).hexdigest(),unchanged_in_latest=raw==latest,
            source_url=f"https://github.com/TruthMachine/ElectrumSVP/blob/{PIN}/{path}",
            latest_url=f"https://github.com/TruthMachine/ElectrumSVP/blob/{LATEST}/{path}",
            excerpts=[dict(start=a,end=b,text="\n".join(lines[a-1:b])) for a,b in ranges]))
    result["source_receipts"]=receipts
    def pools(ref):
        import ast
        tree=ast.parse(git(source,"show",f"{ref}:electrumsv/network.py"))
        core=next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign)
                  and any(isinstance(t,ast.Name) and t.id=="priority_servers" for t in n.targets))
        tree=ast.parse(git(source,"show",f"{ref}:electrumsv/verification_utils.py"))
        helper=next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign)
                    and any(isinstance(t,ast.Name) and t.id=="SERVERS" for t in n.targets))
        a={h for h,_ in core};b=set(helper)
        return dict(core_hosts=sorted(a),helper_hosts=sorted(b),core_count=len(a),helper_count=len(b),
                    union_count=len(a|b),overlap_count=len(a&b))
    result["source_pool_version_comparison"]={PIN:pools(PIN),LATEST:pools(LATEST)}
    result["limits"]=["Search terms are discovery aids, not a proof of absence or automated disclosure-quality score",
                       "Negative findings are limited to reviewed surfaces; external translations, all past communications and private advice were not exhausted",
                       "No evidence about users' actual beliefs or comprehension was collected",
                       "A code/UI mismatch does not establish intent to deceive or actual covert collection"]
    (output/"source-audit.json").write_text(json.dumps(result,indent=2)+"\n")
    urls=["https://electrumsv.io/","https://electrumsv.io/articles/2026/electrumsvp-0_2_0.html",
          "https://electrumsv.io/articles/2026/electrumsvp-0_1_0.html",
          "https://electrumsv.readthedocs.io/",
          "https://electrumsv.readthedocs.io/en/sv-1.3.15/getting-started/creating-a-wallet.html",
          "https://electrumsv.readthedocs.io/en/sv-1.3.15/getting-started/receiving-a-payment.html"]
    pages=[]
    for url in urls:
        row=dict(url=url,at=datetime.now(timezone.utc).isoformat())
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 controlled privacy research"}),timeout=20) as response:
                raw=response.read()
                parser=Text();parser.feed(raw.decode())
                text="\n".join(parser.parts)
                row.update(status=response.status,final_url=response.url,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),
                    relevant_paragraphs=[p for p in parser.parts if TERMS.search(p)][:8],
                    privacy_or_terms_links=[v for v in parser.links if re.search(r"privacy|policy|terms",v,re.I)],
                    homepage_documentation_links=[v for v in parser.links if "readthedocs" in v],
                    excerpt_policy="Narrow paragraphs only; complete pages not republished")
        except Exception as exc:row["error"]=repr(exc)
        pages.append(row)
    (output/"public-pages.json").write_text(json.dumps(pages,indent=2)+"\n")
    print(json.dumps(dict(searched_source_files=len(paths),term_hits=len(hits),reviewed_source_receipts=len(receipts),
                          public_pages_ok=sum(r.get("status")==200 for r in pages)),indent=2))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();collect(a.source,a.output)


if __name__=="__main__":main()
