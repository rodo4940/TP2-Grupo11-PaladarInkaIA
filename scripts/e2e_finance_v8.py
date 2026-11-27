"""16 evidencias reales en Chromium del módulo financiero v8 con QA FICTICIA.

4 estados x 4 viewports. Cambios de estado creados por API real FastAPI sobre
PostgreSQL de CI. NO prueba movimiento de dinero ni aceptación comercial.
"""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from hashlib import sha256
from html import escape
import json
import os
import struct
import httpx
from playwright.sync_api import sync_playwright, expect

API='http://127.0.0.1:8000/api/v1'
WEB=os.getenv('E2E_FRONTEND_URL','http://127.0.0.1:5173')
PASSWORD=os.environ['SEED_ADMIN_PASSWORD']
OUT=Path('e2e/finance-v8')
OUT.mkdir(parents=True,exist_ok=True)
SIZES=[(320,720),(390,844),(768,1024),(1440,900)]
captures=[]
js_errors=[]


def call(client, method, path, token, payload=None):
    res=client.request(method,API+path,headers={'Authorization':'Bearer '+token},
                       json=payload,timeout=30)
    assert 200<=res.status_code<300,(path,res.status_code,res.text[:600])
    return res.json()


def browser_capture(page, slug, state):
    layout=page.evaluate("""() => ({
      viewport:window.innerWidth, document:document.documentElement.scrollWidth,
      overflow:document.documentElement.scrollWidth>window.innerWidth+1
    })""")
    assert not layout['overflow'],(slug,layout)
    filename=f'{len(captures)+1:03d}_{slug}.png'
    path=OUT/filename
    page.screenshot(path=str(path),full_page=False,animations='disabled')
    raw=path.read_bytes()
    assert raw[:8]==b'\x89PNG\r\n\x1a\n'
    w,h=struct.unpack('>II',raw[16:24])
    assert (w,h)==(page.viewport_size['width'],page.viewport_size['height'])
    captures.append({'file':filename,'state':state,'sha256':sha256(raw).hexdigest(),
                     'width':w,'height':h,'overflow':False})
    print('V8 FINANCE',filename,w,h,flush=True)


def capture_state(playwright, state):
    browser=playwright.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
    for w,h in SIZES:
        mobile=w<500
        context=browser.new_context(viewport={'width':w,'height':h},is_mobile=mobile,
                            has_touch=mobile,locale='es-PE',device_scale_factor=1,
                            reduced_motion='reduce')
        page=context.new_page()
        page.set_default_timeout(30000)
        page.on('pageerror',lambda error: js_errors.append(str(error)))
        page.goto(WEB,wait_until='domcontentloaded')
        page.locator('input[autocomplete="username"]').fill('admin')
        page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
        page.get_by_role('button',name='Ingresar al sistema').click()
        expect(page.get_by_role('heading',name='Resumen operativo',exact=True)).to_be_visible()
        if w<=880:
            page.get_by_role('button',name='Abrir menú').click()
        page.locator('nav').get_by_role('button',name='Caja y comprobantes',exact=True).click()
        expect(page.get_by_role('heading',name='Caja y comprobantes',exact=True)).to_be_visible()
        if state in ('refund_pending','refund_confirmed'):
            heading=page.get_by_role('heading',name='Devoluciones de pagos')
            expect(heading).to_be_visible()
            request=page.locator('.billing-entry').filter(has_text='Solicitud #').first
            expect(request).to_be_visible()
            expected='Pendiente de confirmación' if state=='refund_pending' else 'Confirmación manual'
            expect(request).to_contain_text(expected)
            request.scroll_into_view_if_needed()
        else:
            heading=page.get_by_role('heading',name='Arqueo registrado')
            expect(heading).to_be_visible()
            panel=heading.locator('xpath=..')
            expected='Pendiente de aprobación' if state=='closeout_submitted' else 'Aprobado internamente'
            expect(panel).to_contain_text(expected)
            panel.scroll_into_view_if_needed()
        browser_capture(page,f'{w}_{state}',state)
        context.close()
    browser.close()


