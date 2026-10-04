# services/legal_services.py

from database.connection import get_db_connection


def search_legal_sections(crime_category=None, keywords=None):
    """
    Search the legal database for relevant legal provisions.

    The crime category is the primary retrieval signal.
    Keywords provide additional matching support.

    The function returns candidate provisions from the
    database. It does not make a final legal determination.
    """

    connection = get_db_connection()

    if connection is None:
        print("[Legal] Database connection failed.")
        return []

    cursor = connection.cursor(dictionary=True)

    try:

        category_mapping = {
            "THEFT": [
                "theft",
                "stealing",
                "stolen",
                "steal",
            ],

            "SNATCHING": [
                "snatching",
                "snatch",
            ],

            "ROBBERY": [
                "robbery",
                "robbed",
            ],

            "ASSAULT": [
                "assault",
                "hurt",
                "injury",
            ],

            "FRAUD": [
                "fraud",
                "cheating",
                "deception",
            ],

            "CYBERCRIME": [
                "cyber",
                "online",
                "computer",
            ],

            "KIDNAPPING": [
                "kidnapping",
                "kidnap",
                "abduction",
            ],

            "HARASSMENT": [
                "harassment",
                "stalking",
            ],
        }

        crime_category_upper = (
            crime_category.upper()
            if crime_category
            else ""
        )

        category_terms = category_mapping.get(
            crime_category_upper,
            []
        )

        # -------------------------------------------------
        # STEP 1:
        # Try direct category-based retrieval.
        #
        # Example:
        # SNATCHING -> section title "Snatching"
        # -------------------------------------------------

        if category_terms:

            category_conditions = []
            category_parameters = []

            for term in category_terms:

                like_term = f"%{term.lower()}%"

                category_conditions.append(
                    """
                    (
                        LOWER(ls.section_title) LIKE %s
                        OR LOWER(ls.section_description) LIKE %s
                        OR LOWER(ls.keywords) LIKE %s
                    )
                    """
                )

                category_parameters.extend(
                    [
                        like_term,
                        like_term,
                        like_term,
                    ]
                )

            category_query = f"""
                SELECT
                    ls.section_id,
                    la.act_code,
                    la.act_name,
                    la.short_name,
                    ls.section_number,
                    ls.chapter_number,
                    ls.chapter_title,
                    ls.section_title,
                    ls.section_description,
                    ls.section_text,
                    ls.keywords,
                    ls.source_name,
                    ls.source_url
                FROM legal_sections ls
                INNER JOIN legal_acts la
                    ON ls.act_id = la.act_id
                WHERE
                ls.is_active = TRUE
                AND la.is_active = TRUE
                AND la.act_category = 'OFFENCE'
                AND (
                {" OR ".join(category_conditions)}
                )
                ORDER BY
                    CASE
                        WHEN UPPER(ls.section_title) = %s
                        THEN 1
                        ELSE 2
                    END,
                    CAST(ls.section_number AS UNSIGNED)
                LIMIT 10
            """

            category_parameters.append(
                crime_category_upper.title()
            )

            cursor.execute(
                category_query,
                category_parameters
            )

            results = cursor.fetchall()

            if results:

                print(
                    "[Legal] Retrieved "
                    f"{len(results)} provision(s) "
                    f"for {crime_category_upper}."
                )

                return results

        # -------------------------------------------------
        # STEP 2:
        # Keyword fallback.
        #
        # Used if category retrieval produces nothing.
        # -------------------------------------------------

        if keywords:

            keyword_conditions = []
            keyword_parameters = []

            for keyword in keywords:

                if not keyword:
                    continue

                like_term = (
                    f"%{str(keyword).lower()}%"
                )

                keyword_conditions.append(
                    """
                    (
                        LOWER(ls.section_title) LIKE %s
                        OR LOWER(ls.section_description) LIKE %s
                        OR LOWER(ls.keywords) LIKE %s
                    )
                    """
                )

                keyword_parameters.extend(
                    [
                        like_term,
                        like_term,
                        like_term,
                    ]
                )

            if keyword_conditions:

                keyword_query = f"""
                    SELECT
                        ls.section_id,
                        la.act_code,
                        la.act_name,
                        la.short_name,
                        ls.section_number,
                        ls.chapter_number,
                        ls.chapter_title,
                        ls.section_title,
                        ls.section_description,
                        ls.section_text,
                        ls.keywords,
                        ls.source_name,
                        ls.source_url
                    FROM legal_sections ls
                    INNER JOIN legal_acts la
                        ON ls.act_id = la.act_id
                    WHERE
                        ls.is_active = TRUE
                        AND la.is_active = TRUE
                        AND (
                            {" OR ".join(keyword_conditions)}
                        )
                    ORDER BY
                        CAST(ls.section_number AS UNSIGNED)
                    LIMIT 10
                """

                cursor.execute(
                    keyword_query,
                    keyword_parameters
                )

                results = cursor.fetchall()

                if results:

                    print(
                        "[Legal] Retrieved "
                        f"{len(results)} provision(s) "
                        "using keyword search."
                    )

                    return results

        print(
            "[Legal] No matching legal provisions found."
        )

        return []

    finally:

        cursor.close()
        connection.close()


def get_legal_section_by_number(
    act_code,
    section_number
):
    """
    Retrieve one specific legal section.
    """

    connection = get_db_connection()

    if connection is None:
        return None

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        query = """
            SELECT
                ls.section_id,
                la.act_code,
                la.act_name,
                la.short_name,
                ls.section_number,
                ls.chapter_number,
                ls.chapter_title,
                ls.section_title,
                ls.section_description,
                ls.section_text,
                ls.keywords,
                ls.source_name,
                ls.source_url
            FROM legal_sections ls
            INNER JOIN legal_acts la
                ON ls.act_id = la.act_id
            WHERE
                la.act_code = %s
                AND ls.section_number = %s
                AND la.is_active = TRUE
                AND ls.is_active = TRUE
            LIMIT 1
        """

        cursor.execute(
            query,
            (
                act_code,
                section_number,
            )
        )

        return cursor.fetchone()

    finally:

        cursor.close()
        connection.close()