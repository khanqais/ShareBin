import os
import streamlit as st
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()


MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "sharebin")
COLLECTION_NAME = os.getenv("MONGO_COLLECTION", "files")

print(f"Connecting to: {MONGO_URI}")
print(f"Database name: {DB_NAME}")
print(f"Collection name: {COLLECTION_NAME}")

def connect_db():
    
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db, client

def save_data(id, path):
    try:
        db, client = connect_db()
        collection = db[COLLECTION_NAME]
        document = {"code": id, "file_path": path}
        collection.insert_one(document)
        client.close()
        return True
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return False

def download_file(code):
    try:
        db, client = connect_db()
        collection = db[COLLECTION_NAME]
        result = collection.find_one({"code": code})
        client.close()
        return result["file_path"] if result else None
    except Exception as e:
        st.error(f"Database error: {str(e)}")
        return None

def main():
    
    os.makedirs(f"{os.getcwd()}/files", exist_ok=True)
    
    st.title("📂 File Upload & Download")
    
    
    try:
        db, client = connect_db()
        
        client.close()
    except Exception as e:
        st.error(f"❌ MongoDB Connection Error: {str(e)}")
    
    uploaded = st.file_uploader("UPLOAD HERE :)")
        
    if uploaded:
        uID = uuid.uuid4().hex[:8]
        filepath = os.path.join(f"{os.getcwd()}/files", f"{uID}_{uploaded.name}")
        with open(filepath, 'wb') as f:
            f.write(uploaded.getbuffer())
        
        if save_data(uID, filepath):
            st.success(f"✅ Your unique code: `{uID}` (Use this to download your file)")
        else:
            st.error("Failed to save file information to database.")
    
    st.header("🔑 Enter Code to Download File")
    textIn = st.text_input("Unique Code")
        
    if textIn:
        st.info(f"The entered unique code is: `{textIn}`")
        
        file_path = download_file(textIn)
        
        if file_path:
            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    st.download_button(label="📥 Download File",
                                      data=file,
                                      file_name=os.path.basename(file_path))
            else:
                st.error("❌ File exists in database but not on disk.")
        else:
            st.error("❌ Invalid Code! No file found.")

if __name__ == "__main__":
    main()