"""Devoluciones manuales y arqueo de caja con control de dos personas.

No se transfiere dinero ni se emiten CPE SUNAT. El estado 'confirmed'
es una constancia humana basada en una referencia externa, NO una verificación
automática del banco, PSP, OSE ni SUNAT.
"""
from datetime import date, datetime, time, timedelta, timezone
from hashlib import sha256
import json
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.auth import require_roles
from app.domain.models import AuditEvent, CashCloseout, Payment, Refund, User

router = APIRouter()
cashier = require_roles('admin', 'cashier')
admin = require_roles('admin')
LIMA = ZoneInfo('America/Lima')
DISCLAIMER = ('Operación registrada manualmente. No ejecuta una devolución bancaria, '
              'no equivale a comprobante SUNAT ni acredita recepción del dinero.')


class RefundRequestIn(BaseModel):
    payment_id: int = Field(gt=0)
    reason: str = Field(min_length=10, max_length=500)


class RefundConfirmIn(BaseModel):
    external_reference: str = Field(min_length=5, max_length=120)


class CloseoutSubmitIn(BaseModel):
    day: date
    opening_cash_cents: int = Field(ge=0, le=1000000000)
    counted_cash_cents: int = Field(ge=0, le=1000000000)
    note: str = Field(default='', max_length=500)


class CloseoutApprovalIn(BaseModel):
    approval_note: str = Field(min_length=8, max_length=500)


def audit(db: Session, user: User, action: str, entity: str, entity_id: int, detail: str) -> None:
    db.add(AuditEvent(actor_id=user.id, action=action, entity=entity,
                      entity_id=entity_id, detail=detail[:500]))


def boundaries(day: date) -> tuple[datetime, datetime]:
    start = datetime.combine(day, time.min, tzinfo=LIMA).astimezone(timezone.utc)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=LIMA).astimezone(timezone.utc)
    return start, end


def daily_totals(db: Session, day: date) -> dict:
    """Flujo del día local: ingresos del día menos devoluciones CONFIRMADAS ese día."""
    start, end = boundaries(day)
    payments = list(db.scalars(select(Payment).where(
        Payment.created_at >= start, Payment.created_at < end)))
    refunds = list(db.scalars(select(Refund).where(
        Refund.status == 'confirmed', Refund.confirmed_at >= start,
        Refund.confirmed_at < end)))
    methods = ('cash', 'card', 'yape', 'plin')
    gross = {method: 0 for method in methods}
    returned = {method: 0 for method in methods}
    for payment in payments:
        gross[payment.method] += payment.amount_cents
    for refund in refunds:
        returned[refund.payment.method] += refund.payment.amount_cents
    return {
        'payments_count': len(payments),
        'refunds_count': len(refunds),
        'gross_payments_cents': sum(gross.values()),
        'confirmed_refunds_cents': sum(returned.values()),
        'net_cash_flow_cents': sum(gross.values()) - sum(returned.values()),
        'cash_movement_cents': gross['cash'] - returned['cash'],
        'refunds_by_method': returned,
    }


def refund_response(item: Refund) -> dict:
    return {
        'id': item.id, 'payment_id': item.payment_id,
        'order_id': item.payment.order_id, 'method': item.payment.method,
        'amount_cents': item.payment.amount_cents, 'reason': item.reason,
        'status': item.status, 'requested_by': item.requested_by,
        'confirmed_by': item.confirmed_by,
        'external_reference': item.confirmation_reference,
        'created_at': item.created_at.isoformat(),
        'confirmed_at': item.confirmed_at.isoformat() if item.confirmed_at else None,
        'disclaimer': DISCLAIMER,
    }


def closeout_response(item: CashCloseout, current: dict) -> dict:
    stale = any((
        item.gross_payments_cents != current['gross_payments_cents'],
        item.confirmed_refunds_cents != current['confirmed_refunds_cents'],
        item.payments_count != current['payments_count'],
        item.refunds_count != current['refunds_count'],
        item.expected_cash_cents != item.opening_cash_cents + current['cash_movement_cents'],
    ))
    return {
        'id': item.id, 'day': item.day, 'state': item.state,
        'opening_cash_cents': item.opening_cash_cents,
        'expected_cash_cents': item.expected_cash_cents,
        'counted_cash_cents': item.counted_cash_cents,
        'variance_cents': item.variance_cents,
        'gross_payments_cents': item.gross_payments_cents,
        'confirmed_refunds_cents': item.confirmed_refunds_cents,
        'payments_count': item.payments_count, 'refunds_count': item.refunds_count,
        'submitted_by': item.submitted_by, 'approved_by': item.approved_by,
        'note': item.note, 'approval_note': item.approval_note,
        'created_at': item.created_at.isoformat(),
        'approved_at': item.approved_at.isoformat() if item.approved_at else None,
        'finalized_at': item.finalized_at.isoformat() if item.finalized_at else None,
        'finalized_by': item.finalized_by,
        'snapshot_sha256': item.snapshot_sha256,
        'stale': stale,
        'disclaimer': 'Arqueo interno firmado por usuarios del sistema; no cierre tributario ni bancario.',
    }


