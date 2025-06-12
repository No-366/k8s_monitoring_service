# 노드 기준 : nodes.py에 작성

GET /api/nodes

### 전체 노드 목록 및 리소스 사용량

POST /api/nodes/<node_name>/metrics
Content-Type: application/json

{
  "cpu_millicores": 2300,
  "memory_bytes": 4123456789,
  "disk_io": {
    "read_bytes": 104857600,
    "write_bytes": 524288000
  },
  "network_io": {
    "bytes_sent": 19384728,
    "bytes_recv": 28374612
  }
}

```
[
  {
    "node_name": "node-1",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 2300,
    "memory_bytes": 4123456789,
    "disk_io": {
      "read_bytes": 104857600,
      "write_bytes": 524288000
    },
    "network_io": {
      "bytes_sent": 19384728,
      "bytes_recv": 28374612
    }
  },
  {
    "node_name": "node-2",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 1900,
    "memory_bytes": 3012345678,
    "disk_io": {
      "read_bytes": 80530636,
      "write_bytes": 322122547
    },
    "network_io": {
      "bytes_sent": 10293847,
      "bytes_recv": 11223344
    }
  }
]
```

GET /api/nodes/\<node\>

### 특정 노드의 리소스 사용량

호스트 프로세스의 리소스 사용량도 포함

```
{
  "node_name": "node-1",
  "timestamp": "2025-06-11T15:00:00Z",
  "cpu_millicores": 2300,
  "memory_bytes": 4123456789,
  "disk_io": {
    "read_bytes": 104857600,
    "write_bytes": 524288000
  },
  "network_io": {
    "bytes_sent": 19384728,
    "bytes_recv": 28374612
  }
}
```

GET /api/nodes/\<node\>/pods

### 해당 노드에 할당된 모든 파드 목록 및 리소스 사용량, 파드에 의한 리소스 사용량만 포함

```
[
  {
    "node_name": "node-1",
    "timestamp": "2025-06-11T15:00:00Z",
    "pod_name": "web-server-1",
    "namespace": "default",
    "cpu_millicores": 500,
    "memory_bytes": 528870912,
    "disk_io": {
      "read_bytes": 2048000,
      "write_bytes": 1024000
    },
    "network_io": {
      "bytes_sent": 123456,
      "bytes_recv": 654321
    }
  },
  {
    "node_name": "node-1",
    "timestamp": "2025-06-11T15:00:00Z",
    "pod_name": "app-backend-1",
    "namespace": "default",
    "cpu_millicores": 300,
    "memory_bytes": 1073741824,
    "disk_io": {
      "read_bytes": 4096000,
      "write_bytes": 2048000
    },
    "network_io": {
      "bytes_sent": 234567,
      "bytes_recv": 765432
    }
  }
]
```
---
# 파드 기준 : pods.py에 작성

POST /api/namespaces/<namespace>/pods/<pod_name>/metrics
Content-Type: application/json

{
  "cpu_millicores": 300,
  "memory_bytes": 536870912,
  "node_name": "node-1",
  "disk_io": {
    "read_bytes": 2048000,
    "write_bytes": 1024000
  },
  "network_io": {
    "bytes_sent": 123456,
    "bytes_recv": 654321
  }
}

GET /api/pods

### 해당 클러스터에 존재하는 전체 파드 목록 및 리소스 사용량

```
[
  {
    "namespace": "default",
    "pod_name": "web-server-1",
    "node_name": "node-1",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 300,
    "memory_bytes": 536870912,
    "disk_io": {
      "read_bytes": 2048000,
      "write_bytes": 1024000
    },
    "network_io": {
      "bytes_sent": 123456,
      "bytes_recv": 654321
    }
  },
  {
    "namespace": "default",
    "pod_name": "app-backend-1",
    "node_name": "node-2",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 500,
    "memory_bytes": 1073741824,
    "disk_io": {
      "read_bytes": 4096000,
      "write_bytes": 2048000
    },
    "network_io": {
      "bytes_sent": 234567,
      "bytes_recv": 765432
    }
  }
]
```

GET /api/pods/\<podName\>

### 특정 파드의 실시간 리소스 사용량