with httpx.Client() as client:
    admin=client.post(API+'/auth/token',
                      json={'username':'admin','password':PASSWORD},timeout=30)
    assert admin.status_code==200,admin.text
    admin_token=admin.json()['access_token']
    users=call(client,'GET','/users',admin_token)
    cashier_name='cajero_v8_qa'
    cashier_password='SoloQA_Caja_Ficticia_2026'
    if not any(u['username']==cashier_name for u in users):
        call(client,'POST','/users',admin_token,{
           'username':cashier_name,'full_name':'Caja QA sin datos reales',
           'role':'cashier','password':cashier_password})
    cashier=client.post(API+'/auth/token',
                       json={'username':cashier_name,'password':cashier_password},timeout=30)
    assert cashier.status_code==200,cashier.text
    cashier_token=cashier.json()['access_token']
    ledger=call(client,'GET','/billing/ledger',cashier_token)
    eligible=[entry for entry in ledger['entries'] if not entry.get('refund_status')]
    assert eligible,'Se necesita un pago ficticio del e2e_browser.py'
    payment_id=eligible[0]['id']
    refund=call(client,'POST','/billing/refunds',cashier_token,{
         'payment_id':payment_id,'reason':'QA: simulación de reintegro, sin dinero real'})
    assert refund['status']=='pending'
    with sync_playwright() as playwright:
        capture_state(playwright,'refund_pending')
        confirmed=call(client,'POST',f"/billing/refunds/{refund['id']}/confirm",admin_token,
                       {'external_reference':'QA-REINTEGRO-FICTICIO-SIN-TRANSFERENCIA'})
        assert confirmed['status']=='confirmed'
        capture_state(playwright,'refund_confirmed')
        day=datetime.now(ZoneInfo('America/Lima')).date().isoformat()
        closeout=call(client,'POST','/billing/closeouts',cashier_token,{
          'day':day,'opening_cash_cents':1000,'counted_cash_cents':1000,
          'note':'Ejercicio QA sin efectivo ni vouchers reales'})
        assert closeout['state']=='submitted'
        capture_state(playwright,'closeout_submitted')
        approved=call(client,'POST',f"/billing/closeouts/{closeout['id']}/approve",admin_token,{
          'approval_note':'Validación QA exclusivamente sintética: no autoriza operaciones reales'})
        assert approved['state']=='approved'
        capture_state(playwright,'closeout_approved')

assert len(captures)==16,(len(captures),16)
assert not js_errors,js_errors
result={'count':len(captures),'widths':[x[0] for x in SIZES],
        'states':['refund_pending','refund_confirmed','closeout_submitted','closeout_approved'],
        'source':'Capturas reales Chromium/React/FastAPI/PostgreSQL con datos ficticios de CI',
        'commercial_uat':'NO EJECUTADO',
        'generated_utc':datetime.now(timezone.utc).isoformat(),
        'git_sha':os.getenv('GITHUB_SHA','no indicado'),'javascript_errors':js_errors,
        'captures':captures}
(OUT/'RESULTADOS_CAJA_V8.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'MANIFIESTO_SHA256_16.csv').open('w',encoding='utf-8') as f:
    f.write('archivo,estado,ancho,alto,sha256\n')
    for entry in captures:
        f.write(f"{entry['file']},{entry['state']},{entry['width']},{entry['height']},{entry['sha256']}\n")
cards=[]
for item in captures:
    name=escape(item['file'],quote=True)
    cards.append('<article><a href="'+name+'"><img loading="lazy" src="'+name+'" alt="'+name+'"></a>'
                '<p><b>'+name+'</b></p><small>SHA-256 '+item['sha256']+'</small></article>')
html='''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Evidencia caja v8</title><style>body{font:14px system-ui;margin:0;background:#f5f5f1;color:#254d39}header{padding:32px;background:#1b4e39;color:#fff}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;padding:22px}article{padding:10px;background:white;border-radius:12px;min-width:0}img{width:100%;height:300px;object-fit:contain}small{display:block;overflow-wrap:anywhere;font-size:10px}</style></head><body><header><h1>16 capturas reales de caja v8</h1><p>4 estados × 4 resoluciones, hashes completos y 0 overflow. Datos sintéticos en CI; SIN UAT empresarial, SIN emisión SUNAT o transferencia real.</p></header><main>'''+''.join(cards)+'''</main></body></html>'''
(OUT/'GALERIA_CAJA_V8.html').write_text(html,encoding='utf-8')
print('V8 FINANCE: 16 CAPTURAS REALES, 0 OVERFLOW, SHA-256',flush=True)
