# Frontend Setup Instructions

## Prerequisites
- Node.js 16+ and npm installed

## Installation

1. **Navigate to frontend directory:**
   ```bash
   cd webapp/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

   Frontend will be available at: `http://localhost:3000`

4. **Make sure backend is running:**
   ```bash
   # In another terminal
   cd webapp/backend
   python main.py
   ```

   Backend should be running at: `http://localhost:8000`

## Build for Production

```bash
npm run build
```

Built files will be in `dist/` directory.

## Features

- ✨ Modern React with Vite
- 🎨 Beautiful UI with dark mode
- 📱 Fully responsive
- 🚀 Fast development with HMR
- 🎯 API integration with backend
- 💫 Smooth animations and transitions

## Pages

- **Home** - Landing page with features
- **Analyze** - Upload and analyze syllabi
- **Generate** - AI-powered syllabus generation
- **Optimize** - Get optimization suggestions
