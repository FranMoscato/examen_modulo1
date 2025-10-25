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

app = FastAPI()

payments={'1':Payment(REGISTRADO(),1,1000,"PayPal")}


@app.get("/payments")
async def prueba_root():
    pagos={}
    for id in payments.keys():
        pay=payments[id]
        key_dicc={'id':pay.payment_id, 'amount': pay.amount, 'payment_method': pay.payment_method, 'status': pay.status }
        pagos[f'{id}']=key_dicc
    return pagos

