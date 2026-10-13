# 🚀 PaFaqe.al — Albanian Web Design Leads & B2B CRM

**PaFaqe.al** is a specialized B2B SaaS platform designed for web development agencies, digital marketers, and freelance developers. It aggregates open business data across Albania (Tirana, Durrës, Vlorë, Shkodër, etc.) to identify local businesses operating **without a website**, providing contact details, lead scores, and lead management tools.

Live Demo: [https://6kristian.github.io/pafaqe-al/](https://6kristian.github.io/pafaqe-al/)

---

## 🌟 Key Features

* **Lead Discovery & Scoring:** Filter through hundreds of local businesses without a web presence. Automatically calculates a Lead Score based on phone availability, rating, and review counts.
* **Hybrid Persistence Model:**
  * **Guest Users:** Local tracking via browser `localStorage` to manage outreach statuses (`New`, `Contacted`, `Interested`, `Closed`).
  * **Authenticated Users:** Multi-device real-time sync backed by **Firebase Cloud Firestore**.
* **One-Click Outreach:**
  * Direct WhatsApp chat launch (`wa.me`) formatted for Albanian phone numbers (`+355`).
  * One-click summary copy tool for quick CRM pasting.
* **Excel-Optimized CSV Export:** UTF-8 BOM encoded export (`sep=,`) with locked phone string formatting (`="\t..."`) to prevent scientific notation truncation in Excel (`3.55E+11`).
* **Filtering & Deep Linking:** Filter by city, category, minimum rating, and phone presence. State is automatically preserved in URL parameters for easy bookmarking and sharing.
* **Zero-Cost Serverless Hosting:** Runs as a single-page web app hosted on **GitHub Pages**.

---

## 🛠️ Tech Stack

* **Frontend:** Single-page HTML5 / Modern JavaScript (ES6+)
* **Styling:** Tailwind CSS (via CDN)
* **Authentication:** Firebase Authentication (Email/Password)
* **Database:** Firebase Cloud Firestore (NoSQL)
* **Contact Form:** Web3Forms API
* **Hosting:** GitHub Pages

---

## 🚀 Getting Started

### Prerequisites
To run the project locally or deploy your own instance, you will need:
* A modern web browser.
* A free [Firebase Account](https://console.firebase.google.com/) (if enabling backend user sign-in and cloud sync).

### Running Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/6kristian/pafaqe-al.git](https://github.com/6kristian/pafaqe-al.git)
   cd pafaqe-al
