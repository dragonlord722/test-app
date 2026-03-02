# 🍳 AI Fridge Chef: Enterprise Applied AI Platform

**Live Demo:** [Link to your Streamlit App]
**Backend API:** `https://fridge-backend-service-845166114793.us-central1.run.app/docs`

## 🚀 Project Evolution
This platform has successfully transitioned from a monolithic Proof of Concept (PoC) into a hardened, decoupled microservices architecture (**Milestone 2**). By separating the presentation layer from the inference logic, the system achieves independent scalability, enhanced security, and production-grade performance.

## 🏗️ System Architecture
The system is architected as a **Stateless Microservice** ecosystem deployed on Google Cloud Platform (GCP).

* **Frontend (Presentation):** Streamlit (Hosted on Streamlit Community Cloud). Handles client-side optimizations and UI rendering.
* **Backend (Inference):** FastAPI (Containerized with Docker, deployed on Google Cloud Run). Manages business logic and LLM orchestration.
* **AI Engine:** Google Gemini 2.5 Flash (Multimodal VLM).
* **CI/CD:** GitHub Actions using **Workload Identity Federation (WIF)** for keyless, secure GCP deployments.

### 🛡️ L6 Engineering & Performance Highlights
* **Payload Optimization & Compression:** Implemented client-side JPEG compression (thumbnailing to 1024px) before Base64 encoding. This reduced request payloads from ~6MB to <500KB, eliminating network timeouts and reducing latency by 85%.
* **Infrastructure Hardening:** Configured Cloud Run with **2Gi RAM** and **Startup CPU Boost** to handle the high-compute demands of multimodal image decoding and inference.
* **Observability:** Enabled `PYTHONUNBUFFERED` logging and custom FastAPI exception handlers to capture real-time container health metrics and Python tracebacks in Google Cloud Logs Explorer.
* **Zero-Trust Security:** Implemented a custom `X-Portfolio-Token` header validation and **CORS Policy enforcement** to ensure the backend only communicates with authorized clients.
* **Rate Limiting:** Integrated `SlowAPI` to prevent resource exhaustion and protect Gemini API quotas using a per-IP sliding window algorithm.

## 🗺️ Future Roadmap

### Milestone 3: AI Reliability & "Evals"
* **Evaluation Framework:** Integrating `Promptfoo` into the CI pipeline to track hallucination rates and JSON schema adherence across a dataset of 50+ varied fridge scenarios.
* **Prompt Guardrails:** Implementing logic to detect and reject non-food images, returning specific JSON error states rather than hallucinated recipes.

### Milestone 4: Operational Excellence
* **Multi-Model Routing:** Implementing the **Adapter Pattern** to allow seamless switching and automated fallback between Gemini, GPT-4o, and Claude 3.5 Sonnet.
* **Token Budgets:** Introducing a Firestore-based ledger to track and cap total LLM spend per session/IP address.

## 💻 Local Development

### Installation
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/dragonlord722/fridge-app](https://github.com/dragonlord722/fridge-app)
    cd fridge-app
    ```
2.  **Backend Setup:**
    ```bash
    cd backend
    pip install -r requirements.txt
    export X_PORTFOLIO_TOKEN=your_secret
    uvicorn app.main:app --reload
    ```
3.  **Frontend Setup:**
    ```bash
    cd frontend
    pip install -r requirements.txt
    streamlit run streamlit_app.py
    ```
---
