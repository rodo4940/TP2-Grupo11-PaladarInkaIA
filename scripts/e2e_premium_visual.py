"""Diez capturas adicionales de la UI premium, ejecutadas contra React/FastAPI reales.

Sin datos inventados en las imágenes. Las fotografías externas se verifican mediante
naturalWidth: si el CDN falla, la prueba falla (no se presenta como evidencia visual).
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE=os.getenv('E2E_FRONTEND_URL','http://127.0.0.1:5173')
PASSWORD=os.environ['SEED_ADMIN_PASSWORD']
OUT=Path('e2e/evidencias')
MANIFEST=OUT/'e2e-results.json'
data=json.loads(MANIFEST.read_text(encoding='utf-8'))

def capture(page,num,slug,description):
    filename=f'{num:02d}_{slug}.png'
    page.screenshot(path=str(OUT/filename),animations='disabled',full_page=True)
    data['screenshots'].append({
        'file':filename,'step':description,
        'source':'Chromium real / React + FastAPI + PostgreSQL / QA ficticia',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
    })
    print('PREMIUM PROOF',filename,flush=True)

def signin(page):
    page.goto(BASE,wait_until='domcontentloaded')
    page.locator('input[autocomplete="username"]').fill('admin')
    page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
    page.get_by_role('button',name='Ingresar al sistema').click()
    expect(page.get_by_role('heading',name='Resumen operativo')).to_be_visible()

def nav(page,title,heading):
    menu=page.get_by_role('button',name='Abrir menú')
    if menu.is_visible():
        if 'sidebar-open' not in (page.locator('.sidebar').get_attribute('class') or ''):
            menu.click()
    page.locator('nav').get_by_role('button',name=title).click()
    expect(page.get_by_role('heading',name=heading,exact=True).first).to_be_visible()

def wait_photo(page,selector):
    locator=page.locator(selector).first
    expect(locator).to_be_visible()
    locator.evaluate("""el => new Promise((resolve,reject) => {
        if (el.complete) return el.naturalWidth>0 ? resolve(true) : reject(Error('Fotografía remota inválida'));
        el.addEventListener('load',()=>resolve(true),{once:true});
        el.addEventListener('error',()=>reject(Error('Fotografía remota no disponible')),{once:true});
    })""")

with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
    desktop=browser.new_context(viewport={'width':1536,'height':960},locale='es-PE')
    page=desktop.new_page();page.set_default_timeout(25000)
    page.goto(BASE)
    expect(page.get_by_role('heading',name='Bienvenido')).to_be_visible()
    wait_photo(page,'.login-hero-photo img')
    capture(page,91,'premium_login_fotografia','Inicio de sesión real con fotografía referencial efectivamente cargada')
    signin(page)
    wait_photo(page,'.banner-photo img')
    capture(page,92,'premium_dashboard_1536','Dashboard premium: indicadores reales y fotografía cargada')
    nav(page,'Ventas / POS','Nuevo pedido')
    assert page.locator('.product-card').count()>=4,'Faltan pizzas del catálogo semilla'
    page.wait_for_function("""() => [...document.querySelectorAll('.product-card img')].length>=4 && [...document.querySelectorAll('.product-card img')].every(el=>el.complete && el.naturalWidth>0)""",timeout=25000)
    capture(page,93,'premium_catalogo_fotos_reales','Cuatro tarjetas de pizzas con fotografías CDN verificadas y precios de API')
    page.locator('.product-card').first.click()
    capture(page,94,'premium_carrito_una_pizza','Carrito con suma al seleccionar una ficha visual')
    page.locator('.product-card').nth(1).click()
    capture(page,95,'premium_carrito_dos_pizzas','Carrito multirenglón y total calculado en frontend desde catálogo real')
    nav(page,'Productos y recetas','Productos y recetas')
    wait_photo(page,'.catalog-product-cell img')
    capture(page,96,'premium_catalogo_administracion','Mantenimiento de productos: miniaturas de referencia vinculadas por SKU')
    nav(page,'Cocina','Comandas de cocina')
    capture(page,97,'premium_kanban_cocina','Vista de cocina premium con datos persistidos de pedidos de prueba')
    tablet=browser.new_context(viewport={'width':1024,'height':768},locale='es-PE')
    tp=tablet.new_page();tp.set_default_timeout(25000)
    signin(tp);nav(tp,'Ventas / POS','Nuevo pedido')
    capture(tp,98,'premium_tablet_pos_1024','Adaptación de punto de venta a tableta de 1024 píxeles')
    mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=1,locale='es-PE')
    mp=mobile.new_page();mp.set_default_timeout(25000)
    signin(mp)
    capture(mp,99,'premium_dashboard_movil_390','Dashboard operativo real en móvil de 390 píxeles')
    nav(mp,'Ventas / POS','Nuevo pedido')
    wait_photo(mp,'.product-card img')
    capture(mp,100,'premium_pos_movil_fotografias','POS móvil real con tarjetas fotográficas y carrito responsive')
    browser.close()

data['screenshot_count']=len(data['screenshots'])
assert len(data['screenshots'])==100, f"Esperadas 100 capturas, obtenidas {len(data['screenshots'])}"
assert len({p['file'] for p in data['screenshots']})==100,'Capturas repetidas'
MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('TOTAL CAPTURAS ORIGINALES VERIFICADAS:',data['screenshot_count'],flush=True)
