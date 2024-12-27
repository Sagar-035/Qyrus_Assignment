import streamlit as st
import pandas as pd
import json
import io
import sys
import os
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from groq import Groq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()



# Function to read CSV file and output structured data
def read_csv(file_path, head_rows=5):
    try:
        # Read CSV into a pandas DataFrame
        df = pd.read_csv(file_path, nrows=head_rows)
        return df.to_dict(orient='records')  # Returning CSV as a list of dictionaries
    except Exception as e:
        return f"Error reading CSV file: {e}"

# Function to execute generated Python code
def execute_python_code(code: str) -> str:
    try:
        # Create a StringIO object to capture output
        output = io.StringIO()
        # Save the original stdout
        original_stdout = sys.stdout
        # Redirect stdout to the StringIO object
        sys.stdout = output

        # Execute the code with restricted globals
        exec(code, {}, {})

        # Reset stdout to its original value
        sys.stdout = original_stdout

        # Get the captured output
        return output.getvalue()
    except Exception as e:
        # Reset stdout in case of an exception
        sys.stdout = original_stdout
        # Return the traceback of the error
        raise f"Error executing code:\n{str(e)}"

# Function to save uploaded file to a temporary location
def save_uploaded_file(uploaded_file):
    try:
        # Create a temporary directory if it doesn't exist
        temp_dir = os.path.join(os.getcwd(), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Generate a unique filename
        file_path = os.path.join(temp_dir, uploaded_file.name)
        
        # Save the file
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    except Exception as e:
        st.error(f"Error saving file: {e}")
        return None

..................................................
         
# Main Streamlit application
def main():
    st.title("Code Generation and Execution App")
    
    # Sidebar for file upload and user message
    st.sidebar.header("Upload CSV and Provide Instructions")
    uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
    user_message = st.sidebar.text_area("What would you like to do with this CSV?")
    
    # Generate button
    generate_clicked = st.sidebar.button("Generate and Execute Code")
    
    # Main content area
    if uploaded_file is not None:
        # Display CSV preview
        st.subheader("CSV Preview")
        try:
            df = pd.read_csv(uploaded_file)
            st.dataframe(df.head())
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    
    # Code generation and execution
    if generate_clicked and uploaded_file is not None and user_message:
        # Save the uploaded file to a temporary location
        file_path = save_uploaded_file(uploaded_file)
        
        if file_path:
            # Read CSV content
            csv_data = read_csv(file_path)
            
            if isinstance(csv_data, str):
                st.error(f"Error reading CSV: {csv_data}")
            else:
                # Generate code
                st.subheader("Generated Python Code")
                with st.status('Generating code..', state='running'):
                    # Process the request
                    result = generate_python_code(
                        user_message, 
                        csv_data, 
                        file_path  # Pass the full file path
                    )
                    
                    # Display generated code
                st.code(result.code, language='python')
                
                # Display execution output
                st.subheader("Execution Output")
                st.code(result.execution_output)

# Run the app
if __name__ == "__main__":
    main()

#user need to set  their grok api key in .env file
#install all the requirements

         
