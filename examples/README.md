# MUP (Model UI Protocol) 示例

这个目录包含了MUP协议的完整实现示例，展示了如何构建一个基于MUP的AI驱动用户界面系统。

## 文件说明

### 核心文件

- **`simple-form-example.json`** - MUP组件定义示例，展示了一个完整的用户注册表单
- **`mup-client.js`** - JavaScript客户端实现，负责渲染MUP组件并处理用户交互
- **`mup-server.py`** - Python服务端实现，负责生成MUP组件并处理事件
- **`demo.html`** - 完整的演示页面，展示MUP协议的工作流程

## 快速开始

### 1. 环境准备

确保你的系统已安装：
- Python 3.7+
- 现代浏览器 (Chrome 90+, Firefox 88+, Safari 14+)

### 2. 安装依赖

```bash
# 安装Python依赖
pip install websockets
```

### 3. 启动服务器

```bash
# 在examples目录下运行
python mup-server.py
```

服务器将在 `ws://localhost:8080` 启动。

### 4. 打开演示页面

在浏览器中打开 `demo.html` 文件，或者使用本地服务器：

```bash
# 使用Python内置服务器
python -m http.server 8000

# 然后访问 http://localhost:8000/demo.html
```

### 5. 体验演示

1. 点击"连接服务器"按钮
2. 观察动态生成的表单界面
3. 尝试填写表单并查看实时验证
4. 提交表单查看服务器响应

## 架构说明

### 客户端 (mup-client.js)

**主要功能：**
- WebSocket连接管理
- MUP组件渲染
- 用户事件捕获和转发
- 增量更新处理
- 表单验证显示

**核心类：**
- `MUPClient` - 主客户端类
- 组件渲染方法：`createContainer()`, `createText()`, `createInput()`, `createButton()`
- 事件处理：`bindEvents()`, `handleComponentEvent()`

### 服务端 (mup-server.py)

**主要功能：**
- WebSocket服务器
- 动态组件生成
- 事件路由和处理
- 表单验证逻辑
- AI集成接口

**核心类：**
- `MUPServer` - 主服务器类
- `MUPComponent` - 组件数据模型
- `ComponentBuilder` - 组件构建器
- `EventHandler` - 事件处理器基类
- `AIFormGenerator` - AI表单生成器

## 协议流程

### 1. 连接建立

```
客户端 → 服务器: WebSocket连接
客户端 → 服务器: 握手消息 (handshake)
服务器 → 客户端: 初始UI组件树
```

### 2. 用户交互

```
用户操作 → 客户端: DOM事件
客户端 → 服务器: MUP事件消息
服务器处理: 业务逻辑 + 验证
服务器 → 客户端: 更新指令
客户端更新: UI状态变更
```

### 3. 动态更新

```
AI模型 → 服务器: 新的UI需求
服务器生成: MUP组件树
服务器 → 客户端: 组件树更新
客户端渲染: 新的UI界面
```

## 扩展示例

### 添加自定义组件

1. **服务端添加组件类型：**

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

2. **客户端添加渲染逻辑：**

```javascript
createCustomChart(component) {
    const canvas = document.createElement('canvas');
    const props = component.props || {};
    
    canvas.width = props.width || 400;
    canvas.height = props.height || 300;
    
    // 使用Chart.js或其他图表库渲染
    this.renderChart(canvas, props.data, props.chart_type);
    
    return canvas;
}
```

### 集成AI模型

```python
class OpenAIFormGenerator(AIFormGenerator):
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    async def generate_form_from_prompt(self, prompt: str) -> MUPComponent:
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "生成MUP组件JSON"},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 解析AI响应并生成组件
        component_data = json.loads(response.choices[0].message.content)
        return self.parse_component(component_data)
```

## 性能优化

### 客户端优化

1. **组件缓存：**
```javascript
// 缓存已渲染的组件
this.componentCache.set(component.id, {
    component,
    element,
    lastUpdate: Date.now()
});
```

2. **增量更新：**
```javascript
// 只更新变化的部分
applyIncrementalUpdate(operations) {
    operations.forEach(op => {
        if (op.type === 'modify') {
            this.updateComponentProps(op.componentId, op.newProps);
        }
    });
}
```

### 服务端优化

1. **连接池管理：**
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

2. **组件树缓存：**
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def generate_cached_form(form_type: str) -> MUPComponent:
    return self.component_generators[form_type]()
```

## 调试技巧

### 1. 启用详细日志

```python
# 服务端
import logging
logging.basicConfig(level=logging.DEBUG)
```

```javascript
// 客户端
const client = new MUPClient({
    debug: true,
    logLevel: 'verbose'
});
```

### 2. 消息追踪

在浏览器开发者工具中查看WebSocket消息：
- Network标签 → WS过滤器
- 查看发送和接收的MUP消息

### 3. 组件检查

```javascript
// 在浏览器控制台中
console.log(window.mupClient.componentCache);
console.log(window.mupClient.currentTree);
```

## 常见问题

### Q: 连接失败怎么办？
A: 检查服务器是否正在运行，端口是否被占用，防火墙设置等。

### Q: 组件不显示？
A: 检查组件定义是否符合MUP规范，查看浏览器控制台错误信息。

### Q: 事件不响应？
A: 确认事件处理器已正确注册，检查事件名称映射。

### Q: 如何添加新的组件类型？
A: 在服务端添加组件构建方法，在客户端添加对应的渲染逻辑。

## 进阶主题

### 1. 多租户支持

```python
class MultiTenantMUPServer(MUPServer):
    def __init__(self):
        super().__init__()
        self.tenant_configs = {}
    
    async def handle_client(self, websocket, path):
        tenant_id = self.extract_tenant_id(path)
        config = self.tenant_configs.get(tenant_id)
        # 使用租户特定配置
```

### 2. 权限控制

```python
class PermissionHandler:
    def check_component_access(self, user_id: str, component_type: str) -> bool:
        user_permissions = self.get_user_permissions(user_id)
        return component_type in user_permissions.allowed_components
```

### 3. 国际化支持

```javascript
class I18nMUPClient extends MUPClient {
    constructor(options) {
        super(options);
        this.locale = options.locale || 'zh-CN';
        this.translations = options.translations || {};
    }
    
    translateText(text) {
        return this.translations[this.locale]?.[text] || text;
    }
}
```

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 发起Pull Request

## 许可证

MIT License - 详见项目根目录的LICENSE文件。

## 联系方式

- 项目主页：https://github.com/your-org/mup
- 问题反馈：https://github.com/your-org/mup/issues
- 邮件联系：mup-dev@example.com