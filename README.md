# skill-test: wpływ skilli na wydajność agenta

Test porównuje dwa sposoby podania agentowi tej samej wiedzy proceduralnej:

| | Wariant A | Wariant B |
|---|---|---|
| Framework | LangChain `create_agent` (zwykły agent z function calling) | LangChain **deepagents** `create_deep_agent` |
| Wiedza o 12 procedurach | wszystkie 12 opisów w jednym system prompcie | 12 skilli (`SKILL.md`), agent widzi tylko nazwy i opisy, pełną treść czyta `read_file` na żądanie |
| System prompt | nagłówek + 12 procedur (~24 tys. znaków) | ten sam nagłówek + jedno zdanie o skillach (+ lista skilli dodawana przez deepagents) |
| Tool | `credit_analysis_engine` (identyczny, stub, min. 20 ms) | `credit_analysis_engine` (identyczny) + wbudowane narzędzia deepagents |
| Prompt usera | identyczny | identyczny |
| Model | `claude-haiku-5-5` | `claude-haiku-5-5` |
| Prompt caching | `AnthropicPromptCachingMiddleware` | to samo (deepagents dodaje je automatycznie) |

## Domena: analiza wniosków kredytowych

Agent dostaje kompletny wniosek kredytowy i ma wywołać **dokładnie raz** funkcję
`credit_analysis_engine` z argumentami przygotowanymi według właściwej procedury.
Procedur jest 12 = stan cywilny (singiel / małżeństwo) × produkt (auto / dom / kredyt
obrotowy) × kwota (do 50 000 PLN / powyżej 50 000 PLN). Każda procedura ma inne
reguły liczenia dochodu (premie, dochód małżonka), kosztów utrzymania, zobowiązań
(limity kart), inne limity DTI/LTV, stress test, zabezpieczenie, model scoringowy,
dokumenty i dodatkowe weryfikacje. Opisy mają ok. 300–350 słów (ok. 450–600 tokenów)
każdy i są w [`skilltest/skills/*/SKILL.md`](skilltest/skills).

Parametry procedur są w jednym miejscu, [`skilltest/procedures.py`](skilltest/procedures.py).
Z niego generowane są zarówno pliki `SKILL.md` (`python -m skilltest.render_skills`),
jak i klucz odpowiedzi do oceny, więc tekst czytany przez model i oczekiwane wartości
nie mogą się rozjechać. Wariant A składa system prompt z tych samych plików
(bez frontmattera), więc merytoryka jest identyczna.

12 przypadków testowych (po jednym na procedurę) jest w
[`skilltest/cases.py`](skilltest/cases.py). Prompt nie mówi, która procedura obowiązuje.
Kilka przypadków ma pułapki: kwota dokładnie 50 000 PLN (to jeszcze „mała”),
mały kredyt obrotowy dla małżeństwa (dochód i zobowiązania małżonka trzeba
zignorować, ale koszty utrzymania liczy się dla dwóch dorosłych).

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
python -m skilltest.run_benchmark --runs 3
python -m skilltest.analyze results\<katalog z poprzedniego kroku>
```

Linux/macOS analogicznie (`python3 -m venv .venv && . .venv/bin/activate`).

Opcje `run_benchmark`: `--runs N`, `--variants A B`, `--cases c01 c11`,
`--model claude-haiku-5-5`, `--effort low|medium|high`, `--dry-run` (skryptowany
model bez API, tylko do sprawdzenia pipeline'u; tokeny w nim to szacunki).

Pełny przebieg to 3 × 12 × 2 = 72 zadania, ok. 200 wywołań modelu; przy cenach
Haiku 5.5 to rząd kilku centów.

## Kolejność i cache

Zadania idą sekwencyjnie: powtórzenie → przypadek → wariant (A, potem B).
Prefiks (tools + system prompt) jest stały w obrębie wariantu, więc po pierwszym
zadaniu oba warianty czytają go z cache. Tabela „według powtórzenia” w raporcie
pokazuje, ile daje cache.

## Struktura

```
skilltest/
  procedures.py      12 procedur: parametry + oczekiwane argumenty
  render_skills.py   generuje skills/*/SKILL.md
  skills/            12 skilli (wariant B) = treść system promptu wariantu A
  engine.py          tool credit_analysis_engine (deterministyczny) + log wywołań
  cases.py           12 wniosków testowych
  prompts.py         system prompty A i B
  agents.py          budowa agentów A (create_agent) i B (create_deep_agent)
  metrics.py         zbieranie tokenów/czasu i ocena argumentów
  run_benchmark.py   uruchomienie testu
  analyze.py         raport
  fake_model.py      skryptowany model do --dry-run i testów
tests/test_offline.py
```
