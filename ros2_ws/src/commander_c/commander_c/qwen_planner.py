from transformers import AutoModelForCausalLM, AutoTokenizer
import torch


class QwenMissionPlanner:
    def __init__(self):
        self.model_name = "Qwen/Qwen2.5-0.5B-Instruct"

        print("[QwenPlanner] Loading Qwen model on CPU...")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            dtype=torch.float16,
            device_map="cuda"
        )

        print("[QwenPlanner] Qwen model loaded.")

    def generate_reason(self, robot_id, detected_object, risk_score, x, y, command):
        prompt = (
            f"Robot {robot_id} detected object={detected_object}, "
            f"position=({x}, {y}), risk_score={risk_score}. "
            f"The selected command is {command}. "
            "Explain the reason in one short sentence."
        )

        messages = [
            {
                "role": "system",
                "content": "You are a mission planner for an on-device multi-robot rescue system."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        inputs = self.tokenizer([text], return_tensors="pt")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=50,
                do_sample=False
            )

        result = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )

        return result.strip()
