# Local GraphRAG in Python — Reference Solutions

This folder contains the complete reference implementation for all 6 tasks, kept completely separate from the starter code in `src/graphrag/`.

## Running the Pytest Gates Against the Solutions

Override `pythonpath` so `pytest` imports the reference implementation in `solutions/src` instead of the starter stubs in `src`:

```bash
pytest -o pythonpath=solutions/src
```
