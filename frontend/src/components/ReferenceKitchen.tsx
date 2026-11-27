import {useState} from 'react';
import type {Order,OrderStatus} from '../types/domain';

const labels:Record<string,string>={pending:'Pendiente',preparing:'En preparación',ready:'Listo para entregar',delivered:'Entregado'};
const next:Partial<Record<OrderStatus,OrderStatus>>={pending:'preparing',preparing:'ready',ready:'delivered'};
type Props={orders:Order[];busy:boolean;onChange:(order:Order,status:OrderStatus)=>void;onRefresh:()=>Promise<unknown>};
const origin=(o:Order)=>o.table_label.toLowerCase().includes('delivery')?'delivery':o.table_label.toLowerCase().includes('recojo')?'recojo':'salon';
const age=(created:string)=>{const minutes=Math.max(0,Math.round((Date.now()-new Date(created).getTime())/60000));return minutes<60?`${minutes} min`:`${Math.floor(minutes/60)} h ${minutes%60} min`};
export function ReferenceKitchen({orders,busy,onChange,onRefresh}:Props){
 const [filter,setFilter]=useState<'all'|'salon'|'recojo'|'delivery'>('all');
 const [detail,setDetail]=useState<Order|null>(null);
 const active=orders.filter(o=>o.status!=='cancelled');
 const shown=active.filter(o=>filter==='all'||origin(o)===filter);
 const count=(s:OrderStatus)=>shown.filter(o=>o.status===s).length;
 const groups=[{id:'pending' as const,title:'Pendiente',subtitle:'Tickets por iniciar',icon:'⌛'},
 {id:'preparing' as const,title:'En preparación',subtitle:'Pizzas en preparación',icon:'♨'},
 {id:'ready' as const,title:'Listo para entregar',subtitle:'Pedidos preparados para despacho',icon:'✓'},
 {id:'delivered' as const,title:'Entregado',subtitle:'Pedidos finalizados',icon:'▣'}];
 return <div className="pi-kds">
 <div className="pi-module-title"><div><span className="pi-title-icon">♨</span><div><h1>Cocina – KDS</h1><p>Gestión y seguimiento de la preparación de pedidos</p></div></div><div className="pi-title-actions"><span className="pi-success-pill">● Datos del sistema</span><button onClick={()=>void onRefresh()} disabled={busy}>↻ Actualizar</button></div></div>
 <div className="pi-kds-metrics"><div><span>▤</span><small>Tickets activos</small><strong>{active.filter(x=>!['delivered'].includes(x.status)).length}</strong></div><div><span>◴</span><small>Por iniciar</small><strong>{active.filter(x=>x.status==='pending').length}</strong></div><div><span>↠</span><small>En preparación</small><strong>{active.filter(x=>x.status==='preparing').length}</strong></div><div><span>✓</span><small>Listos</small><strong>{active.filter(x=>x.status==='ready').length}</strong></div></div>
 <div className="pi-kds-tabs">{([{id:'all',name:'Todos'}, {id:'salon',name:'Salón'}, {id:'delivery',name:'Delivery'}, {id:'recojo',name:'Para llevar'}] as const).map(x=><button key={x.id} className={filter===x.id?'selected':''} onClick={()=>setFilter(x.id)}>{x.name} ({x.id==='all'?active.length:active.filter(o=>origin(o)===x.id).length})</button>)}</div>
 <div className="pi-kds-board">{groups.map(g=><section className={`pi-kds-lane pi-kds-lane-${g.id}`} key={g.id}><header><div><span>{g.icon}</span><div><h3>{g.title}</h3><small>{g.subtitle}</small></div></div><b>{count(g.id)}</b></header><div className="pi-kds-lane-body">{shown.filter(o=>o.status===g.id).map(o=><article className="pi-kds-card" key={o.id}><div className="pi-kds-ticket-head"><strong>#P-{String(o.id).padStart(4,'0')}</strong><span className="pi-kds-time">◷ {age(o.created_at)}</span></div><p className="pi-kds-origin">{origin(o)==='delivery'?'♧ Delivery':origin(o)==='recojo'?'▣ Para llevar':'♜ Salón'} · {o.table_label}</p><div className="pi-kds-dishes">{o.items.map(i=><div key={i.id}><span>◕</span><div><b>{i.product_name} ×{i.quantity}</b></div></div>)}</div>{o.notes&&<div className="pi-kds-notes">Nota: {o.notes}</div>}<div className="pi-kds-card-actions"><button type="button" onClick={()=>setDetail(o)}>◉ Ver</button>{next[g.id]&&<button type="button" className="pi-kds-action" disabled={busy} onClick={()=>onChange(o,next[g.id]!)}>{g.id==='pending'?'▷ Iniciar preparación':g.id==='preparing'?'✓ Marcar listo':'✓ Entregar'}</button>}</div></article>)}{!shown.some(o=>o.status===g.id)&&<p className="pi-kds-empty">Sin tickets en este estado</p>}</div></section>)}</div>
 <div className="pi-kds-footer"><span>♨ Estado de cocina: <strong>Operativa</strong></span><span>▣ Pendientes: {count('pending')}</span><span>◷ Preparando: {count('preparing')}</span><span>✓ Listos: {count('ready')}</span></div>
 {detail&&<div className="pi-sale-overlay" role="dialog" aria-modal="true" aria-label={`Detalle del pedido ${detail.id}`}><div className="pi-kds-dialog"><button className="pi-close" onClick={()=>setDetail(null)}>×</button><h2>Pedido #P-{String(detail.id).padStart(4,'0')}</h2><p>{detail.table_label} · {new Date(detail.created_at).toLocaleString('es-PE')}</p><div className="pi-kds-dishes">{detail.items.map(i=><div key={i.id}><span>◕</span><strong>{i.quantity} × {i.product_name}</strong></div>)}</div>{detail.notes&&<p>Observaciones: {detail.notes}</p>}<div className="pi-dialog-footer"><span>Estado: {labels[detail.status]??detail.status}</span><button onClick={()=>setDetail(null)}>Cerrar</button></div></div></div>}
 </div>;
}
