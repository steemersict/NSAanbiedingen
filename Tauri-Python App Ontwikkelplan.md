# **Architecturale Blauwdruk en Implementatiestrategie voor Hybride Desktopapplicaties: Een Integratie van Tauri v2, Astro en Python WeasyPrint**

## **Management Samenvatting**

De moderne softwareontwikkeling voor desktopomgevingen bevindt zich op een kantelpunt. De traditionele hegemonie van Electron-gebaseerde applicaties wordt uitgedaagd door efficiëntere, veiligere en modulaire architecturen zoals Tauri. Dit rapport biedt een exhaustieve technische analyse en een gedetailleerd implementatieplan voor het ontwikkelen van een applicatie voor het genereren van aanbiedingenfolders. De gekozen technologische stack—Tauri v2 voor de systeemlaag, Astro voor de frontend-presentatie, en een Python-sidecar met FastAPI en WeasyPrint voor de render-engine—vertegenwoordigt een 'best-of-breed' benadering. Hierbij wordt de reactiviteit van moderne webframeworks gecombineerd met de brute rekenkracht en bibliotheek-ecosystemen van Python.  
Dit document is specifiek opgesteld om te dienen als leidraad voor het gebruik van "Claude Code", een geavanceerde AI-coding assistent. Het beschrijft niet alleen de technische specificaties, maar definieert ook de contextuele kaders, prompt-strategieën en architecturale beslissingen die nodig zijn om de AI effectief aan te sturen. Van de complexe 'DLL-hel' bij het bundelen van GTK-afhankelijkheden op Windows tot de granulaire permissiestructuren van de nieuwe Tauri v2 beveiligingslaag; elk facet wordt diepgaand behandeld.

## **1\. Architecturale Fundamenten en Ontwerppatronen**

### **1.1 De Evolutie naar het Hybride Sidecar-Model**

De overgang van monolithische desktopframeworks naar modulaire systemen vereist een fundamenteel andere kijk op inter-proces communicatie (IPC) en resource-management. Waar Electron een volledige Node.js runtime en Chromium browser bundelt, leunt Tauri op de webview van het besturingssysteem (WebView2 op Windows, WebKit op macOS en Linux). Dit resulteert in drastisch kleinere binaire bestanden en een lager geheugenverbruik. Echter, deze slankheid introduceert een complexiteit: de afwezigheid van een ingebouwde zware backend-runtime zoals Node.js of Python.2  
Om de vereiste functionaliteit voor het genereren van professionele PDF-documenten te realiseren, is gekozen voor het "Sidecar Pattern". Hierbij fungeert de Tauri-applicatie (geschreven in Rust) als de orchestrator die een extern binaire bestand (de Python executable) beheert. Dit is geen triviale toevoeging, maar een architecturale kernbeslissing die de stabiliteit van de applicatie bepaalt. In tegenstelling tot een geïntegreerde bibliotheek, draait de sidecar in zijn eigen geheugenruimte. Dit biedt isolatie—een crash in de PDF-generator trekt de gebruikersinterface niet mee de afgrond in—maar vereist een robuust communicatieprotocol.

### **1.2 IPC-Strategie: De Keuze voor de Localhost API**

Er zijn twee dominante methoden voor communicatie tussen de Rust-core en de Python-sidecar: standaard input/output (stdio) en netwerk sockets (localhost). Voor dit specifieke project, waarbij grote datasets (afbeeldingen, complexe lay-outstructuren) en binaire datastromen (de gegenereerde PDF) worden uitgewisseld, is stdio suboptimaal. Stdio is stream-gebaseerd, blokkerend en vereist complexe serialisatie/deserialisatie logica om framing-fouten te voorkomen.  
De analyse wijst uit dat de **Localhost API-benadering** superieur is. Hierbij start de Python-sidecar een FastAPI-server op een lokale poort. De frontend (Astro) communiceert direct met deze API via standaard HTTP-verzoeken.

