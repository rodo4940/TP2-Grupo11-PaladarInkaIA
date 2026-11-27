"""Control visual de la versión Studio v4: 48 capturas reales adicionales.

Se ejecuta DESPUÉS de la suite de 152 PNG existente, sobre Chromium con
frontend React/TypeScript, API FastAPI y PostgreSQL con datos ficticios.
No produce imágenes simuladas ni edita las capturas obtenidas.
"""
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json
import os
import struct

BASE=os.getenv('E2E_FRONTEND_URL','http://127.0.0.1:5173')
PASSWORD=os.environ['SEED_ADMIN_PASSWORD']
OUT=Path('e2e/evidencias')
data=json.loads((OUT/'e2e-results.json').read_text(encoding='utf-8'))
assert len(data['screenshots'])==152, 'Es indispensable completar las 152 evidencias previas'

sizes=[
 (320,720,'compacto_320'),
 (414,896,'movil_414'),
 (820,1180,'tablet_820'),
 (1366,900,'escritorio_1366'),
]
modules=[
 ('dashboard','Dashboard','¡Bienvenido a Paladar Inka AI!'),
 ('pos','Ventas (POS)','Ventas / Caja POS'),
 ('orders','Pedidos','Gestión de pedidos'),
 ('kitchen','Cocina','Cocina – KDS'),
 ('inventory','Inventario','Inventario'),
 ('products','Productos','Productos y recetas'),
 ('customers','Clientes','Clientes'),
 ('reports','Reportes','Reportes y análisis'),
 ('ai','IA y recomendaciones','Inteligencia operativa'),
 ('users','Usuarios','Usuarios y permisos'),
 ('settings','Configuración','Configuración del entorno'),
]
metrics=[]
runtime_errors=[]
count=152

def inspect(page,scenario):
    value=page.evaluate("""() => ({
      width:window.innerWidth,docWidth:document.documentElement.scrollWidth,
      bodyWidth:document.body.scrollWidth,
      height:window.innerHeight,
      horizontalOverflow:document.documentElement.scrollWidth > window.innerWidth + 2
    })""")
    metric={'scenario':scenario,**value}
    metrics.append(metric)
    assert not value['horizontalOverflow'],f'Desbordamiento horizontal: {metric}'
    return metric

def snapshot(page,slug,description):
    global count
    count+=1
    filename=f'{count:03d}_{slug}.png'
    page.screenshot(path=str(OUT/filename),full_page=True,animations='disabled')
    # Playwright puede exportar un PNG más ancho aunque documentElement.scrollWidth
    # parezca correcto (p. ej., grillas con :has y formularios de Inventario).
    with (OUT/filename).open('rb') as file:
      header=file.read(24)
    assert header[:8]==b'\x89PNG\r\n\x1a\n', f'PNG inválido: {filename}'
    image_width,image_height=struct.unpack('>II',header[16:24])
    expected_width=page.viewport_size['width']
    assert image_width==expected_width,(
      f'Captura desbordada: {filename}, PNG={image_width}px, viewport={expected_width}px'
    )
    data['screenshots'].append({
      'file':filename,'step':description,
      'source':'Captura Chromium real, React/FastAPI/PostgreSQL; entorno de pruebas con datos ficticios',
      'timestamp_utc':datetime.now(timezone.utc).isoformat(),
      'viewport':dict(page.viewport_size),
    })
    print('ESTUDIO V4',filename,flush=True)

def navigate(page,label,heading):
    toggle=page.get_by_role('button',name='Abrir menú')
    if toggle.is_visible():
      if 'sidebar-open' not in (page.locator('.sidebar').get_attribute('class') or ''):
        toggle.click()
    target=page.locator('nav').get_by_role('button',name=label,exact=True)
    target.click()
    expect(page.get_by_role('heading',name=heading,exact=True).first).to_be_visible()
    expect(target).to_have_attribute('aria-current','page')

