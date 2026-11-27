"""Cobertura de contratos de simulador fiscal y entrenamiento de laboratorio."""
from hashlib import sha256
from xml.etree import ElementTree as ET
from tests.test_business import env, post_order


def _pay(client,auth):
    order=post_order(client,auth['cashier'])
    assert order.status_code==201
    payment=client.post(f"/api/v1/orders/{order.json()['id']}/payment",headers=auth['cashier'],
                        json={'method':'cash','amount_cents':3200})
    assert payment.status_code==201
    return payment.json()['id']


def test_fiscal_demo_boleta_xml_validation_and_no_real_sunat(env):
    c,a,_=env
    payment_id=_pay(c,a)
    data={'payment_id':payment_id,'document_type':'03',
          'customer_document_type':'0','customer_document_number':'',
          'customer_name':'Consumidor de laboratorio','idempotency_key':'LAB-DEMO-BOLETA-001'}
    issued=c.post('/api/v1/fiscal-demo/documents',headers=a['cashier'],json=data)
    assert issued.status_code==201,issued.text
    row=issued.json()
    assert row['number'].startswith('BDEM-')
    assert row['sunat_submitted'] is False and row['official_cdr'] is False
    assert row['total_cents']==3200
    assert row['total_cents']==row['net_cents']+row['tax_cents']
    assert row['tax_cents']>0
    assert 'SIMULACIÓN' in row['warning']
    repeat=c.post('/api/v1/fiscal-demo/documents',headers=a['cashier'],json=data)
    assert repeat.status_code==201 and repeat.json()['id']==row['id']
    check=c.get(f"/api/v1/fiscal-demo/documents/{row['id']}/verify",headers=a['cashier'])
    assert check.status_code==200 and check.json()['sha256_matches'] is True
    assert check.json()['official_sunat_validation'] is False
    xml=c.get(f"/api/v1/fiscal-demo/documents/{row['id']}",headers=a['cashier']).json()['xml_demo']
    assert sha256(xml.encode()).hexdigest()==row['sha256']
    root=ET.fromstring(xml)
    assert root.tag.endswith('Invoice')
    assert root.find('.//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}UBLVersionID').text=='2.1'
    bad=c.post('/api/v1/fiscal-demo/documents',headers=a['cashier'],json={
          **data,'idempotency_key':'LAB-DEMO-BOLETA-002'})
    assert bad.status_code==409
    assert c.get('/api/v1/fiscal-demo/documents',headers=a['kitchen']).status_code==403


def test_fiscal_demo_invoice_requires_ruc_and_tax_affectation(env):
    from app.domain.fiscal_demo import valid_ruc
    c,a,_=env
    payment_id=_pay(c,a)
    bad=c.post('/api/v1/fiscal-demo/documents',headers=a['cashier'],json={
        'payment_id':payment_id,'document_type':'01',
        'customer_document_type':'1','customer_document_number':'12345678',
        'customer_name':'Empresa de prueba','idempotency_key':'LAB-FACTURA-DNI-001'})
    assert bad.status_code==422
    prefix='2012345678'
    digit=(11-sum(int(d)*m for d,m in zip(prefix,(5,4,3,2,7,6,5,4,3,2)))%11)%10
    synthetic_ruc=prefix+str(digit)
    assert valid_ruc(synthetic_ruc)
    issue=c.post('/api/v1/fiscal-demo/documents',headers=a['cashier'],json={
        'payment_id':payment_id,'document_type':'01',
        'customer_document_type':'6','customer_document_number':synthetic_ruc,
        'customer_name':'Empresa de laboratorio','affectation_code':'20',
        'idempotency_key':'LAB-FACTURA-RUC-002'})
    assert issue.status_code==201,issue.text
    assert issue.json()['number'].startswith('FDEM-')
    assert issue.json()['tax_cents']==0


