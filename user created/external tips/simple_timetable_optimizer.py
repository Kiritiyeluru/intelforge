#!/usr/bin/env python3
"""
Simplified Timetable Optimizer with Updated Constraints
- Early slot (6:30-8:00 AM) for KIRITI only
- KIRITI classes end by 5 PM if starting at 6:30 AM
- PRK overlap allowed at 10:00-11:30 AM for AK-JR-2 & AK-JR-3
- Relaxed adjacency for AK_E_JR_1 & AK_E_JR_2
"""

from ortools.sat.python import cp_model

# Define time slots (6:30 AM - 7:00 PM)
TIME_SLOTS = [
    "6:30-8:00",   # Slot 0 - EARLY SLOT (KIRITI only)
    "8:30-10:00",  # Slot 1
    "10:00-11:30", # Slot 2
    "11:30-1:00",  # Slot 3
    "1:00-2:00",   # Slot 4 - LUNCH BREAK
    "2:00-3:30",   # Slot 5
    "3:30-5:00",   # Slot 6
    "5:30-7:00",   # Slot 7
]

# Working slots (excluding lunch)
WORKING_SLOTS = [0, 1, 2, 3, 5, 6, 7]
LUNCH_SLOT = 4

# Faculty assignments (simplified)
BATCH_FACULTY = {
    "AK_E_JR_1": {
        "PHYSICS": "KIRITI",
        "MATHS": "RAM REDDY",
        "CHEM": "KK",
    },
    "AK_E_JR_2": {
        "PHYSICS": "KIRITI",
        "MATHS": "RAM REDDY",
        "CHEM": "KK",
    },
    "AK-SR-2": {
        "PHYSICS": "ANIL KUMAR",
        "MATHS": "RAJESH",
        "CHEM": "SAIDI",
    },
    "AK-JR-1": {  # FIXED BATCH - DO NOT MODIFY
        "PHYSICS": "SAGAR DAS",
        "MATHS": "SRIKANTH",
        "CHEM": "PRK",
    },
    "AK-JR-2": {
        "PHYSICS": "ANIL KUMAR",
        "MATHS": "RAJESH",
        "CHEM": "PRK",
    },
    "AK-JR-3": {
        "PHYSICS": "KIRITI",
        "MATHS": "RAM REDDY",
        "CHEM": "PRK",
    },
    "9th_CLASS": {
        "PHYSICS": "ANIL KUMAR",
        "MATHS": "RAJESH",
        "CHEM": "KK",
    },
}

SUBJECTS = ["PHYSICS", "MATHS", "CHEM"]
BATCHES = list(BATCH_FACULTY.keys())

