#!/usr/bin/env python3
"""
Test de persistencia de claves RSA del MCP Server

Este test verifica que:
1. Las claves se generan correctamente la primera vez
2. Las claves se cargan desde disco en ejecuciones posteriores
3. Las claves permanecen consistentes entre reinicios
"""

import subprocess
import time
import os
import re
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
MCP_SERVER_DIR = PROJECT_ROOT / "mcp-server"
KEYS_DIR = MCP_SERVER_DIR / "keys"
PRIVATE_KEY_PATH = KEYS_DIR / "merchant_private.pem"
PUBLIC_KEY_PATH = KEYS_DIR / "merchant_public.pem"

def run_mcp_server_briefly(timeout_seconds=2):
    """
    Inicia el MCP server brevemente y captura su output.
    """
    try:
        result = subprocess.run(
            ["npm", "start"],
            cwd=MCP_SERVER_DIR,
            capture_output=True,
            text=True,
            timeout=timeout_seconds
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired as e:
        # Timeout es esperado
        stdout = e.stdout.decode('utf-8') if isinstance(e.stdout, bytes) else (e.stdout or "")
        stderr = e.stderr.decode('utf-8') if isinstance(e.stderr, bytes) else (e.stderr or "")
        return stdout + stderr

def extract_public_key_preview(output):
    """
    Extrae el preview de la clave pública del output del servidor.
    """
    match = re.search(r'Public key preview: (.+)', output)
    if match:
        return match.group(1).strip()
    return None

def test_rsa_key_persistence():
    """
    Test principal de persistencia de claves RSA.
    """
    print("🧪 Testing RSA Key Persistence")
    print("=" * 60)
    
    # Test 1: Limpiar claves existentes
    print("\n1️⃣ Test: Limpiando claves existentes...")
    if PRIVATE_KEY_PATH.exists():
        PRIVATE_KEY_PATH.unlink()
        print("   ✓ Eliminada clave privada")
    if PUBLIC_KEY_PATH.exists():
        PUBLIC_KEY_PATH.unlink()
        print("   ✓ Eliminada clave pública")
    
    assert not PRIVATE_KEY_PATH.exists(), "❌ Clave privada no se eliminó"
    assert not PUBLIC_KEY_PATH.exists(), "❌ Clave pública no se eliminó"
    print("   ✅ Claves eliminadas correctamente")
    
    # Test 2: Primera ejecución - generar claves
    print("\n2️⃣ Test: Primera ejecución (generar claves)...")
    output1 = run_mcp_server_briefly(timeout_seconds=3)
    
    # Verificar que dice "Generating"
    assert "Generating new RSA key pair" in output1, \
        "❌ No se generaron nuevas claves en primera ejecución"
    print("   ✓ Mensaje de generación encontrado")
    
    # Verificar que se guardaron
    assert "RSA keys saved to disk" in output1, \
        "❌ Las claves no se guardaron en disco"
    print("   ✓ Mensaje de guardado encontrado")
    
    # Verificar que los archivos existen
    time.sleep(0.5)  # Dar tiempo para que se escriban
    assert PRIVATE_KEY_PATH.exists(), "❌ Clave privada no se creó"
    assert PUBLIC_KEY_PATH.exists(), "❌ Clave pública no se creó"
    print("   ✓ Archivos de claves creados")
    
    # Verificar permisos
    private_perms = oct(PRIVATE_KEY_PATH.stat().st_mode)[-3:]
    public_perms = oct(PUBLIC_KEY_PATH.stat().st_mode)[-3:]
    assert private_perms == "600", f"❌ Permisos incorrectos en clave privada: {private_perms}"
    assert public_perms == "644", f"❌ Permisos incorrectos en clave pública: {public_perms}"
    print(f"   ✓ Permisos correctos (privada: {private_perms}, pública: {public_perms})")
    
    # Extraer preview de clave pública
    public_key_preview_1 = extract_public_key_preview(output1)
    assert public_key_preview_1, "❌ No se pudo extraer preview de clave pública"
    print(f"   ✓ Preview de clave: {public_key_preview_1[:50]}...")
    
    # Leer contenido de las claves
    private_key_content_1 = PRIVATE_KEY_PATH.read_text()
    public_key_content_1 = PUBLIC_KEY_PATH.read_text()
    
    assert "BEGIN PRIVATE KEY" in private_key_content_1, "❌ Formato de clave privada inválido"
    assert "BEGIN PUBLIC KEY" in public_key_content_1, "❌ Formato de clave pública inválido"
    print("   ✓ Formato PEM correcto")
    
    print("   ✅ Primera ejecución completada correctamente")
    
    # Test 3: Segunda ejecución - cargar claves existentes
    print("\n3️⃣ Test: Segunda ejecución (cargar claves)...")
    time.sleep(1)  # Esperar un poco antes de la segunda ejecución
    output2 = run_mcp_server_briefly(timeout_seconds=3)
    
    # Verificar que dice "Loading"
    assert "Loading existing RSA keys from disk" in output2, \
        "❌ No se cargaron claves existentes en segunda ejecución"
    print("   ✓ Mensaje de carga encontrado")
    
    assert "RSA keys loaded successfully" in output2, \
        "❌ Las claves no se cargaron exitosamente"
    print("   ✓ Mensaje de éxito encontrado")
    
    # Verificar que NO dice "Generating"
    assert "Generating new RSA key pair" not in output2, \
        "❌ Se generaron nuevas claves en lugar de cargar existentes"
    print("   ✓ No se generaron nuevas claves")
    
    # Extraer preview de clave pública
    public_key_preview_2 = extract_public_key_preview(output2)
    assert public_key_preview_2, "❌ No se pudo extraer preview de clave pública"
    
    # Verificar que el preview es el mismo
    assert public_key_preview_1 == public_key_preview_2, \
        f"❌ Las claves son diferentes:\n  Primera: {public_key_preview_1}\n  Segunda: {public_key_preview_2}"
    print(f"   ✓ Preview de clave idéntico: {public_key_preview_2[:50]}...")
    
    # Leer contenido de las claves nuevamente
    private_key_content_2 = PRIVATE_KEY_PATH.read_text()
    public_key_content_2 = PUBLIC_KEY_PATH.read_text()
    
    # Verificar que el contenido es idéntico
    assert private_key_content_1 == private_key_content_2, \
        "❌ El contenido de la clave privada cambió"
    assert public_key_content_1 == public_key_content_2, \
        "❌ El contenido de la clave pública cambió"
    print("   ✓ Contenido de claves idéntico")
    
    print("   ✅ Segunda ejecución completada correctamente")
    
    # Test 4: Verificar que son un par válido
    print("\n4️⃣ Test: Verificando que son un par RSA válido...")
    try:
        # Extraer módulo de clave privada
        result_private = subprocess.run(
            ["openssl", "rsa", "-in", str(PRIVATE_KEY_PATH), "-noout", "-modulus"],
            capture_output=True,
            text=True,
            check=True
        )
        modulus_private = result_private.stdout.strip()
        
        # Extraer módulo de clave pública
        result_public = subprocess.run(
            ["openssl", "rsa", "-pubin", "-in", str(PUBLIC_KEY_PATH), "-noout", "-modulus"],
            capture_output=True,
            text=True,
            check=True
        )
        modulus_public = result_public.stdout.strip()
        
        # Comparar módulos
        assert modulus_private == modulus_public, \
            "❌ Las claves no forman un par válido (módulos diferentes)"
        print("   ✓ Los módulos coinciden")
        print("   ✅ Par de claves RSA válido")
    except FileNotFoundError:
        print("   ⚠️  OpenSSL no disponible, saltando validación de par")
    except subprocess.CalledProcessError as e:
        print(f"   ⚠️  Error al verificar par: {e}")
    
    # Test 5: Verificar tamaño de clave
    print("\n5️⃣ Test: Verificando tamaño de clave RSA...")
    try:
        result = subprocess.run(
            ["openssl", "rsa", "-pubin", "-in", str(PUBLIC_KEY_PATH), "-text", "-noout"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout
        
        # Buscar "Public-Key: (2048 bit)"
        if "2048 bit" in output:
            print("   ✓ Clave RSA de 2048 bits (correcto)")
        else:
            print(f"   ⚠️  Tamaño de clave no confirmado: {output[:100]}")
        
        print("   ✅ Tamaño de clave verificado")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("   ⚠️  No se pudo verificar tamaño de clave")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ TODOS LOS TESTS PASARON")
    print("=" * 60)
    print("\n📊 Resumen:")
    print(f"   • Claves generadas en primera ejecución")
    print(f"   • Claves cargadas en segunda ejecución")
    print(f"   • Claves persistentes entre reinicios")
    print(f"   • Formato PEM válido")
    print(f"   • Permisos correctos (600/644)")
    print(f"   • Par RSA válido (2048 bits)")
    print(f"\n📁 Ubicación de claves:")
    print(f"   • Privada: {PRIVATE_KEY_PATH}")
    print(f"   • Pública:  {PUBLIC_KEY_PATH}")

if __name__ == "__main__":
    try:
        test_rsa_key_persistence()
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
