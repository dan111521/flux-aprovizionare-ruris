
async function afiseazaFurnizori() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = "<h2>Lista furnizorilor</h2><p>Se încarcă...</p>";

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/furnizori");

        if (!raspuns.ok) {
            throw new Error("Serverul a răspuns cu eroarea " + raspuns.status);
        }

        const furnizori = await raspuns.json();
        
const raspunsProduse = await fetch("http://127.0.0.1:8000/produse");

if (!raspunsProduse.ok) {
    throw new Error("Nu s-au putut încărca produsele.");
}

const produse = await raspunsProduse.json();


        zona.innerHTML = "<h2>Lista furnizorilor</h2>";

        if (furnizori.length === 0) {
            zona.innerHTML += "<p>Nu există furnizori înregistrați.</p>";
            return;
        }

        const lista = document.createElement("ul");

        furnizori.forEach(furnizor => {
            const element = document.createElement("li");
            element.textContent = furnizor.nume;
            lista.appendChild(element);
        });

        zona.appendChild(lista);

    } catch (eroare) {
        zona.innerHTML = "<h2>Lista furnizorilor</h2><p>Nu s-au putut încărca furnizorii.</p>";
        console.error(eroare);
    }
}

async function afiseazaProduse() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = "<h2>Lista produselor</h2><p>Se încarcă...</p>";

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/produse");

        if (!raspuns.ok) {
            throw new Error("Eroare server: " + raspuns.status);
        }

        const produse = await raspuns.json();

        zona.innerHTML = "<h2>Lista produselor</h2>";

        if (produse.length === 0) {
            zona.innerHTML += "<p>Nu există produse înregistrate.</p>";
            return;
        }

        const lista = document.createElement("ul");

        produse.forEach(produs => {
            const element = document.createElement("li");
            element.textContent = produs.denumire + " (" + produs.unitate_masura + ")";
            lista.appendChild(element);
        });

        zona.appendChild(lista);

    } catch (eroare) {
        zona.innerHTML = "<h2>Lista produselor</h2><p>Nu s-au putut încărca produsele.</p>";
        console.error(eroare);
    }
}

async function afiseazaComenzi() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = "<h2>Lista comenzilor</h2><p>Se încarcă...</p>";

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/comenzi");

        if (!raspuns.ok) {
            throw new Error("Eroare server: " + raspuns.status);
        }

        const comenzi = await raspuns.json();

        zona.innerHTML = "<h2>Lista comenzilor</h2>";

        if (comenzi.length === 0) {
            zona.innerHTML += "<p>Nu există comenzi înregistrate.</p>";
            return;
        }

        const lista = document.createElement("ul");

        comenzi.forEach(comanda => {
            const element = document.createElement("li");

            element.textContent =
                "Comanda #" + comanda.id +
                " | Furnizor: " + comanda.furnizor_id +
                " | Livrare: " + comanda.data_livrare +
                " | Status: " + comanda.status;

            lista.appendChild(element);
        });

        zona.appendChild(lista);

    } catch (eroare) {
        zona.innerHTML =
            "<h2>Lista comenzilor</h2><p>Nu s-au putut încărca comenzile.</p>";
        console.error(eroare);
    }
}

async function afiseazaFacturi() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = "<h2>Facturi blocate</h2><p>Se încarcă...</p>";

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/facturi-blocate");

        if (!raspuns.ok) {
            throw new Error("Eroare server: " + raspuns.status);
        }

        const facturi = await raspuns.json();

        zona.innerHTML = "<h2>Facturi blocate</h2>";

        if (facturi.length === 0) {
            zona.innerHTML += "<p>Nu există facturi blocate.</p>";
            return;
        }

        const lista = document.createElement("ul");

        facturi.forEach(factura => {
            const element = document.createElement("li");

            element.textContent =
                "Factura #" + factura.id +
                " | Număr: " + factura.numar +
                " | Valoare: " + factura.valoare +
                " " + factura.moneda +
                " | Status: " + factura.status;

            lista.appendChild(element);
        });

        zona.appendChild(lista);

    } catch (eroare) {
        zona.innerHTML =
            "<h2>Facturi blocate</h2><p>Nu s-au putut încărca facturile.</p>";
        console.error(eroare);
    }
}

