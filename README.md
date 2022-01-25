# Image Captioning (图像描述生成) - Web部署
## 简介
Image Captioning (图像描述生成) 的独立 Web部署端。输入一张图像，生成英文文本描述。
更多详见: [图像描述生成 (Image Captioning)](https://www.oneflow.cloud/#/project/public/code?id=b764f74eff7b10cb73f0a5c1b2e63f0a)

## 架构
`server.py` 中将通过 `Flask`后端框架 启动一个 Web 服务。这个 Flask 服务器接收来自用户浏览器通过 Ajax 发出的请求后，在服务器使用模型完成推理，然后将结果以 JSON 的形式返回。如下所示：

```
┌───────┐           ┌───────┐        ┌───────┐
│       │    Ajax   │       │        │       │
│       ├───────────►       ├────────►       │
│ User  │           │ Flask │        │ Infer │
│       ◄───────────┤       ◄────────┤       │
│       │   JSON    │       │        │       │
└───────┘           └───────┘        └───────┘
```

## 项目文件结构
```
├─oscar                  核心代码
|   ├─datasets              数据处理相关
|   |   └─caption_tsv.py        定义数据张量化工具类
|   ├─modeling              模型结构定义相关
|   |   ├─modeling_bert.py      定义用于 Image Captioning 任务的Bert模型
|   |   └─modeling_utils.py     模型定义辅助代码
|   ├─utils              其他工具代码
|   |   ├─cbs.py                序列搜索策略：受限束搜索 (Constrained Beam Search)
|   |   └─misc.py               杂项工具
|   └─infer_on_single.py     在单张图像上进行推理
|
├─inference_models       推理时加载的模型权重 (包括提取图像特征的Bottom Up Attenion以及Oscar本身)
├─oscar_dependencies     模型依赖，会在执行 launch.sh 初始化运行环境时使用
├─objects_vocab.txt      COCO Caption数据集的类别名称 (用于推理时将从图像中检测到的物体类别ID映射为类别名称)
├─templates              预定义的 HTML 模板
├─launch.sh              用于启动服务的 Shell 脚本
└─server.py              使用 Flask 实现的后端
```

## 部署方法

**Step 1**: 点击项目页面中的"部署" 
<div align="center">
<img width="450px" src="https://oneflow-public.oss-cn-beijing.aliyuncs.com/OneCloud/img/20220112-ZuoYihao-ImageCaptioning/1.png" alt="Step 1">
</div>

**Step 2**: 选择模型文件，保持所有文件选中即可
<div align="center">
<img width="400px" src="https://oneflow-public.oss-cn-beijing.aliyuncs.com/OneCloud/img/20220112-ZuoYihao-ImageCaptioning/2.png" alt="Step 2">
</div>

**Step 3**: 填写基本信息
<div align="center">
<img width="400px" src="https://oneflow-public.oss-cn-beijing.aliyuncs.com/OneCloud/img/20220112-ZuoYihao-ImageCaptioning/3.png" alt="Step 3">
</div>


**Step 4**: 填写配置信息
- "工作环境"选择"公开环境"中的 "oneflow-0.6.0+torch-1.8.1-cu11.1-cudnn8"
- "启动命令行"填写为 `cd /workspace/ && bash launch.sh`
- "端口"填写为`5000` (因为 `server.py` 监听的是5000端口)
<div align="center">
<img width="400px" src="https://oneflow-public.oss-cn-beijing.aliyuncs.com/OneCloud/img/20220112-ZuoYihao-ImageCaptioning/4.png" alt="Step 4">
</div>

**Step 5**: 选择运行环境
<div align="center">
<img width="300px" src="https://oneflow-public.oss-cn-beijing.aliyuncs.com/OneCloud/img/20220112-ZuoYihao-ImageCaptioning/5.png" alt="Step 5">
</div>

**提示**：开始运行后的初始片刻，需要一定时间执行 `launch.sh` 以初始化运行环境，此时访问链接将会返回 "502 Bad Gateway"，稍等片刻即可。


## 其他
除了通过Web端进行在线推理，也可以通过命令行直接调用 `infer_on_single.py` 完成在图像上的推理，用法如下：

在项目根目录下执行：
```
python oscar/infer_on_single.py --image_path <图像文件的路径> --eval_model_dir <使用的模型权重所在目录>
```

