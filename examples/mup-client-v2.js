/**
 * MUP Client 2.0 - 基于 MCP 设计理念的增强客户端
 * 
 * 主要特性：
 * 1. 标准化能力发现和协商
 * 2. 增强的错误处理和重连机制
 * 3. 批量操作支持
 * 4. 上下文保持和状态同步
 * 5. 性能优化和缓存机制
 */

class MUPClientV2 {
    constructor(options = {}) {
        this.serverUrl = options.serverUrl || 'ws://localhost:8080';
        this.clientInfo = {
            name: options.clientName || 'MUP Client v2.0',
            version: '2.0.0',
            capabilities: {
                rendering_targets: ['web'],
                supported_events: ['click', 'input', 'change', 'submit'],
                max_component_depth: 10,
                concurrent_updates: true,
                mcp_integration: false
            }
        };
        
        this.context = {
            user_id: options.userId || 'user_' + Date.now(),
            session_id: options.sessionId || 'session_' + Date.now(),
            preferences: {
                theme: 'light',
                language: 'zh-CN',
                accessibility: {
                    high_contrast: false,
                    screen_reader: false
                }
            }
        };
        
        this.websocket = null;
        this._connected = false;
        this.clientId = null;
        this.serverCapabilities = null;
        this.messageHandlers = new Map();
        this.pendingMessages = new Map();
        this.componentCache = new Map();
        this.eventListeners = new Map();
        
        // 重连配置
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        // 性能监控
        this.performanceMetrics = {
            messagesSent: 0,
            messagesReceived: 0,
            averageLatency: 0,
            connectionUptime: 0
        };
        
        this._setupMessageHandlers();
    }
    
    /**
     * 设置消息处理器
     */
    _setupMessageHandlers() {
        this.messageHandlers.set('handshake_response', this._handleHandshakeResponse.bind(this));
        this.messageHandlers.set('capability_response', this._handleCapabilityResponse.bind(this));
        this.messageHandlers.set('component_update', this._handleComponentUpdate.bind(this));
        this.messageHandlers.set('error', this._handleError.bind(this));
    }
    
    /**
     * 连接到服务器
     */
    async connect() {
        return new Promise((resolve, reject) => {
            try {
                this.websocket = new WebSocket(this.serverUrl);
                
                this.websocket.onopen = () => {
                    console.log('MUP Client v2.0 已连接到服务器');
                    this._connected = true;
                    this.reconnectAttempts = 0;
                    this._sendHandshake();
                    resolve();
                };
                
                this.websocket.onmessage = (event) => {
                    this._handleMessage(event.data);
                };
                
                this.websocket.onclose = (event) => {
                    console.log('与服务器的连接已关闭:', event.code, event.reason);
                    this._connected = false;
                    this._handleDisconnection();
                };
                
                this.websocket.onerror = (error) => {
                    console.error('WebSocket 错误:', error);
                    reject(error);
                };
                
            } catch (error) {
                reject(error);
            }
        });
    }
    
    /**
     * 发送握手消息
     */
    _sendHandshake() {
        const handshakeMessage = {
            mup: {
                version: '2.0.0',
                message_type: 'handshake_request',
                message_id: this._generateMessageId(),
                timestamp: new Date().toISOString(),
                payload: {
                    client_info: this.clientInfo,
                    context: this.context
                }
            }
        };
        
        this._sendMessage(handshakeMessage);
    }
    
    /**
     * 处理握手响应
     */
    _handleHandshakeResponse(payload) {
        this.clientId = payload.client_id;
        this.serverCapabilities = payload.capabilities;
        
        console.log('握手成功，客户端 ID:', this.clientId);
        console.log('服务器能力:', this.serverCapabilities);
        
        // 触发连接成功事件
        this._emit('connected', {
            clientId: this.clientId,
            serverCapabilities: this.serverCapabilities
        });
    }
    
    /**
     * 查询服务器能力
     */
    async queryCapabilities(filters = {}) {
        const queryMessage = {
            mup: {
                version: '2.0.0',
                message_type: 'capability_query',
                message_id: this._generateMessageId(),
                timestamp: new Date().toISOString(),
                payload: {
                    query_type: 'component_availability',
                    filters: filters
                }
            }
        };
        
        return this._sendMessageWithResponse(queryMessage);
    }
    
    /**
     * 处理能力查询响应
     */
    _handleCapabilityResponse(payload) {
        console.log('服务器能力查询结果:', payload);
        return payload;
    }
    