async function afiseazaReceptii() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = "<h2>Recepții depozit</h2><p>Se încarcă...</p>";

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/comenzi");

        if (!raspuns.ok) {
            throw new Error("Eroare server: " + raspuns.status);
        }

        const comenzi = await raspuns.json();

        zona.innerHTML = "<h2>Recepții depozit</h2>";

        if (comenzi.length === 0) {
            zona.innerHTML += "<p>Nu există comenzi de verificat.</p>";
            return;
        }

        const select = document.createElement("select");
        select.id = "comanda-receptie";

        comenzi.forEach(comanda => {
            const optiune = document.createElement("option");
            optiune.value = comanda.id;
            optiune.textContent = "Comanda #" + comanda.id;
            select.appendChild(optiune);
        });
        



        const buton = document.createElement("button");
        buton.textContent = "Verifică recepția";
        const butonInregistrare = document.createElement("button");
butonInregistrare.textContent = "+ Înregistrează recepție";
butonInregistrare.type = "button";
butonInregistrare.onclick = function() {
    const comandaId = document.getElementById("comanda-receptie").value;

    const zonaFormular = document.createElement("div");

    zonaFormular.innerHTML = `
        <h3>Înregistrează recepție - Comanda #${comandaId}</h3>

        <p>
            <label>ID produs:</label><br>
            <input type="number" id="produs-receptionat" min="1">
        </p>

        <p>
            <label>Cantitate primită:</label><br>
            <input type="number" id="cantitate-receptionata"
                   min="0.01" step="0.01">
        </p>

        <button type="button" id="salveaza-receptie">
            Salvează recepția
        </button>
    `;

    document.getElementById("rezultate").appendChild(zonaFormular);
    document.getElementById("salveaza-receptie").onclick = async function() {
    const produsId = Number(document.getElementById("produs-receptionat").value);
    const cantitate = Number(document.getElementById("cantitate-receptionata").value);

    if (!produsId || !Number.isFinite(cantitate) || cantitate <= 0) {
        alert("Completează corect ID-ul produsului și cantitatea!");
        return;
    }

    const receptie = {
        comanda_id: Number(comandaId),
        data_receptie: new Date().toLocaleDateString("en-CA"),
        produse: [
            {
                produs_id: produsId,
                cantitate: cantitate
            }
        ]
    };

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/receptii", {
            method: "POST",
           headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + tokenAutentificare
},
            body: JSON.stringify(receptie)
        });

        if (!raspuns.ok) {
            const eroare = await raspuns.text();
            alert("Eroare la salvare: " + eroare);
            return;
        }

        alert("Recepția a fost salvată cu succes!");
        zonaFormular.remove();

    } catch (eroare) {
        alert("Nu s-a putut contacta serverul.");
    }
};
};
        buton.onclick = verificaReceptie;

        zona.appendChild(select);
        zona.appendChild(buton);
        zona.appendChild(butonInregistrare);

        const rezultat = document.createElement("pre");
        rezultat.id = "situatie-receptie";
        zona.appendChild(rezultat);

    } catch (eroare) {
        zona.innerHTML = "<h2>Recepții depozit</h2><p>Nu s-au putut încărca comenzile.</p>";
        console.error(eroare);
    }
}

async function verificaReceptie() {
    const id = document.getElementById("comanda-receptie").value;
    const rezultat = document.getElementById("situatie-receptie");

    rezultat.textContent = "Se verifică recepția...";

    try {
        const raspuns = await fetch(
            "http://127.0.0.1:8000/comenzi/" + id + "/situatie"
        );

        if (!raspuns.ok) {
            throw new Error("Eroare server: " + raspuns.status);
        }

        const situatie = await raspuns.json();

        rezultat.textContent = JSON.stringify(situatie, null, 2);

    } catch (eroare) {
        rezultat.textContent = "Nu s-a putut verifica recepția.";
        console.error(eroare);
    }
}

