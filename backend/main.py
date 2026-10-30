
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlite3 import IntegrityError
from .curs_valutar import curs_eur_ron
from .database import get_connection, init_db
import requests
from .securitate import verifica_parola
import os
import jwt
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
load_dotenv()
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .autorizare import permite_roluri
from fastapi.middleware.cors import CORSMiddleware
from backend.emailuri import trimite_email

JWT_SECRET = os.getenv("JWT_SECRET")

if not JWT_SECRET:
    raise RuntimeError("Lipseste JWT_SECRET din fisierul .env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Flux de aprovizionare",
    description="Aplicatie pentru achizitii, depozit si contabilitate",
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["null"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class FurnizorNou(BaseModel):
    nume: str = Field(min_length=1)
    cui: str | None = None
    email: str | None = None


@app.get("/")
def pagina_principala():
    return {
        "mesaj": "Bine ai venit in aplicatia Flux de aprovizionare!",
        "departamente": ["Achizitii", "Depozit", "Contabilitate"]
    }


@app.post(
    "/furnizori",
    status_code=201,
    dependencies=[Depends(permite_roluri("achizitii"))]
)
def adauga_furnizor(furnizor: FurnizorNou):
    try:
        with get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO furnizori (nume, cui, email)
                VALUES (?, ?, ?)
                """,
                (furnizor.nume, furnizor.cui, furnizor.email)
            )
            furnizor_id = cursor.lastrowid
            
            conn.execute(
                """
                INSERT INTO jurnal_activitate
                (utilizator_id, actiune, tip_obiect, obiect_id, detalii)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    None,
                    "creare",
                    "furnizor",
                    furnizor_id,
                    f"Furnizor adaugat: {furnizor.nume}"
                )
            )

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Exista deja un furnizor cu acest CUI."
        )

    return {
        "id": furnizor_id,
        "mesaj": "Furnizor adaugat cu succes!"
    }


@app.get("/furnizori")
def lista_furnizori():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, nume, cui, email FROM furnizori ORDER BY id DESC"
        ).fetchall()

    return [dict(row) for row in rows]

from datetime import date


class ProdusNou(BaseModel):
    denumire: str = Field(min_length=1)
    unitate_masura: str = "buc"


class PozitieComandaNoua(BaseModel):
    produs_id: int
    cantitate: float = Field(gt=0)
    pret_unitar: float = Field(ge=0)


class ComandaNoua(BaseModel):
    furnizor_id: int
    data_comanda: date
    data_livrare: date
    produse: list[PozitieComandaNoua] = Field(min_length=1)


@app.post("/produse", status_code=201)
def adauga_produs(produs: ProdusNou):
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO produse (denumire, unitate_masura)
            VALUES (?, ?)
            """,
            (produs.denumire, produs.unitate_masura)
        )
        produs_id = cursor.lastrowid

    return {"id": produs_id, "mesaj": "Produs adaugat!"}


@app.get("/produse")
def lista_produse():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM produse ORDER BY id DESC"
        ).fetchall()

    return [dict(row) for row in rows]



@app.post("/comenzi", status_code=201)
def adauga_comanda(comanda: ComandaNoua):
    if comanda.data_livrare < comanda.data_comanda:
        raise HTTPException(
            status_code=422,
            detail="Livrarea nu poate fi inaintea comenzii."
        )

    with get_connection() as conn:
        furnizor = conn.execute(
            "SELECT id FROM furnizori WHERE id = ?",
            (comanda.furnizor_id,)
        ).fetchone()

        if not furnizor:
            raise HTTPException(
                status_code=404,
                detail="Furnizorul nu exista."
            )

        for pozitie in comanda.produse:
            produs = conn.execute(
                "SELECT id FROM produse WHERE id = ?",
                (pozitie.produs_id,)
            ).fetchone()

            if not produs:
                raise HTTPException(
                    status_code=404,
                    detail=f"Produsul {pozitie.produs_id} nu exista."
                )

        cursor = conn.execute(
            """
            INSERT INTO comenzi
            (furnizor_id, data_comanda, data_livrare)
            VALUES (?, ?, ?)
            """,
            (
                comanda.furnizor_id,
                comanda.data_comanda.isoformat(),
                comanda.data_livrare.isoformat()
            )
        )

        comanda_id = cursor.lastrowid

        for pozitie in comanda.produse:
            conn.execute(
                """
                INSERT INTO pozitii_comanda
                (comanda_id, produs_id, cantitate, pret_unitar)
                VALUES (?, ?, ?, ?)
                """,
                (
                    comanda_id,
                    pozitie.produs_id,
                    pozitie.cantitate,
                    pozitie.pret_unitar
                )
            )
            
        conn.execute(
            """
            INSERT INTO jurnal_activitate
            (utilizator_id, actiune, tip_obiect, obiect_id, detalii)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                None,
                "creare",
                "comanda",
                comanda_id,
                f"Comanda noua pentru furnizorul {comanda.furnizor_id}"
            )
        )


    return {
        "id": comanda_id,
        "mesaj": "Comanda a fost inregistrata cu succes!"
    }


