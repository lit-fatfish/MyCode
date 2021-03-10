# 参考
https://blog.csdn.net/chaipp0607/article/details/74139895
https://blog.csdn.net/c20081052/article/details/81475394
https://github.com/tensorflow/models/tree/master/research/slim

# slim 训练脚本目录
`/home/anlly/devdata/app/tf/models/research/slim`
├── build
├── BUILD
├── data_convert_tfrecords.py # 数据转换为tfrecord脚本
├── datasets
├── deployment
├── dist
├── download_and_convert_data.py
├── eval_image_classifier.py
├── export_inference_graph.py
├── export_inference_graph_test.py
├── __init__.py
├── nets
├── preprocessing
├── README.md
├── run.md # 使用文档
├── scripts
├── setup.cfg.bak
├── setup.py
├── slim.egg-info
├── slim_walkthrough.ipynb
├── train_image_classifier.py # 训练脚本
└── WORKSPACE

# 数据目录结构
├── flowers # flowers 数据集目录
│   └── dataset # 存放数据目录
│       ├── daisy
│       ├── dandelion
│       ├── roses
│       ├── sunflowers
│       └── tulips
├── pre_models # 预训练模型
└── train_logs  # 训练日志
    └── flowers # flowers 训练结果保存路径

# 1、数据集转换
python data_convert_tfrecords.py --dataset_dir=/mnt/tf_data/board_rb_20210223

# 2、inception-V3 模型为基础进行迁移训练【用的会比较多】
DATASET_DIR=/mnt/tf_data/board_rb_20210223
TRAIN_DIR=/mnt/tf_data/train_logs/board_rb_20210223
CHECKPOINT_PATH=/mnt/tf_data/pre_models/inception_v3.ckpt
python train_image_classifier.py \
  --train_dir=${TRAIN_DIR} \
  --dataset_dir=${DATASET_DIR} \
  --dataset_name=flowers \
  --dataset_split_name=train \
  --model_name=inception_v3 \
  --checkpoint_path=${CHECKPOINT_PATH} \
  --checkpoint_exclude_scopes=InceptionV3/Logits,InceptionV3/AuxLogits \
  --trainable_scopes=InceptionV3/Logits,InceptionV3/AuxLogits

# 3、TensorBoard 查看训练结果86:6006
tensorboard --logdir=${TRAIN_DIR}

# jupyter notebook
cd /tf
jupyter notebook --no-browser --port 8888 --ip=0.0.0.0 --allow-root

# 分类模型训练，从头训练
DATASET_DIR=/mnt/tf_data/flowers
TRAIN_DIR=/mnt/tf_data/train_logs/flowers
python train_image_classifier.py \
  --train_dir=${TRAIN_DIR} \
  --dataset_name=flowers \
  --dataset_split_name=train \
  --dataset_dir=${DATASET_DIR} \
  --model_name=inception_v3

# 4、评估模型性能
CHECKPOINT_FILE=/mnt/tf_data/train_logs/board_rb_20210223
python eval_image_classifier.py \
  --alsologtostderr \
  --checkpoint_path=${CHECKPOINT_FILE} \
  --dataset_dir=/mnt/tf_data/board_rb_20210223 \
  --dataset_name=flowers \
  --dataset_split_name=validation \
  --model_name=inception_v3

```
Finished evaluation at 2021-02-01-14:17:25 评估完成
```

```shell
--checkpoint_path: 模型文件存放路径，这个参数既可以接收一个目录的路径，也可以接收一个文件的路径。 
如果接收的是一个目录的路径，如这里的satellite/train_dir，就会在这个目录中寻找最新保存的模型文件，执行验证。
也可以指定一个模型进行验证，以第 300 步的模型为例:
在 satellite/train_dir 文件夹下把被保存为 model.clcpt-300.meta 、 model.ckpt-300.index、 model.ckpt-300.data-00000-of-00001 三个文件。 
此时，如果要对它执行验证，给 checkpoint_path 传递的参数应该为
satellite/train_dir/model.ckpt-300

--eval_dir: 是验证结果存放路径
--dataset_name: 是数据集名称
--dataset_split_name: 是数据集操作类型名（根据验证集还是训练集实际到对应目录下找这阶段的tf-record数据）
--dataset_dir: 就是验证集tf-record存放目录
--model_name: 网络模型结构的名字

其中Accuracy是模型分类准确率，而Recall_5是Top5的准确率，表示在输出的类别概率中，正确类别只要落在前5就算对。由于训练目标类别总共才6类，因此可更改Top-5为Top-2或Top-3的准确率。需要再eval_image_classifier.py中修改如下内容

把其中的召回率5改成2或3就行；更改后再次运行验证指令，得到如下结果（召回率结果下降）
```

