# Aetherra Deployment Guide

This guide explains how to deploy the Aetherra consciousness-aware platform to GitHub Pages.

## 🚀 Deployment Overview

The Aetherra website is built using Vite + React + TypeScript and automatically deployed to GitHub Pages using GitHub Actions. The deployment process is fully automated once configured.

## 📁 Project Structure

```
Aetherra/
├── web/aetherra-website/         # React application source
│   ├── src/                      # Source code
│   ├── package.json              # Dependencies and build scripts
│   └── vite.config.ts            # Vite configuration
├── docs/                         # Built website (GitHub Pages source)
├── .github/workflows/deploy.yml  # GitHub Actions deployment
└── README_DEPLOY.md              # This file
```

## ⚙️ Configuration

### 1. Vite Configuration

The `vite.config.ts` is configured for GitHub Pages deployment:

```typescript
export default defineConfig({
  plugins: [react()],
  base: '/Aetherra/', // GitHub Pages base path
  build: {
    outDir: '../docs',
    emptyOutDir: true
  }
})
```

### 2. Package.json Build Script

The build script outputs to the `docs` directory:

```json
{
  "scripts": {
    "build": "vite build --outDir ../docs --base ./",
  }
}
```

### 3. GitHub Actions Workflow

Located at `.github/workflows/deploy.yml`, this workflow:

- Triggers on pushes to the `main` branch
- Installs Node.js dependencies
- Builds the React application
- Deploys to GitHub Pages

## 🔧 Setup Instructions

### 1. Enable GitHub Pages

1. Go to your repository settings
2. Navigate to "Pages" in the sidebar
3. Under "Source", select "GitHub Actions"
4. The deployment workflow will handle the rest

### 2. Repository Settings

Ensure your repository is configured correctly:

- **Repository name**: Should match the base path in `vite.config.ts`
- **Visibility**: Can be public or private (GitHub Pro required for private Pages)
- **Actions permissions**: Enable GitHub Actions

### 3. Environment Variables

No additional environment variables are required. The workflow uses:

- `GITHUB_TOKEN` (automatically provided)
- Standard GitHub Actions permissions

## 🚀 Deployment Process

### Automatic Deployment

Every push to the `main` branch automatically triggers deployment:

1. **Code Push**: Push changes to the `main` branch
2. **Build Trigger**: GitHub Actions detects changes in web files
3. **Install Dependencies**: `npm ci` installs packages
4. **Build Application**: `npm run build` creates production build
5. **Deploy Pages**: Built files are deployed to GitHub Pages
6. **Live Update**: Site updates at `https://yourusername.github.io/Aetherra/`

### Manual Deployment

To manually trigger deployment:

1. Navigate to the "Actions" tab in your repository
2. Select the "Deploy Aetherra to GitHub Pages" workflow
3. Click "Run workflow" and select the `main` branch

## 🌐 Accessing the Deployed Site

Once deployed, your site will be available at:

```
https://AetherraLabs.github.io/Aetherra/
```

Replace `AetherraLabs` with your actual GitHub username or organization name.

## 📝 Local Development

### Development Server

```bash
cd web/aetherra-website
npm install
npm run dev
```

This starts the development server at `http://localhost:5173`

### Production Build (Local)

```bash
cd web/aetherra-website
npm run build
```

The built files will be in the `docs/` directory.

### Preview Build

```bash
cd web/aetherra-website
npm run preview
```

This serves the production build locally for testing.

## 🔍 Troubleshooting

### Common Issues

**1. 404 Errors on Refresh**
- Solution: The `404.html` file handles client-side routing
- Redirects users back to the main application

**2. Assets Not Loading**
- Check the `base` path in `vite.config.ts`
- Ensure it matches your repository name

**3. Build Failures**
- Check the Actions tab for detailed error logs
- Verify all dependencies are listed in `package.json`

**4. Deployment Not Triggering**
- Check that changes are in the monitored paths
- Verify GitHub Actions are enabled

### Workflow Debugging

View deployment logs:

1. Go to the "Actions" tab
2. Select the latest workflow run
3. Expand job steps to see detailed logs

## 📊 Performance Optimization

The deployed site includes:

- **Code Splitting**: Automatic chunk splitting for optimal loading
- **Asset Optimization**: Minified CSS and JavaScript
- **Caching**: Proper cache headers for static assets
- **Compression**: Gzipped assets for faster loading

## 🔒 Security Considerations

- All secrets are managed through GitHub
- No sensitive data is exposed in the client
- HTTPS is enforced by GitHub Pages
- Content Security Policy headers are configured

## 📈 Monitoring

Monitor your deployment:

- **GitHub Actions**: Build and deployment status
- **GitHub Pages**: Usage and performance metrics
- **Browser DevTools**: Client-side performance analysis

## 🤝 Contributing

To contribute to the deployment process:

1. Fork the repository
2. Make changes to the workflow or configuration
3. Test thoroughly in your fork
4. Submit a pull request with detailed changes

## 📚 Additional Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Vite Documentation](https://vitejs.dev/guide/)
- [React Router GitHub Pages Guide](https://create-react-app.dev/docs/deployment/#github-pages)

---

**Need help?** Check the GitHub Issues or contact the Aetherra development team.

*Last updated: August 8, 2025*
