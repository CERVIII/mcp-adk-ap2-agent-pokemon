---
title: "[Phase 4.1] User Authentication System (OAuth2)"
labels: enhancement, security, backend, phase-4
assignees: CERVIII
---

## 📋 Descripción

Implementar sistema de autenticación completo con OAuth2 (Google/GitHub), JWT para sesiones, y UI de login/logout/registro.

## 🎯 Tipo de Issue

- [x] ✨ Nueva feature
- [x] 🔐 Seguridad
- [x] 🗄️ Database

## 📦 Fase del Roadmap

**Fase 4.1: Sistema de Autenticación**

## ✅ Tareas

### OAuth2 Integration
- [ ] Setup OAuth2 apps en Google Cloud Console
- [ ] Setup OAuth2 apps en GitHub
- [ ] Variables de entorno: `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- [ ] Librería: `authlib` o `python-jose`

### JWT Implementation
- [ ] Generar JWT al login exitoso
- [ ] Claims: `user_id`, `email`, `name`, `exp`, `iat`
- [ ] RS256 signature (reusar claves RSA existentes)
- [ ] Refresh token mechanism (opcional Phase 4.2)

### Database Schema
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100),
    avatar_url VARCHAR(500),
    oauth_provider VARCHAR(20),  -- 'google' | 'github'
    oauth_id VARCHAR(100),
    created_at TIMESTAMP,
    last_login TIMESTAMP
);
```

### Backend Endpoints
- [ ] `GET /auth/google` → Redirect a Google OAuth
- [ ] `GET /auth/google/callback` → Procesa callback
- [ ] `GET /auth/github` → Redirect a GitHub OAuth
- [ ] `GET /auth/github/callback` → Procesa callback
- [ ] `POST /auth/logout` → Invalida JWT
- [ ] `GET /auth/me` → Obtiene usuario actual

### Frontend UI
- [ ] Página `/login` con botones "Login with Google" y "Login with GitHub"
- [ ] Navbar muestra avatar + nombre cuando authenticated
- [ ] Dropdown: "My Account", "Logout"
- [ ] Redirect después de login a página original

### Protected Routes
- [ ] Middleware `@require_auth` para endpoints protegidos
- [ ] `/api/cart/checkout` requiere autenticación
- [ ] `/my-purchases` requiere autenticación

### Session Management
- [ ] Migrar de session_id a user_id en Cart
- [ ] Asociar carritos anónimos con user al login
- [ ] "Continue as guest" option

## 🔧 Detalles Técnicos

**JWT Structure:**
```json
{
  "user_id": 123,
  "email": "trainer@pokemon.com",
  "name": "Ash Ketchum",
  "exp": 1730000000,
  "iat": 1729990000
}
```

**OAuth2 Flow:**
1. User clicks "Login with Google"
2. Redirect to Google authorization page
3. User approves
4. Google redirects to `/auth/google/callback?code=xyz`
5. Backend exchanges code for tokens
6. Fetch user info from Google
7. Create/update user in DB
8. Generate JWT
9. Set JWT in httpOnly cookie
10. Redirect to dashboard

## 📝 Criterios de Aceptación

- [ ] Login con Google funciona
- [ ] Login con GitHub funciona
- [ ] JWT generado y almacenado en cookie
- [ ] Logout limpia JWT
- [ ] UI muestra estado de autenticación
- [ ] Protected routes verifican JWT
- [ ] Carritos anónimos se asocian al user

## 🎨 Frontend Changes

- [ ] Login page con diseño profesional
- [ ] Iconos de Google/GitHub
- [ ] Loading state durante OAuth flow
- [ ] Error handling (OAuth denied, network error)

## ⏱️ Estimación

**Tiempo:** 1.5-2 semanas
**Prioridad:** Alta (prerequisito para features avanzadas)

## 🔗 Issues Relacionados

Prerequisito para: #phase-4-2-user-profiles, #phase-2-4-purchase-history (mejoras)

## 📚 Recursos

- [FastAPI OAuth2](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Authlib Documentation](https://docs.authlib.org/en/latest/)
- [Google OAuth2 Setup](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Apps](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/creating-an-oauth-app)

## 🚨 Consideraciones de Seguridad

**CRÍTICO:**
- [ ] HTTPS obligatorio en producción
- [ ] Secrets en `.env`, nunca en código
- [ ] JWT expiration: 1 hora (considerar refresh tokens)
- [ ] CORS configurado correctamente
- [ ] Rate limiting en endpoints de auth
- [ ] Validar email domain (opcional)
- [ ] No almacenar OAuth tokens, solo JWT propio

**GDPR Compliance:**
- [ ] Botón "Delete Account" (Phase 4.2)
- [ ] Privacy policy actualizada
- [ ] User consent para almacenar datos
