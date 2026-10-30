# Flux de aprovizionare – RURIS

Aplicație web demonstrativă pentru gestionarea integrată a proceselor de achiziții, recepție a mărfurilor și verificare a facturilor.

## Descrierea proiectului

Proiectul urmărește digitalizarea fluxului de aprovizionare, de la înregistrarea furnizorilor și lansarea comenzilor până la recepția produselor și verificarea documentelor financiare.

## Funcționalități principale

- Gestionarea furnizorilor și produselor.
- Crearea comenzilor de aprovizionare cu mai multe produse.
- Înregistrarea recepțiilor parțiale.
- Urmărirea cantităților comandate, recepționate și restante.
- Înregistrarea și verificarea facturilor.
- Identificarea facturilor blocate și a comenzilor întârziate.
- Trimiterea manuală a notificărilor prin email.
- Autentificarea utilizatorilor și controlul accesului pe roluri.
- Jurnal de audit în backend.
- Conversia valorilor valutare.

## Tehnologii utilizate

- **Backend:** Python, FastAPI
- **Frontend:** HTML, CSS, JavaScript
- **Bază de date:** SQLite
- **Autentificare:** JWT
- **Email:** SMTP Yahoo
- **Versionare:** Git și GitHub

## Structura proiectului

```text
flux-aprovizionare/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── autorizare.py
│   ├── securitate.py
│   ├── emailuri.py
│   ├── curs_valutar.py
│   └── creare_utilizator.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   ├── script.js
│   └── ruris.png
├── .gitignore
└── README.md
```

## Instalare și pornire

**1.** Instalați Python și bibliotecile necesare proiectului.

**2.** Configurați fișierul `.env` cu setările necesare autentificării și serviciului SMTP. Parolele și cheile se păstrează local.

**3.** Din folderul principal al proiectului, porniți serverul:

```powershell
py -m uvicorn backend.main:app --reload
```

**4.** Deschideți interfața aplicației din fișierul:

```text
frontend/index.html
```

**5.** Documentația interactivă a API-ului este disponibilă la:

```text
http://127.0.0.1:8000/docs
```

## Notificări prin email

Aplicația permite transmiterea unui email care centralizează comenzile întârziate și facturile blocate.

Trimiterea este declanșată manual, prin butonul **„Trimite notificări pe email”**.

## Observații

Aplicația este un proiect demonstrativ. Pentru utilizarea într-un mediu de producție sunt necesare verificări suplimentare de securitate, configurare și testare.

## Autor

Proiect demonstrativ – Flux de aprovizionare RURIS.