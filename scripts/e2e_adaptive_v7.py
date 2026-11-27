"""Pruebas responsive v7: captura real por viewport, no imágenes simuladas."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from playwright.sync_api import sync_playwright,expect
from html import escape
import json,os,struct

BASE=os.getenv("E2E_FRONTEND_URL","http://127.0.0.1:5173")
PASSWORD=os.environ["SEED_ADMIN_PASSWORD"]
OUT=Path("e2e/adaptive-v7");OUT.mkdir(parents=True,exist_ok=True)
SIZES=[(320,720),(360,780),(390,844),(430,932),(768,1024),(1024,768),(1440,900)]
VIEWS=[
 ("dashboard","Panel general","Resumen operativo"),
 ("pos","Ventas / POS","Nuevo pedido"),
 ("orders","Pedidos","Gestión de pedidos"),
 ("kitchen","Cocina","Comandas de cocina"),
 ("inventory","Inventario / Kardex","Inventario y Kardex"),
 ("products","Productos y recetas","Productos y recetas"),
 ("customers","Clientes","Clientes"),
 ("reports","Reportes de ventas","Reportes y análisis"),
 ("ai","Analítica inteligente","Inteligencia operativa"),
 ("users","Usuarios y roles","Usuarios y permisos"),
 ("settings","Configuración","Configuración del entorno"),
 ("billing","Caja y comprobantes","Caja y comprobantes"),
]
captures=[]
errors=[]

def save(page,key):
    m=page.evaluate("""() => {
      const d=document.documentElement,bar=document.querySelector('.mobile-dock');
      const box=bar?.getBoundingClientRect();
      return {width:innerWidth,scrollWidth:d.scrollWidth,
        overflow:d.scrollWidth>innerWidth+1,
        dock:!!box&&box.width>0,
        dockBottom:box?.bottom??0,
        targets:[...document.querySelectorAll('.mobile-dock button')].filter(x=>x.getClientRects().length).map(x=>({w:x.getBoundingClientRect().width,h:x.getBoundingClientRect().height}))}
    }""")
    assert not m["overflow"],(key,m)
    if page.viewport_size["width"]<=700:
        assert m["dock"] and m["dockBottom"]<=page.viewport_size["height"]+2,(key,m)
        assert all(t["w"]>=42 and t["h"]>=44 for t in m["targets"]),(key,m)
    else:
        assert not m["dock"],(key,m)
    filename=f'{len(captures)+1:03d}_{key}.png'
    path=OUT/filename
    page.screenshot(path=str(path),animations="disabled",full_page=False)
    raw=path.read_bytes();w,h=struct.unpack(">II",raw[16:24])
    assert (w,h)==(page.viewport_size["width"],page.viewport_size["height"]),(filename,w,h)
    captures.append({"file":filename,"scenario":key,"sha256":sha256(raw).hexdigest(),"metrics":m})
    print("RESPONSIVE V7",filename,w,h,flush=True)

def nav(page,label,heading,drawer):
    if drawer:
        page.get_by_role("button",name="Abrir menú").click()
        expect(page.get_by_role("button",name="Cerrar navegación")).to_be_visible()
        assert page.evaluate("document.body.style.overflow")=="hidden"
    btn=page.locator("nav").get_by_role("button",name=label,exact=True)
    btn.click()
    expect(page.get_by_role("heading",name=heading,exact=True).first).to_be_visible()
    expect(btn).to_have_attribute("aria-current","page")
    if drawer:
        assert page.evaluate("document.body.style.overflow")!="hidden"

with sync_playwright() as p:
    browser=p.chromium.launch(channel="chrome",headless=True,args=["--no-sandbox"])
    for w,h in SIZES:
        touch=w<500
        ctx=browser.new_context(viewport={"width":w,"height":h},device_scale_factor=1,
                                is_mobile=touch,has_touch=touch,locale="es-PE",reduced_motion="reduce")
        page=ctx.new_page()
        page.set_default_timeout(30000)
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.goto(BASE,wait_until="domcontentloaded")
        expect(page.get_by_role("heading",name="Bienvenido")).to_be_visible()
        save(page,f"{w}_login")
        page.locator('input[autocomplete="username"]').fill("admin")
        page.locator('input[autocomplete="current-password"]').fill(PASSWORD)
        page.get_by_role("button",name="Ingresar al sistema").click()
        expect(page.get_by_role("heading",name="Resumen operativo",exact=True)).to_be_visible()
        expect(page.locator(".environment")).to_contain_text("Datos sincronizados")
        save(page,f"{w}_dashboard")
        for key,label,heading in VIEWS[1:]:
            nav(page,label,heading,w<=880)
            if w<=700 and key in ("orders","inventory","products","customers","users"):
                loc=page.locator(f".{key}-mobile-cards tbody tr")
                expect(loc.first).to_be_visible()
                assert loc.first.evaluate("(el)=>getComputedStyle(el).display")=="block"
                assert loc.first.locator("td[data-label]").count()>=4
            if key=="billing":
                expect(page.get_by_role("heading",name="Resumen diario de caja")).to_be_visible()
                expect(page.locator(".cash-method-grid article")).to_have_count(4)
            if key=="ai":
                expect(page.get_by_role("heading",name="Consulta tu operación")).to_be_visible()
            save(page,f"{w}_{key}")
        ctx.close()
    browser.close()
assert len(captures)==91,(len(captures),91)
assert not errors,errors
data={"created_utc":datetime.now(timezone.utc).isoformat(),
      "source":"Chromium/React/FastAPI/PostgreSQL reales, datos de QA ficticios",
      "count":len(captures),"widths":[x[0] for x in SIZES],
      "javascript_errors":errors,"captures":captures}
(OUT/"RESULTADOS_RESPONSIVE_V7.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
cards=[]
for item in captures:
    name=escape(item["file"],quote=True)
    cards.append('<article><a href="'+name+'" target="_blank"><img loading="lazy" src="'+name+'" alt="'+name+'"/></a><strong>'+name+'</strong><small>SHA256 '+item["sha256"][:16]+'…</small></article>')
html='''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>El Paladar del Inka · Responsive v7</title><style>body{font:14px system-ui;margin:0;background:#f6f5ee;color:#244733}header{background:#174230;color:white;padding:35px}header h1{font-size:clamp(26px,5vw,46px)}main{padding:25px;max-width:1500px;margin:auto}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:16px}article{border-radius:16px;overflow:hidden;background:white;border:1px solid #dce7da;padding-bottom:13px}img{display:block;width:100%;height:310px;object-fit:contain;background:#faf9f6}article strong,article small{display:block;padding:9px 13px;overflow-wrap:anywhere}small{color:#657668;font-size:10px}</style></head><body><header><h1>91 capturas responsive verificables</h1><p>Siete resoluciones, 12 módulos y acceso. Capturas de viewport exacto y hashes SHA-256; entorno de pruebas, no aceptación empresarial.</p></header><main><section class="grid">'''+''.join(cards)+'''</section></main></body></html>'''
(OUT/"GALERIA_RESPONSIVE_V7.html").write_text(html,encoding="utf-8")
print("V7: 91 CAPTURAS, 7 BREAKPOINTS, 0 OVERFLOW, 0 ERRORES",flush=True)
