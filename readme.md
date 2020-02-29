# Projekt IoT platforma
#### Seminar iz načrtovanja in razvoja programske opreme v telekomunikacijah 2020

Projekt IoT platforma je sestavljen iz treh delov - API strežnika, spletne aplikacije in knjižnice za uporabo na mikrokrmilnikih ESP.

Predvidena uporaba je sledeča:\
Uporabnik si najprej ustvari račun z uporabniškim imenom in geslom, ki se uporabljata za identifikacijo in avtorizacijo pri uporabi API zahtevkov. Nato uporabnik v sistemu ustvari napravo, ki ima svoje ime, lokacijo in spremenljivke. Ta naprava je lahko katerakoli stvar zmožna pošiljanja HTTP zahtevkov. Primer naprave, ki se lahko uporabi je zelo popularen in dostopen mikrokrmilnik ESP8266, ki ima že vgrajeno WiFi povezljivost. Ta naprava lahko nato odčituje razne senzorje in podatke o meritvah z uporabo API klica nalaga na strežnik. Uporabnik do teh meritev lahko dostopa preko spletne ali mobilne aplikacije. Poleg samega pregleda meritev spletna aplikacija omogoča tudi dostop do vseh ostalih funkcionalnosti, ki jih omogoča API, razen nalaganja novih meritev. Dostop do te funkcionalnosti omogoča knjižnica za mikrokrmilnike ESP.



---
## IoT API dokumentacija
API je razdeljen na 3 dele, ki predstavljajo 3 API endpoint-e. To so /users za upravljanje z uporabniki, /devices za upravljanje z uporabnikovimi napravami in /measurements za uporavljanje z meritvami naprav.

Primer strežnika je dostopen na ```api.zrak.janvr.wtf``` in omogoča dostop preko HTTP in HTTPS protokolov.

Vsi zahtevki potrebujejo avtorizacijsko glavo tipa basic.
To pomeni, da v glavo zahtevka 'Authorization' vnesemo vrednost 'Basic ' in pa 'username:password' kodirano v sistemu base64.
Izjema je le zahtevek za ustvarjanje novega uporabnika, kjer se uporabniško ime in geslo vpišeta v telo zahtevka.

