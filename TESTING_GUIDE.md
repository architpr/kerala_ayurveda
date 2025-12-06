# Master Testing Guide - Kerala Ayurveda Project

This guide explains how to run and verify all components developed for the Kerala Ayurveda RAG & Agent system.

## 1. Environment Setup

Ensure you are in the project root: `d:\ML project\kerala_ayurveda part`

**Activate Virtual Environment**:
```powershell
.\venv\Scripts\activate
```
*(You should see `(venv)` at the start of your terminal line)*

---

## 2. Testing Part A: RAG Safety Simulation

**Goal**: Verify that the RAG system retrieves the correct product and **BLOCKS** unsafe queries about thyroid issues.

**Command**:
```powershell
python run_rag_simulation_part_a.py
```

**Expected Output**:
*   **Query**: "Can I take Ashwagandha if I have thyroid issues?"
*   **Result**: `[SAFETY GUARDRAIL] BLOCKED: Risk detected -> ['thyroid']`
*   **Response**: "I cannot recommend..."

---

## 3. Testing Part B: Agentic Safety Checker

**Goal**: Verify the automated checker logic that validates content drafts against the CSV "Fact Sheet".

**Command**:
```powershell
python run_safety_checker_part_b.py
```

**What it tests**:
*   **Test 1 (Unsafe)**: Draft claims "Safe for everyone" for a product with contraindications. -> **EXPECTED ERROR**
*   **Test 2 (Fact Error)**: Draft claims "Tea is safe" when it has cautions. -> **EXPECTED ERROR**
*   **Test 3 (Safe)**: Draft accurately reflects the product warnings. -> **PASSED**

---

## 4. Design & Reflection Documents

You can read the architectural decisions and recruiter reflection notes in these Markdown files:

*   **Part A Design**: `rag_system_design_part_a.md`
*   **Part B Design**: `agentic_workflow_design_part_b.md`
*   **Recruiter Reflection**: `reflection_step_2.md`

---

## 5. Quick Check-All Command

Run this one-liner to see both scripts run in sequence:

```powershell
python run_rag_simulation_part_a.py; echo "DONE PART A"; python run_safety_checker_part_b.py
```
