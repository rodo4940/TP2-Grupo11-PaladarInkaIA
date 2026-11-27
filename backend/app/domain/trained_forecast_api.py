"""Endpoints de demostración del entrenamiento reproducible sin datos personales."""
from fastapi import APIRouter, Depends, Query
from app.domain.auth import require_roles
from app.domain.models import User
from app.domain.trained_forecast import trained_demo,demo_predictions

router=APIRouter()
cashier=require_roles('admin','cashier')


@router.get('/ai/trained-demo/metrics')
def metrics(user:User=Depends(cashier))->dict:
    return trained_demo()


@router.get('/ai/trained-demo/forecast')
def forecast(days:int=Query(7,ge=1,le=14),user:User=Depends(cashier))->dict:
    return demo_predictions(days)
