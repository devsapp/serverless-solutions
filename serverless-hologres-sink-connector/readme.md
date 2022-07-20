# HologresSinkConnector 帮助文档

<p align="center" class="flex justify-center">
    <a href="https://www.serverless-devs.com" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=HologresSinkConnector&type=packageType">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=HologresSinkConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=HologresSinkConnector&type=packageVersion">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=HologresSinkConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=HologresSinkConnector&type=packageDownload">
  </a>
</p>

<description>

> ***fc hologres sink connector***

</description>

## 应用简介
本应用可以将您的原始输入数据进过预处理之后，写入到您创建应用时填写的 Hologres 数据表中，支持批量传输及单条数据传输，传输的数据格式支持 cloudEvent Shema 以及自定义格式。 

本应用在事件数据传输中主要负责数据的数据预处理以及数据投递，其流程可参考下图：

![简介图](https://img.alicdn.com/imgextra/i1/O1CN01E9a3ZD230u3yoFO84_!!6000000007194-2-tps-2864-1082.png)

Poller Service 从源端拉取数据后，再推送给本应用对应的 Sink Service，最终投递到下游服务中，Sink Service 中包含两个功能函数：
- Transform Function： 数据预处理函数，可自定义预处理逻辑，处理后的源端数据会被发送到 Sink Function 中。
- Sink Function：数据投递函数，接收数据后将其投递到下游服务中。

如果您需要对数据进行转换，可以编写应用创建后的 transform 函数。否则您只需调用 sink 函数即可。


## 前期准备
使用该项目，推荐您拥有以下的产品权限 / 策略：

| 服务/业务 | 函数计算 |     
| --- |  --- |   
| 权限/策略 | AliyunFCFullAccess<br>AliyunLogFullAccess<br>AliyunHologresFullAccess |     

<codepre id="codepre">



</codepre>

<deploy>

## 部署 & 体验

<appcenter>

- :fire: 通过 [Serverless 应用中心](https://fcnext.console.aliyun.com/applications/create?template=HologresSinkConnector) ，
[![Deploy with Severless Devs](https://img.alicdn.com/imgextra/i1/O1CN01w5RFbX1v45s8TIXPz_!!6000000006118-55-tps-95-28.svg)](https://fcnext.console.aliyun.com/applications/create?template=HologresSinkConnector)  该应用。 

</appcenter>

- 通过 [Serverless Devs Cli](https://www.serverless-devs.com/serverless-devs/install) 进行部署：
    - [安装 Serverless Devs Cli 开发者工具](https://www.serverless-devs.com/serverless-devs/install) ，并进行[授权信息配置](https://www.serverless-devs.com/fc/config) ；
    - 初始化项目：`s init HologresSinkConnector -d HologresSinkConnector`   
    - 进入项目，并进行项目部署：`cd HologresSinkConnector && s deploy -y`

</deploy>

<appdetail id="flushContent">

## 使用步骤

### 资源准备

依次创建如下资源：
- hologres 实例
- hologres 数据库，简单权限策略选择默认的简单权限模型（SPM）
  ![新建数据库](https://img.alicdn.com/imgextra/i2/O1CN01RWSiAV1nXqhf4Gnhq_!!6000000005100-2-tps-3562-1436.png)
- hologress 数据表，按需初始化主键以及属性
  ![新建数据表](https://img.alicdn.com/imgextra/i4/O1CN01JvbfOt1Mx2rtpRQWU_!!6000000001500-2-tps-3544-900.png)
  ![初始化字段](https://img.alicdn.com/imgextra/i4/O1CN01JC4md31wUUL4dcJ9H_!!6000000006311-2-tps-3564-1004.png)

### 访问控制

依次进行如下访问控制权限操作：
- 在"实例详情"打开实例的公网访问
  ![公网访问](https://img.alicdn.com/imgextra/i4/O1CN01lTmHHF1DcadSxupLs_!!6000000000237-2-tps-3578-1872.png)
- 进入"数据库管理"页面，在"用户管理"页面新增用户
  ![数据库管理](https://img.alicdn.com/imgextra/i3/O1CN01YdtzbE1iOce8M96Qv_!!6000000004403-2-tps-3578-878.png)
  ![新增用户](https://img.alicdn.com/imgextra/i1/O1CN01rblu9P1qEYsDIRqIg_!!6000000005464-2-tps-3580-1758.png)
- 进入"DB 授权"页面，为之前创建的数据库添加用户授权，保证目标用户有读写权限
  ![DB 授权](https://img.alicdn.com/imgextra/i1/O1CN01fSMIXQ1KIAHRIDrpr_!!6000000001140-2-tps-3576-568.png)
  ![新增授权](https://img.alicdn.com/imgextra/i4/O1CN01T2ZJDL1nnQAWEAWJO_!!6000000005134-2-tps-3548-1302.png)

### 应用部署

您可以通过应用中心或直接使用 s 工具进行部署。部署之前，需要对函数的环境变量进行如下检查：
- user 以及 password：确保这两个字段分别为阿里云用户账号的 AccessKey ID 以及 AccessKey Secret，您可以单击[AccessKey 管理](https://usercenter.console.aliyun.com/?spm=a2c4g.11186623.0.0.3acb24f2utlp5d#/manage/ak)，获取密钥信息
- tableName：是否与目标 hologres 数据表名称匹配
- primaryKeysName：是否与目标 hologres 数据表主键匹配

>注：由于 user 以及 password 均为敏感信息，因此不建议将该项目放到 Github 上并设置为公共读

### 参数介绍

应用部署完成后，可以构造函数请求参数来对函数发起调用，测试函数的功能正确性。`eventSchema` 为 cloudEvent 且 `batchOrNot` 为 false 时的调用参数[示例](src/event-template/sink-single-event.json)可以参考：

```
{
"data":{
    "primaryKey1":"xx",
    "primaryKey2":"xx",
    "colName1":"xx",
    "colName2":"xx"
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
    "primaryKey1":"xx",
    "primaryKey2":"xx",
    "colName1":"xx",
    "colName2":"xx"
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
    "primaryKey1":"xx",
    "primaryKey2":"xx",
    "colName1":"xx",
    "colName2":"xx"
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

上述参数中的 `data` 中的内容最终会被写入到 hologres 数据表中。 

### 应用调用
参数构造完成后，可以通过控制台或者 s 工具进行调用，本文以调用 sink function 为例，对这两种方式进行介绍。

#### 控制台调用

应用部署完成后，按照如下步骤进行在控制台进行函数调用：
1. 进入[函数计算控制台](https://fcnext.console.aliyun.com/cn-hangzhou/services)，找到对应的 sink 函数
2. 进入测试函数页面，将[参数介绍](#参数介绍)中的参数输入事件输入框中，点击测试函数即可。
![函数测试](https://img.alicdn.com/imgextra/i2/O1CN01VWhwGH1Rx70AiHRfr_!!6000000002177-2-tps-3576-1908.png)

#### s 工具调用
应用部署完成后，按照如下步骤进行通过 s 工具进行函数调用：
1. 进入应用项目工程下，在 s.yaml 查找应用初始化时输入的 `batchOrNot` 值，若：
   - `batchOrNot` 为 False：将文件 event-template/sink-single-event.json 中的值修改为目标值后，执行 `s sink invoke --event-file event-template/sink-single-event.json` 进行函数调用
   - `batchOrNot` 为 True：将文件 event-template/sink-batch-event.json 中的值修改为目标值后，执行 `s sink invoke --event-file event-template/sink-batch-event.json` 进行函数调用
2. 函数调用完成后，可以登陆到 [hologres 控制台](https://hologram.console.aliyun.com/cn-hangzhou/overview)查看目标数据表中是否已经写入数据。

### 高级功能

#### 通过不同网络访问 hologres 实例
有如下三种网络访问方式：
- 经典网络访问：通过阿里云内网进行访问，不会产生公网流量，同时安全性也高于公网访问,推荐使用
- 公网访问：函数环境变量中的 endpoint 为公网访问地址时，需要 hologres 开启“公网访问”能力，同时会产生公网流量
- vpc 访问：通过 vpc 网络进行访问，不会产生公网流量，需要为 sink 函数配置 vpc

#### 自定义数据转储处理逻辑
本应用创建后会生成两个函数：transform 函数及 sink 函数。如果您需要对原始数据进行处理，可以编写 transform 函数中的 transform 方法，以便按照您需要的方式对数据进行预处理。

#### 修改数据库存入点及存入方式
本应用默认将原始数据每条生成一个记录，并将整体 json decode 后存入 data 表中。如果您需要自定义转储方式，可以对 sink 函数 deliver() 方法中的 hologres 语句进行修改。



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