from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class LocalMind:
    def __init__(self, model_name="Qwen/Qwen2.5-Coder-0.5B-Instruct"):
        print(f"[LocalMind] Loading Reasoning Core ({model_name})... this may take a moment.")
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype="auto", device_map="auto")
            print("[LocalMind] Cortex Online.")
            self.active = True
        except Exception as e:
            print(f"[LocalMind] Warning: Could not load LLM ({e}). Falling back to template mode.")
            self.active = False

    def generate_code(self, prompt_context):
        """
        Generates Python code based on a prompt.
        """
        if not self.active:
            return None

        system_prompt = "You are an autonomous AI architect. Write a valid, self-contained Python script to solve the user's problem. Do not explain. Just write code."
        user_prompt = f"Context: {prompt_context}\nTask: Write a python plugin that performs a useful action related to this context."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )
        model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        generated_ids = self.model.generate(
            **model_inputs,
            max_new_tokens=256,
            temperature=0.7
        )
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]

        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        return self._clean_code(response)

    def _clean_code(self, text):
        # Extract code block if markdown is used
        if "```python" in text:
            text = text.split("```python")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return text.strip()

if __name__ == "__main__":
    mind = LocalMind()
    if mind.active:
        print(mind.generate_code("I found a CSV file with financial data."))
