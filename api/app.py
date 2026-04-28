import gradio as gr
import os
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

hf_token = os.environ.get("HF_TOKEN")

repo_id = "JAZL/ChemGist-Phi3-Q4_K_M-GGUF" 
filename = "chemgist-phi3-q4_k_m.gguf" 

print(f"Downloading {filename} from {repo_id}...")
model_path = hf_hub_download(
    repo_id=repo_id, 
    filename=filename, 
    token=hf_token,
    force_download=True
)

print("Loading model into llama.cpp engine...")
llm = Llama(
    model_path=model_path,
    n_ctx=4096,        
    n_threads=2,      
    verbose=True     
)
print("Model loaded and ready!")

def generate_answer(message: str):
    system_prompt = (
        "You are ChemGist, a highly intelligent and conversational chemistry AI assistant. "
        "Your job is to provide accurate chemical profiles based strictly on your trained knowledge. "
        "When asked about a chemical, always structure your response naturally and conversationally. "
        "Please answer directly and briefly, and ensure that the answer is based or related on the question only. "
        "IMPORTANT RULES: "
        "1. Never repeat words or stutter. "
        "2. Break down physical and theoretical properties using Markdown bullet points for readability. "
        "3. Do not invent or guess SMILES strings or InChIKeys if you are unsure; provide the best known structure. "
        "4. Provide a clear, natural-sounding description of the chemical's uses and history."
    )

    # Properly format the prompt using Phi-3's strict chat template
    prompt = f"<s><|system|>\n{system_prompt}<|end|>\n<|user|>\n{message}<|end|>\n<|assistant|>\n"
    
    stream = llm(
        prompt,
        max_tokens=1024, 
        temperature=0.05,
        top_p=0.95,
        min_p=0.05,
        repeat_penalty=1.05,
        stop=["<|end|>", "<|user|>", "<s>"], 
        echo=False,
        stream=True
    )
    
    partial_response = ""
    buffer = ""
    
    for chunk in stream:
        # Safely extract the token
        token = chunk['choices'][0].get('text', '')
        
        partial_response += token
        buffer += token
        
        # Buffer the stream to prevent UI freezing
        if len(buffer) > 12 or any(char in buffer for char in [' ', '.', '\n', ',', '-']):
            yield partial_response
            buffer = "" 
            
    # Yield any final remaining characters
    if buffer:
        yield partial_response

# Interface
demo = gr.Interface(
    fn=generate_answer,
    inputs=gr.Textbox(label="User Question", placeholder="Type your chemistry question here... (e.g., Tell me about Ammonia)"),
    outputs=gr.Textbox(label="ChemGist Answer"),
    title="ChemGist API Server",
    description="Ask me about chemical definitions, physical properties, or molecular structures."
)

if __name__ == "__main__":
    demo.launch(ssr_mode=False)