# 5、导出训练好的模型（inception_v3_inf_graph.pb只需生成一次）
python export_inference_graph.py \
  --alsologtostderr \
  --model_name=inception_v3 \
  --output_file=/mnt/tf_data/tf_models/board_rb_20210223/inception_v3_inf_graph.pb \
  --dataset_name flowers

```sh
会在satellite文件夹下生成一个pb文件；
注意：
inception_v3_inf_graph.pb 文件中只保存了 Inception V3 的网络结构， 并不包含训练得到的模型参数，
需要将 checkpoint 中的模型参数保存进来。 
方法是使用 freeze_graph. py 脚本（在 chapter_3 文件夹下运行）：
```

# 6、将 checkpoint 中的模型参数,加入 inception_v3_inf_graph.pb
python /usr/local/lib/python3.6/dist-packages/tensorflow_core/python/tools/freeze_graph.py \
  --input_graph /mnt/tf_data/tf_models/board_rb_20210223/inception_v3_inf_graph.pb \
  --input_checkpoint /mnt/tf_data/train_logs/board_rb_20210223/model.ckpt-720848 \
  --input_binary true \
  --output_node_names InceptionV3/Predictions/Reshape_1 \
  --output_graph /mnt/tf_data/tf_models/board_rb_20210223/board_rb_20210223_inception_v3.pb

```
--input_graph: 表示使用的网络结构文件，即之前已经导出的 inception_ v3_inf_graph.pb
--input_ checkpoint: 具体将哪一个 checkpoint 的参数载入到网络结构中 。这里使用的是训练文件夹 train_dir 中的第 100000 步模型文件。 需要根据训练文件夹下 checkpoint 的实际步数，将 100000 修改成对应的数值。
--input_binary: true 导入的 inception_v3 inf_graph.pb 实际是一个 protobuf 文件。 而protobuf文件有两种保存格式，一种是文本形式，一种是二进 制形式。 inception_v3 _inf _graph. pb 是二进制形式，所以对应的参数是 --input_binary true
--output_node_names: InceptionV3/Predictions/Reshape_1在导出的模型中，指定一个输出结点， `InceptionV3/Predictions/Reshape _ l 是 Inception V3 最后的输出层`
--output_graph 最后导出的模型保存为 `slim/satellite／frozen_graph.pb` 文件
```

# 模型测试
<!-- python classify_image_inception_v3.py \
  --model_path /mnt/tf_data/tf_models/board_rb/board_rb_inception_v3.pb \
  --label_path /mnt/tf_data/board_rb/labels.txt \
  --image_file /mnt/tf_data/tf_test_data/board_rb/test/board_rb_1_1.jpg -->

python classify_image_12.py \
  --model_path /mnt/tf_data/tf_models/board_rb_20210223/board_rb_20210223_inception_v3.pb \
  --label_path /mnt/tf_data/board_rb_20210223/labels.txt \
  --image_path /mnt/tf_data/tf_test_data/board_rb/board_12

# 完结
===============================


# 准确率验证
python  eval_image_classifier.py  
  --dataset_name=flowers  
  --dataset_dir=D:/models-master/research/slim/flowers_5  
  --dataset_split_name=validation  
  --model_name=inception_v4  
  --checkpoint_path=D:/models-master/research/slim/flowers_5/my_train  
  --eval_dir=D:/models-master/research/slim/flowers_5/validation_result  
  --batch_size=32

# 导出pb文件
python export_inference_graph.py \
  --alsologtostderr \
  --model_name=inception_v3 \
  --output_file=/tmp/inception_v3_inf_graph.pb

python export_inference_graph.py \
  --alsologtostderr \
  --model_name=mobilenet_v1 \
  --image_size=224 \
  --output_file=/tmp/mobilenet_v1_224.pb


