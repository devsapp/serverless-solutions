# ODPSSinkConnector 帮助文档

<p align="center" class="flex justify-center">
    <a href="https://www.serverless-devs.com" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=ODPSSinkConnector&type=packageType">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=ODPSSinkConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=ODPSSinkConnector&type=packageVersion">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=ODPSSinkConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=ODPSSinkConnector&type=packageDownload">
  </a>
</p>

<description>

> ***函数计算(FC) -> ODPS(MaxCompute) Sink Connector Framework***

</description>

<table>

## 应用简介
本应用可以将您的原始输入数据经过预处理之后，传输到您的 ODPS(MaxCompute) 数据表中。 

本应用在事件数据传输中主要负责数据的数据预处理以及数据投递，其流程可参考下图：

![简介图](https://img.alicdn.com/imgextra/i1/O1CN01E9a3ZD230u3yoFO84_!!6000000007194-2-tps-2864-1082.png)

Poller Service 从源端拉取数据后，再推送给本应用对应的 Sink Service，最终投递到下游服务中，Sink Service 中包含两个功能函数：
- Transform Function： 数据预处理函数，可自定义预处理逻辑，处理后的源端数据会被发送到 Sink Function 中。
- Sink Function：数据投递函数，接收数据后将其投递到下游服务中。

如果您需要对数据进行转换，可以编写应用创建后的 transform 函数。否则您只需调用 sink 函数即可。

## 前期准备

### 权限准备

使用该项目，推荐您拥有以下的产品权限 / 策略：


| 服务/业务 | 函数计算 |     
| --- |  --- |   
| 权限/策略 | AliyunFCFullAccess</br>AliyunDataWorksFullAccess</br>AliyunBSSOrderAccess |     


</table>

### 资源准备

  * 1: 开通 ODPS(MaxCompute) 服务。
  * 2: 创建 ODPS 项目资源。**（如果您已经创建完成或有可以直接使用的项目资源，可跳过此步。）**
    * 2-1: 进入 ODPS 控制台首页，点击**创建项目**。
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/52a09da0785fa1a473953c2a3598d57c/image.png)
    * 2-2: 填写**工作空间名称**，其他选项如无特殊需求可略过，完成后点击**创建项目**。 
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/eadd3641a31f7e03c3b6577f39e480c0/image.png)
    * 2-3: 填写**实例显示名称**，其他选项如无特殊需求可略过，完成后点击**确认创建**，此时创建 odps 项目的过程就完成了。
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/4c0669d9eadb8cb1706294e21eb35920/image.png)
  * 3: 创建 ODPS 数据表资源。**（如果您已经创建完成或有可以直接使用的数据表资源，可跳过此步。）**
    * 3-1: 进入 ODPS 控制台首页，选择 step2 创建的项目，并点击**数据开发**。
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/4c122d3042ca9ebca83cb96df43081a8/image.png)
    * 3-2: 右键点击下图的**业务流程**，点击新建业务流程，并按照要求填写，此 demo 创建的业务流程名称为**fc_odps_sink_v1**。
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/c704ead1235f64dc05d55ee032a224bf/image.png)
    * 3-3: 点击**新建**->**新建表**->**表**，配置表名称和业务路径，点击完成即进入到表配置页面。
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/aa6d7c21f7923f5bc1e3b09e281ae9f6/image.png)
    * 3-4: 按下图设置中文名和表字段，完成后提交到生产环境。（注意：表字段是有序的，例如此 demo 表字段的顺序是 id,name,age。）
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/4ddcba884fcb5247dbd5c222e781297d/image.png)
    * 3-5: 点击左侧的**表管理**，刷新一下页面即可看到刚刚创建的数据表，此时创建 odps 数据表的过程就完成了。
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/4b33ca9d55e94007c9cfbfee73a418ac/image.png)

<codepre id="codepre">



</codepre>

<deploy>

## 使用步骤
### 应用部署

<appcenter>

