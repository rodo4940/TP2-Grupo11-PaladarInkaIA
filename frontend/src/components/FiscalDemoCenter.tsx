import {useCallback,useEffect,useState} from 'react';
import {api,post} from '../services/api';
import type {BillingDocument,FiscalDemoDocument,Role} from '../types/domain';
import './fiscal-lab.css';

const money=(c:number)=>new Intl.NumberFormat('es-PE',{style:'currency',currency:'PEN'}).format(c/100);
type DocKind='01'|'03';
type PersonKind='0'|'1'|'6';
const newKey=()=>`LAB-${Date.now()}-${Math.random().toString(36).slice(2)}`;

/** Generación de documentos DEMOSTRATIVOS: sin SUNAT, CDR ni firma electrónica. */
export function FiscalDemoCenter({token,role,payments}:{
 token:string;role:Role;payments:BillingDocument[];
}){
 const [docs,setDocs]=useState<FiscalDemoDocument[]>([]);
 const [paymentId,setPaymentId]=useState('');
 const [kind,setKind]=useState<DocKind>('03');
 const [docKind,setDocKind]=useState<PersonKind>('0');
 const [docNumber,setDocNumber]=useState('');
 const [customerName,setCustomerName]=useState('CONSUMIDOR FINAL (PRUEBA)');
 const [affectation,setAffectation]=useState('10');
 const [reason,setReason]=useState('Anulación de laboratorio asociada a devolución registrada');
 const [detail,setDetail]=useState<FiscalDemoDocument|null>(null);
 const [feedback,setFeedback]=useState('');
 const [error,setError]=useState('');
 const [loading,setLoading]=useState(false);
 const reload=useCallback(async()=>{
    try{setDocs(await api<FiscalDemoDocument[]>('/fiscal-demo/documents',token));}
    catch(e){setError(e instanceof Error?e.message:'No se pudieron consultar los documentos simulados')}
 },[token]);
 useEffect(()=>{void reload()},[reload]);
 const eligible=payments.filter(p=>!docs.some(d=>d.payment_id===p.id&&(d.document_type==='01'||d.document_type==='03')));
 const issued=docs.filter(d=>d.document_type==='01'||d.document_type==='03');
 const creditAvailable=issued.filter(d=>
   payments.some(p=>p.id===d.payment_id&&p.refund_status==='confirmed')&&
   !docs.some(c=>c.reference_document_id===d.id));
 const issue=async()=>{
  if(!paymentId){setError('Selecciona un cobro registrado.');return;}
  setLoading(true);setError('');setFeedback('');
  try{
   const saved=await post<FiscalDemoDocument>('/fiscal-demo/documents',{
    payment_id:Number(paymentId),document_type:kind,customer_document_type:docKind,
    customer_document_number:docNumber.trim(),customer_name:customerName.trim(),
    affectation_code:affectation,idempotency_key:newKey()
   },token);
   setFeedback(`Creado ${saved.number} — simulación local sin validez tributaria.`);
   setPaymentId('');await reload();await show(saved.id);
  }catch(e){setError(e instanceof Error?e.message:'No se pudo simular el comprobante');}
  finally{setLoading(false)}
 };
 const credit=async(id:number)=>{
  setLoading(true);setError('');setFeedback('');
  try{
    const saved=await post<FiscalDemoDocument>('/fiscal-demo/credit-notes',{
      original_document_id:id,reason_code:'01',reason:reason.trim(),idempotency_key:newKey()
    },token);
    setFeedback(`Nota ${saved.number} simulada con referencia al original; NO enviada a SUNAT.`);
    await reload();await show(saved.id);
  }catch(e){setError(e instanceof Error?e.message:'No se pudo crear nota demo');}
  finally{setLoading(false)}
 };
 const show=async(id:number)=>{
  try{setDetail(await api<FiscalDemoDocument>(`/fiscal-demo/documents/${id}`,token))}
  catch(e){setError(e instanceof Error?e.message:'No se pudo leer el XML');}
 };
 const verify=async()=>{
  if(!detail)return;
  try{
    const d=await api<{sha256_matches:boolean;xml_well_formed:boolean;official_sunat_validation:boolean}>(`/fiscal-demo/documents/${detail.id}/verify`,token);
    setFeedback(d.sha256_matches&&d.xml_well_formed?'XML íntegro (validación LOCAL). SUNAT no consultada.':'Falló la verificación local de integridad.');
  }catch(e){setError(e instanceof Error?e.message:'No se pudo verificar XML')}
 };
 const download=()=>{
  if(!detail?.xml_demo)return;
  const url=URL.createObjectURL(new Blob([detail.xml_demo],{type:'application/xml;charset=utf-8'}));
  const anchor=document.createElement('a');anchor.href=url;anchor.download=`LAB-${detail.number}.xml`;anchor.click();
  window.setTimeout(()=>URL.revokeObjectURL(url),1000);
 };
 return <section className="panel fiscal-lab" aria-labelledby="fiscal-lab-title">
  <div className="panel-head"><div><span className="eyebrow">LABORATORIO TRIBUTARIO</span>
    <h3 id="fiscal-lab-title">Simulador de boletas, facturas y notas de crédito</h3>
    <p>Documentos con totales, datos de receptor, estructura XML UBL 2.1 parcial y SHA-256.</p></div></div>
  <p className="fiscal-warning" role="note"><strong>SOLO DEMOSTRACIÓN · SIN VALIDEZ TRIBUTARIA.</strong> No utiliza RUC de emisor real, certificados, firma digital, recepción SUNAT ni CDR oficial. La comprobación es exclusivamente local.</p>
  {error&&<p className="notice error" role="alert">{error}</p>}
  {feedback&&<p className="notice" role="status">{feedback}</p>}
  <div className="fiscal-grid">
    <div className="fiscal-form">
      <label htmlFor="fiscal-payment">Pago confirmado</label>
      <select id="fiscal-payment" value={paymentId} onChange={e=>setPaymentId(e.target.value)}>
       <option value="">Selecciona un pago</option>{eligible.map(p=><option value={p.id} key={p.id}>{p.document_number} · {money(p.total_cents)}</option>)}
      </select>
      <label htmlFor="fiscal-type">Tipo de documento</label>
      <select id="fiscal-type" value={kind} onChange={e=>{
        const next=e.target.value as DocKind;setKind(next);
        if(next==='01')setDocKind('6');
        else {setDocKind('0');setDocNumber('');}
      }}>
       <option value="03">Boleta demo · 03</option><option value="01">Factura demo · 01</option>
      </select>
      <label htmlFor="fiscal-doc-type">Documento del receptor</label>
      <select id="fiscal-doc-type" value={docKind} onChange={e=>{
         setDocKind(e.target.value as PersonKind);setDocNumber('');
      }} disabled={kind==='01'}>
       {kind==='03'&&<option value="0">Consumidor sin documento</option>}
       {kind==='03'&&<option value="1">DNI · 8 dígitos</option>}
       <option value="6">RUC · 11 dígitos</option>
      </select>
      {docKind!=='0'&&<><label htmlFor="fiscal-doc-number">Número de documento (solo datos de laboratorio)</label>
        <input id="fiscal-doc-number" value={docNumber} inputMode="numeric" maxLength={11}
         onChange={e=>setDocNumber(e.target.value.replace(/\D/g,''))} placeholder={docKind==='6'?'RUC verificado':'DNI de pruebas'}/></>}
      <label htmlFor="fiscal-name">Razón social / nombre</label>
      <input id="fiscal-name" value={customerName} maxLength={160} onChange={e=>setCustomerName(e.target.value)}/>
      <label htmlFor="fiscal-tax">Afectación IGV de ejemplo</label>
      <select id="fiscal-tax" value={affectation} onChange={e=>setAffectation(e.target.value)}>
       <option value="10">10 · Gravado 18 % (referencial)</option>
       <option value="20">20 · Exonerado</option>
       <option value="30">30 · Inafecto</option>
      </select>
      <button type="button" className="primary" disabled={loading||!paymentId} onClick={()=>void issue()}>
       {loading?'Generando…':'Generar XML DEMO'}
      </button>
    </div>
    <div className="fiscal-documents">
      <h4>Historial de laboratorio</h4>
      <div className="fiscal-records">
      {docs.length===0&&<p>No hay comprobantes simulados.</p>}
      {docs.map(d=><button type="button" key={d.id} onClick={()=>void show(d.id)} className="fiscal-record">
       <strong>{d.number}</strong><span>{d.document_label} · {money(d.total_cents)}</span>
       <small>Estado: SIMULADO · SHA {d.sha256.slice(0,12)}…</small>
      </button>)}
      </div>
      {role==='admin'&&creditAvailable.length>0&&<div className="fiscal-credit">
       <h4>Notas de crédito demostrativas</h4>
       <label htmlFor="credit-reason">Motivo de anulación de laboratorio</label>
       <input id="credit-reason" maxLength={250} value={reason} onChange={e=>setReason(e.target.value)}/>
       {creditAvailable.map(d=><button className="secondary" type="button" key={d.id} disabled={loading}
         onClick={()=>void credit(d.id)}>Simular nota sobre {d.number}</button>)}
      </div>}
    </div>
  </div>
  {detail&&<div className="fiscal-preview">
    <h4>{detail.number} · Vista técnica XML</h4>
    <p>Emisor ficticio: {detail.issuer_ruc} · Total: {money(detail.total_cents)} · IGV referencial: {money(detail.tax_cents)} · <strong>Sin CDR ni firma</strong></p>
    <div className="fiscal-actions"><button type="button" className="secondary" onClick={()=>void verify()}>Verificar SHA-256 local</button><button type="button" className="secondary" onClick={download}>Exportar XML DEMO</button></div>
    <pre tabIndex={0}>{detail.xml_demo??'Consulta el detalle del documento.'}</pre>
  </div>}
 </section>;
}
