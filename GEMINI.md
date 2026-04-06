# Session Initialization Protocol

Welcome back. To get up to speed on the AI-Powered Concert Band Arranger project, follow these steps immediately:

1.  **Read `docs/plan.md`**: This is the master architectural roadmap.
2.  **Read `docs/todo.md`**: This contains the immediate granular tasks and Phase 2 progress.
3.  **Read `docs/note-to-self.md`**: **CRITICAL.** This contains the technical "soul" of the project—what failed, what we are currently thinking, and exactly where we left off.
4.  **Analyze Source Code**:
    *   `src/processor.py`: The "Dials" (mathematical engine).
    *   `src/critic.py`: The "Brain" (AI grading logic).
    *   `src/evolver.py`: The "Manager" (Evolutionary loop).

### Checkpoint Protocol
Whenever the user says **"Let's do a checkpoint,"** you must:
1.  Update `docs/plan.md` with any new architectural decisions.
2.  Update `docs/todo.md` with current task status.
3.  Refresh `docs/note-to-self.md` with the latest thinking, failures, and "next session" priorities.
