# skill-test: wpływ skilli na wydajność agenta

Test porównuje sposoby podania agentowi tej samej wiedzy proceduralnej:

| | Wariant A | Wariant B |
|---|---|---|
| Framework | LangChain `create_agent` (zwykły agent z function calling) | LangChain **deepagents** `create_deep_agent` |
| Wiedza o 80 procedurach | wszystkie 80 opisów w jednym system prompcie | 80 skilli (`SKILL.md`), agent widzi tylko nazwy i opisy, pełną treść czyta `read_file` na żądanie |
| System prompt | nagłówek + 80 procedur (~200 tys. znaków, ok. 50 tys. tokenów) | ten sam nagłówek + jedno zdanie o skillach (+ lista skilli dodawana przez deepagents) |
| Tool | `credit_analysis_engine` (identyczny, stub, stałe ~20 ms) | `credit_analysis_engine` (identyczny) + wbudowane narzędzia deepagents |
| Prompt usera | identyczny | identyczny |
| Model | `claude-haiku-5-5` | `claude-haiku-5-5` |
| Prompt caching | `AnthropicPromptCachingMiddleware` | to samo (deepagents dodaje je automatycznie) |

Wariant **C (B-min)** to te same skille bez harnessu deepagents: zwykły
`create_agent` z `SkillsMiddleware` i `FilesystemMiddleware` ograniczonym do jednego
narzędzia `read_file` (bez ls, write_file, edit_file, delete, glob, grep i task).
Mierzy czysty efekt skilli bez narzutu frameworka.

## Domena: analiza wniosków kredytowych

Agent dostaje kompletny wniosek kredytowy i ma wywołać **dokładnie raz** funkcję
`credit_analysis_engine` z argumentami przygotowanymi według właściwej procedury.
Procedur jest 80 = stan cywilny (singiel / małżeństwo) × produkt (auto / dom /
kredyt obrotowy / gotówkowy) × kwota (do 50 000 PLN / powyżej) × zatrudnienie
(umowa o pracę / działalność / umowa zlecenie / emeryt / dochód w EUR z zagranicy).
16 procedur bazowych definiuje reguły liczenia dochodu (premie, dochód małżonka),
kosztów utrzymania, zobowiązań (limity kart), limity DTI/LTV, stress test,
zabezpieczenie, model scoringowy, dokumenty i weryfikacje. Typ zatrudnienia je
modyfikuje (haircut dochodu, premie, przeliczenie EUR, dokumenty, weryfikacje,
model scoringowy). Do tego każda procedura ma drobne, deterministyczne korekty
limitu DTI i kosztów utrzymania, więc liczb jednej procedury nie da się
wywnioskować z sąsiednich i agent musi przeczytać właściwą. Opisy mają ok.
310–430 słów (ok. 450–650 tokenów) i są w [`skilltest/skills/*/SKILL.md`](skilltest/skills).

Parametry procedur są w jednym miejscu, [`skilltest/procedures.py`](skilltest/procedures.py).
Z niego generowane są zarówno pliki `SKILL.md` (`python -m skilltest.render_skills`),
jak i klucz odpowiedzi do oceny. Wariant A składa system prompt z tych samych plików
(bez frontmattera), więc merytoryka jest identyczna.

Przypadki testowe są losowane ([`skilltest/cases.py`](skilltest/cases.py)): w każdym
powtórzeniu losowane jest 15 różnych procedur z 80 i dla każdej generowany jest
kompletny wniosek. Wszystkie warianty w danym powtórzeniu dostają identyczne wnioski.
Seed jest zapisany w `meta.json`, a wylosowane wnioski w `cases_rep<N>.json`.
Prompt nie mówi, która procedura obowiązuje. Wnioski zawierają dane, które
procedura każe zignorować (premia osoby na działalności lub emeryta, cena auta przy
kredycie gotówkowym, oszczędności bez zastawu), a 15% małych kwot to dokładnie
50 000 PLN (to jeszcze „mała”).

## Co jest mierzone (na każde zadanie)

