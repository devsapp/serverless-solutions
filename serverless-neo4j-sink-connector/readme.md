# Neo4jSinkConnectorFramework 帮助文档

<p align="center" class="flex justify-center">
    <a href="https://www.serverless-devs.com" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=Neo4jConnector&type=packageType">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=Neo4jConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=Neo4jConnector&type=packageVersion">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=Neo4jConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=Neo4jConnector&type=packageDownload">
  </a>
</p>

<description>

> ***函数计算 neo4j sink connector***

</description>

## 应用简介
本应用可以将您kafka消息队列的原始输入数据进过预处理之后，写入到您创建应用时填写的 Neo4j 数据库中，支持批量传输及单条数据传输，传输的数据格式支持 cloudEvent Schema 以及自定义格式。
框架由两个函数组成：transform function 及 sink function，框架流程如下图所示：

![流程图](https://img.alicdn.com/imgextra/i1/O1CN01E9a3ZD230u3yoFO84_!!6000000007194-2-tps-2864-1082.png)

Poller Service 从源端拉取数据后，再推送给本应用对应的 Sink Service，最终投递到下游服务中，Sink Service 中包含两个功能函数：
- Transform Function： 数据预处理函数，可自定义预处理逻辑，处理后的源端数据会被发送到 Sink Function 中。
- Sink Function：数据投递函数，接收数据后将其投递到下游服务中。

如果您需要对数据进行转换，可以编写应用创建后的 transform 函数。否则您只需调用 sink 函数即可。


## 前期准备
使用该项目，推荐您拥有以下的产品权限 / 策略：

| 服务/业务 | 函数计算                                                                      |
| --- |---------------------------------------------------------------------------|
| 权限/策略 | AliyunFCFullAccess<br>AliyunLogFullAccess<br> AliyunEventBridgeFullAccess |

<codepre id="codepre">



</codepre>

<deploy>

## 部署 & 体验

<appcenter>

- :fire: 通过 [Serverless 应用中心](https://fcnext.console.aliyun.com/applications/create?template=Neo4jConnector) ，
[![Deploy with Severless Devs](https://img.alicdn.com/imgextra/i1/O1CN01w5RFbX1v45s8TIXPz_!!6000000006118-55-tps-95-28.svg)](https://fcnext.console.aliyun.com/applications/create?template=Neo4jConnector)  该应用。 

</appcenter>

- 通过 [Serverless Devs Cli](https://www.serverless-devs.com/serverless-devs/install) 进行部署：
    - [安装 Serverless Devs Cli 开发者工具](https://www.serverless-devs.com/serverless-devs/install) ，并进行[授权信息配置](https://www.serverless-devs.com/fc/config) ；
    - 初始化项目：`s init Neo4jConnector -d Neo4jConnector`   
    - 进入项目，并进行项目部署：`cd Neo4jConnector && s deploy -y`

</deploy>

<appdetail id="flushContent">


## 使用步骤

### 资源准备
  - 创建Neo4j实例，注意要开启其访问端口
  - 一个可用的Kafka消息队列，可参考消息队列Kafka版官方文档[消息队列快速入门](https://help.aliyun.com/document_detail/99949.html)。

    - 创建VPC专有网络（推荐在生产环境中也使用VPC），可参考[VPC官方文档](https://help.aliyun.com/document_detail/65398.htm?spm=a2c4g.11186623.0.0.61be4c9d4aGfpg#task-1012575)。VPC控制台[链接](https://vpcnext.console.aliyun.com/)。至此即可拥有VPC和相应交换机。

    > 部署Kafka实例时会提示创建可用的VPC专有网络

    - 在Kafka控制台创建需要使用的Kafka Topic与Consumer Group。

### 应用部署

您可以通过应用中心或直接使用 s 工具进行部署。部署之前，需要对函数的环境变量进行如下检查：
- host：目标Neo4j数据库的公网访问地址，e.g: http://xx.xxx.xx.xx
- user 以及 password：确保这两个字段分别为Neo4j的有效用户名及密码，否则不能连接到该Neo4j数据库
- port: 目标Neo4j数据库的访问端口，需要确认数据库所在机器已对该端口入方向放行
- 实例ID (instanceId): 您购买的Kafka实例ID。
- topicName: Kafka实例中某个topic name，此topic的数据生产会触发部署函数，需要您提前创建。
- 消费组 (consumerGroup): 数据由此消费组消费，需要您提前创建。
- 消费位点 (offsetReset): Kafka消费位点，可选择最新位点(latest)或最早位点(earliest)。

>注：由于 user 以及 password 均为敏感信息，因此不建议将应用放到任何代码仓库(Github, Gitee, Gitlab 等)上允许公开访问

### 参数介绍

应用部署完成后，可以构造函数请求参数来对函数发起调用，测试函数的功能正确性。`eventSchema` 为 cloudEvent 且 `batchOrNot` 为 false 时的调用参数[示例](src/event-template/sink-single-event.json)可以参考：

```
{
"data":{
    "type":"xx",
    "name":"xx"
},
"id":"xx",
"source":"acs:mns",
"specversion":"1.0",
"type":"mns:Queue:SendMessage",
"datacontenttype":"application/json; charset\\u003dutf-8",
"time":"xx-xx-xxT00:00:00.000Z",
"subject":"acs:mns:cn-hangzhou:xxxx:queues/xxx",
"aliyunaccountid":"xx"
}
```
`eventSchema` 为 cloudEvent 且 `batchOrNot` 为 true 时，可将批量事件作为函数调用参数，其[示例]((./src/event-template/sink-batch-event.json))可以参考：
```
[
{
"data":{
    "type":"xx",
    "name":"xx"
},
"id":"xx",
"source":"acs:mns",
"specversion":"1.0",
"type":"mns:Queue:SendMessage",
"datacontenttype":"application/json; charset\\u003dutf-8",
"time":"xx-xx-xxT00:00:00.000Z",
"subject":"acs:mns:cn-hangzhou:xxxx:queues/xxx",
"aliyunaccountid":"xx"
},
{
"data":{
    "type":"xx",
    "name":"xx",
},
"id":"xx",
"source":"acs:mns",
"specversion":"1.0",
"type":"mns:Queue:SendMessage",
"datacontenttype":"application/json; charset\\u003dutf-8",
"time":"xx-xx-xxT00:00:00.000Z",
"subject":"acs:mns:cn-hangzhou:xxxx:queues/xxx",
"aliyunaccountid":"xx"
}
]
```

上述参数中的 `data` 中的内容最终会被写入到 Neo4j 数据库中。 

### 应用调用
参数构造完成后，可以通过控制台或者 s 工具进行调用，本文以调用 sink function 为例，对这两种方式进行介绍。

#### 端对端测试（推荐）

  - 登陆Kafka控制台，查看对应实例的对应Topic的`详情`
  - 选择`快速体验消息收发`，发送一个测试消息
  - 登陆到您自己的Neo4j数据库查看是否已经写入数据。

#### 控制台调用

应用部署完成后，按照如下步骤进行在控制台进行函数调用：
1. 进入[函数计算控制台](https://fcnext.console.aliyun.com/cn-hangzhou/services)，找到对应的 sink 函数
2. 进入测试函数页面，将[参数介绍](#参数介绍)中的参数输入事件输入框中，点击测试函数即可。
![函数测试](https://img.alicdn.com/imgextra/i3/O1CN01hcs1S61dBjQUTolNJ_!!6000000003698-0-tps-1996-892.jpg)

#### s 工具调用
应用部署完成后，按照如下步骤进行通过 s 工具进行函数调用：
1. 进入应用项目工程下，在 s.yaml 查找应用初始化时输入的 `batchOrNot` 值，若：
   - `batchOrNot` 为 False：将文件 event-template/sink-single-event.json 中的值修改为目标值后，执行 `s sink invoke --event-file event-template/sink-single-event.json` 进行函数调用
   - `batchOrNot` 为 True：将文件 event-template/sink-batch-event.json 中的值修改为目标值后，执行 `s sink invoke --event-file event-template/sink-batch-event.json` 进行函数调用
2. 函数调用完成后，可以登陆到您自己的Neo4j数据库查看是否已经写入数据。

### 高级功能

#### 自定义数据转储处理逻辑
本应用创建后会生成两个函数：transform 函数及 sink 函数。如果您需要对原始数据进行处理，可以编写 transform 函数中的 transform 方法，以便按照您需要的方式对数据进行预处理。

#### 修改数据库存入点及存入方式
本应用默认将原始数据每条生成一个记录，并将整体 json decode 后存入 data 表中。如果您需要自定义转储方式，可以对 sink 函数 deliver() 方法中的neo4j相关语句进行修改。

</appdetail>

<devgroup>

## 开发者社区

您如果有关于错误的反馈或者未来的期待，您可以在 [Serverless Devs repo Issues](https://github.com/serverless-devs/serverless-devs/issues) 中进行反馈和交流。如果您想要加入我们的讨论组或者了解 FC 组件的最新动态，您可以通过以下渠道进行：

<p align="center">

| <img src="https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1635407298906_20211028074819117230.png" width="130px" > | <img src="https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1635407044136_20211028074404326599.png" width="130px" > | <img src="https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1635407252200_20211028074732517533.png" width="130px" > |
|--- | --- | --- |
| <center>微信公众号：`serverless`</center> | <center>微信小助手：`xiaojiangwh`</center> | <center>钉钉交流群：`33947367`</center> | 

</p>

</devgroup>