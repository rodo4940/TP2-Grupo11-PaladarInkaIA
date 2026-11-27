"""QA visual adicional: inventario negativo, altas, recetas, roles y adaptación móvil."""
import json
import os
import re
from pathlib import Path
from playwright.sync_api import sync_playwright,expect

out=Path('e2e/evidencias')
metadata=out/'e2e-results.json'
manifest=json.loads(metadata.read_text(encoding='utf8'))
base=os.environ.get('E2E_FRONTEND_URL','http://127.0.0.1:5173')
password=os.environ['SEED_ADMIN_PASSWORD']

def photo(page,name,detail):
    page.screenshot(path=str(out/name),full_page=True,animations='disabled')
    manifest['screenshots'].append({'file':name,'step':detail,'source':'Chromium real + React/FastAPI/PostgreSQL; datos ficticios'})
    print('CAPTURA AUTÉNTICA',name,flush=True)

def enter(page,login='admin'):
    page.goto(base)
    page.locator('input[autocomplete="username"]').fill(login)
    page.locator('input[autocomplete="current-password"]').fill(password)
    page.get_by_role('button',name='Ingresar al sistema').click()
    expect(page.get_by_role('heading',name='¡Bienvenido a Paladar Inka AI!')).to_be_visible()

def tab(page,title,heading):
    mobile_menu=page.get_by_role('button',name='Abrir menú')
    if mobile_menu.is_visible():
        mobile_menu.click()
    page.locator('nav').get_by_role('button',name=title).click()
    expect(page.get_by_role('heading',name=heading,exact=True).first).to_be_visible()

