import {useEffect,useRef,useState} from 'react';
import {api,post} from '../services/api';
import type {AssistantAnswer, BusinessContext} from '../types/domain';

type Exchange={id:number;question:string;answer:string;mode:string;warning:string;basis:string[]};
const questions=[
 '¿Cómo van las ventas de hoy?',
 '¿Qué ingredientes debo reponer?',
 '¿Cuáles son los productos más vendidos?',
 '¿Cómo están los pedidos de cocina?',
];
const money=(c:number)=>new Intl.NumberFormat('es-PE',{style:'currency',currency:'PEN'}).format(c/100);

export function BusinessCopilot({token}:{token:string}){
 const [context,setContext]=useState<BusinessContext|null>(null);
 const [contextError,setContextError]=useState('');
 const [input,setInput]=useState('');
 const [history,setHistory]=useState<Exchange[]>([]);
 const [busy,setBusy]=useState(false);
 const [error,setError]=useState('');
 const idRef=useRef(0);
 const inputRef=useRef<HTMLInputElement>(null);
 useEffect(()=>{
  let live=true;
  void api<BusinessContext>('/ai/business-context',token).then(data=>{if(live)setContext(data)})
  .catch(e=>{if(live)setContextError(e instanceof Error?e.message:'Sin conexión con analítica')});
  return()=>{live=false};
 },[token]);
 const send=async(question:string)=>{
  const q=question.trim();if(q.length<5||busy)return;
  setBusy(true);setError('');setInput('');
  try{
    const answer=await post<AssistantAnswer>('/ai/ask',{question:q},token);
    setHistory(old=>[...old.slice(-9),{id:++idRef.current,question:q,answer:answer.answer,
     mode:answer.mode,warning:answer.warning,basis:answer.basis}]);
  }catch(e){setError(e instanceof Error?e.message:'No fue posible consultar al asistente');setInput(q)}
  finally{setBusy(false);inputRef.current?.focus();}
 };
 const snap=context?.snapshot;
 return <section className="copilot-panel" aria-label="Asistente de decisiones">
  <div className="copilot-intro">
    <div className="copilot-emblem" aria-hidden="true"><span>✧</span></div>
    <div><span className="eyebrow">ASISTENCIA PARA EL NEGOCIO</span><h2>Consulta tu operación</h2><p>Preguntas respondidas con ventas, pedidos y existencias reales del entorno conectado.</p></div>
    <div className="copilot-mode"><span className="copilot-signal"/> {history.at(-1)?.mode==='modelo_externo_configurado'?'Modelo configurado':'Análisis explicable'}</div>
  </div>
  <div className="copilot-layout">
    <div className="copilot-main">
      <div className="copilot-conversation" aria-live="polite" aria-label="Respuestas del asistente">
       <div className="copilot-greeting"><span className="copilot-avatar" aria-hidden="true">✧</span><div><strong>Tu analista de operaciones</strong><p>Puedo explicar el estado de la caja, el inventario, las pizzas más vendidas y las comandas. No realizo cobros, cambios de stock ni órdenes por mi cuenta.</p></div></div>
       {history.map(exchange=><div className="copilot-turn" key={exchange.id}>
         <div className="copilot-question">{exchange.question}</div>
         <div className="copilot-answer"><span className="copilot-avatar" aria-hidden="true">✧</span><div><p>{exchange.answer}</p><small>{exchange.mode==='modelo_externo_configurado'?'Respuesta con modelo externo habilitado':'Resultado verificable de reglas locales'} · Base: {exchange.basis.map(x=>x.replaceAll('_',' ')).join(', ')}</small></div></div>
       </div>)}
       {busy&&<div className="copilot-loading" role="status"><span className="copilot-avatar" aria-hidden="true">✧</span>Analizando los registros del sistema…</div>}
       {error&&<div className="notice error" role="alert">{error}</div>}
      </div>
      <div className="copilot-suggestions" aria-label="Preguntas sugeridas">{questions.map(q=><button type="button" key={q} disabled={busy} onClick={()=>void send(q)}>{q}</button>)}</div>
      <form className="copilot-compose" onSubmit={e=>{e.preventDefault();void send(input)}}><label htmlFor="ai-question" className="sr-only">Pregunta al asistente</label><input id="ai-question" ref={inputRef} value={input} maxLength={500} minLength={5} onChange={e=>setInput(e.target.value)} placeholder="Ejemplo: ¿Qué insumos necesitan reposición?" required/><button type="submit" className="primary" disabled={busy||input.trim().length<5}>{busy?'Consultando…':'Consultar'}<span aria-hidden="true"> ↗</span></button></form>
      <p className="copilot-legal">El análisis es informativo. No envía datos personales al proveedor de IA; un modelo externo solo se habilita si el administrador configura una clave de API en el servidor.</p>
    </div>
    <aside className="copilot-context" aria-label="Indicadores utilizados por el asistente">
     <div className="copilot-context-heading"><span className="eyebrow">CONTEXTO DE RESPUESTA</span><h3>Datos disponibles</h3><p>{snap? `Fecha local: ${snap.date_lima}`:'Consultando información…'}</p></div>
     {contextError&&<div role="status" className="notice error">{contextError}</div>}
     <div className="copilot-stat"><span>Ingresos del día</span><strong>{snap?money(snap.today_sales_cents):'—'}</strong><small>Pagos registrados en PEN</small></div>
     <div className="copilot-stat"><span>Pedidos activos</span><strong>{snap?.active_orders??'—'}</strong><small>En cocina y por entregar</small></div>
     <div className="copilot-stat"><span>Alertas de insumos</span><strong>{snap?.low_stock.length??'—'}</strong><small>Stock menor o igual al mínimo</small></div>
     {snap?.top_products.length?<div className="copilot-products"><h4>Productos destacados</h4>{snap.top_products.slice(0,3).map(x=><div key={x.name}><span>{x.name}</span><b>{x.units} uds.</b></div>)}</div>:<div className="copilot-products"><p>Las ventas pagadas aparecerán aquí al registrar pagos.</p></div>}
     <p className="copilot-context-note">No se usa información personal del cliente en las respuestas. Las recomendaciones requieren supervisión humana.</p>
    </aside>
  </div>
 </section>;
}
