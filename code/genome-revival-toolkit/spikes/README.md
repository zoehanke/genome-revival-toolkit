# Migration samples only

Run from the S0 code directory:

```
python -X utf8 -B -m unittest discover -s spikes -v
python -X utf8 -B spikes/run_samples.py --output spikes/runs/samples.json
```

Dependency: already-installed Biopython 1.88. Nothing is downloaded by these
commands. No old module or runtime module is imported. Samples are not shipped.

The sequence sample takes unambiguous strings and an explicit PAM pattern and
spacer length. It covers linear targets with a 3-prime PAM only. The Tm sample
takes explicit Na and primer concentrations, fixes other salts to zero and
uses DNA_NN3/saltcorr=5/non-self-complementary conditions. It does not assess
primer quality, reaction success, targeting activity or editing efficiency.

Independent oracles:

* Reverse complement: manually pair/reverse `AGTCAGAA` to `TTCTGACT`.
* Forward hit: construct 20 A, AGG, 5 T; guide [0,20), PAM [20,23).
* Reverse hit: construct CCT then 20 T; reference guide [3,23), PAM [0,3).
* Invalid PAM: replace AGG with AGT. Out-of-bounds PAM: put AGG before the guide.
* A10 Tm: nine AA/TT stacks (-7.9 kcal/mol, -22.2 cal/mol/K), two terminal
  A/T terms (+2.3, +4.1), gives dH=-66.5 and dS=-191.6.
* C10 Tm: nine GG/CC stacks (-8.0, -19.9), two terminal G/C terms (+0.1, -2.8),
  gives dH=-71.8 and dS=-184.7.
* For each: add `0.368 * 9 * ln(0.050)` to dS, then compute
  `1000*dH / (dS + 1.987*ln(250e-9)) - 273.15` using elementary arithmetic.
  Expected results are 13.824567460959202 C and 46.20545115304333 C.
  No old output or Biopython calculation generated these answers.

Thermodynamic parameter provenance: SantaLucia unified NN table, as cited by the
ported method; DOI 10.1073/pnas.95.4.1460. Only these explicit simple cases were
cross-checked; there is no general numerical-validation claim.

Initial Tm test literals were transcribed incorrectly during authoring and
corrected from the displayed independent arithmetic before any implementation
was run. The final eight tests retain the construction-defined expectations.
This is development evidence, not heldout evaluation or old-code acceptance.
