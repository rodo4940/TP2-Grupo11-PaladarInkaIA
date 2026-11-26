"""Herramienta CLI de aprovisionamiento inicial, sin credenciales incrustadas.

Ejecutar solo tras aplicar migraciones. La contraseña se solicita de forma
interactiva para que no aparezca en el historial ni en la lista de procesos.
"""
from __future__ import annotations
import argparse
from getpass import getpass
from sqlalchemy import select
from app.db.session import SessionLocal
from app.domain.auth import hash_password
from app.domain.models import User


def create_admin(username: str, full_name: str, password: str) -> int:
    """Crea el primer administrador; falla si ya existe cualquier usuario."""
    username=username.strip().lower()
    if len(username)<3 or not username[0].isalpha() or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_.-' for c in username):
        raise ValueError('Nombre de cuenta inválido')
    if len(full_name.strip())<3 or len(full_name)>160:
        raise ValueError('Nombre completo inválido')
    if len(password)<12 or len(password)>128:
        raise ValueError('La contraseña debe contener de 12 a 128 caracteres')
    with SessionLocal() as db:
        if db.scalar(select(User.id).limit(1)) is not None:
            raise RuntimeError('Ya existen usuarios; usar el módulo de administración para nuevas cuentas')
        db.add(User(username=username,full_name=full_name.strip(),role='admin',password_hash=hash_password(password)))
        db.commit()
    return 0


def main() -> int:
    parser=argparse.ArgumentParser(description='Paladar Inka AI — gestión segura')
    sub=parser.add_subparsers(dest='command',required=True)
    add=sub.add_parser('create-admin',help='Crear el primer administrador (solo una vez)')
    add.add_argument('--username',default='admin',help='Usuario administrador inicial')
    add.add_argument('--name',required=True,help='Nombre completo de la persona responsable')
    args=parser.parse_args()
    if args.command=='create-admin':
        one=getpass('Contraseña segura del administrador: ')
        two=getpass('Repetir contraseña: ')
        if one!=two:raise ValueError('Las contraseñas no coinciden')
        create_admin(args.username,args.name,one)
        print('Cuenta administrativa creada; resguardar credenciales y controlar acceso.')
        return 0
    return 2

if __name__=='__main__':raise SystemExit(main())