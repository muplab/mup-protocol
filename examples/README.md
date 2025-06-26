# MUP (Model UI Protocol) Examples

This directory contains complete implementation examples of the MUP protocol, demonstrating how to build an AI-driven user interface system based on MUP.

## File Description

### Core Files

- **`simple-form-example.json`** - MUP component definition example, showcasing a complete user registration form
- **`mup-client.js`** - JavaScript client implementation, responsible for rendering MUP components and handling user interactions
- **`mup-server.py`** - Python server implementation, responsible for generating MUP components and handling events
- **`demo.html`** - Complete demonstration page, showcasing the MUP protocol workflow

## Quick Start

### 1. Environment Setup

Ensure your system has:
- Python 3.7+
- Modern browser (Chrome 90+, Firefox 88+, Safari 14+)

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install websockets
```

### 3. Start the Server

```bash
# Run in the examples directory
python mup-server.py
```

The server will start at `ws://localhost:8080`.

### 4. Open the Demo Page

Open the `demo.html` file in your browser, or use a local server:

```bash
# Use Python's built-in server
python -m http.server 8000

# Then visit http://localhost:8000/demo.html
```

### 5. Experience the Demo

1. Click the "Connect to Server" button
2. Observe the dynamically generated form interface
3. Try filling out the form and see real-time validation
4. Submit the form to see server response

## Architecture Overview

### Client Side (mup-client.js)

**Main Functions:**
- WebSocket connection management
- MUP component rendering
- User event capture and forwarding
- Incremental update handling
- Form validation display

**Core Classes:**
- `MUPClient` - Main client class
- Component rendering methods: `createContainer()`, `createText()`, `createInput()`, `createButton()`
- Event handling: `bindEvents()`, `handleComponentEvent()`

### Server Side (mup-server.py)

**Main Functions:**
- WebSocket server
- Dynamic component generation
- Event routing and handling
- Form validation logic
- AI integration interface

**Core Classes:**
- `MUPServer` - Main server class
- `MUPComponent` - Component data model
- `ComponentBuilder` - Component builder
- `EventHandler` - Event handler base class
- `AIFormGenerator` - AI form generator

## Protocol Flow

### 1. Connection Establishment

```
Client → Server: WebSocket connection
Client → Server: Handshake message
Server → Client: Initial UI component tree
```

### 2. User Interaction

```
User Action → Client: DOM event
Client → Server: MUP event message
Server Processing: Business logic + validation
Server → Client: Update instructions
Client Update: UI state changes
```

### 3. Dynamic Updates

```
AI Model → Server: New UI requirements
Server Generation: MUP component tree
Server → Client: Component tree update
Client Rendering: New UI interface
```

## Extension Examples

### Adding Custom Components

1. **Add component type on server side:**

```python
@staticmethod
def custom_chart(id: str, data: list, chart_type: str = "line") -> MUPComponent:
    props = {
        "data": data,
        "chart_type": chart_type,
        "width": 400,
        "height": 300
    }
    return MUPComponent(id=id, type="custom_chart", props=props)
```

2. **Add rendering logic on client side:**

```javascript
createCustomChart(component) {
    const canvas = document.createElement('canvas');
    const props = component.props || {};
    
    canvas.width = props.width || 400;
    canvas.height = props.height || 300;
    
    // Use Chart.js or other charting libraries for rendering
    this.renderChart(canvas, props.data, props.chart_type);
    
    return canvas;
}
```

### AI Model Integration

```python
class OpenAIFormGenerator(AIFormGenerator):
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    async def generate_form_from_prompt(self, prompt: str) -> MUPComponent:
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Generate MUP component JSON"},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse AI response and generate components
        component_data = json.loads(response.choices[0].message.content)
        return self.parse_component(component_data)
```

## Performance Optimization

### Client-side Optimization

1. **Component Caching:**
```javascript
// Cache rendered components
this.componentCache.set(component.id, {
    component,
    element,
    lastUpdate: Date.now()
});
```

2. **Incremental Updates:**
```javascript
// Only update changed parts
applyIncrementalUpdate(operations) {
    operations.forEach(op => {
        if (op.type === 'modify') {
            this.updateComponentProps(op.componentId, op.newProps);
        }
    });
}
```

### Server-side Optimization

1. **Connection Pool Management:**
```python
class ConnectionPool:
    def __init__(self, max_connections=1000):
        self.connections = {}
        self.max_connections = max_connections
    
    async def add_connection(self, client_id, websocket):
        if len(self.connections) >= self.max_connections:
            await self.cleanup_stale_connections()
        self.connections[client_id] = websocket
```

2. **Component Tree Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def generate_cached_form(form_type: str) -> MUPComponent:
    return self.component_generators[form_type]()
```

## Debugging Tips

### 1. Enable Verbose Logging

```python
# Server side
import logging
logging.basicConfig(level=logging.DEBUG)
```

```javascript
// Client side
const client = new MUPClient({
    debug: true,
    logLevel: 'verbose'
});
```

### 2. Message Tracing

View WebSocket messages in browser developer tools:
- Network tab → WS filter
- View sent and received MUP messages

### 3. Component Inspection

```javascript
// In browser console
console.log(window.mupClient.componentCache);
console.log(window.mupClient.currentTree);
```

## Common Issues

### Q: Connection failed?
A: Check if the server is running, if the port is occupied, firewall settings, etc.

### Q: Components not displaying?
A: Check if component definitions comply with MUP specifications, review browser console error messages.

### Q: Events not responding?
A: Ensure event handlers are properly registered, check event name mappings.

### Q: How to add new component types?
A: Add component building methods on the server side, add corresponding rendering logic on the client side.

## Advanced Topics

### 1. Multi-tenant Support

```python
class MultiTenantMUPServer(MUPServer):
    def __init__(self):
        super().__init__()
        self.tenant_configs = {}
    
    async def handle_client(self, websocket, path):
        tenant_id = self.extract_tenant_id(path)
        config = self.tenant_configs.get(tenant_id)
        # Use tenant-specific configuration
```

### 2. Permission Control

```python
class PermissionHandler:
    def check_component_access(self, user_id: str, component_type: str) -> bool:
        user_permissions = self.get_user_permissions(user_id)
        return component_type in user_permissions.allowed_components
```

### 3. Internationalization Support

```javascript
class I18nMUPClient extends MUPClient {
    constructor(options) {
        super(options);
        this.locale = options.locale || 'en-US';
        this.translations = options.translations || {};
    }
    
    translateText(text) {
        return this.translations[this.locale]?.[text] || text;
    }
}
```

## Contributing Guidelines

1. Fork the project
2. Create a feature branch
3. Commit your changes
4. Submit a Pull Request

## License

MIT License - See the LICENSE file in the project root directory for details.

## Contact

- Project Homepage: https://github.com/muplab/mup-protocol
- Issue Reports: https://github.com/muplab/mup-protocol/issues
- Email Contact: mup@csun.cc
