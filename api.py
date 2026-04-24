"""
ChemGist API Server - Connects the fine-tuned model to the frontend
Optimized version with better error handling and memory management
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import getpass
import requests
import os
import logging
from datetime import datetime
import warnings
from huggingface_hub import HfApi

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

# Global Inference API settings
HF_API_TOKEN = os.environ.get("HUGGINGFACE_API_TOKEN") or os.environ.get("HF_API_TOKEN")
HF_MODEL_NAME = os.environ.get("CHEMGIST_MODEL_NAME", "JAZL/ChemGist-Phi3")
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL_NAME}"
HF_PIPELINE_URL = f"https://api-inference.huggingface.co/pipeline/text-generation?model={HF_MODEL_NAME}"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"} if HF_API_TOKEN else {}
model_loaded = False
inference_url = None


def prompt_for_api_token(prompt_message: str = None) -> bool:
    """Prompt the user for a Hugging Face API token in the terminal."""
    global HF_API_TOKEN, headers
    if prompt_message is None:
        prompt_message = "Hugging Face API token not configured. Enter token or press Enter to cancel: "

    try:
        token = getpass.getpass(prompt_message)
    except Exception as e:
        logger.error(f"Unable to read token from terminal: {type(e).__name__}: {e}")
        return False

    if not token:
        logger.error("No token entered. Server startup canceled.")
        return False

    HF_API_TOKEN = token.strip()
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    return True


def validate_hf_token() -> bool:
    """Validate the provided Hugging Face token."""
    if not HF_API_TOKEN:
        return False
    try:
        api = HfApi()
        profile = api.whoami(token=HF_API_TOKEN)
        logger.info(f"✓ Hugging Face token is valid for user: {profile.get('name', profile.get('username', 'unknown'))}")
        return True
    except Exception as e:
        logger.error(f"Unable to validate Hugging Face token: {type(e).__name__}: {e}")
    return False


def verify_model_access() -> bool:
    """Verify that the model exists and is accessible with this token."""
    try:
        api = HfApi()
        model_info = api.model_info(HF_MODEL_NAME, token=HF_API_TOKEN)
        if model_info.private:
            logger.info(f"Model '{HF_MODEL_NAME}' is private. Token must have read access.")
        else:
            logger.info(f"Model '{HF_MODEL_NAME}' is public.")

        pipeline_tags = getattr(model_info, 'pipeline_tag', None)
        tags = getattr(model_info, 'tags', []) or []
        if pipeline_tags:
            logger.info(f"Model pipeline tag: {pipeline_tags}")
        if tags:
            logger.info(f"Model tags: {tags}")

        if 'text-generation' not in tags and 'text-generation-inference' not in tags and pipeline_tags != 'text-generation':
            logger.warning("This model does not show a text-generation pipeline tag, so it may not be directly available through the Inference API.")

        return True
    except Exception as e:
        logger.error(f"Unable to access model '{HF_MODEL_NAME}': {type(e).__name__}: {e}")
    return False


def verify_inference_api() -> bool:
    """Verify that the Hugging Face Inference API is reachable and the model is available."""
    global inference_url
    try:
        logger.info(f"Verifying Hugging Face Inference API for model: {HF_MODEL_NAME}")
        
        # The standard inference URL is the only one we need to check
        url = HF_API_URL 
        
        # We MUST send a POST request, not a GET request. 
        # Sending a tiny dummy payload to wake up the model.
        payload = {"inputs": "Test", "parameters": {"max_new_tokens": 1}}
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        status = response.status_code
        
        if status == 200:
            inference_url = url
            logger.info(f"✓ Inference endpoint available and model is ready: {url}")
            return True
        elif status == 503:
            # 503 means the server is waking up and loading your model into memory.
            # This is completely normal for the free tier!
            inference_url = url
            logger.info(f"✓ Inference endpoint available (Model is currently loading into memory): {url}")
            return True
        elif status == 401:
            logger.error(f"✗ 401 Unauthorized. Your HF token lacks 'Make calls to the serverless Inference API' permissions.")
            return False
        elif status == 404:
            logger.error(f"✗ 404 Not Found. The model may still be indexing, or is too large for the free serverless tier.")
            return False
        elif status == 429:
            logger.error(f"✗ 429 Too Many Requests. You have hit the rate limit for the free tier.")
            return False
        else:
            logger.warning(f"Endpoint {url} returned {status}: {response.text}")

    except requests.exceptions.Timeout:
        logger.warning(f"Timeout while verifying endpoint. The model might be taking a long time to load.")
        # We can still optimistically set the URL and let the user wait on their first chat
        inference_url = HF_API_URL
        return True
    except Exception as e:
        logger.error(f"✗ Error verifying inference API: {type(e).__name__}: {str(e)}")
    
    return False


def load_model_and_tokenizer():
    """Initialize remote inference API configuration."""
    global model_loaded
    logger.info("Starting Hugging Face Inference API setup...")
    
    if not HF_API_TOKEN:
        if not prompt_for_api_token():
            return False
    
    for attempt in range(2):
        if not HF_API_TOKEN:
            logger.error("No Hugging Face API token configured. Startup canceled.")
            return False

        if not validate_hf_token():
            if attempt == 0:
                logger.error("Provided Hugging Face API token is invalid.")
                if not prompt_for_api_token("Enter a valid Hugging Face API token or press Enter to cancel: "):
                    return False
                continue
            return False

        if not verify_model_access():
            logger.error("Unable to access the Hugging Face model with the provided token.")
            if attempt == 0:
                if not prompt_for_api_token("Enter a Hugging Face API token with model read access or press Enter to cancel: "):
                    return False
                continue
            return False

        if verify_inference_api():
            model_loaded = True
            return True

        if attempt == 0:
            logger.error("Failed to verify the Hugging Face inference endpoint.")
            if not prompt_for_api_token("Enter a new Hugging Face API token or press Enter to cancel: "):
                return False
        else:
            break

    logger.error("Failed to verify the Hugging Face inference model. Server will not start.")
    return False

def generate_answer(question: str) -> str:
    """Generate an answer using the Hugging Face Inference API."""
    
    if not model_loaded or not inference_url:
        return "Error: Remote model not ready. Please restart the server and check the logs."
    
    prompt = (
        "<|user|>\n"
        "You are ChemGist, an intelligent and conversational chemistry assistant. Answer the user's question accurately based on your training.\n\n"
        "Answer the user's question by weaving the following facts into a natural, flowing paragraph. "
        "CRITICAL: Do NOT use colons. Do NOT use bullet points. Do NOT output a list. "
        "Write in complete sentences as if explaining it to a friend.\n\n"
        f"Question: {question}<|end|>\n"
        "<|assistant|>\n"
    )
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 512,
            "temperature": 0.3,
            "top_p": 0.9,
            "repetition_penalty": 1.1,
            "do_sample": True,
            "return_full_text": False
        },
        "options": {
            "use_cache": True,
            "wait_for_model": True
        }
    }
    
    try:
        logger.info(f"Sending request to Hugging Face Inference API endpoint: {inference_url}")
        response = requests.post(inference_url, headers=headers, json=payload, timeout=120)
        
        if response.status_code != 200:
            logger.error(f"Inference API error: {response.status_code} {response.text}")
            return f"Error: Inference API failure ({response.status_code})."
        
        data = response.json()
        
        if isinstance(data, dict) and data.get("error"):
            logger.error(f"Inference API reported error: {data['error']}")
            return f"Error: {data['error']}"
        
        if isinstance(data, list):
            answer = data[0].get("generated_text") if isinstance(data[0], dict) else data[0]
        elif isinstance(data, dict):
            answer = data.get("generated_text") or data.get("text") or str(data)
        else:
            answer = str(data)
        
        answer = answer.strip()
        logger.info(f"✓ Answer received successfully ({len(answer)} chars)")
        return answer
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {type(e).__name__}: {str(e)}")
        return f"Error: Unable to contact Hugging Face Inference API. {str(e)}"
    except Exception as e:
        logger.error(f"Unexpected error generating answer: {type(e).__name__}: {str(e)}")
        return f"Error generating response: {str(e)}"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy" if model_loaded else "loading",
        "model_loaded": model_loaded,
        "model": HF_MODEL_NAME,
        "token_provided": bool(HF_API_TOKEN),
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
