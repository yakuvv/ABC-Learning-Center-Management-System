# Changelog — ABC Learning Center Management System

All notable changes I made across Cursor sessions (logic, database, and UI prompts).  
Module names unchanged: **Profile Students**, **Manage Enrollment**, **Record Attendance**, **Process Payment**, **Manage Grades**.

---

## 1. Database & core logic rebuild

**What I asked for:** Revise only logic, database queries, and user flows — not UI design, colors, layout, buttons, dropdown look, focus effects, or the Date of Birth calendar. Use the new tutorial-center schema (`STUDENT`, `PARENT`, `REGISTRATION`, `REGISTRATION_DETAIL`, `ATTENDANCE`, `GRADE`, `PAYMENT`, etc.) with Level, Group Name, Term, and Learner ID (not School ID / Section / School Year).

**What I changed:**

- **`database.py`** — I made this the single source of truth for the schema. I replaced the old `ENROLLMENT` / `DETAIL` model with **`REGISTRATION`** and **`REGISTRATION_DETAIL`**. Columns now use `level`, `groupName`, `term`, `learnerID`, and related names.
- **All five modules** — I updated SQL and flows to read/write the new tables (e.g. search by Learner ID instead of School ID, payments on `registrationID`, attendance on registration details).
- **`main.py`** — I pass **`user_id`** (`staffID` or `tutorID`) into the dashboard after login so enrollment can record which staff created a registration.
- **Seed/migration scripts** — I updated `database_v2.py`, `migrate_and_seed.py`, `reset_database.py`, `insert_sample_data.py`, `generate_test_data.py`, and `generate_clean_200.py` for the new schema.
- **`update_db_for_payment.py`** — I removed this; it was an old one-off patch for the previous `ENROLLMENT` table.

**Term dropdown (follow-up):**

- **`utils/term_options.py`** (new) — I centralize Term rules here:
  - **Grade 7–10** → `1st Period` … `4th Period`
  - **Grade 11–12** → `1st Semester`, `2nd Semester`
  - No full school years (e.g. `2025-2026`) in Term lists
- I wired this into **Manage Enrollment**, **Record Attendance**, and **Manage Grades** so Term updates when Level changes (Admin and Tutor).

**Reference:** See `database_commented.py` for the schema script with before/after notes.

---

## 2. Learner ID format & empty database

**What I asked for:** Fix bad IDs like `1s-8079-27`. I wanted **`RANDOM2-RANDOM4-RANDOM4`** (e.g. `47-3821-9056`), then wipe all data so the database starts clean.

**What I changed:**

- **`database.py`** — I replaced `generate_school_id()` with **`generate_learner_id()`** (`##-####-####`) and uniqueness checks on `REGISTRATION.learnerID`.
- **`clear_all_data()`** — I added this to delete all rows while keeping the schema.
- **Enrollment module** — New registrations use the new Learner ID format.
- **`abc_learning_center.db`** (and backup) — I reset these locally to an empty database with the new schema.

---

## 3. Dropdown consistency (`ModernCombo` & Profile Students)

**What I asked for:** Same dropdown design everywhere; underline style (then fixes when layout broke); white combo field; navy dropdown list; white arrow; dropdown width matching the field; Profile Gender/DOB matching other modules.

**What I changed:**

- **`utils/modern_combo.py`** — White background (`#ffffff`), no box border, navy dropdown (`#15165e` / white text / `#122aff` hover), white arrow button, and logic to sync dropdown menu width to the combo width.
- **`modules/profile_students.py`** — Gender uses **`ModernCombo`**; Date of Birth uses **`DatePickerCombo`** (looks like `ModernCombo`, calendar popup unchanged). I added DOB placeholder/guide (`MM-DD-YYYY`), fixed visibility and the down arrow, set Gender width to **120px** with DOB filling the rest, and matched filled DOB text color to other fields. I added underlines under Gender/DOB like Email.

---

## 4. Profile Students & Manage Enrollment UI

**Profile Students — what I asked for:**

- Remove the navy vertical line on **Student List** and **Student Directory** table cards.
- Match **Student Directory** search bar design to **Enrollment List** search in Manage Enrollment.

**What I changed:** I removed accent strips on those cards and aligned the search bar styling with enrollment.

**Manage Enrollment — what I asked for:**

- Make **Search Student** behave/look like Process Payment search.
- Shorter search card, **green OK button** back, no vertical line on the selected-student card.
- Taller enrollment list table inside the card; plain white cards (no navy side lines).

**What I changed:** I reworked the search UI, restored OK button and card height, expanded the table, used plain white cards, and removed a large block of old commented-out legacy code so the file matches the live REGISTRATION implementation.

---

## 5. Record Attendance

**What I asked for (kept):**

