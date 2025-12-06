import pandas as pd
import os

def load_data():
    """
    Loads the product catalog CSV.
    """
    csv_path = 'products_catalog.csv'
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Could not find {csv_path}. Make sure you are in the correct directory.")
    
    return pd.read_csv(csv_path)

def safety_check(query, product_row):
    """
    Checks if the user query mentions a condition that appears in the product's contraindications.
    """
    contraindications = product_row.get('contraindications_short', '')
    if pd.isna(contraindications):
        return None
        
    contraindications = str(contraindications).lower()
    query = query.lower()
    
    # Simple keyword matching for simulation
    # In a real system, this would use entity extraction or specific medical condition mapping
    risk_keywords = ["pregnancy", "thyroid", "surgery", "liver", "kidney", "autoimmune"]
    
    found_risks = []
    
    for word in risk_keywords:
        # Check if condition is in query AND in contraindications
        if word in query and word in contraindications:
            found_risks.append(word)
            
    return found_risks

def retrieve_product_info(query, df):
    """
    Simulates retrieval. 
    If query contains 'ashwagandha', retrieve KA-P002.
    """
    if "ashwagandha" in query.lower():
        # Find the row where product_id is KA-P002
        matches = df[df['product_id'] == 'KA-P002']
        if not matches.empty:
            return matches.iloc[0]
    return None

def answer_user_query(query):
    print(f"\n{'='*50}")
    print(f"User Query: \"{query}\"")
    print(f"{'='*50}\n")
    
    try:
        df = load_data()
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # 1. Retrieval
    # Simulate hybrid search prioritizing product match
    product_row = retrieve_product_info(query, df)
    
    # 2. Process
    if product_row is not None:
        print(f"[System] Retrieved Product: {product_row['product_id']} - {product_row['name']}")
        print(f"[System] Database Contraindications: \"{product_row['contraindications_short']}\"")
        
        # 3. Critical Safety Check
        risks = safety_check(query, product_row)
        
        if risks:
            print(f"\n[SAFETY GUARDRAIL] BLOCKED: Risk detected -> {risks}")
            print(f"\n[Response]: \"I cannot recommend `{product_row['name']}` specifically because you mentioned conditions ({', '.join(risks)}) that are listed as precautions for this product. Please consult your physician.\"")
        else:
            print(f"\n[SAFETY GUARDRAIL] PASSED.")
            print(f"\n[Response]: \"Based on the product details, `{product_row['name']}` can help with {product_row['target_concerns']}. It contains {product_row['key_herbs']}.\"")
            
    else:
        print("[System] No specific product matched in catalog (Simulation only supports Ashwagandha queries for now).")
        print("\n[Response]: \"I couldn't find a specific product match, but in general Ayurveda...\"")

if __name__ == "__main__":
    # Test Case 1: Risky Query
    answer_user_query("Can I take Ashwagandha if I have thyroid issues?")
    
    # Test Case 2: Safe Query
    answer_user_query("I am looking for something for stress relief. Is Ashwagandha good?")
