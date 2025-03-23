import os
import io
import streamlit as st
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import asyncio
from streamlit.runtime.scriptrunner import add_script_run_ctx
import nest_asyncio

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("MONGO_DB_NAME", "sharebin")
FILE_COLLECTION = os.getenv("MONGO_COLLECTION", "files")
TEXT_COLLECTION = "texts"

async def connect_db():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    return db, client

async def is_keyword_taken(keyword, collection_name):
    db, client = await connect_db()
    collection = db[collection_name]
    exists = await collection.find_one({"keyword": keyword})
    client.close()
    return exists is not None

async def save_file_data(keyword, file_data_list):
    db, client = await connect_db()
    collection = db[FILE_COLLECTION]

    if await is_keyword_taken(keyword, FILE_COLLECTION):
        client.close()
        return False, "Keyword already taken. Choose another."

    document = {
        "keyword": keyword, 
        "files": file_data_list
    }
    await collection.insert_one(document)
    client.close()
    return True, "Files saved successfully."

async def save_text_data(keyword, text_content):
    db, client = await connect_db()
    collection = db[TEXT_COLLECTION]

    if await is_keyword_taken(keyword, TEXT_COLLECTION):
        client.close()
        return False, "Keyword already taken. Choose another."

    document = {"keyword": keyword, "content": text_content}
    await collection.insert_one(document)
    client.close()
    return True, "Text saved successfully."

async def get_files(keyword):
    db, client = await connect_db()
    collection = db[FILE_COLLECTION]
    result = await collection.find_one({"keyword": keyword})
    client.close()
    return result if result else None

async def get_text_content(keyword):
    db, client = await connect_db()
    collection = db[TEXT_COLLECTION]
    result = await collection.find_one({"keyword": keyword})
    client.close()
    return result["content"] if result else None

# Helper function to run async functions in Streamlit
def run_async(func, *args, **kwargs):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task = loop.create_task(func(*args, **kwargs))
    add_script_run_ctx(task)  # Add Streamlit script context
    return loop.run_until_complete(task)

def main():
    st.title("📂 ShareBin - File & Text Sharing")

    tab1, tab2, tab3 = st.tabs(["Share Files", "Share Text", "Access"])

    with tab1:
        st.header("📄 Upload Files")
        keyword = st.text_input("Enter Access Keyword", key="file_keyword")
        uploaded_files = st.file_uploader("Upload Your Files", accept_multiple_files=True)

        if uploaded_files and keyword:
            file_data_list = []
            
            for uploaded_file in uploaded_files:
                file_buffer = io.BytesIO(uploaded_file.getbuffer())
                file_data = {
                    "filename": uploaded_file.name,
                    "file_data": file_buffer.getvalue()
                }
                file_data_list.append(file_data)
            
            if file_data_list:
                if st.button("Save Files"):
                    with st.spinner("Uploading... Please wait!"):
                        success, message = run_async(save_file_data, keyword, file_data_list)
                    
                    if success:
                        st.success(f"✅ {len(file_data_list)} files saved! Use this keyword to access: `{keyword}`")
                    else:
                        st.error(f"❌ {message}")

    with tab2:
        st.header("📝 Share Text")
        keyword = st.text_input("Enter Access Keyword", key="text_keyword")
        text_content = st.text_area("Enter your text here:", height=300)

        if st.button("Save Text"):
            if keyword and text_content.strip():
                with st.spinner("Saving text... Please wait!"):
                    success, message = run_async(save_text_data, keyword, text_content)

                if success:
                    st.success(f"✅ Text saved! Use this keyword to access: `{keyword}`")
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("Please enter both keyword and text before saving.")

    with tab3:
        st.header("🔑 Access Shared Content")
        keyword = st.text_input("Enter Access Keyword", key="search_keyword")

        if keyword and st.button("Access Content"):
            st.info(f"Looking up content for keyword: `{keyword}`")

            with st.spinner("Fetching content... Please wait!"):
                files_result = run_async(get_files, keyword)

            if files_result:
                st.success(f"✅ Found {len(files_result['files'])} files!")
                
                for i, file_data in enumerate(files_result['files']):
                    st.download_button(
                        label=f"📥 Download {file_data['filename']}",
                        data=file_data['file_data'],
                        file_name=file_data['filename'],
                        key=f"download_{i}"
                    )
            else:
                text_content = run_async(get_text_content, keyword)
                if text_content:
                    st.success("✅ Text content found!")
                    st.text_area("Shared Text:", value=text_content, height=300)
                else:
                    st.error("❌ Invalid Keyword! No content found.")

if __name__ == "__main__":
    main()