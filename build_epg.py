#!/usr/bin/env python3
"""Descarca EPG-urile Open-EPG, pastreaza doar canalele din playlist si scrie un singur epg.xml."""
import gzip, io, sys, urllib.request
import xml.etree.ElementTree as ET

SOURCES = sys.argv[1:] or [
    "https://www.open-epg.com/files/germany.xml",
    "https://www.open-epg.com/files/romania.xml",
]
OUTPUT = "epg.xml"

# ID-urile EPG folosite in tvg-id din playlist
WANT = {
    # Germania
    "ComedyCentral.de", "ProSiebenMAXX.de", "ProSieben.de", "SAT1.de", "KabelEins.de",
    "RTLZWEI.de", "VOX.de", "SAT1GOLD.de", "sixx.de", "KabelEinsDoku.de",
    # Romania
    "Antena1.ro", "ProTV.ro", "ProTVInternational.ro", "ProTVNews.ro",
    "Digi4K.ro", "Eurosport4K.ro", "LoveNature.ro",
}

def load(src):
    if src.startswith("http"):
        req = urllib.request.Request(src, headers={"User-Agent": "Mozilla/5.0"})
        data = urllib.request.urlopen(req, timeout=120).read()
    else:
        data = open(src, "rb").read()
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    return ET.parse(io.BytesIO(data)).getroot()

channels, progs = {}, []
for src in SOURCES:
    root = load(src)
    for c in root.findall("channel"):
        if c.get("id") in WANT:
            channels[c.get("id")] = c
    progs += [p for p in root.findall("programme") if p.get("channel") in WANT]

if not progs:
    sys.exit("Nu s-a gasit niciun program - nu suprascriu epg.xml")

progs.sort(key=lambda p: (p.get("channel"), p.get("start")))
out = ET.Element("tv", {"generator-info-name": "custom merge of Open-EPG"})
out.extend(channels[i] for i in sorted(channels))
out.extend(progs)
ET.indent(out)
ET.ElementTree(out).write(OUTPUT, encoding="UTF-8", xml_declaration=True)

have = {p.get("channel") for p in progs}
print(f"{len(channels)} canale, {len(progs)} programe")
for i in sorted(WANT - have):
    print("FARA PROGRAME:", i)
