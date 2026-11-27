import {useId} from 'react';
/**
 * Identidad vectorial original para El Paladar del Inka.
 * Sol geométrico, tocado andino abstracto y horno/pizza; no representa una
 * imagen histórica oficial ni utiliza iconografía ceremonial auténtica.
 */
export function InkaBrand({size=46,decorative=true}:{size?:number;decorative?:boolean}){
 const seed=useId().replaceAll(':','');
 const sunId='inka-sun-'+seed, faceId='inka-face-'+seed;
 return <svg className="inka-brand-icon" viewBox="0 0 80 80" width={size} height={size} fill="none"
  role={decorative?undefined:'img'} aria-hidden={decorative?'true':undefined}
  aria-label={decorative?undefined:'Símbolo de El Paladar del Inka: sol andino y gastronomía'} focusable="false">
  <defs><linearGradient id={sunId} x1="5" y1="7" x2="68" y2="70" gradientUnits="userSpaceOnUse"><stop stopColor="#ffe4a5"/><stop offset=".53" stopColor="#e0a951"/><stop offset="1" stopColor="#a96931"/></linearGradient>
  <linearGradient id={faceId} x1="25" y1="23" x2="51" y2="67" gradientUnits="userSpaceOnUse"><stop stopColor="#f0c67e"/><stop offset="1" stopColor="#b97744"/></linearGradient></defs>
  <path d="M40 2l5.3 8.5L55 5.7l2 10.7L68 14l-3.3 10.7L75 30l-7 8 8.5 8-11 3 3 11-11.6-1.2-2.1 11.5L44.7 65 40 77l-5.6-11.3-10 4.6-2.6-11.2-11.1 1.3L14 49.4 3 46l9-8-7-8 10.5-5.3L12 14l11.5 2 2-10.3 9.4 4.8L40 2Z" fill={`url(#${sunId})`} opacity=".97"/>
  <circle cx="40" cy="39" r="28" fill="#173c2f" stroke="#fff0c6" strokeWidth="2"/>
  <path d="M18 34L21 20l9 3 9-10 9 10 10-3 4 14-8-5-7 8-8-9-8 9-7-8-6 5Z" fill="#f3ca83" stroke="#f8e6c2" strokeWidth="1.5" strokeLinejoin="round"/>
  <path d="M28 23h7v7h-7zM43 23h7v7h-7z" fill="#aa5533"/><path d="M34 14h12l-6 7-6-7Z" fill="#ad5936"/>
  <path d="M24 36q0-6 7-7h18q7 1 7 7v16q-7 12-16 12T24 52V36Z" fill={`url(#${faceId})`}/>
  <path d="M28 42l8-2-1 5-7-1M52 42l-8-2 1 5 7-1Z" fill="#613c30"/>
  <path d="M40 44l-3 8h6l-3-8Z" fill="#8c4e32"/>
  <path d="M31 55h18l-5 4h-8l-5-4Z" fill="#7d422e"/>
  <path d="M25 48l-6 2 8 9 7 1-9-12ZM55 48l6 2-8 9-7 1 9-12Z" fill="#eed7a7"/>
  <path d="M17 66h46" stroke="#1a4836" strokeWidth="4" strokeLinecap="round"/>
  <path d="M25 71h30" stroke="#d79b58" strokeWidth="2.5" strokeLinecap="round"/>
 </svg>;
}
