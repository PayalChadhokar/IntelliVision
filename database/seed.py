# database/seed.py

from database.connection import get_db_connection


LEGAL_SECTIONS = [
    {
        "act_code": "BNS",
        "section_number": "103",
        "chapter_number": "VI",
        "chapter_title": "Of Offences Affecting the Human Body",
        "section_title": "Punishment for murder",
        "section_description": "Punishment for the offence of murder.",
        "keywords": "murder, death, killing, homicide",
        "is_offence": True,
    },
    {
        "act_code": "BNS",
        "section_number": "109",
        "chapter_number": "VI",
        "chapter_title": "Of Offences Affecting the Human Body",
        "section_title": "Attempt to murder",
        "section_description": "Attempt to murder.",
        "keywords": "attempt murder, attempted murder, kill, killing",
        "is_offence": True,
    },
    {
        "act_code": "BNS",
        "section_number": "115",
        "chapter_number": "VI",
        "chapter_title": "Of Offences Affecting the Human Body",
        "section_title": "Voluntarily causing hurt",
        "section_description": "Voluntarily causing hurt to a person.",
        "keywords": "hurt, assault, injury, voluntarily causing hurt",
        "is_offence": True,
    },
    {
        "act_code": "BNS",
        "section_number": "137",
        "chapter_number": "VI",
        "chapter_title": "Of Offences Affecting the Human Body",
        "section_title": "Kidnapping",
        "section_description": "Kidnapping from India or from lawful guardianship.",
        "keywords": "kidnapping, kidnap, abduct, child, lawful guardianship",
        "is_offence": True,
    },
    {
        "act_code": "BNS",
        "section_number": "303",
        "chapter_number": "XVII",
        "chapter_title": "Of Offences Against Property",
        "section_title": "Theft",
        "section_description": "Dishonestly taking movable property out of another person's possession without consent.",
        "keywords": "theft, stealing, stolen, steal, movable property",
        "is_offence": True,
    },
    {
        "act_code": "BNS",
        "section_number": "304",
        "chapter_number": "XVII",
        "chapter_title": "Of Offences Against Property",
        "section_title": "Snatching",
        "section_description": "Theft committed by suddenly, quickly or forcibly seizing or taking movable property from a person or from their possession.",
        "keywords": "snatching, snatch, seized, grabbed, grabbed phone, forcibly took",
        "is_offence": True,
    },
    {
        "act_code": "BNS",
        "section_number": "309",
        "chapter_number": "XVII",
        "chapter_title": "Of Offences Against Property",
        "section_title": "Robbery",
        "section_description": "Robbery involving theft or extortion accompanied by the circumstances specified in the provision.",
        "keywords": "robbery, robbed, force, threat, instant hurt, instant death",
        "is_offence": True,
    },
    {
        "act_code": "BNS",
        "section_number": "318",
        "chapter_number": "XVII",
        "chapter_title": "Of Offences Against Property",
        "section_title": "Cheating",
        "section_description": "Cheating by deceiving a person and dishonestly or fraudulently inducing an act, omission, or delivery or retention of property.",
        "keywords": "cheating, fraud, cheated, deception, deceive, fraudulent, dishonestly induced",
        "is_offence": True,
    },
]


def seed_legal_sections():
    connection = get_db_connection()

    if connection is None:
        print("ERROR: Could not connect to MySQL.")
        return

    cursor = connection.cursor(dictionary=True)

    try:
        inserted = 0
        skipped = 0

        for section in LEGAL_SECTIONS:

            # Find the corresponding legal act.
            cursor.execute(
                """
                SELECT act_id
                FROM legal_acts
                WHERE act_code = %s
                LIMIT 1
                """,
                (section["act_code"],)
            )

            act = cursor.fetchone()

            if not act:
                print(
                    f"WARNING: Legal act {section['act_code']} "
                    f"was not found. Skipping section "
                    f"{section['section_number']}."
                )
                skipped += 1
                continue

            # Check whether this section already exists.
            cursor.execute(
                """
                SELECT section_id
                FROM legal_sections
                WHERE act_id = %s
                  AND section_number = %s
                LIMIT 1
                """,
                (
                    act["act_id"],
                    section["section_number"],
                )
            )

            existing = cursor.fetchone()

            if existing:
                print(
                    f"SKIPPED: BNS Section "
                    f"{section['section_number']} already exists."
                )
                skipped += 1
                continue

            # Insert the legal section.
            cursor.execute(
                """
                INSERT INTO legal_sections (
                    act_id,
                    section_number,
                    chapter_number,
                    chapter_title,
                    section_title,
                    section_description,
                    keywords,
                    is_offence,
                    is_active,
                    source_name,
                    source_url
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    TRUE,
                    %s,
                    %s
                )
                """,
                (
                    act["act_id"],
                    section["section_number"],
                    section["chapter_number"],
                    section["chapter_title"],
                    section["section_title"],
                    section["section_description"],
                    section["keywords"],
                    section["is_offence"],
                    "NCRB - New Criminal Laws",
                    "https://cytrain.ncrb.gov.in/staticpage/web_pages/IndexBNS.html",
                )
            )

            print(
                f"INSERTED: BNS Section "
                f"{section['section_number']} - "
                f"{section['section_title']}"
            )

            inserted += 1

        connection.commit()

        print()
        print("========================================")
        print("LEGAL DATABASE SEED COMPLETED")
        print("========================================")
        print(f"Inserted : {inserted}")
        print(f"Skipped  : {skipped}")

    except Exception as e:
        connection.rollback()
        print()
        print("ERROR while seeding legal sections:")
        print(e)

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    seed_legal_sections()