
from datetime import date
from decimal import Decimal
import requests

API_URL = "https://cupiu.ro/api/rates/"


def curs_eur_ron(data_factura: date):
    if data_factura > date.today():
        raise ValueError(
            "Data facturii nu poate fi in viitor."
        )

    raspuns = requests.get(
        API_URL,
        params={
            "date": data_factura.isoformat(),
            "currency": "EUR"
        },
        timeout=15
    )

    raspuns.raise_for_status()
    date_api = raspuns.json()

    cursuri = date_api.get("rates", [])

    for element in cursuri:
        if element.get("currency") == "EUR":
            curs = Decimal(str(element["rate"]))
            multiplicator = Decimal(
                str(element.get("multiplier", 1))
            )

            return {
                "data_curs": date_api["date"],
                "curs": str(curs / multiplicator),
                "sursa": "BNR prin cupiu.ro"
            }

    raise ValueError(
        "Nu exista curs EUR disponibil pentru data ceruta."
    )