- :fire: 通过 [Serverless 应用中心](https://fcnext.console.aliyun.com/applications/create?template=ODPSSinkConnector) ，
[![Deploy with Severless Devs](https://img.alicdn.com/imgextra/i1/O1CN01w5RFbX1v45s8TIXPz_!!6000000006118-55-tps-95-28.svg)](https://fcnext.console.aliyun.com/applications/create?template=ODPSSinkConnector)  该应用。 

</appcenter>

- 通过 [Serverless Devs Cli](https://www.serverless-devs.com/serverless-devs/install) 进行部署：
    - [安装 Serverless Devs Cli 开发者工具](https://www.serverless-devs.com/serverless-devs/install) ，并进行[授权信息配置](https://www.serverless-devs.com/fc/config) ；
    - 初始化项目：`s init ODPSSinkConnector -d ODPSSinkConnector`   
    - 进入项目，并进行项目部署：`cd ODPSSinkConnector && s deploy -y`

</deploy>

无论通过上面哪种方式部署，都需要为应用配置参数，具体如下：
  * batchOrNot: 是否批处理事件。为 False 时，会将单条事件消息作为函数入参发起调用；为 True 时，会将多条事件消息聚合后作为函数入参；
  * accessKeyID/accessKeySecret: 账户的 ak 密钥对，用于在函数中访问 ODPS(MaxCompute)。
  * odpsProject: ODPS(MaxCompute) 项目名称，需要字母开头，只能包含字母、下划线和数字。
  * odpsEndpoint: ODPS(MaxCompute) 服务地址，如无特殊需求可选择外网访问地址，地址详见：https://help.aliyun.com/document_detail/34951.html。
  * odpsTableName: ODPS(MaxCompute) 数据表名称。
  * odpsTableColumnsOrder: 按顺序输入 ODPS(MaxCompute) 数据表列名，多个列名之间使用 "," 分隔，例上文资源准备创建的数据表可填写: id,name,age。

### 应用调用
**调用参数**

应用部署完成后，可构造函数请求参数来对函数发起调用，测试函数正确性。eventSchema 为 cloudEvent 且 batchOrNot 为 false 时的调用参数示例可以参考：
```
{
    "data":{
        "id": 1,
        "name": "xiaoming",
        "age": 11
    },
    "id":"EF755211AE83630D7FD1052A357D556F",
    "source":"acs:mns",
    "specversion":"1.0",
    "type":"mns:Queue:SendMessage",
    "datacontenttype":"application/json; charset\\u003dutf-8",
    "time":"2022-07-01T16:04:12.286Z",
    "subject":"acs:mns:cn-hangzhou:xxx:queues/queueName",
    "aliyunaccountid":"xxx"
}
```
eventSchema 为 cloudEvent 且 batchOrNot 为 true 时，可将批量事件作为函数调用参数，其示例可以参考：
```
[
  {
    "data":{
        "id": 1,
        "name": "xiaoming",
        "age": 11
    },
    "id":"EF755211AE83630D7FD1052A357D556F",
    "source":"acs:mns",
    "specversion":"1.0",
    "type":"mns:Queue:SendMessage",
    "datacontenttype":"application/json; charset\\u003dutf-8",
    "time":"2022-07-01T16:04:12.286Z",
    "subject":"acs:mns:cn-hangzhou:xxx:queues/queueName",
    "aliyunaccountid":"xxx"
  },
  {
    "data":{
        "id": 2,
        "name": "xiaoli",
        "age": 12
    },
    "id":"EF755211AE83630D7FD1052A357D556F",
    "source":"acs:mns",
    "specversion":"1.0",
    "type":"mns:Queue:SendMessage",
    "datacontenttype":"application/json; charset\\u003dutf-8",
    "time":"2022-07-01T16:04:12.286Z",
    "subject":"acs:mns:cn-hangzhou:xxx:queues/queueName",
    "aliyunaccountid":"xxx"
  }
]
```
> 注意：当 batchOrNot=False 时数据结构并不是数组，而仅是单个元素。

**调用方式**
  * 控制台调用：
    * 登录[函数计算控制台](https://fcnext.console.aliyun.com/cn-hangzhou/services) ，找到部署的 sink connector 函数。
    * 点击**测试函数**->**配置测试参数**，将上文的调用参数粘贴到下图所示位置中。（注：如果部署的函数 batchOrNot 配置为 False，则复制上文第一条消息，反之复制第二条消息。）
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/96bac8da2bb80a4b426ede8e40904b88/image.png)
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/4d4ce28bbcb870dc656a3dac1e552af2/image.png)
    * 完成后点击测试函数，则此条数据即通过函数插入到 ODPS 对应表中。
  
  * s 工具调用：
    * 进入应用项目工程下，在 s.yaml 查找应用初始化时输入的 batchOrNot 值，若：
      * batchOrNot 为 False：将文件 event-template/sink-single-event.json 中的值修改为目标值后，执行 s sink invoke --event-file event-template/sink-single-event.json 进行函数调用
      * batchOrNot 为 True：将文件 event-template/sink-batch-event.json 中的值修改为目标值后，执行 s sink invoke --event-file event-template/sink-batch-event.json 进行函数调用
    * 函数调用完成后，则此条数据即通过函数插入到 ODPS 对应表中。

<appdetail id="flushContent">

### 测试验证
函数调用成功后，该如何在 ODPS 侧查看数据是否写入成功？
  * 1: 进入 ODPS 数据开发页面，按照下图所示点击**新建**->**新建节点**->**ODPS SQL**，创建完成后会弹出一个可以编写 sql 的界面，进入下一步。
   
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/d5f223b0484c1cb91b6b9a25ea6ec9e0/image.png)
  * 2：写 sql 语句 `SELECT * FROM {tableName};`，点击运行 sql，完成后会返回表内的数据，如下图返回的数据即为上文测试 payload 中的 data 数据。
   ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/618742477e1b8a22fa953ab93381b8f1/image.png)


## 高级功能
### 自定义数据转储处理逻辑
本应用创建后会生成两个函数：transform 函数及 sink 函数。如果您需要对原始数据进行处理，可以编写 transform 函数中的 transform 方法，以便按照您需要的方式对数据进行预处理。

### 指定数据库分区插入数据
ODPS 可以将数据插入指定分区，为简化应用的复杂度，没有对用户提供此选项。如果有此需求，可修改 `src/sink/index.py` 中的 deliver 函数，在 write_table 方法中加入 partition 入参。 


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