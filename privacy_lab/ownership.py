"""Collect bounded public infrastructure/attribution evidence; no identity guesses.

Registry output is reduced to network/domain/organization facts. Personal street
addresses, telephone numbers, and mailbox details are deliberately not retained.
Certificates are public server certificates, never private keys.
"""
import argparse
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import html
from html.parser import HTMLParser
import ipaddress
import json
from pathlib import Path
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request

from asn1crypto import x509
import certifi
import dns.resolver

UA = "Mozilla/5.0 (compatible; ElectrumPrivacyResearch/1.0; public-source-attribution)"


def now():
    return datetime.now(timezone.utc).isoformat()


def fetch(url):
    receipt = dict(url=url, observed_at=now())
    try:
        request = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(request, timeout=18,
                context=ssl.create_default_context(cafile=certifi.where())) as response:
            data = response.read(4*1024*1024)
            receipt.update(status=response.status, final_url=response.url,
                           bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
            return receipt, data
    except Exception as exc:
        receipt.update(error=repr(exc), status=getattr(exc, "code", None))
        return receipt, b""


def organizations(entities):
    result = []
    for entity in entities:
        fields = {row[0]:row[3] for row in entity.get("vcardArray", [None, []])[1]}
        # Published network/registrar organizations only; discard contact fields.
        result.append(dict(handle=entity.get("handle"), roles=entity.get("roles"),
            kind=fields.get("kind"), name=None if fields.get("kind")=="individual" else fields.get("fn"), organization=fields.get("org"),
            links=[x.get("href") for x in entity.get("links", [])]))
    return result


def rdap_record(url):
    receipt,data = fetch(url)
    if data:
        try:
            value = json.loads(data)
            keep = ["handle","name","ldhName","startAddress","endAddress","ipVersion",
                    "type","country","parentHandle","cidr0_cidrs","startAutnum","endAutnum",
                    "events","status","links","port43"]
            receipt["registry_facts"] = {k:value[k] for k in keep if k in value}
            receipt["registry_facts"]["organizations"] = organizations(value.get("entities", []))
            receipt["registry_facts"]["nameservers"] = [n.get("ldhName") for n in value.get("nameservers", [])]
            receipt["filtered"] = "Contact addresses, phone numbers and mailboxes omitted. Registry holder is not necessarily the application operator."
        except Exception as exc:
            receipt["parse_error"] = repr(exc)
    return receipt


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.text, self.skip = [], [], 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        for key,value in attrs:
            if tag == "a" and key == "href" and value:
                self.links.append(value)
    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0,self.skip-1)
    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)


def website(url):
    receipt,data = fetch(url)
    if data:
        parser = Links()
        parser.feed(data.decode(errors="replace"))
        text = " ".join(" ".join(parser.text).split())
        links=set(urllib.parse.urljoin(receipt.get("final_url",url), v) for v in parser.links)
        receipt["links"] = sorted(link for link in links if any(marker in link.lower() for marker in
            ["github.com/","/about","/contact","/privacy","/terms","/support","t.me/","twitter.com/","x.com/","electrumr","docs."]))
        # Small evidence quotes only, not a republication of the site's prose.
        quotes = []
        for phrase in ["Satoshi.io runs nodes", "GorillaPool operates ElectrumX", "To access the ESV server"]:
            position = text.find(phrase)
            if position >= 0:
                quotes.append(" ".join(text[position:].split()[:20]))
        receipt["short_operator_quotes"] = quotes
    return receipt


def zone(domain):
    result = dict(domain=domain, observed_at=now(), records=[])
    for typ in ["A","AAAA","NS","SOA","MX","CAA"]:
        try:
            answer = dns.resolver.resolve(domain,typ,lifetime=5,raise_on_no_answer=False)
            if answer.rrset:
                result["records"].append(dict(type=typ,ttl=answer.rrset.ttl,values=[r.to_text() for r in answer]))
        except Exception as exc:
            result.setdefault("errors",[]).append(dict(type=typ,error=repr(exc)))
    return result


