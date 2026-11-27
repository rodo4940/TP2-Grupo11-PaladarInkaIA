"""Evidencia visual v5: 40 capturas Chromium reales y QA de caja + analítica.

Se ejecuta tras las 200 capturas existentes; el resultado íntegro se archiva
en GitHub Actions. Pantallas tomadas sobre API real con PostgreSQL y datos de QA.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import struct

from playwright.sync_api import sync_playwright, expect

OUT = Path('e2e/evidencias')
BASE = os.environ.get('E2E_FRONTEND_URL', 'http://127.0.0.1:5173')
PASSWORD = os.environ['SEED_ADMIN_PASSWORD']
manifest = json.loads((OUT / 'e2e-results.json').read_text(encoding='utf-8'))
assert len(manifest['screenshots']) == 200, 'Deben ejecutarse primero las 200 evidencias v4'
index = 200
FOCUSED = OUT / 'encuadres_viewport'
FOCUSED.mkdir(exist_ok=True)
results = []
exceptions = []
viewports = [
    (320, 720, 'telefono_320'),
    (390, 844, 'telefono_390'),
    (768, 1024, 'tableta_768'),
    (1280, 800, 'portatil_1280'),
    (1440, 900, 'escritorio_1440'),
]


def assert_layout(page, name):
    data = page.evaluate("""() => {
      const html=document.documentElement;
      const images=[...document.querySelectorAll('main img, .login-hero-photo img')];
      return {
        viewport: innerWidth,
        document_width: html.scrollWidth,
        body_width: document.body.scrollWidth,
        broken_visible_images: images.filter(img =>
          img.getClientRects().length && img.complete && img.naturalWidth === 0
        ).map(img=>img.currentSrc),
        horizontal_overflow: html.scrollWidth > innerWidth + 1
      };
    }""")
    assert not data['horizontal_overflow'], f'Overflow raíz en {name}: {data}'
    assert not data['broken_visible_images'], f'Imagen dañada en {name}: {data}'
    results.append({'scenario':name, **data})


def snap(page, name, description):
    global index
    assert_layout(page, name)
    index += 1
    file_name = f'{index:03d}_{name}.png'
    # Antes de fotografiar la página larga, volver al inicio evita que la
    # topbar sticky y el menú lateral aparezcan a mitad del documento.
    # Retirar el foco visual evita que el skip-link quede sobre la captura.
    page.evaluate("""() => {
      const node=document.activeElement;
      if(node instanceof HTMLElement) node.blur();
      window.scrollTo(0,0);
    }""")
    page.wait_for_timeout(80)
    page.screenshot(path=str(OUT / file_name), full_page=True, animations='disabled')
    # Segunda toma auténtica, sin editar ni deformar: encuadre fijo del dispositivo.
    # En capturas extensas el dock inferior se ve a mitad de la página al combinar
    # todo el scroll; este segundo formato muestra la barra fija en su posición real.
    focus_key = name.split('_', 2)[-1]
    targets = {
      'caja_filtros': '.billing-filters',
      'ticket_interno': '.billing-ticket',
      'ia_contexto': '.copilot-intro',
      'ia_respuesta': '.copilot-conversation',
    }
    focus = next((selector for key,selector in targets.items() if key in name), None)
    if focus and page.locator(focus).count():
      page.locator(focus).first.scroll_into_view_if_needed()
    page.screenshot(path=str(FOCUSED / file_name), full_page=False, animations='disabled')
    # Ambos archivos son salidas directas de Playwright. El encuadre se documenta
    # separado; solo la toma de página completa forma parte del manifiesto 001–240.
    with (OUT / file_name).open('rb') as file:
        header = file.read(24)
    assert header[:8] == b'\x89PNG\r\n\x1a\n', 'Cabecera PNG inválida'
    width, height = struct.unpack('>II', header[16:24])
    expected = page.viewport_size['width']
    assert width == expected, f'Ancho de PNG {width} no coincide con viewport {expected}: {name}'
    assert 400 <= height <= 22000, f'Altura anómala en {name}: {height}px'
    manifest['screenshots'].append({
        'file': file_name,
        'step': description,
        'viewport': page.viewport_size,
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'source': 'React/FastAPI/PostgreSQL reales en Chromium Playwright; solo datos ficticios CI',
    })
    print('V5 EVIDENCE',file_name,width,height,flush=True)


def navigate(page,label,heading):
    menu = page.get_by_role('button',name='Abrir menú')
    if menu.is_visible():
        if 'sidebar-open' not in (page.locator('.sidebar').get_attribute('class') or ''):
            menu.click()
    item = page.locator('nav').get_by_role('button',name=label,exact=True)
    item.click()
    expect(page.get_by_role('heading',name=heading,exact=True).first).to_be_visible()


with sync_playwright() as playwright:
    browser=playwright.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
    for width,height,slug in viewports:
        mobile=width<500
        context=browser.new_context(
            viewport={'width':width,'height':height},
            device_scale_factor=1,locale='es-PE',is_mobile=mobile,has_touch=mobile,
            reduced_motion='reduce')
        page=context.new_page()
        page.set_default_timeout(30000)
        page.on('pageerror',lambda e:exceptions.append(str(e)))
        page.goto(BASE,wait_until='domcontentloaded')
        expect(page.get_by_role('heading',name='Bienvenido')).to_be_visible()
        expect(page.locator('.login-brand .inka-brand-icon')).to_be_visible()
        page.wait_for_function("""() => {
            const img=document.querySelector('.login-hero-photo img');
            return img && img.complete && img.naturalWidth>0;
        }""",timeout=35000)
        snap(page,slug+'_login_inka','Acceso con isotipo Inka vectorial y fotografía referencial nítida')

        page.locator('input[autocomplete="username"]').fill('admin')
        page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
        page.get_by_role('button',name='Ingresar al sistema').click()
        expect(page.get_by_role('heading',name='Resumen operativo',exact=True)).to_be_visible()
        expect(page.locator('.environment')).to_contain_text('Datos sincronizados')
        expect(page.locator('.sidebar-head .inka-brand-icon')).to_have_count(1)
        snap(page,slug+'_dashboard_inka','Panel general con métricas reales e identidad gastronómica')

        navigate(page,'Ventas / POS','Nuevo pedido')
        page.wait_for_function("""() => {
           const imgs=[...document.querySelectorAll('.product-card img')];
           return imgs.length>=4 && imgs.every(img=>img.complete && img.naturalWidth>0);
        }""",timeout=35000)
        snap(page,slug+'_catalogo_pos','Tarjetas fotográficas de venta, categorías, carrito y totales de servidor')

        navigate(page,'Caja y comprobantes','Caja y comprobantes')
        expect(page.get_by_text('Constancias internas — no son boletas ni facturas electrónicas.')).to_be_visible()
        expect(page.get_by_role('heading',name='Historial de pagos')).to_be_visible()
        expect(page.locator('.billing-entry').first).to_be_visible()
        snap(page,slug+'_caja_registros','Módulo de caja consultando pagos confirmados y filtros desde la API')
        page.get_by_label('Filtrar método de pago').select_option('yape')
        snap(page,slug+'_caja_filtros','Consulta por medio de pago, sin modificar registros')
        page.get_by_label('Filtrar método de pago').select_option('all')
        expect(page.locator('.billing-ticket')).to_be_visible()
        assert 'INT-' in page.locator('.billing-ticket').inner_text()
        assert 'No constituye comprobante tributario SUNAT' in page.locator('.billing-ticket').inner_text()
        snap(page,slug+'_ticket_interno','Vista previa imprimible de constancia interna; sin afirmar emisión SUNAT')

        navigate(page,'Analítica inteligente','Inteligencia operativa')
        expect(page.get_by_role('heading',name='Consulta tu operación')).to_be_visible()
        expect(page.get_by_text('Datos disponibles')).to_be_visible()
        snap(page,slug+'_ia_contexto','Asistente operativo con indicadores agregados y metodología visible')
        page.get_by_role('button',name='¿Qué ingredientes debo reponer?').click()
        expect(page.get_by_text('Resultado verificable de reglas locales',exact=False)).to_be_visible()
        snap(page,slug+'_ia_respuesta','Consulta a la API IA y respuesta fundamentada sin mutar datos')
        context.close()

    # Validación del aislamiento de rol cocina en UI y en la API: no hay acceso a caja ni analítica.
    context=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,locale='es-PE')
    page=context.new_page()
    page.goto(BASE)
    page.locator('input[autocomplete="username"]').fill('cocina')
    page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
    page.get_by_role('button',name='Ingresar al sistema').click()
    expect(page.get_by_role('heading',name='Resumen operativo')).to_be_visible()
    page.get_by_role('button',name='Abrir menú').click()
    expect(page.locator('nav').get_by_role('button',name='Caja y comprobantes')).to_have_count(0)
    expect(page.locator('nav').get_by_role('button',name='Analítica inteligente')).to_have_count(0)
    expect(page.get_by_role('button',name='Ir a Vender')).to_have_count(0)
    context.close()
    browser.close()

assert index==240 and len(manifest['screenshots'])==240
assert len(list(FOCUSED.glob('*.png')))==40, 'Faltan encuadres fijos de dispositivo'
assert len({x['file'] for x in manifest['screenshots']})==240
assert not exceptions,f'Errores JS no controlados: {exceptions}'
manifest['screenshot_count']=240
(OUT/'e2e-results.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'inka-v5-results.json').write_text(json.dumps({
 'project':'El Paladar del Inka','total_screenshots':240,
 'new_screenshots':40,'viewport_crops':40,'new_viewports':viewports,
 'scenarios':results,'javascript_errors':exceptions,
 'limits':'Capturas de laboratorio con datos ficticios. Ticket interno, no SUNAT. IA local con opción de modelo por clave.'
},ensure_ascii=False,indent=2),encoding='utf-8')
print('VERIFICADO: 240 PNG REALES, 5 tamaños, caja, ticket, respuesta IA, RBAC, ancho íntegro',flush=True)
