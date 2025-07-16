#!/usr/bin/env python3
"""
Fixed Faculty Timetable Optimizer using Google OR-Tools CP-SAT
Constraints:
1. Faculty assignments are FIXED per batch (cannot be changed)
2. Only timings can be rearranged within 8:30 AM - 7:00 PM window
3. No teacher conflicts across batches at same time
"""


from ortools.sat.python import cp_model

# Define time slots (8:30 AM - 7:00 PM)
TIME_SLOTS = [
    "8:30-10:00",
    "10:00-11:30",
    "11:40-1:00",
    "1:00-2:00",  # LUNCH BREAK
    "2:00-3:30",
    "3:30-5:00",
    "5:30-7:00",
]

# Working time slots (excluding lunch)
WORKING_SLOTS = [0, 1, 2, 4, 5, 6]  # Skip slot 3 (lunch)
LUNCH_SLOT = 3

# FIXED Faculty assignments per batch (extracted from original timetable)
BATCH_FACULTY = {
    "AK_E_JR_1": {
        "PHYSICS": ["KIRITI", "KIRITI"],  # 2 sessions
        "MATHS": ["RAM REDDY", "RAM REDDY"],  # 2 sessions
        "CHEM": ["KK", "KK"],  # 2 sessions
    },
    "AK_E_JR_2": {
        "PHYSICS": ["KIRITI", "KIRITI"],  # 2 sessions
        "MATHS": ["RAM REDDY", "RAM REDDY"],  # 2 sessions
        "CHEM": ["KK", "KK"],  # 2 sessions
    },
    "9th_CLASS": {
        "PHYSICS": ["ANIL KUMAR", "ANIL KUMAR"],  # 2 sessions
        "MATHS": ["RAJESH", "RAJESH"],  # 2 sessions
        "CHEM": ["KK", "KK"],  # 2 sessions
    },
    "AK-SR-2": {
        "PHYSICS": ["ANIL KUMAR", "ANIL KUMAR"],  # 2 sessions
        "MATHS": ["RAJESH", "RAJESH"],  # 2 sessions
        "CHEM": ["SAIDI", "SAIDI"],  # 2 sessions
    },
    "AK-JR-1": {
        "PHYSICS": ["SAGAR DAS", "SAGAR DAS"],  # 2 sessions
        "MATHS": ["SRIKANTH", "SRIKANTH"],  # 2 sessions
        "CHEM": ["PRK", "PRK"],  # 2 sessions
    },
    "AK-JR-2": {
        "PHYSICS": ["ANIL KUMAR", "ANIL KUMAR"],  # 2 sessions
        "MATHS": ["RAJESH", "RAJESH"],  # 2 sessions
        "CHEM": ["PRK", "PRK"],  # 2 sessions
    },
    "AK-JR-3": {
        "PHYSICS": ["KIRITI", "KIRITI"],  # 2 sessions
        "MATHS": ["RAM REDDY", "RAM REDDY"],  # 2 sessions
        "CHEM": ["PRK", "PRK"],  # 2 sessions
    },
}

SUBJECTS = ["PHYSICS", "MATHS", "CHEM"]
BATCHES = list(BATCH_FACULTY.keys())


