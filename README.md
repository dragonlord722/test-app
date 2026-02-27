# AI Recipe & Inventory Assistant (Milestone 1: PoC)

An intelligent, multimodal web application that analyzes images of refrigerator contents to extract available ingredients, identify missing staples, and generate customized culinary recipes. 

This repository currently represents **Milestone 1**, a monolithic Proof of Concept (PoC) designed for rapid validation of vision-language model (VLM) capabilities and strict structured output enforcement.



## 🏗️ System Architecture (Current State)
* **Frontend & State Management:** Streamlit
* **AI/Inference Engine:** Google Gemini 2.5 Flash (via Google GenAI SDK)
* **Output Parsing:** Enforced `application/json` MIME type for deterministic contract rendering.

### Engineering Highlights
* **Multimodal Extraction:** Leverages Gemini 2.5 Flash to process raw image data and extract conceptual food items, even in cluttered or poorly lit refrigerator environments.
* **Structured LLM Output:** Bypasses conversational AI fluff. The model is strictly prompted and configured at the API level to return a predefined JSON schema, ensuring the application frontend does not crash due to malformed string parsing.
* **Cost & Latency Optimization:** Utilizing the Flash variant of the model ensures high-speed inference suitable for synchronous web requests while remaining highly cost-efficient.
* **Application-Layer Security:** Implements a lightweight session-state "bouncer" to protect API quotas during public/shared testing, securely reading from environment variables.

## 🚀 Features
* **Zero-Click Inventory:** Upload a photo and receive a parsed list of detected ingredients.
* **Smart Contextual Gap Analysis:** Identifies common staples that are missing based on the detected context (e.g., noticing missing aromatics like onions/garlic).
* **Dynamic Deep Linking:** Automatically generates localized e-commerce search URLs (Whole Foods) for missing ingredients.
* **Custom Recipe Generation:** Currently tuned for pure vegetarian Indian and Fusion cuisines. 

## 💻 Local Development Setup

### Prerequisites
* Python 3.9+
* A free Google Gemini API Key

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/dragonlord722/fridge-app
   cd fridge-app
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Secrets:
Streamlit requires a local secrets file. Create a hidden .streamlit directory and a secrets.toml file inside it:

   ```bash
   mkdir -p .streamlit
   touch .streamlit/secrets.toml
   ```
   Add the following credentials to .streamlit/secrets.toml:
   Ini, TOML

   GEMINI_API_KEY = "your_google_api_key_here"
   APP_PASSWORD = "your_local_testing_password"

   (Note: Ensure .streamlit/ is added to your .gitignore to prevent credential leakage).

   4.  Run the Application:
   ```bash
   streamlit run app.py
   ```