| Feature | Stdio (JSON-RPC) | Localhost HTTP (FastAPI) |
| :---- | :---- | :---- |
| **Complexiteit** | Hoog (Custom framing nodig) | Laag (Standaard HTTP) |
| **Performance** | Goed voor kleine berichten | Uitstekend voor binaire stromen (Blobs) |
| **Debuggen** | Moeilijk (onzichtbare streams) | Eenvoudig (via browser/Postman/Curl) |
| **Concurrency** | Sequentieel (standaard) | Asynchroon (via ASGI/Uvicorn) |
| **Beveiliging** | Impliciet geïsoleerd | Vereist authenticatie-tokens |

Zoals tabel 1 illustreert, biedt de HTTP-aanpak aanzienlijke voordelen voor debugging en verwerking van binaire bestanden. De frontend kan gebruikmaken van de browser-native fetch API, inclusief streaming responses en upload voortgangsindicatoren, wat essentieel is voor de gebruikerservaring bij het genereren van zware PDF-bestanden.3

### **1.3 De Rol van Astro en WeasyPrint**

De keuze voor Astro als frontend-framework is strategisch. Astro's "Island Architecture" maakt het mogelijk om interactieve componenten (zoals de drag-and-drop editor voor de folder) te bouwen met React of Vue, terwijl de rest van de applicatie statische HTML blijft. Dit minimaliseert de JavaScript-payload. Nog belangrijker is dat Astro uitstekend geschikt is voor het genereren van de HTML-templates die WeasyPrint zal consumeren. Omdat WeasyPrint een "headless browser" is die HTML/CSS naar PDF vertaalt, kan Astro dienen als de *single source of truth* voor zowel de preview op het scherm als de uiteindelijke print-output.4  
WeasyPrint onderscheidt zich van browser-gebaseerde converters (zoals Puppeteer) door zijn ondersteuning voor de Paged Media specificaties van CSS3. Dit is cruciaal voor "aanbiedingenfolders" die vaak specifieke eisen hebben qua paginamarges, afloop (bleed), en kleurprofielen (CMYK). Waar browsers geoptimaliseerd zijn voor continu scrollen, is WeasyPrint geoptimaliseerd voor paginering.6

## ---

**2\. De Ontwikkelomgeving en Claude Code Strategie**

Het succes van dit project hangt af van een strikte context-engineering voor Claude Code. Omdat Tauri v2 en de specifieke sidecar-configuraties complex zijn en snel evolueren, moet de AI voorzien worden van een rigide kader.

### **2.1 Context Engineering: Het CLAUDE.md Bestand**

Om hallucinaties te voorkomen en de AI te dwingen zich aan de v2-specificaties te houden, dient er een CLAUDE.md bestand in de root van het project te worden geplaatst. Dit fungeert als een permanente "systeemprompt" voor de CLI.8  
**Aanbevolen Structuur voor CLAUDE.md:**

# **CLAUDE.md \- Project Context & Guidelines**

## **Project Identity**

* **Type:** Desktop Application (Tauri v2)  
* **Frontend:** Astro (React integration), TailwindCSS  
* **Backend:** Python 3.11+, FastAPI, WeasyPrint, PyInstaller  
* **Core:** Rust (Tauri v2)

## **Architectural Constraints (CRITICAL)**

1. **Tauri v2 Migration:** Gebruik NOOIT v1 configuraties (tauri.conf.json allowlist is deprecated). Gebruik src-tauri/capabilities en ACLs.  
2. **Sidecar Pattern:** Python draait als een gecompileerde executable.  
3. **Port Discovery:** Python bindt aan poort 0 (random free port) en print deze naar stdout. Rust vangt dit af.  
4. **Binary Naming:** Binaries moeten de target-triple bevatten (b.v. main-x86\_64-pc-windows-msvc.exe).

## **Code Style**

* **Python:** Type hints (PEP 484), Pydantic models, Black formatting.  
* **Rust:** Idiomatisch Rust, gebruik thiserror voor foutafhandeling.  
* **Frontend:** TypeScript strict mode, Nano Stores voor state management.

## **Workflow**

