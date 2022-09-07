package oss;

import com.alibaba.fastjson.annotation.JSONField;
import lombok.Data;

@Data
public class Config {
    @JSONField(name = "region")
    public String region;
    @JSONField(name = "concurrency")
    public long concurrency;
    @JSONField(name = "cacheSizeInMB")
    public long cacheSizeInMB;
    @JSONField(name = "cacheTimeWindowInSec")
    public long cacheTimeWindowInSec;
    @JSONField(name = "bucketName")
    public String bucketName;
    @JSONField(name = "objectPath")
    public String objectPath;
    @JSONField(name = "objectPrefix")
    public String objectPrefix;
    @JSONField(name = "objectShardingPath")
    public String objectShardingPath;
}
