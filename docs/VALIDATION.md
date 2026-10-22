# Validation and rubric acceptance

Validated on the author's Apple Silicon macOS environment using the existing
Python 3.11 installation, explicitly selected instead of the original 3.12 target.
These results describe commands actually executed during implementation.

## Environment and setup

| Check | Observed result |
| --- | --- |
| `python --version` | Python 3.11.15 |
| `python -m chatterbot --version` | 1.2.15 |
| `python -m django --version` | 5.2.18 |
| Dependency installation in fresh `.venv` | Successful |
| Additional direct dependencies | chatterbot-corpus 1.3.3, PyYAML 6.0.3 |
| `python -m pip check` | No broken requirements found |
| `python manage.py check` | No issues, 0 silenced |
| `python manage.py migrate` | All contenttypes and 21 ChatterBot migrations applied |
| `python manage.py train_bot` | All three corpora completed |
| `python manage.py test -v 2` | 29 tests passed; see `test-results.txt` |
| Source distribution | Built and inspected; code, corpus and manifests included |
| Source syntax and line length | Parses successfully; Python lines at most 79 characters |

Installation initially encountered sandbox DNS restrictions. Retrying with
approved network access succeeded. Local server binding and HTTP requests also
required sandbox permission. These restrictions were environmental, not package
compatibility failures. No system Python replacement was needed for the project.

## Terminal execution

The actual `python manage.py chat` process was exercised in a pseudo-terminal.
Observed meaningful responses covered:

- Hello and Good morning!
- DevOps, CI/CD, Terraform, Kubernetes
- Standup updates, failed deployments, blameless postmortems
- RTO while learning was OFF
- `/status`, `/learning off`, `/learning on`, and `/exit`
- An unrelated phrase receiving the configured fallback

Automated command tests additionally cover empty input, invalid commands,
`/help`, `/clear`, `/quit`, EOF/Ctrl+D, Ctrl+C, and unexpected runtime failures.
No screenshot was generated or claimed. The author should capture the native
terminal run using the README sequence for the assignment's Word document.

## API execution

Started `python manage.py runserver 127.0.0.1:8000 --noreload` and sent real HTTP
requests using Python's standard-library client with a CSRF cookie and header:

- GET `/api/health/`: HTTP 200, CloudOps Assistant / Django / ChatterBot metadata.
- POST `/api/chat/`: HTTP 200 for `What is CI/CD?`, correct corpus answer,
  confidence 1.0, and `learning_enabled: false`.

Tests additionally enforce CSRF and verify actual unchanged database row counts,
malformed JSON, invalid encoding, empty/non-string inputs, oversized bodies,
content type, methods, and runtime failure responses.

## Findings resolved during validation

1. ChatterBot 1.2.15's Django AppConfig overwrites the configured name with
   `ChatterBot`. BotService now applies the separate authoritative `BOT_NAME`.
2. A 0.75 minimum similarity threshold accepted `What is pizza?` as an IAM query
   at 0.85. The final threshold is 0.90, with a full-corpus regression test for
   this and three additional unrelated questions. This is a conservative
   string-matching heuristic, not a guarantee of semantic correctness.
3. ChatterBot saves responses before an application-level fallback can replace
   them. The service uses a transaction and rolls back rejected low-confidence
   turns, avoiding persistence of an answer the user never saw.
4. Repeated training inserts duplicate rows in the upstream Django adapter.
   Tests confirm old knowledge remains; README documents non-idempotent behavior.

## Rubric assessment

| Category | Weight | Evidence and status |
| --- | --- | --- |
| Application Requirement Delivery | 20% | Python source, genuine Django/ChatterBot ORM integration, terminal client, two manifests, 54 custom Q&A pairs plus assignment example, screenshot directory and repository URL are present. Code scope satisfied. |
| Coding Standards | 40% | Modular service/commands/views, type hints and docstrings, bounded input, logged errors, transactional writes, pinned dependencies, ignored local artifacts, meaningful tests, readable formatting. Reviewed; no numeric grade predicted. |
| Runtime, Correctness, Submission | 40% | Installation, checks, migrations, training, terminal session, learning toggle, exits, HTTP endpoints and 29 tests passed. README provides reproducible instructions. Screenshot, Word document and LMS submission remain the author's later workflow. |

## Limits and remaining submission work

- Similarity is not factual certainty. Unseen paraphrases may fall back; similarly
  spelled topics can still be confused. Add reviewed corpus examples as needed.
- Continuous learning retains accepted conversation text locally and can learn
  unhelpful associations. API traffic is always read-only.
- Greeting wording can vary because standard and custom corpora overlap.
- Health is a liveness check, not a database/training readiness test.
- The source checkout/extracted source archive is the supported run workflow.
- Capture a real screenshot and insert it with the GitHub URL into the final
  Word document. No DOCX or LMS submission was performed in this task.
- The screenshots show rubric category weights, not expanded scoring descriptors;
  this assessment does not claim an instructor grade.