* **Plan Mode:** Voor elke complexe taak, maak eerst een plan.md.  
* **Test:** Schrijf unit tests voor de Python PDF-generatie logic.

Deze context dwingt Claude Code om de "Context → Thought → Action → Observation" cyclus effectief toe te passen en voorkomt dat het terugvalt op verouderde Tauri v1 documentatie.10

### **2.2 Fasering van de Implementatie**

De implementatie via Claude Code dient in strikte fasen te verlopen. De gebruiker moet de AI instrueren om niet alles tegelijk te genereren, maar de componenten laag voor laag op te bouwen.

1. **Fase 1: Backend Core.** Het opzetten van de Python logica en PDF-generatie onafhankelijk van Tauri.  
2. **Fase 2: Bundeling.** Het succesvol compileren van de Python code met PyInstaller, inclusief alle GTK-afhankelijkheden.  
3. **Fase 3: Rust Integratie.** Het opzetten van de Tauri sidecar lifecycle management.  
4. **Fase 4: Frontend Connectie.** De integratie van Astro met de backend via de localhost API.

## ---

**3\. Diepte-analyse: Backend Implementatie (Python)**

De Python-backend is de motor van de applicatie. Hier vinden de zware berekeningen plaats. De integratie van FastAPI en WeasyPrint in een context zonder console vereist specifieke aanpassingen.

### **3.1 Dynamische Poorttoewijzing en Concurrency**

Een veelvoorkomende fout bij sidecar-implementaties is het hardcoden van poortnummers (bijv. 8000). Dit leidt onvermijdelijk tot conflicten als de gebruiker de applicatie twee keer opent of als de poort al in gebruik is.11 De oplossing ligt op het niveau van de OS-kernel: binden aan poort 0\. Wanneer een socket bindt aan poort 0, wijst het besturingssysteem een vrije, ephemerale poort toe.  
Implementatie-detail voor Claude Code:  
De Python server moet als volgt worden geïnstrueerd:

1. Creëer een socket, bind aan ('127.0.0.1', 0).  
2. Lees het toegewezen poortnummer uit met sock.getsockname()\[1\].  
3. Sluit de socket (zodat de poort weer vrijkomt, maar direct daarna door Uvicorn gebruikt kan worden—let op: er is een kleine race condition mogelijk, maar in de praktijk verwaarloosbaar op lokale machines, of beter: laat Uvicorn de socket file descriptor overnemen).  
4. Print een uniek herkenningspatroon naar stdout, bijvoorbeeld SERVER\_PORT=12345.  
5. Start de Uvicorn server op die poort.12

**Code Snippet voor de Prompt:**

Python

\# Instrueer Claude om dit patroon te gebruiken:  
sock \= socket.socket(socket.AF\_INET, socket.SOCK\_STREAM)  
sock.bind(('127.0.0.1', 0))  
port \= sock.getsockname()\[1\]  
sock.close()  
print(f"SERVER\_PORT={port}", flush=True) \# Flush is cruciaal voor realtime detectie in Rust  
uvicorn.run(app, port=port)

### **3.2 WeasyPrint en de "DLL Hel"**

WeasyPrint is afhankelijk van GObject-bibliotheken (Pango, Cairo, GDK-Pixbuf). Deze zijn geschreven in C en worden via CFFI (C Foreign Function Interface) aangeroepen. PyInstaller, de tool om Python te compileren naar een .exe, detecteert deze afhankelijkheden vaak niet automatisch omdat de imports dynamisch zijn.14  
Strategie voor Windows:  
Op Windows is dit het meest problematisch. De GTK3 runtime moet aanwezig zijn. Er zijn twee strategieën:

1. **System-wide installatie:** De gebruiker moet GTK3 installeren. Dit druist in tegen het principe van een "standalone" applicatie.  
2. **Bundeling (Aanbevolen):** De DLL's moeten worden meegeleverd in de \_internal map van de applicatie.

Instructie voor Claude Code:  
Genereer een hook-weasyprint.py voor PyInstaller. Deze hook moet:

* De locatie van de GTK3 DLL's op het bouwsysteem identificeren.  
* Deze DLL's toevoegen aan de binaries lijst in de PyInstaller spec-file.  
* weasyprint en cairocffi toevoegen aan hiddenimports.

Daarnaast moet de Python-code bij het opstarten de PATH omgevingsvariabele aanpassen om de interne \_internal directory toe te voegen, zodat CFFI de DLL's kan vinden.

### **3.3 Asynchrone Taakverwerking**

Het genereren van een PDF met hoge resolutie afbeeldingen kan seconden tot minuten duren. Een synchroon HTTP-verzoek zou de verbinding kunnen doen time-outen. FastAPI biedt BackgroundTasks, maar voor een desktop-app is een eenvoudige aanpak vaak beter:

* **Endpoint 1:** POST /generate \-\> Start het proces, retourneert direct een job\_id.  
* **Endpoint 2:** GET /status/{job\_id} \-\> Polling door de frontend (Progressie).  
* **Endpoint 3:** GET /download/{job\_id} \-\> Haalt het resultaat op.

Gezien de single-user aard van een desktop-app, kan men er ook voor kiezen om het verzoek open te houden (long-polling) als de generatietijd binnen de 30 seconden blijft. Voor "aanbiedingenfolders" met veel pagina's is de job-queue benadering robuuster.15

## ---

**4\. Core Implementatie: Rust en Tauri v2**

De migratie naar Tauri v2 introduceert een strikt beveiligingsmodel gebaseerd op Access Control Lists (ACLs). Dit is een breuk met het allowlist model van v1.

### **4.1 Configuratie van de tauri.conf.json**

In v2 wordt de configuratie verspreid. De tauri.conf.json definieert de basis, maar de permissies staan in capabilities.

JSON

// src-tauri/tauri.conf.json  
{  
  "bundle": {  
    "active": true,  
    "targets": "all",  
    "externalBin": \[  
      "binaries/backend" // Let op: GEEN target-triple hier\!  
    \]  
  },  
  "plugins": {  
    "shell": {  
      "active": true // De shell plugin is niet meer standaard actief  
    }  
  }  
}

Het is cruciaal om te begrijpen dat externalBin verwijst naar de *basisnaam*. Tauri zoekt tijdens de build en runtime automatisch naar backend-x86\_64-pc-windows-msvc.exe (op Windows 64-bit).2

### **4.2 Beveiligingslaag: Capabilities en ACLs**

Om de sidecar te mogen starten, moet er een expliciete capability gedefinieerd worden. Zonder dit zal de Command::new\_sidecar aanroep falen met een permissiefout.  
**Bestand: src-tauri/capabilities/sidecar.json**

JSON

{  
  "identifier": "sidecar-capability",  
  "description": "Permissies voor de Python backend",  
  "windows": \["main"\],  
  "permissions":  
    }  
  \]  
}

Dit JSON-bestand vertelt Tauri dat het hoofdvenster ("main") het recht heeft om de binary "backend" uit te voeren. Dit fijnmazige model voorkomt dat, in het geval van een XSS-kwetsbaarheid in de frontend, malafide JavaScript willekeurige commando's kan uitvoeren.2

### **4.3 Lifecycle Management in Rust**

De Rust-code fungeert als de procesbeheerder. Het moet de sidecar starten, de poort uitlezen en zorgen voor een nette afsluiting.  
Technische Uitdaging: Weesprocessen (Zombie Processes)  
Als de Tauri-applicatie hard wordt afgesloten (bijv. via Taakbeheer), blijft de Python sidecar vaak draaien. Tauri v2 heeft betere procesgroep-beheer dan v1, maar het is verstandig om in Rust de CommandChild structuur te beheren.  
**Implementatieplan voor Rust (lib.rs):**

1. Gebruik tauri\_plugin\_shell::ShellExt om toegang te krijgen tot de shell functionaliteit.  
2. Start het proces en ontvang de Receiver voor stdout.  
3. Start een async taak die de stdout regels leest.  
4. Zodra de regel "SERVER\_PORT=..." wordt gedetecteerd:  
   * Parse het nummer.  
   * Sla dit op in de tauri::State (thread-safe opslag).  
   * Verstuur een event backend-ready naar de frontend.20

