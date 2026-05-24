"""Term dropdown options by level (ABC Learning Center tutorial center)."""

PERIOD_TERMS = ["1st Period", "2nd Period", "3rd Period", "4th Period"]
SEMESTER_TERMS = ["1st Semester", "2nd Semester"]

SENIOR_HIGH_LEVELS = ("Grade 11", "Grade 12")


def get_term_options(level: str) -> list:
    """
    Return Term dropdown values for the given level string (e.g. 'Grade 7').
    Grade 11–12: semesters; Grade 7–10 (and elementary): periods.
    """
    if not level or not str(level).strip():
        return []
    level = str(level).strip()
    if level in SENIOR_HIGH_LEVELS:
        return list(SEMESTER_TERMS)
    return list(PERIOD_TERMS)


def apply_term_combo_for_level(combo, level: str):
    """Set combo values from level; keep current selection if still valid."""
    options = get_term_options(level)
    current = combo.get().strip() if combo.get() else ""
    combo.configure(values=options)
    if level and options:
        combo.configure(state="readonly")
        if current in options:
            combo.set(current)
        else:
            combo.set(options[0])
    else:
        combo.set("")
        if not level:
            combo.configure(state="disabled")
