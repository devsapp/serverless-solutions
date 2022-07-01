本示例功能：将 kafka 规定消息按结构存储到 adb-mysql 中
前置条件：adb、kafka topic 相关资源创建完成，adb 表创建完成。

本示例操作流程：
1. 在本目录执行下述命令安装依赖：
```bash
$ s build --use-docker
```
2. 执行下述命令部署
```bash
$ s deploy
```


使用 layer 方式：
s layer publish --code ./src/layer.zip --compatible-runtime python3 --description layer --region <regionid>  --layer-name eb-elasticsearch-layer

环境变量说明：
SINK_CONFIG = {
    'host': str,        # ElasticSearch HOST名称
    'port': int,        # ElasticSearch 端口号
    'user': str,        # ElasticSearch 用户名
    'password': str,    # ElasticSearch 用户名对应的密码
    'use_ssl': bool,    # 是否使用 ssl 连接
    'index': str,       # 索引
    'doc_type': str,    # doc 类型
    'id': str,          # 实例 ID
}