# Model UI Protocol (MUP) v1.0 Official Specification

## Version Information
- **Protocol Version**: 1.0.0
- **Release Date**: June 2025
- **Compatibility**: Based on WebSocket, HTTP/HTTPS transport
- **Semantic Versioning**: Follows [Semantic Versioning 2.0.0](https://semver.org/)
- **License**: MIT License

## 1. Protocol Overview

### 1.1 Goals and Vision

Model UI Protocol (MUP) is an open standard protocol designed to provide standardized dynamic UI generation and interaction capabilities for Large Language Models (LLM) and AI applications. MUP addresses the limitations of traditional AI applications that can only output text, enabling AI to generate rich, interactive user interfaces.

### 1.2 Core Principles

1. **Standardization**: Provide unified component definitions and communication protocols
2. **Interoperability**: Ensure cross-platform and cross-framework compatibility
3. **Extensibility**: Support custom components and feature extensions
4. **Security**: Built-in authentication, authorization, and data validation mechanisms
5. **Performance**: Optimize transmission efficiency and rendering performance
6. **Backward Compatibility**: Follow semantic versioning to ensure smooth upgrades

### 1.3 Application Scenarios

- Dynamic interface generation for AI assistants
- Intelligent form builders
- Data visualization tools
- UI output for code generators
- Multimodal AI application interfaces

## 2. Architecture Design

### 2.1 Overall Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MUP Host Applications                │
│         (AI Apps, IDEs, Chatbots, etc.)                │
├─────────────────────────────────────────────────────────┤
│                    MUP Client Layer                    │
│        (Protocol client, handles communication         │
│                   and rendering)                       │
├─────────────────────────────────────────────────────────┤
│                    MUP Server Layer                    │
│      (UI generation server, component management       │
│                 and event handling)                    │
├─────────────────────────────────────────────────────────┤
│                  Transport Layer                       │
│            (WebSocket, HTTP/HTTPS, IPC)                │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Core Components

#### 2.2.1 MUP Client
- **Responsibilities**: Connect to MUP server, render UI components, handle user interactions
- **Functions**: Protocol communication, component rendering, event handling, state management

#### 2.2.2 MUP Server
- **Responsibilities**: Generate UI components, handle business logic, manage application state
- **Functions**: Component generation, event response, data processing, permission control

#### 2.2.3 Transport Layer
- **Supported Protocols**: WebSocket (recommended), HTTP/HTTPS, local IPC
- **Features**: Bidirectional communication, real-time updates, connection management

## 3. Protocol Specification

### 3.1 Message Format

All MUP messages must follow the following JSON format:

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

### 3.2 Message Types

#### 3.2.1 Handshake Protocol

**Client Handshake Request**:
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
        "locale": "en-US",
        "timezone": "America/New_York",
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

**Server Handshake Response**:
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
        "description": "Dynamic UI Generation Server",
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

#### 3.2.2 Capability Query

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

#### 3.2.3 Component Update

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

#### 3.2.4 Event Notification

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
          "name": "John Doe",
          "email": "john.doe@example.com"
        },
        "current_state": "form_filling"
      }
    }
  }
}
```

#### 3.2.5 Error Handling

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
        "message": "Unsupported component type",
        "details": {
          "component_type": "unsupported_chart",
          "supported_types": ["container", "text", "input", "button", "form"],
          "request_id": "update_001"
        },
        "recovery_suggestions": [
          "Use supported component types",
          "Check server capability list",
          "Update client version"
        ]
      }
    }
  }
}
```

## 4. Component Specification

### 4.1 Common Component Structure

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

### 4.2 Standard Component Types

#### 4.2.1 Container Component

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

#### 4.2.2 Text Component

