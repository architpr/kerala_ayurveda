import pandas as pd
import os

def load_catalog():
    """Loads the product catalog CSV."""
    csv_path = 'products_catalog.csv'
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not find {csv_path}")
    return pd.read_csv(csv_path)

def check_safety_and_facts(draft_text, product_id, catalog_df):
    """
    Analyzes a content draft against the structured product data.
    Returns a list of error messages (issues).
    """
    issues = []
    
    # Get product data
    product_row = catalog_df[catalog_df['product_id'] == product_id]
    if product_row.empty:
        return [f"Product ID {product_id} not found in catalog."]
    
    product = product_row.iloc[0]
    
    # Lowercase text for easy matching
    draft_lower = draft_text.lower()
    
    # --- CHECK 1: ANIMAL PRODUCTS (Vegan Compliance) ---
    # Logic: If draft claims "vegan" but product contains animal products -> ERROR
    vegan_claims = ["vegan", "plant-based", "100% plant", "no animal products"]
    has_vegan_claim = any(claim in draft_lower for claim in vegan_claims)
    
    # In our CSV, 'contains_animal_products' is likely "No" or "Yes"
    # Let's normalize the CSV value
    contains_animal = str(product['contains_animal_products']).strip().lower()
    
    if has_vegan_claim and contains_animal != 'no':
        issues.append(
            f"[FACT ERROR] Draft claims product is 'Vegan/Plant-based', but catalog "
            f"`contains_animal_products` is '{product['contains_animal_products']}'."
        )

    # --- CHECK 2: SAFETY / CONTRAINDICATIONS ---
    # Logic: If draft claims "safe for everyone" matches absolute safety, valid contraindications exist -> ERROR
    safe_claims = ["safe for everyone", "no side effects", "completely safe", "everyone can take this"]
    has_safe_claim = any(claim in draft_lower for claim in safe_claims)
    
    contraindications = str(product['contraindications_short'])
    has_contraindications = contraindications.lower() != 'nan' and len(contraindications) > 5
    
    if has_safe_claim and has_contraindications:
        issues.append(
            f"[SAFETY ERROR] Draft claims 'Safe for everyone', but catalog lists contraindications: "
            f"\"{product['contraindications_short']}\"."
        )

    # --- CHECK 3: INGREDIENT VERIFICATION ---
    # Logic: Ensure key herbs mentioned are actually in the product (Anti-Hallucination)
    # This is a bit looser, usually we check if *new* herbs are invented.
    # For now, let's just reverse it: If product has "Ashwagandha" and draft discusses "Turmeric" explicitly as an ingredient...
    # (Skipping complex entity extraction for this simple script, sticking to 1 & 2 as primary)

    return issues

def test_safety_checker():
    print("Loading Catalog...")
    df = load_catalog()
    
    print("\n--- TEST CASE 1: UNSAFE DRAFT (Ashwagandha) ---")
    unsafe_draft = """
    Discover the magic of KA-P002! This Ashwagandha supplement is a miracle cure for all your stress. 
    It is completely safe for everyone to use, including pregnant women. 
    It is also 100% vegan.
    """
    print(f"Draft: {unsafe_draft.strip()}")
    print("Running Checks...")
    
    # KA-P002: Ashwagandha (Has contraindications: Pregnancy; Is Vegan: No (hypothetically, let's say checks pass or fail))
    # Actually in CSV line 3: Ashwagandha... contains_animal_products: No.
    # But contraindications: "Caution in thyroid... pregnancy".
    
    errors = check_safety_and_facts(unsafe_draft, "KA-P002", df)
    
    if errors:
        print("❌ ISSUES FOUND:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("✅ PASSED")

    print("\n--- TEST CASE 2: FACTUAL ERROR (Brahmi Oil) ---")
    # Let's simulate a case where we claim a non-vegan product is vegan (if KA-P003 was non-vegan).
    # Looking at CSV: KA-P003 (Brahmi Oil) -> contains_animal_products: No.
    # Let's try to simulate a mismatch manually or use a row that might be risky.
    # Let's invent a test row for demonstration if needed, or stick to the logic.
    
    # Let's try an error where we claim "Safe for everyone" on KA-P005 (Calm Tea) which has "caution in pregnancy"
    unsafe_draft_2 = """
    Our Calm Evening Herbal Tea (KA-P005) is the perfect way to unwind. 
    It creates no side effects and is safe for everyone.
    """
    print(f"Draft: {unsafe_draft_2.strip()}")
    errors_2 = check_safety_and_facts(unsafe_draft_2, "KA-P005", df)
    
    if errors_2:
        print("❌ ISSUES FOUND:")
        for e in errors_2:
            print(f"  - {e}")
    else:
        print("✅ PASSED")

    print("\n--- TEST CASE 3: SAFE DRAFT ---")
    safe_draft = """
    Ashwagandha Stress Balance Tablets (KA-P002) are traditionally used to support stress resilience. 
    Please consult your doctor if you are pregnant or have thyroid conditions.
    """
    print(f"Draft: {safe_draft.strip()}")
    errors_3 = check_safety_and_facts(safe_draft, "KA-P002", df)
    
    if errors_3:
        print("❌ ISSUES FOUND:")
        for e in errors_3:
            print(f"  - {e}")
    else:
        print("✅ PASSED (No critical safety/fact errors found)")

if __name__ == "__main__":
    test_safety_checker()
