# Local Transcript Segment Quality Checker

## Pain point
Local transcription tools produce timestamped text, but creators still need to spot too-long, empty, overlapping, or suspicious segments before publishing.

## Why now
Transcribe.cpp was a top HN item today; local transcription workflows need lightweight QA around generated segments.

## Install and run
No third-party dependency is required. Python 3.9+ is enough.

```bash
python -m src.main --help
python -m src.main examples/transcript.txt --max-seconds 10
python -m src.main examples/transcript.txt --max-seconds 10 --fail-on-issues
```

## Example
```bash
python -m src.main examples/transcript.txt --max-seconds 10
```

The command prints a concise report and can be used in CI or local automation.
Use `--fail-on-issues` to return exit code 1 when transcript quality issues are found.

## Self-check
```bash
python tests/test_main.py
```

## Roadmap
- Add richer input templates.
- Add SARIF export where useful.
- Add more real-world fixtures from community feedback.

## License
MIT
