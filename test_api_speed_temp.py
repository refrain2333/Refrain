"""
API速度测试脚本 - 测试Claude三个模型的首字速度和token/s
生命周期: 临时测试文件，测试完成后可删除
"""

import requests
import time
import json

API_KEY = "sk-49fb2836bf9d58d5fa2a3dd6394a580daab8b4e38555582c"
BASE_URL = "http://43.160.243.8:8000"

MODELS = [
    "claude-sonnet-4-20250514",
    "claude-sonnet-4-5-20250929",
    "claude-opus-4-5-20251101",
    "claude-haiku-4-5",
    "claude-haiku-4-5-20251001"
]

TEST_PROMPT = "Please write a short paragraph about artificial intelligence."


def test_model_speed(model_name):
    """测试单个模型的速度"""
    print(f"\n{'='*60}")
    print(f"Testing model: {model_name}")
    print('='*60)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": TEST_PROMPT}
        ],
        "stream": True,
        "max_tokens": 500
    }

    try:
        start_time = time.time()
        first_token_time = None
        total_tokens = 0
        full_response = ""

        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            headers=headers,
            json=payload,
            stream=True,
            timeout=120
        )

        if response.status_code != 200:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None

        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        if "choices" in data and len(data["choices"]) > 0:
                            delta = data["choices"][0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                if first_token_time is None:
                                    first_token_time = time.time()
                                total_tokens += 1
                                full_response += content
                    except json.JSONDecodeError:
                        pass

        end_time = time.time()

        if first_token_time is None:
            print("No tokens received")
            return None

        ttft = first_token_time - start_time
        total_time = end_time - start_time
        generation_time = end_time - first_token_time
        tokens_per_second = total_tokens / generation_time if generation_time > 0 else 0

        results = {
            "model": model_name,
            "ttft": ttft,
            "total_tokens": total_tokens,
            "total_time": total_time,
            "generation_time": generation_time,
            "tokens_per_second": tokens_per_second
        }

        print(f"TTFT (首字时间): {ttft:.3f}s")
        print(f"Total tokens: {total_tokens}")
        print(f"Generation time: {generation_time:.3f}s")
        print(f"Token/s: {tokens_per_second:.2f}")
        print(f"Total time: {total_time:.3f}s")
        print(f"\nResponse preview: {full_response[:100]}...")

        return results

    except requests.exceptions.Timeout:
        print("Request timeout")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    print("="*60)
    print("Claude API Speed Test")
    print(f"URL: {BASE_URL}")
    print("="*60)

    all_results = []

    for model in MODELS:
        result = test_model_speed(model)
        if result:
            all_results.append(result)
        time.sleep(1)

    if all_results:
        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        print(f"{'Model':<35} {'TTFT(s)':<10} {'Token/s':<10}")
        print("-"*60)
        for r in all_results:
            model_short = r['model'][:33] if len(r['model']) > 33 else r['model']
            print(f"{model_short:<35} {r['ttft']:<10.3f} {r['tokens_per_second']:<10.2f}")


if __name__ == "__main__":
    main()
