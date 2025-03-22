import os
import streamlit as st
import uuid
import mysql.connector

DB_HOST = "localhost"
DB_USER = "fileUser"
DB_PASSWORD = "share_user"
DB_NAME = "sharebin"



def connect_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def save_data(id, path):
    db=connect_db()
    cursor=db.cursor()
    query="INSERT INTO files (code, file_path) VALUES (%s, %s)"
    cursor.execute(query,(id,path))
    db.commit()
    cursor.close()
    db.close()
    
    
def download_file(code):
    db = connect_db()
    cursor = db.cursor()
    query = "SELECT file_path FROM files WHERE code = %s"
    cursor.execute(query, (code,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result[0] if result else None


def main():
    
    st.title("📂 File Upload & Download")

    uploaded = st.file_uploader("UPLOAD HERE :)")    
    
    if uploaded:
    
        uID = uuid.uuid4().hex[:8] 
        filepath = os.path.join(f"{os.getcwd()}/files", f"{uID}_{uploaded.name}")

        with open(filepath, 'wb') as f:
            f.write(uploaded.getbuffer())

        save_data(uID,filepath)
        st.success(f"✅ Your unique code: `{uID}` (Use this to download your file)")

    st.header("🔑 Enter Code to Download File")
    textIn = st.text_input("Unique Code")
    
    if textIn:
        st.info(f"The entered unique code is: `{textIn}`") 
        file_path = download_file(textIn)

        if file_path:
            with open(file_path, "rb") as file:
                st.download_button(label="📥 Download File",
                                   data=file,
                                   file_name=os.path.basename(file_path))
        else:   
            st.error("❌ Invalid Code! No file found.")


if __name__ == "__main__":
    main()
