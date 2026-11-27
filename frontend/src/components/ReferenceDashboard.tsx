import type {Dashboard, Order, Report, Role} from '../types/domain';

const PEN=(value:number)=>new Intl.NumberFormat('es-PE',{style:'currency',currency:'PEN'}).format(value/100);
type Screen='dashboard'|'pos'|'orders'|'kitchen'|'inventory'|'products'|'customers'|'reports'|'ai'|'users'|'settings'|'billing';
type Props={data:Dashboard|null;orders:Order[];report:Report|null;role:Role;user:string;onNavigate:(v:Screen)=>void;refreshedAt:string};
function Trend({values}:{values:number[]}) {
 const width=560,height=160,pad=12,max=Math.max(1,...values);
 const path=values.map((v,i)=>`${i===0?'M':'L'}${pad+i*(width-2*pad)/Math.max(1,values.length-1)} ${height-pad-(v/max)*(height-2*pad)}`).join(' ');
 const area=path+` L ${width-pad} ${height-pad} L ${pad} ${height-pad} Z`;
 return <svg viewBox="0 0 560 160" role="img" aria-label="Evolución de pedidos pagados por día en los últimos siete días" preserveAspectRatio="none" className="pi-trend-svg"><defs><linearGradient id="pi-trend-fill" x1="0" x2="0" y1="0" y2="1"><stop stopColor="#eda82e" stopOpacity=".47"/><stop offset="1" stopColor="#eda82e" stopOpacity=".02"/></linearGradient></defs><path d={area} fill="url(#pi-trend-fill)"/><path d={path} stroke="#edac35" strokeWidth="3.5" fill="none" strokeLinejoin="round" strokeLinecap="round"/>{values.map((v,i)=><circle key={i} cx={pad+i*(width-2*pad)/6} cy={height-pad-(v/max)*(height-2*pad)} r="4.5" fill="#ffcd57" stroke="#1c1b18" strokeWidth="1.5"/>)}</svg>
}
export function ReferenceDashboard({data,orders,report,role,onNavigate,refreshedAt}:Props){
 const today=new Date();
 const dates=Array.from({length:7},(_,i)=>{const d=new Date(today);d.setHours(0,0,0,0);d.setDate(d.getDate()-(6-i));return d;});
 const activity=dates.map(d=>orders.filter(o=>o.paid&&new Date(o.created_at).toDateString()===d.toDateString()).length);
 const statuses={pending:orders.filter(o=>o.status==='pending').length,preparing:orders.filter(o=>o.status==='preparing').length,ready:orders.filter(o=>o.status==='ready').length};
 const completed=orders.filter(o=>o.status==='delivered').length;
 const active=statuses.pending+statuses.preparing+statuses.ready;
 const categories=report?.top_products.slice(0,5)??[];
 const maxTop=Math.max(1,...categories.map(x=>x.quantity));
 const cards=[
  {icon:'◉',label:'Ventas registradas',value:PEN(data?.sales_cents??0),foot:'Acumulado neto de los pagos'},
  {icon:'▤',label:'Pedidos activos',value:String(active),foot:'En cola, preparación o listos'},
  {icon:'⬡',label:'Stock bajo mínimo',value:String(data?.low_stock.length??0),foot:'Insumos que requieren revisión'},
  {icon:'♧',label:'Clientes registrados',value:String(data?.customers_total??0),foot:'En el entorno conectado'}
 ];
 return <div className="pi-dashboard">
  <div className="pi-dashboard-heading"><div><span className="pi-overline">PANEL DE CONTROL · EL PALADAR DEL INKA</span><h1>¡Bienvenido a Paladar Inka AI!</h1><p>Monitorea las operaciones de la pizzería con información obtenida del sistema.</p></div><div className="pi-dashboard-actions"><span>◉ Actualizado {refreshedAt||'al iniciar'}</span>{(role==='admin'||role==='cashier')&&<button onClick={()=>onNavigate('pos')}>＋ Nueva venta</button>}</div></div>
  <div className="pi-metric-grid">{cards.map((c,i)=><article key={c.label} className="pi-metric"><span className="pi-metric-icon">{c.icon}</span><div><p>{c.label}</p><strong>{c.value}</strong><small>{c.foot}</small></div><span className="pi-spark" aria-hidden="true">{i===2?'⚠':'⌁'}</span></article>)}</div>
  <div className="pi-dashboard-layout">
   <section className="pi-surface pi-activity"><header><h3>Pedidos cobrados en los últimos 7 días</h3><span>Datos registrados · Unidades</span></header><Trend values={activity}/><div className="pi-chart-dates">{dates.map((d,i)=><span key={i}>{d.toLocaleDateString('es-PE',{weekday:'short',day:'numeric'})}</span>)}</div></section>
   <section className="pi-surface pi-products"><header><h3>Productos más vendidos</h3><button onClick={()=>onNavigate('reports')}>Ver reportes ↗</button></header>{categories.length?categories.map((p,i)=><div className="pi-top-product" key={p.name}><b>{i+1}</b><div><strong>{p.name}</strong><span className="pi-small-bar"><i style={{width:`${p.quantity/maxTop*100}%`}}/></span></div><span>{p.quantity} unid.</span></div>):<p className="pi-muted">Sin productos cobrados todavía.</p>}</section>
  </div>
  <div className="pi-dashboard-layout pi-bottom-layout">
   <section className="pi-surface"><header><h3>Pedidos recientes</h3><button onClick={()=>onNavigate('orders')}>Ver todos ↗</button></header><div className="pi-recent-orders">{orders.slice(0,6).map(o=><div className="pi-recent-order" key={o.id}><strong>#{o.id}</strong><span>{o.table_label}</span><b>{PEN(o.total_cents)}</b><em className={`pi-state pi-state-${o.status}`}>{({pending:'Pendiente',preparing:'Preparando',ready:'Listo',delivered:'Entregado',cancelled:'Cancelado'} as const)[o.status]}</em></div>)}{orders.length===0&&<p className="pi-muted">No hay pedidos registrados.</p>}</div></section>
   <section className="pi-surface pi-kitchen-summary"><header><h3>Cola de cocina</h3><button onClick={()=>onNavigate('kitchen')}>Ir a cocina ↗</button></header><div className="pi-kitchen-pulse">{[['Pendientes',statuses.pending,'#d2b57e'],['En preparación',statuses.preparing,'#e9a51f'],['Listos',statuses.ready,'#29a55c'],['Entregados',completed,'#4d8c72']].map(([name,count,color])=><div key={String(name)}><span className="pi-pulse-dot" style={{background:String(color)}}/><strong>{count}</strong><small>{name}</small></div>)}</div><p className="pi-muted">Total de pedidos activos: {active}. Los cambios son confirmados por la API.</p></section>
   <section className="pi-surface pi-alerts"><header><h3>Alertas de inventario</h3><button onClick={()=>onNavigate('inventory')}>Ver inventario ↗</button></header>{(data?.low_stock??[]).slice(0,4).map(i=><div className="pi-alert-item" key={i.id}><span>⚠</span><div><strong>{i.name}</strong><small>{i.stock} {i.unit} disponibles · mínimo {i.minimum_stock}</small></div><b>Reponer</b></div>)}{!data?.low_stock.length&&<p className="pi-muted">Sin alertas de stock bajo mínimo.</p>}</section>
  </div>
  <div className="pi-ai-banner"><span>✦ IA · Apoyo a decisiones</span><p>Consulta recomendaciones y análisis explicables basados en registros reales. El modelo entrenado de demostración usa datos sintéticos.</p><button onClick={()=>onNavigate('ai')}>Ver análisis con IA ↗</button></div>
 </div>
}