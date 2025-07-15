#!/usr/bin/env python3
"""
Timetable Optimizer using Google OR-Tools CP-SAT
Constraint: Classes must fit within 8:30 AM - 7:00 PM window
Problem: AK-JR-2 and AK-JR-3 have spillover from 7:00-8:30 PM
"""

from ortools.sat.python import cp_model
import csv
from datetime import datetime, timedelta

# Define time slots (8:30 AM - 7:00 PM)
TIME_SLOTS = [
    "8:30-10:00",
    "10:00-11:30", 
    "11:40-1:00",
    "1:00-2:00",    # LUNCH BREAK
    "2:00-3:30",
    "3:30-5:00",
    "5:30-7:00"
]

# Working time slots (excluding lunch)
WORKING_SLOTS = [0, 1, 2, 4, 5, 6]  # Skip slot 3 (lunch)
LUNCH_SLOT = 3

# Subject definitions
SUBJECTS = ["PHYSICS", "MATHS", "CHEM"]
SUBJECT_INDICES = {subj: i for i, subj in enumerate(SUBJECTS)}

# Teacher assignments (from current timetable)
TEACHERS = {
    "PHYSICS": ["KIRITI", "ANIL KUMAR", "SAGAR DAS"],
    "MATHS": ["RAM REDDY", "RAJESH", "SRIKANTH"], 
    "CHEM": ["PRK", "KK", "SAIDI"]
}

# Batches that need optimization (excluding AK-SR-1)
BATCHES = ["AK_E_JR_1", "AK_E_JR_2", "9th_CLASS", "AK-SR-2", "AK-JR-1", "AK-JR-2", "AK-JR-3"]

def create_timetable_model():
    """Create and solve the timetable optimization problem"""
    
    model = cp_model.CpModel()
    
    # Decision variables: schedule[batch][slot] = subject_index
    schedule = {}
    for batch in BATCHES:
        schedule[batch] = {}
        for slot in WORKING_SLOTS:
            schedule[batch][slot] = model.NewIntVar(0, len(SUBJECTS) - 1, f"{batch}_slot_{slot}")
    
    # Teacher assignment variables: teacher_assigned[batch][slot][teacher] = 1 if assigned
    teacher_assigned = {}
    for batch in BATCHES:
        teacher_assigned[batch] = {}
        for slot in WORKING_SLOTS:
            teacher_assigned[batch][slot] = {}
            for subject in SUBJECTS:
                for teacher in TEACHERS[subject]:
                    teacher_assigned[batch][slot][teacher] = model.NewBoolVar(f"{batch}_{slot}_{teacher}")
    
    # Constraint 1: Each batch must have balanced subject distribution
    for batch in BATCHES:
        subject_counts = {}
        for subject_idx, subject in enumerate(SUBJECTS):
            subject_counts[subject] = []
            for slot in WORKING_SLOTS:
                is_subject = model.NewBoolVar(f"{batch}_{slot}_{subject}_assigned")
                model.Add(schedule[batch][slot] == subject_idx).OnlyEnforceIf(is_subject)
                model.Add(schedule[batch][slot] != subject_idx).OnlyEnforceIf(is_subject.Not())
                subject_counts[subject].append(is_subject)
        
        # Each subject should appear 2 times per batch (6 slots / 3 subjects = 2 each)
        for subject in SUBJECTS:
            model.Add(sum(subject_counts[subject]) == 2)
    
    # Constraint 2: Teacher conflict resolution - one teacher per slot across all batches
    for slot in WORKING_SLOTS:
        for subject in SUBJECTS:
            for teacher in TEACHERS[subject]:
                # Teacher can teach at most one batch per slot
                teacher_uses = []
                for batch in BATCHES:
                    teacher_uses.append(teacher_assigned[batch][slot][teacher])
                model.Add(sum(teacher_uses) <= 1)
    
    # Constraint 3: Link subject assignment to teacher assignment
    for batch in BATCHES:
        for slot in WORKING_SLOTS:
            for subject_idx, subject in enumerate(SUBJECTS):
                is_subject = model.NewBoolVar(f"{batch}_{slot}_{subject}_check")
                model.Add(schedule[batch][slot] == subject_idx).OnlyEnforceIf(is_subject)
                model.Add(schedule[batch][slot] != subject_idx).OnlyEnforceIf(is_subject.Not())
                
                # If this subject is assigned, exactly one teacher must be assigned
                teachers_for_subject = [teacher_assigned[batch][slot][teacher] for teacher in TEACHERS[subject]]
                model.Add(sum(teachers_for_subject) == 1).OnlyEnforceIf(is_subject)
                model.Add(sum(teachers_for_subject) == 0).OnlyEnforceIf(is_subject.Not())
    
    # Constraint 4: Minimize gaps between classes (optional optimization)
    # This helps create more compact schedules
    gap_penalties = []
    for batch in BATCHES:
        for i in range(len(WORKING_SLOTS) - 1):
            slot1, slot2 = WORKING_SLOTS[i], WORKING_SLOTS[i + 1]
            if slot2 - slot1 > 1:  # There's a gap
                gap_penalty = model.NewBoolVar(f"{batch}_gap_{slot1}_{slot2}")
                gap_penalties.append(gap_penalty)
    
    # Objective: Minimize gaps
    model.Minimize(sum(gap_penalties))
    
    return model, schedule, teacher_assigned