@router.post('/billing/refunds', status_code=201)
def request_refund(payload: RefundRequestIn, db: Session = Depends(get_db),
                   actor: User = Depends(cashier)) -> dict:
    payment = db.get(Payment, payload.payment_id)
    if payment is None:
        raise HTTPException(404, 'Pago no encontrado')
    if db.scalar(select(Refund).where(Refund.payment_id == payment.id)) is not None:
        raise HTTPException(409, 'Ya existe una solicitud de devolución para este pago')
    refund = Refund(payment_id=payment.id, requested_by=actor.id, reason=payload.reason)
    db.add(refund)
    try:
        db.flush()
        audit(db, actor, 'refund.request', 'refund', refund.id, f'payment={payment.id}')
        db.commit()
        db.refresh(refund)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Devolución ya solicitada')
    return refund_response(refund)


@router.get('/billing/refunds')
def list_refunds(db: Session = Depends(get_db), actor: User = Depends(cashier)) -> list[dict]:
    entries = db.scalars(select(Refund).order_by(Refund.id.desc()).limit(300))
    return [refund_response(item) for item in entries]


@router.post('/billing/refunds/{refund_id}/confirm')
def confirm_refund(refund_id: int, payload: RefundConfirmIn,
                   db: Session = Depends(get_db), actor: User = Depends(admin)) -> dict:
    item = db.scalar(select(Refund).where(Refund.id == refund_id).with_for_update(of=Refund))
    if item is None:
        raise HTTPException(404, 'Solicitud no encontrada')
    if item.status != 'pending':
        raise HTTPException(409, 'La devolución ya fue confirmada')
    if item.requested_by == actor.id:
        raise HTTPException(409, 'La persona solicitante no puede autorizar su propia devolución')
    today=datetime.now(LIMA).date().isoformat()
    frozen=db.scalar(select(CashCloseout).where(CashCloseout.day==today).with_for_update())
    if frozen and frozen.state=='finalized':
        raise HTTPException(409,'Caja del día finalizada; devolución requiere proceso autorizado')
    item.status = 'confirmed'
    item.confirmed_by = actor.id
    item.confirmation_reference = payload.external_reference.strip()
    item.confirmed_at = datetime.now(timezone.utc)
    audit(db, actor, 'refund.confirm.manual', 'refund', item.id,
          f'payment={item.payment_id}; reference={item.confirmation_reference}')
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'La referencia de confirmación ya está registrada')
    db.refresh(item)
    return refund_response(item)


@router.get('/billing/closeouts/{day}')
def get_closeout(day: date, db: Session = Depends(get_db),
                 actor: User = Depends(cashier)) -> dict:
    item = db.scalar(select(CashCloseout).where(CashCloseout.day == day.isoformat()))
    if item is None:
        raise HTTPException(404, 'Todavía no existe arqueo registrado para esta fecha')
    return closeout_response(item, daily_totals(db, day))


@router.post('/billing/closeouts', status_code=201)
def submit_closeout(payload: CloseoutSubmitIn, db: Session = Depends(get_db),
                    actor: User = Depends(cashier)) -> dict:
    if payload.day > datetime.now(LIMA).date():
        raise HTTPException(422, 'No se permite crear arqueos de fechas futuras')
    existing = db.scalar(select(CashCloseout).where(CashCloseout.day == payload.day.isoformat()))
    if existing is not None:
        raise HTTPException(409, 'Ya existe un arqueo para esta fecha')
    totals = daily_totals(db, payload.day)
    expected = payload.opening_cash_cents + totals['cash_movement_cents']
    item = CashCloseout(
        day=payload.day.isoformat(), opening_cash_cents=payload.opening_cash_cents,
        expected_cash_cents=expected, counted_cash_cents=payload.counted_cash_cents,
        variance_cents=payload.counted_cash_cents - expected,
        gross_payments_cents=totals['gross_payments_cents'],
        confirmed_refunds_cents=totals['confirmed_refunds_cents'],
        payments_count=totals['payments_count'], refunds_count=totals['refunds_count'],
        submitted_by=actor.id, note=payload.note)
    db.add(item)
    try:
        db.flush()
        audit(db, actor, 'closeout.submit', 'cash_closeout', item.id,
              f'day={item.day}; variance={item.variance_cents}')
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, 'Ya existe arqueo para esta fecha')
    db.refresh(item)
    return closeout_response(item, totals)


