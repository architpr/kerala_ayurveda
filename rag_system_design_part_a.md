# RAG System Design (Part A) - Kerala Ayurveda

## 1. Chunking Strategy

### A. FAQ Files (`faq_general_ayurveda_patients.md`)
*   **Strategy**: "Q&A Pair Preservation".
*   **Method**: Split the file by Markdown Level 2 Headers (`##`).
*   **Rationale**: Each question and its corresponding answer form a complete semantic unit. Splitting them mid-answer or combining multiple Q&As into one chunk would dilute the retrieval precision.
*   **Chunk Example**:
    *   *Metadata*: `source: "faq_general_ayurveda_patients.md"`, `topic: "combining with modern medicine"`
    *   *Content*: "## 1. Is Ayurveda safe to combine with modern medicine?\nAyurveda is often used alongside modern medicine..."

### B. Product Catalog (`products_catalog.csv`)
*   **Strategy**: "Row-as-Document".
*   **Method**: Treat each row as a distinct semantic unit. Flatten the columns into a structured text format for embedding.
*   **Rationale**: A product's attributes (herbs, benefits, contraindications) must stay together to allow for safety checks.
*   **Chunk Example**:
    *   *Metadata*: `product_id: "KA-P002"`, `name: "Ashwagandha Stress Balance Tablets"`
    *   *Content*: "Product: Ashwagandha Stress Balance Tablets. Category: Stress & Sleep. Target Concerns: Stress resilience; restful sleep. Contraindications: Caution in thyroid/autoimmune conditions, pregnancy, and with long-term medications."

### C. Long-form MD Files
*   **Strategy**: "Header-Semantic Split".
*   **Method**: Split by H2 headers (`##`). If a section is too long (> 512 tokens), recursively split by H3 or paragraph, preserving the H2 context.
*   **Rationale**: Keeps sections like "Safety" or "The Tridosha Model" intact, ensuring that retrieving one part of the explanation brings the necessary context.

---

## 2. Retrieval Method: Hybrid Search

We propose a **Hybrid Search** architecture combining **Vector Search (Dense)** and **BM25 (Sparse)**.

### Why BM25 is needed for Sanskrit Terms?
*   **Problem**: Standard embedding models (like `text-embedding-3-small` or `all-MiniLM-L6-v2`) may not have rich semantic representations for specific Sanskrit Ayurveda terms like "Vata", "Pitta", "Kapha", "Prakriti", or "Rasayana". They might treat them as rare/unknown tokens or map them to generic "health" concepts.
*   **Solution**: BM25 (Best Matching 25) relies on exact keyword matching and term frequency (TF-IDF). It ensures that if a user queries distinct terms like "Vata imbalance", the system prioritizes documents explicitly containing the word "Vata", rather than just documents about "movement" or "air" (the semantic equivalents).

---

## 3. Function Design (Pseudo-code)

```python
def answer_user_query(query):
    """
    RAG pipeline to answer user queries with a critical safety check using structured data.
    """
    
    # 1. RETRIEVAL (Hybrid)
    # Search across Markdown (Unstructured) and CSV (Structured)
    retrieved_docs = hybrid_search(query, k=5)
    
    # Separation of concerns
    product_docs = [d for d in retrieved_docs if d.source_type == 'product_csv']
    knowledge_docs = [d for d in retrieved_docs if d.source_type == 'markdown']
    
    # 2. CRITICAL: SAFETY CHECK
    # Check if we retrieved any specific product that might have contraindications
    safety_warnings = []
    
    for product in product_docs:
        # Extract the structured contraindications field
        contraindications = product.metadata['contraindications_short']
        
        # Check matching logic (Simple keyword or Semantic check)
        # Function: check_risk(user_query, contraindication_text)
        risk_detected = check_risk_conditions(query, contraindications)
        
        if risk_detected:
            safety_warnings.append(f"WARNING: Output blocked/flagged. Product '{product.name}' has contraindication: '{risk_detected}' matching your query.")

    # 3. GENERATION OR BLOCKING
    if safety_warnings:
        # RETURN SAFETY MESSAGE
        return {
            "response": "I cannot recommend this specifically because you mentioned a condition that is listed as a precaution for this product.",
            "details": safety_warnings,
            "status": "BLOCKED_SAFETY"
        }
    
    # If safe, generate answer using LLM
    context = format_docs(product_docs + knowledge_docs)
    answer = llm_generate(query, context)
    
    return {
        "response": answer,
        "sources": retrieved_docs,
        "status": "SUCCESS"
    }

def check_risk_conditions(query, contraindications_text):
    """
    Checks logic: Does the contraindication text mention a condition present in the query?
    """
    # Pseudo-logic
    query_conditions = extract_conditions(query) # e.g., ['thyroid']
    risk_found = None
    for condition in query_conditions:
        if condition in contraindications_text.lower():
            risk_found = condition
    return risk_found
```

---

## 4. Simulation

**User Query**: *"Can I take Ashwagandha if I have thyroid issues?"*

**System Execution Steps**:

1.  **Retrieval**:
    *   System finds `Ashwagandha` keyword (BM25) and "thyroid issues" context.
    *   **Retrieves CSV Row (KA-P002)**:
        *   `Name`: Ashwagandha Stress Balance Tablets
        *   `Contraindications`: "Caution in thyroid/autoimmune conditions, pregnancy, and with long-term medications"
    *   **Retrieves Markdown**: `faq_general_ayurveda_patients.md` (Section on Safety).

2.  **Safety Check**:
    *   Input: Query mentions "thyroid".
    *   Check: CSV `contraindications_short` contains "Caution in thyroid...".
    *   Match: "thyroid" == "thyroid".
    *   **Action**: **BLOCK** or **WARN**.

3.  **Output**:
    ```text
    Status: BLOCKED_SAFETY
    Detected Risk: Thyroid issues.
    Product Warning: KA-P002 (Ashwagandha Stress Balance Tablets) - Caution in thyroid/autoimmune conditions.
    
    System Response: "I cannot recommend Ashwagandha Stress Balance Tablets in this case. The product explicitly lists a caution for thyroid conditions. Please consult your physician."
    ```

---

## 5. Failure Mode: CSV Retrieval Failure

**Scenario**: The user asks about "Ashwagandha", but for some reason (e.g., retrieval threshold too high, or "Ashwagandha" vs "Ashwagandha Balance" mismatch), the **CSV row (KA-P002)** is **NOT** retrieved. Only the generic markdown files (e.g., `faq_general_ayurveda_patients.md`) are retrieved.

**Resulting Risk**:
*   The generic FAQ might say "Herbs like Ashwagandha are used for stress" (Section 3).
*   The `safety_check` function has **no structured data** to validate against.
*   **Result**: The LLM might generate a response saying: *"Yes, Ashwagandha is great for stress and helps with sleep!"* without mentioning the thyroid warning.
*   **Consequence**: **Hallucination/Omission of Safety**. The system fails to provide the critical warning because it relied only on unstructured generic text rather than the specific product datasheet. This highlights the absolute necessity of high-recall retrieval for the Product CSV.
