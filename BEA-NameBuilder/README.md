# BEA NameBuilder

## Overview
BEA NameBuilder is a web application designed to create and generate standardized file names based on user-defined naming conventions. 
It allows users to build a naming convention with metadata (Date, Categorical, Numerical), specify separators, and generate file names with QR codes for easy sharing.  
We have used Harvard's plan and design file-naming-conventions as a guide for the app.
* https://datamanagement.hms.harvard.edu/plan-design/file-naming-conventions

## Run it locally 

**Prerequisites**
* Python >= 3.13.2

### Setup and Running Instructions

1. **Navigate to the script directory**  
   Open your terminal and change to the directory containing `BEA_NameBuilder`:
   ```bash
   cd <path/to/BEA-NameBuilder>
   ```
    _Replace `<path/to/BEA-NameBuilder>` with the actual path on your system._

2. **Create a virtual environment**  
    It’s good practice to create a virtual environment to isolate dependencies. **<span style="color:red">Run this command only the first time:</span>** 
    ```bash
    python3 -m venv .venv 
    ```
3. Activate the virtual environment  
    * _**Windows**_
        ```bash
        .venv\Scripts\activate
        ```
    * _**Linux/macOS**_
        ```bash
        source venv/bin/activate
        ```
    _After activation, you’ll see (venv) in your terminal prompt._


4. Install all the required packages  

    Install the dependencies listed in `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```
5. Run the application  

    Launch the pH-meter app using Streamlit:

    ```bash
    streamlit run main.py
    ```
    * If your browser doesn’t open automatically, navigate to: `http://localhost:8501`