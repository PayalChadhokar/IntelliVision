import json
import re
import urllib.request
from pathlib import Path

from database.connection import get_db_connection


# ============================================================
# CONFIGURATION
# ============================================================

DATASET_URL = (
    "https://huggingface.co/datasets/"
    "GSMS-B/indian-legal-sections-bns-bnss-bsa-2023/"
    "resolve/main/bns_bnss_bsa_sections.json"
)

LOCAL_DATA_DIR = Path(__file__).resolve().parent / "legal_data"
LOCAL_DATA_FILE = LOCAL_DATA_DIR / "bns_bnss_bsa_sections.json"


ACT_DETAILS = {
    "BNS 2023": {
        "act_code": "BNS",
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "short_name": "BNS",
        "act_year": 2023,
        "act_category": "OFFENCE",
        "description": (
            "Substantive criminal law defining offences and punishments."
        ),
    },
    "BNSS 2023": {
        "act_code": "BNSS",
        "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023",
        "short_name": "BNSS",
        "act_year": 2023,
        "act_category": "PROCEDURE",
        "description": (
            "Criminal procedure law governing investigation, "
            "arrest, trial and related procedures."
        ),
    },
    "BSA 2023": {
        "act_code": "BSA",
        "act_name": "Bharatiya Sakshya Adhiniyam, 2023",
        "short_name": "BSA",
        "act_year": 2023,
        "act_category": "EVIDENCE",
        "description": (
            "Law governing admissibility and proof of evidence."
        ),
    },
}


DATASET_SOURCE_NAME = (
    "GSMS-B Indian Legal Sections Dataset "
    "(BNS, BNSS and BSA 2023)"
)

DATASET_SOURCE_URL = (
    "https://huggingface.co/datasets/"
    "GSMS-B/indian-legal-sections-bns-bnss-bsa-2023"
)


# ============================================================
# DOWNLOAD DATASET
# ============================================================

def download_dataset():
    """
    Download the combined 1,059-section JSON dataset
    if it is not already present locally.
    """

    LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if LOCAL_DATA_FILE.exists():
        print("\n[DATASET] Local dataset already exists.")
        print(f"[DATASET] {LOCAL_DATA_FILE}")
        return

    print("\n[DATASET] Downloading legal dataset...")
    print("[DATASET] Source:")
    print(DATASET_URL)

    try:
        urllib.request.urlretrieve(
            DATASET_URL,
            LOCAL_DATA_FILE
        )

        print("[DATASET] Download completed.")

    except Exception as e:
        print("\n[ERROR] Could not download dataset.")
        print(f"[ERROR] {e}")
        raise


# ============================================================
# LOAD JSON
# ============================================================

def load_dataset():
    print("\n[DATASET] Reading JSON file...")

    with open(
        LOCAL_DATA_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            "Expected the dataset JSON to contain a list."
        )

    print(
        f"[DATASET] Records found: {len(data)}"
    )

    return data


# ============================================================
# CHAPTER NUMBER
# ============================================================

def extract_chapter_number(chapter_text):
    """
    Extract chapter number from strings such as:

    CHAPTER VI OF OFFENCES AFFECTING THE HUMAN BODY
    CHAPTER XVIII OF OFFENCES RELATING TO DOCUMENTS
    """

    if not chapter_text:
        return None

    match = re.search(
        r"CHAPTER\s+([IVXLCDM]+|\d+)",
        chapter_text,
        re.IGNORECASE
    )

    if not match:
        return None

    value = match.group(1).upper()

    # Roman numeral → integer
    roman_values = {
        "I": 1,
        "II": 2,
        "III": 3,
        "IV": 4,
        "V": 5,
        "VI": 6,
        "VII": 7,
        "VIII": 8,
        "IX": 9,
        "X": 10,
        "XI": 11,
        "XII": 12,
        "XIII": 13,
        "XIV": 14,
        "XV": 15,
        "XVI": 16,
        "XVII": 17,
        "XVIII": 18,
        "XIX": 19,
        "XX": 20,
        "XXI": 21,
        "XXII": 22,
        "XXIII": 23,
        "XXIV": 24,
        "XXV": 25,
        "XXVI": 26,
        "XXVII": 27,
        "XXVIII": 28,
        "XXIX": 29,
        "XXX": 30,
        "XXXI": 31,
        "XXXII": 32,
        "XXXIII": 33,
        "XXXIV": 34,
        "XXXV": 35,
        "XXXVI": 36,
        "XXXVII": 37,
        "XXXVIII": 38,
        "XXXIX": 39,
    }

    if value in roman_values:
        return str(roman_values[value])

    return value


# ============================================================
# KEYWORD GENERATION
# ============================================================