    /**
     * 批量操作
     */
    async batchOperation(operations, options = {}) {
        const batchMessage = {
            mup: {
                version: '2.0.0',
                message_type: 'batch_operation',
                message_id: this._generateMessageId(),
                timestamp: new Date().toISOString(),
                payload: {
                    operations: operations,
                    execution_mode: options.executionMode || 'sequential',
                    rollback_on_error: options.rollbackOnError || false
                }
            }
        };
        
        return this._sendMessageWithResponse(batchMessage);
    }
    
    /**
     * 发送事件通知
     */
    async sendEvent(componentId, eventType, eventData = {}) {
        const eventMessage = {
            mup: {
                version: '2.0.0',
                message_type: 'event_notification',
                message_id: this._generateMessageId(),
                timestamp: new Date().toISOString(),
                payload: {
                    component_id: componentId,
                    event_type: eventType,
                    event_data: eventData,
                    handler: this._getEventHandler(componentId, eventType)
                }
            }
        };
        
        return this._sendMessageWithResponse(eventMessage);
    }
    
    /**
     * 获取事件处理器名称
     */
    _getEventHandler(componentId, eventType) {
        const component = this.componentCache.get(componentId);
        if (component && component.events && component.events[eventType]) {
            return component.events[eventType].handler;
        }
        return null;
    }
    
    /**
     * 处理组件更新
     */
    _handleComponentUpdate(payload) {
        console.log('收到组件更新:', payload);
        
        // 处理批量操作结果
        if (payload.batch_results) {
            this._handleBatchResults(payload.batch_results);
            return;
        }
        
        // 处理 UI 更新
        if (payload.ui_updates) {
            payload.ui_updates.forEach(component => {
                this._updateComponent(component);
            });
        }
        
        // 处理单个组件更新
        if (payload.component_id) {
            this._updateComponent(payload);
        }
        
        // 触发更新事件
        this._emit('componentUpdate', payload);
    }
    
    /**
     * 处理批量操作结果
     */
    _handleBatchResults(results) {
        results.forEach((result, index) => {
            if (result.error) {
                console.error(`批量操作 ${index} 失败:`, result.error);
            } else {
                console.log(`批量操作 ${index} 成功:`, result);
            }
        });
    }
    
    /**
     * 更新组件
     */
    _updateComponent(component) {
        // 缓存组件
        this.componentCache.set(component.id, component);
        
        // 渲染组件
        this._renderComponent(component);
        
        // 绑定事件
        this._bindComponentEvents(component);
    }
    
    /**
     * 渲染组件
     */
    _renderComponent(component) {
        const container = document.getElementById('mup-container') || document.body;
        
        switch (component.type) {
            case 'form':
                this._renderForm(component, container);
                break;
            case 'data_table':
                this._renderDataTable(component, container);
                break;
            case 'notification':
                this._renderNotification(component, container);
                break;
            default:
                console.warn('未知的组件类型:', component.type);
        }
    }
    
    /**
     * 渲染表单组件
     */
    _renderForm(component, container) {
        const formElement = document.createElement('form');
        formElement.id = component.id;
        formElement.className = 'mup-form';
        
        // 添加表单字段
        component.props.fields.forEach(field => {
            const fieldContainer = document.createElement('div');
            fieldContainer.className = 'mup-field';
            
            const label = document.createElement('label');
            label.textContent = field.label;
            label.setAttribute('for', field.name);
            
            let input;
            if (field.type === 'textarea') {
                input = document.createElement('textarea');
            } else {
                input = document.createElement('input');
                input.type = field.type;
            }
            
            input.id = field.name;
            input.name = field.name;
            input.placeholder = field.placeholder || '';
            input.required = field.required || false;
            
            fieldContainer.appendChild(label);
            fieldContainer.appendChild(input);
            formElement.appendChild(fieldContainer);
        });
        
        // 添加提交按钮
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.textContent = '提交';
        submitButton.className = 'mup-submit-button';
        formElement.appendChild(submitButton);
        
        // 替换或添加表单
        const existingForm = document.getElementById(component.id);
        if (existingForm) {
            container.replaceChild(formElement, existingForm);
        } else {
            container.appendChild(formElement);
        }
    }
    