Za uporabo strežnika na lastnem račulaniku morate imeti nameščen programski jezik Python 3 in njegove knjižnice [flask](https://flask.palletsprojects.com), [flask_cors](https://flask-cors.readthedocs.io), [click](https://click.palletsprojects.com), in [werkzeug](https://werkzeug.palletsprojects.com).
Za zagon strežnika odpremo ukazno vrstico v mapi kjer se nahajajo datotetke tega repozitorija in izvedemo ukaze (velja za Linux OS):
```
$ export FLASK_APP=hello.py
$ flask init-db
$ flask run
```
Na Windows OS se ukaz ```export``` zamenja s ```set```.\
Ukaz ```flask init-db``` izvedemo samo ob prvem zagonu in pa kadar želimo ponastaviti podatkovno bazo.

Na naslovu ```/manage``` se nahaja tudi spletni vmesnik za administrativno upravljanje z uporabniki, napravami in meritvami. Dostop do tega vmesnika je omogočen le uporabniku admin, ki se ustvari ob ukazu ```flask init-db```. Uporabniško ime: admin, geslo: admin.


----
### ```/users``` API - manipulacija z uporabniškimi računi

#### POST - ustvarjanje novega uporabnika

Primer zahtevka za ustvaritev novega računa:
```
POST /users HTTP/1.1
Host: api.zrak.janvr.wtf
Content-Type: application/json

{
	"username": "JanezNovak",
	"password": "geslo123",
	"email": "janez@novak.si"}
```
Če je bila obdelava zahtevka uspešna bo strežnik vrnil kodo 200 in podatke o ustvarjenem računu.

Primer odgovora:
```
{
    "email": "janez@novak.si",
    "time_created": "2020-02-23 16:25:21",
    "user_id": 5,
    "username": "JanezNovak"
}
```

#### GET - podatki o uporabniku
Z zahtevkom GET lahko pridobimo podatke o uporabniku. Je tudi priročen način za avtorizacijo v odjemalski aplikaciji.

Primer zahtevka:
```
GET /users HTTP/1.1
Host: api.zrak.janvr.wtf
Authorization: Basic SmFuZXpOb3ZhazpnZXNsbzEyMw==
```
V primeru, da je bila obdelava zahtevka uspešna bo strežnik vrnil kodo 200 in podatke o uporabniku.
```
{
    "email": "janez@novak.si",
    "time_created": "2020-02-23 16:25:21",
    "user_id": 5,
    "username": "JanezNovak"
}
```

#### PUT - urejanje uporabnika
V primeru, da se prej ustvarjeni uporabnik želi preimenovati iz Janeza v Jana lahko to stori z PUT zahtevkom enake strukture kot pri ustvarjanju novega uprabnika. V primeru, da se spreminja geslo mora avtorizacijska glava vsebovati staro geslo, telo zahtevka pa novo.

Primer zahtevka za spremenitev uporabniškega ime, e-pošte in gesla:

```
PUT /users HTTP/1.1
Host: api.zrak.janvr.wtf
Content-Type: application/json
Authorization: Basic SmFuZXpOb3ZhazpnZXNsbzEyMw==

{
	"username": "JanNovak",
	"email": "jan@novak.si",
	"password": "geslo1234"
}
```
Podatke katere ne želimo spreminjati lako v zahtevku preprosto izpustimo.
V primeru, da je bila obdelava zahtevka uspešna strežnik odgovori s kodo 200 in posodobljenimi podatki v telesu odgovora.

Primer odgovora na zgornji zahtevek: 
```
{
    "email": "jan@novak.si",
    "time_created": "2020-02-23 16:25:21",
    "user_id": 5,
    "username": "JanNovak"
}
```

#### DELETE - izbris uporabika
Če je uporabnik razočaran na uporabno vrednostjo IoT platforme lahko svoj uporabniški račun izbriše z DELETE zahtevkom.

Primer izbrisa uporabika:
```
DELETE /users HTTP/1.1
Host: api.zrak.janvr.wtf
Authorization: Basic SmFuTm92YWs6Z2VzbG8xMjM0
```
Če je bil izbris uspešen bo strežnik odgovoril s kodo 200 in odgovorom:
```
Success: User 'JanNovak' deleted
```

----
### ```/devices``` API - manipulacija z uporabnikovimi napravami

#### POST - ustvarjanje nove naprave
Za ustvarjanje nove naprave na strežnik pošljemo POST zahtevek z opisom naprave. Vsaka naprava ima svoje ime, lokacijo (neobvezno) in spremenljivke.

Primer zahtevka za ustvarjanje nove naprave z imenom "esp8266", lokacijo "Jupiter" in spremenljivkami "CO2", "T" in "RH":
```
POST /devices HTTP/1.1
Host: api.zrak.janvr.wtf
Content-Type: application/json
Authorization: Basic SmFuZXpOb3ZhazpnZXNsbzEyMw==

{
"device_name": "esp8266",
"device_location": "Jupiter",
"variables": ["CO2", "T", "RH"]
}
```
Če je bila obdelava zahtevka uspešna sledi odgovor s kodo 200:
```
{
    "id": 10,
    "location": "Jupiter",
    "name": "esp8266",
    "time_created": "2020-02-23 18:03:06",
    "user_id": 6,
    "var0": "CO2",
    "var1": "T",
    "var2": "RH",
    "var3": null,
    "var4": null,
    "var5": null,
    "var6": null,
    "var7": null,
    "var8": null,
    "var9": null
}
```

#### GET - podatki o napravi
Z zahtevkom GET lahko pridobimo podatke o vseh napravah, ki pripadajo uporabniku.

Primer zahtevka:
```
GET /devices HTTP/1.1
Host: api.zrak.janvr.wtf
Authorization: Basic SmFuZXpOb3ZhazpnZXNsbzEyMw==
```

Primer odgovora:
```
{
    "0": {
        "id": 10,
        "location": "Jupiter",
        "name": "esp8266",
        "time_created": "2020-02-23 18:03:06",
        "user_id": 6,
        "var0": "CO2",
        "var1": "T",
        "var2": "RH",
        "var3": null,
        "var4": null,
        "var5": null,
        "var6": null,
        "var7": null,
        "var8": null,
        "var9": null
    },
    "1": {
        "id": 8,
        "location": "Jupiter",
        "name": "esp8267",
        "time_created": "2020-02-23 17:57:21",
        "user_id": 6,
        "var0": null,
        "var1": null,
        "var2": null,
        "var3": null,
        "var4": null,
        "var5": null,
        "var6": null,
        "var7": null,
        "var8": null,
        "var9": null
    }
}
```

Če želimo podatke o le eni izmed naprav lahko to dosežemo tako, da na konec naslova dodamo parameter device_id.\
Primer takšnega zahtevka:
```
GET /devices?device_id=10 HTTP/1.1
Host: api.zrak.janvr.wtf
Authorization: Basic SmFuZXpOb3ZhazpnZXNsbzEyMw==
```
V odgovoru je tokrat vsebovana le naprava z id=10:
```
{
    "id": 10,
    "location": "Jupiter",
    "name": "esp8266",
    "time_created": "2020-02-23 18:03:06",
    "user_id": 6,
    "var0": "CO2",
    "var1": "T",
    "var2": "RH",
    "var3": null,
    "var4": null,
    "var5": null,
    "var6": null,
    "var7": null,
    "var8": null,
    "var9": null
}
```
#### PUT - spreminjanje podatkov o napravi
Če želimo spremeniti podatke naprave lahko to storimo z zahtevkom PUT, ki je po obliki enak zahtevku za ustvarjanje nove naprave.\
Primer zahtevka:
```
PUT /devices?device_id=10 HTTP/1.1
Host: api.zrak.janvr.wtf
Content-Type: application/json
Authorization: Basic SmFuZXpOb3ZhazpnZXNsbzEyMw==

{"device_name": "esp32",
"device_location": "Saturn",
"variables": ["NO2", "SO2"]}
```
Če je bila obdelava zahtevka uspešna bo strežnik odgovoril z posodobljenimi podatki.\
Odgovor na zgornji zahtevek
```
{
    "id": 10,
    "location": "Saturn",
    "name": "esp32",
    "time_created": "2020-02-23 18:03:06",
    "user_id": 6,
    "var0": "NO2",
    "var1": "SO2",
    "var2": null,
    "var3": null,
    "var4": null,
    "var5": null,
    "var6": null,
    "var7": null,
    "var8": null,
    "var9": null
}
```

#### DELETE - izbris naprave
Napravo lahko izbrišemo z zahtevkom DELETE. Pri tem moramo v url naslov dodati tudi parameter device_id, ki določa katero napravo želimo izbrisati.\
Primer zahtevka z izbris naprave z id=8:
```
DELETE /devices?device_id=8 HTTP/1.1
Host: api.zrak.janvr.wtf
Authorization: Basic SmFuZXpOb3ZhazpnZXNsbzEyMw==
```
Odgovor strežnika:
```
Success: Device 'esp8267' deleted for user 'JanezNovak'
```
----
### ```/measurements``` API - manipulacija z meritvami

#### POST - nova meritev
Novo meritev lahko na strežnik pošlejmo z zahtevkom POST. Napravo kateri poslana meritev pripada določimo tako, da v url naslov dodamo ali parameter device_id ali pa device_name. V primeru, da sta prisotna oba paremetra se bo uporabil device_id.\
Primer zahtevka za napravo z imenom "esp8266" in spremenljivkama "CO2" in "T":
```
POST /measurements?device_name=esp8266 HTTP/1.1
Host: api.zrak.janvr.wtf
Content-Type: application/json
Authorization: Basic SmFuZXpOb3ZhazpnZXNsbzEyMw==

{"CO2": 912,
"T": 23}
```
Ob uspešni obdelavi je odgovor sledeč:
```
{
    "CO2": 912.0,
    "T": 23.0,
    "dev_id": 10,
    "id": 25,
    "time": "2020-02-23 18:52:43"
}
```
V meritvi lahko posamezene spremenljivke tudi izpustimo.

#### GET - podatki meritev
Podatke o meritvah za posamezno napravo dobimo z zahtevkom GET. Napravo, ki ji meritve pripadajo lahko določimo z uporabo url parametra device_id ali pa device_name. Dodatno lahko uporabimo tudi parametre lim (maksimalno število meritev, ki naj jih strežnik vrne), start (začetni čas) in stop (končni čas).

Primer zahtevka:
```
GET /measurements?device_id=10 HTTP/1.1
Host: api.zrak.janvr.wtf
Authorization: Basic SmFuZXpOb3ZhazpnZXNsbzEyMw==
```
In odgovor strežnika:
```
{
    "0": {
        "CO2": 793.0,
        "T": 24.2,
        "dev_id": 10,
        "id": 30,
        "time": "2020-02-23 19:08:17"
    },
    "1": {
        "CO2": 783.0,
        "T": 24.0,
        "dev_id": 10,
        "id": 29,
        "time": "2020-02-23 19:08:07"
    },
    "2": {
        "CO2": null,
        "T": null,
        "dev_id": 10,
        "id": 28,
        "time": "2020-02-23 19:03:26"
    },
    "3": {
        "CO2": 912.0,
        "T": 23.0,
        "dev_id": 10,
        "id": 25,
        "time": "2020-02-23 18:52:43"
    }
}
```
Meritve so v odgovoru urejene od najnovejše do najstarejše. Število meritev lahko omejimo z uporabo url parametra lim (npr. v naslov dodamo ?lim=2 in tako prejmemo le prvi dve meritvi).\
Če želimo meritve iz nekega časovnega intervala lahko to dosežemo z uporabo url paremtrov start in stop. Oba parametra morata vsebovati UTC datum in uro v obliki YYYYMMDDTHHmmss.\
Primer zahtevka, ki vrne meritve v času od 23.02.2020 19:00:00 do 23.02.2020 19:08:10:
```
GET /measurements?device_name=esp8266&start=20200223T190000&stop=20200223T190810 HTTP/1.1
Host: api.zrak.janvr.wtf
Authorization: Basic SmFuZXpOb3ZhazpnZXNsbzEyMw==
```
Odgovor strežnika:
```
{
    "0": {
        "CO2": 783.0,
        "T": 24.0,
        "dev_id": 10,
        "id": 29,
        "time": "2020-02-23 19:08:07"
    },
    "1": {
        "CO2": null,
        "T": null,
        "dev_id": 10,
        "id": 28,
        "time": "2020-02-23 19:03:26"
    }
}
```

#### DELETE - izbris meritev
Posamezno meritev lahko izbrišemo z zahtevkom DELETE in url parametrom measurement_id.\
Primer zahtevka:
```
DELETE /measurements?device_name=esp8266&measurement_id=25 HTTP/1.1
Host: api.zrak.janvr.wtf
Authorization: Basic SmFuZXpOb3ZhazpnZXNsbzEyMw==
```
Odgovor strežnika:
```
Success: Measurement successfully deleted for device 'esp8266', user 'JanezNovak'
```

Če želimo izbrisati vse meritve na nekem časovnem intervalu lahko to dosežemo z url parametroma start in stop v isti obliki kot je opisano v poglavju zahtevka GET.


### Screenshots
Posnetki zaslona admin vmesnika:\
![Pregled uporabnikov](./screenshots/users.png)
![Pregled naprav](./screenshots/devices.png)

Struktura podatkovne baze:\
![SQL](./screenshots/sql.png)