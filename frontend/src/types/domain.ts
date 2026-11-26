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