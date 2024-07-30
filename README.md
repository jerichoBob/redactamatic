# redactamatic

Playing around with PII/PHI redaction using local models

## setup

To get this party started, you need to start up ollama (either in docker or locally), like this:

locally:
```bash
ollama pull mistral-nemo
ollama run mistral-nemo
```

or in a docker container, like this:
```bash
docker run -p 11434:11434 ollama/mistral-nemo
```

then you can run the script to get started:
```bash
python src/redact.py
```
which hits the ollama server at localhost:11434
