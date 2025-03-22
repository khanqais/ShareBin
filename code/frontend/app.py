import os
import streamlit as st
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv
import streamlit.components.v1 as components


load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "sharebin")
FILE_COLLECTION = os.getenv("MONGO_COLLECTION", "files")
TEXT_COLLECTION = "texts"  

print(f"Connecting to: {MONGO_URI}")
print(f"Database name: {DB_NAME}")

def connect_db():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db, client

def save_file_data(id, path):
    try:
        db, client = connect_db()
        collection = db[FILE_COLLECTION]
        document = {"code": id, "file_path": path}
        collection.insert_one(document)
        client.close()
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False

def save_text_data(id, text_content):
    try:
        db, client = connect_db()
        collection = db[TEXT_COLLECTION]
        document = {"code": id, "content": text_content}
        collection.insert_one(document)
        client.close()
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False

def get_file_path(code):
    try:
        db, client = connect_db()
        collection = db[FILE_COLLECTION]
        result = collection.find_one({"code": code})
        client.close()
        return result["file_path"] if result else None
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return None

def get_text_content(code):
    try:
        db, client = connect_db()
        collection = db[TEXT_COLLECTION]
        result = collection.find_one({"code": code})
        client.close()
        return result["content"] if result else None
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return None

def display_code_with_clipboard(code):
    # HTML and JavaScript for clipboard functionality - using triple quotes for multiline strings
    clipboard_html = f"""
    <div style="display: flex; align-items: center; margin-bottom: 10px;">
        <code id="codeElement" style="padding: 5px 10px; background-color: #f0f2f6; border-radius: 4px; margin-right: 10px;">{code}</code>
        <button onclick="copyToClipboard()" style="cursor: pointer; border: none; background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 4px;">Copy</button>
    </div>
    <div id="copyMessage" style="color: #4CAF50; margin-top: 5px; display: none;">✓ Copied to clipboard!</div>
    
    <script>
    function copyToClipboard() {{
        var codeText = document.getElementById("codeElement").innerText;
        navigator.clipboard.writeText(codeText).then(function() {{
            var copyMessage = document.getElementById("copyMessage");
            copyMessage.style.display = "block";
            setTimeout(function() {{
                copyMessage.style.display = "none";
            }}, 2000);
        }});
    }}
    
    // Auto-copy to clipboard on load
    window.onload = function() {{
        copyToClipboard();
    }}
    </script>
    """
    components.html(clipboard_html, height=80)

def main():
    
    os.makedirs(f"{os.getcwd()}/files", exist_ok=True)
    
    st.title("📂 ShareBin - File & Text Sharing")
    
    
    try:
        db, client = connect_db()
        
        client.close()
    except Exception as e:
        st.error(f"❌ MongoDB Connection Error: {str(e)}")
    
    
    tab1, tab2, tab3 = st.tabs(["Share Files", "Share Text", "Access"])
    
    
    with tab1:
        st.header("📄 Upload a File")
        uploaded = st.file_uploader("UPLOAD HERE :)")
            
        if uploaded:
            uID = uuid.uuid4().hex[:8]
            filepath = os.path.join(f"{os.getcwd()}/files", f"{uID}_{uploaded.name}")
            with open(filepath, 'wb') as f:
                f.write(uploaded.getbuffer())
            
            if save_file_data(uID, filepath):
                st.success("✅ Your unique code (automatically copied to clipboard):")
                display_code_with_clipboard(uID)
            else:
                st.error("Failed to save file information to database.")
    
    
    with tab2:
        st.header("📝 Share Text")
        
        text_content = st.text_area("Enter your text here:", height=300)
        
        if st.button("Generate Sharing Code"):
            if text_content.strip():
                uID = uuid.uuid4().hex[:8]
                
                if save_text_data(uID, text_content):
                    st.success("✅ Your unique code (automatically copied to clipboard):")
                    display_code_with_clipboard(uID)
                else:
                    st.error("Failed to save text to database.")
            else:
                st.error("Please enter some text before generating a code.")
    
    
    with tab3:
        st.header("🔑 Access Shared Content")
        textIn = st.text_input("Enter Unique Code")
            
        if textIn:
            st.info(f"Looking up content for code: `{textIn}`")
            
            
            file_path = get_file_path(textIn)
            
            if file_path:
                if os.path.exists(file_path):
                    st.success("✅ File found!")
                    with open(file_path, "rb") as file:
                        st.download_button(label="📥 Download File",
                                          data=file,
                                          file_name=os.path.basename(file_path))
                else:
                    st.error("❌ File exists in database but not on disk.")
            else:
                
                text_content = get_text_content(textIn)
                
                if text_content:
                    st.success("✅ Text content found!")
                    st.text_area("Shared Text:", value=text_content, height=300)
                    
                    
                    st.markdown("""
                    <style>
                    .stCodeMirrorEditor {
                        overflow-y: auto !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                else:
                    st.error("❌ Invalid Code! No content found.")

if __name__ == "__main__":
    main()