with sync_playwright() as p:
    browser=p.chromium.launch(channel='chrome',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':900},locale='es-PE')
    page.set_default_timeout(15000)
    enter(page)

    tab(page,'Inventario','Inventario y Kardex')
    form=page.locator('form').filter(has=page.get_by_role('button',name='Guardar movimiento')).first
    form.get_by_label('Insumo').select_option(label='Harina')
    form.get_by_label('Variación (+ entrada, − salida)').fill('-9999999')
    form.get_by_label('Motivo de la operación').fill('Prueba de stock insuficiente')
    form.get_by_role('button',name='Guardar movimiento').click()
    expect(page.get_by_role('alert')).to_contain_text('stock negativo')
    photo(page,'39_error_bloqueo_stock_negativo.png','Control de inventario rechaza saldo negativo')

    tab(page,'Productos','Productos y recetas')
    ingredient_form=page.locator('form').filter(has=page.get_by_role('button',name='Registrar insumo')).first
    ingredient_form.get_by_label('SKU').fill('QA-ING-39')
    ingredient_form.get_by_label('Nombre').fill('Rocoto de laboratorio QA')
    ingredient_form.get_by_label('Unidad').select_option('g')
    ingredient_form.get_by_label('Cantidad inicial').fill('2000')
    ingredient_form.get_by_label('Mínimo').fill('300')
    photo(page,'40_nuevo_insumo_completo.png','Formulario de alta de insumo con mínimos')
    ingredient_form.get_by_role('button',name='Registrar insumo').click()
    expect(page.get_by_role('alert')).to_contain_text('Insumo registrado')
    photo(page,'41_insumo_creado_en_postgresql.png','Nuevo insumo creado en persistencia')

    product_form=page.locator('form').filter(has=page.get_by_role('button',name='Registrar producto')).first
    product_form.get_by_label('SKU').fill('QA-PIZ-39')
    product_form.get_by_label('Nombre del producto').fill('Pizza integral de pruebas QA')
    product_form.get_by_label('Categoría').fill('Pizzas')
    product_form.get_by_label('Precio (S/)').fill('47.50')
    photo(page,'42_nuevo_producto_formulario.png','Formulario del nuevo producto de menú')
    product_form.get_by_role('button',name='Registrar producto').click()
    expect(page.get_by_role('alert')).to_contain_text('Producto creado')
    photo(page,'43_producto_registrado_catalogo.png','Producto creado con SKU único')

    recipe=page.locator('section.panel').filter(has=page.get_by_role('heading',name='Asignación de receta')).first
    recipe.get_by_label('Producto').select_option(label='Pizza integral de pruebas QA')
    for ingredient,amount in [('Harina (g )','220'),('Queso mozzarella (g )','130')]:
        ingredient_value=recipe.get_by_label('Insumo').locator('option').filter(has_text=ingredient.split(' (')[0]).first.get_attribute('value')
        assert ingredient_value, 'No se encontró el insumo requerido para la receta'
        recipe.get_by_label('Insumo').select_option(ingredient_value)
        recipe.get_by_label('Cantidad por unidad').fill(amount)
        recipe.get_by_role('button',name=re.compile('Agregar insumo')).click()
    photo(page,'44_receta_dos_ingredientes.png','Receta preparada con harina y queso')
    recipe.get_by_role('button',name=re.compile('Guardar receta')).click()
    expect(page.get_by_role('alert')).to_contain_text('Receta completa actualizada')
    photo(page,'45_receta_guardada_correctamente.png','Guardado de receta validado por el sistema')

    tab(page,'Ventas (POS)','Ventas / Caja POS')
    expect(page.get_by_role('button',name=re.compile('Pizza integral de pruebas QA'))).to_be_visible()
    page.get_by_role('button',name=re.compile('Pizza integral de pruebas QA')).click()
    photo(page,'46_producto_nuevo_disponible_en_pos.png','Producto con receta incorporado al POS')
    page.get_by_label('Mesa o referencia').fill('Mesa Cancelación QA')
    page.get_by_role('button',name='Confirmar pedido').click()
    expect(page.get_by_role('alert')).to_contain_text('Pedido creado')
    photo(page,'47_pedido_pendiente_de_cobro.png','Pedido no pagado conservado en backend')
    tab(page,'Pedidos','Gestión de pedidos')
    row=page.get_by_role('row').filter(has_text='Mesa Cancelación QA')
    row.get_by_role('button',name='Cancelar').click()
    expect(page.get_by_role('alert')).to_contain_text('Cancelado')
    photo(page,'48_cancelacion_pedido_no_pagado.png','Cancelación del pedido no cobrado')
    tab(page,'Inventario','Inventario y Kardex')
    photo(page,'49_kardex_reintegro_por_cancelacion.png','Kardex tras cancelación y reintegro de insumos')

    tab(page,'Usuarios','Usuarios y permisos')
    form=page.locator('form').filter(has=page.get_by_role('button',name='Crear cuenta')).first
    form.get_by_label('Usuario único').fill('qa_colaborador39')
    form.get_by_label('Nombre completo').fill('Colaborador control de accesos')
    form.get_by_label(re.compile('Contraseña inicial')).fill('TemporalQA2026Seguro!')
    form.get_by_label('Rol').select_option('cashier')
    photo(page,'50_nuevo_usuario_formulario.png','Alta de colaborador con rol de caja')
    form.get_by_role('button',name='Crear cuenta').click()
    expect(page.get_by_role('alert')).to_contain_text('Cuenta de colaborador creada')
    photo(page,'51_usuario_creado_y_visible.png','Cuenta nueva confirmada en tabla de usuarios')
    row=page.get_by_role('row').filter(has_text='qa_colaborador39')
    row.get_by_role('combobox').select_option('kitchen')
    expect(page.get_by_role('alert')).to_contain_text('Rol modificado')
    photo(page,'52_rol_de_usuario_cambiado.png','Cambio de rol de caja a cocina')
    row=page.get_by_role('row').filter(has_text='qa_colaborador39')
    row.get_by_role('button',name='Desactivar').click()
    expect(page.get_by_role('alert')).to_contain_text('Estado de cuenta actualizado')
    photo(page,'53_cuenta_desactivada.png','Cuenta de pruebas deshabilitada')

    cashier=browser.new_page(viewport={'width':1440,'height':900},locale='es-PE')
    enter(cashier,'cajero')
    assert cashier.locator('nav').get_by_role('button',name='Usuarios').count()==0
    photo(cashier,'54_cajero_acceso_controlado.png','Rol caja no ve módulo administración')
    tab(cashier,'Inventario','Inventario y Kardex')
    expect(cashier.get_by_text('Solo administración puede modificar las existencias.')).to_be_visible()
    photo(cashier,'55_cajero_no_puede_reponer.png','Rol caja consulta inventario sin modificar existencias')

    mobile=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,locale='es-PE',is_mobile=True,has_touch=True)
    mp=mobile.new_page();enter(mp,'cajero')
    photo(mp,'56_dashboard_movil_autenticado.png','Dashboard real de cajero en móvil 390×844')
    tab(mp,'Ventas (POS)','Ventas / Caja POS')
    photo(mp,'57_pos_movil_autenticado.png','POS responsive en móvil de cajero')

    tablet=browser.new_page(viewport={'width':820,'height':1180},locale='es-PE')
    enter(tablet)
    photo(tablet,'58_tablet_dashboard_autenticado.png','Dashboard real en tamaño tablet 820×1180')

    manifest['screenshot_count']=len(manifest['screenshots'])
    metadata.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    print('TOTAL CAPTURAS REALES',len(manifest['screenshots']),flush=True)
    browser.close()