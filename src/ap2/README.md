# AP2 Protocol - Agent Payments Integration

Implementación del protocolo AP2 (Agent Payments Protocol) para el marketplace de Pokemon.

## Estructura

```
src/ap2/
├── agents/
│   ├── shopping/          # Agente de compras con UI web
│   │   ├── __main__.py
│   │   ├── agent.py
│   │   └── web_ui.py
│   ├── merchant/          # Agente vendedor
│   │   ├── __main__.py
│   │   └── server.py
│   └── credentials_provider/  # Proveedor de credenciales
│       ├── __main__.py
│       └── server.py
├── protocol/              # Tipos y validadores AP2
│   ├── types.py          # CartMandate, PaymentRequest, etc.
│   ├── validators.py     # Validación JWT
│   ├── session.py        # Gestión de sesiones
│   └── utils.py
└── processor/            # Procesador de pagos
    ├── __main__.py
    └── server.py
```

## Puertos

- 8000: Shopping Web UI
- 8001: Merchant Agent
- 8002: Credentials Provider
- 8003: Payment Processor

## Ejecución

```bash
# Todos los agentes
uv run python -m src.shopping_agent &
uv run python -m src.merchant_agent &
uv run python -m src.credentials_provider &
uv run python -m src.payment_processor &

# O usar scripts
./scripts/run-ap2-agents.sh
```

## Variables de Entorno

Ver `.env.example` para configuración requerida:
- `GOOGLE_API_KEY` - API key de Google AI Studio
- Puertos de cada agente
