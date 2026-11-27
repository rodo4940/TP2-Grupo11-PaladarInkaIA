import {useMemo,useState} from 'react';
import {post} from '../services/api';
import type {Dashboard,Ingredient,Order,StockMovement} from '../types/domain';
type Props={ingredients:Ingredient[];movements:StockMovement[];orders:Order[];dashboard:Dashboard|null;admin:boolean;token:string;busy:boolean;onRefresh:()=>Promise<unknown>};
function exportCsv(ingredients:Ingredient[]){const rows=[['SKU','Insumo','Unidad','Stock','Mínimo'],...ingredients.map(i=>[i.sku,i.name,i.unit,i.stock.toString(),i.minimum_stock.toString()])];const csv='\ufeff'+rows.map(r=>r.map(v=>'"'+v.replaceAll('"','""')+'"').join(';')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='inventario_paladar_inka.csv';a.click();URL.revokeObjectURL(url)}
export function ReferenceInventory({ingredients,movements,orders,dashboard,admin,token,busy,onRefresh}:Props){
 const [search,setSearch]=useState('');
 const [filter,setFilter]=useState<'all'|'low'|'normal'>('all');
 const [selectedId,setSelectedId]=useState<number|null>(null);
 const [delta,setDelta]=useState('');
 const [reason,setReason]=useState('Reposición de proveedor');
 const [saving,setSaving]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState('');
 const selected=ingredients.find(x=>x.id===selectedId)??ingredients[0]??null;
 const low=(i:Ingredient)=>i.stock<=i.minimum_stock;
 const visible=useMemo(()=>ingredients.filter(i=>(filter==='all'||(filter==='low'?low(i):!low(i)))&&`${i.sku} ${i.name} ${i.unit}`.toLowerCase().includes(search.trim().toLowerCase())),[ingredients,search,filter]);
 const selectedMoves=selected?movements.filter(m=>m.ingredient_id===selected.id):[];
 const totals=[{label:'Insumos en inventario',value:ingredients.length,icon:'⬡'},{label:'Bajo stock mínimo',value:ingredients.filter(low).length,icon:'⚠'},{label:'Movimientos registrados',value:movements.length,icon:'≡'},{label:'Pedidos registrados',value:orders.length,icon:'▤'}];
 async function adjust(){if(!selected||!admin||saving||!Number.isFinite(Number(delta))||Number(delta)===0||reason.trim().length<4)return;setSaving(true);setError('');setNotice('');try{await post(`/ingredients/${selected.id}/adjust`,{delta:Number(delta),reason:reason.trim()},token);setDelta('');setNotice('Movimiento de inventario registrado correctamente');await onRefresh()}catch(e){setError(e instanceof Error?e.message:'No se pudo actualizar el inventario')}finally{setSaving(false)}}
 return <div className="pi-inventory">
  <div className="pi-module-title"><div><span className="pi-title-icon">⬡</span><div><h1>Inventario</h1><p>Gestión de insumos, existencias, movimientos y consumo por pedidos</p></div></div><div className="pi-title-actions"><button onClick={()=>exportCsv(ingredients)}>↓ Exportar CSV</button>{admin&&<button onClick={()=>document.getElementById('pi-stock-form')?.scrollIntoView({behavior:'smooth'})}>＋ Ajustar stock</button>}</div></div>
  <div className="pi-inventory-metrics">{totals.map(x=><div key={x.label}><span>{x.icon}</span><div><small>{x.label}</small><strong>{x.value}</strong></div></div>)}</div>
  <div className="pi-inventory-tools"><div className="pi-inventory-filter">{(['all','low','normal'] as const).map(x=><button key={x} className={filter===x?'selected':''} onClick={()=>setFilter(x)}>{x==='all'?'Todos':x==='low'?'Stock bajo':'Stock normal'}</button>)}</div><label><span aria-hidden="true">⌕</span><input type="search" aria-label="Buscar en inventario" placeholder="Buscar insumo o SKU..." value={search} onChange={e=>setSearch(e.target.value)}/></label></div>
  <div className="pi-inventory-layout">
  <section className="pi-inventory-list"><header><h3>Insumos ({visible.length})</h3><span>Stock mínimo · Estado</span></header><div className="pi-inventory-table-wrap"><table><thead><tr><th>SKU</th><th>Insumo</th><th>Stock actual</th><th>Mínimo</th><th>Unidad</th><th>Estado</th></tr></thead><tbody>{visible.map(i=><tr key={i.id} onClick={()=>setSelectedId(i.id)} className={selected?.id===i.id?'selected':''}><td><code>{i.sku}</code></td><td><b>{i.name}</b></td><td>{i.stock}</td><td>{i.minimum_stock}</td><td>{i.unit}</td><td><span className={`pi-state ${low(i)?'pi-state-cancelled':'pi-state-delivered'}`}>{low(i)?'Crítico':'Normal'}</span></td></tr>)}</tbody></table>{!visible.length&&<div className="pi-empty">No existen insumos con este filtro.</div>}</div></section>
  <aside className="pi-inventory-detail">{selected?<><header><div><span>DETALLE DEL INSUMO</span><h3>{selected.name}</h3><p>{selected.sku} · Unidad: {selected.unit}</p></div><strong className={low(selected)?'pi-low-stock':'pi-good-stock'}>{low(selected)?'Stock bajo':'Normal'}</strong></header>
   <div className="pi-inventory-detail-metrics"><div><small>Stock actual</small><strong>{selected.stock} {selected.unit}</strong></div><div><small>Stock mínimo</small><strong>{selected.minimum_stock} {selected.unit}</strong></div></div>
   <div className="pi-inventory-movements"><h4>Movimientos (Kardex)</h4>{selectedMoves.slice(0,15).map(m=><div key={m.id}><span className={m.delta<0?'minus':'plus'}>{m.delta>0?'+':''}{m.delta} {selected.unit}</span><div><strong>{m.reference}</strong><small>{new Date(m.created_at).toLocaleString('es-PE',{timeZone:'America/Lima',dateStyle:'short',timeStyle:'short'})}</small></div><b>{m.balance}</b></div>)}{!selectedMoves.length&&<p>No hay movimientos para este insumo.</p>}</div>
   {admin&&<form id="pi-stock-form" onSubmit={e=>{e.preventDefault();void adjust()}} className="pi-inventory-adjust"><h4>Registrar ajuste autorizado</h4><label>Variación (+ entrada, − salida)<input type="number" step="any" required value={delta} onChange={e=>setDelta(e.target.value)} placeholder="Ejemplo: 200 o -20"/></label><label>Motivo<input value={reason} minLength={4} required onChange={e=>setReason(e.target.value)} placeholder="Motivo del ajuste"/></label><button type="submit" disabled={saving||busy||!delta||Number(delta)===0}>{saving?'Guardando…':'Guardar movimiento'}</button></form>}
   {!admin&&<p className="pi-inventory-limited">Solo administración puede modificar las existencias.</p>}
   {error&&<p className="pi-pos-error" role="alert">{error}</p>}{notice&&<p className="pi-inventory-notice" role="status">{notice}</p>}
   </>:<div className="pi-empty">No existen insumos registrados.</div>}</aside>
  </div>
 </div>;
}