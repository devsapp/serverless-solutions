# ETLSinkConnectorFramework 帮助文档

<p align="center" class="flex justify-center">
    <a href="https://www.serverless-devs.com" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=KafkaToOSSConnector&type=packageType">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=KafkaToOSSConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=KafkaToOSSConnector&type=packageVersion">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=KafkaToOSSConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=KafkaToOSSConnector&type=packageDownload">
  </a>
</p>

<description>

> ***ETL Sink Connector Framework***

</description>

## 应用简介
本应用为通用 serverless fc sink connector 框架。该框架适用于事件传输/数据处理流程中的预处理及投递功能。
框架由两个函数组成：transform function 及 sink function，框架流程如下图所示：

![流程图](https://img.alicdn.com/imgextra/i1/O1CN01E9a3ZD230u3yoFO84_!!6000000007194-2-tps-2864-1082.png)

Poller Service 从源端拉取数据后，再推送给本应用对应的 Sink Service，最终投递到下游服务中，Sink Service 中包含两个功能函数：
- Transform Function： 数据预处理函数，可自定义预处理逻辑，处理后的源端数据会被发送到 Sink Function 中。
- Sink Function：数据投递函数，接收数据后将其投递到下游服务中。

本应用为框架应用，面向应用开发者。请勿直接发布本应用。


## 前期准备
使用该项目，推荐您拥有以下的产品权限 / 策略：

| 服务/业务 | 函数计算 |     
| --- |  --- |   
| 权限/策略 | AliyunFCFullAccess<br>AliyunLogFullAccess |     

<codepre id="codepre">



</codepre>

<deploy>

## 部署 & 体验

<appcenter>

- :fire: 通过 [Serverless 应用中心](https://fcnext.console.aliyun.com/applications/create?template=KafkaToOSSConnector) ，
[![Deploy with Severless Devs](https://img.alicdn.com/imgextra/i1/O1CN01w5RFbX1v45s8TIXPz_!!6000000006118-55-tps-95-28.svg)](https://fcnext.console.aliyun.com/applications/create?template=KafkaToOSSConnector)  该应用。 

</appcenter>

- 通过 [Serverless Devs Cli](https://www.serverless-devs.com/serverless-devs/install) 进行部署：
    - [安装 Serverless Devs Cli 开发者工具](https://www.serverless-devs.com/serverless-devs/install) ，并进行[授权信息配置](https://www.serverless-devs.com/fc/config) ；
    - 初始化项目：`s init KafkaToOSSConnector -d KafkaToOSSConnector`   
    - 进入项目，并进行项目部署：`cd KafkaToOSSConnector && s deploy -y`

</deploy>

<appdetail id="flushContent">


## 使用步骤

1. git clone Sink Connector 应用框架：http://gitlab.alibaba-inc.com/serverless/serverless-solutions
2. 将框架中 sink-connector-framework 目录拷贝到需要进行开发的位置；其中 transform 目录无需进行任何修改，需要对于 sink 目录下的函数代码文件按照业务需求进行修改：
  a. Sink 部分需要针对数据处理目标特性，优化错误处理；对于无明确错误码的 Open API 基于 Http Code 进行错误处理及重试；
  b. Sink 部分代码注释完善：要求每个函数都有注释，每个类都有注释；
  c. 丰富 Sink 部分日志；
3. 修改 publish.yaml ，按照应用的需要参数填写用户创建应用时的必填参数。具体可参考：https://github.com/Serverless-Devs/Serverless-Devs/discussions/439
4. 进行测试。建议通过 EB 侧已经创建的应用进行测试。

#### 常用命令

应用中心支持的常用命令
s cli registry -h
s cli registry publish
s cli registry delete --name-version ETLFramework@0.0.1 --type Application

本地测试应用
s init ETLFramework
s deploy -t s.yaml
s sink deploy -t s.yaml
s remove -y

应用文档编写：
在publish.yaml目录下，执行 s cli alireadme

#### 开发规范
##### 函数接口 Schema

参考本文开篇架构图，其中涉及函数间及函数与外部系统的交互有以下几处：
1. Connector - FC Transform 函数；
2. Connector - FC Sink 函数；
3. FC Transform 函数 - FC Sink 函数。

为方便统一，我们规定这三种交互方式的数据结构有两类：
1. 标准的 cloud event 事件（推荐模式）：
```json
{
    "data":{
        "requestId":"62BF1AFC31373136413A6AB2",
        "messageId":"EF755211AE83630D7FD1052A357D556F",
        "messageBody":"I am test message"
    },
    "id":"EF755211AE83630D7FD1052A357D556F",
    "source":"acs:mns",
    "specversion":"1.0",
    "type":"mns:Queue:SendMessage",
    "datacontenttype":"application/json; charset\\u003dutf-8",
    "time":"2022-07-01T16:04:12.286Z",
    "subject":"acs:mns:cn-hangzhou:1026899168480100:queues/liuxia-mns-fc-0629-v2",
    "aliyunaccountid":"1026899168480100"
}
```

2. custom 事件：
string 等类型。custom 事件主要是为了支持 EventBridge 的事件内容转换功能，支持任意格式的事件内容。

##### 函数对外透露参数规范
由于 Sink 包含不同的目标，所以需要用户在创建 sink 前填写对应服务的相关参数。我们规定 Sink 函数所需要的参数统一设计为使用 SINK_CONFIG 一个环境变量。用户在前端分开填写所需参数，之后由我们的 Publish.yaml 规定参数的传入。如：
```
SINK_CONFIG: {
  "access_key": "xxx",
  "access_secret": "xxx",
  "bucket": "xxx",
  "object_prefix": "xxx"
}

```


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