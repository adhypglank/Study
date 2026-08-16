# ==============================================================================
# PROPRIETARY SOFTWARE: CHARTA SPOK COMPILER & SECURE ENGINE V1.3
# HAK CIPTA PEMBUAT: ADI PUTRA (ADHYG GLANK)
# ==============================================================================

import base64
import json
import os
import secrets

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError as exc:
    raise RuntimeError("Install package 'cryptography' to secure Charta vault files.") from exc


CHARTA_VAULT_PATH = os.environ.get("CHARTA_VAULT_PATH", "C:\\ChartaVault")
CHARTA_EXECUTION_ENABLED = True
CHRT_FORMAT = "CHRT-AESGCM-1"
KEY_ENV = "CHARTA_MASTER_KEY"


def _key() -> bytes:
    """Load a 32-byte AES key from the CHARTA_MASTER_KEY environment variable."""
    encoded = os.environ.get(KEY_ENV)
    if not encoded:
        raise RuntimeError(
            f"Set {KEY_ENV} to a base64-urlsafe 32-byte key. "
            "Generate one with: python -c \"import base64, secrets; "
            "print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())\""
        )
    try:
        key = base64.urlsafe_b64decode(encoded.encode("ascii"))
    except Exception as exc:
        raise RuntimeError(f"Invalid {KEY_ENV} value") from exc
    if len(key) != 32:
        raise RuntimeError(f"{KEY_ENV} must decode to exactly 32 bytes")
    return key


def _secure_vault_path(vault_path: str, filename: str, extension: str = ".chrt") -> str:
    """Resolve a safe absolute path inside the vault and block path traversal."""
    base = os.path.abspath(vault_path)
    safe_name = os.path.basename(filename).replace("..", "")
    if not safe_name or safe_name in (".", ".."):
        raise ValueError("Invalid filename")
    target = os.path.abspath(os.path.join(base, f"{safe_name}{extension}"))
    if os.path.commonpath([base, target]) != base:
        raise ValueError(f"Filename escapes vault directory: {filename}")
    return target


