import type {Role} from '../types/domain';
import type {ReactNode} from 'react';

export type DockView='dashboard'|'pos'|'orders'|'kitchen'|'inventory'|'products'|'customers'|'reports'|'ai'|'users'|'settings'|'billing';
const dockIcons:Record<string,ReactNode>={
 dashboard:<><rect x="3.5" y="3.5" width="7" height="7" rx="2"/><rect x="13.5" y="3.5" width="7" height="7" rx="2"/><rect x="3.5" y="13.5" width="7" height="7" rx="2"/><rect x="13.5" y="13.5" width="7" height="7" rx="2"/></>,
 pos:<><path d="M3 4h3l2 11h11l2-8H7"/><circle cx="9" cy="20" r="1"/><circle cx="18" cy="20" r="1"/></>,
 orders:<><path d="M7 4h10l3 3v13H4V7z"/><path d="M8 10h8M8 14h8M8 18h5"/></>,
 kitchen:<><path d="M4 13c-2-4 1-7 5-7 1-4 7-4 8 0 4 0 6 3 4 7"/><path d="M5 14v6h14v-6"/></>,
 inventory:<><path d="m3 7 9-4 9 4v10l-9 4-9-4Z"/><path d="m3 7 9 5 9-5M12 12v9"/></>,
};
const menu:Array<{view:DockView;label:string;roles:Role[]}>= [
 {view:'dashboard',label:'Inicio',roles:['admin','cashier','kitchen']},
 {view:'pos',label:'Vender',roles:['admin','cashier']},
 {view:'orders',label:'Pedidos',roles:['admin','cashier','kitchen']},
 {view:'kitchen',label:'Cocina',roles:['admin','kitchen']},
 {view:'inventory',label:'Stock',roles:['admin','cashier','kitchen']},
];
export function MobileDock({view,role,onNavigate}:{view:DockView;role:Role;onNavigate:(view:DockView)=>void}){
 const items=menu.filter(item=>item.roles.includes(role));
 return <div className="mobile-dock" role="navigation" aria-label="Navegación rápida móvil">
   {items.map(item=><button key={item.view} type="button" className={view===item.view?'dock-item dock-item-active':'dock-item'} onClick={()=>onNavigate(item.view)} aria-label={`Ir a ${item.label}`} aria-current={view===item.view?'page':undefined}>
      <span className="dock-icon"><svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{dockIcons[item.view]}</svg></span>
      <span className="dock-label">{item.label}</span>
   </button>)}
 </div>;
}
