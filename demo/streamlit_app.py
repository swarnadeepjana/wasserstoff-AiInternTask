import streamlit as st
import requests
import os
import pandas as pd
import json
import streamlit.components.v1 as components


# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="📚 Document Research Chatbot", layout="wide")
st.title("📄 Document Research & Theme Chatbot")
st.markdown("<base target='_blank'>", unsafe_allow_html=True)

# File Upload
st.subheader("1. Upload Your Documents (PDF, Image, Text)")
uploaded_files = st.file_uploader(
    "Upload multiple files", type=["pdf", "png", "jpg", "jpeg", "txt"], accept_multiple_files=True
)

author = st.text_input("Author Name")
doc_type = st.selectbox("Document Type", ["Report", "Thesis", "Note", "Uncategorized"])



if st.button("Upload Files"):
    if uploaded_files:
        # ✅ Add unique keys to avoid StreamlitDuplicateElementId
        author = st.text_input("Author Name", key="upload_author_input")
        doc_type = st.selectbox(
            "Document Type",
            ["Report", "Thesis", "Note", "Uncategorized"],
            key="upload_doc_type_select"
        )

        # 📦 Prepare files and metadata
        files = [("files", (file.name, file, file.type)) for file in uploaded_files]
        data = {
            "author": author,
            "doc_type": doc_type
        }

        # 📤 Make POST request to backend
        response = requests.post(f"{BACKEND_URL}/upload", files=files, data=data)

        if response.status_code == 200:
            st.success("✅ All files uploaded successfully.")
        else:
            st.error(f"❌ Failed to upload files. Status code: {response.status_code}")
            try:
                st.json(response.json())
            except:
                st.write(response.text)
    else:
        st.warning("⚠️ Please upload at least one document.")

        
        
        

# Ask a Question
st.subheader("2. Ask a Question About Your Documents")
user_query = st.text_input("Enter your question")

if st.button("Submit Question"):
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("⏳ Searching and analyzing documents..."):
            try:
                res = requests.post(f"{BACKEND_URL}/query", json={"query": user_query})
                if res.status_code == 200:
                    data = res.json()

                    st.markdown("### 📄 Document-Level Answers")
                    if data["answers"]:
                        for ans in data["answers"]:
                            doc_id = ans["doc_id"]
                            page = ans.get("page", "N/A")
                            chunk = ans.get("chunk_index", "N/A")
                            text = ans["text"]

                            # Generate clickable ID
                            st.markdown(f"""
                            **Document**: [{doc_id} - Page {page}, Chunk {chunk}](#{doc_id}_{page}_{chunk})  
                            **Text**: {text}  
                            ---  
                            """)
                    else:
                        st.info("No document-level answers found.")

                    st.subheader("🧠 Synthesized Theme Summary")
                    st.markdown(data.get("theme_summary", "No theme summary available."))

                else:
                    st.error("⚠️ Error while querying documents. Check backend logs.")
            except Exception as e:
                st.error(f"❌ Exception: {e}")





# --- Show tabular results (document-level answers) ---
if 'data' in locals() and data.get("answers"):
    # Add clickable citation links in DataFrame
    for answer in data["answers"]:
        doc_id = answer["doc_id"]
        page = answer.get("page", "N/A")
        para = answer.get("chunk_index", "N/A")
        link = f"[{doc_id}](#{doc_id.lower()}) (Page {page}, Para {para})"
        answer["Citation"] = link

    df = pd.DataFrame(data["answers"])
    df = df.rename(columns={
        "doc_id": "📄 Document ID",
        "text": "📄 Answer Snippet",
        "page": "📌 Page",
        "chunk_index": "📌 Paragraph",
        "Citation": "🔗 Citation"
    })

    st.dataframe(df, use_container_width=True)
else:
    st.info("No document-level answers found.")


# --- Optional: Show clickable chat-style results ---
# Optional: Chat-style per-document answer summary
if 'data' in locals() and data.get("answers"):
    st.markdown("### 💬 Synthesized Answers")
    for doc in data["answers"]:
        doc_id = doc["doc_id"]
        page = doc.get("page", "N/A")
        para = doc.get("chunk_index", "N/A")
        answer = doc.get("text", "")
        filename = doc.get("filename", "")
        
        st.markdown(f"""
    🔖 **{doc_id}** – Page {page}, Paragraph {para}  
    📝 **Answer**: {doc["text"]}
    """)
    
    if filename:
        pdf_url = f"http://localhost:8000/pdfs/{filename}#page={page}"
        components.html(f"""
            <iframe src="{pdf_url}" width="100%" height="600px" style="border:1px solid gray;"></iframe>
        """, height=620) 











#view uploaded documents

st.subheader("3. View Uploaded Documents")

# Path to folder that holds both documents and their metadata
doc_dir = "backend/data/embeddings"
metadata_path = "backend/data/embeddings/metadata.json"  # Fixed typo in "backend"

try:
    with open(metadata_path, "r") as f:
        metadata = json.load(f)

    if not metadata:
        st.info("No documents uploaded yet.")
    else:
        # --- Filters ---
        all_authors = sorted(set(info["author"] for info in metadata if "author" in info))
        selected_author = st.selectbox("Filter by Author", ["All"] + all_authors)

        all_types = sorted(set(info["type"] for info in metadata if "type" in info))
        selected_type = st.selectbox("Filter by Type", ["All"] + all_types)

        # --- Filter Logic ---
        filtered_docs = [
            info for info in metadata
            if (selected_author == "All" or info.get("author") == selected_author)
            and (selected_type == "All" or info.get("type") == selected_type)
        ]

        # --- Include/Exclude Selection ---
        selected_filenames = st.multiselect(
            "📌 Select Documents to Include in Search",
            [info["filename"] for info in filtered_docs],
            default=[info["filename"] for info in filtered_docs]
        )

        # --- Show Document Metadata ---
        for info in filtered_docs:
            if info["filename"] in selected_filenames:
                page = info.get("page", 0)
                para = info.get("chunk_index", 0)
                anchor_id = info["doc_id"].lower()
                st.markdown(f"<a name='{anchor_id}'></a>", unsafe_allow_html=True)
                st.markdown(f"""
                ---
                🔖 **{info.get('doc_id', 'N/A')}**
                - 📄 Filename: `{info['filename']}`
                - 🧑 Title and Author: **{info.get('author', 'Unknown')}**
                - 📅 Date: {info.get('date', 'Unknown')}
                - 🗂️ Type: {info.get('type', 'Unknown')}
                - 📊 Relevance Score: {info.get('relevance_score', 'N/A')}
                """)

        # 💡 Save selected filenames for future use
        st.session_state["selected_docs"] = selected_filenames

except FileNotFoundError:
    st.warning("Metadata file not found. Please upload documents first.")
except Exception as e:
    st.error(f"Failed to load document metadata: {e}")

                

    
    
    
    
    
