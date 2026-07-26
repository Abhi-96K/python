#!/usr/bin/env python3
"""
PDF password checker for a known pattern:
    MAUL + DDMMYYYY

Example passwords tried:
    MAUL01012022
    MAUL02012022
    ...
    MAUL31122026

Use only on PDF files you own or have permission to recover.
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta
from pathlib import Path
from typing import Iterator, Optional

try:
    from pypdf import PdfReader, PdfWriter
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: pypdf\n"
        "Install it with:\n"
        "  python3 -m pip install pypdf"
    ) from exc


def generate_passwords(prefix: str = "MAUL") -> Iterator[str]:
    """Generate passwords in MAUL + DDMMYYYY format for all valid dates from 2022 to 2026."""
    current = date(2022, 1, 1)
    end = date(2026, 12, 31)

    while current <= end:
        yield prefix + current.strftime("%d%m%Y")
        current += timedelta(days=1)


def try_password(pdf_path: Path, password: str) -> bool:
    """Return True if password decrypts the PDF successfully."""
    try:
        reader = PdfReader(str(pdf_path))

        if not reader.is_encrypted:
            print("This PDF is not encrypted. No password needed.")
            return True

        result = reader.decrypt(password)

        if result == 0:
            return False

        # Force-read metadata/page count to confirm decryption really worked.
        _ = len(reader.pages)
        return True

    except Exception:
        return False


def find_password(pdf_path: Path, prefix: str = "MAUL") -> Optional[str]:
    reader = PdfReader(str(pdf_path))
    if not reader.is_encrypted:
        print("This PDF is not encrypted. No password needed.")
        return None

    total = 0

    for password in generate_passwords(prefix):
        total += 1
        print(f"Trying {total:03d}: {password}", end="\r")

        if try_password(pdf_path, password):
            print(" " * 60, end="\r")
            return password

    print(" " * 60, end="\r")
    return None


def save_decrypted_copy(pdf_path: Path, password: str, output_path: Path) -> None:
    """Save a decrypted copy after the correct password is found."""
    reader = PdfReader(str(pdf_path))
    if reader.is_encrypted:
        reader.decrypt(password)

    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    with output_path.open("wb") as output_file:
        writer.write(output_file)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check a PDF password using pattern MAUL + DDMMYYYY for all dates from 2022 to 2026."
    )
    parser.add_argument("pdf", help="Path to the encrypted PDF file")
    parser.add_argument(
        "--prefix",
        default="MAUL",
        help="Fixed password prefix. Default: MAUL",
    )
    parser.add_argument(
        "--save-decrypted",
        action="store_true",
        help="Save a decrypted copy after the password is found",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output path for decrypted PDF. Default: <original>_decrypted.pdf",
    )

    args = parser.parse_args()
    pdf_path = Path(args.pdf).expanduser().resolve()

    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    reader = PdfReader(str(pdf_path))

    print(f"PDF: {pdf_path}")
    print(f"Pattern: {args.prefix} + DDMMYYYY")
    print("Trying all valid dates from 01-01-2022 to 31-12-2026...\n")

    if not reader.is_encrypted:
        print("This PDF is not encrypted. No password needed.")
        if args.save_decrypted:
            output_path = (
                Path(args.output).expanduser().resolve()
                if args.output
                else pdf_path.with_name(pdf_path.stem + "_decrypted.pdf")
            )
            save_decrypted_copy(pdf_path, "", output_path)
            print(f"✅ Decrypted PDF saved at: {output_path}")
        return

    password = find_password(pdf_path, args.prefix)

    if password:
        print(f"✅ Password found: {password}")

        if args.save_decrypted:
            output_path = (
                Path(args.output).expanduser().resolve()
                if args.output
                else pdf_path.with_name(pdf_path.stem + "_decrypted.pdf")
            )
            save_decrypted_copy(pdf_path, password, output_path)
            print(f"✅ Decrypted PDF saved at: {output_path}")
    else:
        print("❌ Password not found in MAUL + DDMMYYYY format from 2022 to 2026.")


if __name__ == "__main__":
    main()