@app.get("/comenzi")
def lista_comenzi():
    with get_connection() as conn:
        comenzi = conn.execute(
            """
            SELECT c.*, f.nume AS furnizor
            FROM comenzi c
            JOIN furnizori f ON f.id = c.furnizor_id
            ORDER BY c.id DESC
            """
        ).fetchall()

        rezultat = []

        for comanda in comenzi:
            date_comanda = dict(comanda)

            pozitii = conn.execute(
                """
                SELECT pc.*, p.denumire
                FROM pozitii_comanda pc
                JOIN produse p ON p.id = pc.produs_id
                WHERE pc.comanda_id = ?
                """,
                (comanda["id"],)
            ).fetchall()

            date_comanda["produse"] = [
                dict(pozitie) for pozitie in pozitii
            ]
            rezultat.append(date_comanda)

    return rezultat

class PozitieReceptieNoua(BaseModel):
    produs_id: int
    cantitate: float = Field(gt=0)


class ReceptieNoua(BaseModel):
    comanda_id: int
    data_receptie: date
    produse: list[PozitieReceptieNoua] = Field(min_length=1)


@app.post("/receptii", status_code=201)
def adauga_receptie(receptie: ReceptieNoua, utilizator = Depends(permite_roluri("depozit"))):
    with get_connection() as conn:
        comanda = conn.execute(
            "SELECT id FROM comenzi WHERE id = ?",
            (receptie.comanda_id,)
        ).fetchone()

        if not comanda:
            raise HTTPException(
                status_code=404,
                detail="Comanda nu exista."
            )

        comandate = conn.execute(
            """
            SELECT produs_id, SUM(cantitate) AS cantitate
            FROM pozitii_comanda
            WHERE comanda_id = ?
            GROUP BY produs_id
            """,
            (receptie.comanda_id,)
        ).fetchall()

        cantitati_comandate = {
            row["produs_id"]: row["cantitate"]
            for row in comandate
        }

        primite = conn.execute(
            """
            SELECT pr.produs_id,
                   SUM(pr.cantitate) AS cantitate
            FROM pozitii_receptie pr
            JOIN receptii r ON r.id = pr.receptie_id
            WHERE r.comanda_id = ?
            GROUP BY pr.produs_id
            """,
            (receptie.comanda_id,)
        ).fetchall()

        cantitati_primite = {
            row["produs_id"]: row["cantitate"]
            for row in primite
        }

        cantitati_noi = {}

        for produs in receptie.produse:
            cantitati_noi[produs.produs_id] = (
                cantitati_noi.get(produs.produs_id, 0)
                + produs.cantitate
            )

        for produs_id, cantitate in cantitati_noi.items():
            if produs_id not in cantitati_comandate:
                raise HTTPException(
                    status_code=422,
                    detail=f"Produsul {produs_id} nu este in comanda."
                )

            total = cantitati_primite.get(produs_id, 0) + cantitate

            if total > cantitati_comandate[produs_id]:
                raise HTTPException(
                    status_code=422,
                    detail=f"Cantitate prea mare pentru produsul {produs_id}."
                )

        cursor = conn.execute(
            """
            INSERT INTO receptii (comanda_id, data_receptie)
            VALUES (?, ?)
            """,
            (receptie.comanda_id, receptie.data_receptie.isoformat())
        )

        receptie_id = cursor.lastrowid

        for produs_id, cantitate in cantitati_noi.items():
            conn.execute(
                """
                INSERT INTO pozitii_receptie
                (receptie_id, produs_id, cantitate)
                VALUES (?, ?, ?)
                """,
                (receptie_id, produs_id, cantitate)
            )
         
        conn.execute(
            """
            INSERT INTO jurnal_activitate
            (utilizator_id, actiune, tip_obiect, obiect_id, detalii)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                None,
                "creare",
                "receptie",
                receptie_id,
                f"Receptie pentru comanda {receptie.comanda_id}"
            )
        )
  

    return {
        "id": receptie_id,
        "mesaj": "Receptia a fost inregistrata cu succes!"
    }


@app.get("/comenzi/{comanda_id}/situatie")
def situatie_comanda(comanda_id: int):
    with get_connection() as conn:
        comanda = conn.execute(
            "SELECT id FROM comenzi WHERE id = ?",
            (comanda_id,)
        ).fetchone()

        if not comanda:
            raise HTTPException(
                status_code=404,
                detail="Comanda nu exista."
            )

        rows = conn.execute(
            """
            SELECT
                p.id AS produs_id,
                p.denumire,
                pc.cantitate AS comandat,
                COALESCE((
                    SELECT SUM(pr.cantitate)
                    FROM pozitii_receptie pr
                    JOIN receptii r ON r.id = pr.receptie_id
                    WHERE r.comanda_id = pc.comanda_id
                      AND pr.produs_id = pc.produs_id
                ), 0) AS primit
            FROM pozitii_comanda pc
            JOIN produse p ON p.id = pc.produs_id
            WHERE pc.comanda_id = ?
            """,
            (comanda_id,)
        ).fetchall()

    produse = []

    for row in rows:
        produs = dict(row)
        produs["restant"] = produs["comandat"] - produs["primit"]
        produse.append(produs)

    return {
        "comanda_id": comanda_id,
        "produse": produse
    }

from decimal import Decimal, ROUND_HALF_UP


class FacturaNoua(BaseModel):
    comanda_id: int
    numar: str = Field(min_length=1)
    data_factura: date
    moneda: str
    valoare: float = Field(ge=0)


@app.post("/facturi", status_code=201)
def adauga_factura(factura: FacturaNoua):
    moneda = factura.moneda.upper()

    if moneda not in ("RON", "EUR"):
        raise HTTPException(
            status_code=422,
            detail="Moneda trebuie sa fie RON sau EUR."
        )

    with get_connection() as conn:
        comanda = conn.execute(
            "SELECT id FROM comenzi WHERE id = ?",
            (factura.comanda_id,)
        ).fetchone()

        if not comanda:
            raise HTTPException(
                status_code=404,
                detail="Comanda nu exista."
            )

        cursor = conn.execute(
            """
            INSERT INTO facturi
            (comanda_id, numar, data_factura,
             moneda, valoare, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                factura.comanda_id,
                factura.numar,
                factura.data_factura.isoformat(),
                moneda,
                factura.valoare,
                "in_verificare"
            )
        )

        factura_id = cursor.lastrowid
        
        conn.execute(
            """
            INSERT INTO jurnal_activitate
            (utilizator_id, actiune, tip_obiect, obiect_id, detalii)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                None,
                "creare",
                "factura",
                factura_id,
                f"Factura {factura.numar} pentru comanda {factura.comanda_id}"
            )
        )


    return {
        "id": factura_id,
        "mesaj": "Factura a fost inregistrata!",
        "status": "in_verificare"
    }


@app.get("/facturi/{factura_id}/verificare")
def verifica_factura(factura_id: int):
    with get_connection() as conn:
        factura = conn.execute(
            "SELECT * FROM facturi WHERE id = ?",
            (factura_id,)
        ).fetchone()

        if not factura:
            raise HTTPException(
                status_code=404,
                detail="Factura nu exista."
            )

        comanda_id = factura["comanda_id"]

        pozitii = conn.execute(
            """
            SELECT pc.produs_id, pc.cantitate,
                   pc.pret_unitar,
                   COALESCE((
                       SELECT SUM(pr.cantitate)
                       FROM pozitii_receptie pr
                       JOIN receptii r
                         ON r.id = pr.receptie_id
                       WHERE r.comanda_id = pc.comanda_id
                         AND pr.produs_id = pc.produs_id
                   ), 0) AS primit
            FROM pozitii_comanda pc
            WHERE pc.comanda_id = ?
            """,
            (comanda_id,)
        ).fetchall()

        valoare_receptionata = sum(
            Decimal(str(p["primit"]))
            * Decimal(str(p["pret_unitar"]))
            for p in pozitii
        )

        valoare_factura = Decimal(str(factura["valoare"]))

        # In aceasta etapa verificam doar facturi in RON.
        
        curs_folosit = None
        data_curs = None

        if factura["moneda"] == "EUR":
            try:
                rezultat_curs = curs_eur_ron(
                    date.fromisoformat(factura["data_factura"])
                )
                curs_folosit = Decimal(rezultat_curs["curs"])
                data_curs = rezultat_curs["data_curs"]
                valoare_factura = valoare_factura * curs_folosit
            except (ValueError, requests.RequestException) as eroare:
                raise HTTPException(
                    status_code=503,
                    detail=f"Nu s-a putut obtine cursul valutar: {eroare}"
                )


        valoare_receptionata = valoare_receptionata.quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        diferenta = valoare_factura - valoare_receptionata

        if diferenta > Decimal("0.01"):
            status = "blocata"
            mesaj = "Factura depaseste valoarea marfii receptionate."
        else:
            status = "necesita_verificare"
            mesaj = "Valoarea este acoperita de receptii. Verificati factura."

        conn.execute(
            "UPDATE facturi SET status = ? WHERE id = ?",
            (status, factura_id)
        )

  
    return {
        "factura_id": factura_id,
        "valoare_factura_ron": float(valoare_factura),
        "valoare_receptionata_ron": float(valoare_receptionata),
        "diferenta_ron": float(diferenta),
        "status": status,
        "mesaj": mesaj,
        "curs_eur_ron": float(curs_folosit) if curs_folosit is not None else None,
        "data_curs": data_curs
    }

class DateAutentificare(BaseModel):
    username: str
    parola: str


@app.post("/login")
def autentificare(date_login: DateAutentificare):
    with get_connection() as conn:
        utilizator = conn.execute(
            """
            SELECT id, nume, username, parola_hash, rol, activ
            FROM utilizatori
            WHERE username = ?
            """,
            (date_login.username,)
        ).fetchone()

    if not utilizator or not utilizator["activ"]:
        raise HTTPException(
            status_code=401,
            detail="Username sau parola incorecta."
        )

    if not verifica_parola(
        date_login.parola,
        utilizator["parola_hash"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Username sau parola incorecta."
        )

   
    token = genereaza_token(utilizator["id"])

    return {
        "mesaj": "Autentificare reusita!",
        "access_token": token,
        "token_type": "bearer",
        "utilizator": {
            "id": utilizator["id"],
            "nume": utilizator["nume"],
            "username": utilizator["username"],
            "rol": utilizator["rol"]
        }
    }


def genereaza_token(utilizator_id: int):
    expirare = datetime.now(timezone.utc) + timedelta(hours=2)

    continut = {
        "sub": str(utilizator_id),
        "exp": expirare
    }

    return jwt.encode(
        continut,
        JWT_SECRET,
        algorithm="HS256"
    )

securitate_token = HTTPBearer()


def utilizator_curent(
    credentials: HTTPAuthorizationCredentials = Depends(securitate_token)
):
    try:
        continut = jwt.decode(
            credentials.credentials,
            JWT_SECRET,
            algorithms=["HS256"]
        )
        utilizator_id = int(continut["sub"])

    except (jwt.PyJWTError, ValueError, KeyError):
        raise HTTPException(
            status_code=401,
            detail="Token invalid sau expirat."
        )

    with get_connection() as conn:
        utilizator = conn.execute(
            """
            SELECT id, nume, username, rol, activ
            FROM utilizatori
            WHERE id = ?
            """,
            (utilizator_id,)
        ).fetchone()

    if not utilizator or not utilizator["activ"]:
        raise HTTPException(
            status_code=401,
            detail="Utilizator inexistent sau inactiv."
        )

    return dict(utilizator)


@app.get("/utilizatorul-meu")
def profil_utilizator(
    utilizator: dict = Depends(utilizator_curent)
):
    return {
        "mesaj": "Token valid!",
        "utilizator": utilizator
    }

def permite_roluri(*roluri_permise):
    def verifica_rol(
        utilizator: dict = Depends(utilizator_curent)
    ):
        if utilizator["rol"] not in roluri_permise:
            raise HTTPException(
                status_code=403,
                detail="Nu ai permisiunea pentru aceasta operatiune."
            )

        return utilizator

    return verifica_rol


@app.get("/jurnal")
def lista_jurnal(
    utilizator: dict = Depends(utilizator_curent)
):
    with get_connection() as conn:
        inregistrari = conn.execute(
            """
            SELECT
                j.id,
                j.data_ora,
                j.actiune,
                j.tip_obiect,
                j.obiect_id,
                j.detalii,
                COALESCE(u.nume, 'Neidentificat') AS utilizator
            FROM jurnal_activitate j
            LEFT JOIN utilizatori u
                ON u.id = j.utilizator_id
            ORDER BY j.id DESC
            LIMIT 100
            """
        ).fetchall()

    return [dict(inregistrare) for inregistrare in inregistrari]
    
class ProdusNecomandatNou(BaseModel):
    comanda_id: int | None = None
    produs_id: int
    cantitate: float = Field(gt=0)
    data_primire: date
    observatii: str | None = None


@app.post("/produse-necomandate", status_code=201)
def adauga_produs_necomandat(
    produs: ProdusNecomandatNou
):
    with get_connection() as conn:
        produs_existent = conn.execute(
            "SELECT id FROM produse WHERE id = ?",
            (produs.produs_id,)
        ).fetchone()

        if not produs_existent:
            raise HTTPException(
                status_code=404,
                detail="Produsul nu exista."
            )

        if produs.comanda_id is not None:
            comanda = conn.execute(
                "SELECT id FROM comenzi WHERE id = ?",
                (produs.comanda_id,)
            ).fetchone()

            if not comanda:
                raise HTTPException(
                    status_code=404,
                    detail="Comanda nu exista."
                )

        cursor = conn.execute(
            """
            INSERT INTO produse_necomandate
            (comanda_id, produs_id, cantitate,
             data_primire, status, observatii)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                produs.comanda_id,
                produs.produs_id,
                produs.cantitate,
                produs.data_primire.isoformat(),
                "in_verificare",
                produs.observatii
            )
        )

        inregistrare_id = cursor.lastrowid

        conn.execute(
            """
            INSERT INTO jurnal_activitate
            (utilizator_id, actiune, tip_obiect,
             obiect_id, detalii)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                None,
                "creare",
                "produs_necomandat",
                inregistrare_id,
                f"Produs {produs.produs_id}, "
                f"cantitate {produs.cantitate}"
            )
        )

    return {
        "id": inregistrare_id,
        "mesaj": "Produsul necomandat a fost inregistrat!",
        "status": "in_verificare"
    }

@app.get("/produse-necomandate")
def lista_produse_necomandate():
    with get_connection() as conn:
        produse = conn.execute(
            """
            SELECT
                pn.id,
                pn.comanda_id,
                pn.produs_id,
                p.denumire AS produs,
                pn.cantitate,
                pn.data_primire,
                pn.status,
                pn.observatii
            FROM produse_necomandate pn
            JOIN produse p ON p.id = pn.produs_id
            ORDER BY pn.id DESC
            """
        ).fetchall()

    return [dict(produs) for produs in produse]

class DecizieProdusNecomandat(BaseModel):
    decizie: str


@app.patch("/produse-necomandate/{produs_id}/decizie")
def decide_produs_necomandat(
    produs_id: int,
    date_decizie: DecizieProdusNecomandat
):
    decizie = date_decizie.decizie.lower().strip()

    if decizie not in ("aprobat", "respins"):
        raise HTTPException(
            status_code=422,
            detail="Decizia trebuie sa fie aprobat sau respins."
        )

    with get_connection() as conn:
        produs = conn.execute(
            """
            SELECT id, status
            FROM produse_necomandate
            WHERE id = ?
            """,
            (produs_id,)
        ).fetchone()

        if not produs:
            raise HTTPException(
                status_code=404,
                detail="Produsul necomandat nu exista."
            )

        if produs["status"] != "in_verificare":
            raise HTTPException(
                status_code=409,
                detail="Pentru acest produs exista deja o decizie."
            )

        conn.execute(
            """
            UPDATE produse_necomandate
            SET status = ?
            WHERE id = ?
            """,
            (decizie, produs_id)
        )

        conn.execute(
            """
            INSERT INTO jurnal_activitate
            (utilizator_id, actiune, tip_obiect, obiect_id, detalii)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                None,
                decizie,
                "produs_necomandat",
                produs_id,
                f"Produs necomandat {decizie}"
            )
        )

    return {
        "id": produs_id,
        "status": decizie,
        "mesaj": "Decizia a fost inregistrata cu succes!"
    }

