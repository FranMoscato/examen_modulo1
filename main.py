from fastapi import FastAPI,Form,UploadFile, File
from typing import Annotated
import os
import shutil
import json
from models import (    Payment,
    REGISTRADO,
    FALLIDO,
    PAGADO)
from strategies.validation_strategy import get_validation_strategy

STATUS_REGISTRADO = "REGISTRADO"
STATUS_PAGADO = "PAGADO"
STATUS_FALLIDO = "FALLIDO"

DATA_PATH = "data.json"
STATUS = "status"
AMOUNT = "amount"
PAYMENT_METHOD = "payment_method"

app = FastAPI()

def load_all_payments():
    with open(DATA_PATH, "r") as f:
        data = json.load(f)
    return data


def save_all_payments(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=4)


def load_payment(payment_id):
    data = load_all_payments()[payment_id]
    return data


def save_payment_data(payment_id, data):
    all_data = load_all_payments()
    all_data[str(payment_id)] = data
    save_all_payments(all_data)


def save_payment(payment_id, amount, payment_method, status):
    data = {
        AMOUNT: amount,
        PAYMENT_METHOD: payment_method,
        STATUS: status,
    }
    save_payment_data(payment_id, data)

def to_status_class(status):
    if status==STATUS_REGISTRADO:
        return REGISTRADO()
    elif status==STATUS_FALLIDO:
        return FALLIDO()
    else:
        return PAGADO()


@app.get("/payments")
async def prueba_root():
    return load_all_payments()

@app.post("/payments/{payment_id}")
async def Registra (payment_id: str, amount : float, payment_method : str):

    data=load_all_payments()
    if payment_id not in data.keys():
        save_payment(payment_id,amount,payment_method,STATUS_REGISTRADO)
        return { "Exito" : "El pago se ha registrado"}
    else:
        return { "Error" : "ID no valido"}
    

@app.post("/payments/{payment_id}/pay")
async def Pay (payment_id: str):
    
    data=load_all_payments()
    if payment_id not in data.keys():
        return { "Error" : "ID no valido"}
    else:
        ST=data[payment_id]['status']
        if ST != STATUS_REGISTRADO:
            return {"Error" : f"El pago se encuentra en estado {ST}"}
        else:
            ST_CLASS=to_status_class(ST)
            
            pago=Payment(ST_CLASS,payment_id,data[payment_id]["amount"],data[payment_id]["payment_method"])
            
            val_strategy=get_validation_strategy(pago.payment_method)

            if val_strategy.validate(payment_id,pago.amount,data):
                msg=pago.pago_exitoso()
                save_payment(pago.payment_id,pago.amount,pago.payment_method,pago.status)
                return {"Exito" : msg}
            else:
                msg=pago.pago_fallido()
                save_payment(pago.payment_id,pago.amount,pago.payment_method,pago.status)
                return {"Error" : msg}


