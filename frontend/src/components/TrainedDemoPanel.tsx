import {useEffect,useState} from 'react';
import {api} from '../services/api';

interface TrainedMetric {
 name:string;coefficients:number[];holdout:{mae:number;wape_pct:number;bias_units:number};
 baseline:{mae:number;wape_pct:number;bias_units:number};samples_train:number;samples_test:number;
 quality_gate_passed:boolean;
}
interface TrainedMetrics {
 model_version:string;model_type:string;dataset_origin:string;dataset_sha256:string;
 source_business_data:boolean;train_period:string;holdout_period:string;
 products:Record<string,TrainedMetric>;warning:string;
}
interface Predicted {
 sku:string;name:string;mae_holdout:number;baseline_mae:number;quality_gate_passed:boolean;
 predictions:Array<{day:string;units:number}>;
}
interface PredictionResponse {items:Predicted[];warning:string;mode:string;horizon_days:number;}

export function TrainedDemoPanel({token}:{token:string}){
 const [metrics,setMetrics]=useState<TrainedMetrics|null>(null);
 const [forecast,setForecast]=useState<PredictionResponse|null>(null);
 const [error,setError]=useState('');
 const [days,setDays]=useState('7');
 useEffect(()=>{
   let live=true;
   void api<TrainedMetrics>('/ai/trained-demo/metrics',token)
    .then(value=>{if(live)setMetrics(value)})
    .catch(e=>{if(live)setError(e instanceof Error?e.message:'No se pudo cargar la evaluación')});
   return()=>{live=false};
 },[token]);
 useEffect(()=>{
   let live=true;
   void api<PredictionResponse>(`/ai/trained-demo/forecast?days=${days}`,token)
    .then(value=>{if(live)setForecast(value)})
    .catch(e=>{if(live)setError(e instanceof Error?e.message:'No se pudo cargar la proyección')});
   return()=>{live=false};
 },[days,token]);
 return <section className="panel" aria-labelledby="trained-demo-title" style={{marginBottom:'20px',minWidth:0}}>
   <div className="panel-head"><div><span className="eyebrow">PREDICCIÓN · MODELO ENTRENADO</span>
    <h3 id="trained-demo-title">Laboratorio de demanda con regresión Ridge</h3>
    <p>Entrenamiento real sobre series sintéticas, separado de las ventas reales del establecimiento.</p>
   </div><span className="tag tag-pending">DATOS FICTICIOS</span></div>
   <div className="billing-disclaimer" role="note"><span aria-hidden="true">ⓘ</span><span>
     <strong>Modelo ML real, datos de laboratorio.</strong> No fue entrenado ni validado con ventas del restaurante.
     Las proyecciones siguientes no autorizan compra de ingredientes ni constituyen demanda comercial.
   </span></div>
   {error&&<p role="alert" className="notice error">{error}</p>}
   {metrics&&<div>
    <p style={{fontSize:'12px',overflowWrap:'anywhere'}}>Versión: <strong>{metrics.model_version}</strong> · Dataset SHA-256: <code>{metrics.dataset_sha256}</code></p>
    <p style={{fontSize:'12px'}}>Entrenamiento: {metrics.train_period} · Validación: {metrics.holdout_period} · 112 días de entrenamiento y 28 de prueba por SKU.</p>
    <div style={{display:'grid',gridTemplateColumns:'repeat(auto-fit,minmax(min(100%,210px),1fr))',gap:12}}>
      {Object.entries(metrics.products).map(([sku,m])=><article key={sku} style={{border:'1px solid #d3dccf',borderRadius:12,padding:13}}>
       <strong>{m.name}</strong><small style={{display:'block'}}>SKU: {sku}</small>
       <div style={{fontSize:13,marginTop:7}}>MAE del modelo: <strong>{m.holdout.mae}</strong> uds.</div>
       <div style={{fontSize:13}}>MAE baseline: <strong>{m.baseline.mae}</strong> uds.</div>
       <div style={{fontSize:13}}>WAPE: {m.holdout.wape_pct}% · <strong>{m.quality_gate_passed?'Mejora la referencia':'No supera la referencia'}</strong></div>
      </article>)}
    </div>
   </div>}
   <div style={{display:'flex',gap:10,alignItems:'center',flexWrap:'wrap',marginTop:15}}>
     <label htmlFor="trained-horizon">Horizonte de pronóstico</label>
     <select id="trained-horizon" value={days} onChange={e=>setDays(e.target.value)} style={{minHeight:44,padding:'8px 12px'}}>
      <option value="1">1 día</option><option value="7">7 días</option><option value="14">14 días</option>
     </select>
   </div>
   <div className="forecast-list" style={{marginTop:12}}>
    {forecast?.items.map(item=><div key={item.sku} style={{minWidth:0}}>
      <span style={{minWidth:0}}><b>{item.name}</b>
       <small style={{whiteSpace:'normal',overflowWrap:'anywhere'}}>{item.predictions.map(p=>`${p.day}: ${p.units}`).join(' · ')}</small>
      </span><strong>{item.predictions[0]?.units??0}<small> uds. primer día</small></strong>
    </div>)}
   </div>
   <p className="method-note">El modelo ajusta coeficientes mediante mínimos cuadrados regularizados. Compara resultados en fechas posteriores al entrenamiento y conserva los errores medidos. Para uso real falta un histórico autorizado del restaurante, nuevos tests y aprobación de negocio.</p>
 </section>;
}