async function afiseazaNotificari() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = "<h2>Notificări</h2><p>Se verifică comenzile întârziate...</p>";

    try {
        const raspuns = await fetch(
            "http://127.0.0.1:8000/comenzi-intarziate"
        );

        if (!raspuns.ok) {
            throw new Error("Eroare server: " + raspuns.status);
        }

        const comenzi = await raspuns.json();

        zona.innerHTML = "<h2>Comenzi întârziate</h2>";

        if (comenzi.length === 0) {
            zona.innerHTML += "<p>Nu există comenzi întârziate în acest moment.</p>";
        }

        const lista = document.createElement("ul");

        comenzi.forEach(comanda => {
            const element = document.createElement("li");

            element.textContent =
                "Comanda #" + comanda.id +
                " | Termen de livrare: " + comanda.data_livrare +
                " | Status: " + comanda.status;

            lista.appendChild(element);
        });

        zona.appendChild(lista);

    await incarcaFacturiBlocate();
} catch (eroare) {
        zona.innerHTML =
            "<h2>Notificări</h2><p>Nu s-au putut încărca notificările.</p>";
        console.error(eroare);
    }
}

function formularFurnizor() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = `
        <h2>Adaugă furnizor nou</h2>

        <form id="formular-furnizor">
            <p>
                <label>Nume furnizor:</label><br>
                <input type="text" id="nume-furnizor" required>
            </p>

            <p>
                <label>CUI:</label><br>
                <input type="text" id="cui-furnizor" required>
            </p>

            <p>
                <label>Email:</label><br>
                <input type="email" id="email-furnizor" required>
            </p>

            <button type="submit">Salvează furnizorul</button>
        </form>

        <p id="mesaj-furnizor"></p>
    `;

    
document.getElementById("formular-furnizor").onsubmit = async function(event) {
    event.preventDefault();

    const mesaj = document.getElementById("mesaj-furnizor");

    if (!tokenAutentificare) {
        mesaj.textContent = "Trebuie să te autentifici mai întâi.";
        return;
    }

    const furnizor = {
        nume: document.getElementById("nume-furnizor").value,
        cui: document.getElementById("cui-furnizor").value,
        email: document.getElementById("email-furnizor").value
    };

    mesaj.textContent = "Se salvează furnizorul...";

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/furnizori", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + tokenAutentificare
            },
            body: JSON.stringify(furnizor)
        });

        if (!raspuns.ok) {
            throw new Error("Eroare: " + raspuns.status);
        }

        mesaj.textContent = "Furnizor salvat cu succes!";
        document.getElementById("formular-furnizor").reset();

    } catch (eroare) {
        mesaj.textContent = "Nu s-a putut salva furnizorul: " + eroare.message;
    }
};

}

let tokenAutentificare = "";

function formularLogin() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = `
        <h2>Autentificare</h2>

        <form id="formular-login">
            <p>
                <label>Utilizator:</label><br>
                <input type="text" id="username-login" required>
            </p>

            <p>
                <label>Parolă:</label><br>
                <input type="password" id="parola-login" required>
            </p>

            <button type="submit">Conectare</button>
        </form>

        <p id="mesaj-login"></p>
    `;

    
document.getElementById("formular-login").onsubmit = async function(event) {
    event.preventDefault();

    const username = document.getElementById("username-login").value;
    const parola = document.getElementById("parola-login").value;
    const mesaj = document.getElementById("mesaj-login");

    mesaj.textContent = "Se verifică autentificarea...";

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                parola: parola
            })
        });

        if (!raspuns.ok) {
            throw new Error("Autentificare nereușită: " + raspuns.status);
        }

        const date = await raspuns.json();

        tokenAutentificare = date.access_token;

        mesaj.textContent = "Autentificare reușită!";
        document.getElementById("stare-autentificare").textContent =
            "Ești autentificat.";

    } catch (eroare) {
        mesaj.textContent = "Autentificare nereușită. Verifică datele.";
        console.error(eroare);
    }
};

}

function formularProdus() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = `
        <h2>Adaugă produs nou</h2>

        <form id="formular-produs">
            <p>
                <label>Denumire produs:</label><br>
                <input type="text" id="denumire-produs" required>
            </p>

            <p>
                <label>Unitate de măsură:</label><br>
                <select id="unitate-produs">
                    <option value="buc">Bucăți</option>
                    <option value="kg">Kilograme</option>
                    <option value="litri">Litri</option>
                    <option value="m">Metri</option>
                </select>
            </p>

            <button type="submit">Salvează produsul</button>
        </form>

        <p id="mesaj-produs"></p>
    `;

    
