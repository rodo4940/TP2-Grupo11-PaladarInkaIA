"""Auditoría automatizada preliminar WCAG con axe-core en navegador real.

Reporta hallazgos (incluidos los pendientes) sin presentarla como certificación WCAG.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
from playwright.sync_api import sync_playwright, expect

base=os.environ.get('E2E_FRONTEND_URL','http://127.0.0.1:5173')
password=os.environ['SEED_ADMIN_PASSWORD']
axe=Path('frontend/node_modules/axe-core/axe.min.js')
if not axe.exists():raise SystemExit('Falta axe-core. Instalar en CI con npm install --no-save axe-core --prefix frontend')
out=Path('e2e/evidencias')
out.mkdir(parents=True,exist_ok=True)
report={'scope':'Axe-core en Chromium contra React/FastAPI/PostgreSQL de QA. NO certificación WCAG 2.1 AA','timestamp_utc':datetime.now(timezone.utc).isoformat(),'pages':[]}
with sync_playwright() as p:
    b=p.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
    page=b.new_page(viewport={'width':1440,'height':900},locale='es-PE')
    page.goto(base)
    def scan(label):
        page.add_script_tag(path=str(axe))
        data=page.evaluate('''async () => {const r=await window.axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}});return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,nodes:v.nodes.map(x=>({target:x.target,summary:x.failureSummary})).slice(0,12)})),incomplete:r.incomplete.map(v=>({id:v.id,impact:v.impact,nodes:v.nodes.length})),passes:r.passes.length}}''')
        severe=[x for x in data['violations'] if x['impact'] in ('critical','serious')]
        report['pages'].append({'name':label,**data,'severe_count':len(severe)})
        print('AXE',label,'violations',len(data['violations']),'serious/critical',len(severe),flush=True)
    scan('Acceso')
    page.locator('input[autocomplete="username"]').fill('admin')
    page.locator('input[autocomplete="current-password"]').fill(password)
    page.get_by_role('button',name='Ingresar al sistema').click()
    expect(page.get_by_role('heading',name='Resumen operativo')).to_be_visible()
    scan('Dashboard')
    for tab,heading in [('Ventas / POS','Nuevo pedido'),('Pedidos','Gestión de pedidos'),('Cocina','Comandas de cocina'),('Inventario / Kardex','Inventario y Kardex'),('Productos y recetas','Productos y recetas'),('Clientes','Clientes'),('Reportes de ventas','Reportes y análisis'),('Usuarios y roles','Usuarios y permisos')]:
        page.locator('nav').get_by_role('button',name=tab).click()
        expect(page.get_by_role('heading',name=heading,exact=True).first).to_be_visible()
        scan(tab)
    b.close()
report['total_violations']=sum(len(p['violations']) for p in report['pages'])
report['serious_or_critical']=sum(p['severe_count'] for p in report['pages'])
(out/'wcag_axe_preliminary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
# The report is the evidence. Explicitly fail severe issues until they are corrected.
assert report['serious_or_critical']==0,'Se detectaron incumplimientos severos WCAG; consultar wcag_axe_preliminary.json'