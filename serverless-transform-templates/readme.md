# ServerlessTransformTemplates 帮助文档

<p align="center" class="flex justify-center">
    <a href="https://www.serverless-devs.com" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=ServerlessTransformTemplates&type=packageType">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=ServerlessTransformTemplates" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=ServerlessTransformTemplates&type=packageVersion">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=ServerlessTransformTemplates" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=ServerlessTransformTemplates&type=packageDownload">
  </a>
</p>

<description>

> ***Serverless ETL Templates***

</description>

## 应用简介

本应用是一个Serverless ETL Templates 示例集合，基于这些模版示例，可以利用函数计算定义自己的数据清洗逻辑。这些示例模版包括：

| 模版名称 | 英文名称 | 函数计算 |
| --- |  --- |  --- |
数据过滤 | filtering | 过滤指定特征的数据，可以根据某个字段，或者某个数据内容进行过滤；
动态路由 | dynamic routing | 对数据进行分析，利用外部API将数据发送到不同的目标处；
数据分割 | transform split | 对数据进行分割，将一条数据变成多条，或者将分割的数据重新组织；
数据映射 | transform projection | 将原来数据中的内容根据某种规则替换成新的内容，例如将IP转换成实际的地址信息；
数据富化 | transform enrichment | 从外部数据源处读取信息，在原来数据的基础上，按照自定义逻辑添加新的数据信息；

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

- :fire: 通过 [Serverless 应用中心](https://fcnext.console.aliyun.com/applications/create?template=ServerlessTransformTemplates) ，
[![Deploy with Severless Devs](https://img.alicdn.com/imgextra/i1/O1CN01w5RFbX1v45s8TIXPz_!!6000000006118-55-tps-95-28.svg)](https://fcnext.console.aliyun.com/applications/create?template=ServerlessTransformTemplates)  该应用。

</appcenter>

- 通过 [Serverless Devs Cli](https://www.serverless-devs.com/serverless-devs/install) 进行部署：
  - [安装 Serverless Devs Cli 开发者工具](https://www.serverless-devs.com/serverless-devs/install) ，并进行[授权信息配置](https://www.serverless-devs.com/fc/config) ；
  - 初始化项目：`s init ServerlessTransformTemplates -d ServerlessTransformTemplates`
  - 进入项目，并进行项目部署：`cd ServerlessTransformTemplates && s deploy -y`

</deploy>

<devgroup>

## 开发者社区

您如果有关于错误的反馈或者未来的期待，您可以在 [Serverless Devs repo Issues](https://github.com/serverless-devs/serverless-devs/issues) 中进行反馈和交流。如果您想要加入我们的讨论组或者了解 FC 组件的最新动态，您可以通过以下渠道进行：

<p align="center">

| <img src="https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1635407298906_20211028074819117230.png" width="130px" > | <img src="https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1635407044136_20211028074404326599.png" width="130px" > | <img src="https://serverless-article-picture.oss-cn-hangzhou.aliyuncs.com/1635407252200_20211028074732517533.png" width="130px" > |
|--- | --- | --- |
| <center>微信公众号：`serverless`</center> | <center>微信小助手：`xiaojiangwh`</center> | <center>钉钉交流群：`33947367`</center> |

</p>

</devgroup>
