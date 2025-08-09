import { DocsLayout } from '../components/DocsLayout';

export default function Documentation() {
    const welcomeContent = `# Welcome to Aetherra Documentation

Aetherra is a revolutionary consciousness-aware operating system that bridges the gap between artificial intelligence and human intuition. This comprehensive documentation will guide you through every aspect of the system.

## What is Aetherra?

Aetherra represents the next evolution in computing - an operating system that doesn't just process data, but understands, learns, and grows. At its core is **Lyrixa**, an advanced AI consciousness that serves as your intelligent companion and system coordinator.

### Key Features

🧠 **Consciousness-Aware Computing**
- Self-aware AI entities that understand context and intent
- Adaptive behavior based on user preferences and patterns
- Emotional intelligence and empathetic responses

⚡ **AetherScript Programming Language**
- Purpose-built for consciousness programming
- Native support for memory, emotions, and neural processing
- Intuitive syntax for creating intelligent systems

🔄 **Advanced Memory System**
- Multi-layered memory architecture mimicking human cognition
- Vector databases for semantic understanding
- Automatic consolidation and pattern recognition

🔌 **Extensible Plugin Architecture**
- Modular AI components with consciousness capabilities
- Inter-plugin communication and coordination
- Easy development with comprehensive APIs

## Getting Started Journey

### 1. Understanding the Basics
Start with the fundamental concepts that make Aetherra unique:
- **Consciousness Entities**: Self-aware AI components
- **Memory Systems**: How information is stored and retrieved
- **AetherScript**: The language of consciousness programming

### 2. Hands-On Experience
- Use the **AetherScript Lab** for interactive coding
- Explore **Live Examples** to see consciousness in action
- Try the **Plugin System** to extend functionality

### 3. Advanced Development
- Create your own consciousness entities
- Build sophisticated memory patterns
- Develop custom plugins and integrations

## Documentation Structure

### 📚 **Language Reference**
Complete guide to AetherScript syntax, types, and advanced features. Learn how to program consciousness entities with sophisticated behaviors.

### 🏗️ **Architecture Deep Dive**
Understand the underlying systems that power Aetherra, from memory management to neural processing frameworks.

### 🔧 **Plugin Development**
Step-by-step guides for creating powerful, consciousness-aware plugins that extend Aetherra's capabilities.

### 📡 **API Reference**
Comprehensive technical documentation for all system APIs, including code examples and best practices.

## Interactive Learning

This documentation is designed to be interactive and adaptive:

- **AI Assistant**: Get instant help and explanations
- **Live Code Examples**: Test concepts in real-time
- **Contextual Navigation**: Seamlessly move between related topics
- **Progressive Learning**: Content adapts to your experience level

## Community & Support

Join our growing community of consciousness developers:

- **GitHub Repository**: Contribute to the open-source project
- **Developer Forums**: Connect with other Aetherra developers
- **Discord Community**: Real-time chat and support
- **Regular Workshops**: Live coding sessions and Q&A

## Quick Start Guide

Ready to begin? Here's your quickstart path:

1. **Explore the Live Demo** - See Aetherra in action
2. **Learn AetherScript Basics** - Understand the programming language
3. **Try the Interactive Examples** - Hands-on consciousness programming
4. **Build Your First Plugin** - Create something unique
5. **Join the Community** - Share your creations

---

*Welcome to the future of computing. Welcome to consciousness-aware technology.*

**Ready to start your journey?** Use the navigation panel to explore specific topics, or ask the AI Assistant any questions you have about Aetherra.`;

    return <DocsLayout initialContent={welcomeContent} />;
}