def test_fiscal_demo_credit_requires_confirmed_refund_and_reference(env):
    c,a,_=env
    payment_id=_pay(c,a)
    original=c.post('/api/v1/fiscal-demo/documents',headers=a['cashier'],json={
        'payment_id':payment_id,'document_type':'03','customer_document_type':'0',
        'customer_document_number':'','customer_name':'Consumidor ficticio',
        'idempotency_key':'LAB-CREDIT-ORIGINAL-001'}).json()
    payload={'original_document_id':original['id'],'reason_code':'01',
             'reason':'Anulación simulada total por devolución de prueba',
             'idempotency_key':'LAB-CREDIT-NOTE-001'}
    notyet=c.post('/api/v1/fiscal-demo/credit-notes',headers=a['admin'],json=payload)
    assert notyet.status_code==409
    req=c.post('/api/v1/billing/refunds',headers=a['cashier'],json={
        'payment_id':payment_id,'reason':'Devolución para prueba de nota crédito'})
    assert req.status_code==201
    confirm=c.post(f"/api/v1/billing/refunds/{req.json()['id']}/confirm",
                   headers=a['admin'],json={'external_reference':'TEST-REFUND-987'})
    assert confirm.status_code==200
    note=c.post('/api/v1/fiscal-demo/credit-notes',headers=a['admin'],json=payload)
    assert note.status_code==201,note.text
    assert note.json()['reference_document_id']==original['id']
    assert note.json()['number'].startswith('BNC1-')
    assert c.post('/api/v1/fiscal-demo/credit-notes',headers=a['admin'],
                 json={**payload,'idempotency_key':'LAB-CREDIT-SECOND-002'}).status_code==409
    assert c.post('/api/v1/fiscal-demo/credit-notes',headers=a['cashier'],json=payload).status_code==403
    note_xml=c.get(f"/api/v1/fiscal-demo/documents/{note.json()['id']}",
                   headers=a['cashier']).json()['xml_demo']
    assert ET.fromstring(note_xml).tag.endswith('CreditNote')


def test_trained_demo_is_fitted_with_chronological_holdout_and_identified_as_synthetic(env):
    from app.domain.trained_forecast import trained_demo,synthetic_history,train_on_authorized_daily_series
    c,a,_=env
    m=c.get('/api/v1/ai/trained-demo/metrics',headers=a['cashier'])
    assert m.status_code==200,m.text
    result=m.json()
    assert result['source_business_data'] is False
    assert result['dataset_origin']=='GENERADO_FICTICIO_DE_LABORATORIO'
    assert len(result['products'])==3 and len(result['dataset_sha256'])==64
    for values in result['products'].values():
        assert len(values['coefficients'])==9
        assert values['samples_train']==112 and values['samples_test']==28
        assert values['holdout']['mae']>=0 and values['baseline']['mae']>=0
    forecast=c.get('/api/v1/ai/trained-demo/forecast?days=7',headers=a['cashier'])
    assert forecast.status_code==200
    assert forecast.json()['mode']=='DEMO_MODELO_ENTRENADO_DATOS_SINTETICOS'
    assert len(forecast.json()['items'][0]['predictions'])==7
    assert c.get('/api/v1/ai/trained-demo/forecast?days=15',headers=a['cashier']).status_code==422
    assert c.get('/api/v1/ai/trained-demo/forecast',headers=a['kitchen']).status_code==403
    assert train_on_authorized_daily_series(synthetic_history()['PIZ-CLASICA'],100)['promoted'] is False


def test_fiscal_sandbox_is_disabled_in_real_production_mode(env,monkeypatch):
    from types import SimpleNamespace
    client,auth,_=env
    monkeypatch.setattr('app.domain.fiscal_demo.get_settings',
                        lambda: SimpleNamespace(app_env='production'))
    denied=client.get('/api/v1/fiscal-demo/documents',headers=auth['admin'])
    assert denied.status_code==403
    assert 'deshabilitado' in denied.json()['detail']


def test_fiscal_local_xml_rounding_is_consistent_with_two_items(env):
    client,auth,_=env
    # Dos unidades, mismas líneas: cálculo de total y subtotal recuperables.
    order=post_order(client,auth['cashier'],quantity=2)
    assert order.status_code==201
    paid=client.post(f"/api/v1/orders/{order.json()['id']}/payment",headers=auth['cashier'],
         json={'method':'cash','amount_cents':6400})
    assert paid.status_code==201
    doc=client.post('/api/v1/fiscal-demo/documents',headers=auth['cashier'],json={
      'payment_id':paid.json()['id'],'document_type':'03',
      'customer_document_type':'0','customer_document_number':'',
      'customer_name':'Consumidor ficticio','idempotency_key':'LAB-MULTI-UNITS-006'})
    assert doc.status_code==201,doc.text
    assert doc.json()['total_cents']==doc.json()['net_cents']+doc.json()['tax_cents']
