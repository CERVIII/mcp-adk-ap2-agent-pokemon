# 🔐 RSA Keys Directory

Este directorio contiene las claves RSA utilizadas para firmar JWT en el protocolo AP2.

## 📁 Archivos

### Generados Automáticamente

- **`merchant_private.pem`** - Clave privada del merchant (RSA 2048-bit)
  - ⚠️ **NUNCA compartir ni subir a Git**
  - Permisos: `600` (solo lectura/escritura para el owner)
  - Usada para: Firmar CartMandates con JWT RS256

- **`merchant_public.pem`** - Clave pública del merchant
  - ✅ Segura para compartir
  - Permisos: `644` (lectura para todos)
  - Usada para: Verificar firmas de CartMandates

## 🔄 Comportamiento

### Primera Ejecución
Cuando el MCP server inicia por primera vez:
1. No encuentra claves en este directorio
2. Genera un nuevo par de claves RSA (2048-bit)
3. Guarda las claves en archivos `.pem`
4. Muestra mensaje: `🔐 Generating new RSA key pair...`

### Ejecuciones Posteriores
En inicios subsiguientes:
1. Encuentra las claves existentes
2. Las carga desde disco
3. Muestra mensaje: `🔑 Loading existing RSA keys from disk...`

## 🛡️ Seguridad

### Claves Privadas
- ❌ **NO** subir a Git (incluido en `.gitignore`)
- ❌ **NO** compartir por email, Slack, etc.
- ❌ **NO** incluir en logs o screenshots
- ✅ Hacer backup seguro (cifrado)
- ✅ Rotación periódica (cada 6-12 meses)

### Claves Públicas
- ✅ Seguro subir a Git
- ✅ Compartir con servicios que validan firmas
- ✅ Incluir en documentación de API

## 🔄 Rotación de Claves

Para generar un nuevo par de claves:

```bash
# Opción 1: Eliminar claves existentes (se regenerarán al iniciar)
rm merchant_private.pem merchant_public.pem

# Opción 2: Hacer backup y eliminar
mv merchant_private.pem merchant_private.pem.backup.$(date +%Y%m%d)
mv merchant_public.pem merchant_public.pem.backup.$(date +%Y%m%d)

# Reiniciar el servidor MCP
cd ..
npm start
```

⚠️ **Importante**: Después de rotar claves, todos los JWT firmados con la clave antigua serán inválidos.

## 📊 Verificación de Claves

### Ver información de la clave pública
```bash
openssl rsa -pubin -in merchant_public.pem -text -noout
```

### Ver información de la clave privada (requiere contraseña si está cifrada)
```bash
openssl rsa -in merchant_private.pem -text -noout
```

### Verificar que las claves son un par válido
```bash
# Extraer módulo de clave privada
openssl rsa -in merchant_private.pem -noout -modulus

# Extraer módulo de clave pública
openssl rsa -pubin -in merchant_public.pem -noout -modulus

# Si los módulos coinciden, las claves son un par válido
```

## 🧪 Testing

Para verificar que las claves persisten correctamente:

```bash
# 1. Iniciar servidor y ver que se generan claves
npm start

# 2. Detener servidor (Ctrl+C)

# 3. Verificar que existen archivos
ls -lh keys/

# 4. Reiniciar servidor
npm start

# 5. Verificar en logs que dice "Loading existing RSA keys" (no "Generating")
```

## 🔍 Troubleshooting

### Error: "Permission denied" al escribir claves
```bash
# Dar permisos al directorio
chmod 700 keys/
```

### Claves corruptas o inválidas
```bash
# Verificar formato PEM
head -n 1 merchant_private.pem
# Debe mostrar: -----BEGIN PRIVATE KEY-----

# Si están corruptas, eliminar y regenerar
rm merchant_*.pem
npm start
```

### Quiero usar mis propias claves
```bash
# Generar claves con OpenSSL
openssl genrsa -out merchant_private.pem 2048
openssl rsa -in merchant_private.pem -pubout -out merchant_public.pem

# Ajustar permisos
chmod 600 merchant_private.pem
chmod 644 merchant_public.pem
```

## 📚 Referencias

- [RFC 7517 - JSON Web Key (JWK)](https://tools.ietf.org/html/rfc7517)
- [RFC 7518 - JSON Web Algorithms (JWA)](https://tools.ietf.org/html/rfc7518)
- [Node.js Crypto Module](https://nodejs.org/api/crypto.html)
- [OpenSSL RSA](https://www.openssl.org/docs/man1.1.1/man1/rsa.html)

---

**Última actualización**: 21 de Octubre de 2025  
**Versión**: 1.0 - Implementación de persistencia de claves RSA
