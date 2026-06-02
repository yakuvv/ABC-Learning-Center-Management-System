# Term dropdown options by level (ABC Learning Center tutorial center).

TERM_OPTIONS = ["Term 1", "Term 2"]


def get_term_options(level: str) -> list:
    # I return Term dropdown values for the given level string (e.g. 'Grade 7'). This system uses 2 terms for all levels.
    if not level or not str(level).strip():
        return []
    return list(TERM_OPTIONS)


def apply_term_combo_for_level(combo, level: str):
    # I set combo values from the level and keep the current selection if it's still valid.
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
