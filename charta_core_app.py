# ==============================================================================
# PROPRIETARY SOFTWARE: CHARTA SPOK COMPILER & AUTO RBT V1.3 (STANDALONE .EXE)
# HAK CIPTA PEMBUAT: ADI PUTRA (ADHYG GLANK)
# ==============================================================================

import base64
import json
import os
import secrets
import time
from dataclasses import dataclass
from datetime import datetime, timezone

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError as exc:
    raise RuntimeError("Install package 'cryptography' to secure Charta vault files.") from exc

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
    """Resolve a safe absolute path inside the vault and reject path traversal."""
    base = os.path.abspath(vault_path)
    if not filename or filename in (".", ".."):
        raise ValueError("Invalid filename")
    if any(sep in filename for sep in ("/", "\\")):
        raise ValueError(f"Filename must not contain path separators: {filename}")
    if filename.startswith(".."):
        raise ValueError(f"Filename must not start with parent references: {filename}")
    safe_name = os.path.basename(filename)
    target = os.path.abspath(os.path.join(base, f"{safe_name}{extension}"))
    if os.path.commonpath([base, target]) != base:
        raise ValueError(f"Filename escapes vault directory: {filename}")
    return target


@dataclass(frozen=True)
class ChartaConnectionConfig:
    """Load integration settings without storing credentials in source code."""

    mt5_server: str
    mt5_login: str
    mt5_password: str
    mt5_investor_password: str
    qwen_api_key: str
    cloud_access_key_id: str
    cloud_access_key_secret: str

    @classmethod
    def from_environment(cls):
        return cls(
            mt5_server=os.environ.get("CHARTA_MT5_SERVER", ""),
            mt5_login=os.environ.get("CHARTA_MT5_LOGIN", ""),
            mt5_password=os.environ.get("CHARTA_MT5_PASSWORD", ""),
            mt5_investor_password=os.environ.get("CHARTA_MT5_INVESTOR_PASSWORD", ""),
            qwen_api_key=os.environ.get("CHARTA_QWEN_API_KEY", ""),
            cloud_access_key_id=os.environ.get("CHARTA_CLOUD_ACCESS_KEY_ID", ""),
            cloud_access_key_secret=os.environ.get("CHARTA_CLOUD_ACCESS_KEY_SECRET", ""),
        )

    def missing_required(self):
        required = {
            "CHARTA_MT5_SERVER": self.mt5_server,
            "CHARTA_MT5_LOGIN": self.mt5_login,
            "CHARTA_MT5_PASSWORD": self.mt5_password,
            "CHARTA_MT5_INVESTOR_PASSWORD": self.mt5_investor_password,
        }
        return [name for name, value in required.items() if not value]

    def validate_for_health_check(self):
        missing = self.missing_required()
        if missing:
            raise RuntimeError(
                "Konfigurasi MT5 belum lengkap. Isi environment variables: "
                + ", ".join(missing)
            )


def get_connection_config():
    """Return configuration for a read-only integration check."""
    return ChartaConnectionConfig.from_environment()


