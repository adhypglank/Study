"""Charta runtime: authenticated encrypted IR compiler and adapters.

This runtime intentionally compiles a documented Python subset into an IR.
It does not claim to convert arbitrary Python, Python dependencies, or a
trading strategy into portable native code without a semantic port.
"""

from __future__ import annotations

import argparse
import ast
import base64
import json
import os
import platform
import secrets
import sys
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import charta_nirmana
import charta_polyglot

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except ImportError as exc:  # pragma: no cover - environment-dependent
    raise RuntimeError("Install cryptography before using Charta .cht files") from exc


FORMAT = "CHARTA-IR-AESGCM-1"
KEY_ENV = "CHARTA_MASTER_KEY"
RUNTIME_VERSION = "1.0"
IR_ABI = "charta-ir/1"

FORMAT_REGISTRY = (
    ("Python", ".py", "text/x-python", "source", "ast-subset", "partial"),
    ("MQL5", ".mq5", "text/x-mql5", "source", "metaeditor", "adapter"),
    ("MQL5 binary", ".ex5", "application/x-metatrader5", "executable", "metaeditor", "external"),
    ("Charta package", ".cht", "application/vnd.charta+binary", "package", "charta-runtime", "native"),
    ("C", ".c", "text/x-c", "source", "external-compiler", "external"),
    ("C++", ".cpp", "text/x-c++", "source", "external-compiler", "external"),
    ("C#", ".cs", "text/x-csharp", "source", "external-compiler", "external"),
    ("Java", ".java", "text/x-java-source", "source", "external-compiler", "external"),
    ("JavaScript", ".js", "text/javascript", "source", "external-runtime", "external"),
    ("TypeScript", ".ts", "video/mp2t", "source", "external-compiler", "external"),
    ("Rust", ".rs", "text/rust", "source", "external-compiler", "external"),
    ("Go", ".go", "text/x-go", "source", "external-compiler", "external"),
    ("PHP", ".php", "application/x-httpd-php", "source", "external-runtime", "external"),
    ("Ruby", ".rb", "application/x-ruby", "source", "external-runtime", "external"),
    ("HTML", ".html", "text/html", "markup", "browser", "export-text"),
    ("CSS", ".css", "text/css", "markup", "browser", "export-text"),
    ("JSON", ".json", "application/json", "data", "parser", "export-text"),
    ("YAML", ".yaml", "application/yaml", "data", "parser", "export-text"),
    ("XML", ".xml", "application/xml", "data", "parser", "export-text"),
    ("CSV", ".csv", "text/csv", "data", "parser", "export-text"),
    ("SQLite", ".sqlite", "application/vnd.sqlite3", "database", "database-driver", "external"),
    ("PDF", ".pdf", "application/pdf", "document", "document-parser", "external"),
    ("ZIP", ".zip", "application/zip", "archive", "archive-tool", "external"),
    ("GZIP", ".gz", "application/gzip", "archive", "archive-tool", "external"),
    ("PNG", ".png", "image/png", "image", "image-library", "external"),
    ("JPEG", ".jpg", "image/jpeg", "image", "image-library", "external"),
    ("WAV", ".wav", "audio/wav", "audio", "media-library", "external"),
    ("MP3", ".mp3", "audio/mpeg", "audio", "media-library", "external"),
    ("MP4", ".mp4", "video/mp4", "video", "media-library", "external"),
    ("WebAssembly", ".wasm", "application/wasm", "executable", "wasm-runtime", "external"),
    ("Windows executable", ".exe", "application/vnd.microsoft.portable-executable", "executable", "operating-system", "external"),
    ("Linux ELF", ".elf", "application/x-executable", "executable", "operating-system", "external"),
)

SANSKRIT = {
    "assign": "न्यासः (Nyāsaḥ)",
    "call": "आह्वानम् (Āhvānam)",
    "compare": "तुलना (Tulanā)",
    "constant": "मूल्यम् (Mūlyam)",
    "expression": "अभिव्यक्तिः (Abhivyaktiḥ)",
    "function": "कार्यं (Kāryam)",
    "if": "यदि (Yadi)",
    "module": "प्रणाली (Praṇālī)",
    "name": "नाम (Nāma)",
    "return": "प्रतिनिवर्तनम् (Pratinivartanam)",
}