```
GET /api/pods/<podName>
[
{
"namespace": "default",
"pod_name": "web-server-1",
"node_name": "node-1",
"timestamp": "2025-06-11T15:00:00Z",
"cpu_millicores": 300,
"memory_bytes": 536870912,
"disk_io": {
"read_bytes": 2048000,
"write_bytes": 1024000
},
"network_io": {
"bytes_sent": 123456,
"bytes_recv": 654321
}
},
{
"namespace": "newNs",
"pod_name": "web-server-1",
"node_name": "node-1",
"timestamp": "2025-06-11T15:00:00Z",
"cpu_millicores": 300,
"memory_bytes": 536870912,
"disk_io": {
"read_bytes": 2048000,
"write_bytes": 1024000
},
"network_io": {
"bytes_sent": 123456,
"bytes_recv": 654321
}
},
]

```

# 네임스페이스 기준 : namespaces.py에 작성

GET /api/namespaces

### 전체 네임스페이스 목록 및 리소스 사용량

```
[
  {
    "namespace": "default",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 1200,
    "memory_bytes": 2147483648,
    "disk_io": {
      "read_bytes": 1024000,
      "write_bytes": 2048000
    },
    "network_io": {
      "bytes_sent": 12345678,
      "bytes_recv": 87654321
    }
  },
  {
    "namespace": "monitoring",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 800,
    "memory_bytes": 1073741824,
    "disk_io": {
      "read_bytes": 512000,
      "write_bytes": 1024000
    },
    "network_io": {
      "bytes_sent": 567890,
      "bytes_recv": 432109
    }
  }
]
```

GET /api/namespaces/\<nsName\>

### 특정 네임스페이스의 리소스 사용량

```
{
  "namespace": "default",
  "timestamp": "2025-06-11T15:00:00Z",
  "cpu_millicores": 1200,
  "memory_bytes": 2147483648,
  "disk_io": {
    "read_bytes": 1024000,
    "write_bytes": 2048000
  },
  "network_io": {
    "bytes_sent": 12345678,
    "bytes_recv": 87654321
  }
}
```

GET /api/namespaces/\<nsName\>/pods

### 해당 네임스페이스의 파드 목록 및 리소스 사용량

```
[
  {
    "namespace": "default",
    "pod_name": "web-server-1",
    "node_name": "node-1",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 300,
    "memory_bytes": 536870912,
    "disk_io": {
      "read_bytes": 2048000,
      "write_bytes": 1024000
    },
    "network_io": {
      "bytes_sent": 123456,
      "bytes_recv": 654321
    }
  },
  {
    "namespace": "default",
    "pod_name": "app-backend-1",
    "node_name": "node-2",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 500,
    "memory_bytes": 1073741824,
    "disk_io": {
      "read_bytes": 4096000,
      "write_bytes": 2048000
    },
    "network_io": {
      "bytes_sent": 234567,
      "bytes_recv": 765432
    }
  }
]
```

# 디플로이먼트 기준 : deployments.py에 작성

GET /api/namespaces/\<nsName\>/deployments

### 특정 네임스페이스의 디플로이먼트 목록 및 리소스 사용량

```
[
  {
    "namespace": "default",
    "deployment_name": "web-server",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 600,
    "memory_bytes": 1073741824,
    "disk_io": {
      "read_bytes": 4096000,
      "write_bytes": 2048000
    },
    "network_io": {
      "bytes_sent": 567890,
      "bytes_recv": 432109
    }
  },
  {
    "namespace": "default",
    "deployment_name": "app-backend",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 800,
    "memory_bytes": 2147483648,
    "disk_io": {
      "read_bytes": 8192000,
      "write_bytes": 4096000
    },
    "network_io": {
      "bytes_sent": 1234567,
      "bytes_recv": 7654321
    }
  }
]
```

GET /api/namespaces/\<nsName\>/deployments/\<dpName\>

### 특정 네임스페이스의 디플로이먼트의 리소스 사용량

```
{
  "namespace": "default",
  "deployment_name": "web-server",
  "timestamp": "2025-06-11T15:00:00Z",
  "cpu_millicores": 600,
  "memory_bytes": 1073741824,
  "disk_io": {
    "read_bytes": 4096000,
    "write_bytes": 2048000
  },
  "network_io": {
    "bytes_sent": 567890,
    "bytes_recv": 432109
  }
}
```