    /**
     * 渲染数据表格组件
     */
    _renderDataTable(component, container) {
        const tableContainer = document.createElement('div');
        tableContainer.id = component.id;
        tableContainer.className = 'mup-table-container';
        
        const table = document.createElement('table');
        table.className = 'mup-table';
        
        // 创建表头
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        
        component.props.columns.forEach(column => {
            const th = document.createElement('th');
            th.textContent = column.title;
            th.dataset.key = column.key;
            
            if (column.sortable) {
                th.className = 'sortable';
                th.style.cursor = 'pointer';
            }
            
            headerRow.appendChild(th);
        });
        
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // 创建表体
        const tbody = document.createElement('tbody');
        
        component.props.data.forEach((row, index) => {
            const tr = document.createElement('tr');
            tr.dataset.index = index;
            
            component.props.columns.forEach(column => {
                const td = document.createElement('td');
                td.textContent = row[column.key] || '';
                tr.appendChild(td);
            });
            
            tbody.appendChild(tr);
        });
        
        table.appendChild(tbody);
        tableContainer.appendChild(table);
        
        // 替换或添加表格
        const existingTable = document.getElementById(component.id);
        if (existingTable) {
            container.replaceChild(tableContainer, existingTable);
        } else {
            container.appendChild(tableContainer);
        }
    }
    
    /**
     * 渲染通知组件
     */
    _renderNotification(component, container) {
        const notification = document.createElement('div');
        notification.id = component.id;
        notification.className = `mup-notification mup-notification-${component.props.type}`;
        
        const message = document.createElement('span');
        message.textContent = component.props.message;
        notification.appendChild(message);
        
        if (component.props.closable) {
            const closeButton = document.createElement('button');
            closeButton.textContent = '×';
            closeButton.className = 'mup-notification-close';
            notification.appendChild(closeButton);
        }
        
        // 添加到通知容器
        let notificationContainer = document.getElementById('mup-notifications');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'mup-notifications';
            notificationContainer.className = 'mup-notifications';
            document.body.appendChild(notificationContainer);
        }
        
        notificationContainer.appendChild(notification);
        
