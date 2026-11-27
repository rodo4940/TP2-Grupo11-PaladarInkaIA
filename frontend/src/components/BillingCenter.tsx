import {useCallback,useEffect,useMemo,useRef,useState} from 'react';
import type {RefObject} from 'react';
import type {BillingDocument,BillingLedger} from '../types/domain';
import {api} from '../services/api';
import {InkaBrand} from './InkaBrand';
import {CashCloseout} from './CashCloseout';

const money=(v:number)=>new Intl.NumberFormat('es-PE',{style:'currency',currency:'PEN'}).format(v/100);
const date=(v:string)=>new Date(v).toLocaleString('es-PE',{timeZone:'America/Lima',dateStyle:'medium',timeStyle:'short'});
const methodName:Record<string,string>={cash:'Efectivo',yape:'Yape',plin:'Plin',card:'Tarjeta'};

/**
 * Módulo de consulta y reimpresión. Fuente única: pagos persistidos en FastAPI.
 * No emite documentos tributarios. El número interno deriva de Payment.id.
 */
export function BillingCenter({token}:{token:string}){
 const [ledger,setLedger]=useState<BillingLedger|null>(null);
 const [selectedId,setSelectedId]=useState<number|null>(null);
 const [search,setSearch]=useState('');
 const [method,setMethod]=useState('all');
 const [loading,setLoading]=useState(false);
 const [error,setError]=useState('');
 const ticketRef=useRef<HTMLDivElement>(null);
 const refresh=useCallback(async()=>{
   setLoading(true);setError('');
   try{
     const result=await api<BillingLedger>('/billing/ledger',token);
     setLedger(result);
     setSelectedId(previous=>previous && result.entries.some(x=>x.id===previous)?previous:result.entries[0]?.id??null);
   }catch(e){setError(e instanceof Error?e.message:'Error consultando caja');}
   finally{setLoading(false)}
 },[token]);
 useEffect(()=>{void refresh()},[refresh]);
 const entries=ledger?.entries??[];
 const filtered=useMemo(()=>entries.filter(item=>
   (method==='all'||item.method===method) &&
   (`${item.document_number} ${item.order_id} ${item.customer_name} ${item.table_label}`).toLowerCase().includes(search.trim().toLowerCase())
 ),[entries,method,search]);
 const selected=entries.find(item=>item.id===selectedId)??null;
 const totalFiltered=filtered.reduce((sum,item)=>sum+item.total_cents,0);
 const print=()=>{if(selected&&ticketRef.current)window.print();};
 return <div className="billing-workspace">
   <div className="page-title module-heading billing-heading">
     <div><span className="eyebrow">CAJA Y TRAZABILIDAD</span><h1>Caja y comprobantes</h1><p>Consulta los cobros registrados y reimprime constancias internas de cada operación.</p></div>
     <span className="billing-title-icon" aria-hidden="true"><InkaBrand size={92}/></span>
   </div>
   <div className="billing-disclaimer" role="note"><span aria-hidden="true">ⓘ</span><span><strong>Constancias internas — no son boletas ni facturas electrónicas.</strong> Para emitir comprobantes tributarios válidos se necesita integrar y validar el sistema de emisión de SUNAT. No se calcula IGV ni se asignan series fiscales.</span></div>
   {error&&<div role="alert" className="notice error billing-error">{error}<button type="button" className="secondary" onClick={()=>void refresh()}>Reintentar</button></div>}
   <div className="billing-metrics">
     <article><span>Pagos confirmados</span><strong>{ledger?.count??'—'}</strong><small>Registros persistidos</small></article>
     <article><span>Ingreso registrado</span><strong>{ledger?money(ledger.total_cents):'—'}</strong><small>Total acumulado de pagos</small></article>
     <article><span>Importe filtrado</span><strong>{money(totalFiltered)}</strong><small>{filtered.length} documentos visibles</small></article>
   </div>
   <CashCloseout token={token}/>
   <div className="billing-columns">
     <section className="panel billing-list">
       <div className="panel-head"><div><h3>Historial de pagos</h3><p>Una constancia por pago registrado; sin duplicar cobros</p></div><button className="secondary" type="button" disabled={loading} onClick={()=>void refresh()}>{loading?'Consultando…':'Actualizar'}</button></div>
       <div className="billing-filters">
        <input aria-label="Buscar comprobante interno" placeholder="Buscar número, cliente o pedido..." value={search} onChange={e=>setSearch(e.target.value)}/>
        <select aria-label="Filtrar método de pago" value={method} onChange={e=>setMethod(e.target.value)}>
         <option value="all">Todos los medios</option><option value="cash">Efectivo</option><option value="yape">Yape</option><option value="plin">Plin</option><option value="card">Tarjeta</option>
        </select>
       </div>
       {loading&&!ledger&&<div className="billing-skeleton" role="status">Consultando pagos del servidor…</div>}
       {!loading&&filtered.length===0&&<div className="billing-empty"><span aria-hidden="true">▤</span><strong>{entries.length?'No hay coincidencias':'No hay cobros registrados'}</strong><p>{entries.length?'Modifica el filtro o la búsqueda.':'Registra el pago de un pedido en Ventas / POS. Entonces su constancia aparecerá aquí.'}</p></div>}
       <div className="billing-entries">
        {filtered.map(item=><button type="button" key={item.id} className={`billing-entry ${selectedId===item.id?'billing-entry-active':''}`} aria-pressed={selectedId===item.id} onClick={()=>setSelectedId(item.id)}>
          <span className="billing-entry-icon" aria-hidden="true">▤</span><span className="billing-entry-body"><strong>{item.document_number}</strong><small>Pedido #{item.order_id} · {date(item.issued_at)}</small><small>{item.customer_name} · {methodName[item.method]||item.method}</small></span>
          <span className="billing-entry-total">{money(item.total_cents)}<small>Registrado</small></span>
        </button>)}
       </div>
       <p className="billing-legal-hint">Registro administrativo: consultar o imprimir no altera el importe del pago ni el inventario.</p>
     </section>
     <section className="panel billing-preview-panel">
      <div className="panel-head"><div><h3>Vista previa del ticket</h3><p>Diseñado para impresión térmica o papel A4</p></div>{selected&&<button className="primary" onClick={print} type="button">Imprimir ticket</button>}</div>
      {selected?<div className="billing-print-frame"><Ticket document={selected} ticketRef={ticketRef}/></div>:<div className="billing-empty"><span aria-hidden="true">◎</span><strong>Selecciona un pago confirmado</strong><p>La vista previa se genera desde los datos de la API.</p></div>}
     </section>
   </div>
 </div>;
}

