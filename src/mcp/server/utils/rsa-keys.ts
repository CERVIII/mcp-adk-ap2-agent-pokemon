/**
 * RSA Key Management for JWT Signatures
 * Handles loading/generating RSA keys for merchant signatures
 */

import { readFile, writeFile, mkdir } from "fs/promises";
import { existsSync } from "fs";
import { dirname, join } from "path";
import { fileURLToPath } from "url";
import crypto from "crypto";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export interface RSAKeyPair {
  privateKey: string;
  publicKey: string;
}

/**
 * Load existing RSA keys from disk or generate new ones if they don't exist.
 * Keys are stored in mcp-server/keys/ directory for persistence across restarts.
 */
export async function loadOrGenerateRSAKeys(): Promise<RSAKeyPair> {
  const keysDir = join(__dirname, '..', '..', '..', 'keys');
  const privateKeyPath = join(keysDir, 'merchant_private.pem');
  const publicKeyPath = join(keysDir, 'merchant_public.pem');

  try {
    // Try to load existing keys
    if (existsSync(privateKeyPath) && existsSync(publicKeyPath)) {
      console.error('🔑 Loading existing RSA keys from disk...');
      const privateKey = await readFile(privateKeyPath, 'utf8');
      const publicKey = await readFile(publicKeyPath, 'utf8');
      console.error('✅ RSA keys loaded successfully');
      console.error('📝 Public key preview:', publicKey.substring(0, 100) + '...');
      return { privateKey, publicKey };
    }
  } catch (error) {
    console.error('⚠️  Error loading keys, will generate new ones:', error);
  }

  // Generate new keys if they don't exist
  console.error('🔐 Generating new RSA key pair for merchant signatures...');
  const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
    modulusLength: 2048,
    publicKeyEncoding: {
      type: 'spki',
      format: 'pem'
    },
    privateKeyEncoding: {
      type: 'pkcs8',
      format: 'pem'
    }
  });

  // Save keys to disk
  try {
    // Ensure keys directory exists
    await mkdir(keysDir, { recursive: true });
    
    // Write keys with proper permissions
    await writeFile(privateKeyPath, privateKey, { mode: 0o600 }); // Read/write for owner only
    await writeFile(publicKeyPath, publicKey, { mode: 0o644 });   // Read for all
    
    console.error('💾 RSA keys saved to disk');
    console.error('   Private key: keys/merchant_private.pem (600)');
    console.error('   Public key:  keys/merchant_public.pem (644)');
    console.error('📝 Public key preview:', publicKey.substring(0, 100) + '...');
  } catch (error) {
    console.error('❌ Error saving keys to disk:', error);
    console.error('⚠️  Keys will only exist in memory for this session');
  }

  return { privateKey, publicKey };
}