```json
{
  "type": "text",
  "props": {
    "content": "Display text",
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

#### 4.2.3 Input Component

```json
{
  "type": "input",
  "props": {
    "input_type": "text|number|email|password|textarea|select|checkbox|radio|file|date|time|datetime",
    "name": "field_name",
    "label": "Field Label",
    "placeholder": "Please enter content",
    "value": "",
    "default_value": "",
    "required": true,
    "disabled": false,
    "readonly": false,
    "multiple": false,
    "options": [
      {"value": "option1", "label": "Option 1"},
      {"value": "option2", "label": "Option 2"}
    ],
    "validation": {
      "pattern": "regex_pattern",
      "min_length": 0,
      "max_length": 100,
      "min_value": 0,
      "max_value": 100,
      "custom_validator": "validator_function",
      "error_message": "Validation failed message"
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

#### 4.2.4 Button Component

```json
{
  "type": "button",
  "props": {
    "text": "Click Button",
    "variant": "primary|secondary|outline|text|danger|success|warning",
    "size": "small|medium|large",
    "disabled": false,
    "loading": false,
    "icon": {
      "name": "icon_name",
      "position": "left|right|top|bottom"
    },
    "full_width": false,
    "tooltip": "Button tooltip information"
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

#### 4.2.5 Form Component

```json
{
  "type": "form",
  "props": {
    "title": "Form Title",
    "description": "Form Description",
    "method": "POST|GET|PUT|DELETE",
    "action": "/api/submit",
    "validation_mode": "onSubmit|onChange|onBlur",
    "auto_save": false,
    "reset_on_submit": false
  },
  "children": [
    {
      "type": "input",
      "props": {}
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

## 5. Security Specification

### 5.1 Authentication Mechanisms

#### 5.1.1 Bearer Token Authentication

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

#### 5.1.2 API Key Authentication

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

### 5.2 Permission Control

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

### 5.3 Data Validation

All input data must undergo strict JSON Schema validation:

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

## 6. Performance Optimization

### 6.1 Batch Operations

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
          "updates": {}
        },
        {
          "operation_id": "op_2",
          "type": "event_binding",
          "component_id": "button_1",
          "events": {}
        }
      ],
      "execution_mode": "sequential|parallel",
      "rollback_on_error": true,
      "timeout": 30000
    }
  }
}
```

### 6.2 Incremental Updates

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
              "content": "New text content"
            }
          }
        }
      ]
    }
  }
}
```

### 6.3 Caching Strategy

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

## 7. Error Handling

### 7.1 Standard Error Codes

| Error Code | Description | HTTP Status Code Equivalent |
|------------|-------------|-----------------------------|
| MUP_SUCCESS | Operation successful | 200 |
| MUP_BAD_REQUEST | Request format error | 400 |
| MUP_UNAUTHORIZED | Unauthorized access | 401 |
| MUP_FORBIDDEN | Insufficient permissions | 403 |
| MUP_NOT_FOUND | Resource not found | 404 |
| MUP_METHOD_NOT_ALLOWED | Method not allowed | 405 |
| MUP_CONFLICT | Resource conflict | 409 |
| MUP_PAYLOAD_TOO_LARGE | Payload too large | 413 |
| MUP_RATE_LIMIT_EXCEEDED | Request rate limit exceeded | 429 |
| MUP_INTERNAL_ERROR | Internal server error | 500 |
| MUP_NOT_IMPLEMENTED | Feature not implemented | 501 |
| MUP_SERVICE_UNAVAILABLE | Service unavailable | 503 |
| MUP_COMPONENT_NOT_SUPPORTED | Component type not supported | - |
| MUP_VALIDATION_FAILED | Data validation failed | - |
| MUP_VERSION_MISMATCH | Version mismatch | - |

### 7.2 Error Response Format

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
        "message": "Component property validation failed",
        "details": {
          "component_id": "input_field_1",
          "invalid_properties": ["max_length", "pattern"],
          "validation_errors": [
            {
              "property": "max_length",
              "expected": "number",
              "actual": "string",
              "message": "max_length must be a number type"
            }
          ]
        },
        "recovery_suggestions": [
          "Check component property types",
          "Refer to component specification documentation",
          "Use JSON Schema validation tools"
        ],
        "documentation_url": "https://mup.dev/docs/components/input"
      }
    }
  }
}
```

## 8. Version Control

### 8.1 Semantic Version Control

MUP follows [Semantic Versioning 2.0.0](https://semver.org/) specification:

- **Major Version (MAJOR)**: Incompatible API changes
- **Minor Version (MINOR)**: Backward-compatible functional additions
- **Patch Version (PATCH)**: Backward-compatible bug fixes

### 8.2 Version Negotiation

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
        "1.0.0": ["Removed deprecated component types", "Changed event payload format"]
      }
    }
  }
}
```

### 8.3 Backward Compatibility

- **Component Backward Compatibility**: New versions must support old version component definitions
- **Event Backward Compatibility**: New versions must handle old version event formats
- **Progressive Enhancement**: New features provided through optional attributes
- **Graceful Degradation**: Unsupported features should have reasonable fallback solutions

## 9. Extensibility