GET /api/namespaces/\<nsName\>/deployments/\<dpName\>/pods

### 특정 네임스페이스의 디플로이먼트의 파드 목록 및 리소스 사용량

```
[
  {
    "namespace": "default",
    "deployment_name": "web-server",
    "pod_name": "web-server-1-abc123",
    "node_name": "node-1",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 300,
    "memory_bytes": 536870912,
    "disk_io": {
      "read_bytes": 2048000,
      "write_bytes": 1024000
    },
    "network_io": {
      "bytes_sent": 123456,
      "bytes_recv": 654321
    }
  },
  {
    "namespace": "default",
    "deployment_name": "web-server",
    "pod_name": "web-server-1-def456",
    "node_name": "node-1",
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 300,
    "memory_bytes": 536870912,
    "disk_io": {
      "read_bytes": 2048000,
      "write_bytes": 1024000
    },
    "network_io": {
      "bytes_sent": 234567,
      "bytes_recv": 765432
    }
  }
]
```



# 시계열 조회 : timeseries.py에 작성

GET /api/nodes/(\<nodeName\>)?window=\<second\>

### 특정 노드 리소스 시계열 조회

```
[
  {
    "node_name": "node-1",
    "timestamp": "2025-06-11T14:59:00Z",
    "cpu_millicores": 1200,
    "memory_bytes": 3216549872,
    "disk_io": {
      "read_bytes": 1048576,
      "write_bytes": 2097152
    },
    "network_io": {
      "bytes_sent": 512000,
      "bytes_recv": 204800
    }
  },
  {
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 1300,
    "memory_bytes": 3250000000,
    "disk_io": {
      "read_bytes": 2097152,
      "write_bytes": 3145728
    },
    "network_io": {
      "bytes_sent": 768000,
      "bytes_recv": 307200
    }
  }
]
```

GET /api/pods/(\<podName\>)?window=\<second\>

### 특정 파드 리소스 시계열 조회

```
[
  {
    "namespace": "default",
    "pod_name": "web-server-1-abc123",
    "timestamp": "2025-06-11T14:59:00Z",
    "cpu_millicores": 200,
    "memory_bytes": 536870912,
    "disk_io": {
      "read_bytes": 1024000,
      "write_bytes": 512000
    },
    "network_io": {
      "bytes_sent": 123456,
      "bytes_recv": 654321
    }
  },
  {
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 220,
    "memory_bytes": 550000000,
    "disk_io": {
      "read_bytes": 1536000,
      "write_bytes": 1024000
    },
    "network_io": {
      "bytes_sent": 223456,
      "bytes_recv": 754321
    }
  }
]
```

GET /api/namespaces/(\<nsName\>)?window=\<second\>

### 특정 네임스페이스 리소스 시계열 조회

```
[
  {
    "timestamp": "2025-06-11T14:59:00Z",
    "cpu_millicores": 800,
    "memory_bytes": 2147483648,
    "disk_io": {
      "read_bytes": 4096000,
      "write_bytes": 2048000
    },
    "network_io": {
      "bytes_sent": 1234567,
      "bytes_recv": 7654321
    }
  },
  {
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 950,
    "memory_bytes": 2300000000,
    "disk_io": {
      "read_bytes": 5120000,
      "write_bytes": 3072000
    },
    "network_io": {
      "bytes_sent": 1434567,
      "bytes_recv": 8054321
    }
  }
]
```

GET /api/namespaces/(\<dpName\>)?window=\<second\>

### 특정 디플로이먼트 리소스 시계열 조회

```
[
  {
    "namespace": "default",
    "deployment_name": "web-server",
    "timestamp": "2025-06-11T14:59:00Z",
    "cpu_millicores": 400,
    "memory_bytes": 1073741824,
    "disk_io": {
      "read_bytes": 2048000,
      "write_bytes": 1024000
    },
    "network_io": {
      "bytes_sent": 567890,
      "bytes_recv": 432109
    }
  },
  {
    "timestamp": "2025-06-11T15:00:00Z",
    "cpu_millicores": 450,
    "memory_bytes": 1100000000,
    "disk_io": {
      "read_bytes": 3072000,
      "write_bytes": 2048000
    },
    "network_io": {
      "bytes_sent": 667890,
      "bytes_recv": 532109
    }
  }
]
```