Rust

// Conceptuele Rust code voor de event loop  
while let Some(event) \= rx.recv().await {  
    if let CommandEvent::Stdout(line) \= event {  
        let text \= String::from\_utf8\_lossy(\&line);  
        if text.contains("SERVER\_PORT=") {  
            // Logica om poort te extracten en event te emitten  
            app\_handle.emit("backend-ready", port\_number).unwrap();  
        }  
    }  
}

## ---

**5\. Frontend Architectuur: Astro en State Management**

Astro staat bekend als een Static Site Generator (SSG), maar in deze context gebruiken we het als een hybride framework. De "aanbiedingenfolder" editor vereist zware client-side interactie, terwijl de previews statisch gegenereerd kunnen worden.

### **5.1 Projectstructuur en Routing**

In een Tauri-context is er geen server die HTML rendert; alles wordt geserveerd vanuit lokale bestanden. Astro moet geconfigureerd worden met output: 'static' en build.format: 'file'.  
**Componentenstructuur:**

* **Editor:** Een interactief React/Vue eiland (client:only). Hier sleept de gebruiker producten naar de pagina.  
* **Preview:** Een component dat de JSON-status van de folder vertaalt naar pure HTML/CSS die overeenkomt met wat WeasyPrint verwacht.

### **5.2 Communicatie met de Backend**

De frontend moet wachten tot de backend klaar is. Dit vereist een reactieve state store. **Nano Stores** is hiervoor ideaal omdat het framework-agnostisch is en buiten de React-tree kan functioneren (handig voor de Tauri event listeners).  
**De "Handshake" Flow:**

1. App start. Astro toont een "Initialiseren..." scherm.  
2. Astro roept via Tauri's invoke systeem een commando start\_server aan in Rust.  
3. Rust start Python, wacht op de poort, en stuurt een event backend-ready.  
4. Astro luistert naar dit event (listen('backend-ready',...)).  
5. Astro slaat de poort en een authenticatie-token op in de Nano Store.  
6. De UI switcht naar de editor.  
7. Alle volgende requests gaan via fetch('http://localhost:${port}/...').

### **5.3 PDF-Export Workflow**

Wanneer de gebruiker op "Exporteer" klikt:

1. De huidige state van de folder wordt geserialiseerd naar JSON.  
2. Astro stuurt een POST request met deze JSON naar de Python backend.  
3. De backend genereert de PDF en retourneert deze als een binaire stream.  
4. Astro ontvangt de Blob.  
5. Astro gebruikt de tauri-plugin-dialog om de gebruiker een opslaglocatie te laten kiezen.  
6. Astro gebruikt de tauri-plugin-fs om de Blob naar schijf te schrijven. Dit omzeilt de browser-download dialoog en biedt een native ervaring.23

## ---

**6\. Build en Distributie Strategie**

Het bouwen van een hybride applicatie vereist een georkestreerde build-pijplijn.

### **6.1 PyInstaller en Target Triples**

Tauri verwacht dat de sidecar binaries een specifieke naamgeving volgen die de architectuur van het systeem weerspiegelt (de "target triple"), bijvoorbeeld x86\_64-pc-windows-msvc. PyInstaller genereert echter gewoon main.exe.  
Er is een script nodig dat draait *tussen* de Python build en de Tauri build.  
Script: scripts/rename-sidecar.js  
Dit Node.js script moet:

1. De huidige Rust target triple detecteren (rustc \-vV).  
2. De binary in de dist/ map van PyInstaller lokaliseren.  
3. De binary hernoemen met de triple suffix en verplaatsen naar src-tauri/binaries/.2

### **6.2 CI/CD Integratie**

