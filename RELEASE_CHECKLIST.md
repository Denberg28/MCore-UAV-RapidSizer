# MCore Release Checklist

## Engineering

- [ ] Requirements and assumptions are explicit.
- [ ] No implemented deterministic calculation was replaced by an AI estimate.
- [ ] Units and coordinate conventions are documented.
- [ ] Changed engineering equations have an independent check.
- [ ] Measured and estimated inputs remain distinguishable.
- [ ] Known limitations are recorded.

## Software

- [ ] `python -m compileall -q app` passes.
- [ ] `python -m pytest -q` passes.
- [ ] CLI sample analysis runs.
- [ ] GUI smoke test passes.
- [ ] New/changed deterministic behavior has regression tests.
- [ ] No credentials, `.env` files, private aircraft data, or generated caches are staged.

## Physical validation

- [ ] Relevant real-aircraft validation has been performed, or the missing evidence is explicitly documented.
- [ ] CG validation compares calculated and physically measured CG.
- [ ] Propulsion claims use matching measured/manufacturer test data where required.

## GitHub

- [ ] Feature branch pushed.
- [ ] GitHub Actions passes.
- [ ] Changes reviewed before merge.
- [ ] `main` is green after merge.
- [ ] Release notes updated.
- [ ] Version tag created only after the release gate passes.