class ChartaSPOKCompiler:
    def __init__(self, vault_path):
        self.vault_path = vault_path
        # Kamus Semantik: Menerjemahkan Kata Kunci SPOK ke Aksara Dewanagari Charta
        self.spok_dictionary = {
            # Subjek (S)
            "SAYA": "अहम् (Aham)",
            "KITA": "वयं (Vayam)",
            "SISTEM": "तन्त्र (Tantra)",
            "BOT_RBT": "आर-बी-टी-यन्त्र (RBT-Yantra)",
            "PEMILIK": "स्वामी (Svāmī)",

            # Predikat (P)
            "MEMINDAHKAN": "स्थापयति (Sthāpayati)",
            "MENYIMPAN": "रक्षति (Rakṣati)",
            "MENJALANKAN": "चालयति (Cālayati)",
            "MEMBACA": "पठति (Paṭhati)",
            "MENGAMANKAN": "गोपयति (Gopayati)",
            "MENGELOLA": "प्रबन्धयति (Prabandhayati)",
            "MENGHITUNG": "गणयति (Gaṇayati)",
            "EKSEKUSI_DUAL_ENTRY": "द्वि-प्रवेश-करोति (Dvi-Praveśa-Karoti)",
            "MENGIRIM_LAPORAN": "विवरणं-प्रेषयति (Vivaraṇaṁ-Preṣayati)",

            # Objek (O)
            "FILE": "सञ्चिका (Sañcikā)",
            "DATA": "दत्तांश (Dattāṁśa)",
            "PROGRAM": "प्रणाली (Praṇālī)",
            "KODE": "सङ्केत (Saṅketa)",
            "STRATEGI_AUTO_RBT": "आर-बी-टी-रणनीति (RBT-Raṇanīti)",
            "ASET_RISIKO_75": "सम्पत्ति-७५% (Sampatti-75%)",
            "BIAYA_INAP_16.5": "रात्रि-शुल्कम्-१६.५ (Rātri-Śulkam-16.5)",
            "BAGI_HASIL_85_15": "लाभ-८५-१५ (Lābha-85-15)",
            "LAPORAN_HARIAN": "दैनिक-विवरण (Dainika-Vivaraṇa)",

            # Keterangan (K)
            "OTOMATIS": "स्वयमेव (Svayameva)",
            "OTOMATIS_24JAM": "अहोरात्रं-स्वयमेव (Ahorātraṁ-Svayameva)",
            "SECARA_AMAN": "सुरक्षितरूपेण (Surakṣitarūpeṇa)",
            "DI_METATRADER5": "एम-क्यू-एल-मञ्चे (MQL-Mañce)",
            "KE_EMAIL_PEMBUAT": "अधिप्-इमेल-दिशि (Adhyp-Email-Diśi)",
            "KE_DRIVE_D": "ड्राइव-ड-दिशि (Drive-D-Diśi)",
            "DI_CLOUD": "मेघे (Meghe)",
        }

    def translate_to_charta(self, spok_sentence):
        """Menerjemahkan kalimat SPOK natural menjadi format Charta Code (Devanagari + AG)"""
        words = spok_sentence.upper().split()
        translated_tokens = []

        for word in words:
            if word in self.spok_dictionary:
                translated_tokens.append(self.spok_dictionary[word])
            else:
                translated_tokens.append(word)  # Pertahankan kata khusus jika tidak ada di kamus

        return " ".join(translated_tokens)

    def compile_and_lock(self, filename, spok_sentences):
        """Mengompilasi kalimat SPOK menjadi Charta Code, lalu menguncinya ke format .chrt biner"""
        charta_script_lines = []

        for idx, sentence in enumerate(spok_sentences, start=1):
            line_id = f"AG{idx}"
            devanagari_translation = self.translate_to_charta(sentence)
            # Format baku Charta Code: [ID_AG] [Devanagari SPOK] इति (Selesai)
            script_line = f"{line_id} पद {devanagari_translation} इति"
            charta_script_lines.append(script_line)

        full_script = "\n".join(charta_script_lines)

        os.makedirs(self.vault_path, exist_ok=True, mode=0o700)

        nonce = secrets.token_bytes(12)
        plaintext = full_script.encode("utf-8")
        associated_data = json.dumps({"format": CHRT_FORMAT, "filename": filename}, separators=(",", ":")).encode("utf-8")
        ciphertext = AESGCM(_key()).encrypt(nonce, plaintext, associated_data)
        envelope = {
            "format": CHRT_FORMAT,
            "nonce": base64.urlsafe_b64encode(nonce).decode("ascii"),
            "ciphertext": base64.urlsafe_b64encode(ciphertext).decode("ascii"),
            "associated": base64.urlsafe_b64encode(associated_data).decode("ascii"),
        }

        filepath = _secure_vault_path(self.vault_path, filename, ".chrt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json.dumps(envelope, separators=(",", ":")))
        os.chmod(filepath, 0o600)

        print(f"\n[CHARTA COMPILER] Berhasil dikompilasi & dikunci mutlak ke: {filepath}")
        print("--- Wujud Asli Charta Code (Terkunci dalam Envelope Terenkripsi) ---")
        print(json.dumps(envelope, separators=(",", ":"))[:60] + "... [Terenkripsi AES-GCM]")

    def execute_chrt(self, filename):
        """Mengeksekusi berkas .chrt melalui Charta VM privat"""
        filepath = _secure_vault_path(self.vault_path, filename, ".chrt")
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"[ERROR] Berkas {filename}.chrt tidak ditemukan di Vault.")

        with open(filepath, "r", encoding="utf-8") as f:
            envelope = json.load(f)

        if envelope.get("format") != CHRT_FORMAT:
            raise ValueError("[SECURITY BREACH] Format .chrt tidak didukung.")

        nonce = base64.urlsafe_b64decode(envelope["nonce"].encode("ascii"))
        ciphertext = base64.urlsafe_b64decode(envelope["ciphertext"].encode("ascii"))
        associated_data = base64.urlsafe_b64decode(envelope["associated"].encode("ascii"))

        # Dekripsi hanya terjadi di dalam memori VM Charta
        decoded_script = AESGCM(_key()).decrypt(nonce, ciphertext, associated_data).decode("utf-8")

        print(f"\n--- [CHARTA VM START EXECUTION: {filename}.chrt] ---")
        for line in decoded_script.strip().split("\n"):
            print(f"[EKSEKUSI AMAN] Menerima instruksi VM -> {line}")
        print("--- [CHARTA VM END EXECUTION] ---\n")


# Inisialisasi Kompilator Charta SPOK
charta_engine = None
if CHARTA_EXECUTION_ENABLED:
    charta_engine = ChartaSPOKCompiler(CHARTA_VAULT_PATH)
    print("Charta SPOK Compiler siap menerima perintah natural.")
else:
    print("Charta execution disabled. Use the MT5 .mq5/.ex5 executor instead.")
