package function;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;

import com.aliyun.fc.runtime.Context;
import com.aliyun.fc.runtime.Credentials;
import com.aliyun.fc.runtime.StreamRequestHandler;
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;

import oss.UnRetryableException;
import oss.OssOperator;
import oss.TaskInfo;

public class Handler implements StreamRequestHandler {

    @Override
    public void handleRequest(InputStream inputStream, OutputStream outputStream, Context context) throws IOException {

        // 获取密钥信息，执行前，确保函数所在的服务配置了角色信息，并且角色需要拥有AliyunOSSFullAccess权限
        // 建议直接使用AliyunFCDefaultRole 角色
        Credentials creds = context.getExecutionCredentials();

        ByteArrayOutputStream result = new ByteArrayOutputStream();
        byte[] buffer = new byte[1024];
        for (int length; (length = inputStream.read(buffer)) != -1; ) {
            result.write(buffer, 0, length);
        }
        String payload = result.toString(StandardCharsets.UTF_8.name());

        // 创建OSSClient实例。
        OssOperator ossOP = OssOperator.getOSSOperator(context);
        TaskInfo params = ossOP.generateTaskParams();
        try {
            // first, get oss file lock
            context.getLogger().info(String.format("now start reserve lock, params: %s", params.str()));
            ossOP.getLock(context, params);
            context.getLogger().info("reserve lock succeeded, now start upload file");
            ossOP.startUploadAppendTask(context, params, payload);
        } catch (UnRetryableException ce) {
            context.getLogger().fatal(String.format("failed to process message: %s", ce.toString()));
            throw new IOException(ce.toString());
        } catch (Exception e) {
            context.getLogger().fatal(String.format("failed to process message: %s", e.toString()));
            throw new IOException(e.toString());
        } finally {
            // todo: we use finaly and prefreeze to garatine the lock is released.
            ossOP.tryReleaseLock(context, params);
        }

        outputStream.write(new String("done").getBytes());
    }
}