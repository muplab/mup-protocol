#!/usr/bin/env python3
"""
MUP (Model UI Protocol) 服务端实现示例
展示如何生成MUP组件并处理客户端事件

安装依赖:
pip install websockets
"""

import json
import asyncio
try:
    import websockets
except ImportError:
    print("请安装websockets: pip install websockets")
    exit(1)
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod


@dataclass
class MUPComponent:
    """MUP组件数据类"""
    id: str
    type: str
    version: str = "1.0.0"
    props: Optional[Dict[str, Any]] = None
    children: Optional[List['MUPComponent']] = None
    events: Optional[Dict[str, Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.props is None:
            self.props = {}
        if self.children is None:
            self.children = []
        if self.events is None:
            self.events = {}
        if self.metadata is None:
            self.metadata = {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "source": "mup-server"
            }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "id": self.id,
            "type": self.type,
            "version": self.version,
            "props": self.props,
            "events": self.events,
            "metadata": self.metadata
        }
        
        if self.children:
            result["children"] = [child.to_dict() for child in self.children]
        
        return result


class ComponentBuilder:
    """组件构建器"""
    
    @staticmethod
    def container(id: str, layout: str = "flex", direction: str = "column", 
                 spacing: int = 16, **kwargs) -> MUPComponent:
        """创建容器组件"""
        props = {
            "layout": layout,
            "direction": direction,
            "spacing": spacing,
            **kwargs
        }
        return MUPComponent(id=id, type="container", props=props)
    
    @staticmethod
    def text(id: str, content: str, variant: str = "body", **kwargs) -> MUPComponent:
        """创建文本组件"""
        props = {
            "content": content,
            "variant": variant,
            **kwargs
        }
        return MUPComponent(id=id, type="text", props=props)
    
    @staticmethod
    def input(id: str, input_type: str = "text", placeholder: str = "", 
             required: bool = False, **kwargs) -> MUPComponent:
        """创建输入组件"""
        props = {
            "input_type": input_type,
            "placeholder": placeholder,
            "value": "",
            "required": required,
            **kwargs
        }
        
        events = {
            "on_change": {
                "handler": f"{id}_change_handler",
                "payload_schema": {
                    "value": "string",
                    "component_id": "string"
                }
            }
        }
        
        return MUPComponent(id=id, type="input", props=props, events=events)
    
    @staticmethod
    def button(id: str, text: str, variant: str = "primary", **kwargs) -> MUPComponent:
        """创建按钮组件"""
        props = {
            "text": text,
            "variant": variant,
            "size": "medium",
            "disabled": False,
            **kwargs
        }
        
        events = {
            "on_click": {
                "handler": f"{id}_click_handler",
                "payload_schema": {
                    "component_id": "string",
                    "timestamp": "string"
                }
            }
        }
        
        return MUPComponent(id=id, type="button", props=props, events=events)


class EventHandler(ABC):
    """事件处理器基类"""
    
    @abstractmethod
    async def handle(self, event_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理事件"""
        pass


class FormValidationHandler(EventHandler):
    """表单验证处理器"""
    
    async def handle(self, event_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        component_id = event_data.get("component_id")
        value = event_data.get("value", "")
        
        # 根据组件ID进行不同的验证
        if component_id and "name" in component_id:
            return self.validate_name(value)
        elif component_id and "email" in component_id:
            return self.validate_email(value)
        elif component_id and "password" in component_id:
            return self.validate_password(value)
        
        return None
    
    def validate_name(self, value: str) -> Dict[str, Any]:
        """验证姓名"""
        if len(value) < 2:
            return {
                "valid": False,
                "message": "姓名至少需要2个字符"
            }
        elif len(value) > 50:
            return {
                "valid": False,
                "message": "姓名不能超过50个字符"
            }
        return {"valid": True}
    
    def validate_email(self, value: str) -> Dict[str, Any]:
        """验证邮箱"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, value):
            return {
                "valid": False,
                "message": "请输入有效的邮箱地址"
            }
        return {"valid": True}
    
    def validate_password(self, value: str) -> Dict[str, Any]:
        """验证密码"""
        import re
        if len(value) < 8:
            return {
                "valid": False,
                "message": "密码至少需要8个字符"
            }
        
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$'
        if not re.match(pattern, value):
            return {
                "valid": False,
                "message": "密码必须包含大小写字母和数字"
            }
        
        return {"valid": True}


class SubmitHandler(EventHandler):
    """提交处理器"""
    
    async def handle(self, event_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        print(f"处理表单提交: {event_data}")
        
        # 这里可以添加实际的业务逻辑
        # 比如保存到数据库、发送邮件等
        
        return {
            "success": True,
            "message": "注册成功！",
            "redirect": "/dashboard"
        }


class MUPServer:
    """MUP服务器"""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.clients: Dict[str, Any] = {}
        self.event_handlers: Dict[str, EventHandler] = {}
        self.component_trees: Dict[str, MUPComponent] = {}
        
        # 注册默认事件处理器
        self.register_handler("validation", FormValidationHandler())
        self.register_handler("submit", SubmitHandler())
    
    def register_handler(self, name: str, handler: EventHandler):
        """注册事件处理器"""
        self.event_handlers[name] = handler
    
    async def start_server(self):
        """启动服务器"""
        print(f"MUP服务器启动在 ws://{self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # 永远运行
    
    async def handle_client(self, websocket):
        """处理客户端连接"""
        client_id = str(uuid.uuid4())
        self.clients[client_id] = websocket
        
        print(f"客户端 {client_id} 已连接")
        
        try:
            async for message in websocket:
                await self.handle_message(client_id, json.loads(message))
        except websockets.exceptions.ConnectionClosed:
            print(f"客户端 {client_id} 已断开连接")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]
    
    async def handle_message(self, client_id: str, message: Dict[str, Any]):
        """处理客户端消息"""
        mup_data = message.get("mup", {})
        payload = mup_data.get("payload", {})
        message_type = mup_data.get("message_type")
        
        if message_type == "handshake_request" and payload.get("type") == "handshake":
            await self.handle_handshake(client_id, payload)
        elif message_type == "event_notification" and payload.get("type") == "user_interaction":
            await self.handle_user_interaction(client_id, payload)
        else:
            print(f"未知消息类型: {message_type}")
    
    async def handle_handshake(self, client_id: str, payload: Dict[str, Any]):
        """处理握手"""
        print(f"处理客户端 {client_id} 的握手")
        
        # 发送初始UI
        ui_tree = self.generate_registration_form()
        await self.send_component_tree(client_id, ui_tree)
    
    async def handle_user_interaction(self, client_id: str, payload: Dict[str, Any]):
        """处理用户交互"""
        event = payload.get("event", {})
        component_id = event.get("component_id")
        event_type = event.get("event_type")
        event_payload = event.get("payload", {})
        
        print(f"用户交互: {component_id} - {event_type}")
        
        # 根据事件类型选择处理器
        if "change" in event_type and "validation" in self.event_handlers:
            result = await self.event_handlers["validation"].handle(event_payload, payload.get("context", {}))
            if result:
                await self.send_validation_result(client_id, component_id, result)
        
        elif "click" in event_type and "submit" in component_id:
            # 收集表单数据
            form_data = await self.collect_form_data(client_id)
            result = await self.event_handlers["submit"].handle(form_data, payload.get("context", {}))
            if result:
                await self.send_submit_result(client_id, result)
    
    def generate_registration_form(self) -> MUPComponent:
        """生成注册表单"""
        # 创建表单容器
        form = ComponentBuilder.container(
            id="registration_form",
            layout="flex",
            direction="column",
            spacing=16,
            padding=[24, 24, 24, 24],
            background="#ffffff",
            border={"width": 1, "color": "#e0e0e0", "radius": 8},
            max_width=400
        )
        
        # 添加标题
        title = ComponentBuilder.text(
            id="form_title",
            content="用户注册",
            variant="h2",
            color="#333333",
            align="center",
            weight="bold"
        )
        
        # 添加姓名输入
        name_input = ComponentBuilder.input(
            id="name_field",
            input_type="text",
            placeholder="请输入您的姓名",
            required=True,
            validation={
                "min_length": 2,
                "max_length": 50,
                "error_message": "姓名长度应在2-50个字符之间"
            }
        )
        
        # 添加邮箱输入
        email_input = ComponentBuilder.input(
            id="email_field",
            input_type="email",
            placeholder="请输入您的邮箱地址",
            required=True,
            validation={
                "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                "error_message": "请输入有效的邮箱地址"
            }
        )
        
        # 添加密码输入
        password_input = ComponentBuilder.input(
            id="password_field",
            input_type="password",
            placeholder="请输入密码",
            required=True,
            validation={
                "min_length": 8,
                "pattern": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$",
                "error_message": "密码至少8位，包含大小写字母和数字"
            }
        )
        
        # 添加提交按钮
        submit_button = ComponentBuilder.button(
            id="submit_button",
            text="注册",
            variant="primary",
            size="large"
        )
        
        # 添加登录链接
        login_link = ComponentBuilder.text(
            id="login_link",
            content="已有账户？点击登录",
            variant="caption",
            color="#007bff",
            align="center"
        )
        if login_link.events is None:
            login_link.events = {}
        login_link.events["on_click"] = {
            "handler": "navigate_to_login",
            "payload_schema": {"component_id": "string"}
        }
        
        # 组装表单
        form.children = [title, name_input, email_input, password_input, submit_button, login_link]
        
        return form
    
    async def send_component_tree(self, client_id: str, component: MUPComponent):
        """发送组件树到客户端"""
        message = {
            "mup": {
                "version": "1.0.0",
                "message_id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source": {
                    "type": "server",
                    "id": "mup-server",
                    "version": "1.0.0"
                },
                "message_type": "component_update",
                "payload": {
                    "type": "component_tree_update",
                    "version": "1.0.0",
                    "timestamp": datetime.now().isoformat(),
                    "update_type": "full",
                    "root_component": component.to_dict()
                }
            }
        }
        
        if client_id in self.clients:
            await self.clients[client_id].send(json.dumps(message))
    
    async def send_validation_result(self, client_id: str, component_id: str, result: Dict[str, Any]):
        """发送验证结果"""
        # 这里可以发送增量更新来显示验证状态
        print(f"验证结果 {component_id}: {result}")
    
    async def send_submit_result(self, client_id: str, result: Dict[str, Any]):
        """发送提交结果"""
        if result.get("success"):
            # 可以发送成功页面或重定向指令
            success_message = ComponentBuilder.text(
                id="success_message",
                content=result.get("message", "操作成功！"),
                variant="h3",
                color="#28a745",
                align="center"
            )
            await self.send_component_tree(client_id, success_message)
    
    async def collect_form_data(self, client_id: str) -> Dict[str, Any]:
        """收集表单数据（模拟）"""
        # 在实际实现中，这里应该从客户端状态中获取数据
        return {
            "name": "示例用户",
            "email": "user@example.com",
            "password": "Password123"
        }


class AIFormGenerator:
    """AI表单生成器示例"""
    
    def __init__(self, mup_server: MUPServer):
        self.server = mup_server
    
    async def generate_dynamic_form(self, requirements: str) -> MUPComponent:
        """根据需求生成动态表单"""
        # 这里可以集成实际的AI模型来生成表单
        # 目前返回一个示例表单
        
        if "联系" in requirements or "contact" in requirements.lower():
            return self.generate_contact_form()
        elif "调查" in requirements or "survey" in requirements.lower():
            return self.generate_survey_form()
        else:
            return self.server.generate_registration_form()
    
    def generate_contact_form(self) -> MUPComponent:
        """生成联系表单"""
        form = ComponentBuilder.container(
            id="contact_form",
            layout="flex",
            direction="column",
            spacing=16
        )
        
        title = ComponentBuilder.text("contact_title", "联系我们", "h2")
        name_input = ComponentBuilder.input("contact_name", placeholder="您的姓名")
        email_input = ComponentBuilder.input("contact_email", input_type="email", placeholder="您的邮箱")
        message_input = ComponentBuilder.input("contact_message", input_type="textarea", placeholder="您的消息")
        submit_btn = ComponentBuilder.button("contact_submit", "发送消息")
        
        form.children = [title, name_input, email_input, message_input, submit_btn]
        return form
    
    def generate_survey_form(self) -> MUPComponent:
        """生成调查表单"""
        form = ComponentBuilder.container(
            id="survey_form",
            layout="flex",
            direction="column",
            spacing=16
        )
        
        title = ComponentBuilder.text("survey_title", "用户满意度调查", "h2")
        rating_text = ComponentBuilder.text("rating_label", "请为我们的服务评分：")
        # 这里可以添加更多复杂的组件类型，如单选按钮、复选框等
        
        form.children = [title, rating_text]
        return form


async def main():
    """主函数"""
    server = MUPServer(host="localhost", port=8080)
    
    # 可以添加AI表单生成器
    ai_generator = AIFormGenerator(server)
    
    try:
        await server.start_server()
    except KeyboardInterrupt:
        print("\n服务器已停止")


if __name__ == "__main__":
    asyncio.run(main())