- **trafność**: czy wszystkie 14 argumentów wywołania toola zgadza się z kluczem
  (liczby z tolerancją 0,5% lub 1 PLN), czy wybrano właściwą procedurę, liczba
  poprawnych pól, najczęściej mylone pola;
- **„wołanie jeden raz”**: ile razy tool faktycznie się wykonał (`engine_calls`), flaga `engine_called_once`;
- **tokeny**: IN bez cache, zapis do cache, odczyt z cache, OUT (z pola `usage` API Anthropic), sumy na zadanie i per wywołanie modelu;
- **liczba wywołań modelu** na zadanie, sekwencja narzędzi (np. `read_file → credit_analysis_engine`);
- **czas**: całego zadania (wall clock) i samych wywołań modelu;
- **koszt** w USD wg cennika Haiku 5.5 ($0,10 / $0,50 za 1M, zapis cache ×1,25, odczyt ×0,1);
- w wariancie B: czy agent przeczytał właściwy skill i ile plików przeczytał.

Surowe dane trafiają do `results/<znacznik czasu>/runs.jsonl` (rekord na zadanie,
zapisywany od razu), podsumowanie do `summary.csv` i `REPORT.md`.

## Uruchomienie

Windows (PowerShell), w `c:\ai\skilltest`:

```powershell
python -m venv .venv          # Python 3.11+
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # wpisz ANTHROPIC_API_KEY albo ustaw zmienną środowiskową
python -m pytest -q tests   # testy offline, bez klucza
python -m skilltest.run_benchmark --runs 3 --cases-per-run 15
python -m skilltest.analyze results\<katalog z poprzedniego kroku>
```

Linux/macOS analogicznie (`python3 -m venv .venv && . .venv/bin/activate`).

Opcje `run_benchmark`: `--runs N`, `--cases-per-run 15`, `--seed N`,
`--variants A B C`, `--model claude-haiku-5-5`, `--effort low|medium|high`,
`--dry-run` (skryptowany model bez API, tylko do sprawdzenia pipeline'u; tokeny
w nim to szacunki).

Pełny przebieg to 3 × 15 × 3 warianty = 135 zadań, ok. 360 wywołań modelu.

### Model lokalny

- Ollama: `pip install langchain-ollama`, potem
  `python -m skilltest.run_benchmark --model ollama:<nazwa modelu> --num-ctx 131072`.
  `--num-ctx` jest ważne: Ollama domyślnie ma małe okno kontekstu i po cichu
  ucina prompt, a prompt wariantu A ma ok. 50 tys. tokenów.
- Serwer zgodny z OpenAI (LM Studio, vLLM, llama.cpp): `pip install langchain-openai`,
  ustaw `OPENAI_BASE_URL` (np. `http://localhost:1234/v1`) i `OPENAI_API_KEY`
  (dowolny), potem `--model openai:<nazwa modelu>`.
- Kolumny cache i koszt w USD dotyczą tylko API Anthropic.

## Kolejność i cache

Zadania idą sekwencyjnie: powtórzenie → przypadek → wariant (A, B, C).
Prefiks (tools + system prompt) jest stały w obrębie wariantu, więc po pierwszym
zadaniu oba warianty czytają go z cache. Tabela „według powtórzenia” w raporcie
pokazuje, ile daje cache.

## Struktura

```
skilltest/
  procedures.py      80 procedur: parametry + oczekiwane argumenty
  render_skills.py   generuje skills/*/SKILL.md
  skills/            80 skilli (wariant B) = treść system promptu wariantu A
  engine.py          tool credit_analysis_engine (deterministyczny) + log wywołań
  cases.py           losowanie i generowanie wniosków testowych
  prompts.py         system prompty A i B
  agents.py          budowa agentów A (create_agent) i B (create_deep_agent)
  metrics.py         zbieranie tokenów/czasu i ocena argumentów
  run_benchmark.py   uruchomienie testu
  analyze.py         raport
  fake_model.py      skryptowany model do --dry-run i testów
tests/test_offline.py
```
