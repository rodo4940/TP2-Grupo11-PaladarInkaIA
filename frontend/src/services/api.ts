/** Cliente REST tipado. Los datos provienen únicamente de FastAPI. */
const API_URL = (import.meta.env.VITE_API_URL ?? '').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(public status: number, message: string) {super(message);this.name='ApiError';}
}
export async function api<T>(path: string, token?: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body !== undefined) headers.set('Content-Type','application/json');
  if (token) headers.set('Authorization',`Bearer ${token}`);
  let response: Response;
  try { response = await fetch(`${API_URL}/api/v1${path}`,{...init,headers}); }
  catch {throw new ApiError(0,'No se pudo conectar al servidor. Revisa el backend y tu red.');}
  if (!response.ok) {
    let detail = `Error HTTP ${response.status}`;
    try {const data = await response.json() as {detail?: string | {msg?: string} | Array<{msg:string}>};
      detail = Array.isArray(data.detail) ? data.detail.map(x=>x.msg).join(' · ') : typeof data.detail === 'string' ? data.detail : detail;
    }catch { /* no-json */ }
    throw new ApiError(response.status,detail);
  }
  return response.json() as Promise<T>;
}
export const post = <T>(path:string, data:unknown, token:string)=>api<T>(path, token, {method:'POST',body:JSON.stringify(data)});
export const patch = <T>(path:string, data:unknown, token:string)=>api<T>(path, token, {method:'PATCH',body:JSON.stringify(data)});
export const put = <T>(path:string, data:unknown, token:string)=>api<T>(path, token, {method:'PUT',body:JSON.stringify(data)});