def tls(host):
    result = dict(host=host,port=50002,observed_at=now(),certificate_identity_authenticated=False)
    try:
        context=ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname=False
        context.verify_mode=ssl.CERT_NONE
        with socket.create_connection((host,50002),timeout=7) as raw:
            with context.wrap_socket(raw,server_hostname=host) as stream:
                der=stream.getpeercert(binary_form=True)
                result.update(peer=stream.getpeername(),tls=stream.version(),certificate_sha256=hashlib.sha256(der).hexdigest())
        cert=x509.Certificate.load(der)
        tbs=cert["tbs_certificate"]
        result.update(subject=tbs["subject"].native,issuer=tbs["issuer"].native,
            validity={k:v.isoformat() for k,v in tbs["validity"].native.items()},
            spki_sha256=hashlib.sha256(tbs["subject_public_key_info"].dump()).hexdigest())
        result["subject_alternative_names"]=[]
        for extension in tbs["extensions"]:
            if extension["extn_id"].native == "subject_alt_name":
                result["subject_alternative_names"]=extension["extn_value"].parsed.native
    except Exception as exc:
        result["error"]=repr(exc)
    return result


def reverse(ip):
    result=dict(ip=ip,observed_at=now())
    try:
        result["ptr"]=socket.gethostbyaddr(ip)[0]
    except Exception as exc:
        result["error"]=repr(exc)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    def save(name,value):
        (args.output/name).write_text(json.dumps(value,indent=2,default=str)+"\n")
    previous=json.loads(Path("evidence/destinations-20261028/dns.json").read_text())
    hosts=[r["host"] for r in previous]
    ips=sorted({ip for r in previous for ip in r["addresses"]})
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        save("tls-certificates.json",list(executor.map(tls,hosts)))
        save("reverse-dns.json",list(executor.map(reverse,ips)))
        domains=["satoshi.io","electrumr.io","electrumr.sv","server.sv","gorillapool.io","bitails.io","aftrek.org"]
        save("dns-zones.json",list(executor.map(zone,domains)))
        pages=["https://satoshi.io/","https://satoshi.io/about","https://electrumr.io/index.html",
               "https://electrumr.io/docs.html","https://docs.gorillapool.io/electrumsv/",
               "https://docs.bitails.io/","https://bitails.io/","https://bsv.aftrek.org/",
               "https://electrumsv.io/articles/2021/electrumsv-1_3_13.html"]
        save("official-websites.json",list(executor.map(website,pages)))
    bootstrap={}
    receipts=[]
    for kind in ["ipv4","ipv6","dns"]:
        receipt,data=fetch(f"https://data.iana.org/rdap/{kind}.json")
        receipts.append(receipt)
        bootstrap[kind]=json.loads(data) if data else {}
    save("iana-bootstrap.json",receipts)
    def ip_url(ip):
        address=ipaddress.ip_address(ip)
        family="ipv4" if address.version==4 else "ipv6"
        entries=[(ipaddress.ip_network(prefix),bases[0]) for prefixes,bases in bootstrap[family].get("services",[]) for prefix in prefixes if address in ipaddress.ip_network(prefix)]
        return max(entries,key=lambda e:e[0].prefixlen)[1]+"ip/"+ip if entries else None
    # One sample per distinct non-shared network plus a representative of the /24.
    representative=["198.154.93.197","128.140.53.204","49.13.228.56","99.127.49.102","2a01:4f8:c17:3e4c::1"]
    urls=[ip_url(ip) for ip in representative]
    urls.append("https://rdap.arin.net/registry/autnum/55286")
    for domain in domains:
        tld=domain.rsplit(".",1)[1]
        services=[bases[0] for tlds,bases in bootstrap["dns"].get("services",[]) if tld in tlds]
        if services:
            urls.append(services[0]+"domain/"+domain)
        else:
            receipts.append(dict(domain=domain,error="No domain RDAP endpoint found in IANA bootstrap"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        save("rdap.json",list(executor.map(rdap_record,[url for url in urls if url])))
        requests=["https://stat.ripe.net/data/network-info/data.json?resource="+urllib.parse.quote(ip,safe="") for ip in representative]
        requests.append("https://stat.ripe.net/data/prefix-overview/data.json?resource=198.154.93.0%2F24")
        def ripe(url):
            receipt,data=fetch(url)
            if data:
                receipt["reported_data"]=json.loads(data).get("data")
            return receipt
        save("routing.json",list(executor.map(ripe,requests)))
    save("iana-bootstrap.json",receipts)
    print(json.dumps(dict(directory=str(args.output),tls_hosts=len(hosts),domains=len(domains),network_samples=len(representative))))


if __name__=="__main__":
    main()