def generate_keywords(section_title, section_text):
    """
    Generate simple searchable keywords.

    These are NOT used as legal authority.
    They are only used to improve database retrieval.
    """

    words = []

    if section_title:
        words.extend(
            re.findall(
                r"[A-Za-z0-9]+",
                section_title.lower()
            )
        )

    # Add selected words from the first part of section text.
    if section_text:
        text_words = re.findall(
            r"[A-Za-z0-9]+",
            section_text.lower()
        )

        words.extend(text_words[:40])

    # Remove duplicates while preserving order.
    unique_words = []

    for word in words:
        if len(word) >= 3 and word not in unique_words:
            unique_words.append(word)

    return ", ".join(unique_words[:60])


# ============================================================
# INSERT / UPDATE ACT
# ============================================================

def get_or_create_act(cursor, act_name):
    """
    Find an existing Act by act_code.

    If it does not exist, create it.
    """

    details = ACT_DETAILS.get(act_name)

    if details is None:
        raise ValueError(
            f"Unknown Act in dataset: {act_name}"
        )

    cursor.execute(
        """
        SELECT act_id
        FROM legal_acts
        WHERE act_code = %s
        LIMIT 1
        """,
        (details["act_code"],)
    )

    existing = cursor.fetchone()

    if existing:
        act_id = existing[0]

        cursor.execute(
            """
            UPDATE legal_acts
            SET
                act_name = %s,
                short_name = %s,
                act_year = %s,
                act_category = %s,
                description = %s,
                source_name = %s,
                source_url = %s,
                is_active = 1
            WHERE act_id = %s
            """,
            (
                details["act_name"],
                details["short_name"],
                details["act_year"],
                details["act_category"],
                details["description"],
                DATASET_SOURCE_NAME,
                DATASET_SOURCE_URL,
                act_id
            )
        )

        return act_id

    cursor.execute(
        """
        INSERT INTO legal_acts
        (
            act_code,
            act_name,
            short_name,
            act_year,
            act_category,
            description,
            source_name,
            source_url,
            is_active
        )
        VALUES
        (
            %s, %s, %s, %s, %s,
            %s, %s, %s, 1
        )
        """,
        (
            details["act_code"],
            details["act_name"],
            details["short_name"],
            details["act_year"],
            details["act_category"],
            details["description"],
            DATASET_SOURCE_NAME,
            DATASET_SOURCE_URL
        )
    )

    return cursor.lastrowid


# ============================================================
# FIND EXISTING SECTION
# ============================================================

def find_existing_section(
    cursor,
    act_id,
    section_number
):
    cursor.execute(
        """
        SELECT section_id
        FROM legal_sections
        WHERE act_id = %s
          AND section_number = %s
        LIMIT 1
        """,
        (
            act_id,
            section_number
        )
    )

    row = cursor.fetchone()

    if row:
        return row[0]

    return None


# ============================================================
# IMPORT ONE SECTION
# ============================================================

def import_section(
    cursor,
    act_id,
    act_name,
    section
):
    section_number = str(
        section.get("section_number", "")
    ).strip()

    section_title = str(
        section.get("section_title", "")
    ).strip()

    chapter = str(
        section.get("chapter", "")
    ).strip()

    section_text = str(
        section.get("text", "")
    ).strip()

    source_label = str(
        section.get("source_label", "")
    ).strip()

    if not section_number:
        return "SKIPPED"

    chapter_number = extract_chapter_number(
        chapter
    )

    keywords = generate_keywords(
        section_title,
        section_text
    )

    # Only BNS sections represent substantive offences
    # in our current legal-retrieval design.
    is_offence = 1 if act_name == "BNS 2023" else 0

    existing_id = find_existing_section(
        cursor,
        act_id,
        section_number
    )

    if existing_id:

        cursor.execute(
            """
            UPDATE legal_sections
            SET
                chapter_number = %s,
                chapter_title = %s,
                section_title = %s,
                section_description = %s,
                section_text = %s,
                keywords = %s,
                is_offence = %s,
                is_active = 1,
                source_name = %s,
                source_url = %s
            WHERE section_id = %s
            """,
            (
                chapter_number,
                chapter,
                section_title,
                section_title,
                section_text,
                keywords,
                is_offence,
                DATASET_SOURCE_NAME,
                DATASET_SOURCE_URL,
                existing_id
            )
        )

        return "UPDATED"

    cursor.execute(
        """
        INSERT INTO legal_sections
        (
            act_id,
            section_number,
            chapter_number,
            chapter_title,
            section_title,
            section_description,
            section_text,
            keywords,
            is_offence,
            is_active,
            source_name,
            source_url
        )
        VALUES
        (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, 1,
            %s, %s
        )
        """,
        (
            act_id,
            section_number,
            chapter_number,
            chapter,
            section_title,
            section_title,
            section_text,
            keywords,
            is_offence,
            DATASET_SOURCE_NAME,
            DATASET_SOURCE_URL
        )
    )

    return "INSERTED"


