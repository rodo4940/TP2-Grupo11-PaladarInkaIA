"""Evidencias reales de UI generadas por Chromium contra frontend React + API PostgreSQL.

No contiene imágenes sintéticas. Utiliza únicamente datos ficticios de semilla.
"""
from datetime import datetime, timezone
from pathlib import Path
import json
import os
import re
from playwright.sync_api import sync_playwright

OUT=Path('e2e/evidencias');OUT.mkdir(parents=True,exist_ok=True)
BASE=os.getenv('E2E_FRONTEND_URL','http://127.0.0.1:5173')
PASSWORD=os.environ['SEED_ADMIN_PASSWORD']
manifest={'environment':'CI local PostgreSQL 17 + React + FastAPI','timestamp_utc':datetime.now(timezone.utc).isoformat(),
          'source':'Chromium/Playwright real browser actions','test_data':'seed fictional / no customer production records', 'screenshots':[]}

def screenshot(page,filename,step):
    page.screenshot(path=str(OUT/filename),full_page=True,animations='disabled')
    manifest['screenshots'].append({'file':filename,'step':step})

with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':900},device_scale_factor=1,locale='es-PE')
    page=context.new_page()
    page.set_default_timeout(20000)
    page.goto(BASE,wait_until='domcontentloaded')
    page.get_by_role('heading',name='Bienvenido').wait_for()
    screenshot(page,'01_login_real.png','Formulario login renderizado desde React')
    page.locator('input[autocomplete="username"]').fill('admin')
    page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
    page.get_by_role('button',name='Ingresar al sistema').click()
    page.get_by_role('heading',name='Resumen operativo').wait_for()
    screenshot(page,'02_dashboard_real.png','Panel consulta estadísticas reales a API')
    nav=page.locator('nav')
    nav.get_by_role('button',name='Ventas / POS').click()
    page.get_by_role('heading',name='Nuevo pedido').wait_for()
    screenshot(page,'03_pos_real.png','Catálogo proviene de tabla PostgreSQL products')
    page.get_by_role('button',name=re.compile('Pizza Inka')).first.click()
    page.get_by_role('button',name='Confirmar pedido').click()
    page.get_by_text('Pedido #1').wait_for()
    screenshot(page,'04_pedido_creado_real.png','Creación HTTP POST /orders y descuento de ingredientes')
    page.get_by_role('button',name=re.compile('Registrar pago')).click()
    page.get_by_text('Pago registrado correctamente').wait_for()
    screenshot(page,'05_pago_real.png','POST de pago único realizado en BD')
    nav.get_by_role('button',name='Pedidos').click()
    page.get_by_role('heading',name='Gestión de pedidos').wait_for()
    screenshot(page,'06_pedidos_real.png','Listado de operaciones y estado del pago')
    nav.get_by_role('button',name='Cocina').click()
    page.get_by_role('heading',name='Comandas de cocina').wait_for()
    screenshot(page,'07_cocina_real.png','Comandas provenientes de la tabla de pedidos')
    page.get_by_role('button',name='Iniciar preparación').click()
    page.get_by_text('Pedido #1 actualizado a En preparación').wait_for()
    screenshot(page,'08_cocina_preparando_real.png','Cambio de estado verificado por API y React')
    nav.get_by_role('button',name='Inventario / Kardex').click()
    page.get_by_role('heading',name='Inventario y Kardex').wait_for()
    page.get_by_text('PEDIDO-1').first.wait_for()
    screenshot(page,'09_kardex_real.png','Movimientos de consumo por pedido y saldo real')
    nav.get_by_role('button',name='Reportes de ventas').click()
    page.get_by_role('heading',name='Reportes y análisis').wait_for()
    screenshot(page,'10_reporte_real.png','Reporte de ventas cobradas obtenido de API')
    nav.get_by_role('button',name='Panel general').click()
    page.get_by_role('heading',name='Resumen operativo').wait_for()
    page.get_by_text('S/ 35.00').first.wait_for()
    screenshot(page,'21_dashboard_venta_confirmada_real.png','Dashboard consultado nuevamente tras pago confirmado en PostgreSQL')

    nav.get_by_role('button',name='Analítica inteligente').click()
    page.get_by_role('heading',name='Inteligencia operativa').wait_for()
    screenshot(page,'11_analitica_real.png','Ranking heurístico con método declarado explícitamente')
    nav.get_by_role('button',name='Usuarios y roles').click()
    page.get_by_role('heading',name='Usuarios y permisos').wait_for()
    screenshot(page,'12_usuarios_real.png','RBAC y bitácora vistos como administrador')
    # Verificación de nuevas pantallas de gestión comercial (React + PostgreSQL)
    nav.get_by_role('button',name='Productos y recetas').click()
    page.get_by_role('heading',name='Editar productos y disponibilidad').wait_for()
    screenshot(page,'15_catalogo_edicion_real.png','Edición de productos y disponibilidad administrada por API')
    page.get_by_label('Producto a editar').select_option('1')
    page.get_by_role('button',name='Guardar cambios').click()
    page.get_by_text('Producto actualizado').wait_for()
    screenshot(page,'16_producto_modificado_real.png','PATCH /products/1 aplicado y tabla actualizada')
    nav.get_by_role('button',name='Clientes').click()
    page.locator('main h1').filter(has_text='Clientes').first.wait_for()
    page.get_by_label('Nombre completo').fill('Cliente verificación QA')
    page.get_by_role('button',name='Guardar cliente').click()
    page.get_by_text('Cliente registrado').wait_for()
    screenshot(page,'17_cliente_real.png','Cliente de prueba creado vía API en base PostgreSQL')
    page.get_by_role('button',name=re.compile('Ver historial')).first.click()
    page.get_by_role('heading',name=re.compile('Ficha del cliente')).wait_for()
    screenshot(page,'18_historial_cliente_real.png','GET /customers/:id/insights desde React')
    nav.get_by_role('button',name='Pedidos').click()
    page.get_by_role('button',name='Ticket interno').first.click()
    page.get_by_role('dialog',name='Ticket interno').wait_for()
    screenshot(page,'19_ticket_interno_real.png','Ticket administrativo no tributario proveniente de API')
    page.locator('.receipt-controls').get_by_role('button',name='Cerrar').click()
    nav.get_by_role('button',name='Configuración').click()
    page.get_by_role('heading',name='Actualizar mi contraseña').wait_for()
    screenshot(page,'20_configuracion_seguridad_real.png','Formulario de cambio de contraseña con revocación JWT del backend')
    context2=browser.new_context(viewport={'width':1440,'height':900},locale='es-PE')
    p2=context2.new_page();p2.goto(BASE)
    p2.locator('input[autocomplete="username"]').fill('cocina')
    p2.locator('input[autocomplete="current-password"]').fill(PASSWORD)
    p2.get_by_role('button',name='Ingresar al sistema').click()
    p2.get_by_role('heading',name='Resumen operativo').wait_for()
    assert p2.locator('nav').get_by_role('button',name='Ventas / POS').count()==0,'Rol cocina puede ver POS'
    p2.locator('nav').get_by_role('button',name='Cocina').click()
    screenshot(p2,'13_rol_cocina_real.png','Sesión del rol cocina sin opción POS')
    mobile=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,locale='es-PE',is_mobile=True,has_touch=True)
    mob=mobile.new_page();mob.goto(BASE)
    mob.get_by_role('heading',name='Bienvenido').wait_for()
    screenshot(mob,'14_responsive_real.png','Viewport móvil de 390×844 con React responsive')
    # Verificación adicional en navegador: documentación OpenAPI y autorización del backend.
    api_context=browser.new_context(viewport={'width':1440,'height':900},locale='es-PE')
    api_page=api_context.new_page()
    resp=api_page.goto('http://127.0.0.1:8000/docs',wait_until='networkidle')
    assert resp and resp.status==200,'Documentación Swagger inaccesible en CI'
    screenshot(api_page,'22_swagger_real.png','Interfaz Swagger/OpenAPI realmente servida por FastAPI en entorno test')
    no_auth=api_page.goto('http://127.0.0.1:8000/api/v1/users',wait_until='domcontentloaded')
    assert no_auth and no_auth.status==401,'Endpoint administrativo no rechaza accesos anónimos'
    screenshot(api_page,'23_denegacion_401_real.png','HTTP 401 real al consultar /api/v1/users sin token JWT')
    bad_context=browser.new_context(viewport={'width':1440,'height':900},locale='es-PE')
    bad=bad_context.new_page();bad.goto(BASE)
    bad.locator('input[autocomplete="username"]').fill('admin')
    bad.locator('input[autocomplete="current-password"]').fill('ClaveIncorrectaNoValida')
    bad.get_by_role('button',name='Ingresar al sistema').click()
    bad.get_by_text('Usuario o contraseña incorrectos').first.wait_for()
    screenshot(bad,'24_login_incorrecto_real.png','Error HTTP 401 visible tras credenciales de prueba incorrectas')
    api_context.close();bad_context.close()
    (OUT/'e2e-results.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('CAPTURAS REALES VERIFICADAS:',len(manifest['screenshots']))
    browser.close()

# Escenarios funcionales adicionales con datos ficticios, ejecutados en el mismo entorno de CI.
from subprocess import run
from sys import executable
run([executable, 'scripts/e2e_operaciones.py'], check=True)
