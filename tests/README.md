# Tests y Scripts de Prueba

Esta carpeta contiene scripts de prueba para validar el funcionamiento del proyecto.

## 📋 Archivos de Test

### `test_mcp.py`
Test completo del servidor MCP.

**Uso:**
```bash
python tests/test_mcp.py
```

**Prueba:**
- Conexión con el servidor MCP
- Todas las tools disponibles
- Respuestas correctas

### `test_mcp_simple.py`
Test simplificado del servidor MCP.

**Uso:**
```bash
python tests/test_mcp_simple.py
```

**Prueba:**
- Funcionalidades básicas
- Respuesta rápida

### `test_unified_mcp.sh`
Script bash para probar el servidor MCP unificado.

**Uso:**
```bash
chmod +x tests/test_unified_mcp.sh
./tests/test_unified_mcp.sh
```

**Realiza:**
- Instalación de dependencias
- Compilación del servidor
- Inicio del servidor MCP
- Verificación de tools disponibles

## 🚀 Ejecutar Todos los Tests

```bash
# Tests Python
python tests/test_mcp.py
python tests/test_mcp_simple.py

# Test del servidor
./tests/test_unified_mcp.sh
```

## 📝 Notas

- Asegúrate de tener el MCP Server compilado antes de ejecutar tests
- Los tests de Python requieren las dependencias instaladas
- El script bash es interactivo y requiere Ctrl+C para detener el servidor

## 🔗 Ver También

- [README Principal](../README.md)
- [MCP Server README](../mcp-server/README.md)
- [AP2 Integration Tests](../ap2-integration/README.md#testing)