with sync_playwright() as browser_tool:
    browser=browser_tool.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
    for width,height,slug in sizes:
      mobile=width<500
      context=browser.new_context(
        viewport={'width':width,'height':height},
        is_mobile=mobile,has_touch=mobile,locale='es-PE',
        device_scale_factor=1,reduced_motion='reduce',
      )
      page=context.new_page()
      page.set_default_timeout(30000)
      page.on('pageerror',lambda error:runtime_errors.append(str(error)))
      page.goto(BASE,wait_until='domcontentloaded')
      expect(page.get_by_role('heading',name='Bienvenido')).to_be_visible()
      inspect(page,slug+'_login')
      snapshot(page,slug+'_login_studio','Inicio de sesión y arte de pizzería en '+str(width)+'×'+str(height))
      page.locator('input[autocomplete="username"]').fill('admin')
      page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
      page.get_by_role('button',name='Ingresar al sistema').click()
      expect(page.get_by_role('heading',name='¡Bienvenido a Paladar Inka AI!',exact=True)).to_be_visible()
      expect(page.locator('.environment')).to_contain_text('Datos sincronizados')
      if width<=700:
        dock=page.get_by_role('navigation',name='Navegación rápida móvil')
        expect(dock).to_be_visible()
        expect(dock.get_by_role('button',name='Ir a Inicio')).to_have_attribute('aria-current','page')
        dock.get_by_role('button',name='Ir a Vender').click()
        expect(page.get_by_role('heading',name='Ventas / Caja POS',exact=True)).to_be_visible()
        dock.get_by_role('button',name='Ir a Inicio').click()
        expect(page.get_by_role('heading',name='¡Bienvenido a Paladar Inka AI!',exact=True)).to_be_visible()
      else:
        expect(page.locator('.mobile-dock')).to_be_hidden()
      for key,label,heading in modules:
        if key!='dashboard':navigate(page,label,heading)
        if key not in ('dashboard','pos','orders','kitchen','inventory'):
          expect(page.locator('.module-heading .section-artwork')).to_be_visible()
          expect(page.locator('.module-heading')).to_have_count(1)
        if key=='dashboard':
          expect(page.get_by_role('heading',name='Pedidos cobrados en los últimos 7 días')).to_be_visible()
        if key=='pos':
          expect(page.locator('.pi-pos-card').first).to_be_visible()
          page.wait_for_function("""() => {
            const photos=[...document.querySelectorAll('.pi-pos-card img')];
            return photos.length>=4 && photos.every(photo=>photo.complete && photo.naturalWidth>0);
          }""",timeout=35000)
          page.locator('.pi-pos-card img').evaluate_all("imgs => Promise.all(imgs.map(img => img.decode()))")
          if width<=1250:
            expect(page.locator('.pi-pos-ticket')).to_be_visible()
        if key=='settings':
          expect(page.get_by_role('heading',name='Configuración del entorno',exact=True)).to_be_visible()
        result=inspect(page,slug+'_'+key)
        snapshot(page,slug+'_'+key+'_studio',
          f'Módulo {heading}: interfaz Studio v4 en {width}×{height}; overflow={result["horizontalOverflow"]}')
      page.get_by_role('button',name='Abrir ayuda y atajos').click()
      expect(page.get_by_role('dialog',name='Centro de ayuda')).to_be_visible()
      page.keyboard.press('Escape')
      expect(page.get_by_role('dialog',name='Centro de ayuda')).to_have_count(0)
      if width>=1000:
        page.keyboard.press('Alt+2')
        expect(page.get_by_role('heading',name='Ventas / Caja POS',exact=True)).to_be_visible()
        page.keyboard.press('Alt+1')
        expect(page.get_by_role('heading',name='¡Bienvenido a Paladar Inka AI!',exact=True)).to_be_visible()
      context.close()
    # Validación funcional sin Internet al proveedor de fotografías: se usa arte local.
    offline=browser.new_context(viewport={'width':414,'height':896},locale='es-PE')
    offline.route('**/images.unsplash.com/**',lambda request:request.abort())
    p_off=offline.new_page()
    p_off.set_default_timeout(30000)
    p_off.goto(BASE,wait_until='domcontentloaded')
    expect(p_off.get_by_role('heading',name='Bienvenido')).to_be_visible()
    p_off.wait_for_function("""() => {
       const image=document.querySelector('.login-hero-photo img');
       return image && image.currentSrc.includes('/illustrations/pizza-artisan.svg')
          && image.complete && image.naturalWidth>0;
    }""")
    p_off.locator('input[autocomplete="username"]').fill('admin')
    p_off.locator('input[autocomplete="current-password"]').fill(PASSWORD)
    p_off.get_by_role('button',name='Ingresar al sistema').click()
    expect(p_off.get_by_role('heading',name='¡Bienvenido a Paladar Inka AI!')).to_be_visible()
    p_off.get_by_role('button',name='Ir a Vender').click()
    expect(p_off.get_by_role('heading',name='Ventas / Caja POS')).to_be_visible()
    p_off.wait_for_function("""() => {
      const photos=[...document.querySelectorAll('.pi-pos-card img')];
      return photos.length>=4 && photos.every(img=>img.currentSrc.includes('/illustrations/pizza-artisan.svg') && img.complete && img.naturalWidth>0);
    }""",timeout=30000)
    offline.close()
    # El rol cocina no debe tener un acceso de venta en su dock ni sidebar.
    restricted=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='es-PE')
    p_role=restricted.new_page()
    p_role.set_default_timeout(30000)
    p_role.goto(BASE)
    p_role.locator('input[autocomplete="username"]').fill('cocina')
    p_role.locator('input[autocomplete="current-password"]').fill(PASSWORD)
    p_role.get_by_role('button',name='Ingresar al sistema').click()
    expect(p_role.get_by_role('heading',name='¡Bienvenido a Paladar Inka AI!')).to_be_visible()
    expect(p_role.get_by_role('button',name='Ir a Vender')).to_have_count(0)
    p_role.get_by_role('button',name='Abrir menú').click()
    expect(p_role.locator('nav').get_by_role('button',name='Ventas (POS)')).to_have_count(0)
    restricted.close()
    browser.close()

assert count==200 and len(data['screenshots'])==200, 'La matriz debe contener exactamente 200 capturas'
assert len({item['file'] for item in data['screenshots']})==200, 'Evidencias duplicadas'
report={
  'project':'El Paladar del Inka',
  'environment':'Chromium contra React + FastAPI + PostgreSQL con datos ficticios',
  'viewports':sizes,
  'new_screenshots':48,
  'total_screenshots':200,
  'verified_viewport_scenarios':len(metrics),
  'horizontal_overflows':[item for item in metrics if item['horizontalOverflow']],
  'runtime_errors':runtime_errors,
  'scenarios':metrics,
  'limit':'No equivale a UAT firmada ni a autorización comercial',
}
(OUT/'studio-v4-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
assert not runtime_errors,f'Excepciones JavaScript no manejadas: {runtime_errors}'
data['screenshot_count']=200
(OUT/'e2e-results.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print('STUDIO V4 OK: 48 nuevas / 200 capturas reales, sin errores de JS ni overflow horizontal',flush=True)