document.getElementById("formular-produs").onsubmit = async function(event) {
    event.preventDefault();

    const mesaj = document.getElementById("mesaj-produs");

    if (!tokenAutentificare) {
        mesaj.textContent = "Trebuie să te autentifici mai întâi.";
        return;
    }

    const produs = {
        denumire: document.getElementById("denumire-produs").value,
        unitate_masura: document.getElementById("unitate-produs").value
    };

    mesaj.textContent = "Se salvează produsul...";

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/produse", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + tokenAutentificare
            },
            body: JSON.stringify(produs)
        });

        if (!raspuns.ok) {
            throw new Error("Eroare: " + raspuns.status);
        }

        mesaj.textContent = "Produs salvat cu succes!";
        document.getElementById("formular-produs").reset();

    } catch (eroare) {
        mesaj.textContent = "Nu s-a putut salva produsul: " + eroare.message;
    }
};

}

async function formularComanda() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = `
        <h2>Comandă nouă</h2>
        <p>Se încarcă furnizorii...</p>
    `;

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/furnizori");

        if (!raspuns.ok) {
            throw new Error("Nu s-au putut încărca furnizorii.");
        }

        const furnizori = await raspuns.json();
const raspunsProduse = await fetch("http://127.0.0.1:8000/produse");

if (!raspunsProduse.ok) {
    throw new Error("Nu s-au putut încărca produsele.");
}

const produse = await raspunsProduse.json();
        zona.innerHTML = `
            <h2>Comandă nouă</h2>

            <form id="formular-comanda">
                <p>
                    <label>Furnizor:</label><br>
                    <select id="furnizor-comanda" required></select>
                </p>

                <p>
                    <label>Data livrării:</label><br>
                    <input type="date" id="data-livrare-comanda" required>
                </p>
                
<p>
    <label>Produs:</label><br>
    <select id="produs-comanda" required></select>
</p>

<p>
    <label>Cantitate:</label><br>
    <input type="number" id="cantitate-comanda"
           min="0.01" step="0.01" required>
</p>

<p>
    <label>Preț unitar (RON):</label><br>
    <input type="number" id="pret-comanda"
           min="0" step="0.01" required>
</p>
<p>
    <button type="button" id="adauga-produs-comanda">
        + Adaugă produs în comandă
    </button>
</p>
<p id="numar-produse-comanda">Produse în comandă: 0</p>

                <button type="submit">Continuă</button>
            </form>

            <p id="mesaj-comanda"></p>
        `;

        const select = document.getElementById("furnizor-comanda");

        furnizori.forEach(furnizor => {
            const optiune = document.createElement("option");
            optiune.value = furnizor.id;
            optiune.textContent = furnizor.nume;
            select.appendChild(optiune);
        });

 const selectProduse = document.getElementById("produs-comanda");

produse.forEach(produs => {
    const optiune = document.createElement("option");
    optiune.value = produs.id;
    optiune.textContent = produs.denumire;
    selectProduse.appendChild(optiune);
});
        
const produseAdaugate = [];

document.getElementById("adauga-produs-comanda").onclick = function() {
    const produsId = Number(
        document.getElementById("produs-comanda").value
    );
    const cantitate = Number(
        document.getElementById("cantitate-comanda").value
    );
    const pret = Number(
        document.getElementById("pret-comanda").value
    );

    if (!produsId || cantitate <= 0 || pret < 0 ||
        !Number.isFinite(cantitate) || !Number.isFinite(pret)) {
        alert("Completează corect produsul, cantitatea și prețul.");
        return;
    }

    produseAdaugate.push({
        produs_id: produsId,
        cantitate: cantitate,
        pret_unitar: pret
    });

    document.getElementById("numar-produse-comanda").textContent =
        "Produse în comandă: " + produseAdaugate.length;

    document.getElementById("cantitate-comanda").value = "";
    document.getElementById("pret-comanda").value = "";
};

