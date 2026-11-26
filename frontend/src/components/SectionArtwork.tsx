import type {ReactNode} from 'react';

/**
 * Elementos gráficos propios del sistema, no capturas ni resultados.
 * SVG ligero y decorativo: acompaña el encabezado sin asumir información del backend.
 */
type Module='dashboard'|'pos'|'orders'|'kitchen'|'inventory'|'products'|'customers'|'reports'|'ai'|'users'|'settings';

const artwork:Record<Exclude<Module,'dashboard'>,ReactNode>={
 pos:<><path d="M24 84Q45 24 110 24Q129 25 151 35L136 157Q73 143 24 84Z" fill="#f4d79c" stroke="#bb7544" strokeWidth="8"/><path d="M37 86Q65 41 113 39L126 139Q71 124 37 86Z" fill="#ec954a"/><path d="M44 85L129 138M113 40L129 138" stroke="#fff0b0" strokeWidth="4"/><circle cx="78" cy="73" r="13" fill="#b53e35"/><circle cx="101" cy="104" r="13" fill="#b53e35"/><circle cx="63" cy="104" r="10" fill="#b53e35"/><path d="M92 70Q77 51 70 64Q74 81 92 70" fill="#2f7049"/></>,
 orders:<><rect x="35" y="18" width="113" height="145" rx="18" fill="#f7eee1" stroke="#bd996a" strokeWidth="6"/><path d="M68 41H114M64 70H118M64 97H116M64 126H101" stroke="#91b5a0" strokeWidth="8" strokeLinecap="round"/><circle cx="50" cy="42" r="5" fill="#cf8d54"/><circle cx="50" cy="70" r="5" fill="#cf8d54"/><circle cx="50" cy="97" r="5" fill="#cf8d54"/><path d="M124 133l12 12 24-28" fill="none" stroke="#3a8560" strokeWidth="10" strokeLinecap="round" strokeLinejoin="round"/></>,
 kitchen:<><path d="M39 110Q12 80 42 53Q51 31 79 33Q93 8 120 32Q155 25 162 57Q180 79 153 108V137H39Z" fill="#f7e7cf" stroke="#b58b59" strokeWidth="7"/><path d="M39 112H153M64 88V68M93 86V55M124 89V69" stroke="#d0a678" strokeWidth="6" strokeLinecap="round"/><rect x="44" y="135" width="105" height="16" rx="8" fill="#d8ae79"/><path d="M25 163H167" stroke="#6d9b77" strokeWidth="8" strokeLinecap="round"/></>,
 inventory:<><path d="M22 58l69-37 75 38-74 39Z" fill="#e8d0a4" stroke="#8b845b" strokeWidth="5"/><path d="M22 58v84l70 36V98Z" fill="#dfad71" stroke="#8b845b" strokeWidth="5"/><path d="M166 59v84l-74 35V98Z" fill="#c78d5f" stroke="#8b845b" strokeWidth="5"/><path d="M57 40l74 41v31" stroke="#fff3d2" strokeWidth="10"/><path d="M111 124h35M111 139h25" stroke="#fff4dc" strokeWidth="6" strokeLinecap="round"/></>,
 products:<><path d="M20 110l71-84 71 84-71 57Z" fill="#f6e4c7" stroke="#a68a68" strokeWidth="6"/><circle cx="93" cy="100" r="48" fill="#efbe65" stroke="#b76b35" strokeWidth="7"/><circle cx="93" cy="100" r="38" fill="#d4573c"/><circle cx="81" cy="85" r="10" fill="#ffe1a6"/><circle cx="112" cy="111" r="10" fill="#ffe1a6"/><circle cx="83" cy="125" r="9" fill="#ffe1a6"/><path d="M111 78Q97 64 91 79Q95 94 111 78" fill="#508055"/></>,
 customers:<><circle cx="94" cy="62" r="33" fill="#e4c39c"/><path d="M34 156Q35 105 93 105Q151 105 154 156Z" fill="#82a791"/><circle cx="143" cy="75" r="22" fill="#dfba92"/><path d="M152 110q27 11 27 45h-20" fill="#b2cdbc"/><path d="M66 65q12-24 40-12" fill="none" stroke="#795d48" strokeWidth="10" strokeLinecap="round"/></>,
 reports:<><rect x="27" y="35" width="136" height="132" rx="16" fill="#f2e8db" stroke="#c7b595" strokeWidth="6"/><path d="M46 147V112H62V147ZM79 147V83H95V147ZM111 147V95H127V147ZM142 147V58H156V147Z" fill="#6d9f82"/><path d="M47 76l34-26 34 13 31-22" stroke="#c18a52" strokeWidth="6" fill="none" strokeLinecap="round"/><circle cx="146" cy="41" r="6" fill="#c18a52"/></>,
 ai:<><path d="M92 15l23 52 52 25-52 22-23 53-23-53-52-22 52-25Z" fill="#e6cb83" stroke="#b88d43" strokeWidth="5"/><circle cx="92" cy="92" r="26" fill="#f9ebc5"/><path d="M80 93l10 10 18-21" fill="none" stroke="#4d8a67" strokeWidth="8" strokeLinecap="round"/><circle cx="150" cy="40" r="9" fill="#94b3a5"/><circle cx="33" cy="147" r="8" fill="#c79362"/></>,
 users:<><path d="M35 145V132q0-34 37-46l23 18 24-18q37 11 37 46v13Z" fill="#93b19e"/><circle cx="95" cy="51" r="35" fill="#e8c69e"/><path d="M62 51Q61 16 91 15q45-3 41 39Q102 42 84 29Q77 50 62 51Z" fill="#806245"/><path d="M35 156h122" stroke="#d0ad79" strokeWidth="8" strokeLinecap="round"/></>,
 settings:<><circle cx="95" cy="95" r="65" fill="#e3d4b7" stroke="#b99b66" strokeWidth="5"/><path d="M95 41v17M95 130v18M41 95h17M130 95h18M58 58l12 12M121 121l12 12M132 58l-12 12M70 120l-12 12" stroke="#9c8159" strokeWidth="10" strokeLinecap="round"/><circle cx="95" cy="95" r="34" fill="#f6e8ca"/><circle cx="95" cy="95" r="15" fill="#57816c"/></>,
};
export function SectionArtwork({view}:{view:Module}){
 if(view==='dashboard')return null;
 return <div className="section-artwork" aria-hidden="true">
   <span className="artwork-orbit artwork-orbit-one"/><span className="artwork-orbit artwork-orbit-two"/>
   <svg viewBox="0 0 190 190" width="190" height="190" fill="none" focusable="false">{artwork[view]}</svg>
   <span className="artwork-spark artwork-spark-one"/><span className="artwork-spark artwork-spark-two"/>
  </div>;
}
