import os
import streamlit as st
import uuid

def main():
    uploaded=st.file_uploader("UPLOAD HERE :)")    
    
    if uploaded:
        uID=uuid.uuid4().hex[:8]
        
        filepath=os.path.join(os.getcwd(), f"{uploaded.name}_{uID}")
        
        with open(filepath, 'wb') as f:
            f.write(uploaded.getbuffer())
        
        st.code(f"The unique code is: {uID}" , language="Markdown")

    
        
    


if __name__=="__main__":
    main()