### 9.1 Custom Components

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
        "description": "Chart data"
      },
      "chart_type": {
        "type": "string",
        "enum": ["line", "bar", "pie", "scatter"],
        "description": "Chart type"
      },
      "theme": {
        "type": "string",
        "default": "default",
        "description": "Chart theme"
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
        "title": "Basic Bar Chart",
        "code": "..."
      }
    ]
  }
}
```

### 9.2 Plugin System

```json
{
  "plugin": {
    "name": "advanced-forms",
    "version": "1.0.0",
    "description": "Advanced form components plugin",
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

## 10. Implementation Guide

### 10.1 Server-side Implementation Points

1. **Component Registration System**: Manage available component types and versions
2. **Event Router**: Route UI events to appropriate handlers
3. **State Manager**: Maintain synchronization between UI state and business state
4. **Permission Controller**: Implement role-based access control
5. **Cache Manager**: Optimize caching strategies for components and data

### 10.2 Client-side Implementation Points

1. **Protocol Handler**: Handle parsing and generation of MUP messages
2. **Component Rendering Engine**: Convert MUP components to native UI
3. **Event Capturer**: Capture user interactions and convert to MUP events
4. **State Synchronizer**: Handle incremental updates of component state
5. **Error Handler**: Gracefully handle network and protocol errors

### 10.3 Performance Optimization Recommendations

1. **Use WebSocket**: Implement low-latency bidirectional communication
2. **Component Lazy Loading**: Load component definitions and resources on demand
3. **Virtual Scrolling**: Use virtual scrolling techniques when handling large amounts of data
4. **Diff Algorithm**: Use efficient diff algorithms to optimize update performance
5. **Compressed Transmission**: Enable gzip or brotli compression to reduce transmission size

## 11. Testing Specification

### 11.1 Unit Testing

- Component rendering tests
- Event handling tests
- Data validation tests
- Error handling tests

### 11.2 Integration Testing

- Client-server communication tests
- Multi-component interaction tests
- State synchronization tests
- Performance benchmark tests

### 11.3 Compatibility Testing

- Cross-browser compatibility
- Inter-version compatibility
- Mobile device compatibility
- Accessibility testing

## 12. Deployment Guide

### 12.1 Production Environment Requirements

- **Server**: HTTP server supporting WebSocket
- **Load Balancer**: Load balancer supporting WebSocket
- **Monitoring**: Real-time performance and error monitoring
- **Logging**: Structured logging
- **Security**: HTTPS/WSS encrypted transmission

### 12.2 Scalability Considerations

- **Horizontal Scaling**: Support multi-instance deployment
- **State Management**: Use external state storage like Redis
- **Message Queue**: Handle high-concurrency events
- **CDN**: Static resource distribution

## 13. Community and Ecosystem

### 13.1 Open Source Contribution

- **GitHub Repository**: https://github.com/mup-protocol/mup
- **Contribution Guidelines**: Welcome community contributions of components, tools, and documentation
- **Code Standards**: Follow unified code style and quality standards
- **License**: MIT License, encouraging commercial and open source use

### 13.2 Ecosystem

- **Component Marketplace**: Distribution platform for third-party components
- **Development Tools**: IDE plugins, debugging tools, testing frameworks
- **Template Library**: Pre-built templates for common UI patterns
- **Training Resources**: Documentation, tutorials, best practice guides

## 14. Future Development

### 14.1 Short-term Goals (6 months)

- Improve core component library
- Release official SDK and tools
- Establish community contribution mechanisms
- Improve documentation and examples

### 14.2 Medium-term Goals (1 year)

- Support 3D and AR/VR components
- Integrate AI-driven UI generation
- Build component marketplace ecosystem
- Support more programming languages

### 14.3 Long-term Vision (2-3 years)

- Become the standard protocol for AI application UI
- Support cross-modal interactions (voice, gestures, etc.)
- Intelligent UI optimization and personalization
- Deep integration with mainstream AI platforms

---

## Appendix

### A. References

- [WebSocket Protocol RFC 6455](https://tools.ietf.org/html/rfc6455)
- [JSON Schema Specification](https://json-schema.org/)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [OAuth 2.0 Authorization Framework](https://tools.ietf.org/html/rfc6749)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)

### B. Example Code

For complete example code, please refer to the examples directory in the project repository.

### C. Changelog

#### v1.0.0 (2025-06-26)
- Initial official version release
- Define core protocol specifications
- Implement basic component types
- Establish security and performance standards

---

**Protocol Maintainers**: MUP Working Group  
**Contact**: mup@csun.cc  
**License**: MIT License  
**Last Updated**: June 26, 2025