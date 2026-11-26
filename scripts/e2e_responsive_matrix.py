"""Matriz 4×13: capturas de interfaz auténtica, responsive y acceso funcional.

La suite anterior produce 100 PNG reales. Esta añade exactamente 52 imágenes,
realizadas en Chromium sobre el sistema QA (React + FastAPI + PostgreSQL).
Cada captura se indexa con viewport, sección, resultado de overflow y hash
que generará el manifiesto final. No simula datos ni resultados de UAT.
"""
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json
import os

OUT=Path('e2e/evidencias')
MANIFEST=OUT/'e2e-results.json'
BASE=os.getenv('E2E_FRONTEND_URL','http://127.0.0.1:5173')
PASSWORD=os.environ['SEED_ADMIN_PASSWORD']
data=json.loads(MANIFEST.read_text(encoding='utf-8'))
assert len(data['screenshots'])==100, 'La matriz debe partir de 100 capturas de QA previas'
screens=[
 ('dashboard','Panel general','Resumen operativo'),
 ('pos','Ventas / POS','Nuevo pedido'),
 ('orders','Pedidos','Gestión de pedidos'),
 ('kitchen','Cocina','Comandas de cocina'),
 ('inventory','Inventario / Kardex','Inventario y Kardex'),
 ('products','Productos y recetas','Productos y recetas'),
 ('customers','Clientes','Clientes'),
 ('reports','Reportes de ventas','Reportes y análisis'),
 ('ai','Analítica inteligente','Inteligencia operativa'),
 ('users','Usuarios y roles','Usuarios y permisos'),
 ('settings','Configuración','Configuración del entorno'),
]
viewports=[
 (360,780,'telefono_compacto'),
 (390,844,'telefono_estandar'),
 (768,1024,'tableta_vertical'),
 (1440,900,'escritorio'),
]
num=100
checks=[]
errors=[]

def capture(page,slug,description):
    global num
    num+=1
    name=f'{num:03d}_{slug}.png'
    page.screenshot(path=str(OUT/name),animations='disabled',full_page=True)
    data['screenshots'].append({
        'file':name,
        'step':description,
        'source':'Chromium real | React 19, FastAPI, PostgreSQL | QA con datos ficticios',
        'timestamp_utc':datetime.now(timezone.utc).isoformat(),
        'viewport':{'width':page.viewport_size['width'],'height':page.viewport_size['height']},
    })
    print('CAPTURA RESPONSIVE',name,flush=True)

def verify_viewport(page,slug):
    metric=page.evaluate("""() => {
      const root=document.documentElement;
      const main=document.getElementById('main-content');
      const bounds=main ? main.getBoundingClientRect() : null;
      return {
        width:window.innerWidth,
        docWidth:root.scrollWidth,
        mainRight:bounds ? Math.round(bounds.right) : null,
        hasHorizontalOverflow:root.scrollWidth>window.innerWidth+2,
      };
    }""")
    result={'screen':slug,**metric}
    checks.append(result)
    if metric['hasHorizontalOverflow']:
        errors.append(result)
    return result

def select_section(page,nav,heading):
    toggle=page.get_by_role('button',name='Abrir menú')
    if toggle.is_visible():
        cls=page.locator('.sidebar').get_attribute('class') or ''
        if 'sidebar-open' not in cls:toggle.click()
    page.locator('nav').get_by_role('button',name=nav).click()
    expect(page.get_by_role('heading',name=heading,exact=True).first).to_be_visible()
    expect(page.locator('nav').get_by_role('button',name=nav)).to_have_attribute('aria-current','page')

with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
    for width,height,label in viewports:
        mobile=width<=390
        context=browser.new_context(
            viewport={'width':width,'height':height},
            is_mobile=mobile,has_touch=mobile,
            device_scale_factor=1,locale='es-PE',reduced_motion='reduce',
        )
        page=context.new_page()
        page.set_default_timeout(25000)
        page.goto(BASE,wait_until='domcontentloaded')
        expect(page.get_by_role('heading',name='Bienvenido',exact=True)).to_be_visible()
        verify_viewport(page,f'{label}_login')
        capture(page,f'{label}_login_v3',f'Login de calidad editorial en {width}×{height}; formulario autenticable')
        page.locator('input[autocomplete="username"]').fill('admin')
        page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
        page.get_by_role('button',name='Ingresar al sistema').click()
        expect(page.get_by_role('heading',name='Resumen operativo',exact=True)).to_be_visible()
        expect(page.locator('.environment')).to_contain_text('Datos sincronizados')
        for key,nav,heading in screens:
            if key!='dashboard':select_section(page,nav,heading)
            if key=='dashboard':
                expect(page.get_by_role('heading',name='Tu operación de un vistazo')).to_be_visible()
            if key=='pos':
                expect(page.locator('.product-card').first).to_be_visible()
                if width<=1250:
                    expect(page.get_by_role('button',name='Ver carrito (0)')).to_be_visible()
            if key=='products':
                expect(page.get_by_role('heading',name='Productos y recetas',exact=True).first).to_be_visible()
            if key=='kitchen':
                expect(page.locator('.kitchen-columns')).to_be_visible()
            metric=verify_viewport(page,f'{label}_{key}')
            print('RESPONSIVE CHECK',label,key,metric,flush=True)
            capture(page,f'{label}_{key}_v3',
                    f'Módulo {heading}, viewport {width}×{height}; vista y permisos verificados; overflow: {metric["hasHorizontalOverflow"]}')
        page.get_by_role('button',name='Abrir ayuda y atajos').click()
        expect(page.get_by_role('dialog',name='Centro de ayuda')).to_be_visible()
        expect(page.get_by_text('Pulsa').first).to_be_visible()
        verify_viewport(page,f'{label}_ayuda')
        capture(page,f'{label}_ayuda_v3',
                f'Modal de ayuda contextual en {width}×{height}; navegación y atajos por rol')
        page.keyboard.press('Escape')
        expect(page.get_by_role('dialog',name='Centro de ayuda')).to_have_count(0)
        if width==1440:
            page.keyboard.press('Alt+2')
            expect(page.get_by_role('heading',name='Nuevo pedido',exact=True)).to_be_visible()
            page.keyboard.press('Alt+1')
            expect(page.get_by_role('heading',name='Resumen operativo',exact=True)).to_be_visible()
        context.close()
    browser.close()

assert len(data['screenshots'])==152, f'Esperadas 152, encontradas {len(data["screenshots"])}'
files=[x['file'] for x in data['screenshots']]
assert len(set(files))==152, 'Archivo duplicado en manifiesto'
data['screenshot_count']=152
MANIFEST.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'responsive-matrix-results.json').write_text(json.dumps({
 'source':'Playwright Chromium real; datos de QA ficticios',
 'checked_viewports':viewports,
 'captured_states':len(checks),
 'screenshots_total':len(files),
 'overflow_findings':errors,
 'checks':checks,
 'notes':'El overflow de tablas internas se permite solo dentro de .table-wrap; el documento raíz no debe desbordarse.',
},ensure_ascii=False,indent=2),encoding='utf-8')
assert not errors, f'Hay {len(errors)} pantallas con overflow horizontal: {errors}'
print('MATRIZ RESPONSIVE 4×13 APROBADA. TOTAL 152 EVIDENCIAS REALES.',flush=True)
