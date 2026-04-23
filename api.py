"""
ChemGist API Server - Connects the fine-tuned model to the frontend
Optimized version with better error handling and memory management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel, AutoPeftModelForCausalLM
import os
import logging
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Global model and tokenizer
model = None
tokenizer = None
device = None
model_loaded = False

def load_model_and_tokenizer():
    """Load the fine-tuned model and tokenizer with optimized settings"""
    global model, tokenizer, device, model_loaded
    
    logger.info("Starting model loading process...")
    
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using device: {device}")
    
    # Get model directory
    model_dir = os.path.join(os.path.dirname(__file__), "model")
    base_model_name = "microsoft/Phi-3-mini-4k-instruct"
    
    try:
        # Step 1: Load tokenizer (with timeout-friendly settings)
        logger.info("Loading tokenizer from local model directory...")
        tokenizer = AutoTokenizer.from_pretrained(
            model_dir,
            trust_remote_code=True,
            use_fast=False  # Use slower but more reliable tokenizer
        )
        logger.info(f"✓ Tokenizer loaded successfully (vocab size: {len(tokenizer)})")
        
        # Step 2: Load base model with memory optimization
        logger.info(f"Loading base model: {base_model_name}")
        
        # Use memory-efficient loading
        model = AutoModelForCausalLM.from_pretrained(
            base_model_name,
            torch_dtype=torch.float16 if device.type == "cuda" else torch.float32,
            device_map="auto" if device.type == "cuda" else None,
            trust_remote_code=True,
            low_cpu_mem_usage=True
        )
        logger.info("✓ Base model loaded successfully")
        
        # Step 3: Load and merge LoRA adapter
        logger.info("Loading LoRA adapter...")
        model = PeftModel.from_pretrained(
            model,
            model_dir,
            is_trainable=False
        )
        logger.info("✓ LoRA adapter loaded")
        
        # Merge adapters into base model
        logger.info("Merging LoRA adapters into base model...")
        model = model.merge_and_unload()
        logger.info("✓ Adapters merged successfully")
        
        # Move to device if needed
        if device.type != "cuda":
            model = model.to(device)
        
        model.eval()
        logger.info("✓✓✓ MODEL FULLY LOADED AND READY ✓✓✓")
        model_loaded = True
        return True
        
    except Exception as e:
        logger.error(f"✗ Error loading model: {type(e).__name__}: {str(e)}")
        logger.error("Make sure:")
        logger.error("1. Base model 'microsoft/Phi-3-mini-4k-instruct' can be downloaded from Hugging Face")
        logger.error("2. You have internet connection for the first load (it will cache afterwards)")
        logger.error("3. Sufficient GPU/RAM available for the model")
        return False

def generate_answer(question: str) -> str:
    """Generate an answer using the fine-tuned model"""
    
    if not model_loaded or model is None or tokenizer is None:
        return "Error: Model not loaded. Please restart the server and check the logs."
    
    try:
        # Prepare the prompt
        prompt = f"Question: {question}\nAnswer:"
        
        logger.info(f"Processing question: {question[:50]}...")
        
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(device)
        
        # Generate response with torch.no_grad for memory efficiency
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=150,
                min_length=10,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                temperature=0.3,
                top_p=0.9,
                top_k=50,
                repetition_penalty=1.2,
                do_sample=True,
                num_beams=1
            )
        
        # Decode the output
        input_length = inputs.input_ids.shape[1]
        generated_tokens = outputs[0][input_length:]
        answer = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        
        logger.info(f"✓ Answer generated successfully ({len(answer)} chars)")
        return answer.strip()
        
    except torch.cuda.OutOfMemoryError:
        logger.error("CUDA out of memory - try reducing max_new_tokens or using CPU")
        return "Error: Out of GPU memory. Please try a shorter question."
    except Exception as e:
        logger.error(f"Error generating answer: {type(e).__name__}: {str(e)}")
        return f"Error generating response: {str(e)}"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy" if model_loaded else "loading",
        "model_loaded": model_loaded,
        "device": str(device),
        "timestamp": datetime.now().isoformat()
    }), 200 if model_loaded else 503

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing 'message' field in request"
            }), 400
        
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({
                "error": "Message cannot be empty"
            }), 400
        
        logger.info(f"Received message: {message}")
        
        # Generate answer using the model
        answer = generate_answer(message)
        
        return jsonify({
            "success": True,
            "message": message,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Serve the frontend"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'frontend.html'), 'r') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error serving frontend: {str(e)}")
        return f"Error loading frontend: {str(e)}", 500

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 Starting ChemGist API Server...")
    logger.info("=" * 60)
    
    # Load model before starting server
    if load_model_and_tokenizer():
        logger.info("✓ Server is ready to receive requests!")
        logger.info("=" * 60)
        logger.info(f"🌐 Access the chatbot at: http://localhost:5000")
        logger.info(f"📊 Health check: http://localhost:5000/health")
        logger.info(f"💬 API endpoint: POST http://localhost:5000/api/chat")
        logger.info("=" * 60)
        app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    else:
        logger.error("=" * 60)
        logger.error("✗✗✗ FAILED TO LOAD MODEL - SERVER CANNOT START ✗✗✗")
        logger.error("=" * 60)
        exit(1)
