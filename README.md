# Proof of Concept (PoC) z opartym na AI systemem kategoryzacji i routingu wiadomości

Proof of Concept (PoC) mikroserwisowego systemu kategoryzacji i automatycznego routingu wiadomości e-mail wewnątrz firmy. Aplikacja analizuje treść wiadomości od użytkownika za pomocą lokalnego modelu LLM (Llama 3.2) i decyduje do jakiego działu powinno zostać przekierowane zgłoszenie, a następnie automatycznie wysyła e-mail przez lokalny serwer SMTP do odpowiedniego działu poprzez wywołanie narzędzia agenta (tool calling).

---

## Architektura i Wybory Technologiczne

1. **API Service (FastAPI + Pydantic-AI):**
   - **FastAPI:** Wybrane przez wsparcie łatwego tworzenia prostego API oraz automatyczne tworzenie interaktywnej dokumentacji Swagger UI (`/api/v1/docs`) oraz specyfikacji OpenAPI (`/api/v1/openapi.json`).
   - **Pydantic-AI:** Wybrany z uwagi na wsparcie Dependency Injection (`AgentDeps`), kontekst wykonania (`RunContext`) oraz bezpieczny Tool Calling (`@agent.tool`).
2. **Silnik LLM (Ollama + Llama 3.2):**
   - **Ollama:** Uruchomiona w kontenerze Docker.
   - **Llama 3.2 (3B):** Wybrano z uwagi na to, że jest to lekki, wydajny model, który można uruchomić w kontenerze. Posiada wsparcie dla Function/Tool Calling.
3. **Lokalny serwer SMTP (MailHog):**
   - Serwer SMTP przechwytujący wszystkie wysłane wiadomości e-mail. Wybrano ze względu na automatyczne udostępnianie panelu webowego ułatwiającego ręczną weryfikację odebranych wiadomości.

---

## Wymagania Przed Uruchomieniem

- Zainstalowany **Docker** oraz **Docker Compose**.

---

## Instrukcja Uruchomienia

1. Po pobraniu repozytorium należy przejść do katalogu głównego projektu (PoC):
   ```
   cd PoC
   ```

2. Następnie uruchomić całe środowisko za pomocą Docker Compose:
   ```
   docker compose up -d
   ```

3. **Pobieranie modelu :**
   Jeśli model `llama3.2` nie jest jeszcze wczytany w  Ollamie, pobierz go poleceniem:
   ```bash
   docker exec -it ollama ollama pull llama3.2
   ```

4. Po uruchomieniu dokumentacja i specyfikacja API dostępne są pod adresami:
   - **Interfejs Swagger UI (Dokumentacja API):** [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
   - **Specyfikacja OpenAPI (JSON):** [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

5. Panel webowy skrzynki MailHog dostępny będzie pod adresem:
   - [http://localhost:8025](http://localhost:8025)

---

## Testowanie (Przykładowe Zapytania)

Wyślij zapytanie POST na adres `http://localhost:8000/api/v1/route` z treścią zgłoszenia w formacie JSON.

### Wersja dla PowerShell:
```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/route" -Method Post -ContentType "application/json" -Body '{"email": "jan.kowalski@firma.pl", "message": "Dzień dobry, mam pytanie dotyczące mojej ostatniej wypłaty."}'
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/route" -Method Post -ContentType "application/json" -Body '{"email": "jan.kowalski@firma.pl", "message": "Dzień dobry, mam problem z komputerem."}'
```

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/route" -Method Post -ContentType "application/json" -Body '{"email": "jan.kowalski@firma.pl", "message": "Co muszę zrobić żeby dostać awans?"}'
```

### Wersja dla CMD:
```cmd
curl -X POST http://localhost:8000/api/v1/route -H "Content-Type: application/json" -d "{\"email\": \"jan.kowalski@firma.pl\", \"message\": \"Dzień dobry, mam problem z komputerem.\"}"
```

```cmd
curl -X POST http://localhost:8000/api/v1/route -H "Content-Type: application/json" -d "{\"email\": \"jan.kowalski@firma.pl\", \"message\": \"Dzień dobry, mam pytanie dotyczące mojej wypłaty.\"}"
```

```cmd
curl -X POST http://localhost:8000/api/v1/route -H "Content-Type: application/json" -d "{\"email\": \"jan.kowalski@firma.pl\", \"message\": \"Co muszę zrobić żeby dostać awans?\"}"
```


---

## Weryfikacja w MailHog

1. Otwórz w przeglądarce panel [http://localhost:8025](http://localhost:8025).
2. Widoczne będą wiadomości e-mail przekierowane do odpowiedniego działu.
3. Nagłówek `Reply-To` w szczegółach wiadomości wskazuje bezpośrednio adres nadawcy zgłoszenia.
