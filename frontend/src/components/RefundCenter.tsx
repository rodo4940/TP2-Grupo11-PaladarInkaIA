import {useCallback,useEffect,useState} from 'react';
import {api,post} from '../services/api';
import type {BillingDocument,InternalRefund,Role} from '../types/domain';

const money=(v:number)=>new Intl.NumberFormat('es-PE',{style:'currency',currency:'PEN'}).format(v/100);

/** Control administrativo: el sistema no envía fondos a ningún banco o billetera. */
export function RefundCenter({token,role,userId,entries,onChanged}:{
 token:string;role:Role;userId:number;entries:BillingDocument[];onChanged:()=>void;
}){
 const [requests,setRequests]=useState<InternalRefund[]>([]);
 const [paymentId,setPaymentId]=useState('');
 const [reason,setReason]=useState('');
 const [references,setReferences]=useState<Record<number,string>>({});
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState('');
 const [notice,setNotice]=useState('');
 const refresh=useCallback(async()=>{
   try {setRequests(await api<InternalRefund[]>('/billing/refunds',token));}
   catch(e){setError(e instanceof Error?e.message:'No se pudieron consultar las devoluciones');}
 },[token]);
 useEffect(()=>{void refresh()},[refresh]);
 const eligible=entries.filter(p=>!p.refund_status && !requests.some(r=>r.payment_id===p.id));
 const request=async()=>{
   const id=Number(paymentId);
   if(!id || reason.trim().length<10){setError('Selecciona un pago y explica el motivo (mínimo 10 caracteres).');return;}
   setBusy(true);setError('');setNotice('');
   try{
     await post<InternalRefund>('/billing/refunds',{payment_id:id,reason:reason.trim()},token);
     setNotice('Solicitud registrada. Otro responsable administrador debe comprobar el reintegro externo.');
     setPaymentId('');setReason('');await refresh();onChanged();
   }catch(e){setError(e instanceof Error?e.message:'No se pudo registrar la devolución')}
   finally{setBusy(false)}
 };
 const confirm=async(item:InternalRefund)=>{
   const external_reference=references[item.id]?.trim()??'';
   if(external_reference.length<5){setError('Registra la referencia comprobable del reintegro (mínimo 5 caracteres).');return}
   setBusy(true);setError('');setNotice('');
   try{
     await post<InternalRefund>(`/billing/refunds/${item.id}/confirm`,{external_reference},token);
     setNotice('Se registró la confirmación manual; conserva el comprobante del reintegro.');
     await refresh();onChanged();
   }catch(e){setError(e instanceof Error?e.message:'Error confirmando devolución')}
   finally{setBusy(false)}
 };
 return <section className="panel" aria-labelledby="refunds-title">
  <div className="panel-head"><div><span className="eyebrow">DOBLE CONTROL</span><h3 id="refunds-title">Devoluciones de pagos</h3>
   <p>Solicita la devolución total de un pago; una persona administradora distinta registra la referencia externa del reintegro.</p>
  </div></div>
  <div className="billing-disclaimer" role="note"><span aria-hidden="true">ⓘ</span><span>
   Este módulo <strong>NO transfiere dinero</strong> ni emite notas de crédito SUNAT. La confirmación exige verificar el reintegro fuera del sistema.</span></div>
  {error&&<p role="alert" className="notice error">{error}</p>}
  {notice&&<p role="status" className="notice">{notice}</p>}
  <div className="cash-closeout-actions">
   <label htmlFor="refund-payment">Pago a devolver</label>
   <select id="refund-payment" value={paymentId} onChange={e=>setPaymentId(e.target.value)}>
    <option value="">Selecciona el pago confirmado</option>
    {eligible.map(p=><option key={p.id} value={p.id}>{p.document_number} · {money(p.total_cents)}</option>)}
   </select>
   <label htmlFor="refund-reason">Motivo</label>
   <input id="refund-reason" maxLength={500} value={reason} onChange={e=>setReason(e.target.value)}
    placeholder="Describe el motivo de la solicitud" />
   <button type="button" className="primary" disabled={busy||!eligible.length} onClick={()=>void request()}>Solicitar devolución</button>
  </div>
  <div className="billing-entries" aria-label="Solicitudes de devolución">
   {requests.length===0&&<p>No se registraron solicitudes de devolución.</p>}
   {requests.map(item=><div key={item.id} className="billing-entry" style={{cursor:'default',display:'flex',flexWrap:'wrap',gap:'0.75rem',alignItems:'center'}}>
    <div className="billing-entry-body"><strong>Solicitud #{item.id} · Pedido #{item.order_id}</strong>
     <small>{money(item.amount_cents)} · {item.method} · {item.status==='confirmed'?'Confirmación manual':'Pendiente de confirmación'}</small>
     <small>Motivo: {item.reason}</small>
     {item.external_reference&&<small>Referencia: {item.external_reference}</small>}
    </div>
    {role==='admin'&&item.status==='pending'&&item.requested_by!==userId&&<div className="cash-closeout-actions">
     <label htmlFor={`refund-ref-${item.id}`}>Referencia del reintegro verificado</label>
     <input id={`refund-ref-${item.id}`} value={references[item.id]??''}
      onChange={e=>setReferences(old=>({...old,[item.id]:e.target.value}))} maxLength={120}
      placeholder="N.º de operación / recibo" />
     <button type="button" className="secondary" disabled={busy}
      onClick={()=>void confirm(item)}>Registrar confirmación manual</button>
    </div>}
   </div>)}
  </div>
 </section>;
}