def create_fixed_faculty_model():
    """Create timetable model with FIXED faculty assignments"""

    model = cp_model.CpModel()

    # Decision variables: batch_schedule[batch][slot] = (subject_index, session_index)
    batch_schedule = {}
    for batch in BATCHES:
        batch_schedule[batch] = {}
        for slot in WORKING_SLOTS:
            # subject_index: 0=PHYSICS, 1=MATHS, 2=CHEM
            # session_index: 0=first session, 1=second session
            batch_schedule[batch][slot] = {
                "subject": model.NewIntVar(
                    0, len(SUBJECTS) - 1, f"{batch}_slot_{slot}_subject"
                ),
                "session": model.NewIntVar(0, 1, f"{batch}_slot_{slot}_session"),
            }

    # Constraint 1: Each batch must have exactly 2 sessions of each subject
    for batch in BATCHES:
        for subject_idx, subject in enumerate(SUBJECTS):
            subject_slots = []
            for slot in WORKING_SLOTS:
                is_subject = model.NewBoolVar(f"{batch}_{slot}_{subject}_assigned")
                model.Add(
                    batch_schedule[batch][slot]["subject"] == subject_idx
                ).OnlyEnforceIf(is_subject)
                model.Add(
                    batch_schedule[batch][slot]["subject"] != subject_idx
                ).OnlyEnforceIf(is_subject.Not())
                subject_slots.append(is_subject)

            # Exactly 2 sessions per subject
            model.Add(sum(subject_slots) == 2)

    # Constraint 2: Each session (0 or 1) should be used exactly once per subject per batch
    for batch in BATCHES:
        for subject_idx, subject in enumerate(SUBJECTS):
            for session_idx in [0, 1]:
                session_uses = []
                for slot in WORKING_SLOTS:
                    is_this_subject_session = model.NewBoolVar(
                        f"{batch}_{slot}_{subject}_session_{session_idx}"
                    )

                    # Both conditions must be true
                    model.Add(
                        batch_schedule[batch][slot]["subject"] == subject_idx
                    ).OnlyEnforceIf(is_this_subject_session)
                    model.Add(
                        batch_schedule[batch][slot]["session"] == session_idx
                    ).OnlyEnforceIf(is_this_subject_session)

                    # If either condition is false, this var is false
                    subject_not_match = model.NewBoolVar(
                        f"{batch}_{slot}_{subject}_not_match_{session_idx}"
                    )
                    session_not_match = model.NewBoolVar(
                        f"{batch}_{slot}_{subject}_session_not_match_{session_idx}"
                    )

                    model.Add(
                        batch_schedule[batch][slot]["subject"] != subject_idx
                    ).OnlyEnforceIf(subject_not_match)
                    model.Add(
                        batch_schedule[batch][slot]["session"] != session_idx
                    ).OnlyEnforceIf(session_not_match)

                    model.AddBoolOr(
                        [is_this_subject_session, subject_not_match, session_not_match]
                    )
                    model.Add(is_this_subject_session == 0).OnlyEnforceIf(
                        subject_not_match
                    )
                    model.Add(is_this_subject_session == 0).OnlyEnforceIf(
                        session_not_match
                    )

                    session_uses.append(is_this_subject_session)

                # Each session used exactly once
                model.Add(sum(session_uses) == 1)

    # Constraint 3: No teacher conflicts (same teacher cannot teach multiple batches at same time)
    for slot in WORKING_SLOTS:
        # Track which teachers are teaching at this slot
        teacher_usage = {}

        for batch in BATCHES:
            for subject_idx, subject in enumerate(SUBJECTS):
                for session_idx in [0, 1]:
                    teacher = BATCH_FACULTY[batch][subject][session_idx]

                    if teacher not in teacher_usage:
                        teacher_usage[teacher] = []

                    # Check if this teacher is teaching this batch at this slot
                    teaching_here = model.NewBoolVar(
                        f"{teacher}_{batch}_{slot}_{subject}_{session_idx}"
                    )

                    # Teacher is teaching if both subject and session match
                    model.Add(
                        batch_schedule[batch][slot]["subject"] == subject_idx
                    ).OnlyEnforceIf(teaching_here)
                    model.Add(
                        batch_schedule[batch][slot]["session"] == session_idx
                    ).OnlyEnforceIf(teaching_here)

                    # If either doesn't match, not teaching
                    not_subject = model.NewBoolVar(
                        f"not_{batch}_{slot}_{subject}_{session_idx}"
                    )
                    not_session = model.NewBoolVar(
                        f"not_session_{batch}_{slot}_{subject}_{session_idx}"
                    )

                    model.Add(
                        batch_schedule[batch][slot]["subject"] != subject_idx
                    ).OnlyEnforceIf(not_subject)
                    model.Add(
                        batch_schedule[batch][slot]["session"] != session_idx
                    ).OnlyEnforceIf(not_session)

                    model.AddBoolOr([teaching_here, not_subject, not_session])
                    model.Add(teaching_here == 0).OnlyEnforceIf(not_subject)
                    model.Add(teaching_here == 0).OnlyEnforceIf(not_session)

                    teacher_usage[teacher].append(teaching_here)

        # Each teacher can teach at most one batch per slot
        for teacher, usages in teacher_usage.items():
            model.Add(sum(usages) <= 1)

    return model, batch_schedule


