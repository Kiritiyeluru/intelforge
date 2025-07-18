# College Timetable Optimization Guide

## 📋 Time Slot Configuration

### Standard Time Slots (1.5 hours each)
- **Slot 0**: 6:30 AM - 8:00 AM (EARLY SLOT - KIRITI only)
- **Slot 1**: 8:30 AM - 10:00 AM
- **Slot 2**: 10:00 AM - 11:30 AM
- **Slot 3**: 11:30 AM - 1:00 PM
- **Lunch**: 1:00 PM - 2:00 PM
- **Slot 4**: 2:00 PM - 3:30 PM
- **Slot 5**: 3:30 PM - 5:00 PM
- **Slot 6**: 5:30 PM - 7:00 PM

### Special Slots for 9th Class
- **8:30 AM - 10:00 AM**: IOQM Exam (blocked)
- **10:00 AM - 1:00 PM**: Combined Slots 1 & 2 (3 hours)
- **2:00 PM - 5:00 PM**: Combined Slots 3 & 4 (3 hours)
- **5:30 PM - 7:00 PM**: Slot 5 (1.5 hours - counts as 2 slots for faculty)

## 🏢 Building Layout & Distance Constraints

### Building 1 (Close Distance)
- **AK_E_JR_1**
- **AK_E_JR_2**

### Building 2 (0.55 km from Building 1)
- **AK-SR-2**
- **AK-JR-2**
- **AK-JR-3**

### Building 3 (Far Distance - Traffic Issues)
- **9th Class**
- **Requires lunch break (1-2 PM) or evening break (5-5:30 PM) for travel**

## 📐 Key Constraints

### Faculty Assignment Rules
1. **Faculty cannot be changed between batches**
2. **Classes must run from 6:30 AM to 7:00 PM maximum** (with early slot)
3. **Minimize faculty travel between buildings**

### KIRITI Special Requirements (NEW)
- **Early slot (6:30-8:00 AM) only for KIRITI** in Building 1 (AK_E_JR_1, AK_E_JR_2)
- **If KIRITI starts at 6:30 AM, all KIRITI classes must end by 5:00 PM**
- **No other faculty can use the 6:30-8:00 AM slot**

### PRK Overlap (ALLOWED)
- **PRK can teach both AK-JR-2 and AK-JR-3 CHEM at 10:00-11:30 AM** (only allowed overlap)
- **This is the only teacher overlap permitted**

### 9th Class Special Requirements
- **Both 1.5-hour classes must be scheduled together** (avoid double travel)
- **No grouping options available**
- **Faculty taking 5:30-7:00 PM slot counts as having 2 slots that day**

### Building Preferences (RELAXED)
- **AK_E_JR_1 and AK_E_JR_2**: Adjacency preference relaxed (flexible scheduling)
- **Other batches**: Prefer adjacent slots but allow flexibility
- **Acceptable**: Non-adjacent sessions if needed for feasible solution

## ⚠️ Current Issues

### Schedule Overrun Problems
- **Target**: All classes end by 7:00 PM
- **Current**: Classes extending to 8:30 PM and 10:30 PM
- **Cause**: Poor arrangement creating 1.5-hour gaps for faculty

### Fixed Batch (Do Not Modify)
**AK-JR-1**:
- **CHEM - PRK**: Fixed at 1:30-3:30 PM and 3:30-5:00 PM
- **Reason**: Different timing constraints, only common slot available
- **Faculty**: Sagar Das and Srikanth (no overlap with other batches)
- **Action**: Remove entirely from optimization process
## 📅 Current Timetables (July 16, 2025)

### Building 1: AK-EXTEN-JR Classes

#### AK_E_JR_1
```
TIME        | 6:30-8:00   | 8:30-10:00    | 10:00-11:30   | 11:40-1:00   | 1:00-2:00   | 2:00-3:30 | 3:30-5:00 | 5:30-7:00    | 7:00-8:30    | 9:00-10:30
--------------------------------------------------------------------------------------------------------------------------------------
AK_E_JR_1   | PHYSICS-WORK| MATHS-RAMREDDY| MATHS-RAMREDDY| CHEM-WORKING | LUNCH BREAK | CHEM-KK   | CHEM-KK   | PHYSICS-KIRITI| PHYSICS-KIRITI| MATHS-WORKING
```

#### AK_E_JR_2
```
TIME        | 6:30-8:00   | 8:30-10:00    | 10:00-11:30   | 11:40-1:00   | 1:00-2:00   | 2:00-3:30 | 3:30-5:00 | 5:30-7:00    | 7:00-8:30    | 9:00-10:30
--------------------------------------------------------------------------------------------------------------------------------------
AK_E_JR_2   | PHYSICS-WORK| PHYSICS-KIRITI| PHYSICS-KIRITI| MATHS-RAMREDDY| LUNCH BREAK | MATHS-RAM | CHEM-WORKING| CHEM-KK     | CHEM-KK     | MATHS-WORKING
```

