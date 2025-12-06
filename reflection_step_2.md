# Reflection (Step 2)

*   **Hybrid Data Unification Challenge**: The primary technical complexity lay in reconciling the strict, tabular constraints of the Product CSV (SKUs, specific contraindications) with the free-flowing, unstructured nature of the educational Markdown content. Designing a retrieval strategy that respects both—fetching "exact row matches" for safety while pulling "semantic context" for explanations—was critical to preventing hallucinations.

*   **Safety-First Retrieval Architecture**: We deliberately chose a "Row-as-Document" chunking strategy for the CSV to ensure that a product's safety warnings are never decoupled from its identity. This prevents the dangerous scenario where an agent retrieves a product's benefits but misses its warnings because they were split into a different chunk.

*   **AI vs. Manual Design Balance**: While we leveraged AI to generate the initial JSON schemas and skeleton code for the agent definitions, the critical logic for the `safety_check` function was manually architected. Reliance on AI for the safety logic itself was deemed too risky; hard-coded logic checking the `contraindications` column provides the deterministic guardrails necessary for a medical/wellness application.

*   **Tone As a Systematic Constraint**: Transforming "Tone" from a subjective feeling into an objective metric (via the "Tone Adherence Score") allowed us to automate quality control. By treating specific phrases ("miracle cure") as hard constraints, we moved the editing process from a creative review to a scalable, automated pipeline.
