import os
import logging
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from services.helpers import download_hugging_face_embeddings
from services.prompt import *
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from flask_cors import CORS

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
CORS(app)  # allow React frontend to call backend
app.secret_key = os.environ.get("SECRET_KEY", "super-secret-key")  # needed for session

# Load API Keys
load_dotenv()
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not PINECONE_API_KEY or not OPENAI_API_KEY:
    logger.error("API keys not found. Check your .env file.")
    raise EnvironmentError("Missing PINECONE_API_KEY or OPENAI_API_KEY")

# Initialize embeddings + Pinecone
embeddings = download_hugging_face_embeddings()
index_name = "aariv-medical-chatbot"
docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)
retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# LLM Setup
chatModel = ChatOpenAI(model="gpt-4o")

base_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{input}"),
    ]
)

question_answer_chain = create_stuff_documents_chain(chatModel, base_prompt)
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# -------------------- Helpers --------------------
def get_history():
    """Fetch conversation history from session"""
    return session.get("history", [])

def update_history(role, content):
    """Append a message to session history"""
    history = get_history()
    history.append({"role": role, "content": content})
    session["history"] = history[-10:]  # keep only last 10 messages


# -------------------- Routes --------------------
@app.route("/")
def index():
    return "Aariv"


# Dummy user (replace with DB or JWT later)
VALID_USER = {
    "username": "admin",
    "password": "password123"
}

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"message": "Missing username or password"}), 400

    username = data["username"]
    password = data["password"]

    if username == VALID_USER["username"] and password == VALID_USER["password"]:
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@app.route("/api/chat", methods=["POST"])
def chat_api():
    try:
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' in request body"}), 400

        user_msg = data["message"].strip()
        if not user_msg:
            return jsonify({"error": "Message cannot be empty"}), 400

        # Get history and build contextual input
        history = get_history()
        context = "\n".join([f"{m['role']}: {m['content']}" for m in history])
        full_input = f"Conversation so far:\n{context}\n\nUser: {user_msg}"

        logger.info(f"User: {user_msg}")

        # Call RAG chain
        response = rag_chain.invoke({"input": full_input})
        answer = response.get("answer", "Sorry, I could not generate an answer.")

        # Update session history
        update_history("user", user_msg)
        update_history("assistant", answer)

        logger.info(f"Answer: {answer}")
        return jsonify({"answer": answer, "history": get_history()})

    except Exception as e:
        logger.exception("Error handling /api/chat request")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/api/clear", methods=["POST"])
def clear_history():
    """Reset conversation history"""
    session["history"] = []
    return jsonify({"message": "Conversation history cleared."})


# -------------------- Run --------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)