### Building 2: AK-SR & JR Classes

#### AK-SR-1
```
TIME        | 6:30-8:00   | 8:30-10:30    | 10:40-12:30   | 12:30-1:30 | 1:30-3:30    | 3:30-5:30    | 6:00-8:00     | 8:30-10:30
--------------------------------------------------------------------------------------------------------------------------
AK-SR-1     | MPC-WORKING | PHYSICS-SAGAR | PHYSICS-SAGAR | LUNCH BREAK| MATHS-SRIKANTH| MATHS-SRIKANTH| CHEM-SAIDIREDDY| CHEM-SAIDIREDDY
```

#### AK-SR-2
```
TIME        | 6:30-8:00  | 8:30-10:00     | 10:00-11:30  | 11:40-1:00  | 1:00-2:00   | 2:00-3:30   | 3:30-5:00   | 5:30-7:00    | 7:00-8:30    | 9:00-10:30
----------------------------------------------------------------------------------------------------------------------------------------
AK-SR-2     | CHEM-WORK  | PHYSICS-ANILK  | MATHS-RAJESH | MATHS-RAJESH| LUNCH BREAK | CHEM-SAIDI  | CHEM-SAIDI  | PHYSICS-ANILK| PHYSICS-WORKING| MATHS-WORKING
```

#### AK-JR-1 (Fixed - Do Not Modify)
```
TIME        | 6:30-8:00   | 8:30-10:30    | 10:40-12:30   | 12:30-1:30 | 1:30-3:30  | 3:30-5:30  | 6:00-8:00      | 8:30-10:30
-----------------------------------------------------------------------------------------------------------------------
AK-JR-1     | MPC-WORKING | MATHS-SRIKANTH| MATHS-SRIKANTH| LUNCH BREAK| CHEM-PRK   | CHEM-PRK   | PHYSICS-SAGARDAS| PHYSICS-SAGARDAS
```

#### AK-JR-2
```
TIME        | 6:30-8:00  | 8:30-10:00 | 10:00-11:30| 11:40-1:00| 1:00-2:00   | 2:00-3:30    | 3:30-5:00    | 5:30-7:00    | 7:00-8:30      | 9:00-10:30
----------------------------------------------------------------------------------------------------------------------------------------
AK-JR-2     | MATHS-WORK | CHEM-PRK   | CHEM-PRK   | CHEM-WORK  | LUNCH BREAK | MATHS-RAJESH | MATHS-RAJESH | PHYSICS-WORKING| PHYSICS-ANILK | PHYSICS-ANILK
```

#### AK-JR-3
```
TIME        | 6:30-8:00    | 8:30-10:00 | 10:00-11:30| 11:40-1:00| 1:00-2:00   | 2:00-3:30     | 3:30-5:00     | 5:30-7:00     | 7:00-8:30     | 9:00-10:30
----------------------------------------------------------------------------------------------------------------------------------------
AK-JR-3     | PHYSICS-WORK | CHEM-WORK  | CHEM-PRK   | CHEM-PRK   | LUNCH BREAK | PHYSICS-KIRITI| PHYSICS-KIRITI| MATHS-RAMREDDY| MATHS-RAMREDDY| MATHS-WORKING
```

### Building 3: 9th Class
```
TIME        | 8:00-11:00 | 11:10-1:00     | 1:00-2:00   | 2:00-5:00       | 5:00-8:00
-------------------------------------------------------------------------------------
9th CLASS   | IOQM EXAM  | CHEM-KK        | LUNCH BREAK | PHYSICS-ANILKUMAR| MATHS-RAJESH
```

### 🚨 Current Schedule Issues

**Classes Running Over 7:00 PM Deadline:**
- **AK_E_JR_1**: Extends to 8:30 PM (issue: 7:00-8:30 PM slot)
- **AK_E_JR_2**: Extends to 8:30 PM (issue: 7:00-8:30 PM slot)
- **AK-JR-2**: Extends to 10:00 PM (MAJOR issue: 7:00-10:30 PM)
- **AK-JR-3**: Extends to 8:30 PM (issue: 7:00-8:30 PM slot)
- **AK-SR-2**: No issue - classes end by 7:00 PM ✅

**Notes:**
- 9:00-10:30 PM slots are "working hours" (self-study) - faculty not required
- Real issue is 7:00-8:30 PM extension for most batches

---

# OR-Tools Timetable Optimization Guide

## 📋 Quick Setup

### 1. Install OR-Tools
```bash
sudo apt update
sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install ortools
```

### 2. VS Code Setup
```bash
code .
# Install Python extension: Ctrl+Shift+X → Search "Python"
# Select interpreter: Ctrl+Shift+P → "Python: Select Interpreter" → Choose ./venv/bin/python
```

