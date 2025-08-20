/**
 * MUP (Model UI Protocol) 客户端实现示例
 * 展示如何渲染MUP组件并处理用户交互
 */

class MUPClient {
  constructor(options = {}) {
    this.version = '1.0.0';
    this.containerId = options.containerId || 'mup-container';
    this.serverUrl = options.serverUrl || 'ws://localhost:8080';
    this.eventHandlers = new Map();
    this.componentCache = new Map();
    this.currentTree = null;
    this.socket = null;
    
    this.init();
  }

  /**
   * 初始化客户端
   */
  init() {
    this.setupWebSocket();
    this.registerDefaultHandlers();
  }

  /**
   * 设置WebSocket连接
   */
  setupWebSocket() {
    this.socket = new WebSocket(this.serverUrl);
    
    this.socket.onopen = () => {
      console.log('MUP客户端已连接到服务器');
      this.sendHandshake();
    };
    
    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.handleServerMessage(message);
    };
    
    this.socket.onclose = () => {
      console.log('MUP连接已断开');
      // 实现重连逻辑
      setTimeout(() => this.setupWebSocket(), 3000);
    };
    
    this.socket.onerror = (error) => {
      console.error('MUP连接错误:', error);
    };
  }

  /**
   * 发送握手消息
   */
  sendHandshake() {
    const handshake = {
      mup: {
        version: this.version,
        message_id: this.generateId(),
        timestamp: new Date().toISOString(),
        source: {
          type: 'client',
          id: 'web-client',
          version: this.version
        },
        message_type: 'handshake_request',
        payload: {
          type: 'handshake',
          capabilities: ['container', 'text', 'input', 'button'],
          context: {
            viewport: {
              width: window.innerWidth,
              height: window.innerHeight,
              device_type: this.getDeviceType()
            },
            render_target: 'web',
            user_agent: navigator.userAgent
          }
        }
      }
    };
    
    this.socket.send(JSON.stringify(handshake));
  }

  /**
   * 处理服务器消息
   */
  handleServerMessage(message) {
    const { mup } = message;
    
    switch (mup.payload.type) {
      case 'component_tree_update':
        this.handleComponentTreeUpdate(mup.payload);
        break;
      case 'incremental_update':
        this.handleIncrementalUpdate(mup.payload);
        break;
      case 'error':
        this.handleError(mup.payload.error);
        break;
      default:
        console.warn('未知消息类型:', mup.payload.type);
    }
  }

  /**
   * 处理组件树更新
   */
  handleComponentTreeUpdate(payload) {
    this.currentTree = payload.root_component;
    this.renderComponent(this.currentTree, this.getContainer());
  }

  /**
   * 处理增量更新
   */
  handleIncrementalUpdate(payload) {
    payload.operations.forEach(op => {
      this.applyOperation(op);
    });
  }

  /**
   * 应用增量操作
   */
  applyOperation(operation) {
    const { op, path, value } = operation;
    const element = this.findElementByPath(path);
    
    switch (op) {
      case 'add':
        this.addComponent(element, value);
        break;
      case 'remove':
        this.removeComponent(element);
        break;
      case 'replace':
        this.replaceComponent(element, value);
        break;
      case 'move':
        this.moveComponent(element, value);
        break;
    }
  }

  /**
   * 渲染组件
   */
  renderComponent(component, parentElement) {
    const element = this.createDOMElement(component);
    
    // 缓存组件
    this.componentCache.set(component.id, {
      component,
      element
    });
    
    // 渲染子组件
    if (component.children && component.children.length > 0) {
      component.children.forEach(child => {
        this.renderComponent(child, element);
      });
    }
    
    parentElement.appendChild(element);
    return element;
  }

  /**
   * 创建DOM元素
   */
  createDOMElement(component) {
    let element;
    
    switch (component.type) {
      case 'container':
        element = this.createContainer(component);
        break;
      case 'text':
        element = this.createText(component);
        break;
      case 'input':
        element = this.createInput(component);
        break;
      case 'button':
        element = this.createButton(component);
        break;
      default:
        console.warn(`不支持的组件类型: ${component.type}`);
        element = document.createElement('div');
    }
    
    // 设置通用属性
    element.setAttribute('data-mup-id', component.id);
    element.setAttribute('data-mup-type', component.type);
    
    // 绑定事件
    this.bindEvents(element, component);
    
    return element;
  }

  /**
   * 创建容器组件
   */
  createContainer(component) {
    const div = document.createElement('div');
    const props = component.props || {};
    
    // 设置布局
    if (props.layout === 'flex') {
      div.style.display = 'flex';
      div.style.flexDirection = props.direction || 'row';
      if (props.spacing) {
        div.style.gap = `${props.spacing}px`;
      }
    } else if (props.layout === 'grid') {
      div.style.display = 'grid';
    }
    
    // 设置样式
    if (props.padding) {
      const [top, right, bottom, left] = props.padding;
      div.style.padding = `${top}px ${right}px ${bottom}px ${left}px`;
    }
    
    if (props.background) {
      div.style.backgroundColor = props.background;
    }
    
    if (props.border) {
      div.style.border = `${props.border.width}px solid ${props.border.color}`;
      div.style.borderRadius = `${props.border.radius}px`;
    }
    
    if (props.max_width) {
      div.style.maxWidth = `${props.max_width}px`;
    }
    
    return div;
  }

  /**
   * 创建文本组件
   */
  createText(component) {
    const props = component.props || {};
    let element;
    
    // 根据变体选择元素类型
    switch (props.variant) {
      case 'h1':
        element = document.createElement('h1');
        break;
      case 'h2':
        element = document.createElement('h2');
        break;
      case 'h3':
        element = document.createElement('h3');
        break;
      default:
        element = document.createElement('p');
    }
    
    element.textContent = props.content || '';
    
    // 设置样式
    if (props.color) {
      element.style.color = props.color;
    }
    
    if (props.align) {
      element.style.textAlign = props.align;
    }
    
    if (props.weight) {
      element.style.fontWeight = props.weight;
    }
    
    if (props.size) {
      element.style.fontSize = `${props.size}px`;
    }
    
    return element;
  }

  /**
   * 创建输入组件
   */
  createInput(component) {
    const props = component.props || {};
    let element;
    
    if (props.input_type === 'textarea') {
      element = document.createElement('textarea');
    } else {
      element = document.createElement('input');
      element.type = props.input_type || 'text';
    }
    
    // 设置属性
    if (props.placeholder) {
      element.placeholder = props.placeholder;
    }
    
    if (props.value !== undefined) {
      element.value = props.value;
    }
    
    if (props.required) {
      element.required = true;
    }
    
    if (props.disabled) {
      element.disabled = true;
    }
    
    // 设置样式
    element.style.padding = '8px 12px';
    element.style.border = '1px solid #ddd';
    element.style.borderRadius = '4px';
    element.style.fontSize = '14px';
    
    return element;
  }

  /**
   * 创建按钮组件
   */
  createButton(component) {
    const button = document.createElement('button');
    const props = component.props || {};
    
    button.textContent = props.text || '';
    
    // 设置样式
    button.style.padding = '8px 16px';
    button.style.border = 'none';
    button.style.borderRadius = '4px';
    button.style.cursor = 'pointer';
    button.style.fontSize = '14px';
    
    // 根据变体设置样式
    switch (props.variant) {
      case 'primary':
        button.style.backgroundColor = '#007bff';
        button.style.color = 'white';
        break;
      case 'secondary':
        button.style.backgroundColor = '#6c757d';
        button.style.color = 'white';
        break;
      default:
        button.style.backgroundColor = '#f8f9fa';
        button.style.color = '#333';
    }
    
    if (props.disabled) {
      button.disabled = true;
      button.style.opacity = '0.6';
      button.style.cursor = 'not-allowed';
    }
    
    return button;
  }

  /**
   * 绑定事件
   */
  bindEvents(element, component) {
    if (!component.events) return;
    
    Object.entries(component.events).forEach(([eventName, eventConfig]) => {
      const domEventName = this.mapMUPEventToDOMEvent(eventName);
      
      element.addEventListener(domEventName, (event) => {
        this.handleComponentEvent(event, component, eventName, eventConfig);
      });
    });
  }

  /**
   * 映射MUP事件到DOM事件
   */
  mapMUPEventToDOMEvent(mupEvent) {
    const mapping = {
      'on_click': 'click',
      'on_change': 'input',
      'on_focus': 'focus',
      'on_blur': 'blur'
    };
    
    return mapping[mupEvent] || mupEvent.replace('on_', '');
  }

  /**
   * 处理组件事件
   */
  handleComponentEvent(domEvent, component, eventName, eventConfig) {
    // 构建事件负载
    const payload = {
      component_id: component.id,
      timestamp: new Date().toISOString()
    };
    
    // 根据事件类型添加特定数据
    if (eventName === 'on_change') {
      payload.value = domEvent.target.value;
    } else if (eventName === 'on_click') {
      payload.mouse_position = [domEvent.clientX, domEvent.clientY];
    }
    
    // 发送事件到服务器
    this.sendEventToServer({
      type: 'user_interaction',
      event: {
        component_id: component.id,
        event_type: eventName,
        payload
      },
      context: this.getCurrentContext()
    });
    
    // 执行本地处理器
    if (this.eventHandlers.has(eventConfig.handler)) {
      const handler = this.eventHandlers.get(eventConfig.handler);
      handler(payload, component);
    }
  }

  /**
   * 发送事件到服务器
   */
  sendEventToServer(eventData) {
    const message = {
      mup: {
        version: this.version,
        message_id: this.generateId(),
        timestamp: new Date().toISOString(),
        source: {
          type: 'client',
          id: 'web-client',
          version: this.version
        },
        message_type: 'event_notification',
        payload: eventData
      }
    };
    
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
    }
  }

  /**
   * 注册默认事件处理器
   */
  registerDefaultHandlers() {
    // 表单验证处理器
    this.eventHandlers.set('validate_name', (payload, component) => {
      const validation = component.props.validation;
      if (validation) {
        const value = payload.value;
        const isValid = value.length >= validation.min_length && 
                       value.length <= validation.max_length;
        
        this.showValidationResult(component.id, isValid, validation.error_message);
      }
    });
    
    this.eventHandlers.set('validate_email', (payload, component) => {
      const validation = component.props.validation;
      if (validation && validation.pattern) {
        const regex = new RegExp(validation.pattern);
        const isValid = regex.test(payload.value);
        
        this.showValidationResult(component.id, isValid, validation.error_message);
      }
    });
    
    this.eventHandlers.set('submit_registration', (payload, component) => {
      // 收集表单数据
      const formData = this.collectFormData();
      console.log('提交注册数据:', formData);
      
      // 这里可以发送到后端API
      // fetch('/api/register', { method: 'POST', body: JSON.stringify(formData) })
    });
  }

  /**
   * 显示验证结果
   */
  showValidationResult(componentId, isValid, errorMessage) {
    const element = document.querySelector(`[data-mup-id="${componentId}"]`);
    if (element) {
      if (isValid) {
        element.style.borderColor = '#28a745';
        this.removeErrorMessage(componentId);
      } else {
        element.style.borderColor = '#dc3545';
        this.showErrorMessage(componentId, errorMessage);
      }
    }
  }

  /**
   * 显示错误消息
   */
  showErrorMessage(componentId, message) {
    this.removeErrorMessage(componentId);
    
    const element = document.querySelector(`[data-mup-id="${componentId}"]`);
    if (element) {
      const errorDiv = document.createElement('div');
      errorDiv.className = 'mup-error-message';
      errorDiv.style.color = '#dc3545';
      errorDiv.style.fontSize = '12px';
      errorDiv.style.marginTop = '4px';
      errorDiv.textContent = message;
      
      element.parentNode.insertBefore(errorDiv, element.nextSibling);
    }
  }

  /**
   * 移除错误消息
   */
  removeErrorMessage(componentId) {
    const element = document.querySelector(`[data-mup-id="${componentId}"]`);
    if (element && element.nextSibling && element.nextSibling.className === 'mup-error-message') {
      element.nextSibling.remove();
    }
  }

  /**
   * 收集表单数据
   */
  collectFormData() {
    const formData = {};
    const inputs = document.querySelectorAll('[data-mup-type="input"]');
    
    inputs.forEach(input => {
      const id = input.getAttribute('data-mup-id');
      formData[id] = input.value;
    });
    
    return formData;
  }

  /**
   * 获取当前上下文
   */
  getCurrentContext() {
    return {
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight
      },
      timestamp: new Date().toISOString(),
      url: window.location.href
    };
  }

  /**
   * 获取容器元素
   */
  getContainer() {
    let container = document.getElementById(this.containerId);
    if (!container) {
      container = document.createElement('div');
      container.id = this.containerId;
      document.body.appendChild(container);
    }
    return container;
  }

  /**
   * 获取设备类型
   */
  getDeviceType() {
    const width = window.innerWidth;
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    return 'desktop';
  }

  /**
   * 生成唯一ID
   */
  generateId() {
    return 'mup_' + Math.random().toString(36).substr(2, 9);
  }

  /**
   * 处理错误
   */
  handleError(error) {
    console.error('MUP错误:', error);
    // 可以显示用户友好的错误消息
  }

  /**
   * 清理资源
   */
  destroy() {
    if (this.socket) {
      this.socket.close();
    }
    this.componentCache.clear();
    this.eventHandlers.clear();
  }
}

// 使用示例
if (typeof window !== 'undefined') {
  // 浏览器环境
  window.MUPClient = MUPClient;
  
  // 自动初始化
  document.addEventListener('DOMContentLoaded', () => {
    const client = new MUPClient({
      containerId: 'mup-app',
      serverUrl: 'ws://localhost:8080/mup'
    });
    
    // 全局访问
    window.mupClient = client;
  });
} else {
  // Node.js环境
  module.exports = MUPClient;
}