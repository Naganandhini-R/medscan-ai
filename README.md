# MedScan-AI: A Hybrid AI-Blockchain Ecosystem for Real-Time Medicine Authentication

**Domain:** Artificial Intelligence (Computer Vision) & Blockchain Technology

---

##  The Core Problem

* **Global Crisis:** A massive volume of counterfeit medicines are circulating in developing nations, acting as substandard or falsified medical products.
* **Security Failure:** Traditional holograms and 2D barcodes are easily cloned by sophisticated counterfeiters.
* **System Gap:** Existing central databases are vulnerable to hacking and do not verify the physical integrity of the packaging.

---

##  Our Mission
To save lives and economic loss by creating a "Digital Twin" verification system that validates both the **Physical Item** (via AI) and its **Digital History** (via Blockchain).

---

##  Abstract & Solution Architecture
**MedScan-AI** is a dual-layered security framework designed to detect counterfeit medicines by verifying packaging aesthetics and digital provenance simultaneously.

### The Hybrid Approach:
* **Physical Layer (AI Vision):** Detects microscopic printing imperfections (resolution, font bleeding, color shifts) that distinguish industrial printing from home-made fakes.
* **Digital Layer (Blockchain):** Stores immutable "Birth Certificates" for every batch, preventing data tampering.

### Key Intelligence Features:
* **Geolocation Geofencing:** Alerts if a medicine is scanned outside its authorized sales region.
* **Outbreak Analytics:** Detects "clone attacks" via high-frequency scan anomalies.
* **Real-Time Feedback:** Immediate "Genuine" or "Fake" classification for the consumer.

---

##  Technical "Secret Sauce"

### 1. AI Computer Vision Pipeline (The Eyes)
* **Logo Detection:** Uses ORB algorithms to match feature keypoints against the official master template.
* **Layout & Structure:** Morphological analysis to check text alignment and spacing.
* **Color Forensics:** RGB Histogram Entropy to detect washed-out or inconsistent ink densities.
* **Font Analysis:** Adaptive thresholding to spot cheap "bleeding" ink common in fakes.

### 2. Blockchain Ledger (The Truth)
* **Platform:** Ethereum (EVM Compatible).
* **Smart Contract:** Stores the cryptographic hash of the manufacturer's batch data.
* **Immutability:** Once a batch is registered by the manufacturer, it cannot be altered or deleted by anyone.

---

## System Specifications

### Hardware Requirements
* **Server:** Quad-core CPU, 16GB RAM, SSD Storage (for AI Processing & Blockchain Node).
* **Client:** Android/iOS Smartphone with 12MP+ Camera (Macro photography capable).

### Software Tech Stack
* **Mobile App:** React Native, TypeScript, Vision Camera, MLKit OCR.
* **Backend API:** FastAPI (High Performance Python), Celery (Task Queue), Redis.
* **AI Engine:** OpenCV (Headless), Scikit-Image, NumPy, PyTorch.
* **Blockchain:** Solidity (Smart Contracts), Hardhat, Web3.py, Ganache.
* **Database:** PostgreSQL (Relational Data), Docker (Containerization).
* **Security Notification:** SMTP (`smtplib`), FastAPI BackgroundTasks.
* **Web Portal:** HTML5/JS Dashboard for Manufacturer batch registration.

---

##  The Proposed System & Methodology
### The Sequential Authentication Pipeline

1. **Manufacturer Verification:** Central Admin approves the license; manufacturer is granted "Verified" status.
2. **Blockchain Seeding:** Verified Manufacturer seeds genuine batch data and regions into the Ethereum Smart Contract.
3. **Physical Mobile Scan:** Consumer captures a high-resolution image via the React Native Mobile App.
4. **AI Forensics & Standards Check:** The Backend runs noise reduction, OCR, and cross-references results against FDA & RxNorm standards to validate clinical nomenclature.
5. **Authenticity Scoring:** Calculates a score based on microscopic printing flaws, color entropy, and layout alignment.
6. **Blockchain Cross-Check:** Queries the ledger via Web3.py to ensure the scanned batch data is cryptographically valid.
7. **Instant Action:** Immediate Genuine/Fake classification for the user; real-time threat map update for the Admin.

---

##  Key Features
* **AI Vision Pipeline:** Micro-printed logo and layout verification.
* **Immutable Ledger:** Blockchain-based batch tracking.
* **Forensic Reporting:** Instant notification to manufacturers upon counterfeit detection.
* **Geospatial Tracking:** Automated purchase point tracking via GPS coordinates.

---

##  Project Structure
* `/mobile`: React Native application for consumers.
* `/backend`: FastAPI server for AI processing and API management.
* `/blockchain`: Smart contracts and blockchain integration scripts.
* `/merchant-portal`: Web dashboard for manufacturers.
