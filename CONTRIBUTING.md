# Contributing research and corrections

Independent review, replications, corrections, competing interpretations and new evidence are welcome through [GitHub Issues](https://github.com/p2ppsr/electrum-privacy-research/issues) and pull requests. Public review is an ongoing part of this project. Contributions from maintainers, service operators, users and other researchers use the same evidence-based process; publication does not depend on advance approval, private outreach or a response window.

Reference a claim ID from [CLAIMS](CLAIMS.md) or question ID from [OPEN-QUESTIONS](OPEN-QUESTIONS.md), or explain a new topic. Provide:

- The precise claim, correction or question and why it matters.
- The wallet version, source commit or artifact hash, platform and relevant experimental controls.
- Reproduction steps, expected and observed behavior, and supporting public evidence or controlled test artifacts.
- Attribution limits, alternative explanations and any proposed wording change.

Use disposable test data. Do not submit personal wallet files, recovery phrases, private keys, passwords or identifiable third-party financial histories. Financial examples should use controlled wallets and clearly identify their chain and monetary scope.

Run `RESEARCH_PYTHON=python3 bash scripts/validate.sh` for changes to retained analysis. Update `claims.json` and regenerate `CLAIMS.md` when a claim's support or limits change. Keep historical raw captures, failed attempts and pinned snapshots intact; add dated corrections and new results. Refresh the SHA-256 inventory with `python3 -m privacy_lab.manifest` after changing the payload. Source and method details are in [REPRODUCE](REPRODUCE.md).

Review discussions should identify the disputed claim, evidence, disposition, retest artifact and resulting text change. Acknowledgment of a contribution does not imply endorsement of unrelated claims. Unanswered questions and disagreement are not confirmation of misconduct.

Keep discussion professional and focused on methods, evidence and conclusions. Personal insults, harassment, threats and disclosure of private information are out of scope and may be removed or closed. Technical disagreement and well-supported criticism are welcome.

Original research contributions use the repository's Apache-2.0 license. Preserve applicable third-party rights and notices described in [LICENSING](LICENSING.md).
