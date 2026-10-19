# Analiza: skille (B) vs wszystko w system prompcie (A)

Przebieg: 15.10.2026, `claude-haiku-5-5` (effort domyślny), 12 przypadków × 3 powtórzenia × 2 warianty = 72 zadania, 0 błędów. Pełne liczby są w [`20261015T081233Z/REPORT.md`](20261015T081233Z/REPORT.md).

## Wynik w jednym zdaniu

Przy 12 procedurach skille niczego nie poprawiły ani nie popsuły w jakości (100% w obu wariantach). Kosztują natomiast jedno dodatkowe wywołanie modelu: **+11% tokenów IN, +11% czasu, +5% kosztu** na zadanie.

## Liczby (średnia na zadanie)

| | A: jeden prompt | B: deepagents + skille | B / A |
|---|---|---|---|
| Trafność (14/14 pól, właściwa procedura) | 100% | 100% | – |
| Tool wywołany dokładnie raz | 36/36 | 36/36 | – |
| Wywołania modelu | 2 | 3 | 1,50× |
| Tokeny IN | 23 832 | 26 399 | 1,11× |
| – w tym z cache (odczyt) | 22 418 (94%) | 24 495 (93%) | |
| Tokeny IN na jedno wywołanie | ~11 900 | ~8 800 | 0,74× |
| Tokeny OUT | 1 230 | 1 159 | 0,94× |
| Czas zadania | 5,88 s ± 1,28 | 6,53 s ± 0,60 | 1,11× |
| Koszt | $0,00102 | $0,00106 | 1,05× |

## Co z tego wynika

1. **Jakość: remis.** Haiku 5.5 bezbłędnie wybiera procedurę i liczy wszystkie 14 argumentów w obu układach, łącznie z pułapkami (kwota dokładnie 50 000, ignorowanie małżonka przy małym kredycie obrotowym). W wariancie B agent za każdym razem czytał właściwy skill, i to dokładnie jeden (36/36, zawsze `read_file → credit_analysis_engine`). Przy tej skali 12 opisów po ~500 tokenów nie „rozprasza” modelu, więc progressive disclosure nie ma czego naprawiać.

2. **Tokeny: krótszy prompt, ale o jedno wywołanie więcej.** Pojedyncze wywołanie w B jest o ~26% mniejsze (lista skilli zamiast 12 pełnych opisów). B robi jednak 3 wywołania zamiast 2: dochodzi odczyt skilla. Do tego deepagents dokłada w każdym wywołaniu własne narzędzia (ls, read_file, write_file, edit_file, glob, grep, task, delete) i instrukcję systemu skilli. Bilans to +11% tokenów IN.

3. **Koszt: różnica prawie znika przez cache.** W obu wariantach ~93–94% wejścia to odczyt z cache (10% ceny). Płaci się głównie za OUT i zapis do cache, więc +11% tokenów daje tylko +5% kosztu. W B jest o 6% mniej tokenów OUT: model krócej „myśli”, gdy ma przed sobą tylko jedną procedurę.

4. **Czas: +0,65 s na dodatkowy round-trip, ale stabilniej.** B jest o 11% wolniejszy (dodatkowe wywołanie modelu), za to ma o połowę mniejszy rozrzut czasu (σ 0,60 s wobec 1,28 s). Krótszy kontekst daje bardziej przewidywalne wywołania.

5. **Cache rozgrzewa się po pierwszym przebiegu.** W pierwszym powtórzeniu zapis do cache jest 2× wyższy w obu wariantach. Od drugiego koszt A spada o 15%, a B o 11%.

## Kiedy skille zaczną się opłacać (szacunek, nie pomiar)

Prompt A rośnie o pełny opis z każdą nową procedurą i jest wysyłany w każdym wywołaniu. B rośnie tylko o jedną linię opisu skilla (~60 tokenów). Liniowa ekstrapolacja z tych danych przy ~550 tokenach na procedurę daje zrównanie tokenów IN przy około **15–20 procedurach**. Powyżej tego B zużywa mniej tokenów, a przewaga rośnie z liczbą procedur. Czas B zawsze będzie gorszy o jeden round-trip, chyba że opisy są na tyle długie, że ich przetwarzanie w A trwa dłużej. Ekstrapolacja zakłada, że trafność A się utrzyma, a tego ten test nie sprawdza.

## Ograniczenia testu

- Zadanie okazało się za łatwe dla Haiku 5.5 (sufit 100%), więc test nie mówi nic o tym, czy skille pomagają jakości przy trudniejszych lub liczniejszych procedurach.
- Wariant B to nie same skille, tylko skille plus harness deepagents (dodatkowe narzędzia i prompt). Część narzutu pochodzi z deepagents, a nie z samego mechanizmu skilli.
- 3 powtórzenia × 12 przypadków to 36 prób na wariant. Różnice czasu (+11%) mieszczą się w rozrzucie A.

## Co warto sprawdzić dalej

- 50–100 procedur (np. więcej wymiarów: zatrudnienie, waluta), żeby znaleźć realny punkt przecięcia i zobaczyć, czy A zaczyna się mylić.
- Wariant B bez zbędnych narzędzi deepagents (tylko `read_file`), żeby oddzielić koszt skilli od kosztu harnessu.
- Wariant „skill w tool description” bez osobnego wywołania (skille wstrzykiwane po klasyfikacji), żeby zobaczyć, czy da się uniknąć dodatkowego round-tripu.
