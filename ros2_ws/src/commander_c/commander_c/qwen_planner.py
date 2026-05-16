import os


SYSTEM_PROMPT = "You are a mission planner for an on-device multi-robot rescue system."


def rule_based_reason(robot_id, detected_object, risk_score, x, y, command):
    if risk_score >= 7:
        return (
            f"Robot {robot_id} should {command} because a high-risk "
            f"{detected_object} was detected near ({x:.2f}, {y:.2f})."
        )

    if detected_object == "person":
        return (
            f"Robot {robot_id} should approach the victim candidate at "
            f"({x:.2f}, {y:.2f}) while the other robot keeps exploring."
        )

    if detected_object == "obstacle":
        return (
            f"Robot {robot_id} should update the local map and avoid the "
            f"obstacle near ({x:.2f}, {y:.2f})."
        )

    return (
        f"Robot {robot_id} should continue exploration because no urgent "
        f"rescue or hazard event was detected near ({x:.2f}, {y:.2f})."
    )


class QwenMissionPlanner:
    def __init__(self):
        self.model_name = "Qwen/Qwen2.5-0.5B-Instruct"
        self.enabled = os.getenv("TRI_EDGE_ENABLE_QWEN", "auto").lower()
        self.model = None
        self.tokenizer = None

        if self.enabled in {"0", "false", "no", "off"}:
            print("[QwenPlanner] Qwen disabled. Using deterministic fallback planner.")
            return

        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch

            print("[QwenPlanner] Loading Qwen model on CPU...")

            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
                device_map="cpu"
            )

            print("[QwenPlanner] Qwen model loaded.")
        except Exception as exc:
            print(f"[QwenPlanner] Qwen unavailable: {exc}")
            print("[QwenPlanner] Falling back to deterministic mission reasoning.")
            self.model = None
            self.tokenizer = None

    def generate_reason(self, robot_id, detected_object, risk_score, x, y, command):
        if self.model is None or self.tokenizer is None:
            return rule_based_reason(robot_id, detected_object, risk_score, x, y, command)

        prompt = (
            f"Robot {robot_id} detected object={detected_object}, "
            f"position=({x}, {y}), risk_score={risk_score}. "
            f"The selected command is {command}. "
            "Explain the reason in one short sentence."
        )

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
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
