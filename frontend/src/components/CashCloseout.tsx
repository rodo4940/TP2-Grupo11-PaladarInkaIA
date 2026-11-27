import {useEffect,useMemo,useState} from 'react';
import {api} from '../services/api';
import type {DailyCashSummary} from '../types/domain';

const amount=(c:number)=>new Intl.NumberFormat('es-PE',{style:'currency',currency:'PEN'}).format(c/100);
const todayInPeru=()=>{
 const d=new Intl.DateTimeFormat('en-US',{timeZone:'America/Lima',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
 const get=(type:string)=>d.find(x=>x.type===type)?.value??'';
 return `${get('year')}-${get('month')}-${get('day')}`;
};
const names:Record<string,string>={cash:'Efectivo',card:'Tarjeta',yape:'Yape',plin:'Plin'};

export function CashCloseout({token}:{token:string}){
 const [day,setDay]=useState(todayInPeru);
 const [summary,setSummary]=useState<DailyCashSummary|null>(null);
 const [error,setError]=useState('');
 const [busy,setBusy]=useState(false);
 const [physicalCash,setPhysicalCash]=useState('');
 useEffect(()=>{
   let mounted=true;
   setBusy(true);setError('');
   void api<DailyCashSummary>(`/billing/daily-summary?day=${encodeURIComponent(day)}`,token)
    .then(value=>{if(mounted)setSummary(value)})
    .catch(e=>{if(mounted){setSummary(null);setError(e instanceof Error?e.message:'No se pudo consultar el cierre')}})
    .finally(()=>{if(mounted)setBusy(false)});
   return()=>{mounted=false};
 },[day,token]);
 const cashValue=useMemo(()=>{
   const cleaned=physicalCash.trim().replace(',','.');
   if(!/^\d{1,10}(\.\d{1,2})?$/.test(cleaned))return null;
   const cents=Math.round(Number(cleaned)*100);
   return Number.isSafeInteger(cents)?cents:null;
 },[physicalCash]);
 const variance=summary&&cashValue!==null?cashValue-summary.by_method.cash.amount_cents:null;

 const exportCsv=()=>{
   if(!summary)return;
   const rows:(string|number)[][]=[
    ['EL PALADAR DEL INKA - RESUMEN INTERNO DE COBROS'],
    ['Fecha local',summary.date],
    ['Zona horaria',summary.timezone],
    ['Estado','Requiere verificación manual; NO emitido SUNAT'],
    [],
    ['Medio de pago','Operaciones','Total PEN'],
    ...(['cash','card','yape','plin'] as const).map(method=>[
      names[method],summary.by_method[method].count,
      (summary.by_method[method].amount_cents/100).toFixed(2)
    ]),
    ['TOTAL',summary.payments_count,(summary.gross_payments_cents/100).toFixed(2)],
    [],
    ['Constancia interna','Pedido','Medio','Importe PEN'],
    ...summary.entries.map(item=>[
      item.document_number,item.order_id,names[item.method]??'Otro',
      (item.total_cents/100).toFixed(2)
    ]),
   ];
   // Todas las columnas proceden de etiquetas constantes e importes enteros; 
   // no se exportan nombres/campos arbitrarios del cliente, previniendo CSV injection.
   const csv='\uFEFF'+rows.map(r=>r.map(v=>`"${String(v).replaceAll('"','""')}"`).join(';')).join('\r\n');
   const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
   const a=document.createElement('a');a.href=url;a.download=`caja_interna_${summary.date}.csv`;a.click();
   window.setTimeout(()=>URL.revokeObjectURL(url),1000);
 };
 return <section className="cash-closeout panel" aria-labelledby="cash-closeout-title">
   <div className="panel-head cash-closeout-header">
     <div><span className="eyebrow">CONTROL OPERATIVO</span><h3 id="cash-closeout-title">Resumen diario de caja</h3><p>Consulta pagos por día en horario de Perú y compáralos con el dinero efectivamente recibido.</p></div>
     <div className="cash-closeout-actions"><label htmlFor="cash-closeout-date">Fecha del resumen</label><input id="cash-closeout-date" aria-label="Fecha del resumen de caja" type="date" value={day} onChange={e=>setDay(e.target.value)}/><button className="secondary" type="button" disabled={busy||!summary} onClick={exportCsv}>Exportar CSV</button></div>
   </div>
   {error&&<p role="alert" className="notice error">{error}</p>}
   {busy&&<p role="status" className="cash-summary-loading">Consultando pagos confirmados en PostgreSQL…</p>}
   {summary&&<div className="cash-closeout-body">
     <div className="cash-method-grid">
      {(['cash','yape','plin','card'] as const).map(method=><article key={method}>
        <span className={`cash-method-icon cash-method-${method}`} aria-hidden="true">{method==='cash'?'S/':method==='card'?'▣':method==='yape'?'Y':'P'}</span>
        <div><small>{names[method]}</small><strong>{amount(summary.by_method[method].amount_cents)}</strong><span>{summary.by_method[method].count} pago(s)</span></div>
      </article>)}
     </div>
     <div className="cash-closeout-bottom">
      <div className="cash-closeout-total"><span>Ingreso confirmado del día</span><strong>{amount(summary.gross_payments_cents)}</strong><small>{summary.payments_count} pago(s) · America/Lima · Importes íntegros, sin descuentos ni devoluciones</small></div>
      <div className="cash-physical-count"><label htmlFor="cash-physical-input">Efectivo contado en caja (S/)</label><input id="cash-physical-input" inputMode="decimal" placeholder="Ej.: 125.50" value={physicalCash} onChange={e=>setPhysicalCash(e.target.value)} aria-describedby="cash-variance-note"/>
        <div className="cash-variance" id="cash-variance-note">{variance===null?'Ingresa el efectivo contado para comparar.':<><span>Diferencia respecto al efectivo registrado</span><strong className={variance===0?'cash-balanced':variance>0?'cash-surplus':'cash-deficit'}>{variance>0?'+':''}{amount(variance)}</strong></>}</div>
      </div>
     </div>
     <p className="cash-closeout-legal"><strong>Sin cierre registrado:</strong> este es un reporte informativo y una comparación local, no un arqueo firmado. La cantidad contada no se guarda ni modifica transacciones. Revisar vouchers, efectivo, faltantes y devoluciones pendientes antes de aprobar el cierre con la persona responsable. No es comprobante tributario.</p>
   </div>}
 </section>;
}
