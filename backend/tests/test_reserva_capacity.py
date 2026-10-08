import unittest
from fastapi import HTTPException

from app.services.reserva_service import ReservaService


def test_rejects_capacity_above_availability_limit():
    with unittest.TestCase().assertRaises(HTTPException) as raised:
        ReservaService.validar_capacidad_maxima(capacidad=5, cantidad_personas=2)
    assert raised.exception.status_code == 400


def test_accepts_capacity_at_availability_limit():
    ReservaService.validar_capacidad_maxima(capacidad=4, cantidad_personas=2)
