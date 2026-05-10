from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_name = "Qwen/Qwen2.5-0.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    dtype=torch.float32,
    device_map="cpu"
)

messages = [
    {
        "role": "system",
        "content": "You are a mission planner for a multi-robot rescue system."
    },
    {
        "role": "user",
        "content": (
            "Robot A detected a hazard at (-3.5, -3.6) with risk_score 8. "
            "Robot B is clear at (3.5, -3.5). "
            "Return short commands for each robot."
        )
    }
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)

inputs = tokenizer([text], return_tensors="pt")

with torch.no_grad():
    outputs = model.generate(
        **inputs,
        max_new_tokens=60,
        do_sample=False
    )

result = tokenizer.decode(
    outputs[0][inputs.input_ids.shape[1]:],
    skip_special_tokens=True
)

print(result)
