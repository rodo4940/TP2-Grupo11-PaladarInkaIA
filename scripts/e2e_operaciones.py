"""QA visual de operaciones mediante navegador real y datos ficticios de PostgreSQL."""
import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

folder=Path('e2e/evidencias')
manifest_file=folder/'e2e-results.json'
manifest=json.loads(manifest_file.read_text(encoding='utf8'))
base=os.environ.get('E2E_FRONTEND_URL','http://127.0.0.1:5173')
password=os.environ['SEED_ADMIN_PASSWORD']

def shot(page,name,description):
    page.screenshot(path=str(folder/name),full_page=True,animations='disabled')
    manifest['screenshots'].append({'file':name,'step':description,'source':'Chromium UI real; datos de QA'})
    print('EVIDENCIA REAL',name,flush=True)

def screen(page,title,heading):
    page.locator('nav').get_by_role('button',name=title).click()
    expect(page.get_by_role('heading',name=heading,exact=True).first).to_be_visible()

with sync_playwright() as playwright:
    browser=playwright.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':900},locale='es-PE')
    page.set_default_timeout(15000)
    page.goto(base)
    page.locator('input[autocomplete="username"]').fill('admin')
    page.locator('input[autocomplete="current-password"]').fill(password)
    page.get_by_role('button',name='Ingresar al sistema').click()
    expect(page.get_by_role('heading',name='Resumen operativo')).to_be_visible()
    shot(page,'25_dashboard_despues_primer_cobro.png','Dashboard real tras el cobro del primer pedido')

    screen(page,'Clientes','Clientes')
    form=page.locator('form').filter(has=page.get_by_role('button',name='Guardar cliente')).first
    form.get_by_label('Nombre completo').fill('Cliente integral de pruebas QA')
    form.get_by_label('Teléfono (opcional)').fill('900123456')
    form.get_by_role('button',name='Guardar cliente').click()
    expect(page.get_by_role('alert')).to_contain_text('Cliente registrado')
    shot(page,'26_cliente_creado_en_interfaz.png','Creación real de cliente de QA en la interfaz')

    screen(page,'Ventas / POS','Nuevo pedido')
    page.get_by_role('button',name=re.compile('Pizza Suprema')).first.click()
    page.get_by_role('button',name=re.compile('Pizza Vegetariana')).first.click()
    page.get_by_label('Mesa o referencia').fill('Mesa QA-07')
    page.get_by_label('Observaciones').fill('Comanda de prueba con dos pizzas')
    shot(page,'27_pos_carrito_dos_pizzas.png','Carrito de compra con dos productos distintos')
    page.get_by_role('button',name='Confirmar pedido').click()
    expect(page.get_by_role('alert')).to_contain_text('Pedido creado')
    shot(page,'28_pedido_dos_pizzas_confirmado.png','Segundo pedido confirmado en backend y UI')
    page.get_by_label('Método de pago').select_option('yape')
    shot(page,'29_metodo_de_pago_yape.png','Elección de medio de pago Yape')
    page.get_by_role('button',name=re.compile('Registrar pago')).click()
    expect(page.get_by_role('alert')).to_contain_text('Pago registrado correctamente')
    shot(page,'30_yape_pago_confirmado.png','Pago de la nueva orden confirmado en PostgreSQL')

    screen(page,'Pedidos','Gestión de pedidos')
    row=page.get_by_role('row').filter(has_text='Mesa QA-07')
    row.get_by_role('button',name='Detalle').click()
    expect(page.get_by_role('heading',name=re.compile('Seguimiento del pedido'))).to_be_visible()
    shot(page,'31_detalle_trazabilidad_pedido.png','Vista detallada de líneas, total y etapas del pedido')
    page.get_by_role('button',name='Cerrar detalle').click()

    screen(page,'Cocina','Comandas de cocina')
    card=page.locator('article.kanban-card').filter(has_text='Mesa QA-07')
    expect(card).to_be_visible()
    shot(page,'32_comanda_pendiente_cocina.png','Comanda pendiente en tablero Kanban')
    card.get_by_role('button',name='Iniciar preparación').click()
    expect(page.get_by_role('alert')).to_contain_text('En preparación')
    shot(page,'33_comanda_en_preparacion.png','Comanda cambia a estado de preparación')
    card=page.locator('article.kanban-card').filter(has_text='Mesa QA-07')
    card.get_by_role('button',name='Marcar listo').click()
    expect(page.get_by_role('alert')).to_contain_text('Listo')
    shot(page,'34_comanda_lista.png','Comanda marcada lista para entrega')
    card=page.locator('article.kanban-card').filter(has_text='Mesa QA-07')
    card.get_by_role('button',name='Entregar pedido').click()
    expect(page.get_by_role('alert')).to_contain_text('Entregado')
    shot(page,'35_comanda_entregada.png','Pedido entregado sale de columnas activas')

    screen(page,'Inventario / Kardex','Inventario y Kardex')
    form=page.locator('form').filter(has=page.get_by_role('button',name='Guardar movimiento')).first
    form.get_by_label('Insumo').select_option(label='Harina')
    form.get_by_label('Variación (+ entrada, − salida)').fill('500')
    form.get_by_label('Motivo de la operación').fill('Reposición de harina para QA')
    form.get_by_role('button',name='Guardar movimiento').click()
    expect(page.get_by_role('alert')).to_contain_text('Movimiento de inventario registrado')
    shot(page,'36_kardex_reposicion_aprobada.png','Reposición de harina registrada con referencia en Kardex')

    screen(page,'Reportes de ventas','Reportes y análisis')
    expect(page.get_by_text('Yape').first).to_be_visible()
    shot(page,'37_reporte_ventas_yape_efectivo.png','Reporte desglosa ventas por método de pago')
    screen(page,'Analítica inteligente','Inteligencia operativa')
    shot(page,'38_analitica_ventas_confirmadas.png','Ranking descriptivo y proyección de demanda desde registros pagados')

    manifest['screenshot_count']=len(manifest['screenshots'])
    manifest_file.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print('TOTAL CAPTURAS REALES',len(manifest['screenshots']),flush=True)
    browser.close()