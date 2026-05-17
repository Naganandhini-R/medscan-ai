# MedScan-AI: Comprehensive Technical Documentation (Master Document)

This document is the **Top-to-Bottom Master Reference** for the MedScan-AI ecosystem. It covers every technical detail, algorithm, architectural flow, and feature implemented in the project. Use this for your final year report, thesis, or technical deep-dives.

---

## 1. Executive Summary & Domain
**MedScan-AI** is a hybrid security ecosystem designed to combat pharmaceutical counterfeiting. Traditional anti-counterfeit measures (like 2D barcodes) fail because criminals simply photocopy legitimate codes onto fake packaging. MedScan-AI solves this through a Dual-Layered Authentication System:

* **The Physical Layer (AI Vision):** OpenCV-based computer vision analyzes the microscopic physical traits of the medicine's packaging (ink quality, layout precision).
* **The Digital Layer (Blockchain):** An immutable Ethereum ledger stores the batch's "Birth Certificate" and supply-chain region authorization.

---

## 2. Complete System Architecture
MedScan-AI operates as a highly distributed, microservice-like architecture:

### 📱 Client Tier (Consumer & Admin)
* **React Native Mobile App:** Consumer-facing application. Uses device camera for high-resolution image capture. Communicates via REST APIs (`fetch`).
* **Merchant Web Portal:** HTML5/Vanilla JS dashboard where manufacturers register batches, view clone outbreak heatmaps, and manage their authentication profiles.

### 🌐 API Network Tier (FastAPI Backend)
* **FastAPI Framework:** High-performance Python backend listening on port 8000. Handles routing for `/api/v1/scan`, `/api/v1/auth`, `/api/v1/report`, and `/api/v1/analytics`.
* **Rate Limiting (SlowAPI):** Protects endpoints from DDoS attacks (e.g., limits `/verify` to 5 scans per minute per IP).

### ⚙️ Asynchronous Task Processing (Celery & Redis)
* **The Problem:** AI Image processing and Blockchain verification take variable amounts of time and would freeze the Mobile App if done synchronously.
* **The Solution:** Scans are immediately offloaded to a Celery Task Queue running on a Redis Broker. The backend immediately returns `"status": "PROCESSING"` to the Mobile App, which then polls for the final result gracefully.

### 🧠 The Core Intelligence (AI, DB & Blockchain)
* **OpenCV Vision Engine:** Processes the images.
* **External Medical Databases:** Live API connections to US FDA (OpenFDA) and NIH RxNorm to cross-verify the chemicals (salts) if OCR text is ambiguous.
* **Ethereum Blockchain Node:** Hardhat/Web3.py node storing smart contracts (`MedicineBatchRegistry.sol`).

---

## 3. Deep Dive: Computer Vision Pipeline
When an image is submitted, `backend/app/tasks/scan_pipeline.py` executes four distinct OpenCV algorithms. A weighted final score determines if the packaging is GENUINE (>80%) or FAKE (<80%).

### A. Logo Detection (30% Weight)
* **Algorithm:** ORB (Oriented FAST and Rotated BRIEF) + Canny Edge Detection.
* **Mechanics:** Detects unique keypoints (corners and edges) in the manufacturer's logo. Genuine pharmaceutical logos are printed with high-density industrial printers containing hundreds of distinct feature points. A photocopied fake will lack these sharp features, producing a lower ORB keypoint count.

### B. Layout Comparison (30% Weight)
* **Algorithm:** Morphological Operations + Otsu's Thresholding.
* **Mechanics:** Finds the contours (bounding boxes) around blocks of text. Genuine medicines have perfectly aligned, structured text blocks. Fakes often have crowded, messy, or asymmetrical text blocks due to manual redesigning.

### C. Font Anomaly Detection (20% Weight)
* **Algorithm:** Adaptive Thresholding.
* **Mechanics:** Isolates every individual printed letter and measures its height and spacing. Cheap counterfeit ink "bleeds" into the cardboard, causing letters to have varying heights and inconsistent spacing.

