#! /bin/sh
list=(0.png)         #数组 list 用于存储要转换成 gif 的 png 图片
for i in {1..10..1}  #前 0-10 epoch,d_loss下降较快
do
    list=(${list[@]} ${i}.png)
done

for i in {15..120..5} # 15-120 epcoh,步长为5
do
    list=(${list[@]} ${i}.png)
done
convert -delay 100 ${list[@]} loss.gif  #convert 命令由 ImageMagick 包提供