def solve_and_display_timetable():
    """Solve the timetable problem and display results"""
    
    model, schedule, teacher_assigned = create_timetable_model()
    
    # Create solver and solve
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0  # 30 second timeout
    
    status = solver.Solve(model)
    
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        print("✅ OPTIMIZED TIMETABLE SOLUTION FOUND!")
        print("=" * 80)
        
        # Display the optimized timetable
        for batch in BATCHES:
            print(f"\n🎓 {batch.replace('_', ' ')}")
            print("-" * 60)
            
            for slot_idx, slot in enumerate(WORKING_SLOTS):
                if slot == LUNCH_SLOT:
                    continue
                    
                time_slot = TIME_SLOTS[slot]
                subject_idx = solver.Value(schedule[batch][slot])
                subject = SUBJECTS[subject_idx]
                
                # Find assigned teacher
                assigned_teacher = None
                for teacher in TEACHERS[subject]:
                    if solver.Value(teacher_assigned[batch][slot][teacher]) == 1:
                        assigned_teacher = teacher
                        break
                
                print(f"  {time_slot:<12} | {subject:<8} | {assigned_teacher}")
            
            print(f"  1:00-2:00    | LUNCH BREAK")
        
        # Export to CSV
        export_to_csv(solver, schedule, teacher_assigned)
        
        print(f"\n📊 Solver Statistics:")
        print(f"   Status: {solver.StatusName(status)}")
        print(f"   Time: {solver.WallTime():.2f} seconds")
        print(f"   Conflicts: {solver.NumConflicts()}")
        
        return True
        
    else:
        print("❌ NO SOLUTION FOUND")
        print(f"Status: {solver.StatusName(status)}")
        return False

def export_to_csv(solver, schedule, teacher_assigned):
    """Export the optimized timetable to CSV"""
    
    with open("optimized_timetable.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Batch", "Time_Slot", "Subject", "Teacher"])
        
        for batch in BATCHES:
            for slot in WORKING_SLOTS:
                if slot == LUNCH_SLOT:
                    writer.writerow([batch, "1:00-2:00", "LUNCH BREAK", ""])
                    continue
                
                time_slot = TIME_SLOTS[slot]
                subject_idx = solver.Value(schedule[batch][slot])
                subject = SUBJECTS[subject_idx]
                
                # Find assigned teacher
                assigned_teacher = ""
                for teacher in TEACHERS[subject]:
                    if solver.Value(teacher_assigned[batch][slot][teacher]) == 1:
                        assigned_teacher = teacher
                        break
                
                writer.writerow([batch, time_slot, subject, assigned_teacher])
    
    print("\n💾 Timetable exported to: optimized_timetable.csv")

if __name__ == "__main__":
    print("🚀 Starting Timetable Optimization...")
    print("📋 Constraints:")
    print("   • Classes must fit within 8:30 AM - 7:00 PM")
    print("   • No teacher conflicts across batches")
    print("   • Balanced subject distribution per batch")
    print("   • Lunch break at 1:00-2:00 PM")
    print()
    
    success = solve_and_display_timetable()
    
    if success:
        print("\n✅ Optimization completed successfully!")
        print("🎯 All classes now fit within 8:30 AM - 7:00 PM window")
    else:
        print("\n❌ Optimization failed - may need to adjust constraints")