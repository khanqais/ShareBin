import os
import streamlit as st
import uuid

file_dir = {} 

def download_file(code):
    
    if code in file_dir:
    
        file_path = file_dir.get(code) 
    
        if os.path.exists(file_path):
    
            print("exists")
    
            with open(file_path, 'rb') as f:
                st.download_button(data=f, label="⬇️ Download File", file_name=os.path.basename(file_path), mime="application/octet-stream")
        else:
            st.error("❌ File not found.")
    else:
        st.error("❌ Invalid code.")

def main():
    
    st.title("📂 File Upload & Download")

    uploaded = st.file_uploader("UPLOAD HERE :)")    
    
    if uploaded:
    
        uID = uuid.uuid4().hex[:8] 
        filepath = os.path.join(os.getcwd(), f"{uploaded.name}_{uID}")

        with open(filepath, 'wb') as f:
            f.write(uploaded.getbuffer())

        file_dir[uID] = filepath 
        st.success(f"✅ Your unique code: `{uID}` (Use this to download your file)")

    st.header("🔑 Enter Code to Download File")
    textIn = st.text_input("Unique Code")
    
    if textIn:
        st.info(f"The entered unique code is: `{textIn}`") 
        download_file(textIn) 

if __name__ == "__main__":
    main()