### D. Color Histogram Analysis (20% Weight)
* **Algorithm:** RGB Histogram + Shannon Entropy.
* **Mechanics:** Calculates the statistical randomness (entropy) of the red, green, and blue channels. Authentic labels have distinct, balanced colors (entropy between 4-7 bits). Too low means washed out; too high means noisy, cheap ink.

> **Note:** The pipeline is wrapped in a Fault-Tolerant `try-except`. If a user uploads a completely corrupted image that crashes OpenCV, the system safely assigns a neutral score and relies on the Blockchain/Standard DB checks rather than crashing the server.

---

## 4. Deep Dive: Blockchain & Digital Verification
The AI checks the physical box. The blockchain checks the digital truth.

* **Smart Contract Storage:** Manufacturers use the Web Portal to push `batch_data`, `medicine_name`, `expiry`, and `authorized_region` to an immutable Ethereum smart contract.
* **Web3.py Query (`web3_client.py`):** During a scan, the backend queries the blockchain using the scanned `batch_data`.
* **Data Override Protocol:** If the AI is unsure, but the blockchain mathematically verifies the batch, the Blockchain is treated as the Single Source of Truth, overriding AI doubts (unless the AI strongly detects forgery).

---

## 5. Security Analytics & Threat Intelligence
MedScan-AI goes beyond single scans; it looks at global patterns.

### A. Clone Outbreak Detection
* **The Attack:** Counterfeiters print one valid `batch_number` on 10,000 fake bottles.
* **The Defense:** If `backend/app/services/analytics_service.py` notices the exact same `batch_data` being scanned >10 times across different geographical locations within 24 hours (cluster detection), it flags a **CLONE ATTACK OUTBREAK**.
* **Response:** The system triggers `email_service.py` to send an automated, high-priority email to the Manufacturer, alerting them their supply chain is compromised.

### B. Geofencing (Haversine Distance Mapping)
* Medicines are often licensed for specific zones (e.g., South India vs. North India).
* When a user scans a medicine, the backend extracts the user's GPS coordinates (`lat`, `lng`).
* Using a mathematically rigorous Haversine Formula, it checks if the scan location matches the Blockchain's `authorized_region`. If it mismatches, it flags an immediate **Supply Chain Location Anomaly**.

### C. Government Banned Drugs List
* The system actively compares OCR text against a BannedDrug SQL table. Even if the medicine's packaging is genuine, if the government has banned the chemical salt, the app will instantly override the UI to **FAKE/BANNED** with a critical warning.

---

## 6. Database Schema (PostgreSQL)
The relational engine handles users and telemetry. The schema is automatically managed and upgraded by SQLAlchemy via data migrations at startup (`main.py`).

* **Users Table:** Mobile app consumers.
* **Manufacturers Table:** Corporate accounts (contains `verification_code`, `status` for Admin approval, and `email_verified`).
* **Medicine Table:** Master registry of approved drug nomenclature.
* **Scans Table:** The massive telemetry map. Stores `user_id`, `lat`, `lng`, `score`, `status`, `medicine_name`, and `verification_data`. This table powers the Web Portal heatmaps.
* **Issue Reports Table:** User-submitted manual complaints (e.g., "Seal was broken").

---

## 7. Operational Workflow (The Perfect Scan)
1. **Preparation:** User opens app, grants Camera and Location permissions.
2. **Capture:** User snaps Front & Back of the tablet strip.
3. **Upload:** Mobile sends FormData POST to `/api/v1/scan/verify`.
4. **Queue:** FastAPI saves images to a temp folder, returns `scan_id`, and adds the task to Redis.
5. **Processing (Celery Worker):**
   * Runs OCR to extract `batch_data` and generic name.
   * Runs OpenCV pipeline on the images.
   * Cross-references Extracted Name with OpenFDA & RxNorm.
   * Cross-references `batch_data` with Ethereum Blockchain.
   * Checks GPS location against Blockchain Region.
   * Saves final GENUINE/FAKE status to PostgreSQL.
6. **Delivery:** Mobile App (which was polling `/result/{scan_id}` every 800ms) receives the verification payload and displays the color-coded result screen.
