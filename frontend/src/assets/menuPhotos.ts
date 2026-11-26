/**
 * Fotografías de referencia para las fichas de productos del entorno piloto.
 * Origen: Unsplash (licencia https://unsplash.com/license).
 * No son imágenes verificadas de las recetas de la pizzería.
 * El negocio debe aprobar fotografías propias por SKU antes del go-live.
 */
import type {Product} from '../types/domain';

const cdn = (id:string,width=960) => `https://images.unsplash.com/${id}?auto=format&fit=crop&w=${width}&q=82`;
const PHOTO_IDS:Record<string,string>={
 'PIZ-INK':'photo-1692737580547-b45bb4a02356',
 'PIZ-AND':'photo-1574071318508-1cdbab80d002',
 'PIZ-SUP':'photo-1565299624946-b28f40a0ae38',
 'PIZ-VEG':'photo-1513104890138-7c749659a591',
};
export const HERO_PHOTO=cdn('photo-1574071318508-1cdbab80d002',1600);
export const productImage=(product:Pick<Product,'sku'>)=>{
 const id=PHOTO_IDS[product.sku.trim().toUpperCase()];
 return id?cdn(id):null;
};