SPOK_DICTIONARY = {
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
    "FILE": "सञ्चिका (Sañcikā)",
    "DATA": "दत्तांश (Dattāṁśa)",
    "KODE": "सङ्केत (Saṅketa)",
    "PROGRAM": "प्रणाली (Praṇālī)",
    "STRATEGI_AUTO_RBT": "आर-बी-टी-रणनीति (RBT-Raṇanīti)",
    "ASET_RISIKO_75": "सम्पत्ति-७५% (Sampatti-75%)",
    "BIAYA_INAP_16.5": "रात्रि-शुल्कम्-१६.५ (Rātri-Śulkam-16.5)",
    "BAGI_HASIL_85_15": "लाभ-८५-१५ (Lābha-85-15)",
    "LAPORAN_HARIAN": "दैनिक-विवरण (Dainika-Vivaraṇa)",
    "OTOMATIS": "स्वयमेव (Svayameva)",
    "OTOMATIS_24JAM": "अहोरात्रं-स्वयमेव (Ahorātraṁ-Svayameva)",
    "DI_METATRADER5": "एम-क्यू-एल-मञ्चे (MQL-Mañce)",
    "KE_EMAIL_PEMBUAT": "अधिप्-इमेल-दिशि (Adhyp-Email-Diśi)",
    "SECARA_AMAN": "सुरक्षितरूपेण (Surakṣitarūpeṇa)",
    "KE_DRIVE_D": "ड्राइव-ड-दिशि (Drive-D-Diśi)",
    "DI_CLOUD": "मेघे (Meghe)",

    # Predikat / konstruksi umum (polyglot)
    "MENAMPILKAN": "दर्शयति (Darśayati)",
    "JIKA": "यदि (Yadi)",
    "JIKA_TIDAK": "अथवा (Athavā)",
    "JIKA_LAIN": "अन्यथा (Anyathā)",
    "ULANG": "पुनरावर्तयति (Punarāvartayati)",
    "ULANG_SELAMA": "पुनरावर्तयति-यावत् (Punarāvartayati-Yāvat)",
    "FUNGSI": "कार्यं (Kāryam)",
    "MENGEMBALIKAN": "प्रतिनिवर्तयति (Pratinivartayati)",
    "MENGGUNAKAN": "उपयुङ्क्ते (Upayuṅkte)",
    "MENGHAPUS": "अपनयति (Apanayati)",
    "MEMASUKKAN": "निवेशयति (Niveśayati)",
    "MEMPERBARUI": "नवीकरोति (Navīkaroti)",
    "MEMILIH": "वृणोति (Vṛṇoti)",
    "CEK": "परीक्षयति (Parīkṣayati)",
    "COBA": "यतते (Yatate)",
    "KECUALI": "वर्जयति (Varjayati)",
    "BUKA": "उद्घाटयति (Udghāṭayati)",
    "TULIS": "लिखति (Likhati)",
    "PASANG": "संस्थापयति (Saṃsthāpayati)",
    "BANGUN": "निर्माति (Nirmāti)",

    # Predikat MQL5 / MetaTrader
    "KIRIM_PESANAN": "आदेशं-प्रेषयति (Ādeśaṁ-Preṣayati)",
    "TUTUP_PESANAN": "आदेशं-पिदधाति (Ādeśaṁ-Pidadhāti)",
    "HITUNG_MA": "माध्यम-गणयति (Mādhyama-Gaṇayati)",
    "SAAT_TIK": "तिक्-समये (Tik-Samaye)",
    "BACA_PASAR": "बाजारं-पठति (Bājāraṁ-Paṭhati)",

    # Predikat sistem / file / web
    "PINDAH_DIREKTORI": "मार्ग-स्थापयति (Mārga-Sthāpayati)",
    "MENYALIN": "अनुलिखति (Anulikhati)",
    "KELAS": "वर्ग (Varga)",
    "HALAMAN": "पृष्ठ (Pṛṣṭha)",
    "GAYA": "शैली (Śailī)",
    "TOMBOL": "पिण्ड (Piṇḍa)",
    "KLIK": "नुदति (Nudati)",

    # Objek / keterangan tambahan
    "PESAN": "सन्देश (Sandēśa)",
    "KONDISI": "अवस्था (Avasthā)",
    "DAFTAR": "सूची (Sūcī)",
    "NAMA": "नाम (Nāma)",
    "NILAI": "मूल्य (Mūlya)",
    "MODUL": "प्रणाली (Praṇālī)",
    "DARI": "स्मात् (Smāt)",
    "DIMANA": "यत्र (Yatra)",
    "ORDER": "आदेश (Ādeśa)",
    "PASAR": "बाजार (Bājāra)",
    "APLIKASI": "अनुप्रयोग (Anuprayoga)",
    "SIMBOL": "चिह्न (Cihna)",

    # Predikat Charta Nirmāṇa (AI/ML)
    "MUAT_MODEL": "आरोपयति (Āropayati)",
    "LATIH_MODEL": "अभ्यस्यति (Abhyasyati)",
    "INFERENSI": "अनुमानयति (Anumānayati)",
    "SIAPKAN_DATA": "सज्जयति (Sajjayati)",
    "EVALUASI_MODEL": "मूल्यांकयति (Mūlyāṅkayati)",
    "SIMPAN_MODEL": "संरक्षति (Saṃrakṣati)",
    "PREDIKSI": "पूर्वानुमानयति (Pūrvānumānayati)",

    # Objek / keterangan Charta Nirmāṇa
    "MODEL": "प्रतिरूप (Pratirūpa)",
    "DATASET": "दत्तसङ्ग्रह (Dattasaṅgraha)",
    "FITUR": "विशेषण (Viśeṣaṇa)",
    "LABEL": "लक्ष्य (Lakṣya)",
    "HASIL": "फल (Phala)",
    "AKURASI": "यथार्थता (Yathārthatā)",
    "METRIK": "मापदण्ड (Māpadaṇḍa)",
    "JARINGAN": "जाल (Jāla)",
}


