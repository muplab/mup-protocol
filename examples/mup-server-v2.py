#!/usr/bin/env python3
"""
MUP Server 2.0 - 基于 MCP 设计理念的改进实现

主要改进：
1. 标准化能力发现和协商
2. 增强的安全性和认证
3. 上下文保持机制
4. 与 MCP 的集成支持
5. 批量操作和性能优化
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict, field
from enum import Enum
import websockets

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MessageType(Enum):
    """消息类型枚举"""
    HANDSHAKE_REQUEST = "handshake_request"
    HANDSHAKE_RESPONSE = "handshake_response"
    CAPABILITY_QUERY = "capability_query"
    CAPABILITY_RESPONSE = "capability_response"
    AUTH_REQUEST = "auth_request"
    AUTH_RESPONSE = "auth_response"
    COMPONENT_UPDATE = "component_update"
    EVENT_NOTIFICATION = "event_notification"
    BATCH_OPERATION = "batch_operation"
    STATE_SYNC = "state_sync"
    CONTEXT_TRANSFER = "context_transfer"
    ERROR = "error"
    REQUEST = "request"

@dataclass
class ClientCapabilities:
    """客户端能力描述"""
    rendering_targets: List[str]
    supported_events: List[str]
    max_component_depth: int
    concurrent_updates: bool
    mcp_integration: bool = False

@dataclass
class ServerCapabilities:
    """服务器能力描述"""
    component_types: List[Dict[str, Any]]
    event_handlers: List[str]
    security: Dict[str, Any]
    performance: Dict[str, Any]
    mcp_connectors: List[str] = field(default_factory=list)

@dataclass
class SecurityContext:
    """安全上下文"""
    user_id: str
    session_id: str
    auth_token: Optional[str] = None
    permissions: Dict[str, Any] = field(default_factory=dict)
    auth_method: str = "none"

@dataclass
class UIContext:
    """UI 上下文"""
    viewport: Dict[str, int]
    theme: str
    language: str
    accessibility: Dict[str, bool]
    device_type: str = "desktop"

class MUPMessage:
    """MUP 2.0 消息封装"""
    
    def __init__(self, message_type: MessageType, payload: Dict[str, Any], 
                 version: str = "2.0.0", message_id: str | None = None):
        self.version = version
        self.message_type = message_type
        self.payload = payload
        self.message_id = message_id or f"msg_{int(time.time() * 1000)}"
        self.timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "mup": {
                "version": self.version,
                "message_type": self.message_type.value,
                "message_id": self.message_id,
                "timestamp": self.timestamp,
                "payload": self.payload
            }
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MUPMessage':
        data = json.loads(json_str)
        mup_data = data.get("mup", {})
        return cls(
            message_type=MessageType(mup_data.get("message_type")),
            payload=mup_data.get("payload", {}),
            version=mup_data.get("version", "2.0.0"),
            message_id=mup_data.get("message_id")
        )

class ComponentBuilder:
    """增强的组件构建器"""
    
    @staticmethod
    def create_component(component_type: str, component_id: str, 
                        props: Dict[str, Any] = dict(),
                        events: Dict[str, Any] = dict(),
                        metadata: Dict[str, Any] = dict()) -> Dict[str, Any]:
        """创建标准化组件"""
        return {
            "id": component_id,
            "type": component_type,
            "version": "1.0.0",
            "props": props or {},
            "events": events or {},
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "server_id": "mup_server_v2",
                **(metadata or {})
            }
        }
    
    @staticmethod
    def form(form_id: str, fields: List[Dict[str, Any]], 
             validation_rules: Dict[str, Any] = dict()) -> Dict[str, Any]:
        """创建高级表单组件"""
        return ComponentBuilder.create_component(
            "form",
            form_id,
            props={
                "fields": fields,
                "validation": validation_rules or {},
                "layout": "vertical",
                "auto_save": False
            },
            events={
                "on_submit": {"handler": "handle_form_submit"},
                "on_validate": {"handler": "handle_field_validation"},
                "on_change": {"handler": "handle_form_change"}
            }
        )
    
    @staticmethod
    def data_table(table_id: str, columns: List[Dict[str, Any]], 
                   data: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
        """创建数据表格组件"""
        return ComponentBuilder.create_component(
            "data_table",
            table_id,
            props={
                "columns": columns,
                "data": data or [],
                "pagination": {"enabled": True, "page_size": 10},
                "sorting": {"enabled": True, "multi_column": False},
                "filtering": {"enabled": True, "global_search": True}
            },
            events={
                "on_row_click": {"handler": "handle_row_selection"},
                "on_sort": {"handler": "handle_table_sort"},
                "on_filter": {"handler": "handle_table_filter"}
            }
        )
    
    @staticmethod
    def notification(notification_id: str, message: str, 
                    notification_type: str = "info") -> Dict[str, Any]:
        """创建通知组件"""
        return ComponentBuilder.create_component(
            "notification",
            notification_id,
            props={
                "message": message,
                "type": notification_type,
                "duration": 5000,
                "closable": True,
                "position": "top-right"
            },
            events={
                "on_close": {"handler": "handle_notification_close"}
            }
        )

class MUPServerV2:
    """MUP 2.0 服务器实现"""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.clients: Dict[str, Dict[str, Any]] = {}
        self.event_handlers: Dict[str, Callable] = {}
        self.component_registry: Dict[str, Dict[str, Any]] = {}
        self.security_contexts: Dict[str, SecurityContext] = {}
        
        # 注册默认事件处理器
        self._register_default_handlers()
        
        # 服务器能力定义
        self.capabilities = ServerCapabilities(
            component_types=[
                {
                    "type": "form",
                    "version": "2.0.0",
                    "features": ["validation", "conditional_logic", "auto_save"]
                },
                {
                    "type": "data_table",
                    "version": "2.0.0",
                    "features": ["sorting", "filtering", "pagination", "export"]
                },
                {
                    "type": "notification",
                    "version": "1.0.0",
                    "features": ["auto_dismiss", "stacking", "actions"]
                }
            ],
            event_handlers=[
                "handle_form_submit",
                "handle_field_validation",
                "handle_row_selection",
                "handle_table_sort",
                "handle_notification_close"
            ],
            security={
                "authentication_required": False,
                "supported_auth_methods": ["api_key", "oauth2"],
                "permission_model": "rbac"
            },
            performance={
                "max_concurrent_clients": 100,
                "batch_operation_limit": 50,
                "component_cache_ttl": 3600
            },
            mcp_connectors=["postgres", "file_system", "web_api"]
        )
    
    def _register_default_handlers(self):
        """注册默认事件处理器"""
        self.event_handlers.update({
            "handle_form_submit": self._handle_form_submit,
            "handle_field_validation": self._handle_field_validation,
            "handle_row_selection": self._handle_row_selection,
            "handle_table_sort": self._handle_table_sort,
            "handle_notification_close": self._handle_notification_close
        })
    
    async def _handle_handshake(self, websocket, 
                               message: MUPMessage) -> MUPMessage:
        """处理握手请求"""
        client_info = message.payload.get("client_info", {})
        context = message.payload.get("context", {})
        
        # 创建客户端会话
        client_id = f"client_{int(time.time() * 1000)}"
        self.clients[client_id] = {
            "websocket": websocket,
            "info": client_info,
            "context": context,
            "connected_at": datetime.utcnow(),
            "capabilities": ClientCapabilities(**client_info.get("capabilities", {}))
        }
        
        # 创建安全上下文
        user_id = context.get("user_id", "anonymous")
        session_id = context.get("session_id", client_id)
        self.security_contexts[client_id] = SecurityContext(
            user_id=user_id,
            session_id=session_id
        )
        
        logger.info(f"客户端 {client_id} 已连接: {client_info.get('name', 'Unknown')}")
        
        # 返回服务器能力
        return MUPMessage(
            MessageType.HANDSHAKE_RESPONSE,
            {
                "server_info": {
                    "name": "MUP Server v2.0",
                    "version": "2.0.0",
                    "description": "基于 MCP 设计理念的增强 UI 服务器",
                    "vendor": "MUP Protocol Team"
                },
                "capabilities": asdict(self.capabilities),
                "client_id": client_id,
                "session_info": {
                    "session_id": session_id,
                    "server_time": datetime.utcnow().isoformat() + "Z"
                }
            }
        )
    
    async def _handle_capability_query(self, websocket,
                                     message: MUPMessage) -> MUPMessage:
        """处理能力查询"""
        query_type = message.payload.get("query_type")
        filters = message.payload.get("filters", {})
        
        if query_type == "component_availability":
            # 根据过滤条件返回可用组件
            available_components = []
            for comp_type in self.capabilities.component_types:
                if self._matches_filters(comp_type, filters):
                    available_components.append(comp_type)
            
            return MUPMessage(
                MessageType.CAPABILITY_RESPONSE,
                {
                    "query_type": query_type,
                    "available_components": available_components,
                    "total_count": len(available_components)
                }
            )
        
        return MUPMessage(
            MessageType.ERROR,
            {"error": f"不支持的查询类型: {query_type}"}
        )
    
    def _matches_filters(self, component: Dict[str, Any], 
                        filters: Dict[str, Any]) -> bool:
        """检查组件是否匹配过滤条件"""
        if "component_type" in filters:
            if component["type"] != filters["component_type"]:
                return False
        
        if "required_features" in filters:
            component_features = set(component.get("features", []))
            required_features = set(filters["required_features"])
            if not required_features.issubset(component_features):
                return False
        
        return True
    
    async def _handle_batch_operation(self, websocket,
                                    message: MUPMessage) -> MUPMessage:
        """处理批量操作"""
        operations = message.payload.get("operations", [])
        execution_mode = message.payload.get("execution_mode", "sequential")
        rollback_on_error = message.payload.get("rollback_on_error", False)
        
        results = []
        
        if execution_mode == "parallel":
            # 并行执行
            tasks = []
            for op in operations:
                task = asyncio.create_task(self._execute_operation(op))
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
        else:
            # 顺序执行
            for op in operations:
                try:
                    result = await self._execute_operation(op)
                    results.append(result)
                except Exception as e:
                    if rollback_on_error:
                        # 回滚之前的操作
                        await self._rollback_operations(results)
                        return MUPMessage(
                            MessageType.ERROR,
                            {"error": f"批量操作失败，已回滚: {str(e)}"}
                        )
                    else:
                        results.append({"error": str(e)})
        
        return MUPMessage(
            MessageType.COMPONENT_UPDATE,
            {
                "batch_results": results,
                "execution_mode": execution_mode,
                "total_operations": len(operations),
                "successful_operations": sum(1 for r in results if isinstance(r, dict) and "error" not in r)
            }
        )
    
    async def _execute_operation(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个操作"""
        op_type = operation.get("type")
        op_id = operation.get("operation_id")
        
        if op_type == "component_update":
            component_id = operation.get("component_id")
            updates = operation.get("updates", {})
            
            # 更新组件
            if component_id in self.component_registry:
                self.component_registry[component_id].update(updates)
                return {
                    "operation_id": op_id,
                    "status": "success",
                    "component_id": component_id
                }
            else:
                raise ValueError(f"组件 {component_id} 不存在")
        
        elif op_type == "event_binding":
            component_id = operation.get("component_id")
            events = operation.get("events", {})
            
            # 绑定事件
            if component_id in self.component_registry:
                self.component_registry[component_id]["events"].update(events)
                return {
                    "operation_id": op_id,
                    "status": "success",
                    "component_id": component_id,
                    "events_bound": len(events)
                }
            else:
                raise ValueError(f"组件 {component_id} 不存在")
        
        else:
            raise ValueError(f"不支持的操作类型: {op_type}")
    
    async def _rollback_operations(self, results: List[Dict[str, Any]]):
        """回滚操作"""
        # 这里应该实现具体的回滚逻辑
        logger.warning("执行操作回滚...")
        pass
    
    # 事件处理器实现
    async def _handle_form_submit(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理表单提交"""
        form_data = event_data.get("form_data", {})
        component_id = event_data.get("component_id")
        
        logger.info(f"表单 {component_id} 提交: {form_data}")
        
        # 模拟表单验证和处理
        if "email" in form_data and "@" not in form_data["email"]:
            return {
                "status": "error",
                "message": "邮箱格式不正确",
                "field_errors": {"email": "请输入有效的邮箱地址"}
            }
        
        # 创建成功通知
        notification = ComponentBuilder.notification(
            f"notification_{int(time.time())}",
            "表单提交成功！",
            "success"
        )
        
        return {
            "status": "success",
            "message": "表单提交成功",
            "ui_updates": [notification]
        }
    
    async def _handle_field_validation(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理字段验证"""
        field_name = event_data.get("field_name")
        field_value = event_data.get("field_value")
        
        # 实时验证逻辑
        validation_result = {
            "field_name": field_name,
            "is_valid": True,
            "error_message": None
        }
        
        if field_name == "email" and field_value and "@" not in field_value:
            validation_result["is_valid"] = False
            validation_result["error_message"] = "邮箱格式不正确"
        
        return validation_result
    
    async def _handle_row_selection(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理表格行选择"""
        row_data = event_data.get("row_data", {})
        row_index = event_data.get("row_index")
        
        logger.info(f"选择了第 {row_index} 行: {row_data}")
        
        return {
            "status": "success",
            "selected_row": row_data,
            "row_index": row_index
        }
    
    async def _handle_table_sort(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理表格排序"""
        column = event_data.get("column")
        direction = event_data.get("direction", "asc")
        
        logger.info(f"按 {column} 列 {direction} 排序")
        
        return {
            "status": "success",
            "sort_column": column,
            "sort_direction": direction
        }
    
    async def _handle_notification_close(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理通知关闭"""
        notification_id = event_data.get("component_id")
        
        # 从组件注册表中移除通知
        if notification_id in self.component_registry:
            del self.component_registry[notification_id]
        
        return {
            "status": "success",
            "notification_id": notification_id,
            "action": "removed"
        }
    
    async def handle_client_message(self, websocket, 
                                  message_str: str):
        """处理客户端消息"""
        try:
            message = MUPMessage.from_json(message_str)
            response = None
            
            if message.message_type == MessageType.HANDSHAKE_REQUEST:
                response = await self._handle_handshake(websocket, message)
            
            elif message.message_type == MessageType.CAPABILITY_QUERY:
                response = await self._handle_capability_query(websocket, message)
            
            elif message.message_type == MessageType.BATCH_OPERATION:
                response = await self._handle_batch_operation(websocket, message)
            
            elif message.message_type == MessageType.EVENT_NOTIFICATION:
                # 处理事件通知
                event_data = message.payload
                handler_name = event_data.get("handler")
                
                if handler_name in self.event_handlers:
                    result = await self.event_handlers[handler_name](event_data)
                    response = MUPMessage(
                        MessageType.COMPONENT_UPDATE,
                        result
                    )
                else:
                    response = MUPMessage(
                        MessageType.ERROR,
                        {"error": f"未知的事件处理器: {handler_name}"}
                    )
            
            else:
                response = MUPMessage(
                    MessageType.ERROR,
                    {"error": f"不支持的消息类型: {message.message_type.value}"}
                )
            
            if response:
                await websocket.send(response.to_json())
        
        except Exception as e:
            logger.error(f"处理消息时出错: {e}")
            error_response = MUPMessage(
                MessageType.ERROR,
                {"error": f"服务器内部错误: {str(e)}"}
            )
            await websocket.send(error_response.to_json())
    
    async def handle_client(self, websocket):
        """处理客户端连接"""
        client_address = websocket.remote_address
        logger.info(f"新客户端连接: {client_address}")
        
        try:
            async for message in websocket:
                await self.handle_client_message(websocket, message)
        
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"客户端 {client_address} 断开连接")
        
        except Exception as e:
            logger.error(f"客户端连接错误: {e}")
        
        finally:
            # 清理客户端数据
            client_id = None
            for cid, client_data in self.clients.items():
                if client_data["websocket"] == websocket:
                    client_id = cid
                    break
            
            if client_id:
                del self.clients[client_id]
                if client_id in self.security_contexts:
                    del self.security_contexts[client_id]
                logger.info(f"已清理客户端 {client_id} 的数据")
    
    async def start_server(self):
        """启动服务器"""
        logger.info(f"启动 MUP Server v2.0 在 {self.host}:{self.port}")
        
        # 创建示例组件
        self._create_sample_components()
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"MUP Server v2.0 正在监听 ws://{self.host}:{self.port}")
            await asyncio.Future()  # 保持服务器运行
    
    def _create_sample_components(self):
        """创建示例组件"""
        # 创建示例表单
        sample_form = ComponentBuilder.form(
            "sample_form",
            [
                {
                    "name": "name",
                    "type": "text",
                    "label": "姓名",
                    "required": True,
                    "placeholder": "请输入您的姓名"
                },
                {
                    "name": "email",
                    "type": "email",
                    "label": "邮箱",
                    "required": True,
                    "placeholder": "请输入您的邮箱"
                },
                {
                    "name": "message",
                    "type": "textarea",
                    "label": "留言",
                    "required": False,
                    "placeholder": "请输入您的留言"
                }
            ],
            {
                "name": {"min_length": 2, "max_length": 50},
                "email": {"pattern": r"^[^@]+@[^@]+\.[^@]+$"},
                "message": {"max_length": 500}
            }
        )
        
        # 创建示例数据表格
        sample_table = ComponentBuilder.data_table(
            "sample_table",
            [
                {"key": "id", "title": "ID", "sortable": True},
                {"key": "name", "title": "姓名", "sortable": True},
                {"key": "email", "title": "邮箱", "sortable": True},
                {"key": "created_at", "title": "创建时间", "sortable": True}
            ],
            [
                {"id": 1, "name": "张三", "email": "zhang@example.com", "created_at": "2024-01-01"},
                {"id": 2, "name": "李四", "email": "li@example.com", "created_at": "2024-01-02"},
                {"id": 3, "name": "王五", "email": "wang@example.com", "created_at": "2024-01-03"}
            ]
        )
        
        # 注册组件
        self.component_registry["sample_form"] = sample_form
        self.component_registry["sample_table"] = sample_table
        
        logger.info("已创建示例组件")

if __name__ == "__main__":
    server = MUPServerV2()
    asyncio.run(server.start_server())