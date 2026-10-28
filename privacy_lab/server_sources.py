"""Retain public source-discovery receipts, immutable refs and narrow code facts."""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.parse

from .ownership import fetch


def gh(arguments):
    process=subprocess.run(["gh",*arguments],capture_output=True,text=True,timeout=40)
    row=dict(command=["gh",*arguments],observed_at=datetime.now(timezone.utc).isoformat(),exit_code=process.returncode)
    try:
        row["result"]=json.loads(process.stdout)
    except ValueError:
        row["stdout"]=process.stdout
    if process.stderr:
        row["stderr"]=process.stderr
    return row


def file_facts(repo,path,ref,needles):
    endpoint=f"repos/{repo}/contents/{path}?ref={ref}"
    row=gh(["api",endpoint])
    value=row.pop("result",{})
    if "content" not in value:
        row["result"]=value
        return row
    data=base64.b64decode(value["content"])
    text=data.decode()
    row.update(repository=repo,path=path,ref=ref,blob_sha=value["sha"],
        content_sha256=hashlib.sha256(data).hexdigest(),
        source_url=f"https://github.com/{repo}/blob/{ref}/{path}",
        matched_lines=[dict(line=i+1,text=line) for i,line in enumerate(text.splitlines()) if any(n in line for n in needles)])
    return row


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    def save(name,value):
        (args.output/name).write_text(json.dumps(value,indent=2)+"\n")
    profiles=[]
    for user in ["KeyvanJS","TruthMachine"]:
        profiles.append(gh(["api",f"users/{user}","--jq","{login,name,company,blog,bio,html_url}"]))
    profiles.append(gh(["api","orgs/bitails","--jq","{login,name,company,blog,description,html_url}"]))
    save("public-profiles.json",profiles)
    searches=[
        ["api","repos/KeyvanJS/ElectrumR"],
        ["api","repos/KeyvanJS/ElectrumR/releases"],
        ["api","users/KeyvanJS/repos?per_page=100","--jq","[.[]|{full_name,description,default_branch,fork}]"],
        ["search","repos","ElectrumR in:name fork:true","--visibility","public","--limit","100","--json","fullName,description,url"],
        ["search","code",'"electrumr.sock" is:public',"--limit","50","--json","repository,path,url"],
        ["search","code",'"ElectrumR" "SessionManager" is:public',"--limit","50","--json","repository,path,url"],
        ["api","-X","GET","search/code","-f",'q="electrumr_db" language:Rust is:public',"-f","per_page=50","--jq","{total_count,items:[.items[]|{repository:.repository.full_name,path,html_url}]}"],
        ["api","-X","GET","search/code","-f",'q="sv.electrumr.sv" language:Rust is:public',"-f","per_page=50","--jq","{total_count,items:[.items[]|{repository:.repository.full_name,path,html_url}]}"],
        ["search","repos","electrumx org:GorillaPool","--visibility","public","--limit","50","--json","fullName,description,url"],
    ]
    save("github-searches.json",[gh(query) for query in searches])
    metadata=[]
    for repo in ["bitails/electrumx-adaptor","kyuupichan/electrumx","spesmilo/electrumx","KeyvanJS/block-frontend"]:
        metadata.append(gh(["api",f"repos/{repo}","--jq","{full_name,html_url,default_branch,visibility,archived,description,license:.license.spdx_id}"]))
        branch="main" if repo.startswith("bitails/") else "master"
        metadata.append(gh(["api",f"repos/{repo}/commits/{branch}","--jq","{sha,date:.commit.committer.date,message:.commit.message}"]))
    metadata.append(gh(["api","repos/kyuupichan/electrumx/tags?per_page=100","--jq","[.[]|select(.name==\"1.20.2\" or .name==\"1.19.0\")|{name,sha:.commit.sha}]"]))
    metadata.append(gh(["api","repos/KeyvanJS/block-frontend/contents","--jq","[.[]|{name,type}] "]))
    save("repository-metadata.json",metadata)
    bitails="f184a1ad862ea37e93eec339de0c6cafa4e2cd36"
    code=[
        file_facts("bitails/electrumx-adaptor","src/tcp/tcp.service.ts",bitails,["SERVER_VERSION","ElectrumX 1.20.2","Welcome to Bitails","BLOCKCHAIN_SCRIPTHASH_SUBSCRIBE","scriptHashGetHistory","scripthashGetHistory","BITAILS"]),
        file_facts("bitails/electrumx-adaptor","src/bitails/api/bitails.api.service.ts",bitails,["API_ENDPOINT}/scripthash/","apikey:"]),
        file_facts("bitails/electrumx-adaptor",".env.sample",bitails,["BITAILS_API_ENDPOINT=","BITAILS_MAPI_ENDPOINT="]),
        file_facts("bitails/electrumx-adaptor","src/bitails/socket/bitails.socket.ts",bitails,["API_ENDPOINT}/global"]),
        file_facts("bitails/electrumx-adaptor","LICENSE",bitails,["MIT License","Copyright"]),
        file_facts("kyuupichan/electrumx","electrumx/__init__.py","8245608f847be7b186012246d638f90fdb7cec48",["version ="]),
        file_facts("kyuupichan/electrumx","electrumx/lib/coins.py","8245608f847be7b186012246d638f90fdb7cec48",["class BitcoinSV(","class BitcoinSVTestnet(","class BitcoinSVRegtest("]),
        file_facts("kyuupichan/electrumx","electrumx/__init__.py","918efa0ced96e0d64dad91a2c9abe1457a6facdf",["version ="]),
        file_facts("spesmilo/electrumx","README.md","280cb339aa158e099eb936033eecd15719770651",["Licence:","project is a fork", "dropped support"]),
    ]
    save("source-facts.json",code)
    additional=[]
    urls=["https://gitlab.com/api/v4/projects?search=ElectrumR&simple=true&per_page=100",
          "https://codeberg.org/api/v1/repos/search?q=ElectrumR&limit=50",
          "https://archive.softwareheritage.org/api/1/origin/"+urllib.parse.quote("https://github.com/KeyvanJS/ElectrumR",safe="")+"/get/"]
    for url in urls:
        row,data=fetch(url)
        if data:
            try:
                value=json.loads(data)
                if isinstance(value,list):
                    value=[{k:x.get(k) for k in ["path_with_namespace","web_url","description"]} for x in value]
                row["result"]=value
            except ValueError:
                row["parse_error"]="Response was not JSON; cannot establish archive/search absence."
        additional.append(row)
    save("additional-public-searches.json",additional)
    print(json.dumps(dict(directory=str(args.output),github_queries=len(searches),source_files=len(code))))


if __name__=="__main__":
    main()