        // 自动关闭
        if (component.props.duration > 0) {
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, component.props.duration);
        }
    }
    
    /**
     * 绑定组件事件
     */
    _bindComponentEvents(component) {
        const element = document.getElementById(component.id);
        if (!element) return;
        
        // 移除旧的事件监听器
        this._removeComponentEvents(component.id);
        
        const listeners = [];
        
        if (component.type === 'form') {
            // 表单提交事件
            const submitHandler = (e) => {
                e.preventDefault();
                const formData = new FormData(element);
                const data = Object.fromEntries(formData.entries());
                
                this.sendEvent(component.id, 'on_submit', {
                    form_data: data,
                    component_id: component.id
                });
            };
            
            element.addEventListener('submit', submitHandler);
            listeners.push({ event: 'submit', handler: submitHandler });
            
            // 字段验证事件
            const inputs = element.querySelectorAll('input, textarea');
            inputs.forEach(input => {
                const changeHandler = (e) => {
                    this.sendEvent(component.id, 'on_validate', {
                        field_name: e.target.name,
                        field_value: e.target.value,
                        component_id: component.id
                    });
                };
                
                input.addEventListener('blur', changeHandler);
                listeners.push({ element: input, event: 'blur', handler: changeHandler });
            });
        }
        
        if (component.type === 'data_table') {
            // 行点击事件
            const rows = element.querySelectorAll('tbody tr');
            rows.forEach((row, index) => {
                const clickHandler = (e) => {
                    const rowData = {};
                    const cells = row.querySelectorAll('td');
                    component.props.columns.forEach((column, colIndex) => {
                        rowData[column.key] = cells[colIndex]?.textContent || '';
                    });
                    
                    this.sendEvent(component.id, 'on_row_click', {
                        row_data: rowData,
                        row_index: index,
                        component_id: component.id
                    });
                };
                
                row.addEventListener('click', clickHandler);
                listeners.push({ element: row, event: 'click', handler: clickHandler });
            });
            
            // 排序事件
            const sortableHeaders = element.querySelectorAll('th.sortable');
            sortableHeaders.forEach(header => {
                const sortHandler = (e) => {
                    const column = e.target.dataset.key;
                    const currentDirection = e.target.dataset.sortDirection || 'asc';
                    const newDirection = currentDirection === 'asc' ? 'desc' : 'asc';
                    
                    this.sendEvent(component.id, 'on_sort', {
                        column: column,
                        direction: newDirection,
                        component_id: component.id
                    });
                    
                    e.target.dataset.sortDirection = newDirection;
                };
                
                header.addEventListener('click', sortHandler);
                listeners.push({ element: header, event: 'click', handler: sortHandler });
            });
        }
        
        if (component.type === 'notification') {
            // 关闭事件
            const closeButton = element.querySelector('.mup-notification-close');
            if (closeButton) {
                const closeHandler = (e) => {
                    this.sendEvent(component.id, 'on_close', {
                        component_id: component.id
                    });
                    
                    if (element.parentNode) {
                        element.parentNode.removeChild(element);
                    }
                };
                
                closeButton.addEventListener('click', closeHandler);
                listeners.push({ element: closeButton, event: 'click', handler: closeHandler });
            }
        }
        
        // 保存事件监听器引用
        this.eventListeners.set(component.id, listeners);
    }
    
    /**
     * 移除组件事件监听器
     */
    _removeComponentEvents(componentId) {
        const listeners = this.eventListeners.get(componentId);
        if (listeners) {
            listeners.forEach(({ element, event, handler }) => {
                const target = element || document.getElementById(componentId);
                if (target) {
                    target.removeEventListener(event, handler);
                }
            });
            this.eventListeners.delete(componentId);
        }
    }
    
    /**
     * 处理错误消息
     */
    _handleError(payload) {
        console.error('服务器错误:', payload.error);
        this._emit('error', payload);
    }
    
    /**
     * 处理断开连接
     */
    _handleDisconnection() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            
            console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})，${delay}ms 后重试...`);
            
            setTimeout(() => {
                this.connect().catch(error => {
                    console.error('重连失败:', error);
                });
            }, delay);
        } else {
            console.error('达到最大重连次数，停止重连');
            this._emit('disconnected', { reason: 'max_retries_exceeded' });
        }
    }
    
    /**
     * 处理收到的消息
     */
    _handleMessage(messageStr) {
        try {
            const message = JSON.parse(messageStr);
            const mupData = message.mup;
            
            if (!mupData) {
                console.warn('收到无效的 MUP 消息:', message);
                return;
            }
            
            const messageType = mupData.message_type;
            const payload = mupData.payload;
            const messageId = mupData.message_id;
            
            // 更新性能指标
            this.performanceMetrics.messagesReceived++;
            
            // 处理待响应的消息
            if (this.pendingMessages.has(messageId)) {
                const { resolve } = this.pendingMessages.get(messageId);
                this.pendingMessages.delete(messageId);
                resolve(payload);
                return;
            }
            
            // 处理消息
            const handler = this.messageHandlers.get(messageType);
            if (handler) {
                handler(payload);
            } else {
                console.warn('未知的消息类型:', messageType);
            }
            
        } catch (error) {
            console.error('解析消息时出错:', error);
        }
    }
    
    /**
     * 发送消息
     */
    _sendMessage(message) {
        if (!this._connected || !this.websocket) {
            console.warn('未连接到服务器，无法发送消息');
            return false;
        }
        
        try {
            this.websocket.send(JSON.stringify(message));
            this.performanceMetrics.messagesSent++;
            return true;
        } catch (error) {
            console.error('发送消息时出错:', error);
            return false;
        }
    }
    
    /**
     * 发送消息并等待响应
     */
    _sendMessageWithResponse(message, timeout = 5000) {
        return new Promise((resolve, reject) => {
            const messageId = message.mup.message_id;
            
            // 保存待响应的消息
            this.pendingMessages.set(messageId, { resolve, reject });
            
            // 设置超时
            setTimeout(() => {
                if (this.pendingMessages.has(messageId)) {
                    this.pendingMessages.delete(messageId);
                    reject(new Error('消息响应超时'));
                }
            }, timeout);
            
            // 发送消息
            if (!this._sendMessage(message)) {
                this.pendingMessages.delete(messageId);
                reject(new Error('发送消息失败'));
            }
        });
    }
    
    /**
     * 生成消息 ID
     */
    _generateMessageId() {
        return 'msg_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    /**
     * 事件发射器
     */
    _emit(eventName, data) {
        const event = new CustomEvent(`mup:${eventName}`, { detail: data });
        document.dispatchEvent(event);
    }
    
    /**
     * 添加事件监听器
     */
    on(eventName, handler) {
        document.addEventListener(`mup:${eventName}`, handler);
    }
    
    /**
     * 移除事件监听器
     */
    off(eventName, handler) {
        document.removeEventListener(`mup:${eventName}`, handler);
    }
    
    /**
     * 检查连接状态
     */
    isConnected() {
        return this._connected && this.websocket && this.websocket.readyState === WebSocket.OPEN;
    }
    
    /**
     * 断开连接
     */
    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        this._connected = false;
        this.clientId = null;
        
        // 清理缓存和事件监听器
        this.componentCache.clear();
        this.eventListeners.forEach((listeners, componentId) => {
            this._removeComponentEvents(componentId);
        });
        this.eventListeners.clear();
        this.pendingMessages.clear();
    }
    
    /**
     * 获取性能指标
     */
    getPerformanceMetrics() {
        return { ...this.performanceMetrics };
    }
}

// 导出类
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MUPClientV2;
} else if (typeof window !== 'undefined') {
    window.MUPClientV2 = MUPClientV2;
}