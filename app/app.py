import gradio as gr
import torch
import os
from transformers import AutoModelForCausalLM, AutoTokenizer

# Name of your public/private model on Hugging Face
model_id = "JAZL/ChemGist-Phi3"

# Fetch the secret token we just added to the Space settings
hf_token = os.environ.get("HF_TOKEN")

print(f"Loading tokenizer and model for {model_id} on CPU. This will take a few minutes...")

# Pass the token to the tokenizer
tokenizer = AutoTokenizer.from_pretrained(
    model_id, 
    token=hf_token
)

# Pass the token to the model
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="cpu",
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    token=hf_token
)
print("Model loaded successfully into CPU memory!")

def generate_answer(message: str) -> str:
    prompt = (
        "<|user|>\n"
        "You are ChemGist, an intelligent and conversational chemistry assistant. Answer the user's question accurately based on your training.\n\n"
        "Answer the user's question by weaving the following facts into a natural, flowing paragraph. "
        "CRITICAL: Do NOT use colons. Do NOT use bullet points. Do NOT output a list. "
        "Write in complete sentences as if explaining it to a friend.\n\n"
        f"Question: {message}<|end|>\n"
        "<|assistant|>\n"
    )
    
    # Send inputs to CPU
    inputs = tokenizer(prompt, return_tensors="pt").to("cpu")
    
    # Generate the text
    # NOTE: max_new_tokens is set to 200 to prevent CPU timeouts
    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        temperature=0.3,
        top_p=0.9,
        repetition_penalty=1.1,
        do_sample=True
    )
    
    full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Clean up the output to only return the assistant's reply
    if "<|assistant|>" in full_response:
        answer = full_response.split("<|assistant|>")[-1].strip()
    else:
        answer = full_response.strip()
        
    return answer

# Build the Gradio Interface
demo = gr.Interface(
    fn=generate_answer,
    inputs=gr.Textbox(label="User Question", placeholder="Type your chemistry question here..."),
    outputs=gr.Textbox(label="ChemGist Answer"),
    title="ChemGist API Server (CPU Version)",
    description="This Space hosts the ChemGist-Phi3 model on a Free CPU. Please be patient, CPU inference is slow and replies may take 1-3 minutes."
)

if __name__ == "__main__":
    demo.launch()