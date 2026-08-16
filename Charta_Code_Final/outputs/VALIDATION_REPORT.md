# Charta Code Final — Polyglot Validation Report

Languages tested: 51
SPOK dictionary entries: 74
SPOK templates: 42

| Language | Extension | SPOK lines | Charta lines | Valid Devanagari | Status |
|---|---|---:|---:|:---:|:---:|
| abap | .abap | 5 | 5 | Yes | PASS |
| ada | .adb | 5 | 5 | Yes | PASS |
| assembly | .asm | 5 | 5 | Yes | PASS |
| bash | .sh | 5 | 5 | Yes | PASS |
| batch | .bat | 5 | 5 | Yes | PASS |
| c | .c | 5 | 5 | Yes | PASS |
| cobol | .cob | 5 | 5 | Yes | PASS |
| cpp | .cpp | 5 | 5 | Yes | PASS |
| crystal | .cr | 5 | 5 | Yes | PASS |
| csharp | .cs | 5 | 5 | Yes | PASS |
| css | .css | 5 | 5 | Yes | PASS |
| dart | .dart | 5 | 5 | Yes | PASS |
| delphi | .dpr | 5 | 5 | Yes | PASS |
| elixir | .ex | 5 | 5 | Yes | PASS |
| erlang | .erl | 5 | 5 | Yes | PASS |
| fortran | .f90 | 5 | 5 | Yes | PASS |
| fsharp | .fs | 5 | 5 | Yes | PASS |
| go | .go | 5 | 5 | Yes | PASS |
| groovy | .groovy | 5 | 5 | Yes | PASS |
| haskell | .hs | 5 | 5 | Yes | PASS |
| html | .html | 5 | 5 | Yes | PASS |
| java | .java | 5 | 5 | Yes | PASS |
| javascript | .js | 5 | 5 | Yes | PASS |
| julia | .jl | 5 | 5 | Yes | PASS |
| kotlin | .kt | 5 | 5 | Yes | PASS |
| lisp | .lisp | 5 | 5 | Yes | PASS |
| lua | .lua | 5 | 5 | Yes | PASS |
| matlab | .m | 5 | 5 | Yes | PASS |
| mql5 | .mq5 | 5 | 5 | Yes | PASS |
| nim | .nim | 5 | 5 | Yes | PASS |
| objective-c | .m | 5 | 5 | Yes | PASS |
| pascal | .pas | 5 | 5 | Yes | PASS |
| perl | .pl | 5 | 5 | Yes | PASS |
| php | .php | 5 | 5 | Yes | PASS |
| powershell | .ps1 | 5 | 5 | Yes | PASS |
| prolog | .pro | 5 | 5 | Yes | PASS |
| python | .py | 5 | 5 | Yes | PASS |
| r | .r | 5 | 5 | Yes | PASS |
| rpg | .rpgle | 5 | 5 | Yes | PASS |
| ruby | .rb | 5 | 5 | Yes | PASS |
| rust | .rs | 5 | 5 | Yes | PASS |
| scala | .scala | 5 | 5 | Yes | PASS |
| scratch | .sb3 | 5 | 5 | Yes | PASS |
| solidity | .sol | 5 | 5 | Yes | PASS |
| sql | .sql | 5 | 5 | Yes | PASS |
| swift | .swift | 5 | 5 | Yes | PASS |
| typescript | .ts | 5 | 5 | Yes | PASS |
| v | .v | 5 | 5 | Yes | PASS |
| verilog | .v | 5 | 5 | Yes | PASS |
| vhdl | .vhd | 5 | 5 | Yes | PASS |
| visual_basic | .vb | 5 | 5 | Yes | PASS |

**Failures:** 0

Notes:
- Synthetic samples contain the first 5 mapped keywords for each language.
- SPOK output is validated to only contain tokens present in `charta_runtime.SPOK_DICTIONARY` (74 entries).
- Charta (Devanagari) output is validated to contain at least one Devanagari codepoint.
- `.cht` packages are generated only when `CHARTA_MASTER_KEY` is set and are git-ignored by the root `.gitignore`.