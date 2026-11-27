import os, json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, expect

OUT=Path("e2e/release-evidence")
OUT.mkdir(parents=True,exist_ok=True)
BASE=os.getenv("E2E_FRONTEND_URL","http://127.0.0.1:5173")
VIEWS=["Dashboard","Ventas (POS)","Finanzas / Caja","Pedidos","Cocina","Inventario","Productos","Clientes","Reportes","IA y recomendaciones","Usuarios","Configuración"]
SIZES=[(320,720),(360,780),(390,844),(430,932),(768,1024),(1024,768),(1440,900)]
records=[]
errors=[]
def capture(page, name, width, height):
    page.evaluate("document.fonts.ready")
    page.evaluate("Promise.all(Array.from(document.images).map(i=>i.decode().catch(()=>{})))")
    metric=page.evaluate("({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})")
    path=OUT/f"{width}_{len(records):03d}.png"
    page.screenshot(path=str(path),animations="disabled",full_page=True)
    records.append(dict(module=name,width=width,height=height,file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),overflow=metric["scrollWidth"]>metric["width"]+2,commit=os.getenv("GITHUB_SHA","local"),utc=datetime.now(timezone.utc).isoformat()))
    (OUT/"manifest.json").write_text(json.dumps(records,ensure_ascii=False,indent=2))
with sync_playwright() as p:
    browser=p.chromium.launch()
    for width,height in SIZES:
        ctx=browser.new_context(viewport=dict(width=width,height=height),has_touch=width<=1024,locale="es-PE",device_scale_factor=1,reduced_motion="reduce")
        page=ctx.new_page()
        page.on("pageerror",lambda e:errors.append(str(e)))
        page.goto(BASE)
        expect(page.locator('input[autocomplete="username"]')).to_be_visible()
        capture(page,"Login",width,height)
        page.locator('input[autocomplete="username"]').fill("admin")
        page.locator('input[autocomplete="current-password"]').fill(os.environ["SEED_ADMIN_PASSWORD"])
        page.get_by_role("button",name="Ingresar al sistema").click()
        expect(page.locator(".environment")).to_contain_text("Datos sincronizados",timeout=30000)
        for name in VIEWS:
            if name!="Dashboard":
                toggle=page.get_by_role("button",name="Abrir menú")
                if toggle.is_visible() and "sidebar-open" not in (page.locator(".sidebar").get_attribute("class") or ""): toggle.click()
                nav=page.locator("nav").get_by_role("button",name=name,exact=True).first
                nav.click()
                expect(nav).to_have_attribute("aria-current","page")
            expect(page.locator("#main-content")).to_be_visible()
            capture(page,name,width,height)
        ctx.close()
    browser.close()
(OUT/"result.json").write_text(json.dumps(dict(count=len(records),errors=errors,overflow=[r for r in records if r["overflow"]]),ensure_ascii=False,indent=2))
assert len(records)==91
assert not errors,errors
assert not any(r["overflow"] for r in records)