document.getElementById("formular-comanda").onsubmit = async function(event) {
    event.preventDefault();

    const mesaj = document.getElementById("mesaj-comanda");

    if (!tokenAutentificare) {
        mesaj.textContent = "Trebuie să te autentifici mai întâi.";
        return;
    }
if (produseAdaugate.length === 0) {
    alert("Adaugă cel puțin un produs în comandă!");
    return;
}
    const comanda = {
        furnizor_id: Number(
            document.getElementById("furnizor-comanda").value
        ),
        data_comanda: new Date().toLocaleDateString("en-CA"),
        data_livrare: document.getElementById("data-livrare-comanda").value,
        produse: produseAdaugate
    };

    mesaj.textContent = "Se salvează comanda...";

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/comenzi", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + tokenAutentificare
            },
            body: JSON.stringify(comanda)
        });

        if (!raspuns.ok) {
            const eroare = await raspuns.text();
            throw new Error("Cod " + raspuns.status + ": " + eroare);
        }

        mesaj.textContent = "Comanda a fost salvată cu succes!";
        document.getElementById("formular-comanda").reset();

    } catch (eroare) {
        mesaj.textContent = "Eroare la salvare: " + eroare.message;
    }
};


    } catch (eroare) {
        zona.textContent = "Nu s-a putut deschide formularul de comandă.";
        console.error(eroare);
    }
}


async function formularFactura() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = `
        <h2>Înregistrare factură nouă</h2>

        <form id="formular-factura">
            <p>
                <label>ID comandă:</label><br>
                <input type="number" id="factura-comanda" min="1" required>
            </p>

            <p>
                <label>Număr factură:</label><br>
                <input type="text" id="factura-numar" required>
            </p>

            <p>
                <label>Data facturii:</label><br>
                <input type="date" id="factura-data" required>
            </p>

            <p>
                <label>Moneda:</label><br>
                <select id="factura-moneda">
                    <option value="RON">RON</option>
                    <option value="EUR">EUR</option>
                </select>
            </p>

            <p>
                <label>Valoare factură:</label><br>
                <input type="number" id="factura-valoare"
                       min="0.01" step="0.01" required>
            </p>

            <button type="submit">Salvează factura</button>
        </form>
    `;
    
    document.getElementById("formular-factura").onsubmit = async function(event) {
        event.preventDefault();

        const factura = {
            comanda_id: Number(document.getElementById("factura-comanda").value),
            numar: document.getElementById("factura-numar").value,
            data_factura: document.getElementById("factura-data").value,
            moneda: document.getElementById("factura-moneda").value,
            valoare: Number(document.getElementById("factura-valoare").value)
        };

        try {
            const raspuns = await fetch("http://127.0.0.1:8000/facturi", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...(tokenAutentificare ? {
                        "Authorization": "Bearer " + tokenAutentificare
                    } : {})
                },
                body: JSON.stringify(factura)
            });

            if (!raspuns.ok) {
                alert("Eroare la salvarea facturii: " + await raspuns.text());
                return;
            }

            alert("Factura a fost salvată cu succes!");
            document.getElementById("formular-factura").reset();

        } catch (eroare) {
            alert("Nu s-a putut contacta serverul.");
        }
    };

}

async function verificaFactura() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = `
        <h2>Verificare factură</h2>

        <p>
            <label>ID factură:</label><br>
            <input type="number" id="id-factura-verificare" min="1" required>
        </p>

        <button type="button" id="buton-verifica-factura">
            Verifică
        </button>

        <div id="rezultat-verificare-factura"></div>
    `;

    document.getElementById("buton-verifica-factura").onclick = async function() {
        const id = Number(document.getElementById("id-factura-verificare").value);
        const rezultat = document.getElementById("rezultat-verificare-factura");

        if (!Number.isInteger(id) || id <= 0) {
            rezultat.textContent = "Introdu un ID de factură valid.";
            return;
        }

        rezultat.textContent = "Se verifică factura...";

        try {
            const raspuns = await fetch(
                "http://127.0.0.1:8000/facturi/" + id + "/verificare"
            );

            if (!raspuns.ok) {
                rezultat.textContent = "Eroare: " + await raspuns.text();
                return;
            }

            const date = await raspuns.json();

            rezultat.innerHTML = `
                <h3>Rezultatul verificării</h3>
                <p>Valoare factură: ${date.valoare_factura_ron} RON</p>
                <p>Valoare recepționată: ${date.valoare_receptionata_ron} RON</p>
                <p>Diferență: ${date.diferenta_ron} RON</p>
                <p>Status: <strong>${date.status}</strong></p>
                <p>Mesaj: ${date.mesaj}</p>
            `;

        } catch (eroare) {
            rezultat.textContent = "Nu s-a putut contacta serverul.";
        }
    };
}


