# 🇦🇱 PaFaqe.al

> The premier B2B intelligence platform engineered for web design agencies, digital marketing pioneers, and freelance developers to discover and close local Albanian businesses operating without a website.

🔗 **Live Production URL:** [https://6kristian.github.io/pafaqe-al/](https://6kristian.github.io/pafaqe-al/)[cite: 1]

---

## 🚀 Overview

**PaFaqe.al** bridges the critical gap between Albania's thriving traditional business sector and the digital economy. Thousands of local enterprises—ranging from boutique hotels and family restaurants to specialized clinics and auto services—rely exclusively on fragmented social media or physical foot traffic. 

PaFaqe.al aggregates open market data into a structured sales pipeline, giving outreach professionals direct access to verified phone numbers, custom lead scoring, instant WhatsApp pitch generators, and cloud CRM tools.

---

## ✨ Key Features

* **13,900+ Verified Leads:** Aggregated across major Albanian municipalities (including Tirana, Durrës, Vlorë, and beyond) and structured efficiently via Firestore chunks (`lead_chunks`).
* **Secure Authentication & Gating:** Powered by Firebase Auth with strict **Option B** security rules ensuring only verified email accounts can access lead records.
* **Instant WhatsApp Pitch Generator:** Create customized, high-converting outreach scripts instantly with a single click.
* **Cloud CRM Workspace:** Save custom lead statuses, notes, and follow-up reminders synchronized securely per user profile.
* **Advanced Filtering & Search:** Filter dynamically by city, category, or search keywords with blazing-fast client-side rendering.
* **Lightning-Fast Performance:** Optimized for sub-second First Contentful Paint (FCP) and Largest Contentful Paint (LCP)[cite: 1].
* **Dark & Light Mode:** Fully responsive, modern SaaS interface built with custom styling and Tailwind CSS.

---

## 🛠️ Tech Stack

* **Frontend:** HTML5, Vanilla JavaScript (ES6+), Tailwind CSS (`output.css`)[cite: 1]
* **Backend & Database:** Firebase Auth & Cloud Firestore (Compat SDK v10.8.0)[cite: 1]
* **Hosting & CDN:** GitHub Pages powered by Fastly CDN[cite: 1]

---

## 🔒 Firestore Security Rules

The application enforces strict data privacy and access control using the following production rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {

    // Full lead list: verified accounts can read, nobody can write from client.
    match /lead_chunks/{chunkId} {
      allow read: if request.auth != null && request.auth.token.email_verified == true;
      allow write: if false;
    }

    // Each user's profile, statuses, and notes: strictly scoped to that user.
    match /users/{uid}/{document=**} {
      allow read, write: if request.auth != null && request.auth.uid == uid;
    }

    // Default deny
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
