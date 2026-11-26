import type {Order,OrderStatus,Role} from '../types/domain';

/**
 * Panel operativo de lectura: exclusivamente derivado de los pedidos que entrega la API.
 * No crea datos, no ejecuta llamadas y no confunde volumen con tiempo real.
 */
type NextView='orders'|'pos'|'kitchen';
const statusName:Record<OrderStatus,string>={
 pending:'Por preparar',preparing:'En cocina',ready:'Listos',delivered:'Entregados',cancelled:'Cancelados',
};
const accents:Record<OrderStatus,string>={
 pending:'var(--pending,#d4a25a)',preparing:'var(--preparing,#b86d3d)',
 ready:'var(--ready,#4d9a78)',delivered:'var(--delivered,#285a43)',cancelled:'var(--cancelled,#a7ada7)',
};
const states:OrderStatus[]=['pending','preparing','ready','delivered'];
export function OperationsOverview({orders,role,onNavigate}:{orders:Order[];role:Role;onNavigate:(view:NextView)=>void}){
 const valid=orders.filter(x=>x.status!=='cancelled');
 const total=valid.length;
 const complete=valid.filter(x=>x.status==='delivered').length;
 const progress=total?Math.round(complete/total*100):0;
 const pending=valid.filter(x=>x.status==='pending').length;
 const ready=valid.filter(x=>x.status==='ready').length;
 const unpaid=valid.filter(x=>!x.paid).length;
 const counts=states.map(status=>({status,count:valid.filter(x=>x.status===status).length}));
 const segments=counts.map((entry,i)=>{
  const start=counts.slice(0,i).reduce((sum,item)=>sum+item.count,0)/Math.max(1,total)*100;
  const end=(counts.slice(0,i+1).reduce((sum,item)=>sum+item.count,0))/Math.max(1,total)*100;
  return `${accents[entry.status]} ${start}% ${end}%`;
 }).join(', ');
 const ringStyle={background:total?`conic-gradient(${segments})`:'#e8e9e2'};
 return <section className="operations-overview" aria-label="Centro de operaciones">
   <div className="operations-heading">
    <div><span className="eyebrow">PULSO DEL NEGOCIO</span><h2>Tu operación de un vistazo</h2><p>Distribución actual de pedidos registrados, sin estimaciones ni datos simulados de interfaz.</p></div>
    <button className="text-action" onClick={()=>onNavigate('orders')}>Revisar pedidos <span aria-hidden="true">↗</span></button>
   </div>
   <div className="operations-grid">
    <div className="operations-ring-card">
      <div className="operations-ring" style={ringStyle} role="img" aria-label={`Pedidos entregados: ${complete} de ${total} vigentes (${progress} por ciento)`}>
        <span><b>{progress}%</b><small>entregados</small></span>
      </div>
      <div className="operations-ring-info"><strong>Seguimiento de entregas</strong>
        <p><b>{complete} de {total}</b> pedidos vigentes completados</p>
        <div className="operations-progress" aria-hidden="true"><span style={{width:`${progress}%`}}/></div>
        <small>Los pedidos cancelados no se incluyen en este porcentaje.</small>
      </div>
    </div>
    <div className="operations-status-list" aria-label="Distribución por estado">
     {counts.map(({status,count})=><div key={status} className="operations-status">
      <div className="operations-status-label"><span className="status-dot" style={{background:accents[status]}}/>{statusName[status]}<b>{count}</b></div>
      <div className="operations-bar"><span style={{width:`${total?count/total*100:0}%`,background:accents[status]}}/></div>
     </div>)}
    </div>
    <div className="operations-next">
     <span className="eyebrow">ATENCIÓN INMEDIATA</span>
     <h3>¿Qué sigue ahora?</h3>
     {(role==='admin'||role==='kitchen')&&<button onClick={()=>onNavigate('kitchen')}><span className="action-icon">♨</span><span><b>{pending} por preparar</b><small>Ver comandas de cocina</small></span><span aria-hidden="true">↗</span></button>}
     <button onClick={()=>onNavigate('orders')}><span className="action-icon">✓</span><span><b>{ready} listos para entregar</b><small>Consultar seguimiento</small></span><span aria-hidden="true">↗</span></button>
     {(role==='admin'||role==='cashier')&&<button onClick={()=>onNavigate('pos')}><span className="action-icon">S/</span><span><b>{unpaid} por cobrar</b><small>Ir al punto de venta</small></span><span aria-hidden="true">↗</span></button>}
    </div>
   </div>
  </section>;
}
