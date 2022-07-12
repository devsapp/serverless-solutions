# FCOssSinkConnector 帮助文档

<p align="center" class="flex justify-center">
    <a href="https://www.serverless-devs.com" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=FCOssSinkConnector&type=packageType">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=FCOssSinkConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=FCOssSinkConnector&type=packageVersion">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=FCOssSinkConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=FCOssSinkConnector&type=packageDownload">
  </a>
</p>

<description>

> ***函数计算 oss sink connector***

</description>

<table>

## 前期准备
使用该项目，推荐您拥有以下的产品权限 / 策略：

| 服务/业务 | 函数计算 |     
| --- |  --- |   
| 权限/策略 | AliyunFCFullAccess</br>AliyunLogFullAccess |     


</table>

<codepre id="codepre">



</codepre>

<deploy>

## 部署 & 体验

<appcenter>

- :fire: 通过 [Serverless 应用中心](https://fcnext.console.aliyun.com/applications/create?template=FCOssSinkConnector) ，
[![Deploy with Severless Devs](https://img.alicdn.com/imgextra/i1/O1CN01w5RFbX1v45s8TIXPz_!!6000000006118-55-tps-95-28.svg)](https://fcnext.console.aliyun.com/applications/create?template=FCOssSinkConnector)  该应用。 

</appcenter>

- 通过 [Serverless Devs Cli](https://www.serverless-devs.com/serverless-devs/install) 进行部署：
    - [安装 Serverless Devs Cli 开发者工具](https://www.serverless-devs.com/serverless-devs/install) ，并进行[授权信息配置](https://www.serverless-devs.com/fc/config) ；
    - 初始化项目：`s init FCOssSinkConnector -d FCOssSinkConnector`   
    - 进入项目，并进行项目部署：`cd FCOssSinkConnector && s deploy -y`

</deploy>

<appdetail id="flushContent">


## 应用简介
本应用为函数计算 Oss sink connector。使用本应用可以将您的原始输入数据转存到您创建应用时填写的OSS中。本应用支持批量传输及单条数据传输；并支持 cloudEvent Schema 及自定义数据格式。如果您需要对数据进行转换，可以编写应用创建后的 transform 函数。否则您只需调用 sink 函数即可。

## 使用步骤
您可以通过应用中心或直接使用 s 工具进行部署。
1. 准备资源：创建 oss 实例，并开启公网访问；
2. 部署应用；参数按照需要进行填写；
3. 进行测试。构建输入参数（dataSchema：cloudEvent）
```
{
    "data":{
        "requestId":"xx",
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
之后调用 invokeFunction（控制台测试或使用 SDK）进行测试。


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