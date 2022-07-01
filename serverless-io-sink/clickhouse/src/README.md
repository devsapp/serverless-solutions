本示例功能：将 kafka 规定消息按结构存储到 clickhouse 中
前置条件：clickhouse、kafka topic 相关资源创建完成，clickhouse表创建完成。

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
s layer publish --code ./src/layer.zip --compatible-runtime python3 --description layer --region <regionid>  --layer-name eb-clickhouse-layer