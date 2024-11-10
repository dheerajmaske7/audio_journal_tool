from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "bigcode/starcoder2-15b"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