async function incarcaFacturiBlocate() {
    const zona = document.getElementById("rezultate");

    const titlu = document.createElement("h2");
    titlu.textContent = "Facturi blocate";
    zona.appendChild(titlu);

    try {
        const raspuns = await fetch("http://127.0.0.1:8000/facturi-blocate");

        if (!raspuns.ok) {
            throw new Error("Eroare server: " + raspuns.status);
        }

        const facturi = await raspuns.json();

        if (facturi.length === 0) {
            const mesaj = document.createElement("p");
            mesaj.textContent = "Nu există facturi blocate.";
            zona.appendChild(mesaj);
            return;
        }

        const lista = document.createElement("ul");

        facturi.forEach(factura => {
            const element = document.createElement("li");
            element.textContent =
                factura.numar +
                " | Comanda #" + factura.comanda_id +
                " | Valoare: " + factura.valoare + " " + factura.moneda +
                " | Status: " + factura.status;

            lista.appendChild(element);
        });

        zona.appendChild(lista);

    } catch (eroare) {
        const mesaj = document.createElement("p");
        mesaj.textContent = "Nu s-au putut încărca facturile blocate.";
        zona.appendChild(mesaj);
        console.error(eroare);
    }
}


function formularReceptie() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = `
        <h2>Recepție nouă</h2>

        <p>
            <label>ID comandă:</label><br>
            <input type="number" id="receptie-comanda" min="1">
        </p>

        <p>
            <label>Data recepției:</label><br>
            <input type="date" id="receptie-data">
        </p>

        <p>
            <label>ID produs:</label><br>
            <input type="number" id="receptie-produs" min="1">
        </p>

        <p>
            <label>Cantitate primită:</label><br>
            <input type="number" id="receptie-cantitate"
                   min="0.01" step="0.01">
        </p>

        <button type="button" id="salveaza-receptie">
            Salvează recepția
        </button>

        <p id="mesaj-receptie"></p>
    `;
    
    document.getElementById("salveaza-receptie").onclick = async function() {
        const mesaj = document.getElementById("mesaj-receptie");

        const comandaId = Number(
            document.getElementById("receptie-comanda").value
        );
        const data = document.getElementById("receptie-data").value;
        const produsId = Number(
            document.getElementById("receptie-produs").value
        );
        const cantitate = Number(
            document.getElementById("receptie-cantitate").value
        );

        if (!Number.isInteger(comandaId) || comandaId <= 0 ||
            !data || !Number.isInteger(produsId) || produsId <= 0 ||
            !Number.isFinite(cantitate) || cantitate <= 0) {
            mesaj.textContent = "Completează corect toate câmpurile.";
            return;
        }

        const receptie = {
            comanda_id: comandaId,
            data_receptie: data,
            produse: [
                {
                    produs_id: produsId,
                    cantitate: cantitate
                }
            ]
        };

        mesaj.textContent = "Se salvează recepția...";

        try {
            const raspuns = await fetch("http://127.0.0.1:8000/receptii", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(receptie)
            });

            if (!raspuns.ok) {
                mesaj.textContent = "Eroare: " + await raspuns.text();
                return;
            }

            mesaj.textContent = "Recepția a fost salvată cu succes!";
        } catch (eroare) {
            mesaj.textContent = "Nu s-a putut contacta serverul.";
        }
    };

}

async function trimiteNotificariEmail() {
    const zona = document.getElementById("rezultate");

    zona.innerHTML = "<p>Se verifică notificările...</p>";

    try {
        const raspuns = await fetch(
            "http://127.0.0.1:8000/trimite-notificari-email",
            {
                method: "POST"
            }
        );

        const rezultat = await raspuns.json();

        if (!raspuns.ok) {
            throw new Error(rezultat.detail || "Eroare la trimitere.");
        }

        zona.innerHTML = `<p>${rezultat}</p>`;
    } catch (eroare) {
        zona.textContent = "Eroare: " + eroare.message;
    }
}