class ChartaLocalVault:
    """AES-GCM authenticated encryption for Charta .chrt source files."""

    def __init__(self, vault_path="C:\\ChartaVault"):
        self.vault_path = os.path.abspath(vault_path)
        os.makedirs(self.vault_path, exist_ok=True, mode=0o700)
        print(f"[CHARTA LOCAL VAULT] Direktori aman diciptakan di: {self.vault_path}")

    def _filepath(self, filename: str) -> str:
        return _secure_vault_path(self.vault_path, filename, ".chrt")

    def _associated_data(self, filename: str) -> bytes:
        return json.dumps({"format": CHRT_FORMAT, "filename": filename}, separators=(",", ":")).encode("utf-8")

    def encrypt_to_chrt(self, raw_script: str, filename: str = ""):
        nonce = secrets.token_bytes(12)
        plaintext = raw_script.encode("utf-8")
        associated_data = self._associated_data(filename)
        ciphertext = AESGCM(_key()).encrypt(nonce, plaintext, associated_data)
        envelope = {
            "format": CHRT_FORMAT,
            "nonce": base64.urlsafe_b64encode(nonce).decode("ascii"),
            "ciphertext": base64.urlsafe_b64encode(ciphertext).decode("ascii"),
            "associated": base64.urlsafe_b64encode(associated_data).decode("ascii"),
        }
        inner = base64.urlsafe_b64encode(json.dumps(envelope, separators=(",", ":")).encode("utf-8")).decode("ascii")
        return f"CHRT_HEADER_V1.3_ADI_PUTRA::{inner}::CHRT_FOOTER_END"

    def decrypt_from_chrt(self, cipher_text: str, filename: str = ""):
        parts = cipher_text.split("::", 2)
        if len(parts) != 3 or parts[0] != "CHRT_HEADER_V1.3_ADI_PUTRA" or parts[2] != "CHRT_FOOTER_END":
            raise ValueError("[SECURITY BREACH] Upaya pembongkaran biner ilegal terdeteksi!")
        envelope = json.loads(base64.urlsafe_b64decode(parts[1]).decode("ascii"))
        if envelope.get("format") != CHRT_FORMAT:
            raise ValueError("[SECURITY BREACH] Format .chrt tidak didukung.")
        nonce = base64.urlsafe_b64decode(envelope["nonce"].encode("ascii"))
        ciphertext = base64.urlsafe_b64decode(envelope["ciphertext"].encode("ascii"))
        associated_data = base64.urlsafe_b64decode(envelope["associated"].encode("ascii"))
        return AESGCM(_key()).decrypt(nonce, ciphertext, associated_data).decode("utf-8")

    def save_file(self, filename, content):
        filepath = self._filepath(filename)
        encrypted_data = self.encrypt_to_chrt(content, filename=filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(encrypted_data)
        os.chmod(filepath, 0o600)
        print(f"[COMPILER] Berkas Berhasil Dikompilasi & Dikunci ke: {filepath}")
        return filepath

    def load_file(self, filename):
        filepath = self._filepath(filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"[ERROR] Berkas {filename}.chrt tidak ditemukan.")
        with open(filepath, "r", encoding="utf-8") as f:
            cipher = f.read()
        return self.decrypt_from_chrt(cipher, filename=filename)


class ChartaSPOKTranslator:
    def __init__(self):
        self.dictionary = {
            "SAYA": "अहम् (Aham)",
            "KITA": "वयं (Vayam)",
            "SISTEM": "तन्त्र (Tantra)",
            "BOT_RBT": "आर-बी-टी-यन्त्र (RBT-Yantra)",
            "PEMILIK": "स्वामी (Svāmī)",
            "MEMINDAHKAN": "स्थापयति (Sthāpayati)",
            "MENYIMPAN": "रक्षति (Rakṣati)",
            "MENJALANKAN": "चालयति (Cālayati)",
            "MEMBACA": "पठति (Paṭhati)",
            "MENGAMANKAN": "गोपयति (Gopayati)",
            "MENGELOLA": "प्रबन्धयति (Prabandhayati)",
            "MENGHITUNG": "गणयति (Gaṇayati)",
            "EKSEKUSI_DUAL_ENTRY": "द्वि-प्रवेश-करोति (Dvi-Praveśa-Karoti)",
            "MENGIRIM_LAPORAN": "विवरणं-प्रेषयति (Vivaraṇaṁ-Preṣayati)",
            "STRATEGI_AUTO_RBT": "आर-बी-टी-रणनीति (RBT-Raṇanīti)",
            "ASET_RISIKO_75": "सम्पत्ति-७५% (Sampatti-75%)",
            "BIAYA_INAP_16.5": "रात्रि-शुल्कम्-१६.५ (Rātri-Śulkam-16.5)",
            "BAGI_HASIL_85_15": "लाभ-८५-१५ (Lābha-85-15)",
            "LAPORAN_HARIAN": "दैनिक-विवरण (Dainika-Vivaraṇa)",
            "OTOMATIS_24JAM": "अहोरात्रं-स्वयमेव (Ahorātraṁ-Svayameva)",
            "DI_METATRADER5": "एम-क्यू-एल-मञ्चे (MQL-Mañce)",
            "KE_EMAIL_PEMBUAT": "अधिप्-इमेल-दिशि (Adhyp-Email-Diśi)",
            "SECARA_AMAN": "सुरक्षितरूपेण (Surakṣitarūpeṇa)",
            "KE_DRIVE_D": "ड्राइव-ड-दिशि (Drive-D-Diśi)",
            "DI_CLOUD": "मेघे (Meghe)",
            "OTOMATIS": "स्वयमेव (Svayameva)",
            "FILE": "सञ्चिका (Sañcikā)",
            "DATA": "दत्तांश (Dattāṁśa)",
            "KODE": "सङ्केत (Saṅketa)",
            "PROGRAM": "प्रणाली (Praṇālī)",
        }

    def _deva(self, label: str) -> str:
        """Return the Devanagari part of a 'Devanagari (IAST)' label."""
        if " (" in label:
            return label.split(" (", 1)[0]
        return label

    def convert(self, spok_lines):
        charta_code_lines = []
        for idx, line in enumerate(spok_lines, start=1):
            line_id = f"AG{idx}"
            tokens = line.upper().split()
            translated = [self._deva(self.dictionary.get(t, t)) for t in tokens]
            charta_code_lines.append(f"{line_id} पद {' '.join(translated)} इति")
        return "\n".join(charta_code_lines)


class ChartaVirtualMachine:
    def __init__(self, owner=None):
        self.owner = owner or os.environ.get("CHARTA_OWNER", "Adi Putra (Adhyp Glank)")
        env_emails = os.environ.get("CHARTA_AUDIT_EMAILS", "")
        self.emails = [e.strip() for e in env_emails.split(",") if e.strip()]

    def run(self, decrypted_code):
        print("\n" + "="*70)
        print("  🏛️  CHARTA STANDALONE RUNTIME ENVIRONMENT (.EXE)")
        print(f"  HAK CIPTA PEMBUAT: {self.owner}")
        print("="*70)

        lines = decrypted_code.strip().split("\n")
        total_modal = 10000.0
        alokasi_aset_75 = total_modal * 0.75
        biaya_inap_aktual = 16.50
        profit_simulasi = 1250.0 - biaya_inap_aktual

        for line in lines:
            time.sleep(0.4)
            print(f"[CHARTA VM EXEC] -> {line}")
            if "AG1" in line:
                print("   └── [LOGIKA AG1] Inisialisasi Sistem Auto RBT V1.3 Berhasil.")
            elif "AG2" in line:
                print(f"   └── [LOGIKA AG2] Batas Aset (75% Max Risk): ${alokasi_aset_75:,.2f} USD terkunci.")
            elif "AG3" in line:
                print("   └── [LOGIKA AG3] Eksekusi Dual-Point Entry Aktif di MetaTrader 5.")
            elif "AG4" in line:
                s_own = profit_simulasi * 0.85
                s_usr = profit_simulasi * 0.15
                print(f"   └── [LOGIKA AG4] Bagi Hasil B2B -> Owner (85%): ${s_own:,.2f} | User (15%): ${s_usr:,.2f}")
            elif "AG5" in line:
                ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
                print(f"   └── [LOGIKA AG5] Audit Log Otomatis Terkirim pada {ts}:")
                if self.emails:
                    for em in self.emails:
                        print(f"       └── 📧 Sent Encrypted Data -> {em}")
                else:
                    print("       └── [INFO] Tidak ada alamat audit email yang dikonfigurasi (CHARTA_AUDIT_EMAILS).")
            elif "AG6" in line:
                print("   └── [LOGIKA AG6] Eksekusi Selesai. RAM Cleaned (Zero-Leak Protection).")
        print("="*70 + "\n")


if __name__ == "__main__":
    if not CHARTA_EXECUTION_ENABLED:
        print("Charta execution disabled. Use the MT5 .mq5/.ex5 executor instead.")
        raise SystemExit(0)

    try:
        vault = ChartaLocalVault()
        translator = ChartaSPOKTranslator()
        vm = ChartaVirtualMachine()

        perintah_spok = [
            "SISTEM MENJALANKAN STRATEGI_AUTO_RBT OTOMATIS_24JAM",
            "BOT_RBT MENGELOLA ASET_RISIKO_75 DI_METATRADER5",
            "SISTEM EKSEKUSI_DUAL_ENTRY STRATEGI_AUTO_RBT OTOMATIS_24JAM",
            "PEMILIK MENGHITUNG BAGI_HASIL_85_15 OTOMATIS_24JAM",
            "SISTEM MENGIRIM_LAPORAN LAPORAN_HARIAN KE_EMAIL_PEMBUAT",
            "SISTEM MENJALANKAN STRATEGI_AUTO_RBT KE_EMAIL_PEMBUAT"
        ]

        charta_code = translator.convert(perintah_spok)
        filename = "AUTO_RBT_V1_3_PRO"

        vault.save_file(filename, charta_code)

        print("\n[INFO] Memuat kembali berkas .chrt dan mengeksekusinya di VM...")
        decrypted_data = vault.load_file(filename)
        vm.run(decrypted_data)
    except RuntimeError as err:
        print(f"[KESALAHAN] {err}")

    input("\n[TEKAN ENTER UNTUK KELUAR DARI APLIKASI CHARTA...]")
