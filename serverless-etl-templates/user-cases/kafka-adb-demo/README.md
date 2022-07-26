本示例功能：将 kafka 规定消息按结构存储到 adb-mysql 或 adb-postgre 中
前置条件：adb、kafka topic 相关资源创建完成，adb 表创建完成。

本示例操作流程：
1. 首先在 kafka 控制台创建一个 etl 任务（随便一个任务）
2. 在本目录同级创建一个临时目录，并 cd 到该目录下。执行
```bash
$ s cli fc sync --region cn-shanghai --service-name {kafka 创建的 serviceName} --function-name {kafka 创建的 functionName} --access default
```
同步下函数，此时 s 会创建一个目录 'A'
3. cp 本目录下的 code/requirements.txt 到 sync 下来的函数目录 A 中
4. 参考 s_demo.yaml, 修改 A/s.yaml 中的 code 路径为相对路径
5. 在本目录执行下述命令安装依赖：
```bash
$ s build --use-docker
```
6. 将 code/index.py 中代码内容贴到目录 A 的函数代码 index.py 中

7. 执行下述命令部署
```bash
$ s deploy
```
8. 测试：
可以在 kafka etl 页面直接发送数据。注意：key kafka_log（可以在代码中改动）

后续优化内容：
1. 将本模板集成到 kafka 控制台中。目标不再为 kafka topic，而是 'mysql' 类型（支持 adb，是否支持其他 mysql 如 rds 需验证）
（1）支持填写 endpoint、port、account、secret 和 vpcID、vswID、securityGroupID，这些作为环境变量，由函数执行时读取
2. 集成后，产出一篇 kafka to mysql 最佳实践文档；