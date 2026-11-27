"""Evidencia v6 de arqueo visual: 12 PNG reales en 4 resoluciones.

Requiere la suite completa anterior y datos de QA; no maquilla capturas ni
modifica saldos. La comparación de efectivo es visual y no constituye un
cierre de caja firmado ni comprobante tributario.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import struct
from playwright.sync_api import sync_playwright, expect

ROOT=Path('e2e/evidencias')
manifest=json.loads((ROOT/'e2e-results.json').read_text(encoding='utf-8'))
assert len(manifest['screenshots'])==240,'La suite v5 debe crear 240 PNG antes del arqueo v6'
BASE=os.getenv('E2E_FRONTEND_URL','http://127.0.0.1:5173')
PASSWORD=os.environ['SEED_ADMIN_PASSWORD']
viewports=[(320,720,'compacto320'),(390,844,'movil390'),(768,1024,'tablet768'),(1440,900,'escritorio1440')]
number=240
metrics=[]
errors=[]

def screenshot(page,slug,title):
    global number
    layout=page.evaluate("""() => ({
      viewport:innerWidth,doc:document.documentElement.scrollWidth,
      overflow:document.documentElement.scrollWidth>innerWidth+1
    })""")
    assert not layout['overflow'],(slug,layout)
    number+=1
    filename=f'{number:03d}_{slug}.png'
    page.screenshot(path=str(ROOT/filename),full_page=True,animations='disabled')
    with (ROOT/filename).open('rb') as f:head=f.read(24)
    assert head[:8]==b'\x89PNG\r\n\x1a\n',filename
    w,h=struct.unpack('>II',head[16:24])
    assert w==page.viewport_size['width'],f'Ancho fuera de viewport: {filename} ({w})'
    assert 500<=h<=23000,f'Altura fuera de límites: {filename} ({h})'
    manifest['screenshots'].append({
      'file':filename,'step':title,
      'viewport':page.viewport_size,
      'source':'Captura PNG directa de Chromium/Playwright, React/FastAPI/PostgreSQL y datos ficticios',
      'timestamp_utc':datetime.now(timezone.utc).isoformat()
    })
    metrics.append({'file':filename,'png_width':w,'png_height':h,'overflow':False})
    print('V6 CAJA',filename,'DIMENSIONES',w,h,flush=True)

with sync_playwright() as playwright:
    browser=playwright.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
    for w,h,slug in viewports:
        mobile=w<500
        context=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,has_touch=mobile,locale='es-PE',device_scale_factor=1,reduced_motion='reduce')
        page=context.new_page()
        page.set_default_timeout(35000)
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(BASE,wait_until='domcontentloaded')
        page.locator('input[autocomplete="username"]').fill('admin')
        page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
        page.get_by_role('button',name='Ingresar al sistema').click()
        expect(page.get_by_role('heading',name='¡Bienvenido a Paladar Inka AI!',exact=True)).to_be_visible()
        menu=page.get_by_role('button',name='Abrir menú')
        if menu.is_visible():menu.click()
        page.locator('nav').get_by_role('button',name='Finanzas / Caja').click()
        expect(page.get_by_role('heading',name='Resumen diario de caja')).to_be_visible()
        expect(page.locator('.cash-method-grid article')).to_have_count(4)
        expect(page.locator('.cash-closeout-total strong')).to_be_visible()
        date_field=page.get_by_label('Fecha del resumen de caja')
        original_day=date_field.input_value()
        assert len(original_day)==10
        screenshot(page,slug+'_resumen_caja','Resumen de cobros por cuatro medios de pago, fecha Perú y ticket')
        date_field.fill('2020-01-01')
        expect(page.locator('.cash-closeout-total strong')).to_have_text('S/ 0.00')
        screenshot(page,slug+'_consulta_historica','Consulta día sin operaciones con cero cobros y cero mutaciones')
        date_field.fill(original_day)
        expect(page.locator('.cash-closeout-total strong')).not_to_have_text('S/ 0.00')
        page.get_by_label('Efectivo contado en caja (S/)').fill('0.00')
        expect(page.locator('.cash-variance strong')).to_be_visible()
        screenshot(page,slug+'_arqueo_diferencia','Comparación manual de efectivo con registros de caja y diferencia en PEN')
        if mobile:
            expect(page.get_by_role('navigation',name='Navegación rápida móvil')).to_be_visible()
        else:
            expect(page.locator('.mobile-dock')).to_be_hidden()
        context.close()
    browser.close()

assert number==252 and len(manifest['screenshots'])==252
assert len({x['file'] for x in manifest['screenshots']})==252
assert not errors,errors
manifest['screenshot_count']=252
(ROOT/'e2e-results.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'caja-v6-results.json').write_text(json.dumps({
    'new_screenshots':12,'total_screenshots':252,'viewports':viewports,
    'metrics':metrics,'browser_errors':errors,
    'scope':'Resumen de caja y arqueo visual de demostración. No constituye cierre firmado ni emisión tributaria.'
},ensure_ascii=False,indent=2),encoding='utf-8')
print('V6 PASO: 12 nuevas capturas reales; 252 total. Cero overflow y errores JS.',flush=True)
