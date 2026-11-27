"""Simulador CPE UBL 2.1 para laboratorio. NUNCA comunica con SUNAT.

Genera factura (01), boleta (03) y nota de crédito (07) de demostración,
con validaciones locales explícitas, XML, integridad y estado SIMULADO.
El XML carece de firma digital autorizada, certificado y CDR real:
NO ES un CPE válido ni reemplaza validación oficial UBL/XSD/catálogos.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
import re
from xml.etree import ElementTree as ET

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.auth import require_roles
from app.domain.models import AuditEvent, FiscalDemoDocument, Payment, User, Refund
from app.domain.billing_ai import LIMA

router=APIRouter()
cashier=require_roles('admin','cashier')
admin=require_roles('admin')
NOTICE='SIMULACIÓN ACADÉMICA SIN VALIDEZ TRIBUTARIA. NO EMITIDO NI CONSULTADO ANTE SUNAT.'
NS={
 'cbc':'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
 'cac':'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
 'Invoice':'urn:oasis:names:specification:ubl:schema:xsd:Invoice-2',
 'CreditNote':'urn:oasis:names:specification:ubl:schema:xsd:CreditNote-2',
}
for p,u in NS.items():
    if p not in ('Invoice','CreditNote'):ET.register_namespace(p,u)
SERIES={'01':'FDEM','03':'BDEM','07':'FNC1'}
TYPES={'01':'FACTURA_DEMO','03':'BOLETA_DEMO','07':'NOTA_CREDITO_DEMO'}
VALID_AFFECTATIONS={'10','20','30'}


class FiscalIssueIn(BaseModel):
    payment_id: int=Field(gt=0)
    document_type: str=Field(pattern='^(01|03)$')
    customer_document_type: str=Field(pattern='^(0|1|6)$')
    customer_document_number: str=Field(default='',max_length=11)
    customer_name: str=Field(min_length=3,max_length=160)
    affectation_code: str=Field(default='10',pattern='^(10|20|30)$')
    idempotency_key: str=Field(min_length=12,max_length=96,pattern=r'^[a-zA-Z0-9_.-]+$')

    @model_validator(mode='after')
    def check_customer(self):
        if self.document_type=='01' and self.customer_document_type!='6':
            raise ValueError('Factura demo requiere RUC de receptor')
        if self.customer_document_type=='6' and not valid_ruc(self.customer_document_number):
            raise ValueError('RUC de receptor con formato/dígito verificador inválido')
        if self.customer_document_type=='1' and not re.fullmatch(r'\d{8}',self.customer_document_number):
            raise ValueError('DNI de receptor debe tener 8 dígitos')
        if self.customer_document_type=='0' and self.customer_document_number:
            raise ValueError('Consumidor sin documento no puede tener número')
        return self


class FiscalCreditIn(BaseModel):
    original_document_id: int=Field(gt=0)
    reason_code: str=Field(default='01',pattern='^(01)$')
    reason: str=Field(min_length=10,max_length=250)
    idempotency_key: str=Field(min_length=12,max_length=96,pattern=r'^[a-zA-Z0-9_.-]+$')


def valid_ruc(value:str)->bool:
    """Dígito de control peruano; no garantiza vigencia en padrón SUNAT."""
    if not re.fullmatch(r'\d{11}',value) or value[:2] not in {'10','15','17','20'}:
        return False
    total=sum(int(d)*m for d,m in zip(value[:10],(5,4,3,2,7,6,5,4,3,2)))
    check=(11-total%11)%10
    return check==int(value[-1])


def money(cents:int)->str:
    return str((Decimal(cents)/100).quantize(Decimal('.01')))


def split_tax(gross:int,code:str)->tuple[int,int]:
    if code!='10':return gross,0
    net=int((Decimal(gross)*Decimal(100)/Decimal(118)).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
    return net,gross-net


def elem(parent:ET.Element,namespace:str,name:str,value:str|int|None=None,attrs:dict|None=None)->ET.Element:
    out=ET.SubElement(parent,f'{{{NS[namespace]}}}{name}',attrs or {})
    if value is not None:out.text=str(value)
    return out


def make_xml(doc:FiscalDemoDocument, payment:Payment, original:str|None=None)->str:
    is_credit=doc.document_type=='07'
    root=ET.Element(f'{{{NS["CreditNote" if is_credit else "Invoice"]}}}{"CreditNote" if is_credit else "Invoice"}')
    elem(root,'cbc','UBLVersionID','2.1')
    elem(root,'cbc','CustomizationID','2.0')
    elem(root,'cbc','ID',f'{doc.series}-{doc.correlative}')
    elem(root,'cbc','IssueDate',doc.issue_date)
    if is_credit:
        discrepancy=elem(root,'cac','DiscrepancyResponse')
        elem(discrepancy,'cbc','ReferenceID',original)
        elem(discrepancy,'cbc','ResponseCode','01')
        elem(discrepancy,'cbc','Description',doc.reason)
        reference=elem(root,'cac','BillingReference')
        invoice_ref=elem(reference,'cac','InvoiceDocumentReference')
        elem(invoice_ref,'cbc','ID',original)
    else:
        elem(root,'cbc','InvoiceTypeCode',doc.document_type,{'listID':'0101'})
    elem(root,'cbc','DocumentCurrencyCode','PEN')
    supplier=elem(root,'cac','AccountingSupplierParty')
    party=elem(supplier,'cac','Party')
    ident=elem(party,'cac','PartyIdentification')
    elem(ident,'cbc','ID','00000000000',{'schemeID':'6'})
    legal=elem(party,'cac','PartyLegalEntity')
    elem(legal,'cbc','RegistrationName','EL PALADAR DEL INKA - EMISOR FICTICIO DE PRUEBAS')
    customer=elem(root,'cac','AccountingCustomerParty')
    customer_party=elem(customer,'cac','Party')
    identification=elem(customer_party,'cac','PartyIdentification')
    elem(identification,'cbc','ID',doc.customer_document_number or '-',{'schemeID':doc.customer_document_type})
    legal=elem(customer_party,'cac','PartyLegalEntity')
    elem(legal,'cbc','RegistrationName',doc.customer_name)
    tax_total=elem(root,'cac','TaxTotal')
    elem(tax_total,'cbc','TaxAmount',money(doc.tax_cents),{'currencyID':'PEN'})
    subtotal=elem(tax_total,'cac','TaxSubtotal')
    elem(subtotal,'cbc','TaxableAmount',money(doc.net_cents),{'currencyID':'PEN'})
    elem(subtotal,'cbc','TaxAmount',money(doc.tax_cents),{'currencyID':'PEN'})
    category=elem(subtotal,'cac','TaxCategory')
    elem(category,'cbc','ID',doc.affectation_code)
    scheme=elem(category,'cac','TaxScheme')
    elem(scheme,'cbc','ID','1000' if doc.affectation_code=='10' else '9997')
    elem(scheme,'cbc','Name','IGV' if doc.affectation_code=='10' else 'EXO')
    elem(scheme,'cbc','TaxTypeCode','VAT' if doc.affectation_code=='10' else 'FRE')
    monetary=elem(root,'cac','LegalMonetaryTotal' if is_credit else 'LegalMonetaryTotal')
    elem(monetary,'cbc','LineExtensionAmount',money(doc.net_cents),{'currencyID':'PEN'})
    elem(monetary,'cbc','TaxInclusiveAmount',money(doc.total_cents),{'currencyID':'PEN'})
    elem(monetary,'cbc','PayableAmount',money(doc.total_cents),{'currencyID':'PEN'})
    lines=payment.order.items
    for n,line in enumerate(lines,1):
        gross=line.quantity*line.unit_price_cents
        net,tax=split_tax(gross,doc.affectation_code)
        one=elem(root,'cac','CreditNoteLine' if is_credit else 'InvoiceLine')
        elem(one,'cbc','ID',n)
        elem(one,'cbc','CreditedQuantity' if is_credit else 'InvoicedQuantity',line.quantity,{'unitCode':'NIU'})
        elem(one,'cbc','LineExtensionAmount',money(net),{'currencyID':'PEN'})
        subtotal=elem(one,'cac','TaxTotal')
        elem(subtotal,'cbc','TaxAmount',money(tax),{'currencyID':'PEN'})
        item=elem(one,'cac','Item')
        elem(item,'cbc','Description',line.product_name)
        price=elem(one,'cac','Price')
        elem(price,'cbc','PriceAmount',money(int(Decimal(net)/line.quantity)),{'currencyID':'PEN'})
    return ET.tostring(root,encoding='unicode',xml_declaration=False)


def response(doc:FiscalDemoDocument,include_xml:bool=False)->dict:
    payload={
      'id':doc.id,'payment_id':doc.payment_id,'document_type':doc.document_type,
      'document_label':TYPES[doc.document_type],'number':f'{doc.series}-{doc.correlative}',
      'issue_date':doc.issue_date,'currency':'PEN','total_cents':doc.total_cents,
      'net_cents':doc.net_cents,'tax_cents':doc.tax_cents,'affectation_code':doc.affectation_code,
      'customer_document_type':doc.customer_document_type,
      'customer_document_number':doc.customer_document_number,
      'customer_name':doc.customer_name,'reference_document_id':doc.reference_document_id,
      'status':'SIMULADO_VALIDADO_LOCALMENTE','sha256':doc.xml_sha256,
      'issuer_ruc':'00000000000','digital_signature':False,'sunat_submitted':False,
      'official_cdr':False,'warning':NOTICE,
    }
    if include_xml:payload['xml_demo']=doc.xml_demo
    return payload


@router.post('/fiscal-demo/documents',status_code=201)
def issue(payload:FiscalIssueIn,db:Session=Depends(get_db),user:User=Depends(cashier))->dict:
    current=db.scalar(select(FiscalDemoDocument).where(FiscalDemoDocument.idempotency_key==payload.idempotency_key))
    if current is not None:
        if (current.payment_id==payload.payment_id and current.document_type==payload.document_type
            and current.customer_document_number==payload.customer_document_number):
            return response(current)
        raise HTTPException(409,'La clave de idempotencia corresponde a otro documento')
    payment=db.get(Payment,payload.payment_id)
    if payment is None:raise HTTPException(404,'Pago no encontrado')
    existing=db.scalar(select(FiscalDemoDocument).where(FiscalDemoDocument.payment_id==payment.id,
                         FiscalDemoDocument.document_type.in_(['01','03'])))
    if existing:raise HTTPException(409,'Este pago ya tiene comprobante de demostración')
    if payment.refund and payment.refund.status=='confirmed':
        raise HTTPException(409,'No emitir comprobante original sobre pago ya devuelto')
    net,tax=split_tax(payment.amount_cents,payload.affectation_code)
    doc=FiscalDemoDocument(payment_id=payment.id,document_type=payload.document_type,
       series=SERIES[payload.document_type],correlative=0,
       issue_date=datetime.now(LIMA).date().isoformat(),customer_name=payload.customer_name,
       customer_document_number=payload.customer_document_number,
       customer_document_type=payload.customer_document_type,
       affectation_code=payload.affectation_code,total_cents=payment.amount_cents,
       net_cents=net,tax_cents=tax,xml_demo='',xml_sha256='',
       idempotency_key=payload.idempotency_key,created_by=user.id)
    db.add(doc)
    try:
        db.flush()
        doc.correlative=doc.id
        doc.xml_demo=make_xml(doc,payment)
        doc.xml_sha256=sha256(doc.xml_demo.encode()).hexdigest()
        db.add(AuditEvent(actor_id=user.id,action='fiscal.demo.issue',entity='fiscal_demo',
                          entity_id=doc.id,detail=f'{doc.series}-{doc.correlative};NO SUNAT'))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409,'Comprobante de laboratorio duplicado')
    return response(doc)


@router.post('/fiscal-demo/credit-notes',status_code=201)
def credit(payload:FiscalCreditIn,db:Session=Depends(get_db),user:User=Depends(admin))->dict:
    existing=db.scalar(select(FiscalDemoDocument).where(FiscalDemoDocument.idempotency_key==payload.idempotency_key))
    if existing is not None:
        if existing.reference_document_id==payload.original_document_id:return response(existing)
        raise HTTPException(409,'Idempotencia duplicada')
    original=db.get(FiscalDemoDocument,payload.original_document_id)
    if original is None:raise HTTPException(404,'Comprobante demo original no encontrado')
    if original.document_type not in ('01','03'):
        raise HTTPException(422,'Solo se admite nota sobre boleta/factura de laboratorio')
    payment=db.get(Payment,original.payment_id)
    if not payment.refund or payment.refund.status!='confirmed':
        raise HTTPException(409,'Requiere devolución confirmada manualmente antes de nota de prueba')
    if db.scalar(select(FiscalDemoDocument).where(FiscalDemoDocument.reference_document_id==original.id)):
        raise HTTPException(409,'Documento de demostración ya tiene nota de crédito')
    doc=FiscalDemoDocument(payment_id=payment.id,document_type='07',
       series='FNC1' if original.document_type=='01' else 'BNC1',correlative=0,
       issue_date=datetime.now(LIMA).date().isoformat(),
       customer_name=original.customer_name,
       customer_document_number=original.customer_document_number,
       customer_document_type=original.customer_document_type,
       affectation_code=original.affectation_code,
       total_cents=original.total_cents,net_cents=original.net_cents,
       tax_cents=original.tax_cents,xml_demo='',xml_sha256='',
       reference_document_id=original.id,reason=payload.reason,
       idempotency_key=payload.idempotency_key,created_by=user.id)
    db.add(doc)
    try:
        db.flush()
        doc.correlative=doc.id
        doc.xml_demo=make_xml(doc,payment,original=f'{original.series}-{original.correlative}')
        doc.xml_sha256=sha256(doc.xml_demo.encode()).hexdigest()
        db.add(AuditEvent(actor_id=user.id,action='fiscal.demo.credit',entity='fiscal_demo',
                          entity_id=doc.id,detail=f'original={original.id};NO SUNAT'))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409,'Nota de crédito demo duplicada')
    return response(doc)


@router.get('/fiscal-demo/documents')
def listing(db:Session=Depends(get_db),user:User=Depends(cashier))->list[dict]:
    return [response(row) for row in db.scalars(select(FiscalDemoDocument).order_by(
        FiscalDemoDocument.id.desc()).limit(250))]


@router.get('/fiscal-demo/documents/{document_id}')
def detail(document_id:int,db:Session=Depends(get_db),
           user:User=Depends(cashier))->dict:
    row=db.get(FiscalDemoDocument,document_id)
    if row is None:raise HTTPException(404,'Documento demo no encontrado')
    return response(row,include_xml=True)


@router.get('/fiscal-demo/documents/{document_id}/verify')
def verify(document_id:int,db:Session=Depends(get_db),
           user:User=Depends(cashier))->dict:
    row=db.get(FiscalDemoDocument,document_id)
    if row is None:raise HTTPException(404,'Documento demo no encontrado')
    valid=sha256(row.xml_demo.encode()).hexdigest()==row.xml_sha256
    return {'sha256_matches':valid,'xml_well_formed':_is_xml(row.xml_demo),
            'local_validation_only':True,'official_sunat_validation':False,
            'official_cdr':False,'warning':NOTICE}


def _is_xml(content:str)->bool:
    try:ET.fromstring(content);return True
    except ET.ParseError:return False