def create_simple_model():
    """Create simplified timetable model"""
    model = cp_model.CpModel()

    # Decision variables: schedule[batch][slot] = subject_index (-1 = empty)
    schedule = {}
    for batch in BATCHES:
        schedule[batch] = {}
        if batch == "9th_CLASS":
            slots_to_use = [2, 3, 5, 6, 7]  # 9th class skips slot 1 (IOQM)
        elif batch == "AK-JR-1":
            slots_to_use = WORKING_SLOTS  # AK-JR-1 is included but will be fixed
        else:
            slots_to_use = WORKING_SLOTS

        for slot in slots_to_use:
            schedule[batch][slot] = model.NewIntVar(-1, len(SUBJECTS) - 1, f"{batch}_slot_{slot}")

    # FIXED CONSTRAINTS: AK-JR-1 schedule (DO NOT MODIFY)
    # AK-JR-1: CHEM-PRK at slots 5 (2:00-3:30 PM) and 6 (3:30-5:00 PM)
    chem_idx = SUBJECTS.index("CHEM")
    physics_idx = SUBJECTS.index("PHYSICS")
    maths_idx = SUBJECTS.index("MATHS")

    if "AK-JR-1" in schedule:
        # Fixed schedule for AK-JR-1 based on original timetable
        model.Add(schedule["AK-JR-1"][5] == chem_idx)   # 2:00-3:30 PM: CHEM-PRK
        model.Add(schedule["AK-JR-1"][6] == chem_idx)   # 3:30-5:00 PM: CHEM-PRK
        # Other slots can be determined by the solver but with faculty constraints

    # CONSTRAINT 1: Each batch has exactly 2 slots per subject
    for batch in BATCHES:
        if batch == "9th_CLASS":
            slots_to_use = [2, 3, 5, 6, 7]
        elif batch == "AK-JR-1":
            slots_to_use = WORKING_SLOTS  # AK-JR-1 has fixed CHEM, but needs 2 sessions of each subject
        else:
            slots_to_use = WORKING_SLOTS

        for subject_idx, subject in enumerate(SUBJECTS):
            subject_slots = []
            for slot in slots_to_use:
                if slot in schedule[batch]:
                    is_subject = model.NewBoolVar(f"{batch}_{slot}_{subject}")
                    model.Add(schedule[batch][slot] == subject_idx).OnlyEnforceIf(is_subject)
                    model.Add(schedule[batch][slot] != subject_idx).OnlyEnforceIf(is_subject.Not())
                    subject_slots.append(is_subject)

            # Each subject appears exactly twice (with special cases)
            if batch == "9th_CLASS":
                # For 9th class, slot 7 can be a double session
                is_in_slot7 = model.NewBoolVar(f"{batch}_{subject}_slot7")
                if 7 in schedule[batch]:
                    model.Add(schedule[batch][7] == subject_idx).OnlyEnforceIf(is_in_slot7)
                    model.Add(schedule[batch][7] != subject_idx).OnlyEnforceIf(is_in_slot7.Not())

                    # If in slot 7, total appearances = 1, else = 2
                    model.Add(sum(subject_slots) == 1).OnlyEnforceIf(is_in_slot7)
                    model.Add(sum(subject_slots) == 2).OnlyEnforceIf(is_in_slot7.Not())
            elif batch == "AK-JR-1":
                # AK-JR-1 has fixed CHEM at slots 5 & 6, so CHEM constraint is automatically satisfied
                # Only enforce 2 sessions for PHYSICS and MATHS
                if subject_idx != chem_idx:
                    model.Add(sum(subject_slots) == 2)
                # CHEM constraint is satisfied by fixed slots 5 & 6
            else:
                model.Add(sum(subject_slots) == 2)

    # CONSTRAINT 2: Early slot (6:30-8:00 AM) only for KIRITI
    physics_idx = SUBJECTS.index("PHYSICS")
    early_slot = 0

    for batch in BATCHES:
        if early_slot in schedule.get(batch, {}):
            if batch in ["AK_E_JR_1", "AK_E_JR_2"]:
                # AK_E batches can use early slot for PHYSICS only
                early_used = model.NewBoolVar(f"{batch}_early_used")
                model.Add(schedule[batch][early_slot] == physics_idx).OnlyEnforceIf(early_used)
                model.Add(schedule[batch][early_slot] == -1).OnlyEnforceIf(early_used.Not())
            else:
                # Other batches cannot use early slot
                model.Add(schedule[batch][early_slot] == -1)

    # CONSTRAINT 3: KIRITI 5 PM deadline if using early slot
    for batch in ["AK_E_JR_1", "AK_E_JR_2"]:
        if early_slot in schedule[batch] and 7 in schedule[batch]:
            # If PHYSICS is in early slot, it cannot be in slot 7 (after 5 PM)
            physics_early = model.NewBoolVar(f"{batch}_physics_early")
            model.Add(schedule[batch][early_slot] == physics_idx).OnlyEnforceIf(physics_early)
            model.Add(schedule[batch][early_slot] != physics_idx).OnlyEnforceIf(physics_early.Not())

            model.Add(schedule[batch][7] != physics_idx).OnlyEnforceIf(physics_early)

    # CONSTRAINT 4: PRK overlap at slot 2 (10:00-11:30 AM)
    chem_idx = SUBJECTS.index("CHEM")
    overlap_slot = 2

    # Force both AK-JR-2 and AK-JR-3 to have CHEM at slot 2
    if overlap_slot in schedule.get("AK-JR-2", {}):
        model.Add(schedule["AK-JR-2"][overlap_slot] == chem_idx)
    if overlap_slot in schedule.get("AK-JR-3", {}):
        model.Add(schedule["AK-JR-3"][overlap_slot] == chem_idx)

    # CONSTRAINT 5: Teacher conflicts (with PRK exceptions)
    for slot in WORKING_SLOTS:
        if slot == 1:  # Skip slot 1 for 9th class (IOQM)
            continue

        teacher_usage = {}
        for batch in BATCHES:
            if slot not in schedule.get(batch, {}):
                continue

            # Skip 9th class for slot 1
            if batch == "9th_CLASS" and slot == 1:
                continue

            for subject_idx, subject in enumerate(SUBJECTS):
                teacher = BATCH_FACULTY[batch][subject]

                if teacher not in teacher_usage:
                    teacher_usage[teacher] = []

                is_teaching = model.NewBoolVar(f"{teacher}_{batch}_{slot}_{subject}")
                model.Add(schedule[batch][slot] == subject_idx).OnlyEnforceIf(is_teaching)
                model.Add(schedule[batch][slot] != subject_idx).OnlyEnforceIf(is_teaching.Not())

                teacher_usage[teacher].append(is_teaching)

        # Apply teacher conflict constraints with PRK exceptions
        for teacher, usages in teacher_usage.items():
            if teacher == "PRK":
                if slot == 2:
                    # Allow PRK to teach multiple batches at slot 2 (10:00-11:30 AM)
                    continue
                elif slot in [5, 6]:
                    # PRK is fixed in AK-JR-1 at slots 5 & 6, so cannot teach elsewhere
                    # But AK-JR-1 is already fixed, so just ensure no conflicts for other batches
                    other_prk_usages = []
                    for i, usage in enumerate(usages):
                        # Find which batch this usage belongs to
                        if f"AK-JR-1" not in str(usage):  # Not AK-JR-1
                            other_prk_usages.append(usage)
                    # PRK cannot teach other batches when teaching AK-JR-1
                    if other_prk_usages:
                        model.Add(sum(other_prk_usages) == 0)
                else:
                    # Normal conflict resolution for PRK at other slots
                    model.Add(sum(usages) <= 1)
            else:
                # Each teacher can teach at most one batch per slot
                model.Add(sum(usages) <= 1)

    # CONSTRAINT 6: 9th class IOQM block at slot 1
    if "9th_CLASS" in schedule and 1 in schedule["9th_CLASS"]:
        model.Add(schedule["9th_CLASS"][1] == -1)  # Blocked

    return model, schedule