@dataclass(frozen=True)
class Instruction:
    op: str
    data: dict[str, Any]
    sanskrit: str


@dataclass(frozen=True)
class ChartaModule:
    name: str
    source_language: str
    instructions: tuple[Instruction, ...]


class UnsupportedPython(Exception):
    pass


def _literal(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant) and isinstance(node.value, (str, int, float, bool, type(None))):
        return node.value
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_literal(item) for item in node.elts]
    raise UnsupportedPython(f"Unsupported literal: {type(node).__name__}")


def _expr(node: ast.AST) -> dict[str, Any]:
    if isinstance(node, ast.Constant):
        return {"kind": "constant", "value": _literal(node)}
    if isinstance(node, ast.Name):
        return {"kind": "name", "value": node.id}
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return {"kind": "attribute", "owner": node.value.id, "value": node.attr}
    if isinstance(node, ast.Call):
        if not isinstance(node.func, (ast.Name, ast.Attribute)):
            raise UnsupportedPython("Only named function calls are supported")
        function = _expr(node.func)
        return {
            "kind": "call",
            "function": function,
            "args": [_expr(arg) for arg in node.args],
            "keywords": {item.arg: _expr(item.value) for item in node.keywords if item.arg},
        }
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        operator = type(node.ops[0]).__name__
        return {"kind": "compare", "left": _expr(node.left), "operator": operator, "right": _expr(node.comparators[0])}
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
        return {"kind": "binary", "operator": type(node.op).__name__, "left": _expr(node.left), "right": _expr(node.right)}
    raise UnsupportedPython(f"Unsupported expression: {type(node).__name__}")


def compile_python(source: str, name: str = "module") -> ChartaModule:
    tree = ast.parse(source, filename=f"{name}.py")
    instructions: list[Instruction] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            instructions.append(Instruction("assign", {"target": node.targets[0].id, "value": _expr(node.value)}, SANSKRIT["assign"]))
        elif isinstance(node, ast.Expr):
            instructions.append(Instruction("expression", {"value": _expr(node.value)}, SANSKRIT["expression"]))
        elif isinstance(node, ast.FunctionDef):
            instructions.append(Instruction("function", {"name": node.name, "args": [arg.arg for arg in node.args.args]}, SANSKRIT["function"]))
        elif isinstance(node, ast.Return):
            instructions.append(Instruction("return", {"value": _expr(node.value) if node.value else None}, SANSKRIT["return"]))
        else:
            raise UnsupportedPython(f"Unsupported statement: {type(node).__name__}")
    return ChartaModule(name, "python-subset", tuple(instructions))


def compile_spok(source: str, name: str = "spok_module") -> ChartaModule:
    """Compile one Indonesian SPOK sentence per line into Charta IR."""
    instructions: list[Instruction] = []
    for line_number, raw_line in enumerate(source.splitlines(), 1):
        words = raw_line.strip().upper().split()
        if not words:
            continue
        if len(words) < 3:
            raise ValueError(f"SPOK line {line_number} needs Subject Predicate Object")
        subject, predicate, object_word = words[:3]
        context = words[3:]
        translate = lambda word: SPOK_DICTIONARY.get(word, word)
        instructions.append(Instruction(
            "spok",
            {
                "subject": subject,
                "predicate": predicate,
                "object": object_word,
                "context": context,
                "sanskrit": {
                    "subject": translate(subject),
                    "predicate": translate(predicate),
                    "object": translate(object_word),
                    "context": [translate(word) for word in context],
                },
            },
            "वाक्यम् (Vākyam)",
        ))
    if not instructions:
        raise ValueError("SPOK source contains no sentences")
    return ChartaModule(name, "indonesian-spok", tuple(instructions))


