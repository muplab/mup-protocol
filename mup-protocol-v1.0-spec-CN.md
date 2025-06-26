# Model UI Protocol (MUP) v1.0 正式规范

## 版本信息
- **协议版本**: 1.0.0
- **发布日期**: 2025年6月
- **兼容性**: 基于 WebSocket、HTTP/HTTPS 传输
- **语义化版本**: 遵循 [Semantic Versioning 2.0.0](https://semver.org/)
- **许可证**: MIT License

## 1. 协议概述

### 1.1 目标与愿景

Model UI Protocol (MUP) 是一个开放标准协议，旨在为大语言模型(LLM)和AI应用提供标准化的动态UI生成和交互能力。MUP解决了传统AI应用只能输出文本的限制，使AI能够生成丰富的、交互式的用户界面。

### 1.2 核心原则

1. **标准化**: 提供统一的组件定义和通信协议 <mcreference link="https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design" index="3">3</mcreference>
2. **互操作性**: 确保跨平台、跨框架的兼容性
3. **可扩展性**: 支持自定义组件和功能扩展
4. **安全性**: 内置认证、授权和数据验证机制
5. **性能**: 优化传输效率和渲染性能
6. **向后兼容**: 遵循语义化版本控制，确保平滑升级 <mcreference link="https://www.postman.com/api-platform/api-versioning/" index="1">1</mcreference>

### 1.3 应用场景

- AI助手的动态界面生成
- 智能表单构建器
- 数据可视化工具
- 代码生成器的UI输出
- 多模态AI应用界面

## 2. 架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    MUP Host Applications                │
│           (AI应用、IDE、聊天机器人等)                    │
├─────────────────────────────────────────────────────────┤
│                    MUP Client Layer                    │
│              (协议客户端，处理通信和渲染)                 │
├─────────────────────────────────────────────────────────┤
│                    MUP Server Layer                    │
│         (UI生成服务器，组件管理和事件处理)                │
├─────────────────────────────────────────────────────────┤
│                  Transport Layer                       │
│            (WebSocket, HTTP/HTTPS, IPC)                │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心组件

#### 2.2.1 MUP Client
- **职责**: 连接MUP服务器，渲染UI组件，处理用户交互
- **功能**: 协议通信、组件渲染、事件处理、状态管理

#### 2.2.2 MUP Server
- **职责**: 生成UI组件，处理业务逻辑，管理应用状态
- **功能**: 组件生成、事件响应、数据处理、权限控制

#### 2.2.3 Transport Layer
- **支持协议**: WebSocket (推荐)、HTTP/HTTPS、本地IPC
- **特性**: 双向通信、实时更新、连接管理

## 3. 协议规范

### 3.1 消息格式

所有MUP消息必须遵循以下JSON格式 <mcreference link="https://cryptoapis.io/blog/151-pros-and-cons-of-json-rpc-and-rest-apis-protocols" index="1">1</mcreference>:

```json
{
  "mup": {
    "version": "1.0.0",
    "message_id": "msg_1234567890_abcdef",
    "timestamp": "2024-12-01T12:00:00.000Z",
    "message_type": "request|response|notification|error",
    "source": {
      "type": "client|server",
      "id": "unique_source_id",
      "version": "1.0.0"
    },
    "target": {
      "type": "client|server",
      "id": "unique_target_id"
    },
    "payload": {}
  }
}
```

### 3.2 消息类型

#### 3.2.1 握手协议 (Handshake)

**客户端握手请求**:
```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "handshake_request",
    "message_id": "handshake_001",
    "timestamp": "2024-12-01T12:00:00.000Z",
    "payload": {
      "client_info": {
        "name": "MUP Client",
        "version": "1.0.0",
        "platform": "web|desktop|mobile",
        "capabilities": {
          "rendering_targets": ["web", "native"],
          "supported_events": ["click", "input", "scroll", "resize"],
          "max_component_depth": 20,
          "concurrent_updates": true,
          "batch_operations": true
        }
      },
      "context": {
        "user_id": "user_123",
        "session_id": "session_456",
        "locale": "zh-CN",
        "timezone": "Asia/Shanghai",
        "preferences": {
          "theme": "light|dark|auto",
          "font_size": "small|medium|large",
          "accessibility": {
            "high_contrast": false,
            "screen_reader": false,
            "reduced_motion": false
          }
        }
      }
    }
  }
}
```

**服务器握手响应**:
```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "handshake_response",
    "message_id": "handshake_001",
    "timestamp": "2024-12-01T12:00:01.000Z",
    "payload": {
      "server_info": {
        "name": "MUP Server",
        "version": "1.0.0",
        "description": "动态UI生成服务器",
        "vendor": "MUP Foundation"
      },
      "client_id": "client_789",
      "session_id": "session_456",
      "capabilities": {
        "component_types": [
          {
            "type": "container",
            "version": "1.0.0",
            "features": ["flex_layout", "grid_layout", "responsive"]
          },
          {
            "type": "form",
            "version": "1.0.0",
            "features": ["validation", "conditional_logic", "file_upload"]
          },
          {
            "type": "chart",
            "version": "1.0.0",
            "features": ["interactive", "real_time", "export"]
          }
        ],
        "event_handlers": [
          "form_submit",
          "button_click",
          "input_change",
          "chart_interact"
        ],
        "security": {
          "authentication_required": true,
          "supported_auth_methods": ["bearer_token", "api_key"],
          "permissions_model": "rbac"
        }
      }
    }
  }
}
```

#### 3.2.2 能力查询 (Capability Query)

```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "capability_query",
    "message_id": "query_001",
    "timestamp": "2024-12-01T12:00:02.000Z",
    "payload": {
      "query_type": "component_availability",
      "filters": {
        "component_type": "chart",
        "required_features": ["interactive", "real_time"],
        "data_source_type": "json",
        "min_version": "1.0.0"
      }
    }
  }
}
```

#### 3.2.3 组件更新 (Component Update)

```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "component_update",
    "message_id": "update_001",
    "timestamp": "2024-12-01T12:00:03.000Z",
    "payload": {
      "update_type": "full|partial|incremental",
      "component_tree": {
        "id": "app_root",
        "type": "container",
        "version": "1.0.0",
        "props": {
          "layout": "flex",
          "direction": "column",
          "spacing": 16,
          "padding": [16, 16, 16, 16]
        },
        "children": [
          {
            "id": "header",
            "type": "container",
            "props": {
              "layout": "flex",
              "direction": "row",
              "justify_content": "space-between",
              "align_items": "center"
            },
            "children": []
          }
        ],
        "events": {},
        "metadata": {
          "created_at": "2024-12-01T12:00:03.000Z",
          "updated_at": "2024-12-01T12:00:03.000Z",
          "source": "llm_model_gpt4",
          "version": "1.0.0"
        }
      }
    }
  }
}
```

#### 3.2.4 事件通知 (Event Notification)

```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "event_notification",
    "message_id": "event_001",
    "timestamp": "2024-12-01T12:00:04.000Z",
    "payload": {
      "component_id": "submit_button",
      "event_type": "click",
      "event_data": {
        "mouse_position": [100, 200],
        "modifier_keys": ["ctrl"],
        "timestamp": "2024-12-01T12:00:04.000Z"
      },
      "context": {
        "form_data": {
          "name": "张三",
          "email": "zhangsan@example.com"
        },
        "current_state": "form_filling"
      }
    }
  }
}
```

#### 3.2.5 错误处理 (Error Handling)

```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "error",
    "message_id": "error_001",
    "timestamp": "2024-12-01T12:00:05.000Z",
    "payload": {
      "error": {
        "code": "MUP_COMPONENT_NOT_SUPPORTED",
        "message": "不支持的组件类型",
        "details": {
          "component_type": "unsupported_chart",
          "supported_types": ["container", "text", "input", "button", "form"],
          "request_id": "update_001"
        },
        "recovery_suggestions": [
          "使用支持的组件类型",
          "检查服务器能力列表",
          "更新客户端版本"
        ]
      }
    }
  }
}
```

## 4. 组件规范

### 4.1 通用组件结构

```json
{
  "id": "unique_component_id",
  "type": "component_type",
  "version": "1.0.0",
  "props": {
    "key": "value"
  },
  "children": [],
  "events": {
    "event_name": {
      "handler": "handler_id",
      "payload_schema": {}
    }
  },
  "style": {
    "css_property": "value"
  },
  "metadata": {
    "created_at": "2024-12-01T12:00:00.000Z",
    "updated_at": "2024-12-01T12:00:00.000Z",
    "source": "component_source",
    "tags": ["tag1", "tag2"]
  }
}
```

### 4.2 标准组件类型

#### 4.2.1 容器组件 (Container)

```json
{
  "type": "container",
  "props": {
    "layout": "flex|grid|absolute",
    "direction": "row|column",
    "justify_content": "flex-start|center|flex-end|space-between|space-around",
    "align_items": "flex-start|center|flex-end|stretch",
    "spacing": 16,
    "padding": [8, 16, 8, 16],
    "margin": [0, 0, 0, 0],
    "background_color": "#ffffff",
    "border": {
      "width": 1,
      "color": "#e0e0e0",
      "radius": 4,
      "style": "solid|dashed|dotted"
    },
    "responsive": {
      "breakpoints": {
        "mobile": "<768px",
        "tablet": "768px-1024px",
        "desktop": ">1024px"
      }
    }
  }
}
```

#### 4.2.2 文本组件 (Text)

```json
{
  "type": "text",
  "props": {
    "content": "显示文本",
    "variant": "h1|h2|h3|h4|h5|h6|body|caption|subtitle",
    "color": "#000000",
    "align": "left|center|right|justify",
    "weight": "normal|bold|light|100-900",
    "size": 14,
    "line_height": 1.5,
    "font_family": "system-ui|serif|monospace",
    "decoration": "none|underline|line-through",
    "transform": "none|uppercase|lowercase|capitalize",
    "selectable": true,
    "copyable": false
  }
}
```

#### 4.2.3 输入组件 (Input)

```json
{
  "type": "input",
  "props": {
    "input_type": "text|number|email|password|textarea|select|checkbox|radio|file|date|time|datetime",
    "name": "field_name",
    "label": "字段标签",
    "placeholder": "请输入内容",
    "value": "",
    "default_value": "",
    "required": true,
    "disabled": false,
    "readonly": false,
    "multiple": false,
    "options": [
      {"value": "option1", "label": "选项1"},
      {"value": "option2", "label": "选项2"}
    ],
    "validation": {
      "pattern": "regex_pattern",
      "min_length": 0,
      "max_length": 100,
      "min_value": 0,
      "max_value": 100,
      "custom_validator": "validator_function",
      "error_message": "验证失败提示"
    },
    "autocomplete": "on|off|name|email|username",
    "spellcheck": true
  },
  "events": {
    "on_change": {
      "handler": "input_change_handler",
      "payload_schema": {
        "value": "string",
        "component_id": "string",
        "validation_result": "object"
      }
    },
    "on_focus": {
      "handler": "input_focus_handler"
    },
    "on_blur": {
      "handler": "input_blur_handler"
    }
  }
}
```

#### 4.2.4 按钮组件 (Button)

```json
{
  "type": "button",
  "props": {
    "text": "点击按钮",
    "variant": "primary|secondary|outline|text|danger|success|warning",
    "size": "small|medium|large",
    "disabled": false,
    "loading": false,
    "icon": {
      "name": "icon_name",
      "position": "left|right|top|bottom"
    },
    "full_width": false,
    "tooltip": "按钮提示信息"
  },
  "events": {
    "on_click": {
      "handler": "button_click_handler",
      "payload_schema": {
        "component_id": "string",
        "timestamp": "string",
        "context": "object"
      }
    }
  }
}
```

#### 4.2.5 表单组件 (Form)

```json
{
  "type": "form",
  "props": {
    "title": "表单标题",
    "description": "表单描述",
    "method": "POST|GET|PUT|DELETE",
    "action": "/api/submit",
    "validation_mode": "onSubmit|onChange|onBlur",
    "auto_save": false,
    "reset_on_submit": false
  },
  "children": [
    {
      "type": "input",
      "props": {...}
    }
  ],
  "events": {
    "on_submit": {
      "handler": "form_submit_handler",
      "payload_schema": {
        "form_data": "object",
        "validation_result": "object"
      }
    },
    "on_reset": {
      "handler": "form_reset_handler"
    },
    "on_validate": {
      "handler": "form_validate_handler"
    }
  }
}
```

## 5. 安全性规范

### 5.1 认证机制

#### 5.1.1 Bearer Token认证

```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "auth_request",
    "payload": {
      "auth_method": "bearer_token",
      "credentials": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "Bearer"
      }
    }
  }
}
```

#### 5.1.2 API Key认证

```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "auth_request",
    "payload": {
      "auth_method": "api_key",
      "credentials": {
        "api_key": "mup_key_1234567890abcdef",
        "client_id": "client_123"
      }
    }
  }
}
```

### 5.2 权限控制

```json
{
  "permissions": {
    "ui_generation": {
      "allowed_components": ["container", "text", "input", "button", "form"],
      "restricted_components": ["file_upload", "camera_access", "location_access"],
      "max_component_count": 1000,
      "max_nesting_depth": 20,
      "max_payload_size": "10MB"
    },
    "data_access": {
      "read_user_data": false,
      "write_user_data": false,
      "access_external_apis": true,
      "allowed_domains": ["*.example.com", "api.trusted-service.com"]
    },
    "event_handling": {
      "allowed_events": ["click", "input", "submit", "change"],
      "restricted_events": ["file_access", "system_call", "network_request"]
    }
  }
}
```

### 5.3 数据验证

所有输入数据必须经过严格的JSON Schema验证:

```json
{
  "validation_rules": {
    "component_props": {
      "type": "object",
      "additionalProperties": false,
      "required": ["type", "id"],
      "properties": {
        "type": {
          "type": "string",
          "enum": ["container", "text", "input", "button", "form"]
        },
        "id": {
          "type": "string",
          "pattern": "^[a-zA-Z0-9_-]+$",
          "maxLength": 100
        }
      }
    },
    "event_payload": {
      "type": "object",
      "maxProperties": 50,
      "properties": {
        "component_id": {
          "type": "string",
          "pattern": "^[a-zA-Z0-9_-]+$"
        }
      }
    }
  }
}
```

## 6. 性能优化

### 6.1 批量操作

```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "batch_operation",
    "payload": {
      "operations": [
        {
          "operation_id": "op_1",
          "type": "component_update",
          "component_id": "table_1",
          "updates": {...}
        },
        {
          "operation_id": "op_2",
          "type": "event_binding",
          "component_id": "button_1",
          "events": {...}
        }
      ],
      "execution_mode": "sequential|parallel",
      "rollback_on_error": true,
      "timeout": 30000
    }
  }
}
```

### 6.2 增量更新

```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "incremental_update",
    "payload": {
      "base_version": "1.2.3",
      "target_version": "1.2.4",
      "operations": [
        {
          "op": "add|remove|replace|move|copy|test",
          "path": "/root/children/0",
          "value": {
            "id": "new_component",
            "type": "text",
            "props": {
              "content": "新增文本"
            }
          }
        }
      ]
    }
  }
}
```

### 6.3 缓存策略

```json
{
  "cache_policy": {
    "component_templates": {
      "ttl": 3600,
      "max_size": "100MB",
      "invalidation_triggers": ["schema_change", "permission_update"]
    },
    "user_preferences": {
      "ttl": 86400,
      "storage": "local|session|memory"
    },
    "static_assets": {
      "ttl": 604800,
      "cdn_enabled": true,
      "compression": "gzip|brotli"
    }
  }
}
```

## 7. 错误处理

### 7.1 标准错误代码

| 错误代码 | 描述 | HTTP状态码等价 |
|---------|------|---------------|
| MUP_SUCCESS | 操作成功 | 200 |
| MUP_BAD_REQUEST | 请求格式错误 | 400 |
| MUP_UNAUTHORIZED | 未授权访问 | 401 |
| MUP_FORBIDDEN | 权限不足 | 403 |
| MUP_NOT_FOUND | 资源不存在 | 404 |
| MUP_METHOD_NOT_ALLOWED | 方法不允许 | 405 |
| MUP_CONFLICT | 资源冲突 | 409 |
| MUP_PAYLOAD_TOO_LARGE | 负载过大 | 413 |
| MUP_RATE_LIMIT_EXCEEDED | 请求频率超限 | 429 |
| MUP_INTERNAL_ERROR | 服务器内部错误 | 500 |
| MUP_NOT_IMPLEMENTED | 功能未实现 | 501 |
| MUP_SERVICE_UNAVAILABLE | 服务不可用 | 503 |
| MUP_COMPONENT_NOT_SUPPORTED | 组件类型不支持 | - |
| MUP_VALIDATION_FAILED | 数据验证失败 | - |
| MUP_VERSION_MISMATCH | 版本不匹配 | - |

### 7.2 错误响应格式

```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "error",
    "message_id": "error_001",
    "timestamp": "2024-12-01T12:00:00.000Z",
    "payload": {
      "error": {
        "code": "MUP_VALIDATION_FAILED",
        "message": "组件属性验证失败",
        "details": {
          "component_id": "input_field_1",
          "invalid_properties": ["max_length", "pattern"],
          "validation_errors": [
            {
              "property": "max_length",
              "expected": "number",
              "actual": "string",
              "message": "max_length必须是数字类型"
            }
          ]
        },
        "recovery_suggestions": [
          "检查组件属性类型",
          "参考组件规范文档",
          "使用JSON Schema验证工具"
        ],
        "documentation_url": "https://mup.dev/docs/components/input"
      }
    }
  }
}
```

## 8. 版本控制

### 8.1 语义化版本控制

MUP遵循[Semantic Versioning 2.0.0](https://semver.org/)规范 <mcreference link="https://www.postman.com/api-platform/api-versioning/" index="1">1</mcreference>:

- **主版本号(MAJOR)**: 不兼容的API修改
- **次版本号(MINOR)**: 向后兼容的功能性新增
- **修订号(PATCH)**: 向后兼容的问题修正

### 8.2 版本协商

```json
{
  "mup": {
    "version": "1.0.0",
    "message_type": "version_negotiation",
    "payload": {
      "supported_versions": ["1.0.0", "1.1.0", "1.2.0"],
      "preferred_version": "1.2.0",
      "minimum_version": "1.0.0",
      "deprecated_versions": ["0.9.0"],
      "breaking_changes": {
        "1.0.0": ["移除了过时的组件类型", "更改了事件负载格式"]
      }
    }
  }
}
```

### 8.3 向后兼容性

- **组件向后兼容**: 新版本必须支持旧版本的组件定义
- **事件向后兼容**: 新版本必须能处理旧版本的事件格式
- **渐进增强**: 新功能通过可选属性提供
- **优雅降级**: 不支持的功能应有合理的回退方案

## 9. 扩展性

### 9.1 自定义组件

```json
{
  "type": "custom_chart",
  "namespace": "com.example.charts",
  "version": "1.0.0",
  "schema": {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
      "data": {
        "type": "array",
        "description": "图表数据"
      },
      "chart_type": {
        "type": "string",
        "enum": ["line", "bar", "pie", "scatter"],
        "description": "图表类型"
      },
      "theme": {
        "type": "string",
        "default": "default",
        "description": "图表主题"
      }
    },
    "required": ["data", "chart_type"]
  },
  "renderer": {
    "web": "https://cdn.example.com/chart-renderer.js",
    "native": "com.example.ChartRenderer",
    "fallback": "container"
  },
  "documentation": {
    "url": "https://docs.example.com/chart-component",
    "examples": [
      {
        "title": "基础柱状图",
        "code": "..."
      }
    ]
  }
}
```

### 9.2 插件系统

```json
{
  "plugin": {
    "name": "advanced-forms",
    "version": "1.0.0",
    "description": "高级表单组件插件",
    "author": "Example Corp",
    "license": "MIT",
    "dependencies": {
      "mup": "^1.0.0"
    },
    "components": [
      "date_picker",
      "rich_text_editor",
      "file_uploader"
    ],
    "event_handlers": [
      "advanced_validation",
      "auto_save"
    ],
    "themes": [
      "material_design",
      "bootstrap"
    ],
    "installation": {
      "npm": "npm install @mup/advanced-forms",
      "cdn": "https://cdn.mup.dev/plugins/advanced-forms/1.0.0/"
    }
  }
}
```

## 10. 实现指南

### 10.1 服务端实现要点

1. **组件注册系统**: 管理可用组件类型和版本
2. **事件路由器**: 将UI事件路由到相应处理器
3. **状态管理器**: 维护UI状态与业务状态的同步
4. **权限控制器**: 实施基于角色的访问控制
5. **缓存管理器**: 优化组件和数据的缓存策略

### 10.2 客户端实现要点

1. **协议处理器**: 处理MUP消息的解析和生成
2. **组件渲染引擎**: 将MUP组件转换为本地UI
3. **事件捕获器**: 捕获用户交互并转换为MUP事件
4. **状态同步器**: 处理组件状态的增量更新
5. **错误处理器**: 优雅处理网络和协议错误

### 10.3 性能优化建议

1. **使用WebSocket**: 实现低延迟的双向通信 <mcreference link="https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API" index="2">2</mcreference>
2. **组件懒加载**: 按需加载组件定义和资源
3. **虚拟滚动**: 处理大量数据时使用虚拟滚动技术
4. **diff算法**: 使用高效的diff算法优化更新性能
5. **压缩传输**: 启用gzip或brotli压缩减少传输大小

## 11. 测试规范

### 11.1 单元测试

- 组件渲染测试
- 事件处理测试
- 数据验证测试
- 错误处理测试

### 11.2 集成测试

- 客户端-服务器通信测试
- 多组件交互测试
- 状态同步测试
- 性能基准测试

### 11.3 兼容性测试

- 跨浏览器兼容性
- 不同版本间兼容性
- 移动设备兼容性
- 无障碍访问测试

## 12. 部署指南

### 12.1 生产环境要求

- **服务器**: 支持WebSocket的HTTP服务器
- **负载均衡**: 支持WebSocket的负载均衡器
- **监控**: 实时性能和错误监控
- **日志**: 结构化日志记录
- **安全**: HTTPS/WSS加密传输

### 12.2 扩展性考虑

- **水平扩展**: 支持多实例部署
- **状态管理**: 使用Redis等外部状态存储
- **消息队列**: 处理高并发事件
- **CDN**: 静态资源分发

## 13. 社区与生态

### 13.1 开源贡献

- **GitHub仓库**: https://github.com/mup-protocol/mup
- **贡献指南**: 欢迎社区贡献组件、工具和文档
- **代码规范**: 遵循统一的代码风格和质量标准
- **许可证**: MIT License，鼓励商业和开源使用

### 13.2 生态系统

- **组件市场**: 第三方组件的分发平台
- **开发工具**: IDE插件、调试工具、测试框架
- **模板库**: 常用UI模式的预构建模板
- **培训资源**: 文档、教程、最佳实践指南

## 14. 未来发展

### 14.1 短期目标 (6个月)

- 完善核心组件库
- 发布官方SDK和工具
- 建立社区贡献机制
- 完善文档和示例

### 14.2 中期目标 (1年)

- 支持3D和AR/VR组件
- 集成AI驱动的UI生成
- 建立组件市场生态
- 支持更多编程语言

### 14.3 长期愿景 (2-3年)

- 成为AI应用UI的标准协议
- 支持跨模态交互(语音、手势等)
- 智能化UI优化和个性化
- 与主流AI平台深度集成

---

## 附录

### A. 参考资料

- [WebSocket Protocol RFC 6455](https://tools.ietf.org/html/rfc6455)
- [JSON Schema Specification](https://json-schema.org/)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

### B. 示例代码

完整的示例代码请参考项目仓库中的examples目录。

### C. 变更日志

#### v1.0.0 (2025-06-26)
- 初始正式版本发布
- 定义核心协议规范
- 实现基础组件类型
- 建立安全性和性能标准

---

**协议维护者**: MUP工作组  
**联系方式**: mup@csun.cc
**许可证**: MIT License 
**最后更新**: 2025年6月26日