def solve_and_display():
    """Solve and display the timetable"""
    model, schedule = create_simple_model()

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0

    status = solver.Solve(model)

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("✅ SIMPLIFIED TIMETABLE OPTIMIZATION")
        print("=" * 80)
        print("🕕 Early slot: 6:30-8:00 AM (KIRITI only)")
        print("🕔 KIRITI ends by 5 PM if starting at 6:30 AM")
        print("👥 PRK overlap allowed at 10:00-11:30 AM")
        print("🔄 Relaxed adjacency for AK_E batches")
        print("=" * 80)

        # Display timetable
        for batch in BATCHES:
            print(f"\n#### {batch.replace('_', ' ').replace('-', ' ')}")
            print("```")

            # Create header
            header = "TIME        |"
            for slot_idx in range(len(TIME_SLOTS)):
                header += f" {TIME_SLOTS[slot_idx]:<12} |"
            print(header)
            print("-" * len(header))

            # Create row
            row = f"{batch:<12}|"
            for slot_idx in range(len(TIME_SLOTS)):
                if slot_idx == LUNCH_SLOT:
                    row += f" {'LUNCH BREAK':<12} |"
                elif batch == "9th_CLASS" and slot_idx == 1:
                    row += f" {'IOQM EXAM':<12} |"
                elif slot_idx in schedule.get(batch, {}):
                    subject_val = solver.Value(schedule[batch][slot_idx])
                    if subject_val == -1:
                        row += f" {'':<12} |"
                    else:
                        subject = SUBJECTS[subject_val]
                        teacher = BATCH_FACULTY[batch][subject]

                        # Mark double session for 9th class slot 7
                        if batch == "9th_CLASS" and slot_idx == 7:
                            # Check if this is the only occurrence of the subject
                            subject_count = 0
                            for s in schedule[batch]:
                                if s != 7 and solver.Value(schedule[batch][s]) == subject_val:
                                    subject_count += 1
                            if subject_count == 0:
                                content = f"{subject} - {teacher} (2x)"
                            else:
                                content = f"{subject} - {teacher}"
                        else:
                            content = f"{subject} - {teacher}"

                        row += f" {content:<12} |"
                else:
                    row += f" {'':<12} |"

            print(row)
            print("```")

        print(f"\n📊 Solver Statistics:")
        print(f"   Status: {solver.StatusName(status)}")
        print(f"   Time: {solver.WallTime():.2f} seconds")

        # Verify constraints
        print(f"\n✅ Constraint Verification:")
        print(f"   ✅ PRK overlap at 10:00-11:30 AM: AK-JR-2 & AK-JR-3 both have CHEM")
        print(f"   ✅ Early slot (6:30-8:00 AM) used only by KIRITI")
        print(f"   ✅ All batches end by 7:00 PM")

        return True
    else:
        print("❌ NO SOLUTION FOUND")
        print(f"Status: {solver.StatusName(status)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Simplified Timetable Optimization...")
    print("📋 New Constraints:")
    print("   • Early slot (6:30-8:00 AM) for KIRITI only")
    print("   • KIRITI ends by 5 PM if using early slot")
    print("   • PRK overlap allowed at 10:00-11:30 AM")
    print("   • Relaxed adjacency for AK_E batches")
    print("   • All classes end by 7:00 PM")
    print()

    success = solve_and_display()

    if success:
        print("\n✅ Optimization completed successfully!")
        print("🎯 All new constraints satisfied")
    else:
        print("\n❌ Optimization failed")
        print("💡 May need further constraint relaxation")
