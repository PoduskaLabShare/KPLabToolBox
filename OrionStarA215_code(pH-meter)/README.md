# Orion Star A215 Script
**This is a script to control the Orion Star A250 pH-meter.**

**Prerequisites**
* Python >= 3.13.2

The script provides a GUI interface, allowing users to operate the pH-meter without writing any code.

### Setup and Running Instructions

1. **Navigate to the script directory**  
   Open your terminal and change to the directory containing `OrionStarA150_code(pH-meter)`:
   ```bash
   cd <path/to/OrionStarA215_code(pH-meter)>
   ```
    _Replace `<path/to/OrionStarA215_code(pH-meter)>` with the actual path on your system._

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
    streamlit run ph_script.py
    ```
    * If your browser doesn’t open automatically, navigate to: `http://localhost:8501`

Update the available electrodes in the `electrode_list.json`