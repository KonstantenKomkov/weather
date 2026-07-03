# Weather Frontend

React 18 + Vite. Django отдаёт собранный `build/index.html` на `/`.

## Development

```bash
# из корня репозитория
make up              # Django на :8000
make frontend-install
make frontend-dev    # :5173, /api проксируется на Django
```

## Production build

```bash
make frontend-build
```

Артефакты: `mainapp/build/` (не коммитить — в `.gitignore`).
