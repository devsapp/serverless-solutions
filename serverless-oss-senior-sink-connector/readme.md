# OSSSeniorSinkConnector 帮助文档


<p align="center" class="flex justify-center">
    <a href="https://www.serverless-devs.com" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=OSSSeniorSinkConnector&type=packageType">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=OSSSeniorSinkConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=OSSSeniorSinkConnector&type=packageVersion">
  </a>
  <a href="http://www.devsapp.cn/details.html?name=OSSSeniorSinkConnector" class="ml-1">
    <img src="http://editor.devsapp.cn/icon?package=OSSSeniorSinkConnector&type=packageDownload">
  </a>
</p>

<description>

> ***函数计算(FC) -> 对象存储(OSS) sink connector***

</description>


## 应用简介
本应用可以将您的原始输入数据经过压缩处理后，写入到您创建应用时填写的 OSS bucket 中。

## 前期准备

### 权限准备

使用该项目，推荐您拥有以下的产品权限 / 策略：

| 服务/业务 | 函数计算                                                             |     
| --- |------------------------------------------------------------------|   
| 权限/策略 | AliyunFCFullAccess<br>AliyunLogFullAccess<br>AliyunOSSFullAccess |     


### 资源准备
  * 1: 开通 OSS(MaxCompute) 服务。
  * 2: 创建 OSS Bucket 资源。（如果您已经创建完成或有可以直接使用的项目资源，可跳过此步。）
    * 2-1: 登录 [OSS 控制台](https://oss.console.aliyun.com/overview)， 点击 **Bucket 列表** -> **创建 Bucket**。
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/lambda/757b1ca33d0b6c68d629481e33fe3074/image.png)
    * 2-2: 填写 **Bucket 名称**，其他配置如无特殊需求可使用默认配置，点击**确定**即成功创建一个 oss bucket 资源。
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/lambda/7974432f8540037db48b0e5d30efae9c/image.png)

      
## 使用步骤

### 应用部署

<appcenter>

- :fire: 通过 [Serverless 应用中心](https://fcnext.console.aliyun.com/applications/create?template=OSSSeniorSinkConnector) ，
[![Deploy with Severless Devs](https://img.alicdn.com/imgextra/i1/O1CN01w5RFbX1v45s8TIXPz_!!6000000006118-55-tps-95-28.svg)](https://fcnext.console.aliyun.com/applications/create?template=OSSSeniorSinkConnector)  该应用。 

</appcenter>

- 通过 [Serverless Devs Cli](https://www.serverless-devs.com/serverless-devs/install) 进行部署：
    - [安装 Serverless Devs Cli 开发者工具](https://www.serverless-devs.com/serverless-devs/install) ，并进行[授权信息配置](https://www.serverless-devs.com/fc/config) ；
    - 初始化项目：`s init OSSSeniorSinkConnector -d OSSSeniorSinkConnector`   
    - 进入项目，并进行项目部署：`cd OSSSeniorSinkConnector && s deploy -y`

<appdetail id="flushContent">

### 应用参数

无论通过上面哪种方式部署，都需要为应用配置参数，具体如下：
  * endpoint: OSS 访问域名, 请根据自身需求选择相应类型的 endpoint，通常可选择外网 Endpoint，详情可参考：https://help.aliyun.com/document_detail/31837.html。
  * bucket: 目标 OSS bucket 名称。
  * objectPath: OSS object 路径, 格式为 `'/path/'`，如果 object 直接存放在 bucket 一级目录下，仅需填写 `'/'`，例：(1)/a/b/c/ (2)/a/ (3) /。
  * objectNamePrefix: OSS object 前缀名称, 最终命名为 `PREFIX_${TIMESTAMP}_${RANDOM}`，其中 TIMESTAMP 精确到毫秒，RANDOM 为 8 位随机字符串。
  * compressType: 可以选择指定压缩算法(zip/gzip/snappy等)，将数据压缩后上传到 OSS。(默认值为 'None'，即不压缩。)

### 应用调用

#### 调用参数
应用部署完成后，可构造函数请求参数来对函数发起调用，测试函数正确性。 其示例可以参考：
```
[
    {
        "name":"xiaoMing",
        "age":"23",
        "gender":"male"
    },
    {
        "name":"xiaoHong",
        "age":"22",
        "gender":"female"
    }
]
```

#### 调用方式
  * 控制台调用
    * 登录[函数计算控制台](https://fcnext.console.aliyun.com/cn-hangzhou/services) ，找到部署的函数。
    * 点击**测试函数**->**配置测试参数**，将上文的调用参数粘贴到下图所示位置中。
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/033b7b6fe2a812a92eabffef39e6a10e/image.png)
    ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/ac5abb24640fe7ffaf8f8277b0557a1a/image.png)
    * 函数调用完成后，则此数据即通过函数上传到 OSS bucket 中。
  * s 工具调用：
    * 进入应用项目工程下，执行下面命令：`s sink invoke --event-file event-example/sink-event.json`。
    * 函数调用完成后，则此数据即通过函数上传到 OSS bucket 中。

### 测试验证
函数调用成功后，该如何在 OSS 侧查看数据是否写入成功？
  * 登录 OSS 控制台，找到创建应用时填写的投递 Bucket，如果函数执行成功，则可以在 bucket 下看到一个名为 `{objectPathPrefix}_{timestamp}.zip` 的 object。
  * 点击**更多**->**下载**，查看解压后的文件内容是否和函数的测试参数一致。
  ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/b858238f4a1a5c3361935ee607290123/image.png)
  ![image](http://git.cn-hangzhou.oss-cdn.aliyun-inc.com/uploads/serverless/serverless-solutions/f130a87bb32a1bd8b961f76aad665049/image.png)

### 高级功能

#### 通过不同网络访问 oss 实例
有如下三种网络访问方式：
- 经典网络访问：通过阿里云内网进行访问，不会产生公网流量，同时安全性也高于公网访问,推荐使用
- 公网访问：函数环境变量中的 endpoint 为公网访问地址时，需要 oss 开启“公网访问”能力，同时会产生公网流量
- vpc 访问：通过 vpc 网络进行访问，不会产生公网流量，需要为 sink 函数配置 vpc

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