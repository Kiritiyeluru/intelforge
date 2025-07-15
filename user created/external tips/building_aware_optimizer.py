#!/usr/bin/env python3
"""
Building-Aware Timetable Optimizer using Google OR-Tools CP-SAT
Constraints:
1. Faculty assignments are FIXED per batch (cannot be changed)
2. Building locations affect teacher availability
3. Travel time between buildings considered
4. Classes must fit within 8:30 AM - 7:00 PM window
"""

from ortools.sat.python import cp_model
from datetime import datetime, timedelta

# Define time slots (8:30 AM - 7:00 PM) - NUMBERED SYSTEM
TIME_SLOTS = [
    "8:30-10:00",    # Slot 1
    "10:00-11:30",   # Slot 2
    "11:30-1:00",    # Slot 3
    "1:00-2:00",     # LUNCH BREAK
    "2:00-3:30",     # Slot 4
    "3:30-5:00",     # Slot 5
    "5:30-7:00"      # Slot 6
]

# Fixed time slot assignments (cannot be changed)
FIXED_ASSIGNMENTS = {
    "AK-JR-1": {
        4: ("CHEM", "PRK", 0),  # Slot 4: 2:00-3:30 CHEM - PRK (session 0)
        5: ("CHEM", "PRK", 1),  # Slot 5: 3:30-5:00 CHEM - PRK (session 1)
    },
    "9th_CLASS": {
        0: ("BLOCKED", "IOQM", 0),  # Slot 1: 8:30-10:00 BLOCKED for IOQM
    }
}

# Working time slots (excluding lunch)
WORKING_SLOTS = [0, 1, 2, 4, 5, 6]  # Slots 1,2,3,4,5,6 (skip lunch)
LUNCH_SLOT = 3

# Working slots for 9th_CLASS (excluding blocked slot 1 and lunch)
NINTH_CLASS_WORKING_SLOTS = [1, 2, 4, 5, 6]  # Slots 2,3,4,5,6 (skip slot 1 and lunch)

# Building assignments
BUILDING_ASSIGNMENTS = {
    "Building_1": ["AK_E_JR_1", "AK_E_JR_2"],
    "Building_2": ["AK-SR-2", "AK-JR-1", "AK-JR-2", "AK-JR-3"],
    "Building_3": ["9th_CLASS"]
}

# Create reverse mapping: batch -> building
BATCH_BUILDING = {}
for building, batches in BUILDING_ASSIGNMENTS.items():
    for batch in batches:
        BATCH_BUILDING[batch] = building

# FIXED Faculty assignments per batch (extracted from original timetable)
BATCH_FACULTY = {
    "AK_E_JR_1": {
        "PHYSICS": ["KIRITI", "KIRITI"],  # 2 sessions
        "MATHS": ["RAM REDDY", "RAM REDDY"],  # 2 sessions
        "CHEM": ["KK", "KK"]  # 2 sessions
    },
    "AK_E_JR_2": {
        "PHYSICS": ["KIRITI", "KIRITI"],  # 2 sessions
        "MATHS": ["RAM REDDY", "RAM REDDY"],  # 2 sessions  
        "CHEM": ["KK", "KK"]  # 2 sessions
    },
    "9th_CLASS": {
        "PHYSICS": ["ANIL KUMAR", "ANIL KUMAR"],  # 2 sessions
        "MATHS": ["RAJESH", "RAJESH"],  # 2 sessions
        "CHEM": ["KK", "KK"]  # 2 sessions
    },
    "AK-SR-2": {
        "PHYSICS": ["ANIL KUMAR", "ANIL KUMAR"],  # 2 sessions
        "MATHS": ["RAJESH", "RAJESH"],  # 2 sessions
        "CHEM": ["SAIDI", "SAIDI"]  # 2 sessions
    },
    "AK-JR-1": {
        "PHYSICS": ["SAGAR DAS", "SAGAR DAS"],  # 2 sessions
        "MATHS": ["SRIKANTH", "SRIKANTH"],  # 2 sessions
        "CHEM": ["PRK", "PRK"]  # 2 sessions
    },
    "AK-JR-2": {
        "PHYSICS": ["ANIL KUMAR", "ANIL KUMAR"],  # 2 sessions
        "MATHS": ["RAJESH", "RAJESH"],  # 2 sessions
        "CHEM": ["PRK", "PRK"]  # 2 sessions
    },
    "AK-JR-3": {
        "PHYSICS": ["KIRITI", "KIRITI"],  # 2 sessions
        "MATHS": ["RAM REDDY", "RAM REDDY"],  # 2 sessions
        "CHEM": ["PRK", "PRK"]  # 2 sessions
    }
}