# ============================================================
# MAIN IMPORT
# ============================================================

def main():

    print("=" * 65)
    print(" IntelliVision - Legal Acts & Sections Importer")
    print("=" * 65)

    # --------------------------------------------------------
    # Download
    # --------------------------------------------------------

    download_dataset()

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    dataset = load_dataset()

    # --------------------------------------------------------
    # Validate expected count
    # --------------------------------------------------------

    expected_counts = {
        "BNS 2023": 358,
        "BNSS 2023": 531,
        "BSA 2023": 170
    }

    actual_counts = {}

    for record in dataset:
        act = record.get("act")

        if act:
            actual_counts[act] = (
                actual_counts.get(act, 0) + 1
            )

    print("\n[DATASET] Act distribution:")

    for act_name, expected in expected_counts.items():
        actual = actual_counts.get(act_name, 0)

        print(
            f"  {act_name:<10} "
            f"{actual:>4} / expected {expected}"
        )

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------

    connection = get_db_connection()

    if connection is None:
        raise RuntimeError(
            "Could not connect to MySQL."
        )

    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # Create/update Acts
        # ----------------------------------------------------

        act_ids = {}

        print("\n[DATABASE] Preparing legal Acts...")

        for act_name in ACT_DETAILS:

            act_id = get_or_create_act(
                cursor,
                act_name
            )

            act_ids[act_name] = act_id

            print(
                f"  {act_name} -> act_id={act_id}"
            )

        connection.commit()

        # ----------------------------------------------------
        # Import sections
        # ----------------------------------------------------

        counters = {
            "BNS 2023": {
                "INSERTED": 0,
                "UPDATED": 0,
                "SKIPPED": 0
            },
            "BNSS 2023": {
                "INSERTED": 0,
                "UPDATED": 0,
                "SKIPPED": 0
            },
            "BSA 2023": {
                "INSERTED": 0,
                "UPDATED": 0,
                "SKIPPED": 0
            }
        }

        print("\n[DATABASE] Importing sections...")

        for index, section in enumerate(
            dataset,
            start=1
        ):

            act_name = section.get("act")

            if act_name not in act_ids:
                print(
                    f"[WARNING] Unknown Act: {act_name}"
                )
                continue

            result = import_section(
                cursor,
                act_ids[act_name],
                act_name,
                section
            )

            counters[act_name][result] += 1

            if index % 100 == 0:
                print(
                    f"  Processed {index}/"
                    f"{len(dataset)} sections..."
                )

        connection.commit()

        # ----------------------------------------------------
        # Final verification
        # ----------------------------------------------------

        print("\n" + "=" * 65)
        print(" IMPORT COMPLETED")
        print("=" * 65)

        total_inserted = 0
        total_updated = 0
        total_skipped = 0

        for act_name in expected_counts:

            inserted = counters[act_name]["INSERTED"]
            updated = counters[act_name]["UPDATED"]
            skipped = counters[act_name]["SKIPPED"]

            total_inserted += inserted
            total_updated += updated
            total_skipped += skipped

            print(
                f"\n{act_name}"
            )
            print(
                f"  Inserted : {inserted}"
            )
            print(
                f"  Updated  : {updated}"
            )
            print(
                f"  Skipped  : {skipped}"
            )

        print("\n-----------------------------------------------")
        print(
            f"Total inserted : {total_inserted}"
        )
        print(
            f"Total updated  : {total_updated}"
        )
        print(
            f"Total skipped  : {total_skipped}"
        )
        print("-----------------------------------------------")

        # ----------------------------------------------------
        # Database count verification
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                la.act_code,
                COUNT(ls.section_id)
            FROM legal_acts la
            LEFT JOIN legal_sections ls
                ON la.act_id = ls.act_id
            WHERE la.act_code IN ('BNS', 'BNSS', 'BSA')
            GROUP BY la.act_id, la.act_code
            ORDER BY la.act_code
            """
        )

        print("\n[DATABASE] Current section counts:")

        for row in cursor.fetchall():
            print(
                f"  {row[0]} : {row[1]} sections"
            )

        print("\n[DATABASE] Legal data is ready.")

    except Exception:

        connection.rollback()

        print(
            "\n[ERROR] Import failed."
        )
        print(
            "[ERROR] Database changes were rolled back."
        )

        raise

    finally:

        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()