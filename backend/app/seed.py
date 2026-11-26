"""Carga inicial EXCLUSIVA de demostración. Exige credenciales suministradas por entorno."""
import os
from sqlalchemy import select
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.domain.auth import hash_password
from app.domain.models import User, Product, Ingredient, RecipeLine

PIZZAS=[('PIZ-INK','Pizza Inka',3500),('PIZ-AND','Pizza Andina',3200),('PIZ-SUP','Pizza Suprema',4200),('PIZ-VEG','Pizza Vegetariana',3000)]
INGREDIENTS=[('HAR','Harina','g',24000,6000),('MOZ','Queso mozzarella','g',13000,3000),('TOM','Salsa de tomate','g',11000,2500),('POL','Pollo','g',7000,1400),('CEC','Cecina','g',6500,1200),('VER','Verduras variadas','g',9000,1600)]
RECIPES={'PIZ-INK':{'HAR':250,'MOZ':180,'TOM':100,'CEC':100}, 'PIZ-AND':{'HAR':250,'MOZ':160,'TOM':100,'POL':110}, 'PIZ-SUP':{'HAR':280,'MOZ':200,'TOM':120,'CEC':130,'POL':90}, 'PIZ-VEG':{'HAR':240,'MOZ':140,'TOM':100,'VER':210}}

def seed_demo() -> None:
    if get_settings().app_env == 'production': raise RuntimeError('La semilla demo está prohibida en producción')
    password = os.getenv('SEED_ADMIN_PASSWORD','')
    if len(password)<12:raise RuntimeError('Definir SEED_ADMIN_PASSWORD con mínimo 12 caracteres; no hay contraseña predeterminada')
    with SessionLocal() as db:
        for username,role,name in [('admin','admin','Administrador Demo'),('cajero','cashier','Caja Demo'),('cocina','kitchen','Cocina Demo')]:
            if db.scalar(select(User).where(User.username==username)) is None:
                db.add(User(username=username,role=role,full_name=name,password_hash=hash_password(password)))
        for sku,name,unit,stock,minimum_stock in INGREDIENTS:
            if db.scalar(select(Ingredient).where(Ingredient.sku==sku)) is None:
                db.add(Ingredient(sku=sku,name=name,unit=unit,stock=stock,minimum_stock=minimum_stock))
        for sku,name,price in PIZZAS:
            if db.scalar(select(Product).where(Product.sku==sku)) is None:
                db.add(Product(sku=sku,name=name,price_cents=price,category='Pizzas'))
        db.flush()
        ing={i.sku:i for i in db.scalars(select(Ingredient))}
        products={p.sku:p for p in db.scalars(select(Product))}
        for sku,recipe in RECIPES.items():
            p=products[sku]
            if not db.scalar(select(RecipeLine.id).where(RecipeLine.product_id==p.id)):
                for key,amount in recipe.items():db.add(RecipeLine(product_id=p.id,ingredient_id=ing[key].id,amount=amount))
        db.commit()
    print('Datos ficticios generados. Cambiar credenciales antes de compartir el entorno.')

if __name__=='__main__':seed_demo()