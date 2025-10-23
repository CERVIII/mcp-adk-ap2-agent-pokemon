# MCP Server CI/CD

Este directorio contiene los workflows de GitHub Actions para el proyecto.

## 🔄 Workflows Activos

### 1. Test MCP (`test-mcp.yml`)
Ejecuta la suite completa de tests unitarios del servidor MCP.

**Triggers:**
- Push a `main` o `refactor/project-restructure`
- Pull Requests a `main`
- Cambios en archivos relevantes del MCP

**Acciones:**
- ✅ Ejecuta 250 tests unitarios
- ✅ Genera reporte de cobertura
- ✅ Sube cobertura a Codecov (opcional)
- ✅ Prueba en Node.js 20.x y 22.x

**Duración esperada:** ~30-40 segundos

---

### 2. Build & Lint (`build.yml`)
Verifica que el código TypeScript compila correctamente.

**Triggers:**
- Push a `main` o `refactor/project-restructure`
- Pull Requests a `main`

**Acciones:**
- ✅ Verifica compilación TypeScript
- ✅ Valida tipos

**Duración esperada:** ~20 segundos

---

## 📊 Badges para README

Agrega estos badges a tu `README.md` principal:

```markdown
[![MCP Tests](https://github.com/CERVIII/mcp-adk-ap2-agent-pokemon/actions/workflows/test-mcp.yml/badge.svg)](https://github.com/CERVIII/mcp-adk-ap2-agent-pokemon/actions/workflows/test-mcp.yml)
[![Build](https://github.com/CERVIII/mcp-adk-ap2-agent-pokemon/actions/workflows/build.yml/badge.svg)](https://github.com/CERVIII/mcp-adk-ap2-agent-pokemon/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/CERVIII/mcp-adk-ap2-agent-pokemon/branch/main/graph/badge.svg)](https://codecov.io/gh/CERVIII/mcp-adk-ap2-agent-pokemon)
```

---

## 🔧 Configuración Local

Para ejecutar los mismos tests que CI:

```bash
# Instalar dependencias
npm ci

# Ejecutar tests
npm test

# Generar cobertura
npm run test:coverage
```

---

## 🚀 Optimizaciones

Los workflows están optimizados para:
- ⚡ Uso de caché de npm (`cache: 'npm'`)
- 🎯 Ejecución condicional (solo si cambian archivos relevantes)
- 📊 Reportes automáticos en el PR
- 🔄 Matrix testing (múltiples versiones de Node.js)

---

## ❓ Troubleshooting

### Tests fallan en CI pero pasan localmente
- Verifica que uses `npm ci` en lugar de `npm install`
- Asegúrate de que `package-lock.json` esté actualizado
- Revisa las versiones de Node.js

### Cobertura no se sube a Codecov
- Necesitas configurar `CODECOV_TOKEN` en Settings → Secrets
- O elimina ese step si no usas Codecov

### Workflow no se ejecuta
- Verifica que los paths en `on.push.paths` coincidan con tus archivos
- Revisa que el branch esté en la lista de `branches`
