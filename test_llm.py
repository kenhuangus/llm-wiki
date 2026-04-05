"""
test_llm.py — LLM Connectivity Diagnostics
Tests the multi-node failover system by attempting a 
high-fidelity synthesis call to the Main (Ken-Mac) node first.
"""
import sys
import os

# Add tools/ to path
sys.path.insert(0, os.path.join(os.getcwd(), 'tools'))
from common import call_local_model

def run_test():
    print("\n[DIAGNOSTICS] Starting LLM Connectivity Test...")
    print("------------------------------------------------------------")
    
    system_prompt = "You are a helpful assistant for the LLM Wiki project."
    input_text = "Hello! Please introduce yourself and state your model version if possible."
    
    print(f"INPUT: {input_text}")
    print("------------------------------------------------------------")
    
    response = call_local_model(system_prompt, input_text)
    
    if response:
        print("\n[RESULT] Llm returned output successfully:")
        print("------------------------------------------------------------")
        print(response)
        print("------------------------------------------------------------")
    else:
        print("\n[CRITICAL] All model nodes failed to return a response.")

if __name__ == "__main__":
    run_test()