def _key() -> bytes:
    encoded = os.environ.get(KEY_ENV)
    if not encoded:
        raise RuntimeError(f"Set {KEY_ENV} to a base64-encoded 32-byte key")
    try:
        key = base64.urlsafe_b64decode(encoded.encode("ascii"))
    except Exception as exc:
        raise RuntimeError(f"Invalid {KEY_ENV}") from exc
    if len(key) != 32:
        raise RuntimeError(f"{KEY_ENV} must decode to exactly 32 bytes")
    return key


def generate_key() -> str:
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode("ascii")


def build_manifest(module: ChartaModule) -> dict[str, Any]:
    return {
        "format": FORMAT,
        "runtime": "charta-runtime",
        "runtime_version": RUNTIME_VERSION,
        "ir_abi": IR_ABI,
        "module": module.name,
        "source_language": module.source_language,
        "target_os": platform.system().lower(),
        "target_arch": platform.machine().lower(),
        "capabilities": ["ir", "sanskrit-trace"],
        "dependencies": ["cryptography>=42.0"],
    }


def pack(module: ChartaModule, output: Path) -> None:
    nonce = secrets.token_bytes(12)
    manifest = build_manifest(module)
    plaintext = json.dumps({"manifest": manifest, "instructions": [asdict(item) for item in module.instructions]}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    associated_data = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ciphertext = AESGCM(_key()).encrypt(nonce, plaintext, associated_data)
    envelope = {"format": FORMAT, "manifest": manifest, "nonce": base64.urlsafe_b64encode(nonce).decode("ascii"), "ciphertext": base64.urlsafe_b64encode(ciphertext).decode("ascii")}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(json.dumps(envelope, separators=(",", ":")).encode("ascii"))
    os.chmod(output, 0o600)


def unpack(path: Path) -> ChartaModule:
    envelope = json.loads(path.read_bytes().decode("ascii"))
    if envelope.get("format") != FORMAT:
        raise ValueError("Unsupported Charta package format")
    manifest = envelope.get("manifest")
    if not isinstance(manifest, dict) or manifest.get("ir_abi") != IR_ABI:
        raise ValueError("Unsupported Charta IR ABI")
    nonce = base64.urlsafe_b64decode(envelope["nonce"])
    ciphertext = base64.urlsafe_b64decode(envelope["ciphertext"])
    associated_data = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    plaintext = AESGCM(_key()).decrypt(nonce, ciphertext, associated_data)
    data = json.loads(plaintext.decode("utf-8"))
    if data.get("manifest") != manifest:
        raise ValueError("Charta manifest integrity check failed")
    return ChartaModule(manifest["module"], manifest["source_language"], tuple(Instruction(**item) for item in data["instructions"]))


def inspect_package(path: Path) -> None:
    envelope = json.loads(path.read_bytes().decode("ascii"))
    manifest = envelope.get("manifest", {})
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


@lru_cache(maxsize=None)
def _deva(label: str) -> str:
    """Return the Devanagari part of a 'Devanagari (IAST)' label."""
    if " (" in label:
        return label.rsplit(" (", 1)[0]
    return label


def to_charta(module: ChartaModule) -> str:
    lines = []
    for index, item in enumerate(module.instructions, 1):
        if item.op == "spok":
            s = item.data["sanskrit"]
            words = [
                _deva(s["subject"]),
                _deva(s["predicate"]),
                _deva(s["object"]),
                *[_deva(w) for w in s["context"]],
            ]
            lines.append(f"AG{index} पद {' '.join(words)} इति")
        else:
            lines.append(f"AG{index} पद {_deva(item.sanskrit)} {item.op} इति")
    return "\n".join(lines)


def to_python(module: ChartaModule) -> str:
    lines = [f"# Generated by Charta runtime from {module.name}.cht"]
    for item in module.instructions:
        if item.op == "spok":
            data = item.data
            if charta_nirmana.is_ai_command(data["predicate"]):
                lines.append(charta_nirmana.to_python(data))
            else:
                lines.append(f"# SPOK: {data['subject']} {data['predicate']} {data['object']} {' '.join(data['context'])}")
        elif item.op == "assign":
            lines.append(f"{item.data['target']} = {repr(item.data['value'])}")
        elif item.op == "function":
            lines.append(f"def {item.data['name']}({', '.join(item.data['args'])}):\n    pass")
        else:
            lines.append(f"# Charta IR: {item.op} {item.data}")
    return "\n".join(lines) + "\n"


def to_mq5(module: ChartaModule) -> str:
    lines = [
        "// Generated by Charta runtime; review before attaching to a live account.",
        "// MetaTrader 5 reads Charta decisions via the ZeroMQ bridge (charta_mt5_bridge.py).",
        "#property strict",
        "#include <charta_bridge.mqh>",
        "input string ChartaTopic = \"charta/signals\";",
        "",
        "void OnTick()",
        "{",
        "   string signal = ChartaRequest(ChartaTopic);",
        "   if(StringLen(signal) == 0) return;",
        "   // Charta IR instructions are intentionally explicit for review.",
    ]
    for index, item in enumerate(module.instructions, 1):
        if item.op == "spok":
            data = item.data
            lines.append(f"   // AG{index} SPOK: {data['subject']} {data['predicate']} {data['object']} {' '.join(data['context'])}")
            lines.append(f"   ProcessChartaSignal(signal, \"AG{index}\");")
        else:
            lines.append(f"   // AG{index}: {item.sanskrit} {item.op}")
    lines.extend(["}", ""])
    return "\n".join(lines)


def _spok_sentence(data: dict[str, Any]) -> str:
    ctx = " ".join(data.get("context", []))
    return f"{data['subject']} {data['predicate']} {data['object']}{' ' + ctx if ctx else ''}"


def to_article(module: ChartaModule) -> str:
    title = f"Artikel Eksekusi Charta: {module.name}"
    paragraphs = [f"{title}\n" + "=" * len(title), ""]
    paragraphs.append("Program berikut disusun dengan pola SPOK (Subyek-Predikat-Obyek-Keterangan) dalam bahasa Indonesia, kemudian diterjemahkan ke aksara Sanskerta dan dikemas dalam format .cht bersertifikat.")
    paragraphs.append("")
    for index, item in enumerate(module.instructions, 1):
        if item.op == "spok":
            paragraphs.append(f"Langkah {index}. {_spok_sentence(item.data)}.")
    paragraphs.append("")
    paragraphs.append("Setiap langkah di atas dijalankan secara otomatis dan aman oleh Charta Runtime melalui AES-GCM, sehingga makna asli hanya dapat dibuka dengan kunci pribadi.")
    return "\n".join(paragraphs) + "\n"


def to_story(module: ChartaModule) -> str:
    lines = [f"Kisah Eksekusi Charta: {module.name}", ""]
    lines.append("Pada sebuah sesi perdagangan, Sistem Charta mulai bercerita.")
    for item in module.instructions:
        if item.op == "spok":
            sentence = _spok_sentence(item.data)
            # Simple narrative connectors
            if item.data["predicate"] in ("MENJALANKAN", "JALANKAN"):
                lines.append(f"Tanpa suara, {sentence}, seolah menyatu dengan mesin.")
            elif item.data["predicate"] in ("MENGIRIM_LAPORAN",):
                lines.append(f"Kemudian, {sentence}, membawa kabar terbaru ke pemiliknya.")
            elif item.data["predicate"] in ("MENGHITUNG",):
                lines.append(f"Dengan teliti, {sentence}, memastikan tiap bagian berada pada tempatnya.")
            else:
                lines.append(f"Lalu, {sentence}.")
    lines.append("")
    lines.append("Demikianlah kisah Charta: terlihat sebagai aksara Sanskerta, tetapi dibaliknya berdenyut logika Python yang terlindungi rapat.")
    return "\n".join(lines) + "\n"


def format_rows() -> list[dict[str, str]]:
    fields = ("name", "extension", "mime", "category", "adapter", "support")
    return [dict(zip(fields, row)) for row in FORMAT_REGISTRY]


def print_formats() -> None:
    print("NAME\tEXTENSION\tMIME\tCATEGORY\tADAPTER\tSUPPORT")
    for row in format_rows():
        print("\t".join(row.values()))


def print_spok_help() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    print("POLA: SUBYEK PREDIKAT OBYEK KETERANGAN")
    print("\nPADANAN SPOK -> AKSARA SANSKERTA -> OPERASI CHARTA")
    rows = (
        ("SAYA / KITA / SISTEM", "अहम् / वयं / तन्त्र", "name / module"),
        ("MENJALANKAN", "चालयति", "call"),
        ("MENYIMPAN", "रक्षति", "assign / call"),
        ("MEMBACA", "पठति", "call"),
        ("MENGELOLA", "प्रबन्धयति", "call"),
        ("MENGHITUNG", "गणयति", "expression"),
        ("FILE / DATA / KODE", "सञ्चिका / दत्तांश / सङ्केत", "constant / name"),
        ("OTOMATIS / SECARA_AMAN", "स्वयमेव / सुरक्षितरूपेण", "context"),
        ("DI_METATRADER5", "एम-क्यू-एल-मञ्चे", "adapter: MQL5 review"),
    )
    for subject, sanskrit, operation in rows:
        print(f"{subject}\t{sanskrit}\t{operation}")
    print("\nCONTOH:")
    print("SISTEM MENJALANKAN STRATEGI_AUTO_RBT OTOMATIS_24JAM")
    print("-> AG1 पद तन्त्र चालयति आर-बी-टी-रणनीति अहोरात्रं इति")
    print("\nGunakan compile-spok untuk membuat paket .cht terenkripsi.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile and inspect encrypted Charta IR packages")
    subparsers = parser.add_subparsers(dest="command", required=True)
    key_parser = subparsers.add_parser("key")
    key_parser.set_defaults(action=lambda _: print(generate_key()))
    formats_parser = subparsers.add_parser("formats", help="List registered formats and adapters")
    formats_parser.set_defaults(action=lambda _: print_formats())
    spok_help_parser = subparsers.add_parser("spok-help", help="Show Indonesian SPOK and Sanskrit mappings")
    spok_help_parser.set_defaults(action=lambda _: print_spok_help())
    polyglot_parser = subparsers.add_parser("polyglot-help", help="List supported polyglot languages")
    polyglot_parser.set_defaults(action=lambda _: print("\n".join(charta_polyglot.supported_languages())))
    inspect_parser = subparsers.add_parser("inspect", help="Show package manifest without decrypting code")
    inspect_parser.add_argument("package", type=Path)
    inspect_parser.set_defaults(action=lambda args: inspect_package(args.package))
    compile_parser = subparsers.add_parser("compile-python")
    compile_parser.add_argument("source", type=Path)
    compile_parser.add_argument("output", type=Path)
    compile_parser.set_defaults(action=lambda args: pack(compile_python(args.source.read_text(encoding="utf-8"), args.source.stem), args.output))
    spok_parser = subparsers.add_parser("compile-spok", help="Compile Indonesian SPOK sentences into encrypted .cht")
    spok_parser.add_argument("source", type=Path)
    spok_parser.add_argument("output", type=Path)
    spok_parser.set_defaults(action=lambda args: pack(compile_spok(args.source.read_text(encoding="utf-8"), args.source.stem), args.output))
    polyglot_compile_parser = subparsers.add_parser("compile-polyglot", help="Compile code from Python/JS/C/MQL5/SQL/etc. into encrypted .cht")
    polyglot_compile_parser.add_argument("source", type=Path)
    polyglot_compile_parser.add_argument("output", type=Path)
    polyglot_compile_parser.add_argument("--language", type=str, default=None, help="Language override (e.g. python, mql5, sql)")
    polyglot_compile_parser.set_defaults(
        action=lambda args: pack(
            compile_spok(
                charta_polyglot.to_spok(args.source.read_text(encoding="utf-8"), args.language, args.source),
                args.source.stem,
            ),
            args.output,
        )
    )
    translate_parser = subparsers.add_parser("translate-code", help="Show SPOK translation of a source file without compiling")
    translate_parser.add_argument("source", type=Path)
    translate_parser.add_argument("--language", type=str, default=None)
    translate_parser.set_defaults(
        action=lambda args: print(
            charta_polyglot.to_spok(args.source.read_text(encoding="utf-8"), args.language, args.source)
        )
    )
    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("package", type=Path)
    export_parser.add_argument("format", choices=("charta", "python", "mq5", "article", "story"))
    export_parser.set_defaults(action=lambda args: print({"charta": to_charta, "python": to_python, "mq5": to_mq5, "article": to_article, "story": to_story}[args.format](unpack(args.package)), end=""))
    args = parser.parse_args()
    args.action(args)


if __name__ == "__main__":
    main()
