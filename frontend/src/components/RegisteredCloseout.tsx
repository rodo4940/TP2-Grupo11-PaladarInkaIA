import {useCallback,useEffect,useState} from 'react';
import {api,ApiError,post} from '../services/api';
import type {RegisteredCashCloseout,Role} from '../types/domain';

const money=(v:number)=>new Intl.NumberFormat('es-PE',{style:'currency',currency:'PEN'}).format(v/100);
const parseCash=(value:string)=>{
 const clean=value.trim().replace(',','.');
 if(!/^\d{1,10}(\.\d{1,2})?$/.test(clean))return null;
 const n=Math.round(Number(clean)*100);
 return Number.isSafeInteger(n)?n:null;
};

/** Arqueo interno: registra conteo y doble aprobación, sin movimiento financiero. */
export function RegisteredCloseout({token,day,role,userId,countedCashCents}:{
 token:string;day:string;role:Role;userId:number;countedCashCents:number|null;
}){
 const [record,setRecord]=useState<RegisteredCashCloseout|null>(null);
 const [opening,setOpening]=useState('0');
 const [note,setNote]=useState('');
 const [approvalNote,setApprovalNote]=useState('');
 const [error,setError]=useState('');
 const [message,setMessage]=useState('');
 const [busy,setBusy]=useState(false);
 const refresh=useCallback(async()=>{
   try {setRecord(await api<RegisteredCashCloseout>(`/billing/closeouts/${day}`,token));}
   catch(e){if(e instanceof ApiError&&e.status===404)setRecord(null);
     else setError(e instanceof Error?e.message:'No fue posible consultar el arqueo');}
 },[day,token]);
 useEffect(()=>{void refresh()},[refresh]);
 const save=async()=>{
  const opening_cash_cents=parseCash(opening);
  if(opening_cash_cents===null||countedCashCents===null){setError('Ingresa fondo inicial y efectivo contado válidos.');return}
  setBusy(true);setError('');setMessage('');
  try{
   setRecord(await post<RegisteredCashCloseout>('/billing/closeouts',{
    day,opening_cash_cents,counted_cash_cents:countedCashCents,note
   },token));
   setMessage('Arqueo registrado. Falta revisión por otra persona administradora.');
  }catch(e){setError(e instanceof Error?e.message:'No se pudo registrar el arqueo')}
  finally{setBusy(false)}
 };
 const approve=async()=>{
  if(!record||approvalNote.trim().length<8){setError('Escribe una nota de verificación (mínimo 8 caracteres).');return}
  setBusy(true);setError('');setMessage('');
  try{
   setRecord(await post<RegisteredCashCloseout>(`/billing/closeouts/${record.id}/approve`,
    {approval_note:approvalNote.trim()},token));
   setMessage('Arqueo interno aprobado con registro de responsable y fecha.');
  }catch(e){setError(e instanceof Error?e.message:'No se pudo aprobar')}
  finally{setBusy(false)}
 };
 return <div className="cash-closeout-bottom" style={{marginTop:'1rem',flexWrap:'wrap'}}>
  <div className="cash-physical-count" style={{flex:'1 1 220px'}}>
   <h4>Arqueo registrado</h4>
   {error&&<p role="alert" className="notice error">{error}</p>}
   {message&&<p role="status" className="notice">{message}</p>}
   {!record?<div className="cash-closeout-actions">
     <label htmlFor="cash-opening">Fondo inicial de caja (S/)</label>
     <input id="cash-opening" inputMode="decimal" value={opening}
      onChange={e=>setOpening(e.target.value)} placeholder="0.00"/>
     <label htmlFor="cash-closeout-note">Observaciones</label>
     <input id="cash-closeout-note" value={note} maxLength={500}
      onChange={e=>setNote(e.target.value)} placeholder="Vouchers, diferencias, incidencias"/>
     <button type="button" className="secondary" disabled={busy||countedCashCents===null}
      onClick={()=>void save()}>Registrar arqueo del día</button>
    </div>:
    <div>
     <p><strong>{record.state==='approved'?'Aprobado internamente':'Pendiente de aprobación'}</strong>
      {record.stale?' · Datos cambiaron desde el arqueo':''}</p>
     <p>Esperado: {money(record.expected_cash_cents)} · Contado: {money(record.counted_cash_cents)}</p>
     <p>Diferencia: <strong>{money(record.variance_cents)}</strong></p>
     <p>Registrado por usuario #{record.submitted_by}
      {record.approved_by?` · Aprobado por #${record.approved_by}`:''}</p>
     {role==='admin'&&record.state==='submitted'&&record.submitted_by!==userId&&
      <div className="cash-closeout-actions">
       <label htmlFor="cash-approval-note">Nota de revisión independiente</label>
       <input id="cash-approval-note" value={approvalNote} maxLength={500}
        onChange={e=>setApprovalNote(e.target.value)} placeholder="Verifiqué efectivo y vouchers"/>
       <button type="button" className="primary" disabled={busy||record.stale}
        onClick={()=>void approve()}>Aprobar arqueo interno</button>
      </div>}
    </div>}
  </div>
  <p className="cash-closeout-legal" style={{flex:'1 1 220px'}}>
   Esta aprobación registra una revisión humana, no confirma depósitos bancarios ni genera cierre
   contable o comprobantes electrónicos. Si cambian pagos o devoluciones, el registro queda marcado
   como desactualizado y requiere revisión.</p>
 </div>;
}
