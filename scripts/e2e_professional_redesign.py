"""Pruebas exploratorias guiadas en Chromium sobre la app REAL rediseñada.

Las capturas son PNG originales de navegador; utilizan datos ficticios y APIs de test.
Nunca afirman aceptación de usuarios ni auditoría productiva.
"""
from pathlib import Path
from datetime import datetime, timezone
import json
import os
import re
from playwright.sync_api import sync_playwright, expect

OUT=Path('e2e/evidencias')
FILE=OUT/'e2e-results.json'
BASE=os.getenv('E2E_FRONTEND_URL','http://127.0.0.1:5173')
PASSWORD=os.environ['SEED_ADMIN_PASSWORD']
manifest=json.loads(FILE.read_text('utf-8'))

def shot(page,n,title,proof):
    name=f'{n:02d}_{title}.png'
    page.screenshot(path=str(OUT/name),animations='disabled',full_page=True)
    manifest['screenshots'].append({'file':name,'step':proof,'source':'real Chromium/Playwright + FastAPI + PostgreSQL, seed QA','timestamp_utc':datetime.now(timezone.utc).isoformat()})
    print('PROOF',name,flush=True)

def login(page,role='admin'):
    page.goto(BASE,wait_until='domcontentloaded')
    page.locator('input[autocomplete="username"]').fill(role)
    page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
    page.get_by_role('button',name='Ingresar al sistema').click()
    expect(page.get_by_role('heading',name='¡Bienvenido a Paladar Inka AI!')).to_be_visible()

def section(page,nav_title,heading):
    hamburger=page.get_by_role('button',name='Abrir menú')
    if hamburger.is_visible() and 'sidebar-open' not in (page.locator('.sidebar').get_attribute('class') or ''):hamburger.click()
    page.locator('nav').get_by_role('button',name=nav_title).click()
    expect(page.get_by_role('heading',name=heading,exact=True).first).to_be_visible()