Voor een reproduceerbare build, met name vanwege de native dependencies van WeasyPrint, is het aan te raden om GitHub Actions te gebruiken met matrix builds voor Windows, MacOS en Linux. Het bouwen van de Windows-versie op een Linux-machine (cross-compilatie) is voor Python/GTK applicaties uiterst complex en foutgevoelig (Wine is vaak instabiel voor dit doel). Het advies is om native runners te gebruiken.

## ---

**Conclusie en Aanbevelingen**

De implementatie van een desktopapplicatie voor het genereren van aanbiedingenfolders met Tauri v2, Astro en Python is een ambitieus maar technisch superieur alternatief voor traditionele methoden. De architectuur biedt de perfecte balans tussen ontwikkelgemak (Astro/HTML/CSS voor lay-out), kracht (Python/WeasyPrint voor PDF-rendering) en performance (Rust/Tauri voor de runtime).  
De kritieke succesfactoren voor dit project zijn:

1. **Strikte Context Engineering:** Gebruik CLAUDE.md om de AI binnen de lijnen van Tauri v2 te houden.  
2. **Robuuste Sidecar Lifecycle:** Zorg dat het starten en stoppen van de Python-processen feilloos wordt afgehandeld om "zombies" te voorkomen.  
3. **Correcte Bundeling:** Besteed extra aandacht aan de PyInstaller-configuratie voor GTK-afhankelijkheden.

Door het volgen van dit stappenplan en het hanteren van de beschreven architecturale patronen, kan een schaalbare, onderhoudbare en performante applicatie worden gerealiseerd die voldoet aan de hoge eisen van grafische productie.

### **Stappenplan voor Claude Code (Samenvattend)**

1. **Initialisatie:** npm create tauri-app@latest (kies Astro). Maak CLAUDE.md.  
2. **Backend Proto:** Schrijf backend/server.py met poort 0 binding. Test los van Tauri.  
3. **Backend Build:** Configureer PyInstaller (backend.spec) en maak het rename-script.  
4. **Tauri Core:** Implementeer lib.rs voor sidecar spawning en event emission. Configureer capabilities.  
5. **Frontend:** Bouw de Astro UI en de fetch logica naar de dynamische poort.  
6. **Integratie:** Test de volledige loop van klik tot PDF.

2

#### **Geciteerd werk**

