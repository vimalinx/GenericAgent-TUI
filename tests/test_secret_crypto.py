"""Tests for Secret Vault crypto primitives (ga_tui.app).

Verifies the argon2id key derivation + xchacha20-poly1305 AEAD round-trip,
error handling, and nonce/aad properties. Requires PyNaCl (a project dep).
"""
from __future__ import annotations

import os

import pytest

from ga_tui.app import (
    NACL_XCHACHA_ABYTES,
    NACL_XCHACHA_KEYBYTES,
    NACL_XCHACHA_NPUBBYTES,
    SecretVaultError,
    secret_b64,
    secret_crypto_available,
    secret_decrypt_bytes,
    secret_derive_key,
    secret_encrypt_bytes,
    secret_import_key_id,
    secret_unb64,
)


pytestmark = pytest.mark.skipif(
    not secret_crypto_available(),
    reason="PyNaCl/libsodium not available",
)


@pytest.fixture()
def key() -> bytes:
    return secret_derive_key("correct horse battery staple", os.urandom(16))


class TestKeyDerivation:
    def test_key_length(self) -> None:
        key = secret_derive_key("password", os.urandom(16))
        assert len(key) == NACL_XCHACHA_KEYBYTES

    def test_same_password_different_salt_different_key(self) -> None:
        salt1 = os.urandom(16)
        salt2 = os.urandom(16)
        k1 = secret_derive_key("pw", salt1)
        k2 = secret_derive_key("pw", salt2)
        assert k1 != k2

    def test_wrong_salt_length_raises(self) -> None:
        with pytest.raises(SecretVaultError, match="salt"):
            secret_derive_key("pw", b"tooshort")

    def test_empty_password_still_derives(self) -> None:
        # Empty password is allowed by the KDF; the vault policy (min chars)
        # is enforced elsewhere.
        key = secret_derive_key("", os.urandom(16))
        assert len(key) == NACL_XCHACHA_KEYBYTES


class TestEncryptDecrypt:
    def test_roundtrip(self, key: bytes) -> None:
        plaintext = b"secret message"
        sealed = secret_encrypt_bytes(key, plaintext)
        assert secret_decrypt_bytes(key, sealed) == plaintext

    def test_ciphertext_includes_nonce(self, key: bytes) -> None:
        sealed = secret_encrypt_bytes(key, b"data")
        # nonce is prepended: total = nonce + ciphertext + tag
        assert len(sealed) == NACL_XCHACHA_NPUBBYTES + len(b"data") + NACL_XCHACHA_ABYTES

    def test_nonce_is_random(self, key: bytes) -> None:
        s1 = secret_encrypt_bytes(key, b"data")
        s2 = secret_encrypt_bytes(key, b"data")
        # Nonces (first NPUBBYTES) must differ.
        assert s1[:NACL_XCHACHA_NPUBBYTES] != s2[:NACL_XCHACHA_NPUBBYTES]

    def test_wrong_key_fails(self, key: bytes) -> None:
        sealed = secret_encrypt_bytes(key, b"data")
        other_key = secret_derive_key("other", os.urandom(16))
        with pytest.raises(SecretVaultError):
            secret_decrypt_bytes(other_key, sealed)

    def test_tampered_ciphertext_fails(self, key: bytes) -> None:
        sealed = bytearray(secret_encrypt_bytes(key, b"data"))
        # Flip a bit in the ciphertext body (after nonce).
        sealed[-1] ^= 0x01
        with pytest.raises(SecretVaultError):
            secret_decrypt_bytes(key, bytes(sealed))

    def test_aad_mismatch_fails(self, key: bytes) -> None:
        sealed = secret_encrypt_bytes(key, b"data", aad=b"context-a")
        with pytest.raises(SecretVaultError):
            secret_decrypt_bytes(key, sealed, aad=b"context-b")

    def test_aad_match_succeeds(self, key: bytes) -> None:
        sealed = secret_encrypt_bytes(key, b"data", aad=b"context-a")
        assert secret_decrypt_bytes(key, sealed, aad=b"context-a") == b"data"

    def test_empty_key_rejected(self) -> None:
        with pytest.raises(SecretVaultError, match="key"):
            secret_encrypt_bytes(b"", b"data")

    def test_wrong_key_length_rejected(self) -> None:
        with pytest.raises(SecretVaultError, match="key"):
            secret_encrypt_bytes(b"short", b"data")

    def test_too_short_ciphertext_rejected(self, key: bytes) -> None:
        with pytest.raises(SecretVaultError, match="过短"):
            secret_decrypt_bytes(key, b"short")

    def test_decrypt_empty_plaintext(self, key: bytes) -> None:
        sealed = secret_encrypt_bytes(key, b"")
        assert secret_decrypt_bytes(key, sealed) == b""


class TestBase64Helpers:
    def test_b64_roundtrip(self) -> None:
        data = os.urandom(32)
        assert secret_unb64(secret_b64(data)) == data

    def test_unb64_invalid_raises(self) -> None:
        with pytest.raises(Exception):
            secret_unb64("not!!!valid!!!base64!!!")


class TestImportKeyId:
    def test_stable(self) -> None:
        pk = os.urandom(32)
        assert secret_import_key_id(pk) == secret_import_key_id(pk)

    def test_different_keys_different_id(self) -> None:
        assert secret_import_key_id(os.urandom(32)) != secret_import_key_id(os.urandom(32))

    def test_truncated_to_24(self) -> None:
        pk = os.urandom(32)
        assert len(secret_import_key_id(pk)) == 24
