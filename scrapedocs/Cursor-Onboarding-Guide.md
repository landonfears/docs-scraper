# 🧠 Local Context Onboarding for Cursor AI

Welcome to your AI-enhanced dev workflow using **Cursor** + local documentation context!

This guide helps Cursor AI understand and use the custom docs you’ve injected into this project.

---

## 📁 Folder Structure

Your local documentation lives here:

```bash
/docs/
├── shadcn/        # UI components reference
├── tailwind/      # Styling utilities
├── prisma/        # ORM API and config
└── ...            # Other scraped docs
```

---

## 💬 What to Tell Cursor (First Time)

Open the Cursor chat and say:

```text
Use the /docs folder in this project as local documentation context. For example, /docs/shadcn contains the official ShadCN UI docs. Assume these are the canonical docs when answering related questions.
```

---

## 🔍 Example Prompts

- `Explain how to use the Typography component from /docs/shadcn`
- `Summarize how to configure a new Prisma model from /docs/prisma`
- `How do I add custom Tailwind colors using local docs in /docs/tailwind?`

---

## 🛠 Tips

- Keep all scraped docs in `/docs` in markdown format for maximum AI readability.
- Use your `copy-docs` or `inject-context` CLI to quickly inject relevant folders into new projects.
- Customize this README as needed per project.

---

## ✅ Cursor Setup Complete

You're now running a context-rich AI dev environment with:

- Centralized doc scraping ✅
- Project-level injection ✅
- Local AI comprehension ✅

Happy building! 🚀
