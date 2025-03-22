import os
import io
import streamlit as st
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

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
    return exists is not None

async def save_file_data(keyword, file_buffer, filename):
    db, client = await connect_db()
    collection = db[FILE_COLLECTION]

    if await is_keyword_taken(keyword, FILE_COLLECTION):
        return False, "Keyword already taken. Choose another."

    document = {"keyword": keyword, "filename": filename, "file_data": file_buffer.getvalue()}
    await collection.insert_one(document)
    return True, "File saved successfully."

async def save_text_data(keyword, text_content):
    db, client = await connect_db()
    collection = db[TEXT_COLLECTION]

    if await is_keyword_taken(keyword, TEXT_COLLECTION):
        return False, "Keyword already taken. Choose another."

    document = {"keyword": keyword, "content": text_content}
    await collection.insert_one(document)
    return True, "Text saved successfully."

async def get_file(keyword):
    db, client = await connect_db()
    collection = db[FILE_COLLECTION]
    result = await collection.find_one({"keyword": keyword})
    return result if result else None

async def get_text_content(keyword):
    db, client = await connect_db()
    collection = db[TEXT_COLLECTION]
    result = await collection.find_one({"keyword": keyword})
    return result["content"] if result else None

def main():
    st.title("📂 ShareBin - File & Text Sharing")

    tab1, tab2, tab3 = st.tabs(["Share Files", "Share Text", "Access"])

    with tab1:
        st.header("📄 Upload a File")
        keyword = st.text_input("Enter Access Keyword", key="file_keyword")
        uploaded = st.file_uploader("Upload Your File")

        if uploaded and keyword:
            file_buffer = io.BytesIO(uploaded.getbuffer())

            with st.spinner("Uploading... Please wait!"):
                success, message = st.session_state.loop.run_until_complete(
                    save_file_data(keyword, file_buffer, uploaded.name)
                )
            
            if success:
                st.success(f"✅ File saved! Use this keyword to access: `{keyword}`")
            else:
                st.error(f"❌ {message}")

    with tab2:
        st.header("📝 Share Text")
        keyword = st.text_input("Enter Access Keyword", key="text_keyword")
        text_content = st.text_area("Enter your text here:", height=300)

        if st.button("Save Text"):
            if keyword and text_content.strip():
                with st.spinner("Saving text... Please wait!"):
                    success, message = st.session_state.loop.run_until_complete(
                        save_text_data(keyword, text_content)
                    )

                if success:
                    st.success(f"✅ Text saved! Use this keyword to access: `{keyword}`")
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("Please enter both keyword and text before saving.")

    with tab3:
        st.header("🔑 Access Shared Content")
        keyword = st.text_input("Enter Access Keyword", key="search_keyword")

        if keyword:
            st.info(f"Looking up content for keyword: `{keyword}`")

            with st.spinner("Fetching content... Please wait!"):
                file_result = st.session_state.loop.run_until_complete(get_file(keyword))

            if file_result:
                st.success("✅ File found!")
                st.download_button(label="📥 Download File",
                                   data=file_result["file_data"],
                                   file_name=file_result["filename"])
            else:
                text_content = st.session_state.loop.run_until_complete(get_text_content(keyword))
                if text_content:
                    st.success("✅ Text content found!")
                    st.text_area("Shared Text:", value=text_content, height=300)
                else:
                    st.error("❌ Invalid Keyword! No content found.")

if __name__ == "__main__":
    if "loop" not in st.session_state:
        import asyncio
        st.session_state.loop = asyncio.new_event_loop()
    main()