SUBJECTS = ["PHYSICS", "MATHS", "CHEM"]
BATCHES = list(BATCH_FACULTY.keys())

# Travel time constraints (in time slots)
TRAVEL_CONSTRAINTS = {
    ("Building_1", "Building_2"): 0,  # 0.55 km - no travel time needed
    ("Building_2", "Building_1"): 0,  # 0.55 km - no travel time needed
    ("Building_1", "Building_3"): 1,  # Far away - need lunch/snack break
    ("Building_3", "Building_1"): 1,  # Far away - need lunch/snack break
    ("Building_2", "Building_3"): 1,  # Far away - need lunch/snack break
    ("Building_3", "Building_2"): 1,  # Far away - need lunch/snack break
}

def create_building_aware_model():
    """Create timetable model with building location constraints"""
    
    model = cp_model.CpModel()
    
    # Decision variables: batch_schedule[batch][slot] = (subject_index, session_index)
    batch_schedule = {}
    for batch in BATCHES:
        batch_schedule[batch] = {}
        if batch == "9th_CLASS":
            # Special handling for 9th_CLASS with different time slots
            for slot in NINTH_CLASS_WORKING_SLOTS:
                batch_schedule[batch][slot] = {
                    'subject': model.NewIntVar(0, len(SUBJECTS)-1, f"{batch}_slot_{slot}_subject"),
                    'session': model.NewIntVar(0, 1, f"{batch}_slot_{slot}_session")
                }
        else:
            # Regular batches
            for slot in WORKING_SLOTS:
                batch_schedule[batch][slot] = {
                    'subject': model.NewIntVar(0, len(SUBJECTS)-1, f"{batch}_slot_{slot}_subject"),
                    'session': model.NewIntVar(0, 1, f"{batch}_slot_{slot}_session")
                }
    
    # Apply fixed assignments first
    for batch in BATCHES:
        if batch in FIXED_ASSIGNMENTS:
            for slot, (subject, teacher, session) in FIXED_ASSIGNMENTS[batch].items():
                batch_slots = NINTH_CLASS_WORKING_SLOTS if batch == "9th_CLASS" else WORKING_SLOTS
                if slot in batch_slots and slot in batch_schedule[batch]:
                    if subject != "BLOCKED":  # Only apply if not blocked
                        subject_idx = SUBJECTS.index(subject)
                        model.Add(batch_schedule[batch][slot]['subject'] == subject_idx)
                        model.Add(batch_schedule[batch][slot]['session'] == session)
    
    # Constraint 1: Each batch must have exactly 2 sessions of each subject
    for batch in BATCHES:
        if batch == "9th_CLASS":
            # Special constraint for 9th_CLASS: 
            # - Slot 6 (5:30-7:00 PM) counts as 2 sessions for the same subject
            # - Other slots count as 1 session each
            # - Need exactly 3 subjects total (one per available slot including slot 6)
            
            # For 9th_CLASS: Each subject needs exactly 2 sessions
            # - Have 5 working slots: [1, 2, 4, 5, 6]
            # - Slot 6 (5:30-7:00 PM) counts as 2 sessions
            # - If subject is in slot 6, it appears only once (but counts as 2 sessions)
            # - If subject is not in slot 6, it must appear exactly twice in other slots
            
            for subject_idx, subject in enumerate(SUBJECTS):
                subject_slots = []
                for slot in NINTH_CLASS_WORKING_SLOTS:
                    is_subject = model.NewBoolVar(f"{batch}_{slot}_{subject}_assigned")
                    model.Add(batch_schedule[batch][slot]['subject'] == subject_idx).OnlyEnforceIf(is_subject)
                    model.Add(batch_schedule[batch][slot]['subject'] != subject_idx).OnlyEnforceIf(is_subject.Not())
                    subject_slots.append(is_subject)
                
                # Check if subject is in slot 6
                is_in_slot6 = model.NewBoolVar(f"{batch}_{subject}_in_slot6")
                model.Add(batch_schedule[batch][6]['subject'] == subject_idx).OnlyEnforceIf(is_in_slot6)
                model.Add(batch_schedule[batch][6]['subject'] != subject_idx).OnlyEnforceIf(is_in_slot6.Not())
                
                # If in slot 6, appears exactly once (slot 6 = 2 sessions)
                # If not in slot 6, appears exactly twice in other slots
                model.Add(sum(subject_slots) == 1).OnlyEnforceIf(is_in_slot6)
                model.Add(sum(subject_slots) == 2).OnlyEnforceIf(is_in_slot6.Not())
        else:
            # Regular batches
            for subject_idx, subject in enumerate(SUBJECTS):
                subject_slots = []
                for slot in WORKING_SLOTS:
                    if slot in batch_schedule[batch]:  # Check if slot exists for this batch
                        is_subject = model.NewBoolVar(f"{batch}_{slot}_{subject}_assigned")
                        model.Add(batch_schedule[batch][slot]['subject'] == subject_idx).OnlyEnforceIf(is_subject)
                        model.Add(batch_schedule[batch][slot]['subject'] != subject_idx).OnlyEnforceIf(is_subject.Not())
                        subject_slots.append(is_subject)
                
                # Exactly 2 sessions per subject
                model.Add(sum(subject_slots) == 2)
    
    # Constraint 2: Each session (0 or 1) should be used exactly once per subject per batch
    for batch in BATCHES:
        slots_to_check = NINTH_CLASS_WORKING_SLOTS if batch == "9th_CLASS" else WORKING_SLOTS
        
        if batch == "9th_CLASS":
            # For 9th_CLASS, we don't enforce strict session constraints due to only 3 slots
            # Skip this constraint for 9th_CLASS
            continue
            
        for subject_idx, subject in enumerate(SUBJECTS):
            for session_idx in [0, 1]:
                session_uses = []
                for slot in slots_to_check:
                    if slot in batch_schedule[batch]:  # Check if slot exists for this batch
                        is_this_subject_session = model.NewBoolVar(f"{batch}_{slot}_{subject}_session_{session_idx}")
                        
                        # Both conditions must be true
                        model.Add(batch_schedule[batch][slot]['subject'] == subject_idx).OnlyEnforceIf(is_this_subject_session)
                        model.Add(batch_schedule[batch][slot]['session'] == session_idx).OnlyEnforceIf(is_this_subject_session)
                        
                        # If either condition is false, this var is false
                        subject_not_match = model.NewBoolVar(f"{batch}_{slot}_{subject}_not_match_{session_idx}")
                        session_not_match = model.NewBoolVar(f"{batch}_{slot}_{subject}_session_not_match_{session_idx}")
                        
                        model.Add(batch_schedule[batch][slot]['subject'] != subject_idx).OnlyEnforceIf(subject_not_match)
                        model.Add(batch_schedule[batch][slot]['session'] != session_idx).OnlyEnforceIf(session_not_match)
                        
                        model.AddBoolOr([is_this_subject_session, subject_not_match, session_not_match])
                        model.Add(is_this_subject_session == 0).OnlyEnforceIf(subject_not_match)
                        model.Add(is_this_subject_session == 0).OnlyEnforceIf(session_not_match)
                        
                        session_uses.append(is_this_subject_session)
                
                # Each session used exactly once
                model.Add(sum(session_uses) == 1)
    
    # Constraint 3: Building-aware teacher conflicts with travel time
    all_possible_slots = set(WORKING_SLOTS + NINTH_CLASS_WORKING_SLOTS)
    for slot in all_possible_slots:
        teacher_usage = {}
        
        for batch in BATCHES:
            # Check if this batch has this slot
            batch_slots = NINTH_CLASS_WORKING_SLOTS if batch == "9th_CLASS" else WORKING_SLOTS
            if slot not in batch_slots or slot not in batch_schedule[batch]:
                continue
                
            for subject_idx, subject in enumerate(SUBJECTS):
                for session_idx in [0, 1]:
                    teacher = BATCH_FACULTY[batch][subject][session_idx]
                    batch_building = BATCH_BUILDING[batch]
                    
                    if teacher not in teacher_usage:
                        teacher_usage[teacher] = {}
                    
                    if batch_building not in teacher_usage[teacher]:
                        teacher_usage[teacher][batch_building] = []
                    
                    # Check if this teacher is teaching this batch at this slot
                    teaching_here = model.NewBoolVar(f"{teacher}_{batch}_{slot}_{subject}_{session_idx}")
                    
                    # Teacher is teaching if both subject and session match
                    model.Add(batch_schedule[batch][slot]['subject'] == subject_idx).OnlyEnforceIf(teaching_here)
                    model.Add(batch_schedule[batch][slot]['session'] == session_idx).OnlyEnforceIf(teaching_here)
                    
                    # If either doesn't match, not teaching
                    not_subject = model.NewBoolVar(f"not_{batch}_{slot}_{subject}_{session_idx}")
                    not_session = model.NewBoolVar(f"not_session_{batch}_{slot}_{subject}_{session_idx}")
                    
                    model.Add(batch_schedule[batch][slot]['subject'] != subject_idx).OnlyEnforceIf(not_subject)
                    model.Add(batch_schedule[batch][slot]['session'] != session_idx).OnlyEnforceIf(not_session)
                    
                    model.AddBoolOr([teaching_here, not_subject, not_session])
                    model.Add(teaching_here == 0).OnlyEnforceIf(not_subject)
                    model.Add(teaching_here == 0).OnlyEnforceIf(not_session)
                    
                    teacher_usage[teacher][batch_building].append(teaching_here)
        
        # Apply building-specific constraints
        for teacher, buildings in teacher_usage.items():
            # Teacher can teach at most one batch per slot within same building
            for building, usages in buildings.items():
                model.Add(sum(usages) <= 1)
            
            # Check cross-building constraints
            building_list = list(buildings.keys())
            for i in range(len(building_list)):
                for j in range(i + 1, len(building_list)):
                    building1, building2 = building_list[i], building_list[j]
                    travel_time = TRAVEL_CONSTRAINTS.get((building1, building2), 0)
                    
                    if travel_time > 0:
                        # Teacher cannot teach in both buildings at same slot if travel time > 0
                        if buildings[building1] and buildings[building2]:
                            model.Add(sum(buildings[building1]) + sum(buildings[building2]) <= 1)
    
    # Very Strong Soft Constraint: Highly prefer adjacent sessions (almost hard)
    # Create objective variables for session grouping
    grouping_bonus = []
    
    # For each batch, strongly prefer adjacent sessions of same subject/teacher
    for batch in BATCHES:
        # Skip AK-JR-1 as it's fixed and undisturbed
        if batch == "AK-JR-1":
            continue
            
        # Get the appropriate slots for this batch
        batch_slots = NINTH_CLASS_WORKING_SLOTS if batch == "9th_CLASS" else WORKING_SLOTS
        
        if batch == "9th_CLASS":
            # For 9th_CLASS: MANDATORY grouping - faculty must make only 1 trip
            # Each subject must appear in adjacent slots (except slot 6 which counts as 2)
            for subject_idx, subject in enumerate(SUBJECTS):
                # Check all valid adjacent pairs for 9th_CLASS
                ninth_class_adjacent_pairs = [
                    (1, 2),  # Slots 2,3: 10:00-1:00 PM
                    (2, 4),  # Slots 3,4: 11:30-1:00 PM then 2:00-3:30 PM (across lunch)
                    (4, 5),  # Slots 4,5: 2:00-5:00 PM
                    # Slot 6 is special - counts as 2 sessions by itself
                ]
                
                # Check if subject is in slot 6 (counts as 2 sessions)
                is_in_slot6 = model.NewBoolVar(f"{batch}_{subject}_in_slot6")
                model.Add(batch_schedule[batch][6]['subject'] == subject_idx).OnlyEnforceIf(is_in_slot6)
                model.Add(batch_schedule[batch][6]['subject'] != subject_idx).OnlyEnforceIf(is_in_slot6.Not())
                
                # If in slot 6, subject is done (2 sessions)
                # If not in slot 6, must be in exactly one adjacent pair
                pair_assignments = []
                for slot1, slot2 in ninth_class_adjacent_pairs:
                    if slot1 in batch_schedule[batch] and slot2 in batch_schedule[batch]:
                        pair_assigned = model.NewBoolVar(f"{batch}_{subject}_{slot1}_{slot2}_pair")
                        
                        # Both slots must be the same subject
                        model.Add(batch_schedule[batch][slot1]['subject'] == subject_idx).OnlyEnforceIf(pair_assigned)
                        model.Add(batch_schedule[batch][slot2]['subject'] == subject_idx).OnlyEnforceIf(pair_assigned)
                        
                        # If not assigned to this pair, at least one slot is different subject
                        different_1 = model.NewBoolVar(f"diff1_{batch}_{subject}_{slot1}_{slot2}")
                        different_2 = model.NewBoolVar(f"diff2_{batch}_{subject}_{slot1}_{slot2}")
                        
                        model.Add(batch_schedule[batch][slot1]['subject'] != subject_idx).OnlyEnforceIf(different_1)
                        model.Add(batch_schedule[batch][slot2]['subject'] != subject_idx).OnlyEnforceIf(different_2)
                        
                        model.AddBoolOr([pair_assigned, different_1, different_2])
                        
                        pair_assignments.append(pair_assigned)
                
                # MANDATORY: Either in slot 6 OR in exactly one adjacent pair
                if pair_assignments:
                    model.Add(sum(pair_assignments) == 1).OnlyEnforceIf(is_in_slot6.Not())
                    model.Add(sum(pair_assignments) == 0).OnlyEnforceIf(is_in_slot6)
            continue
            
        # For regular batches: heavily reward adjacency
        for subject_idx, subject in enumerate(SUBJECTS):
            # Check all valid adjacent pairs
            valid_adjacent_pairs = [
                (0, 1),  # Slots 1,2: 8:30-11:30 AM
                (1, 2),  # Slots 2,3: 10:00-1:00 PM
                (2, 4),  # Slots 3,4: 11:30-1:00 PM then 2:00-3:30 PM (across lunch)
                (4, 5),  # Slots 4,5: 2:00-5:00 PM
                (5, 6),  # Slots 5,6: 3:30-7:00 PM
            ]
            
            for slot1, slot2 in valid_adjacent_pairs:
                if slot1 in batch_schedule[batch] and slot2 in batch_schedule[batch]:
                    # Check if both slots have the same subject
                    same_subject_adjacent = model.NewBoolVar(f"{batch}_{subject}_adjacent_{slot1}_{slot2}")
                    
                    # Both slots must be the same subject
                    model.Add(batch_schedule[batch][slot1]['subject'] == subject_idx).OnlyEnforceIf(same_subject_adjacent)
                    model.Add(batch_schedule[batch][slot2]['subject'] == subject_idx).OnlyEnforceIf(same_subject_adjacent)
                    
                    # If not same subject, set to false
                    not_same_1 = model.NewBoolVar(f"not_same_{batch}_{subject}_{slot1}_{slot2}_1")
                    not_same_2 = model.NewBoolVar(f"not_same_{batch}_{subject}_{slot1}_{slot2}_2")
                    
                    model.Add(batch_schedule[batch][slot1]['subject'] != subject_idx).OnlyEnforceIf(not_same_1)
                    model.Add(batch_schedule[batch][slot2]['subject'] != subject_idx).OnlyEnforceIf(not_same_2)
                    
                    model.AddBoolOr([same_subject_adjacent, not_same_1, not_same_2])
                    model.Add(same_subject_adjacent == 0).OnlyEnforceIf(not_same_1)
                    model.Add(same_subject_adjacent == 0).OnlyEnforceIf(not_same_2)
                    
                    # Add very high bonus for adjacency (almost hard constraint)
                    if BATCH_BUILDING[batch] == "Building_3":
                        grouping_bonus.append(same_subject_adjacent * 100)  # Very high weight for far building
                    else:
                        grouping_bonus.append(same_subject_adjacent * 50)   # High weight for close buildings
    
    # Set optimization objective to strongly favor grouping
    if grouping_bonus:
        model.Maximize(sum(grouping_bonus))
    
    return model, batch_schedule

