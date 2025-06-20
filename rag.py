import os
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.schema import Document

def build_profile_summary(profile_data):
    return f"""
    Household of {profile_data['household_size']} people.
    Kids: {profile_data['has_kids']}, Elderly: {profile_data['has_elderly']}, Pets: {profile_data['has_pets']}.
    Milk: {profile_data['milk_freq']} ({profile_data['milk_qty']} L/day), 
    Rice: {profile_data['rice_qty']} kg/day, 
    Oil: {profile_data['oil_qty']} L/month.
    Eggs: {profile_data['eggs_per_week']} per week, Bread: {profile_data['bread_freq']}.
    Shops: {profile_data['shopping_freq']} on {profile_data['shopping_day']}, {profile_data['shopping_mode']}, prefers {profile_data['delivery_pref']} delivery.
    """

def store_profile_embedding(user_id: str, summary_text: str):
    """
    Stores or updates a user's profile summary in a LangChain FAISS index.
    - user_id: unique identifier
    - summary_text: full profile summary text
    """
    # Create a Document with summary content and metadata
    doc = Document(page_content=summary_text, metadata={"user_id": user_id})

    embedding_model = OllamaEmbeddings(model="mxbai-embed-large")
    index_dir = "faiss_index"

    # Load or initialize the index
    if os.path.isdir(index_dir) and os.path.exists(os.path.join(index_dir, "index.faiss")):
        faiss_index = FAISS.load_local(index_dir, embedding_model, allow_dangerous_deserialization=True)
        faiss_index.add_documents([doc])
    else:
        faiss_index = FAISS.from_documents([doc], embedding_model)

    # Save the updated index
    faiss_index.save_local(index_dir)

def set_rag_chain():
    embedding_model = OllamaEmbeddings(model="mxbai-embed-large")

    index_dir = "faiss_index"
    index_file = os.path.join(index_dir, "index.faiss")

    # 2. Load your FAISS vector store (created earlier)
    faiss_index = FAISS.load_local("faiss_index", embedding_model, allow_dangerous_deserialization=True)

    # # 3. Create a retriever from FAISS
    retriever = faiss_index.as_retriever()

    # 4. Load Ollama LLM (for example: llama3)
    llm = Ollama(model="tinyllama")

    # 5. Set up a RetrievalQA chain (RAG)
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=False
    )
    return rag_chain