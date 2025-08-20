# Model UI Protocol (MUP) v1.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/mup-protocol/mup-protocol)
[![Protocol](https://img.shields.io/badge/protocol-WebSocket-green.svg)](https://tools.ietf.org/html/rfc6455)

Model UI Protocol (MUP) is an open standard protocol designed to provide standardized dynamic UI generation and interaction capabilities for Large Language Models (LLM) and AI applications. MUP addresses the limitations of traditional AI applications that can only output text, enabling AI to generate rich, interactive user interfaces.

## 🎯 Vision

MUP enables AI models to create dynamic, interactive user interfaces that go beyond simple text responses. Imagine AI assistants that can generate forms, charts, dashboards, and complex interactive components in real-time based on user needs.

## ✨ Key Features

- **🔧 Standardized Components**: Unified component definitions for cross-platform compatibility
- **🚀 Real-time Communication**: WebSocket-based bidirectional communication
- **🔒 Security First**: Built-in authentication, authorization, and data validation
- **📱 Cross-platform**: Support for web, desktop, and mobile applications
- **🎨 Rich UI Components**: Forms, charts, containers, inputs, buttons, and more
- **⚡ Performance Optimized**: Batch operations, incremental updates, and intelligent caching
- **🔄 Version Control**: Semantic versioning with backward compatibility
- **🛠️ Extensible**: Support for custom components and plugins

## 🏗️ Architecture

![Kernel density estimation graph](/MUP-LLM-Architecture-Graphical-Abstract.png)

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- Modern web browser (Chrome 90+, Firefox 88+, Safari 14+)
- WebSocket support

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/mup-protocol/mup-protocol.git
   cd mup-protocol
   ```

2. **Install dependencies**
   ```bash
   cd examples
   pip install -r requirements.txt
   ```

3. **Start the MUP server**
   ```bash
   python mup-server.py
   ```
   Server will start at `ws://localhost:8080`

4. **Open the demo**
   ```bash
   # Start a local web server
   python -m http.server 8000
   
   # Open http://localhost:8000/demo.html in your browser
   ```

### Basic Usage

#### Server-side (Python)

```python
import asyncio
import websockets
import json

async def handle_client(websocket, path):
    # Send a simple form component
    component = {
        "mup": {
            "version": "1.0.0",
            "message_type": "component_update",
            "payload": {
                "component_tree": {
                    "id": "login_form",
                    "type": "form",
                    "props": {
                        "title": "Login"
                    },
                    "children": [
                        {
                            "id": "username",
                            "type": "input",
                            "props": {
                                "label": "Username",
                                "type": "text",
                                "required": True
                            }
                        }
                    ]
                }
            }
        }
    }
    await websocket.send(json.dumps(component))

start_server = websockets.serve(handle_client, "localhost", 8080)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

#### Client-side (JavaScript)

```javascript
const socket = new WebSocket('ws://localhost:8080');

socket.onmessage = function(event) {
    const message = JSON.parse(event.data);
    if (message.mup.message_type === 'component_update') {
        renderComponent(message.mup.payload.component_tree);
    }
};

function renderComponent(component) {
    // Render the component based on its type and props
    const element = document.createElement('div');
    element.id = component.id;
    // ... rendering logic
    document.body.appendChild(element);
}
```

## 📚 Documentation

- **[Protocol Specification (English)](./mup-protocol-v1.0-spec-EN.md)** - Complete technical specification
- **[Protocol Specification (中文)](./mup-protocol-v1.0-spec-CN.md)** - 完整技术规范
- **[Examples](./examples/)** - Working examples and demos
- **[API Reference](./docs/api.md)** - Detailed API documentation

## 🧩 Component Types

MUP supports a rich set of standard components:

| Component | Description | Use Cases |
|-----------|-------------|----------|
| `container` | Layout container with flex/grid support | Page layouts, sections |
| `text` | Text display with rich formatting | Headings, paragraphs, labels |
| `input` | Form inputs (text, number, email, etc.) | User data collection |
| `button` | Interactive buttons with events | Actions, form submission |
| `form` | Form container with validation | User registration, surveys |
| `chart` | Data visualization components | Analytics, dashboards |
| `table` | Tabular data display | Data grids, reports |
| `modal` | Overlay dialogs | Confirmations, details |

## 🔧 Use Cases

- **AI Assistants**: Generate dynamic forms and interfaces based on user requests
- **Code Generators**: Create interactive configuration UIs for generated code
- **Data Visualization**: Build real-time dashboards and charts
- **Form Builders**: Intelligent form generation with validation
- **Multimodal AI**: Combine text, UI, and interactive elements

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Roadmap

- [ ] **v1.1**: Enhanced chart components and data binding
- [ ] **v1.2**: Mobile-optimized components and touch events
- [ ] **v1.3**: Advanced animation and transition support
- [ ] **v2.0**: Plugin system and custom component marketplace

## 💬 Community

- **GitHub Discussions**: [Ask questions and share ideas](https://github.com/muplab/mup-protocol/discussions)

## 🙏 Acknowledgments

- Thanks to all contributors who have helped shape MUP
- Inspired by modern UI frameworks and WebSocket protocols
- Built with ❤️ for the AI and developer community

---

**Made with ❤️ by the MUP Protocol Team**