def solve_and_display_fixed_faculty():
    """Solve with fixed faculty assignments and display as plain text tables"""

    model, batch_schedule = create_fixed_faculty_model()

    # Create solver
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0  # Increase timeout

    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("✅ OPTIMIZED TIMETABLE WITH FIXED FACULTY ASSIGNMENTS")
        print("=" * 80)
        print("🎯 All classes fit within 8:30 AM - 7:00 PM window")
        print("👨‍🏫 Faculty assignments preserved as per original batch requirements")
        print("=" * 80)

        # Display each batch as a plain text table
        for batch in BATCHES:
            print(f"\n#### {batch.replace('_', ' ').replace('-', ' ')}")
            print()
            print("```")

            # Create table header
            header = "TIME        |"
            for slot in WORKING_SLOTS:
                if slot == LUNCH_SLOT:
                    continue
                header += f" {TIME_SLOTS[slot]:<12} |"
            header += " 1:00-2:00    |"

            print(header)
            print("-" * len(header))

            # Create table row
            row = f"{batch:<12}|"
            lunch_added = False

            for slot in WORKING_SLOTS:
                if slot == LUNCH_SLOT:
                    continue

                subject_idx = solver.Value(batch_schedule[batch][slot]["subject"])
                session_idx = solver.Value(batch_schedule[batch][slot]["session"])

                subject = SUBJECTS[subject_idx]
                teacher = BATCH_FACULTY[batch][subject][session_idx]

                cell_content = f" {subject} - {teacher}"
                row += f"{cell_content:<12} |"

                # Add lunch break after the appropriate slot
                if slot == 2 and not lunch_added:  # After 11:40-1:00 slot
                    row += " LUNCH BREAK  |"
                    lunch_added = True

            if not lunch_added:
                row += " LUNCH BREAK  |"

            print(row)
            print("```")

        print("\n📊 Solver Statistics:")
        print(f"   Status: {solver.StatusName(status)}")
        print(f"   Time: {solver.WallTime():.2f} seconds")
        print(f"   Conflicts: {solver.NumConflicts()}")

        return True

    else:
        print("❌ NO SOLUTION FOUND WITH FIXED FACULTY CONSTRAINTS")
        print(f"Status: {solver.StatusName(status)}")
        print("\n🔍 Possible issues:")
        print(
            "   • Teacher conflicts cannot be resolved with current faculty assignments"
        )
        print("   • Need to adjust lunch break timing")
        print("   • Consider allowing some faculty flexibility")
        return False


if __name__ == "__main__":
    print("🚀 Starting Fixed Faculty Timetable Optimization...")
    print("📋 Constraints:")
    print("   • Faculty assignments are FIXED per batch")
    print("   • Classes must fit within 8:30 AM - 7:00 PM")
    print("   • No teacher conflicts across batches")
    print("   • Lunch break at 1:00-2:00 PM")
    print("   • 2 sessions per subject per batch")
    print()

    success = solve_and_display_fixed_faculty()

    if success:
        print("\n✅ Optimization completed successfully!")
        print("🎯 All classes now fit within 8:30 AM - 7:00 PM window")
        print("👨‍🏫 Original faculty assignments preserved")
    else:
        print("\n❌ Optimization failed with fixed faculty constraints")
        print("💡 Consider minor faculty adjustments to resolve conflicts")
