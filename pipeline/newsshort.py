"""Render nieuwsshorts uit een JSON spec.
Gebruik: python3 newsshort.py spec.json outdir
spec: [{"id":"zorg-1123-s2","brand":"zorg"|"novins","scenes":[{"t":"hook","eyebrow":"Uit het nieuws","title":"...","icon":"alert"},{"t":"text","icon":"check","title":"...","body":"..."} of {"t":"stat","big":"4 uur","text":"...","src":"..."}]}]
Iconen: shield check mail laptop lock key eye book user users userx phone call wifi usb doc euro cloud server refresh clock bell list search printer qr home car trash alert chart target link chat flag award.
De afsluitende CTA scene wordt automatisch toegevoegd."""
import asyncio, json, pathlib, sys, engine
CTA = {"zorg": {"t": "cta", "title": "Hoe staat uw praktijk ervoor?", "body": "Doe de zelfcheck in twee minuten."},
       "novins": {"t": "cta", "title": "Vragen over uw situatie?", "body": "Wij denken praktisch met u mee."}}
spec = json.load(open(sys.argv[1]))
items = [dict(id=s["id"], brand=s["brand"], kind="short", scenes=s["scenes"] + [CTA[s["brand"]]]) for s in spec]
asyncio.run(engine.render_all(items, pathlib.Path(sys.argv[2])))
