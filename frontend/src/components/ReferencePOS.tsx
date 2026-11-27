import {useEffect,useMemo,useState} from 'react';
import {api,post} from '../services/api';
import {productImage} from '../assets/menuPhotos';
import type {Customer, InternalReceipt, Order, Product} from '../types/domain';

const PEN=(c:number)=>new Intl.NumberFormat('es-PE',{style:'currency',currency:'PEN'}).format(c/100);
type Destination='products'|'customers'|'billing'|'orders';
type Props={products:Product[];customers:Customer[];token:string;initialOrder:Order|null;onRefresh:()=>Promise<unknown>;onNavigate:(view:Destination)=>void};
const paymentOptions=[{id:'cash',name:'Efectivo',icon:'▣'},{id:'card',name:'Tarjeta',icon:'▤'},{id:'yape',name:'Yape',icon:'◈'},{id:'plin',name:'Plin',icon:'◉'}] as const;
function ProductImage({product}:{product:Product}){
 const url=productImage(product);
 return <div className="pi-pos-photo">{url?<img src={url} alt={`Foto referencial de ${product.name}`} loading="lazy" onError={e=>{e.currentTarget.src='/illustrations/pizza-artisan.svg'}}/>:<img src="/illustrations/pizza-artisan.svg" alt="Imagen referencial de producto" loading="lazy"/>}</div>;
}
export function ReferencePOS({products,customers,token,initialOrder,onRefresh,onNavigate}:Props){
 const [search,setSearch]=useState('');
 const [category,setCategory]=useState('Todos');
 const [cart,setCart]=useState<Record<number,number>>({});
 const [orderType,setOrderType]=useState<'Salón'|'Recojo'|'Delivery'>('Salón');
 const [table,setTable]=useState('Mostrador');
 const [customer,setCustomer]=useState('');
 const [note,setNote]=useState('');
 const [method,setMethod]=useState<'cash'|'card'|'yape'|'plin'>('cash');
 const [received,setReceived]=useState('');
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState('');
 const [pendingOrder,setPendingOrder]=useState<Order|null>(initialOrder?.paid?null:initialOrder);
 const [paidOrder,setPaidOrder]=useState<Order|null>(null);
 const [receipt,setReceipt]=useState<InternalReceipt|null>(null);
 useEffect(()=>{if(initialOrder&&!initialOrder.paid){setPendingOrder(initialOrder);setError('')}},[initialOrder?.id]);
 const categories=['Todos',...new Set(products.map(p=>p.category))];
 const visible=products.filter(p=>(category==='Todos'||category===p.category)&&`${p.name} ${p.sku}`.toLowerCase().includes(search.trim().toLowerCase()));
 const items=useMemo(()=>Object.entries(cart).map(([id,quantity])=>({product:products.find(p=>p.id===Number(id)),quantity})).filter((x):x is {product:Product;quantity:number}=>Boolean(x.product)&&x.quantity>0),[cart,products]);
 const count=items.reduce((n,x)=>n+x.quantity,0);
 const estimated=items.reduce((n,x)=>n+x.product.price_cents*x.quantity,0);
 const total=pendingOrder?.total_cents??estimated;
 const receivedCents=Math.round(Number(received)*100);
 const change=(id:number,n:number)=>setCart(old=>({...old,[id]:Math.max(0,Math.min(100,(old[id]||0)+n))}));
 const readyToPay=method!=='cash'||(Number.isFinite(receivedCents)&&receivedCents>=total);
 async function createOnly(){
  if(busy||!count||pendingOrder)return;
  setBusy(true);setError('');
  try{
   const order=await post<Order>('/orders',{items:items.map(x=>({product_id:x.product.id,quantity:x.quantity})),customer_id:customer?Number(customer):null,table_label:(orderType==='Salón'?table:`${orderType}: ${table}`).slice(0,32),notes:note},token);
   setPendingOrder(order);setCart({});setNote('');
   void onRefresh();
  }catch(e){setError(e instanceof Error?e.message:'No fue posible registrar el pedido.')}
  finally{setBusy(false)}
 }
 async function checkout(){
  if(busy||(!pendingOrder&&!count)||!readyToPay)return;
  setBusy(true);setError('');
  let order=pendingOrder;
  try{
   if(!order){order=await post<Order>('/orders',{items:items.map(x=>({product_id:x.product.id,quantity:x.quantity})),customer_id:customer?Number(customer):null,table_label:(orderType==='Salón'?table:`${orderType}: ${table}`).slice(0,32),notes:note},token);setPendingOrder(order);}
   await post(`/orders/${order.id}/payment`,{method,amount_cents:order.total_cents},token);
   setPaidOrder(order);setPendingOrder(null);setCart({});setNote('');setReceived('');
   try{setReceipt(await api<InternalReceipt>(`/orders/${order.id}/receipt`,token))}catch{setReceipt(null)}
   void onRefresh();
  }catch(e){setError(e instanceof Error?e.message:'No se pudo completar el pago. Comprueba el estado del pedido antes de reintentar.');void onRefresh()}
  finally{setBusy(false)}
 }
 return <div className="pi-pos">
  <div className="pi-module-title"><div><span className="pi-title-icon">▣</span><div><h1>Ventas / Caja POS</h1><p>Registro de ventas y cobros del establecimiento</p></div></div><div className="pi-title-actions"><span className="pi-success-pill">● Sistema conectado</span><button onClick={()=>onNavigate('billing')}>◫ Consultar caja</button></div></div>
  <div className="pi-pos-grid">
   <section className="pi-pos-catalog">
    <div className="pi-pos-categories">{categories.map(c=><button key={c} className={category===c?'selected':''} onClick={()=>setCategory(c)}>{c==='Todos'?'✦ ':c.toLowerCase().includes('pizza')?'◕ ':c.toLowerCase().includes('bebida')?'◧ ':''}{c}</button>)}</div>
    <div className="pi-pos-toolbar"><label><span aria-hidden="true">⌕</span><input type="search" aria-label="Buscar producto en el punto de venta" value={search} onChange={e=>setSearch(e.target.value)} placeholder="Buscar producto por nombre, código o categoría..."/></label><span>{visible.length} artículos</span><button onClick={()=>onNavigate('products')}>Ver catálogo ↗</button></div>
    {visible.length?<div className="pi-pos-products">{visible.map(p=><article className="pi-pos-card" key={p.id}><ProductImage product={p}/><div className="pi-pos-card-body"><h3>{p.name}</h3><small>{p.category} · {p.sku}</small><div><strong>{PEN(p.price_cents)}</strong><button aria-label={`Agregar ${p.name} al pedido`} onClick={()=>change(p.id,1)}>＋ Agregar</button></div></div></article>)}</div>:<p className="pi-empty">No se encontraron productos.</p>}
   </section>
   <aside className="pi-pos-ticket" id="order-cart"><div className="pi-pos-modes">{(['Salón','Recojo','Delivery'] as const).map(t=><button key={t} className={orderType===t?'selected':''} onClick={()=>setOrderType(t)} disabled={!!pendingOrder}>{t==='Salón'?'♜':t==='Recojo'?'♙':'♧'} {t}</button>)}</div>
    <div className="pi-pos-selector"><label>Cliente<select aria-label="Cliente" value={customer} disabled={!!pendingOrder} onChange={e=>setCustomer(e.target.value)}><option value="">Cliente de mostrador</option>{customers.map(c=><option key={c.id} value={c.id}>{c.name}</option>)}</select></label><button aria-label="Nuevo cliente" onClick={()=>onNavigate('customers')}>＋ Nuevo</button></div>
    <label className="pi-pos-reference">Mesa o referencia<input value={table} maxLength={32} disabled={!!pendingOrder} onChange={e=>setTable(e.target.value)}/></label>
    <div className="pi-pos-items-head"><h3>Pedido {pendingOrder?`#${pendingOrder.id}`:''}</h3><span>{count} productos</span>{!pendingOrder&&count>0&&<button onClick={()=>setCart({})}>Vaciar</button>}</div>
    {pendingOrder?<div className="pi-pos-locked">El pedido #{pendingOrder.id} ya se registró. Confirma su pago sin crear otro pedido.</div>:items.length?<div className="pi-pos-cart-lines">{items.map(({product,quantity})=><div className="pi-pos-cart-line" key={product.id}><ProductImage product={product}/><div><b>{product.name}</b><small>{PEN(product.price_cents)} por unidad</small><div className="pi-pos-qty"><button aria-label={`Restar ${product.name}`} onClick={()=>change(product.id,-1)}>−</button><span>{quantity}</span><button aria-label={`Sumar ${product.name}`} onClick={()=>change(product.id,1)}>＋</button></div></div><strong>{PEN(quantity*product.price_cents)}</strong></div>)}</div>:<p className="pi-empty">Selecciona productos para iniciar una venta.</p>}
    <label className="pi-pos-note">Notas del pedido<textarea rows={2} maxLength={500} disabled={!!pendingOrder} value={note} onChange={e=>setNote(e.target.value)} placeholder="Ej.: Sin cebolla, extra queso..."/></label>
    <div className="pi-pos-totals"><div><span>Subtotal</span><b>{PEN(total)}</b></div><div><span>Descuentos</span><b>Sin descuento</b></div><div className="pi-pos-grand"><strong>Total a cobrar</strong><strong>{PEN(total)}</strong></div></div>
    <h4 className="pi-pos-pay-title">Método de pago</h4><div className="pi-pos-pay-methods">{paymentOptions.map(p=><button key={p.id} className={method===p.id?'selected':''} onClick={()=>setMethod(p.id)}>{p.icon}<small>{p.name}</small></button>)}</div>
    {method==='cash'&&<div className="pi-pos-cash"><label>Monto recibido (S/)<input type="number" min="0" inputMode="decimal" step=".01" value={received} onChange={e=>setReceived(e.target.value)} placeholder={`Mínimo: ${(total/100).toFixed(2)}`}/></label><div><span>Vuelto</span><strong>{PEN(Math.max(0,receivedCents-total))}</strong></div></div>}
    <p className="pi-pos-disclaimer">Cobro registrado en el sistema; Yape, Plin y tarjeta requieren verificar por separado la transacción externa. Los tickets son internos, sin validez SUNAT.</p>
    {error&&<div className="pi-pos-error" role="alert">{error}</div>}
    {!pendingOrder&&<button className="pi-pos-create-only" disabled={busy||!count} onClick={()=>void createOnly()}>♨ Enviar pedido a cocina sin cobrar</button>}
    <button className="pi-pos-charge" disabled={busy||(!pendingOrder&&!count)||!readyToPay} onClick={()=>void checkout()}>{busy?'Procesando…':pendingOrder?'▣ Confirmar cobro del pedido':'▣ Cobrar pedido'}</button>
   </aside>
  </div>
  {paidOrder&&<div className="pi-sale-overlay" role="dialog" aria-modal="true" aria-label="Venta completada"><div className="pi-sale-modal"><div className="pi-sale-success">✓</div><h2>¡Venta completada con éxito!</h2><p>El pago del pedido #{paidOrder.id} fue registrado en el sistema.</p><div className="pi-sale-paper"><h3>El Paladar del Inka</h3><b>Ticket interno · No es comprobante tributario</b><div><span>Pedido</span><strong>#{paidOrder.id}</strong></div><div><span>Medio de pago</span><strong>{paymentOptions.find(x=>x.id===method)?.name}</strong></div><div><span>Total</span><strong>{PEN(paidOrder.total_cents)}</strong></div>{receipt&&<p>{receipt.disclaimer}</p>}</div><div className="pi-sale-actions"><button onClick={()=>window.print()}>Imprimir ticket</button><button onClick={()=>{setPaidOrder(null);setReceipt(null)}}>Nueva venta</button><button onClick={()=>{setPaidOrder(null);onNavigate('orders')}}>Ver pedidos</button></div></div></div>}
 </div>;
}