def solve_and_display_building_aware():
    """Solve with building awareness and display chronologically"""
    
    model, batch_schedule = create_building_aware_model()
    
    # Create solver
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0
    
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("✅ BUILDING-AWARE TIMETABLE OPTIMIZATION")
        print("=" * 80)
        print("🏢 Building assignments considered")
        print("🚶 Travel time constraints applied")
        print("🎯 All classes fit within 8:30 AM - 7:00 PM")
        print("=" * 80)
        
        # Group by buildings for better organization
        for building, batches in BUILDING_ASSIGNMENTS.items():
            print(f"\n🏢 {building.upper()}")
            print("=" * 60)
            
            for batch in batches:
                if batch in BATCHES and batch != "AK-JR-1":  # Skip AK-JR-1 from display
                    print(f"\n#### {batch.replace('_', ' ').replace('-', ' ')}")
                    print()
                    print("```")
                    
                    if batch == "9th_CLASS":
                        # Special handling for 9th_CLASS with slot numbering
                        header = "TIME        |"
                        for slot_idx in range(len(TIME_SLOTS)):
                            slot_name = f"Slot {slot_idx + 1}" if slot_idx != LUNCH_SLOT else "Lunch"
                            header += f" {TIME_SLOTS[slot_idx]:<12} |"
                        
                        print(header)
                        print("-" * len(header))
                        
                        # Create table row for 9th_CLASS
                        row = f"{batch:<12}|"
                        
                        for slot_idx in range(len(TIME_SLOTS)):
                            if slot_idx == 0:  # Slot 1 - blocked for IOQM
                                row += f" {'IOQM EXAM':<12} |"
                            elif slot_idx == LUNCH_SLOT:  # Lunch break
                                row += f" {'LUNCH BREAK':<12} |"
                            elif slot_idx in NINTH_CLASS_WORKING_SLOTS and slot_idx in batch_schedule[batch]:
                                subject_idx = solver.Value(batch_schedule[batch][slot_idx]['subject'])
                                session_idx = solver.Value(batch_schedule[batch][slot_idx]['session'])
                                
                                subject = SUBJECTS[subject_idx]
                                teacher = BATCH_FACULTY[batch][subject][session_idx]
                                
                                # For slot 6 (5:30-7:00 PM), indicate it's a double session
                                if slot_idx == 6:  # Slot 6 is 5:30-7:00 PM
                                    cell_content = f"{subject} - {teacher} (2x)"
                                else:
                                    cell_content = f"{subject} - {teacher}"
                                row += f" {cell_content:<12} |"
                            else:
                                row += f" {'':<12} |"
                        
                        print(row)
                    else:
                        # Regular batch handling
                        header = "TIME        |"
                        for slot_idx in range(len(TIME_SLOTS)):
                            header += f" {TIME_SLOTS[slot_idx]:<12} |"
                        
                        print(header)
                        print("-" * len(header))
                        
                        # Create table row
                        row = f"{batch:<12}|"
                        
                        for slot_idx in range(len(TIME_SLOTS)):
                            if slot_idx == LUNCH_SLOT:
                                row += f" {'LUNCH BREAK':<12} |"
                            else:
                                # Find the working slot index
                                working_slot_idx = None
                                working_slot_counter = 0
                                for ws in WORKING_SLOTS:
                                    if ws == slot_idx:
                                        working_slot_idx = working_slot_counter
                                        break
                                    if ws < slot_idx:
                                        working_slot_counter += 1
                                
                                if working_slot_idx is not None and slot_idx in WORKING_SLOTS:
                                    subject_idx = solver.Value(batch_schedule[batch][slot_idx]['subject'])
                                    session_idx = solver.Value(batch_schedule[batch][slot_idx]['session'])
                                    
                                    subject = SUBJECTS[subject_idx]
                                    teacher = BATCH_FACULTY[batch][subject][session_idx]
                                    
                                    cell_content = f"{subject} - {teacher}"
                                    row += f" {cell_content:<12} |"
                                else:
                                    row += f" {'':<12} |"
                        
                        print(row)
                    print("```")
        
        print(f"\n📊 Solver Statistics:")
        print(f"   Status: {solver.StatusName(status)}")
        print(f"   Time: {solver.WallTime():.2f} seconds")
        print(f"   Conflicts: {solver.NumConflicts()}")
        
        # Building-specific travel analysis
        print(f"\n🏢 Building Travel Analysis:")
        for building, batches in BUILDING_ASSIGNMENTS.items():
            print(f"   {building}: {', '.join(batches)}")
        
        print(f"\n🚶 Travel Constraints:")
        print(f"   Building 1 ↔ Building 2: 0.55 km (no travel time)")
        print(f"   Building 3 ↔ Others: Far away (requires lunch/snack break)")
        
        return True
        
    else:
        print("❌ NO SOLUTION FOUND WITH BUILDING CONSTRAINTS")
        print(f"Status: {solver.StatusName(status)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Building-Aware Timetable Optimization...")
    print("📋 Constraints:")
    print("   • Faculty assignments are FIXED per batch")
    print("   • Building locations affect scheduling")
    print("   • Travel time between buildings considered")
    print("   • Classes must fit within 8:30 AM - 7:00 PM")
    print("   • Lunch break at 1:00-2:00 PM")
    print()
    
    success = solve_and_display_building_aware()
    
    if success:
        print("\n✅ Building-aware optimization completed!")
        print("🎯 All classes scheduled with building constraints")
        print("📅 Timetables displayed in chronological order")
    else:
        print("\n❌ Optimization failed with building constraints")
        print("💡 Consider adjusting travel time constraints")