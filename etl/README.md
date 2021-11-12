ETL related solutions
see: https://www.splunk.com/en_us/blog/it/event-processing-design-patterns-with-pulsar-functions.html

Pulsar Function:

[ ] Dynamic Routing
[X] Filtering
[X] Transformation
  [X] Projection & Replacement
  [X] Enrichment
  [ ] Split
  ? [ ] Enhanced Replacement
[ ] Alerts and Thresholds
[ ] Simple Counting and Counting with Windows

SLS:
see: https://help.aliyun.com/document_detail/159702.html

[X] 过滤：同 Filtering

[ ] 富化
  [ ] OSS
  [ ] RDS
  [ ] 自定义特定数据
  
转换：同 Transformation

[ ] 分裂
    [ ] 1 - n topic 分发 (Dynamic Routing)
    [ ] 1 - 1 topic 分裂 (Split)
  
