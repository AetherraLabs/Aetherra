# 🌐 Aetherra Website Development

This directory contains the **source code** for the Aetherra website. Never edit the `docs/` directory directly!

## 🚀 Quick Start

### Development (Hot Reload)
```bash
# Windows
dev-website.bat

# Linux/Mac
./dev-website.sh
```

### Production Build
```bash
# Windows
build-website.bat

# Linux/Mac
./build-website.sh
```

## 📁 Project Structure

```
website-src/                 # ← Edit these files
├── src/
│   ├── components/         # Reusable components
│   ├── pages/             # Website pages
│   ├── App.jsx            # Main app
│   ├── main.jsx           # Entry point
│   └── index.css          # Global styles
├── package.json           # Dependencies
├── vite.config.js         # Build configuration
└── index.html            # HTML template

docs/                      # ← Auto-generated (DO NOT EDIT)
├── assets/               # Built JavaScript/CSS
└── index.html           # Built HTML
```

## 🛠️ Development Workflow

1. **Make changes** in `website-src/src/`
2. **Test locally** with `dev-website.bat`
3. **Build for production** with `build-website.bat`
4. **Deploy** by pushing to GitHub (automatic)

## ✅ Why This Setup?

- **No more manual editing** of minified files
- **Hot reload** during development
- **Proper React Router** with all functions
- **Easy debugging** with source maps
- **Consistent builds** every time

## 🔧 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally

## 📦 Dependencies

- **React 19.1.0** - UI framework
- **React Router 6.30.1** - Client-side routing
- **Framer Motion** - Animations
- **Vite 7.0.6** - Build tool

---

**Remember**: Always edit files in `website-src/`, never in `docs/`!
