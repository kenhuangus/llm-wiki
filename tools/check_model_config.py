"""
Check LLM model configuration and context length.
"""

import requests
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import LLM_MAIN_URL, LLM_MAIN_MODEL


def check_model_info():
    """Check model information and capabilities."""
    print("=" * 80)
    print("  LLM Model Configuration Check")
    print("=" * 80)
    print()
    
    print(f"Server URL: {LLM_MAIN_URL}")
    print(f"Model: {LLM_MAIN_MODEL}")
    print()
    
    # Test 1: Check available models
    print("📋 Available Models:")
    try:
        response = requests.get("http://ken-mac.local:1234/v1/models", timeout=5)
        models = response.json()
        for model in models.get('data', []):
            print(f"   - {model['id']}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 2: Ask about context length
    print("🔍 Testing Context Length:")
    try:
        payload = {
            "model": LLM_MAIN_MODEL,
            "messages": [
                {"role": "user", "content": "What is your maximum context length in tokens? Give me just the number."}
            ],
            "max_tokens": 100,
            "temperature": 0.0
        }
        response = requests.post(
            LLM_MAIN_URL,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        data = response.json()
        
        if "choices" in data:
            answer = data["choices"][0]["message"]["content"]
            print(f"   Model says: {answer}")
            
            # Check usage stats
            if "usage" in data:
                usage = data["usage"]
                print(f"\n   Token Usage:")
                print(f"   - Prompt tokens: {usage.get('prompt_tokens', 'N/A')}")
                print(f"   - Completion tokens: {usage.get('completion_tokens', 'N/A')}")
                print(f"   - Total tokens: {usage.get('total_tokens', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print()
    
    # Test 3: Test with increasing output lengths
    print("📏 Testing Output Length Limits:")
    test_lengths = [500, 1000, 2000, 4000, 8000]
    
    for max_tokens in test_lengths:
        try:
            payload = {
                "model": LLM_MAIN_MODEL,
                "messages": [
                    {"role": "user", "content": f"Write exactly {max_tokens} words about artificial intelligence. Start with 'Artificial intelligence is...'"}
                ],
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            response = requests.post(
                LLM_MAIN_URL,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60
            )
            data = response.json()
            
            if "choices" in data:
                content = data["choices"][0]["message"]["content"]
                actual_tokens = data.get("usage", {}).get("completion_tokens", 0)
                finish_reason = data["choices"][0].get("finish_reason", "unknown")
                word_count = len(content.split())
                
                status = "✅" if finish_reason == "stop" else "⚠️"
                print(f"   {status} max_tokens={max_tokens}: Got {actual_tokens} tokens, {word_count} words, finish_reason={finish_reason}")
            else:
                print(f"   ❌ max_tokens={max_tokens}: Error - {data.get('error', 'Unknown')}")
                
        except Exception as e:
            print(f"   ❌ max_tokens={max_tokens}: Exception - {e}")
    
    print()
    
    # Test 4: Check server configuration (if accessible)
    print("⚙️  Server Configuration:")
    print("   Note: LM Studio configuration is in the UI")
    print("   Check: Settings → Model → Context Length")
    print("   Recommended: 8192 or higher for paper generation")
    print()
    
    # Recommendations
    print("=" * 80)
    print("  Recommendations")
    print("=" * 80)
    print()
    print("1. In LM Studio:")
    print("   - Go to Settings → Model")
    print("   - Set 'Context Length' to 8192 or 16384")
    print("   - Set 'Max Tokens' to 8192 or higher")
    print("   - Reload the model")
    print()
    print("2. For paper generation:")
    print("   - Minimum context: 8192 tokens")
    print("   - Recommended: 16384 tokens")
    print("   - Optimal: 32768 tokens (if model supports)")
    print()
    print("3. Current code settings:")
    print("   - Local model: max_tokens=8192")
    print("   - OpenRouter: max_tokens=16384")
    print()


if __name__ == '__main__':
    check_model_info()
