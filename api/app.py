import gradio as gr
import os
import re
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

hf_token = os.environ.get("HF_TOKEN")

repo_id = "JAZL/ChemGist-Phi3-Q4_K_M-GGUF" 
filename = "chemgist-phi3-q4_k_m.gguf" 

print(f"⏳ Downloading {filename} from {repo_id}...")
model_path = hf_hub_download(
    repo_id=repo_id, 
    filename=filename, 
    token=hf_token
)

print("🧠 Loading model into llama.cpp engine...")
llm = Llama(
    model_path=model_path,
    n_ctx=4096,       
    n_threads=2,      
    verbose=False     
)
print("✅ Model loaded and ready!")

def generate_answer(message: str) -> str:
    prompt = (
        "<|user|>\n"
        "You are ChemGist, an intelligent and conversational chemistry expert trained exclusively on the ChemGist-CHON dataset. "
        "Your goal is to provide accurate chemical information with a natural, professional warmth.\n\n"
        "CRITICAL INSTRUCTIONS:\n"
        "- FOCUS & DATASET: Answer ONLY using facts from your chemistry training. Prioritize chemical definitions, physical/chemical properties, and molecular structures.\n"
        "- BOUNDARIES: Do NOT invent historical trivia (names/dates), unverified medical claims, or background filler. If the core facts are brief, keep your answer brief.\n"
        "- FORMATTING: Use complete sentences and weave facts into one continuous, natural paragraph. Do NOT use colons, bullet points, numbered lists, or robotic boilerplate language.\n\n"
        f"Question: {message}<|end|>\n"
        "<|assistant|>\n"
    )
    
    output = llm(
        prompt,
        max_tokens=1024, 
        temperature=0.1,
        top_p=0.9,
        repeat_penalty=1.15,
        stop=["<|end|>", "<|user|>"], 
        echo=False 
    )
    
    answer = output['choices'][0]['text'].strip()
    
    # Erase ANY sentence that contains the word ChEMBL, regardless of the chemical name or phase.
    # Regex explanation: (?i) ignores case. [^.]* matches anything that isn't a period.
    answer = re.sub(r'(?i)[^.]*listed in the ChEMBL database[^.]*\.', '', answer)
    answer = re.sub(r'(?i)[^.]*clinical trial phase[^.]*\.', '', answer)
    
    # Erase Wikipedia-style bracketed citations like [1], [3], [4], etc.
    answer = re.sub(r'\[\d+\]', '', answer)
    
    # Clean up double spaces left behind by the deleted sentences
    answer = re.sub(r'\s{2,}', ' ', answer).strip()
    
    # Dynamic Sentence Trimming (If it runs out of tokens) ---
    if answer and answer[-1] not in ['.', '!', '?']:
        last_punct = max(answer.rfind('.'), answer.rfind('!'), answer.rfind('?'))
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