1. Embedding External Binaries \- Tauri, geopend op december 9, 2025, [https://v2.tauri.app/develop/sidecar/](https://v2.tauri.app/develop/sidecar/)  
2. dieharders/example-tauri-v2-python-server-sidecar: An ... \- GitHub, geopend op december 9, 2025, [https://github.com/dieharders/example-tauri-v2-python-server-sidecar](https://github.com/dieharders/example-tauri-v2-python-server-sidecar)  
3. Build Modern, Print-Ready PDFs with Python, Flask & WeasyPrint \- Incentius Blog, geopend op december 9, 2025, [https://www.incentius.com/blog-posts/build-modern-print-ready-pdfs-with-python-flask-weasyprint/](https://www.incentius.com/blog-posts/build-modern-print-ready-pdfs-with-python-flask-weasyprint/)  
4. Add Integrations \- Astro Docs, geopend op december 9, 2025, [https://docs.astro.build/en/guides/integrations-guide/](https://docs.astro.build/en/guides/integrations-guide/)  
5. Common Use Cases \- WeasyPrint 67.0 documentation \- CourtBouillon, geopend op december 9, 2025, [https://doc.courtbouillon.org/weasyprint/stable/common\_use\_cases.html](https://doc.courtbouillon.org/weasyprint/stable/common_use_cases.html)  
6. WeasyPrint, geopend op december 9, 2025, [https://weasyprint.org/](https://weasyprint.org/)  
7. Writing a good CLAUDE.md | HumanLayer Blog, geopend op december 9, 2025, [https://www.humanlayer.dev/blog/writing-a-good-claude-md](https://www.humanlayer.dev/blog/writing-a-good-claude-md)  
8. Tell us your best practices for coding with Claude Code, geopend op december 9, 2025, [https://www.reddit.com/r/ClaudeAI/comments/1o98c8f/tell\_us\_your\_best\_practices\_for\_coding\_with/](https://www.reddit.com/r/ClaudeAI/comments/1o98c8f/tell_us_your_best_practices_for_coding_with/)  
9. Mastering Claude Code: A Developer’s Guide | by Mor Dvash | Israeli Tech Radar | Nov, 2025, geopend op december 9, 2025, [https://medium.com/israeli-tech-radar/mastering-claude-code-a-developers-guide-746a68363f4e](https://medium.com/israeli-tech-radar/mastering-claude-code-a-developers-guide-746a68363f4e)  
10. Tauri sidecar's capabilities and support \- Reddit, geopend op december 9, 2025, [https://www.reddit.com/r/tauri/comments/1in82rl/tauri\_sidecars\_capabilities\_and\_support/](https://www.reddit.com/r/tauri/comments/1in82rl/tauri_sidecars_capabilities_and_support/)  
11. python \- On localhost, how do I pick a free port number? \- Stack Overflow, geopend op december 9, 2025, [https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number](https://stackoverflow.com/questions/1365265/on-localhost-how-do-i-pick-a-free-port-number)  
12. What's the easiest way to find an unused local port? \- Unix & Linux Stack Exchange, geopend op december 9, 2025, [https://unix.stackexchange.com/questions/55913/whats-the-easiest-way-to-find-an-unused-local-port](https://unix.stackexchange.com/questions/55913/whats-the-easiest-way-to-find-an-unused-local-port)  
13. Writing a pandas Sidecar for Tauri \- MClare Blog, geopend op december 9, 2025, [https://mclare.blog/posts/writing-a-pandas-sidecar-for-tauri/](https://mclare.blog/posts/writing-a-pandas-sidecar-for-tauri/)  
14. Background Tasks \- FastAPI, geopend op december 9, 2025, [https://fastapi.tiangolo.com/tutorial/background-tasks/](https://fastapi.tiangolo.com/tutorial/background-tasks/)  
15. Background Tasks \- BackgroundTasks \- FastAPI, geopend op december 9, 2025, [https://fastapi.tiangolo.com/reference/background/](https://fastapi.tiangolo.com/reference/background/)  
16. Embedding External Binaries | Tauri v1, geopend op december 9, 2025, [https://tauri.app/v1/guides/building/sidecar/](https://tauri.app/v1/guides/building/sidecar/)  
17. Permissions \- Tauri, geopend op december 9, 2025, [https://v2.tauri.app/security/permissions/](https://v2.tauri.app/security/permissions/)  
18. Capabilities | Tauri, geopend op december 9, 2025, [https://v2.tauri.app/security/capabilities/](https://v2.tauri.app/security/capabilities/)  
19. how to use tauri app and python script as a back end \- Stack Overflow, geopend op december 9, 2025, [https://stackoverflow.com/questions/75913627/how-to-use-tauri-app-and-python-script-as-a-back-end](https://stackoverflow.com/questions/75913627/how-to-use-tauri-app-and-python-script-as-a-back-end)  
20. Calling Rust from the Frontend \- Tauri, geopend op december 9, 2025, [https://v2.tauri.app/develop/calling-rust/](https://v2.tauri.app/develop/calling-rust/)  
21. Emitting global event from Rust in Tauri \- Stack Overflow, geopend op december 9, 2025, [https://stackoverflow.com/questions/79246978/emitting-global-event-from-rust-in-tauri](https://stackoverflow.com/questions/79246978/emitting-global-event-from-rust-in-tauri)  
22. Features & Recipes \- Tauri, geopend op december 9, 2025, [https://v2.tauri.app/plugin/](https://v2.tauri.app/plugin/)  
23. Sidecar \- The Tauri Documentation WIP, geopend op december 9, 2025, [https://jonaskruckenberg.github.io/tauri-docs-wip/examples/sidecar.html](https://jonaskruckenberg.github.io/tauri-docs-wip/examples/sidecar.html)  
24. Configuration | Tauri v1, geopend op december 9, 2025, [https://tauri.app/v1/api/config/](https://tauri.app/v1/api/config/)