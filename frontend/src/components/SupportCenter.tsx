import {useEffect,useRef} from 'react';
import type {Role} from '../types/domain';

type HelpView='dashboard'|'pos'|'orders'|'kitchen'|'inventory'|'products'|'customers'|'reports'|'ai'|'users'|'settings'|'billing';
const viewHelp:Record<HelpView,{title:string;steps:string[]}>={
 dashboard:{title:'Panel general',steps:['Consulta los indicadores que provienen del servidor.','Usa Actualizar para consultar información nueva.','Abre la sección correspondiente desde los accesos rápidos.']},
 pos:{title:'Punto de venta',steps:['Busca una pizza o filtra por categoría y añádela al carrito.','Indica modalidad, referencia y cliente opcional.','Confirma el pedido y registra el pago por el monto confirmado.']},
 orders:{title:'Pedidos',steps:['Filtra por estado o busca por número y mesa.','Abre Detalle para revisar productos, seguimiento y pago.','Desde una cuenta autorizada, continúa el flujo o emite el ticket interno.']},
 kitchen:{title:'Cocina',steps:['Revisa las comandas ordenadas por fase.','Inicia la preparación, marca el pedido listo y registra la entrega.','El estado se guarda en la API para conservar la trazabilidad.']},
 inventory:{title:'Inventario y Kardex',steps:['Consulta las existencias por insumo y sus umbrales.','Busca movimientos trazables vinculados a pedidos.','Registra ajustes de inventario solo con cuenta autorizada.']},
 products:{title:'Productos y recetas',steps:['Administra precios, disponibilidad y categorías.','Asigna cantidades de ingredientes antes de vender un producto.','Las fotografías son ilustrativas: no sustituyen la validación de recetas.']},
 customers:{title:'Clientes',steps:['Registra clientes y sus datos de contacto.','Consulta historial y gastos basados en pedidos pagados.','Los puntos mostrados son referenciales, no un programa de canjes.']},
 reports:{title:'Reportes',steps:['Consulta ingresos registrados por pago.','Compara los productos según unidades efectivamente cobradas.','Exporta a CSV cuando necesites respaldar el análisis.']},
 ai:{title:'Analítica operativa',steps:['Revisa el ranking de menú y una estimación descriptiva de demanda.','Pregunta al asistente por ventas, inventario, productos y cocina; la API responde a partir de indicadores.','Si no hay clave de modelo externo se usan reglas explicables; no se ejecutan cambios automáticamente.']},
 billing:{title:'Caja y comprobantes',steps:['Registra un pago en Ventas / POS.','Consulta y filtra constancias INT por cliente, pedido o medio de pago.','Imprime el ticket interno. No sustituye la boleta o factura electrónica SUNAT.']},
 users:{title:'Usuarios y roles',steps:['Crea usuarios con contraseñas robustas.','Asigna permisos de caja, cocina o administración.','Revisa la bitácora y desactiva las cuentas sin uso.']},
 settings:{title:'Configuración',steps:['Comprueba la versión y el entorno conectados.','Actualiza la contraseña si es necesario.','Cambiar la contraseña revoca sesiones previas.']},
};
export function SupportCenter({open,onClose,view,role}:{open:boolean;onClose:()=>void;view:HelpView;role:Role}){
 const dialogRef=useRef<HTMLDivElement>(null);
 useEffect(()=>{
  if(!open)return;
  const before=document.activeElement as HTMLElement|null;
  const oldOverflow=document.body.style.overflow;
  document.body.style.overflow='hidden';
  dialogRef.current?.querySelector<HTMLButtonElement>('.help-close')?.focus();
  const trap=(event:KeyboardEvent)=>{
   if(event.key!=='Tab')return;
   const items=[...(dialogRef.current?.querySelectorAll<HTMLElement>('button,a[href],input,select,textarea,[tabindex]:not([tabindex="-1"])')||[])].filter(el=>!el.hasAttribute('disabled'));
   if(!items.length)return;
   const first=items[0],last=items[items.length-1];
   if(event.shiftKey && (document.activeElement===first||!dialogRef.current?.contains(document.activeElement))){event.preventDefault();last.focus();}
   else if(!event.shiftKey && (document.activeElement===last||!dialogRef.current?.contains(document.activeElement))){event.preventDefault();first.focus();}
  };
  document.addEventListener('keydown',trap);
  return()=>{document.removeEventListener('keydown',trap);document.body.style.overflow=oldOverflow;before?.focus();};
 },[open]);
 if(!open)return null;
 const item=viewHelp[view];
 const shortcuts=[['Alt + 1','Panel general'],['Alt + 2','Ventas / POS'],['Alt + 3','Pedidos'],['Alt + 4','Cocina']];
 return <div className="help-overlay" onMouseDown={event=>{if(event.target===event.currentTarget)onClose()}}>
  <div className="help-dialog" ref={dialogRef} role="dialog" aria-modal="true" aria-labelledby="help-title" aria-describedby="help-description">
    <header className="help-head"><div><span className="eyebrow">GUÍA RÁPIDA</span><h2 id="help-title">Centro de ayuda</h2><p id="help-description">Orientación práctica según la pantalla que estás utilizando.</p></div>
      <button className="help-close" aria-label="Cerrar ayuda" onClick={onClose}>×</button></header>
    <section className="help-section"><span className="eyebrow">ESTÁS EN</span><h3>{item.title}</h3>
      <ol>{item.steps.map(step=><li key={step}>{step}</li>)}</ol></section>
    <section className="help-section"><span className="eyebrow">NAVEGACIÓN RÁPIDA</span>
      <div className="shortcut-grid">{shortcuts.filter(([_,label])=>(label==='Ventas / POS'?role!=='kitchen':label==='Cocina'?role!=='cashier':true)).map(([hotkey,label])=><div key={hotkey}><kbd>{hotkey}</kbd><span>{label}</span></div>)}</div>
      <p className="help-hint">Pulsa <kbd>Esc</kbd> para cerrar esta ayuda o el menú móvil.</p>
    </section>
    <footer className="help-footer"><span>El Paladar del Inka · Gestión operativa</span><button className="primary" onClick={onClose}>Entendido</button></footer>
   </div>
 </div>;
}
