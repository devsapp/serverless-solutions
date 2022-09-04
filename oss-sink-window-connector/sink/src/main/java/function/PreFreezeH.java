package function;

import com.aliyun.fc.runtime.Context;
import com.aliyun.fc.runtime.PreFreezeHandler;
import oss.OssOperator;

import java.io.IOException;

public class PreFreezeH implements PreFreezeHandler {

    @Override
    public void preFreeze(Context context) throws IOException {
        context.getLogger().info("task done, now start release lock");
        // lock was released in handler. prefreeze is not always called.
        //OssOperator.getOSSOperator(context).tryReleaseLock(context);
    }
}

