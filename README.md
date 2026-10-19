# PaFaqe.al

A lightweight web app designed to help web designers, developers, and marketers find local businesses in Albania that don't have a website.

Live site: [https://6kristian.github.io/pafaqe-al/](https://6kristian.github.io/pafaqe-al/)

## Features
- **13,900+ Leads:** Covers businesses across major Albanian cities like Tirana, Durrës, and Vlorë.
- **Chunked Database:** Leads are stored in Firestore chunks (`lead_chunks`) for fast retrieval.
- **Secure Access:** Uses Firebase Auth with email verification enforced via security rules so only verified users can view lead data.
- **Built-in Tools:** Includes an instant WhatsApp pitch generator, custom lead notes, and follow-up reminders.
- **Lightweight Frontend:** Clean, responsive UI with dark/light mode support.

## Tech Stack
- **Frontend:** HTML, Vanilla JavaScript, Tailwind CSS
- **Backend/Database:** Firebase Auth & Cloud Firestore (Compat SDK v10.8.0)
- **Hosting:** GitHub Pages

## Running Locally
To test or run the project locally:

1. Clone the repository
2. Spin up a local static server:
   ```bash
   python -m http.server 8000