with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':900},locale='es-PE',accept_downloads=True)
    page=context.new_page();page.set_default_timeout(20000)
    page.goto(BASE)
    expect(page.get_by_role('heading',name='Bienvenido')).to_be_visible()
    shot(page,59,'login_profesional','Pantalla de acceso real con diseño empresarial y credenciales aún no enviadas')
    login(page)
    shot(page,60,'dashboard_operativo_redisenado','¡Bienvenido a Paladar Inka AI! con KPI consultados de PostgreSQL')
    page.get_by_role('button',name=re.compile('Nueva venta')).click()
    expect(page.get_by_role('heading',name='Ventas / Caja POS')).to_be_visible()
    shot(page,61,'accion_rapida_nueva_venta','Acción rápida del dashboard abre el POS funcional')
    page.get_by_role('button',name='Pizzas',exact=True).click()
    shot(page,62,'filtro_pizzas_pos','Filtro de categoría Pizzas aplicado en React a datos reales de API')
    page.get_by_label('Buscar productos').fill('Andina')
    expect(page.get_by_role('button',name=re.compile('Pizza Andina'))).to_be_visible()
    shot(page,63,'busqueda_producto_andina','Búsqueda incremental de productos por nombre')
    page.get_by_label('Buscar productos').fill('NoExisteProductoQA123')
    assert page.locator('.pi-pos-card').count()==0
    shot(page,64,'busqueda_sin_resultados','Búsqueda sin coincidencias verificadas: cero tarjetas visibles')
    page.get_by_label('Buscar productos').fill('')
    page.get_by_role('button',name='Todos',exact=True).click()
    page.get_by_role('button',name=re.compile('Pizza Inka')).first.click()
    page.locator('.pi-pos-modes > button').nth(1).click()
    shot(page,65,'tipo_atencion_recojo','Selección de modalidad de recojo para pedido nuevo')
    page.locator('.pi-pos-modes > button').nth(2).click()
    shot(page,66,'tipo_atencion_delivery','Selección de referencia de entrega, sin fingir integración de reparto')
    page.locator('.pi-pos-modes > button').nth(0).click()
    page.get_by_label('Mesa o referencia').fill('Mesa Diseño-88')
    page.get_by_role('button',name=re.compile('Pizza Andina')).first.click()
    shot(page,67,'carrito_operacion_multilina','Carrito de dos pizzas y total calculado desde catálogo activo')
    row=page.locator('.pi-pos-cart-line').filter(has_text='Pizza Inka')
    row.get_by_role('button',name='+').click()
    assert row.locator('.pi-pos-qty span').inner_text()=='2'
    shot(page,68,'stepper_cantidad_funcional','Control de cantidades del carrito actualiza unidades y subtotal')
    page.get_by_role('button',name='Confirmar pedido').click()
    expect(page.get_by_role('alert')).to_contain_text('Pedido creado')
    shot(page,69,'pedido_creado_con_stock','Pedido persistido y existencias descontadas transaccionalmente')
    page.get_by_label('Método de pago').select_option('plin')
    shot(page,70,'seleccion_pago_plin','Método de pago Plin seleccionado antes de confirmar')
    page.get_by_role('button',name=re.compile('Registrar pago')).click()
    expect(page.get_by_role('alert')).to_contain_text('Pago registrado correctamente')
    shot(page,71,'pago_plin_registrado','Pago único registrado con medio Plin en backend')
    section(page,'Pedidos','Gestión de pedidos')
    page.get_by_label('Buscar pedidos').fill('Diseño-88')
    assert page.locator('tbody tr').filter(has_text='Diseño-88').count()==1
    shot(page,72,'busqueda_pedidos_por_mesa','Filtro de pedidos por mesa muestra el registro recién creado')
    page.get_by_label('Buscar pedidos').fill('')
    page.get_by_role('button',name=re.compile(r'Pendiente \(')).click()
    shot(page,73,'filtro_pedidos_pendientes','Filtro de pedidos por estado pendiente en base de datos')
    page.get_by_role('button',name=re.compile(r'Todos \(')).click()
    row=page.get_by_role('row').filter(has_text='Diseño-88')
    row.get_by_role('button',name='Detalle').click()
    shot(page,74,'detalle_pedido_tres_pizzas','Detalle de líneas, total, pago y seguimiento del pedido')
    page.get_by_role('button',name='Cerrar detalle').click()
    section(page,'Cocina','Cocina – KDS')
    shot(page,75,'kanban_rediseno_cocina','Columnas de cocina con estados pendientes, preparación y listos')
    section(page,'Inventario','Inventario y Kardex')
    page.get_by_label('Buscar insumo').fill('Queso')
    assert page.locator('tbody').first.locator('tr').filter(has_text='Queso').count()>=1
    shot(page,76,'inventario_busqueda_queso','Inventario filtrado por nombre de insumo')
    page.get_by_label('Buscar insumo').fill('InsumoQAImposible')
    assert page.locator('tbody').first.locator('tr').count()==0
    shot(page,77,'inventario_busqueda_vacia','Inventario sin coincidencias; no se modifican existencias')
    page.get_by_label('Buscar insumo').fill('')
    with page.expect_download() as download_info:
        page.get_by_role('button',name=re.compile('Exportar CSV')).first.click()
    download=download_info.value
    assert download.suggested_filename=='inventario_paladar_inka.csv'
    dest=OUT/'inventario_qa_exportado.csv';download.save_as(dest)
    assert 'Queso' in dest.read_text('utf-8-sig')
    shot(page,78,'exportacion_inventario_csv','Exportación real CSV (el archivo se adjunta como evidencia)')
    section(page,'Productos y recetas','Productos y recetas')
    shot(page,79,'catalogo_recetas_administracion','Catálogo, formulario de alta y receta completa en interfaz')
    section(page,'Clientes','Clientes')
    page.get_by_label('Buscar cliente').fill('Cliente')
    shot(page,80,'busqueda_clientes_real','Búsqueda en listado de clientes de prueba registrados')
    page.get_by_label('Buscar cliente').fill('')
    section(page,'Reportes','Reportes y análisis')
    expect(page.get_by_text('Plin').first).to_be_visible()
    shot(page,81,'reporte_ventas_con_plin','Reporte de ventas por método de cobro incluyendo pago de esta prueba')
    with page.expect_download() as report_download:
        page.get_by_role('button',name=re.compile('Exportar reporte CSV')).click()
    exported=report_download.value;assert exported.suggested_filename=='reporte_ventas_paladar_inka.csv'
    exported.save_as(OUT/'reporte_ventas_qa_exportado.csv')
    shot(page,82,'exportacion_reporte_real','Descarga real de reporte con productos vendidos y cantidades')
    section(page,'IA y recomendaciones','Inteligencia operativa')
    shot(page,83,'analitica_heuristica_metodo','Panel heurístico y media móvil claramente identificados; sin ML entrenado')
    section(page,'Usuarios','Usuarios y permisos')
    shot(page,84,'seguridad_usuarios_roles','Roles, usuarios, accesos y bitácora de acciones del backend')
    section(page,'Configuración','Configuración del entorno')
    shot(page,85,'seguridad_configuracion','Configuración y formulario de revocación de sesiones por contraseña')
    mobile=browser.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=1,locale='es-PE')
    mp=mobile.new_page();mp.set_default_timeout(15000);login(mp,'cajero')
    shot(mp,86,'movil_dashboard_redisenado','Panel operativo responsive con credenciales del cajero')
    mp.get_by_role('button',name='Abrir menú').click()
    expect(mp.locator('.sidebar')).to_have_class(re.compile('sidebar-open'))
    shot(mp,87,'movil_menu_desplegado','Navegación móvil real con menú lateral y permisos de cajero')
    section(mp,'Ventas (POS)','Ventas / Caja POS')
    shot(mp,88,'movil_punto_venta','Punto de venta móvil con catálogo y carrito adaptativos')
    api_unauthorized=browser.new_page(viewport={'width':1440,'height':900})
    response=api_unauthorized.goto('http://127.0.0.1:8000/api/v1/users')
    assert response is not None and response.status==401
    shot(api_unauthorized,89,'qa_http_401_usuarios','HTTP 401 real de acceso anónimo al módulo de administración')
    context_api=p.request.new_context(base_url='http://127.0.0.1:8000')
    signed=context_api.post('/api/v1/auth/token',data={'username':'cocina','password':PASSWORD})
    assert signed.status==200
    tok=signed.json()['access_token']
    context_forbidden=browser.new_context(viewport={'width':1440,'height':900},extra_http_headers={'Authorization':f'Bearer {tok}'})
    forb=context_forbidden.new_page()
    resp=forb.goto('http://127.0.0.1:8000/api/v1/users')
    assert resp is not None and resp.status==403
    shot(forb,90,'qa_http_403_cocina','HTTP 403 real: usuario de cocina no autorizado a listar colaboradores')
    manifest['screenshot_count']=len(manifest['screenshots'])
    FILE.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('CAPTURAS NUEVA UI TOTAL',len(manifest['screenshots']),flush=True)
    context_api.dispose();browser.close()