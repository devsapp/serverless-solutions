cd layer && zip -r etl_layer ./*

注意将 rule.py 和 enrichment-xxx.py 部署在同一个目录
todos:
1. rule validate;
2. basic Realization 
3. optimize：
（1）static methods and classes move to layer 
（2）如果有 key 的富化需求，P2 进行