- Remove navy vertical line on **Attendance History** table card (left filters untouched).
- Remove navy line on **STUDENTS** card (Record Attendance tab only).
- Swap **student table** and **Present / Absent / Late / Total** cards; modern rectangular stat cards, **no emojis**, plain look.
- **Filter Class** dropdowns: black underline like Profile Gender/DOB.
- Plain white cards where requested; class details spacing like enrollment list.
- Fix **Attendance History** row/column alignment.

**What I changed:** Layout order, stat card styling, filter underlines, class details formatting, accent lines removed on named cards, and history table alignment.

**What I asked for then reverted:**

- ALL CAPS section labels across modules — I asked to **bring the original label text back**.
- **STUDENTS roster** column tweaks (shared grid, smaller name columns) — I said it got worse and asked to **bring the roster table back to the original**; I kept the history-tab alignment fix.

**Also from schema work:** REGISTRATION-based queries, dynamic Term via `term_options`, Admin and Tutor both supported.

---

## 6. Process Payment & Manage Grades

**Process Payment**

- **What I asked for:** Search/enrollment flow aligned with the new registration model (label cap experiments were later reverted).
- **What I changed:** Searches `REGISTRATION` by Learner ID / student name; shows Learner ID, Level, Group Name; saves payments on `registrationID`. Placeholder text says Learner ID instead of School ID.

**Manage Grades**

- **What I asked for:** Section title styling (partially rolled back); Term logic like attendance.
- **What I changed:** Queries use REGISTRATION and new columns; Term dropdown follows grade level via `term_options`.

---

## 7. Dashboard & login

**What I asked for:**

- Remove navy line on **RECENT ATTENDANCE (Today)** (Admin + Tutor).
- Remove blue line on the **“Good evening, …”** greeting card; fix corner radius / module card spacing.
- Try a **dark dashboard** — I reverted; I wanted the original light design back.
- Full **Admin vs Tutor** dashboard redesign — I reverted; I asked not to redesign the dashboard.
- Compact dashboard — reverted with the original.

**What stayed:**

- **`dashboard.py`** — Optional card accent (`show_accent=False` on attendance table). Greeting card without the blue strip; slightly rounder cards. **Tutor** hides staff-only nav (Profile Students, Manage Enrollment, Process Payment) and the “Payments Recorded” stat. Stats use **`REGISTRATION`** (“Active Registrations”). **`user_id`** is passed in for modules that need it.
- **`main.py`** — Passes `user_id` through the loading screen into `Dashboard`.

**What did not stay:** Dark theme and the large redesigned dashboard layout.

---

## 8. Rules I set vs what actually changed

| My rule | What happened |
|--------|----------------|
| Don’t change UI in the schema rebuild | Logic/SQL changed; later chats **did** change UI (dropdowns, cards, attendance layout) per my prompts. |
| Don’t change DOB calendar popup | Calendar behavior kept; only the **appearance** of the DOB control changed in Profile. |
| Don’t change label **text** (only caps) | I asked for ALL CAPS, then asked to **restore** original labels — those cap changes were rolled back. |

---

## 9. Files I am not treating as app releases

| File | Note |
|------|------|
| `pdf_extracted.txt` | Scratch — not part of the app. |
| `abc_learning_center.db` / backup | Local empty/reset DB; optional on GitHub — on another machine I can run `reset_database.py` or `python database.py` instead. |
| `database_commented.py` | Reference copy of `database.py` with schema change comments (not imported by the app). |

---

## 10. Summary — how the system works now

I moved the app from a **school-style** model (School ID, grade/section/school year, `ENROLLMENT`) to a **tutorial-center** model (**Learner ID**, Level, Group Name, Term as periods/semesters, `REGISTRATION`). IDs are random `##-####-####`. Term choices depend on grade level in enrollment, attendance, and grades. UI work focused on **consistent dropdowns**, **plain white cards without navy side bars**, **attendance screen layout**, and **dashboard polish** — while **reverting** dashboard redesigns and roster-table experiments I did not like.

---

## Schema quick reference (before → after)

| Before | After |
|--------|--------|
| `generate_school_id()` → `YY-####-##` | `generate_learner_id()` → `##-####-####` |
| `ENROLLMENT` (`schoolID`, `gradeLevel`, `section`, `schoolYear`) | `REGISTRATION` (`learnerID`, `level`, `groupName`, `term`) |
| `DETAIL` → `enrollmentID` | `REGISTRATION_DETAIL` → `registrationID` |
| `PAYMENT.enrollmentID` | `PAYMENT.registrationID` |
| `GRADE.quarter` | `GRADE.period` |
| `STUDENT.levelType` | `STUDENT.level`, `program` |
| `SUBJECT.gradeLevel`, `strand`, … | `SUBJECT.level`, `program`, `termType` |

---

*Last updated: May 2026*
