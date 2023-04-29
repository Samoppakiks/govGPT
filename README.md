# govGPT

This project is a Flask web application that uses various Python libraries and API services. This README will guide you through the process of setting up the project on your local machine, starting from installing Visual Studio Code to running the web application.

## Prerequisites

*Visual Studio Code (VSCode) installed on your system
*Git installed on your system

## Step 1: Install Visual Studio Code (VSCode)

If you don't have VSCode installed, please download and install it from the following link: [https://code.visualstudio.com](https://code.visualstudio.com/)

## Step 2: Install Git

If you don't have Git installed, please download and install it from the following link: [https://git-scm.com/downloads](https://git-scm.com/downloads)

## Step 3: Clone the Repository

Open VSCode and click on the "Terminal" in the top menu, then click on "New Terminal". This will open a terminal window at the bottom of the screen.
*In the terminal, navigate to the directory where you want to save the project files.
*Run the following command to clone the GitHub repository:

```git clone https://github.com/Samoppakiks/govGPT.git```

*After cloning the repository, open the project folder in VSCode by clicking on "File" > "Open Folder..." and selecting the govGPT folder.

## Step 4: Open the Terminal in VSCode
If you closed the terminal, click on "Terminal" in the top menu and then click on "New Terminal" to open a new terminal window at the bottom of the screen.

## Step 5: Set up a Virtual Environment
In the terminal, run the following command to install the virtualenv package if you don't have it already:

```pip install virtualenv```

Next, create a new virtual environment in your project directory with the following command:

```python -m venv venv```

Activate the virtual environment:
On Windows, run:
```.\venv\Scripts\Activate```
On macOS/Linux, run:
```source venv/bin/activate```

## Step 6: Select the Python Interpreter
In VSCode, click on the "Python" text in the lower-left corner of the window (or press Cmd/Ctrl+Shift+P to open the Command Palette).
Search for "Python: Select Interpreter" and click on it.
Choose "Python 3.11.3" from the list of available interpreters.

## Step 7: Install Dependencies
In the terminal, run the following command to install the required dependencies from the requirements.txt file:

```pip install -r requirements.txt```

## Step 8: Add API Keys
Open the src/embedchat.py file in VSCode.
Replace the following lines with your own API keys in the specified format:
```
openaiapi = os.environ["OPENAI_API_KEY"]
pinecone_api_key = os.environ["PINECONE_API_KEY"]
pinecone_environment = os.environ["PINECONE_ENVIRONMENT"]
```
For example, if your API keys are your_openai_key, your_pinecone_key, and your_pinecone_environment, replace the lines with:

```
openaiapi = "your_openai_key"
pinecone_api_key = "your_pinecone_key"
pinecone_environment = "your_pinecone_environment"
```

## Step 9: Run the Application
In the terminal, run the following command to start the Flask web application:
```python app.py```
The terminal will display a local link (e.g., http://127.0.0.1:5000/). Click on the link to open the locally hosted website in your web browser.

Use the website as desired.








