import os
import logging
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from services.helpers import download_hugging_face_embeddings
from services.prompt import *
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# -------------------- Logging Setup --------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# -------------------- Flask App --------------------
app = Flask(__name__)

# Load API Keys
load_dotenv()
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not PINECONE_API_KEY or not OPENAI_API_KEY:
    logger.error("API keys not found. Check your .env file.")
    raise EnvironmentError("Missing PINECONE_API_KEY or OPENAI_API_KEY")

# Initialize embeddings + Pinecone
try:
    embeddings = download_hugging_face_embeddings()
    index_name = "aariv-medical-chatbot"
    docsearch = PineconeVectorStore.from_existing_index(
        index_name=index_name,
        embedding=embeddings
    )
    retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})
except Exception as e:
    logger.exception("Error initializing Pinecone or embeddings.")
    raise

# LLM Setup
chatModel = ChatOpenAI(model="gpt-4o")
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(chatModel, prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# -------------------- Routes --------------------
@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/get", methods=["POST"])
def chat_form():
    """Legacy HTML form endpoint"""
    try:
        msg = request.form.get("msg", "").strip()
        if not msg:
            logger.warning("Empty form message received.")
            return "Error: empty message", 400

        logger.info(f"User (form): {msg}")
        response = rag_chain.invoke({"input": msg})
        answer = response.get("answer", "Sorry, I could not generate an answer.")
        logger.info(f"Answer: {answer}")
        return str(answer)
    except Exception as e:
        logger.exception("Error handling /get request")
        return "Internal Server Error", 500

@app.route("/api/chat", methods=["POST"])
def chat_api():
    """JSON API endpoint for frontend/React"""
    try:
        data = request.get_json()
        if not data or "message" not in data:
            logger.warning("Invalid JSON payload received.")
            return jsonify({"error": "Missing 'message' in request body"}), 400

        user_msg = data["message"].strip()
        if not user_msg:
            return jsonify({"error": "Message cannot be empty"}), 400

        logger.info(f"User (API): {user_msg}")
        response = rag_chain.invoke({"input": user_msg})
        answer = response.get("answer", "Sorry, I could not generate an answer.")

        logger.info(f"Answer: {answer}")
        return jsonify({"answer": answer})

    except Exception as e:
        logger.exception("Error handling /api/chat request")
        return jsonify({"error": "Internal Server Error"}), 500

# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
