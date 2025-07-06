# Aetherra Website

The official website for Aetherra - Code Awakened, the next-generation AI-native development environment.

## 🌟 Features

### Visual Design

- **Crystal Blue & Jade Green** brand color scheme
- **Responsive design** optimized for all devices
- **Dark theme** with elegant typography
- **Smooth animations** and interactive elements

### Interactive Components

- **Particle background animation** for visual appeal
- **Interactive terminal demo** with live command execution
- **AI assistant preview** with floating modal
- **Live code generation demo** with syntax highlighting
- **Progressive Web App (PWA)** capabilities

### Performance

- **Service Worker** for offline functionality
- **Optimized assets** and lazy loading
- **Fast loading times** with efficient CSS/JS
- **SEO optimized** with proper meta tags

## 🚀 Technologies Used

- **HTML5** with semantic markup
- **CSS3** with custom properties and modern features
- **Vanilla JavaScript** for interactions
- **Service Worker** for PWA functionality
- **Web App Manifest** for app-like experience

## 📱 PWA Features

The website is a full Progressive Web App with:

- **Offline functionality** via service worker
- **App-like experience** when installed
- **Push notifications** support
- **Background sync** for analytics
- **Responsive design** for all screen sizes

## 🎨 Design System

### Colors

- **Primary**: Crystal Blue (#0891b2)
- **Secondary**: Jade Green (#22c55e)
- **Accent**: Intelligence Purple (#8b5cf6)
- **Background**: Deep Space (#0f172a)

### Typography

- **Primary Font**: Inter (San-serif)
- **Code Font**: JetBrains Mono (Monospace)

### Spacing

- Consistent 8px base unit system
- Responsive spacing that scales with screen size

## 🛠️ Development

### Local Development

```bash
# Serve locally (any simple HTTP server)
python -m http.server 8000
# or
npx serve .
```

### File Structure

```text
website/
├── index.html          # Main HTML file
├── styles.css          # All styles and design system
├── script.js           # Interactive functionality
├── sw.js              # Service worker for PWA
├── manifest.json      # Web app manifest
├── favicon.svg        # Site icon
└── README.md         # This file
```

### Browser Support

- **Modern browsers** (Chrome 80+, Firefox 75+, Safari 13+, Edge 80+)
- **Mobile browsers** with full responsive support
- **PWA features** on supported browsers

## 🔧 Customization

### Adding New Sections

1. Add HTML structure to `index.html`
2. Add corresponding styles to `styles.css`
3. Add any interactive behavior to `script.js`

### Updating Colors

Modify the CSS custom properties in `:root` selector:

```css
:root {
    --crystal-blue: #0891b2;
    --jade-green: #22c55e;
    /* Add your colors here */
}
```

### Adding Animations

Use the existing transition system:

```css
.your-element {
    transition: var(--transition);
}
```

## 📈 Analytics

The website includes placeholders for:

- **Page view tracking**
- **Button click tracking**
- **Performance monitoring**
- **Error tracking**

Add your analytics provider code in the respective functions in `script.js`.

## 🚀 Deployment

### GitHub Pages

1. Push to repository
2. Enable GitHub Pages in repository settings
3. Configure custom domain if needed

### Netlify

1. Connect repository
2. Deploy with default settings
3. Configure custom domain and SSL

### Cloudflare Pages

1. Connect repository
2. Use build settings: `npm run build` (if applicable)
3. Deploy with global CDN

## 📝 Content Updates

### Adding Features

Update the features grid in the HTML with new feature cards following the existing pattern.

### Updating Documentation Links

Modify the navigation and documentation sections to point to your actual documentation.

### Customizing Demo Code

Update the Aetherra code examples in the demo section to showcase your latest language features.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly across browsers
5. Submit a pull request

## 📄 License

This website is part of the Aetherra project and follows the same licensing terms.

## 🔗 Links

- **Main Project**: [Aetherra Repository](https://github.com/your-username/aetherra)
- **Documentation**: [GitHub Repository](https://github.com/Zyonic88/Aetherra)
- **Live Website**: [zyonic88.github.io/Aetherra](https://zyonic88.github.io/Aetherra/)

---

Built with ❤️ for the Aetherra community