@router.post('/billing/closeouts/{closeout_id}/approve')
def approve_closeout(closeout_id: int, payload: CloseoutApprovalIn,
                     db: Session = Depends(get_db), actor: User = Depends(admin)) -> dict:
    item = db.scalar(select(CashCloseout).where(CashCloseout.id == closeout_id).with_for_update())
    if item is None:
        raise HTTPException(404, 'Arqueo no encontrado')
    if item.state != 'submitted':
        raise HTTPException(409, 'Este arqueo ya está aprobado')
    if item.submitted_by == actor.id:
        raise HTTPException(409, 'La persona que registra caja no puede aprobar su propio arqueo')
    current = daily_totals(db, date.fromisoformat(item.day))
    if closeout_response(item, current)['stale']:
        raise HTTPException(409, 'Los pagos/devoluciones cambiaron después del arqueo; requiere revisión manual')
    item.state = 'approved'
    item.approved_by = actor.id
    item.approved_at = datetime.now(timezone.utc)
    item.approval_note = payload.approval_note
    audit(db, actor, 'closeout.approve.internal', 'cash_closeout', item.id,
          f'day={item.day}; variance={item.variance_cents}')
    db.commit()
    db.refresh(item)
    return closeout_response(item, current)


class FinalizeIn(BaseModel):
    final_note: str=Field(min_length=12,max_length=500)


def snapshot_sha(item:CashCloseout)->str:
    fields={
        'day':item.day,'opening_cash_cents':item.opening_cash_cents,
        'expected_cash_cents':item.expected_cash_cents,'counted_cash_cents':item.counted_cash_cents,
        'variance_cents':item.variance_cents,'gross_payments_cents':item.gross_payments_cents,
        'confirmed_refunds_cents':item.confirmed_refunds_cents,'payments_count':item.payments_count,
        'refunds_count':item.refunds_count,'submitted_by':item.submitted_by,
        'approved_by':item.approved_by,'approval_note':item.approval_note,
    }
    return sha256(json.dumps(fields,sort_keys=True,separators=(',',':'),
                              ensure_ascii=False).encode()).hexdigest()


@router.post('/billing/closeouts/{closeout_id}/finalize')
def finalize_closeout(closeout_id:int,payload:FinalizeIn,db:Session=Depends(get_db),
                      actor:User=Depends(admin))->dict:
    """Bloquea internamente el período; no constituye declaración tributaria."""
    item=db.scalar(select(CashCloseout).where(CashCloseout.id==closeout_id).with_for_update())
    if item is None:raise HTTPException(404,'Arqueo no encontrado')
    if item.state!='approved':
        raise HTTPException(409,'Solo se finaliza un arqueo aprobado')
    if item.submitted_by==actor.id:
        raise HTTPException(409,'La persona que registró caja no puede finalizarla')
    current=daily_totals(db,date.fromisoformat(item.day))
    if closeout_response(item,current)['stale']:
        raise HTTPException(409,'Los movimientos cambiaron; se requiere conciliación nueva')
    if db.scalar(select(Refund.id).where(Refund.status=='pending')) is not None:
        raise HTTPException(409,'Existen devoluciones pendientes')
    item.state='finalized';item.finalized_by=actor.id
    item.finalized_at=datetime.now(timezone.utc)
    item.snapshot_sha256=snapshot_sha(item)
    audit(db,actor,'closeout.finalize.internal','cash_closeout',item.id,
          f'day={item.day};hash={item.snapshot_sha256[:16]};{payload.final_note[:140]}')
    db.commit();db.refresh(item)
    return closeout_response(item,current)


@router.get('/billing/closeouts/{day}/integrity')
def integrity(day:date,db:Session=Depends(get_db),actor:User=Depends(cashier))->dict:
    item=db.scalar(select(CashCloseout).where(CashCloseout.day==day.isoformat()))
    if item is None:raise HTTPException(404,'Arqueo no encontrado')
    current=daily_totals(db,day)
    digest=snapshot_sha(item)
    return {'day':day.isoformat(),'state':item.state,
            'hash_saved':item.snapshot_sha256,'hash_current':digest,
            'hash_valid':item.state=='finalized' and digest==item.snapshot_sha256,
            'movements_unchanged':not closeout_response(item,current)['stale'],
            'scope':'INTEGRIDAD INTERNA; NO HOMOLOGACIÓN SUNAT NI BANCARIA'}
