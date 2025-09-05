import logging
from typing import List
from langchain.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

# ----------------------------
# Configure logging
# ----------------------------
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("services.helpers")


# Extract Data From PDFs
def load_pdf_file(data_path: str) -> List[Document]:
    """
    Load all PDF files from a given directory and return as a list of Documents.
    """
    try:
        loader = DirectoryLoader(
            data_path,
            glob="*.pdf",
            loader_cls=PyPDFLoader
        )
        documents = loader.load()
        logger.info(f"Loaded {len(documents)} PDF documents from {data_path}")
        return documents
    except Exception as e:
        logger.error(f"Error loading PDFs from {data_path}: {e}", exc_info=True)
        return []


# Keep only minimal metadata
def filter_to_minimal_docs(docs: List[Document]) -> List[Document]:
    """
    Given a list of Document objects, return a new list with only:
    - page_content (original text)
    - metadata containing only 'source'
    """
    minimal_docs: List[Document] = []
    for doc in docs:
        src = doc.metadata.get("source", "unknown")
        minimal_docs.append(
            Document(
                page_content=doc.page_content,
                metadata={"source": src}
            )
        )
    logger.info(f"Filtered {len(docs)} docs -> {len(minimal_docs)} minimal docs")
    return minimal_docs


# Split docs into smaller text chunks
def text_split(docs: List[Document],
               chunk_size: int = 500,
               chunk_overlap: int = 20) -> List[Document]:
    """
    Split documents into smaller chunks for embedding/vectorization.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    text_chunks = splitter.split_documents(docs)
    logger.info(f"Split {len(docs)} docs into {len(text_chunks)} chunks "
                f"(chunk_size={chunk_size}, overlap={chunk_overlap})")
    return text_chunks


# HuggingFace Embeddings (384-dim model)
def download_hugging_face_embeddings() -> HuggingFaceEmbeddings:
    """
    Load sentence-transformers/all-MiniLM-L6-v2 embeddings from HuggingFace.
    This model returns vectors of dimension 384.
    """
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        logger.info("Successfully loaded HuggingFace embeddings model (384 dims).")
        return embeddings
    except Exception as e:
        logger.error(f"Error loading embeddings: {e}", exc_info=True)
        raise
