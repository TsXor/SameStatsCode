# SameStatsCode - 复现代码

## 配置依赖
```bash
pip install -r requirements.txt
```
建议使用3.10及以上的Python。  

## 运行
### 无参运行
```bash
python launcher.py
```
将触发“交互输入模式”，按照终端提示输入参数即可。   
Windows环境下可以直接双击`launcher.py`。  
### 查看帮助
```bash
python launcher.py --help
```
具体用法请看下面，此“帮助”只列出有效参数。  

## 使用指南
### 参数
- `SOURCE`（源数据集）  
  csv形式的源数据点集的路径。可以指定绝对路径，或相对于`seed_datasets`的路径。`.csv`后缀可以省略。  
- `TARGET`（转化目标）  
  转化目标的名称。当前暂不支持加载自定义图形，内置图形的名称请参考`same_stats\algo\default_dests.py`  
- `--n-iter`（迭代数）  
- `--n-frames`（生成图片帧数）  
- `--error-precision`（误差精度）  
### 输出
输出文件位于`results`目录下，会创建一个用运行时间标记的文件夹来存放。  
`data`保存中间数据，`images`保存图片帧，`video`保存视频。  

## 自定义
`same_stats`是一个完整的模块，你可以通过它自定义输入和输出文件夹，或者调用算法的API。  
