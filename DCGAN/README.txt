训练环境
OS: Deepin Linux 15.11 x86_64
GPU: NVIDIA GeForce GTX 960M
tensorflow-gpu (1.4.0)
scipy 1.3.1
cv2 4.1.1
PIL 6.2.1
imageio 2.6.1
cuda V8.0.44
cudnn v6.0

从头开始训练模型,数据集位于data/anime,生成的sample图片位于out目录,生成的loss图片位于samples目录的子目录loss中:
python3 main.py --input_height 96 --input_width 96 --output_height 48 --output_width 48 --dataset anime --crop --train --epoch 1 --input_fname_pattern "*.jpg"


继续checkpoint训练,需要指定checkpoint目录(--checkpoint_dir)和sample图片生成目录(--out_name):
python3 main.py --input_height 64 --input_width 64 --output_height 48 --output_width 48 --dataset anime --crop --train --epoch 3 --input_fname_pattern "*.jpg" --checkpoint_dir '/home/mogician/DL/DCGAN-tensorflow/out/20191114.134044 - data - anime - x64.z100.uniform_signed.y48.b64/checkpoint' --out_name '20191114.134044 - data - anime - x64.z100.uniform_signed.y48.b64'

训练结束后,生成测试图片:
python3 main.py --input_height 64 --input_width 64 --output_height 48 --output_width 48 --dataset anime --crop  --epoch 1 --input_fname_pattern "*.jpg" --visualize True --checkpoint_dir '/home/mogician/DL/DCGAN-tensorflow/out/20191114.134044 - data - anime - x64.z100.uniform_signed.y48.b64/checkpoint'

取部分生成的loss图片制成gif动态图:
将 gif.sh 移动到loss图片目录,在已经安装 ImageMagick 的前提下,执行:
bash gif.sh
