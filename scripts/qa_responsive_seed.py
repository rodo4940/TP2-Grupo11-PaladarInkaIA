"""Fijación de datos de laboratorio para pruebas responsive independientes del E2E extendido.
Crea un cobro no tributario y un cliente mediante FastAPI real, sin datos del restaurante."""
import os,httpx
API="http://127.0.0.1:8000/api/v1"
password=os.environ["SEED_ADMIN_PASSWORD"]
with httpx.Client(timeout=25) as client:
    signed=client.post(API+"/auth/token",json={"username":"admin","password":password})
    signed.raise_for_status()
    h={"Authorization":"Bearer "+signed.json()["access_token"]}
    def request(method,path,body=None):
        r=client.request(method,API+path,headers=h,json=body)
        assert r.status_code in (200,201), (method,path,r.status_code,r.text[:400])
        return r.json()
    products=request("GET","/products")
    assert products,"La semilla QA no tiene productos"
    first=products[0]
    order=request("POST","/orders",{"items":[{"product_id":first["id"],"quantity":1}],"table_label":"QA-Responsive-01","notes":"Registro demostrativo de test"})
    request("POST",f'/orders/{order["id"]}/payment',{"method":"cash","amount_cents":order["total_cents"]})
    request("POST","/customers",{"name":"Cliente QA Responsive"})
    print("Fixture responsive: 1 pago y 1 cliente registrados en PostgreSQL de laboratorio",flush=True)
