export type Role = 'admin'|'cashier'|'kitchen';
export interface User {id:number;username:string;full_name:string;role:Role;active?:boolean}
export interface AuthResponse {access_token:string;token_type:string;user:User}
export interface Product {id:number;sku:string;name:string;category:string;price_cents:number;active:boolean}
export interface Ingredient {id:number;sku:string;name:string;unit:string;stock:number;minimum_stock:number}
export interface Customer {id:number;name:string;phone:string|null;notes:string|null}
export interface OrderItem {id:number;product_id:number;product_name:string;quantity:number;unit_price_cents:number}
export type OrderStatus = 'pending'|'preparing'|'ready'|'delivered'|'cancelled';
export interface Order {id:number;status:OrderStatus;customer_id:number|null;table_label:string;total_cents:number;notes:string;created_at:string;items:OrderItem[];paid:boolean}
export interface StockMovement {id:number;ingredient_id:number;delta:number;balance:number;reference:string;actor_id:number;created_at:string}
export interface Dashboard {sales_cents:number;orders_total:number;orders_active:number;orders_delivered:number;customers_total:number;low_stock:Array<{id:number;name:string;stock:number;minimum_stock:number;unit:string}>}
export interface Report {paid_orders:number;sales_cents:number;by_method:Record<string,number>;top_products:Array<{name:string;quantity:number}>}
export interface Recommendation {method:string;items:Array<{product_id:number;name:string;price_cents:number;orders_count:number;reason:string}>}
export interface Forecast {method:string;type:string;sample_paid_orders_7d:number;limitations:string;items:Array<{product_id:number;name:string;units_by_day:number[];suggested_units_next_day:number;indicative_range:[number,number]}>}
export interface Audit {id:number;actor_id:number;action:string;entity:string;entity_id:number;detail:string;created_at:string}
export interface SystemInfo {app:string;version:string;environment:string;database:string;modules:string[]}

export interface CustomerInsights {customer_id:number;orders_total:number;orders_paid:number;spent_cents:number;reference_points:number;top_products:Array<{name:string;quantity:number}>;history:Array<{id:number;created_at:string;status:OrderStatus;paid:boolean;total_cents:number}>;points_disclaimer:string}
export interface InternalReceipt {type:'TICKET_INTERNO_NO_TRIBUTARIO';order_id:number;issued_at:string;business_label:string;table_label:string;status:string;items:Array<{name:string;quantity:number;unit_price_cents:number;subtotal_cents:number}>;total_cents:number;method:string;disclaimer:string}
/** Comprobantes administrativos basados en Payment; nunca documentos CPE SUNAT. */
export interface BillingDocument {
 id:number;document_number:string;document_type:'TICKET_INTERNO_NO_TRIBUTARIO';
 fiscal_status:'NO_EMITIDO_SUNAT';order_id:number;issued_at:string;
 refund_status:'pending'|'confirmed'|null;net_cents:number;
 method:string;total_cents:number;customer_name:string;table_label:string;
 order_status:OrderStatus;items:Array<{name:string;quantity:number;unit_price_cents:number;subtotal_cents:number}>;
 disclaimer:string;
}
export interface BillingLedger {
 entries:BillingDocument[];count:number;total_cents:number;currency:'PEN';
 confirmed_refunds_cents:number;net_registered_cents:number;
 fiscal_status:'NO_EMITIDO_SUNAT';disclaimer:string;
}
export interface BusinessSnapshot {
 today_sales_cents:number;previous_day_sales_cents:number;sample_paid_orders:number;
 active_orders:number;pending_kitchen:number;preparing_kitchen:number;ready_delivery:number;
 products_active:number;low_stock:Array<{name:string;stock:number;unit:string;minimum_stock:number}>;
 top_products:Array<{name:string;units:number}>;date_lima:string;
}
export interface BusinessContext {mode:string;snapshot:BusinessSnapshot;disclaimer:string}
export interface AssistantAnswer {
 answer:string;mode:'modelo_externo_configurado'|'reglas_explicables_locales';
 basis:string[];snapshot_date:string;sample_paid_orders:number;warning:string;
}

export interface DailyCashSummary {
 date:string;timezone:'America/Lima';currency:'PEN';
 payments_count:number;gross_payments_cents:number;
 by_method:Record<'cash'|'card'|'yape'|'plin',{count:number;amount_cents:number}>;
 entries:BillingDocument[];
 reconciliation_state:'PENDIENTE_VERIFICACION_MANUAL';
 reconciliation_note:string;fiscal_status:'NO_EMITIDO_SUNAT';
 confirmed_refunds_cents:number;net_cash_flow_cents:number;refunds_count:number;
 refunds_by_method:Record<'cash'|'card'|'yape'|'plin',number>;
 internal_closeout_state:'submitted'|'approved'|'finalized'|null;
}

/** La confirmación de devolución es HUMANA; la API no mueve dinero. */
export interface InternalRefund {
 id:number;payment_id:number;order_id:number;method:string;amount_cents:number;
 reason:string;status:'pending'|'confirmed';requested_by:number;confirmed_by:number|null;
 external_reference:string|null;created_at:string;confirmed_at:string|null;disclaimer:string;
}
export interface RegisteredCashCloseout {
 id:number;day:string;state:'submitted'|'approved'|'finalized';opening_cash_cents:number;
 expected_cash_cents:number;counted_cash_cents:number;variance_cents:number;
 gross_payments_cents:number;confirmed_refunds_cents:number;payments_count:number;
 refunds_count:number;submitted_by:number;approved_by:number|null;note:string;
 approval_note:string;created_at:string;approved_at:string|null;stale:boolean;disclaimer:string;
 finalized_at:string|null;finalized_by:number|null;snapshot_sha256:string|null;
}

/** DEMO: no es CPE tributario ni CDR emitido por SUNAT. */
export interface FiscalDemoDocument {
 id:number;payment_id:number;document_type:'01'|'03'|'07';
 document_label:string;number:string;issue_date:string;currency:'PEN';
 total_cents:number;net_cents:number;tax_cents:number;affectation_code:string;
 customer_document_type:string;customer_document_number:string;customer_name:string;
 reference_document_id:number|null;status:'SIMULADO_VALIDADO_LOCALMENTE';
 sha256:string;issuer_ruc:string;digital_signature:false;sunat_submitted:false;
 official_cdr:false;warning:string;xml_demo?:string;
}
