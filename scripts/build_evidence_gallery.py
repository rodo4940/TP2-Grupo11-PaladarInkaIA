"""Genera galería auditable y manifiesto SHA256 desde capturas Playwright verdaderas.

Se ejecuta solo DESPUÉS de crear todos los PNG y pasar el workflow.
No genera pantallas, no maquilla resultados y falla ante evidencia faltante.
"""
from pathlib import Path
from datetime import datetime, timezone
from html import escape
from hashlib import sha256
import csv
import json
import os
import struct

ROOT=Path('e2e/evidencias')
obj=json.loads((ROOT/'e2e-results.json').read_text(encoding='utf-8'))
screens=obj['screenshots']
assert len(screens)==252, f'El lote no contiene 252 capturas: {len(screens)}'
seen=set()
records=[]
for item in screens:
    name=item['file']
    assert name == Path(name).name and name not in seen, f'Ruta o nombre no válido: {name}'
    seen.add(name)
    path=ROOT/name
    assert path.exists() and path.stat().st_size>1000, f'PNG inexistente o vacío: {name}'
    data=path.read_bytes()
    assert data[:8]==b'\x89PNG\r\n\x1a\n', f'Cabecera PNG inválida: {name}'
    width,height=struct.unpack('>II',data[16:24])
    assert width>=320 and height>=300, f'Resolución insuficiente: {name}'
    records.append({
        'n':int(name.split('_')[0]), 'file':name, 'titulo':item['step'],
        'width':width, 'height':height, 'bytes':len(data),
        'sha256':sha256(data).hexdigest(), 'timestamp_utc':item.get('timestamp_utc', 'no proporcionado'),
        'source':item.get('source', 'Chromium/Playwright sobre entorno de QA'),
    })
records.sort(key=lambda row:row['n'])
assert [r['n'] for r in records]==list(range(1,253)), 'No se encuentra numeración consecutiva 01-252'

with (ROOT/'MANIFIESTO_SHA256_252.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f,fieldnames=list(records[0]))
    writer.writeheader()
    writer.writerows(records)

report={
    'proyecto':'El Paladar del Inka · Taller de Proyectos 2',
    'tipo':'Evidencias reales de Chromium/Playwright sobre sistema QA',
    'cantidad_imagenes':252,
    'total_bytes':sum(r['bytes'] for r in records),
    'git_sha':os.getenv('GITHUB_SHA','ejecución local'),
    'generado_utc':datetime.now(timezone.utc).isoformat(),
    'integridad':'252 nombres de PNG distintos, cabecera válida, resolución mínima y SHA256 por archivo; las imágenes pueden repetirse visualmente',
    'limites':'Datos ficticios; no constituye UAT empresarial ni autorización de producción',
}
(ROOT/'REPORTE_EVIDENCIAS_252.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')

cards=[]
for r in records:
    file=escape(r['file'],quote=True)
    title=escape(r['titulo'])
    hash_short=r['sha256'][:12]
    cards.append('<article class="proof" data-search="'+escape((r['file']+' '+r['titulo']).lower(),quote=True)+'">'
       +'<a href="'+file+'" target="_blank" rel="noopener noreferrer"><img loading="lazy" src="'+file+'" alt="'+title+'"/></a>'
       +'<div class="details"><span class="proof-no">EVIDENCIA '+str(r['n']).zfill(3)+'</span>'
       +'<h2>'+title+'</h2><small>'+str(r['width'])+' × '+str(r['height'])+' px · SHA256 '+hash_short+'…</small>'
       +'<p><a href="'+file+'" target="_blank" rel="noopener noreferrer">Abrir captura original ↗</a></p></div></article>')
html='''<!doctype html><html lang="es"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>252 evidencias originales · Paladar Inka</title>
<style>
:root{font-family:system-ui,sans-serif;color:#20352b;background:#f7f5ef}
*{box-sizing:border-box}
body{margin:0}
header{padding:54px clamp(18px,6vw,90px);background:linear-gradient(110deg,#17372e,#32543b);color:#fff}
header h1{font-size:clamp(30px,5vw,54px);margin:8px 0 16px;letter-spacing:-.04em}
header p{max-width:850px;line-height:1.7;color:#d9e9dc}
header b{color:#ebca90}
main{max-width:1550px;margin:auto;padding:28px clamp(18px,4vw,55px)}
.toolbar{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:22px;flex-wrap:wrap}
input{border:1px solid #c8d1c7;background:#fff;border-radius:11px;padding:12px 15px;width:min(100%,410px);font:inherit}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(310px,1fr));gap:20px}
.proof{border-radius:16px;overflow:hidden;background:#fff;border:1px solid #e4e6de;box-shadow:0 8px 22px #253c2910}
.proof img{width:100%;aspect-ratio:16/10;object-fit:cover;object-position:top;display:block;background:#eff1ea}
.details{padding:20px}
.proof-no{font-size:10px;color:#ad5a36;font-weight:800;letter-spacing:.17em}
h2{font-size:16px;line-height:1.4;color:#24392d}
small{color:#66766b}
.details a{color:#a63439;font-weight:700}
code{color:#efd499}
footer{padding:30px 20px;background:#f0eee5;text-align:center;color:#59675d;font-size:12px}
</style></head><body>
<header><b>PALADAR INKA · QA AUDITABLE</b><h1>252 capturas originales del sistema</h1>
<p>Estas capturas se generaron mediante <strong>Chromium/Playwright</strong> sobre React, FastAPI y PostgreSQL con datos de laboratorio. Incluyen login, ventas, clientes, cocina, inventario, seguridad, diseños responsive y pruebas de interfaz. Consulta MANIFIESTO_SHA256_252.csv para verificar los archivos. <b>No acreditan aceptación de usuarios ni puesta en producción.</b></p>
<p>Commit CI: <code>'''+escape(report['git_sha'])+'''</code></p></header>
<main><div class="toolbar"><strong id="count">252 evidencias</strong><input id="query" type="search" aria-label="Buscar evidencias" placeholder="Buscar por pantalla, prueba o número..."/></div>
<section class="grid" id="grid">'''+''.join(cards)+'''</section></main>
<footer>Universidad Continental · Taller de Proyectos 2 · Galería generada desde archivos originales con SHA256</footer>
<script>
const q=document.getElementById('query'),cards=Array.from(document.querySelectorAll('.proof'));
q.addEventListener('input',()=>{
 const value=q.value.toLocaleLowerCase('es').trim();
 let count=0;
 cards.forEach(card=>{const show=card.dataset.search.includes(value);card.hidden=!show;if(show)count++});
 document.getElementById('count').textContent=count+' evidencias';
});
</script></body></html>'''
(ROOT/'GALERIA_252.html').write_text(html,encoding='utf-8')
print('GALERIA_252.html creada; 252 hashes SHA256 y archivos validados')