function Ticket({document,ticketRef}:{document:BillingDocument;ticketRef:RefObject<HTMLDivElement|null>}){
 return <div className="billing-ticket" ref={ticketRef} id="billing-ticket-print" role="region" aria-label={`Ticket interno ${document.document_number}`}>
  <div className="ticket-brand"><InkaBrand size={67}/><div><strong>EL PALADAR<br/>DEL INKA</strong><span>Gastronomía & tradición</span></div></div>
  <div className="ticket-type">CONSTANCIA INTERNA DE PAGO</div>
  <div className="ticket-meta"><div><span>Referencia</span><b>{document.document_number}</b></div><div><span>Fecha</span><b>{date(document.issued_at)}</b></div><div><span>Pedido</span><b>#{document.order_id}</b></div><div><span>Ubicación</span><b>{document.table_label}</b></div><div><span>Cliente</span><b>{document.customer_name}</b></div></div>
  <table className="billing-ticket-table"><thead><tr><th>Descripción</th><th>Cant.</th><th>Importe</th></tr></thead><tbody>
   {document.items.map((item,i)=><tr key={i}><td>{item.name}<small>{money(item.unit_price_cents)} c/u</small></td><td>{item.quantity}</td><td>{money(item.subtotal_cents)}</td></tr>)}
  </tbody></table>
  <div className="ticket-payment"><span>Medio de pago</span><strong>{methodName[document.method]||document.method}</strong></div>
  <div className="ticket-grand-total"><span>TOTAL PAGADO</span><strong>{money(document.total_cents)}</strong></div>
  <div className="ticket-end-note"><span>Gracias por tu visita</span><p>Documento de uso interno. No constituye comprobante tributario SUNAT; no es boleta ni factura electrónica.</p><small>Identificación interna {document.document_number} · Estado: pago registrado</small></div>
 </div>
}
