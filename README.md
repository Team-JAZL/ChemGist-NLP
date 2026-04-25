# ChemGist-NLP
Final Project for CCS 249: NLP

## Overview
ChemGist is an organic chemistry assistant built as a browser-based chatbot UI. It helps students and researchers explore molecules, formulas, reaction concepts, and functional groups with a friendly AI interface.

This project also includes backend data-processing tools for chemical datasets, but the main web app is served from `index.html` with `styles.css` and `script.js`.

## Prerequisites
- Python 3.8 or higher
- Internet connection for external JavaScript dependencies and API calls
- A modern browser (Chrome, Edge, Firefox, etc.)

## Installation
1. Clone or download this repository.
2. Install the Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App Locally
The web app uses JavaScript modules, so it must be served over HTTP rather than opened directly from the file system.

1. Open a terminal in the project folder.
2. Start a simple local server:
   ```bash
   python -m http.server 8000
   ```
3. Open your browser and visit:
   ```text
   http://localhost:8000
   ```
4. The ChemGist interface should load and the chat experience will be available.

## Using the App
- **New Chat**: Click `New Chat` in the sidebar to start a fresh conversation.
- **Chat Suggestions**: Click any suggestion card on the empty state screen to send that question immediately.
- **Send a Question**: Type your chemistry question in the input box at the bottom and press `Enter` or click the send button.
- **Chat History**: The sidebar shows recent chats. Click a history item to open that conversation.
- **Rename or Delete**: Use the triple-dot menu on a history item to rename the title or delete the chat.
- **Theme Toggle**: Use the dark mode toggle in the sidebar footer to switch between light and dark themes.

## Features
- AI-powered chemistry chat interface
- Organic chemistry text formatting for subscripts and superscripts
- Local chat history stored in browser `localStorage`
- Responsive sidebar and message layout
- Chat rename/delete controls
- Dark mode support

## Data Processing (Optional)
If you want to use the dataset-processing functionality instead of the browser app:
1. Place your dataset CSV file in the `data/` directory.
2. Make sure the file includes a `SMILES` column.
3. Run:
   ```bash
   python main.py
   ```
4. The script will process each compound, query PubChem, and save results into the project database.

## Troubleshooting
- If the web page shows a local file warning, restart the app using `python -m http.server 8000` and open `http://localhost:8000`.
- If the chat does not load, verify your browser supports module scripts and that the server is running.
- For Python processing issues, check that your Python version matches the requirements and that `requirements.txt` is installed.