### 3. Basic Solver Template
```python
from ortools.sat.python import cp_model

# Define your problem variables
batches = ["AK_E_JR_1", "AK_E_JR_2", "AK-SR-2"]
subjects = ["Math", "Physics", "Chem"]
time_slots = 6

model = cp_model.CpModel()

# Create decision variables: timetable[batch][slot] = subject_index
timetable = {}
for batch in batches:
    timetable[batch] = [
        model.NewIntVar(0, len(subjects) - 1, f"{batch}_slot_{s}")
        for s in range(time_slots)
    ]

# Add constraints
for batch in batches:
    model.AddAllDifferent(timetable[batch])  # No repeated subjects

# Solve
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL:
    for batch in batches:
        print(f"Batch {batch}:")
        for slot in range(time_slots):
            subject = subjects[solver.Value(timetable[batch][slot])]
            print(f"  Slot {slot+1}: {subject}")
```

### 4. Export Results
```python
import csv
with open("optimized_schedule.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Batch", "Slot", "Subject"])
    for batch in batches:
        for slot in range(time_slots):
            subject = subjects[solver.Value(timetable[batch][slot])]
            writer.writerow([batch, slot + 1, subject])
```

---

## 🎯 Implemented Solution

### ✅ Problem Solved: July 15, 2025

**Issue:** Classes extending beyond 7:00 PM deadline to 8:30 PM and 10:30 PM for various batches.

**Solution:** OR-Tools based optimizer preserving faculty assignments while rearranging timings within 8:30 AM - 7:00 PM window.

### 📁 Solution Files

1. **`timetable_optimizer.py`** - Initial optimizer (allows faculty changes) ❌ Not used
2. **`fixed_faculty_optimizer.py`** - Previous solution ❌ Deprecated
3. **`building_aware_optimizer.py`** - ✅ **CURRENT SOLUTION** - With early slot & relaxed constraints

### 🔧 Usage Instructions

```bash
# Navigate to project directory
cd "/home/kiriti/alpha_projects/intelforge"

# Activate virtual environment
source venv/bin/activate

# Navigate to optimizer directory
cd "user created/external tips"

# Run the building-aware optimizer with new constraints
python3 building_aware_optimizer.py
```

### 📊 Optimization Results

**Before:**
- **AK-JR-2**: Classes until 10:00 PM ❌
- **AK-JR-3**: Classes until 8:30 PM ❌
- **AK_E_JR_1**: Classes until 8:30 PM ❌
- **AK_E_JR_2**: Classes until 8:30 PM ❌

**Current Target (Updated Constraints):**
- **ALL BATCHES**: Classes end by 7:00 PM ✅
- **EARLY SLOT**: 6:30-8:00 AM available for KIRITI only ✅
- **KIRITI CONSTRAINT**: If starting at 6:30 AM, end by 5:00 PM ✅
- **PRK OVERLAP**: Allowed at 10:00-11:30 AM for AK-JR-2 & AK-JR-3 ✅
- **RELAXED ADJACENCY**: Flexible scheduling for AK_E batches ✅
- **Faculty assignments**: Preserved exactly ✅
- **Lunch break**: Maintained at 1:00-2:00 PM ✅

### 🛠️ Technical Details

- **Solver**: Google OR-Tools CP-SAT (Constraint Programming)
- **Updated Constraints**:
  - Fixed faculty assignments per batch
  - 6:30 AM - 7:00 PM time window (with early slot)
  - KIRITI early slot exclusivity (6:30-8:00 AM)
  - KIRITI 5 PM deadline if using early slot
  - PRK overlap allowed at 10:00-11:30 AM only
  - Relaxed adjacency for AK_E_JR_1 & AK_E_JR_2
  - 2 sessions per subject per batch
  - Lunch break at 1:00-2:00 PM
- **Optimization Time**: TBD (in progress)
- **Status**: Under development with new constraints

### 📝 Key Learnings

1. **Faculty assignments are non-negotiable** - must be preserved
2. **OR-Tools CP-SAT** excellent for complex scheduling problems
3. **Plain text table output** most practical for educational scheduling
4. **Teacher conflict resolution** critical for feasible solutions
5. **Constraint modeling** requires balance between flexibility and requirements

### 🔍 Troubleshooting Tips

**If optimizer fails:**
1. Check teacher conflicts in faculty assignments
2. Verify time slot configuration matches available hours
3. Ensure lunch break timing doesn't conflict with class requirements
4. Consider adjusting session distribution if needed

**For new batches/faculty:**
1. Add new entries to `BATCH_FACULTY` dictionary
2. Update `BATCHES` list to include new batch names
3. Ensure all faculty are properly assigned to subjects
