# Zectrix API Reference

> Auto-generated from https://cloud.zectrix.com/home/api-docs
> Base URL: `https://cloud.zectrix.com/open/v1/`
> Auth: `X-API-Key: zt_your_key_here`

---

## Table of Contents

- [Devices](#devices)
- [Todos](#todos)
- [Display](#display)

---

## Devices

### List Devices

```http
GET /devices
```

**Headers:**
```
X-API-Key: zt_your_key_here
```

**Response:**
```json
{
  "code": 0,
  "data": [
    {
      "deviceId": "AA:BB:CC:DD:EE:FF",
      "alias": "我的设备",
      "board": "bread-compact-wifi"
    }
  ]
}
```

---

## Todos

### List Todos

```http
GET /todos
```

**Query Parameters:**

| Name | Type | Description |
|------|------|-------------|
| status | int | Filter by status: 0=pending, 1=completed |
| deviceId | string | Filter by device MAC address |

**Response:**
```json
{
  "code": 0,
  "data": [
    {
      "id": 1,
      "title": "买牛奶",
      "description": "",
      "dueDate": "2026-03-20",
      "dueTime": "09:00",
      "repeatType": "none",
      "status": 0,
      "priority": 1,
      "completed": false,
      "deviceId": "AA:BB:CC:DD:EE:FF",
      "deviceName": "我的设备",
      "createDate": "2026-03-18 10:00:00",
      "updateDate": 1742284800
    }
  ]
}
```

### Create Todo

```http
POST /todos
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "title": "买牛奶",
    "status": 0,
    "priority": 1,
    "deviceId": "AA:BB:CC:DD:EE:FF",
    "createDate": "2026-03-18 10:00:00"
  }
}
```

### Update Todo

```http
PUT /todos/{id}
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "id": 1,
    "title": "买牛奶和面包",
    "status": 0,
    "priority": 1
  }
}
```

### Toggle Complete

```http
PUT /todos/{id}/complete
```

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| id | int | Todo ID (required) |

**Response:**
```json
{ "code": 0, "msg": "success" }
```

### Delete Todo

```http
DELETE /todos/{id}
```

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| id | int | Todo ID (required) |

**Response:**
```json
{ "code": 0, "msg": "success" }
```

---

## Display

### Push Image

```http
POST /devices/{deviceId}/display/image
```

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| deviceId | string | Device MAC address |

**Form Data:**

| Name | Type | Description |
|------|------|-------------|
| images | file | Image files, up to 5 images, max 2MB each (required) |
| dither | boolean | Use dithering algorithm (default true). Disable for hard threshold |
| pageId | int | Page number (1-5). Persistent storage if specified |

**Response:**
```json
{
  "code": 0,
  "data": {
    "totalPages": 1,
    "pushedPages": 1,
    "pageId": "1"
  }
}
```

### Push Text

```http
POST /devices/{deviceId}/display/text
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "totalPages": 1,
    "pushedPages": 1,
    "pageId": "1"
  }
}
```

### Push Structured Text (Title + Body)

```http
POST /devices/{deviceId}/display/structured-text
```

**Response:**
```json
{
  "code": 0,
  "data": {
    "totalPages": 1,
    "pushedPages": 1,
    "pageId": "1"
  }
}
```

### Delete Page(s)

```http
DELETE /devices/{deviceId}/display/pages/{pageId}
```

**Path Parameters:**

| Name | Type | Description |
|------|------|-------------|
| deviceId | string | Device MAC address (required) |
| pageId | int | Page number. Omit to delete all pages |

**Response:**
```json
{ "code": 0, "msg": "success" }
```
