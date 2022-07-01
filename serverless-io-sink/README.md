# serverless-io-sink

* AnalyticDBMysqlSinkConnector

```
ADB_MYSQL_SINK_CONFIG_SCHEMA = {
    'host': str,        # ADB HOST名称
    'port': int,        # ADB 端口号
    'database': str,    # ADB 连接的数据库
    'user': str,        # ADB 用户名
    'password': str,    # ADB 用户名对应的密码
}
```

* AnalyticDBPostgreSQLSinkConnector

```
ADB_POSTGRESQL_SINK_CONFIG_SCHEMA = {
    'host': str,        # ADB HOST名称
    'port': int,        # ADB 端口号
    'database': str,    # ADB 连接的数据库
    'user': str,        # ADB 用户名
    'password': str,    # ADB 用户名对应的密码
}
```

* SQLServerSinkConnector

```
SQL_SERVER_SINK_CONFIG_SCHEMA = {
    'host': str,        # ADB HOST名称
    'port': int,        # ADB 端口号
    'database': str,    # ADB 连接的数据库
    'user': str,        # ADB 用户名
    'password': str,    # ADB 用户名对应的密码
}
```

* HologresSinkConnector

```
HOLOGRES_SINK_CONFIG_SCHEMA = {
    'host': str,        # Hologres HOST名称
    'port': int,        # Hologres 端口号
    'database': str,    # Hologres 数据库名称
    'user': str,        # Hologres 用户名
    'password': str,    # Hologres 用户名对应的密码
}
```

* ElasticSearchSinkConnector

```
ES_SINK_CONFIG_SCHEMA = {
    'host': str,        # ElasticSearch HOST名称
    'port': int,        # ElasticSearch 端口号
    'user': str,        # ElasticSearch 用户名
    'password': str,    # ElasticSearch 用户名对应的密码
    'use_ssl': bool,    # 是否使用 ssl 连接
    'index': str,       # 索引
    'doc_type': str,    # doc 类型
    'id': str,          # 实例 ID
}
```

* OssSinkConnector

```
OSS_SINK_CONFIG_SCHEMA = {
    'endpoint': 'str',                  # OSS访问域名，例如：https://oss-cn-beijing.aliyuncs.com
    'bucket': 'str',                    # OSS bucket名称
    'object_prefix': 'str',             # OSS object 前缀
}
```

* OtsSinkConnector

```
OTS_SINK_CONFIG_SCHEMA = {
    'endpoint': str,                    # OTS访问域名，例如：http://instance.cn-hangzhou.ots.aliyun.com
    'instance_name': 'str',             # OTS实例名称
    'table_name': 'str',                # OTS表格名称
    'primary_keys_name': list,          # OTS主键列表，用','分割。例如：pk1,pk2
    'rows_name': list,                  # OTS列数据列表，用','分割。例如：data1,data2
}
```

* ClickHouseSinkConnector

```
CLICK_HOUSE_SINK_CONFIG_SCHEMA = {
    'clickhouse_full_url': 'str', # clickhouse全连接URL，例如：clickhouse://admin:password@localhost:9000/default
    'execute_sql': 'str',         # clickhouse执行sql，例如：INSERT INTO test (x) VALUES (%(a)s), (%(b)s)
    'template_params': 'str',     # clickhouse sql参数模板，例如：{"a": "{{ message.id }}", "b": "{{ message.data }}"}
}
```
