# Wyniki: 20261015T081233Z

Model: `claude-haiku-5-5`, effort: `domyślny`, powtórzeń: 3, przypadków: 12, start: 20261015T081233Z.

## Średnie na jedno zadanie (jedna aplikacja kredytowa)

| Metryka | Wariant A (n=36) | Wariant B (n=36) | B / A |
|---|---|---|---|
| Poprawne argumenty (wszystkie pola) | 100% | 100% | |
| Poprawna procedura | 100% | 100% | |
| Tool wywołany dokładnie 1 raz | 100% | 100% | |
| Śr. poprawnych pól (z 14) | 14.00 | 14.00 | 1.00× |
| Wywołania modelu / zadanie | 2.00 | 3.00 | 1.50× |
| Tokeny IN razem | 23 832 ± 223 | 26 399 ± 392 | 1.11× |
|   w tym bez cache | 6 | 8 | 1.33× |
|   w tym zapis do cache | 1 407 ± 1 856 | 1 896 ± 1 409 | 1.35× |
|   w tym odczyt z cache | 22 418 ± 1 902 | 24 495 ± 1 500 | 1.09× |
| Tokeny OUT | 1 230 ± 176 | 1 159 ± 133 | 0.94× |
| Czas zadania [s] | 5.88 ± 1.28 | 6.53 ± 0.60 | 1.11× |
| Czas samego modelu [s] | 5.85 ± 1.28 | 6.45 ± 0.60 | 1.10× |
| Koszt / zadanie [USD] | 0.00102 ± 0.00022 | 0.00106 ± 0.00017 | 1.05× |

## Według powtórzenia (wpływ cache)

| Wariant | Powt. | Tokeny IN | odczyt z cache | zapis do cache | Tokeny OUT | Czas [s] | Koszt [USD] | Poprawne |
|---|---|---|---|---|---|---|---|---|
| A | 1 | 23 843 | 21 589 | 2 248 | 1 265 | 6.43 | 0.00113 | 100% |
| A | 2 | 23 828 | 22 833 | 989 | 1 211 | 5.56 | 0.00096 | 100% |
| A | 3 | 23 824 | 22 833 | 984 | 1 214 | 5.65 | 0.00096 | 100% |
| B | 1 | 26 402 | 23 611 | 2 783 | 1 152 | 6.43 | 0.00116 | 100% |
| B | 2 | 26 399 | 24 737 | 1 654 | 1 158 | 6.55 | 0.00103 | 100% |
| B | 3 | 26 397 | 25 138 | 1 251 | 1 168 | 6.60 | 0.00099 | 100% |

## Trafność według przypadku

| Przypadek | Procedura | A: poprawne / wywołań toola | B: poprawne / wywołań toola |
|---|---|---|---|
| c01 | SINGLE_AUTO_SMALL | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |
| c02 | SINGLE_AUTO_LARGE | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |
| c03 | MARRIED_AUTO_SMALL | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |
| c04 | MARRIED_AUTO_LARGE | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |
| c05 | SINGLE_HOME_SMALL | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |
| c06 | SINGLE_HOME_LARGE | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |
| c07 | MARRIED_HOME_SMALL | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |
| c08 | MARRIED_HOME_LARGE | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |
| c09 | SINGLE_REV_SMALL | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |
| c10 | SINGLE_REV_LARGE | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |
| c11 | MARRIED_REV_SMALL | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |
| c12 | MARRIED_REV_LARGE | 3/3 (tool: 1/1/1) | 3/3 (tool: 1/1/1) |

## Najczęstsze błędne pola

- **A**: brak
- **B**: brak

## Zachowanie skilli w wariancie B

- Przeczytano właściwy skill: 36/36 zadań
- Średnio odczytów `read_file` na zadanie: 1.00 (max 1)
- Sekwencje narzędzi:
  - `read_file → credit_analysis_engine` ×36
