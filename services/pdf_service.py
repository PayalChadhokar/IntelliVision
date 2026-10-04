from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

import os


# ============================================================
# PDF SERVICE
# ============================================================

def generate_fir_pdf(fir_data, output_path):
    """
    Generate an FIR PDF from approved FIR data.

    This service only formats information already reviewed
    and approved by the officer. It does not generate or
    modify the factual contents of the complaint.
    """

    if not fir_data:
        raise ValueError(
            "FIR data is required."
        )

    if not output_path:
        raise ValueError(
            "PDF output path is required."
        )


    # --------------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # --------------------------------------------------------

    output_directory = os.path.dirname(
        output_path
    )

    if output_directory:
        os.makedirs(
            output_directory,
            exist_ok=True
        )


    # --------------------------------------------------------
    # DOCUMENT
    # --------------------------------------------------------

    document = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35
    )


    styles = getSampleStyleSheet()


    title_style = ParagraphStyle(
        "FIRTitle",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=14,
        leading=18,
        spaceAfter=8
    )


    subtitle_style = ParagraphStyle(
        "FIRSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        leading=13,
        spaceAfter=4
    )


    heading_style = ParagraphStyle(
        "FIRHeading",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=5
    )


    body_style = ParagraphStyle(
        "FIRBody",
        parent=styles["Normal"],
        fontSize=9,
        leading=13
    )


    # --------------------------------------------------------
    # STORY
    # --------------------------------------------------------

    story = []


    story.append(
        Paragraph(
            "N.C.R.B. I.I.F.-I",
            title_style
        )
    )


    story.append(
        Paragraph(
            "FIRST INFORMATION REPORT",
            title_style
        )
    )


    story.append(
        Paragraph(
            "(Under Section 173 B.N.S.S.)",
            subtitle_style
        )
    )


    story.append(
        Spacer(
            1,
            8
        )
    )


    # --------------------------------------------------------
    # BASIC FIR INFORMATION
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "1. Basic FIR Information",
            heading_style
        )
    )


    basic_data = [
        [
            "District",
            str(fir_data.get("district") or "")
        ],
        [
            "Police Station",
            str(fir_data.get("police_station") or "")
        ],
        [
            "Year",
            str(fir_data.get("year") or "")
        ],
        [
            "FIR No.",
            str(fir_data.get("fir_number") or "")
        ],
        [
            "Date & Time of FIR",
            str(fir_data.get("fir_date_time") or "")
        ]
    ]


    basic_table = Table(
        basic_data,
        colWidths=[150, 350]
    )


    basic_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )


    story.append(
        basic_table
    )


    # --------------------------------------------------------
    # ACTS AND SECTIONS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "2. Acts and Sections",
            heading_style
        )
    )


    sections = fir_data.get(
        "sections",
        []
    )


    if sections:

        section_rows = [
            [
                "Act",
                "Section",
                "Status"
            ]
        ]

        for section in sections:

            section_rows.append([
                str(
                    section.get("act_name") or ""
                ),
                str(
                    section.get("section_number") or ""
                ),
                str(
                    section.get(
                        "verification_status",
                        ""
                    ) or ""
                )
            ])

    else:

        section_rows = [
            [
                "No sections entered",
                "",
                ""
            ]
        ]


    section_table = Table(
        section_rows,
        colWidths=[250, 100, 150]
    )


    section_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.lightgrey
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )
        ])
    )


    story.append(
        section_table
    )


    # --------------------------------------------------------
    # OCCURRENCE
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "3. Occurrence of Offence",
            heading_style
        )
    )


    occurrence_data = [
        [
            "From Date & Time",
            str(
                fir_data.get(
                    "occurrence_from"
                ) or ""
            )
        ],
        [
            "To Date & Time",
            str(
                fir_data.get(
                    "occurrence_to"
                ) or ""
            )
        ],
        [
            "Information Received",
            str(
                fir_data.get(
                    "information_received_datetime"
                ) or ""
            )
        ],
        [
            "General Diary Reference",
            str(
                fir_data.get(
                    "general_diary_reference"
                ) or ""
            )
        ]
    ]


    occurrence_table = Table(
        occurrence_data,
        colWidths=[180, 320]
    )


    occurrence_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )
        ])
    )


    story.append(
        occurrence_table
    )


    # --------------------------------------------------------
    # COMPLAINANT
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "4. Complainant / Informant",
            heading_style
        )
    )


    complainant_data = [
        [
            "Name",
            str(
                fir_data.get(
                    "complainant_name"
                ) or ""
            )
        ],
        [
            "Father / Husband",
            str(
                fir_data.get(
                    "complainant_father_husband"
                ) or ""
            )
        ],
        [
            "DOB / Year",
            str(
                fir_data.get(
                    "complainant_dob_year"
                ) or ""
            )
        ],
        [
            "Nationality",
            str(
                fir_data.get(
                    "complainant_nationality"
                ) or ""
            )
        ],
        [
            "Occupation",
            str(
                fir_data.get(
                    "complainant_occupation"
                ) or ""
            )
        ],
        [
            "Address",
            str(
                fir_data.get(
                    "complainant_address"
                ) or ""
            )
        ],
        [
            "Phone / Mobile",
            str(
                fir_data.get(
                    "complainant_phone"
                ) or ""
            )
        ]
    ]


    complainant_table = Table(
        complainant_data,
        colWidths=[180, 320]
    )


    complainant_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )
        ])
    )


    story.append(
        complainant_table
    )


    # --------------------------------------------------------
    # ACCUSED
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "5. Accused Details",
            heading_style
        )
    )


    story.append(
        Paragraph(
            str(
                fir_data.get(
                    "accused_details"
                ) or ""
            ),
            body_style
        )
    )


    # --------------------------------------------------------
    # PROPERTY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "6. Property Details",
            heading_style
        )
    )


    property_data = [
        [
            "Property",
            str(
                fir_data.get(
                    "property_details"
                ) or ""
            )
        ],
        [
            "Total Value",
            str(
                fir_data.get(
                    "total_property_value"
                ) or ""
            )
        ]
    ]


    property_table = Table(
        property_data,
        colWidths=[180, 320]
    )


    property_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "FONTNAME",
                (0, 0),
                (0, -1),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )
        ])
    )


    story.append(
        property_table
    )


    # --------------------------------------------------------
    # FIRST INFORMATION CONTENTS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "7. First Information Contents",
            heading_style
        )
    )


    story.append(
        Paragraph(
            str(
                fir_data.get(
                    "first_information_contents"
                ) or ""
            ),
            body_style
        )
    )


    # --------------------------------------------------------
    # ACTION TAKEN
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "8. Action Taken",
            heading_style
        )
    )


    story.append(
        Paragraph(
            str(
                fir_data.get(
                    "action_taken"
                ) or ""
            ),
            body_style
        )
    )


    story.append(
        Spacer(
            1,
            30
        )
    )


    # --------------------------------------------------------
    # OFFICER SIGNATURE
    # --------------------------------------------------------

    signature_data = [
        [
            "Investigating / Recording Officer",
            "Signature"
        ],
        [
            str(
                fir_data.get(
                    "officer_name"
                ) or ""
            ),
            "________________________"
        ],
        [
            str(
                fir_data.get(
                    "officer_rank"
                ) or ""
            ),
            ""
        ]
    ]


    signature_table = Table(
        signature_data,
        colWidths=[250, 250]
    )


    signature_table.setStyle(
        TableStyle([
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.black
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, 0),
                "Helvetica-Bold"
            ),
            (
                "FONTSIZE",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            )
        ])
    )


    story.append(
        signature_table
    )


    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    document.build(
        story
    )


    return output_path