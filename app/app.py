import gradio as gr
import os
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# 1. Securely fetch token
hf_token = os.environ.get("HF_TOKEN")

repo_id = "JAZL/ChemGist-Phi3-Q4_K_M-GGUF" 
filename = "chemgist-phi3-q4_k_m.gguf" 

print(f"⏳ Downloading {filename} from {repo_id}...")
# This downloads the file to the container's local storage
model_path = hf_hub_download(
    repo_id=repo_id, 
    filename=filename, 
    token=hf_token
)

print("🧠 Loading model into llama.cpp engine...")
# 2. Initialize llama.cpp
llm = Llama(
    model_path=model_path,
    n_ctx=4096,       # Context window
    n_threads=2,      # Perfectly matches the Hugging Face Free Tier CPU limits
    verbose=False     # Hides C++ log spam
)
print("✅ Model loaded and ready!")

def generate_answer(message: str) -> str:
    # 3. Dynamic Prompting Strategy
    # We use explicit negative constraints to stop database hallucinations natively.
    prompt = (
        "<|user|>\n"
        "You are ChemGist, an intelligent, warm, and conversational chemistry assistant trained exclusively on the ChemGist-CHON dataset. "
        "Explain chemical concepts accurately, clearly, and naturally.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "- FOCUS: Concentrate STRICTLY on chemical definitions, physical/chemical properties, molecular structures, and real-world applications.\n"
        "- DATABASE GUARDS: Do NOT mention 'Unnamed Compound', 'ChEMBL', 'PubChem', 'database listings', 'clinical phases', 'assays', or 'target organisms'.\n"
        "- IDENTIFIER GUARDS: Do NOT output raw chemical identifiers like SMILES strings, InChI keys, or CIDs unless explicitly asked.\n"
        "- TONE GUARDS: Do NOT use robotic boilerplate phrases like 'This compound is listed as...' or 'Information is not available.'\n"
        "- FORMATTING: Do NOT use colons, bullet points, numbered lists, or line breaks. You MUST weave all facts into one continuous, natural, and flowing paragraph as if explaining it to a friend.\n\n"
        f"Question: {message}<|end|>\n"
        "<|assistant|>\n"
    )
    
    # 4. Generate the response using llama.cpp
    output = llm(
        prompt,
        max_tokens=512,
        temperature=0.3,
        top_p=0.9,
        repeat_penalty=1.1,
        stop=["<|end|>", "<|user|>"], 
        echo=False 
    )
    
    # Extract the text
    answer = output['choices'][0]['text'].strip()
    
    # 5. Dynamic Sentence Trimming (Post-Processing)
    # If the response gets cut off and doesn't end with proper punctuation, 
    # we search backwards to find the last complete sentence and slice the string there.
    if answer and answer[-1] not in ['.', '!', '?']:
        last_period = answer.rfind('.')
        last_exclamation = answer.rfind('!')
        last_question = answer.rfind('?')
        
        # Find whichever punctuation mark came last in the text
        last_punct = max(last_period, last_exclamation, last_question)
        
        # If we found punctuation, cut off the broken fragment after it
        if last_punct != -1:
            answer = answer[:last_punct + 1]

    return answer

# Build the Gradio Interface
demo = gr.Interface(
    fn=generate_answer,
    inputs=gr.Textbox(label="User Question", placeholder="Type your chemistry question here..."),
    outputs=gr.Textbox(label="ChemGist Answer"),
    title="ChemGist API Server (⚡ GGUF Speed)",
)

if __name__ == "__main__":
    demo.launch(ssr_mode=False)