@app.get("/comenzi-intarziate")
def lista_comenzi_intarziate():
    astazi = date.today().isoformat()

    with get_connection() as conn:
        comenzi = conn.execute(
            """
            SELECT c.id, c.data_livrare,
                   f.nume AS furnizor
            FROM comenzi c
            JOIN furnizori f ON f.id = c.furnizor_id
            WHERE c.data_livrare < ?
            ORDER BY c.data_livrare
            """,
            (astazi,)
        ).fetchall()

        rezultat = []

        for comanda in comenzi:
            produse = conn.execute(
                """
                SELECT p.denumire,
                       pc.cantitate AS comandat,
                       COALESCE((
                           SELECT SUM(pr.cantitate)
                           FROM pozitii_receptie pr
                           JOIN receptii r
                             ON r.id = pr.receptie_id
                           WHERE r.comanda_id = pc.comanda_id
                             AND pr.produs_id = pc.produs_id
                       ), 0) AS primit
                FROM pozitii_comanda pc
                JOIN produse p ON p.id = pc.produs_id
                WHERE pc.comanda_id = ?
                """,
                (comanda["id"],)
            ).fetchall()

            restante = []

            for produs in produse:
                cantitate_restanta = (
                    produs["comandat"] - produs["primit"]
                )

                if cantitate_restanta > 0:
                    restante.append({
                        "produs": produs["denumire"],
                        "cantitate_restanta": cantitate_restanta
                    })

            if restante:
                rezultat.append({
                    "comanda_id": comanda["id"],
                    "furnizor": comanda["furnizor"],
                    "termen_livrare": comanda["data_livrare"],
                    "status": "intarziata",
                    "produse_restante": restante
                })

    return rezultat


@app.get("/facturi-blocate")
def lista_facturi_blocate():
    with get_connection() as conn:
        facturi = conn.execute(
            """
            SELECT
                f.id,
                f.numar,
                f.comanda_id,
                f.data_factura,
                f.moneda,
                f.valoare,
                f.status
            FROM facturi f
            WHERE f.status = 'blocata'
            ORDER BY f.id DESC
            """
        ).fetchall()

    return [dict(factura) for factura in facturi]
@app.post("/trimite-notificari-email")
def trimite_notificari_comenzi():
    destinatar = os.getenv("EMAIL_NOTIFICARI")

    if not destinatar:
        raise HTTPException(
            status_code=500,
            detail="Lipseste EMAIL_NOTIFICARI din .env"
        )

    comenzi = lista_comenzi_intarziate()
    facturi = lista_facturi_blocate()

    if not comenzi and not facturi:
        return "Nu exista comenzi intarziate sau facturi blocate."

    mesaj = "NOTIFICARI - FLUX DE APROVIZIONARE\n\n"

    mesaj += "COMENZI INTARZIATE:\n\n"

    if comenzi:
        for comanda in comenzi:
            mesaj += (
                f"Comanda #{comanda['comanda_id']}\n"
                f"Furnizor: {comanda['furnizor']}\n"
                f"Termen livrare: {comanda['termen_livrare']}\n\n"
            )
    else:
        mesaj += "Nu exista comenzi intarziate.\n\n"

    mesaj += "\nFACTURI BLOCATE:\n\n"

    if facturi:
        for factura in facturi:
            mesaj += (
                f"Factura: {factura['numar']}\n"
                f"Comanda: #{factura['comanda_id']}\n"
                f"Valoare: {factura['valoare']} {factura['moneda']}\n"
                f"Status: {factura['status']}\n\n"
            )
    else:
        mesaj += "Nu exista facturi blocate.\n"

    try:
        trimite_email(
            destinatar,
            "Alerta - Flux de aprovizionare",
            mesaj
        )
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Emailul nu a putut fi trimis."
        )

    return "Emailul cu notificarile a fost trimis cu succes."