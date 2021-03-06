# -*- coding:utf8 -
import random
import math
import numpy as np
import matplotlib.pyplot as plt


class GA(object):
    def __init__(self, num_city, num_total, iteration, data):
        self.num_city = num_city    #城市个数
        self.num_total = num_total  #种群个数
        self.scores = []
        self.iteration = iteration  #迭代次数
        self.location = data        #城市坐标
        self.ga_choose_ratio = 0.2  #gc概率
        self.mutate_ratio = 0.1     #突变概率
        # fruits是所有的种群，随机生成种群
        self.fruits = self.random_init(num_total, num_city)
        #dis_mat记录了所有点之间的距离
        self.dis_mat = self.compute_dis_mat(num_city, data)

        # 显示初始化后的最佳路径
        scores = self.compute_adp(self.fruits)
        # 将种群适应度从大到小排列
        sort_index = np.argsort(-scores)
        init_best = self.fruits[sort_index[0]]
        init_best = self.location[init_best]
        init_best = np.vstack((init_best, init_best[0]))
        plt.subplot(2, 2, 2)
        plt.title('init best result')
        plt.plot(init_best[:, 0], init_best[:, 1])
        self.iter_x = [0]
        # 没开始迭代之前的适应度
        self.iter_y = [1. / scores[sort_index[0]]]

    def random_init(self, num_total, num_city):
        tmp = [x for x in range(num_city)]
        result = []
        for i in range(num_total):
            random.shuffle(tmp)
            result.append(tmp)
        return result

    # 计算不同城市之间的距离
    def compute_dis_mat(self, num_city, location):
        dis_mat = np.zeros((num_city, num_city))
        for i in range(num_city):
            for j in range(num_city):
                if i == j:
                    dis_mat[i][j] = np.inf
                    continue
                a = location[i]
                b = location[j]
                tmp = np.sqrt(sum((x[0] - x[1]) ** 2 for x in zip(a, b)))
                dis_mat[i][j] = tmp
        return dis_mat

    # 计算路径长度
    def compute_pathlen(self, path, dis_mat):
        #得到第一个城市和最后一个城市之间的距离
        try:
            a = path[0]
            b = path[-1]
        except:
            import pdb
            pdb.set_trace()
        result = dis_mat[a][b]
        for i in range(len(path) - 1):
            a = path[i]
            b = path[i + 1]
            result += dis_mat[a][b]
        return result

    # 计算种群适应度
    def compute_adp(self, fruits):
        adp = []
        for fruit in fruits:
            #种群是整数时，抛出异常
            if isinstance(fruit, int):
                import pdb
                pdb.set_trace()
            length = self.compute_pathlen(fruit, self.dis_mat)
            adp.append(1.0 / length)
        return np.array(adp)
    
    #交叉
    #x,y是两个基因（路径），进行染色体交叉
    def ga_cross(self, x, y):
        len_ = len(x)
        #二者长度不一样抛出异常
        assert len(x) == len(y)
        path_list = [t for t in range(len_)]
        #截取长度为2的随机数
        order = list(random.sample(path_list, 2))
        order.sort()
        #start和end是进行交叉的部分
        start, end = order

        # 找到冲突点并存下他们的下标,x中存储的是y中的下标,y中存储x与它冲突的下标
        #tmp是进行交叉的部分
        tmp = x[start:end]
        x_conflict_index = []
        for sub in tmp:
            index = y.index(sub)
            #x中的部分不在y中
            if not (index >= start and index < end):
                x_conflict_index.append(index)

        y_confict_index = []
        tmp = y[start:end]
        for sub in tmp:
            index = x.index(sub)
            #y中的部分不在x中
            if not (index >= start and index < end):
                y_confict_index.append(index)

        #判断冲突的部分长度是否相同
        assert len(x_conflict_index) == len(y_confict_index)

        # 交叉
        tmp = x[start:end]
        x[start:end] = y[start:end]
        y[start:end] = tmp

        # 解决冲突
        # 之前对冲突部分也进行了交换，还原冲突部分
        for index in range(len(x_conflict_index)):
            i = x_conflict_index[index]
            j = y_confict_index[index]
            y[i], x[j] = x[j], y[i]
        
        #保证交换
        assert len(set(x)) == len_ and len(set(y)) == len_
        return list(x), list(y)
    
    #进行父代的选择
    #选择概率最大的几个作为父代
    def ga_parent(self, scores, ga_choose_ratio):
        #返回从大到小的索引
        sort_index = np.argsort(-scores).copy()
        sort_index = sort_index[0:int(ga_choose_ratio * len(sort_index))]
        parents = []
        parents_score = []
        #循环所有的下标
        for index in sort_index:
            parents.append(self.fruits[index])
            parents_score.append(scores[index])
        return parents, parents_score

    #使用轮盘赌算法进行选择,获得一个新种群
    def ga_choose(self, genes_score, genes_choose):
        sum_score = sum(genes_score)
        #算出每个种群的累积概率
        score_ratio = [sub * 1.0 / sum_score for sub in genes_score]
        rand1 = np.random.rand()
        rand2 = np.random.rand()
        #循环所有的累积概率
        for i, sub in enumerate(score_ratio):
            if rand1 >= 0:
                rand1 -= sub
                if rand1 < 0:
                    index1 = i
            if rand2 >= 0:
                rand2 -= sub
                if rand2 < 0:
                    index2 = i
            if rand1 < 0 and rand2 < 0:
                break

        return list(genes_choose[index1]), list(genes_choose[index2])

    #突变
    #gene是一个种群，即一个路径，变异是随机截取基因中一段，进行倒置
    def ga_mutate(self, gene):
        path_list = [t for t in range(len(gene))]
        order = list(random.sample(path_list, 2))
        order.sort()
        start, end =order
        tmp = gene[start:end]
        # np.random.shuffle(tmp)
        #从最后一个元素到第一个元素遍历一遍
        tmp = tmp[::-1]
        gene[start:end] = tmp
        return list(gene)

    def ga(self):
        # 获得优质父代,score是种群适应度
        scores = self.compute_adp(self.fruits)
        #选择部分优秀个体作为父代候选集合父代选择
        #通过种群适应度和交换概率进行
        parents, parents_score = self.ga_parent(scores, self.ga_choose_ratio)
        tmp_best_one = parents[0]
        tmp_best_score = parents_score[0]
        # 新的种群fruits,里面所有选中的父代
        fruits = parents[:]
        # 生成新的种群，
        while len(fruits) < self.num_total:
            # 轮盘赌方式对父代进行选择
            gene_x, gene_y = self.ga_choose(parents_score, parents)
            # x,y交叉
            gene_x_new, gene_y_new = self.ga_cross(gene_x, gene_y)
            # 交叉以后x,y进行突变
            if np.random.rand() < self.mutate_ratio:
                gene_x_new = self.ga_mutate(gene_x_new)
            if np.random.rand() < self.mutate_ratio:
               gene_y_new = self.ga_mutate(gene_y_new)
            #计算出x,y的适应度
            x_adp = 1. / self.compute_pathlen(gene_x_new, self.dis_mat)
            y_adp = 1. / self.compute_pathlen(gene_y_new, self.dis_mat)
            # 将适应度高的放入种群中
            if x_adp > y_adp and (not gene_x_new in fruits):
                fruits.append(gene_x_new)
            elif x_adp <= y_adp and (not gene_y_new in fruits):
                fruits.append(gene_y_new)

        self.fruits = fruits
        return tmp_best_one, tmp_best_score

    def run(self):
        BEST_LIST = None
        best_score = -np.inf
        #循环所有的迭代次数
        for i in range(1, self.iteration + 1):
            tmp_best_one, tmp_best_score = self.ga()
            #iter_x是迭代次数
            self.iter_x.append(i)
            #iter_y是距离
            self.iter_y.append(1. / tmp_best_score)
            if tmp_best_score > best_score:
                best_score = tmp_best_score
                BEST_LIST = tmp_best_one
        print("最短长度：")
        print(1./best_score)
        print('最短路径：')
        print(self.location[BEST_LIST])
        plt.subplot(2, 2, 4)
        plt.title('convergence curve')
        plt.plot(self.iter_x, self.iter_y)
        #返回城市的坐标，最短距离
        return self.location[BEST_LIST], 1. / best_score


# 读取数据
def read_tsp(path):
    lines = open(path, 'r').readlines()
    assert 'NODE_COORD_SECTION\r\n' in lines
    index = lines.index('NODE_COORD_SECTION\r\n')
    data = lines[index + 1:-1]
    tmp = []
    for line in data:
        line = line.strip().split(' ')
        if line[0] == 'EOF':
            continue
        tmpline = []
        for x in line:
            if x == '':
                continue
            else:
                tmpline.append(float(x))
        if tmpline == []:
            continue
        tmp.append(tmpline)
    data = tmp
    return data

#读取数据
data = read_tsp('data/st14.tsp')
data = np.array(data)
plt.suptitle('GA in st14.tsp')
#将每个城市的编号去掉
data = data[:, 1:]
#将当前窗口划分成2X2的网格，在1位置创建坐标图
plt.subplot(2, 2, 1)
plt.title('raw data')
#show_data加入所有的城市，并在最后一个城市后加上第一个城市
show_data = np.vstack([data, data[0]])
#确定x轴和y轴的数据
plt.plot(data[:, 0], data[:, 1])
#最好假设为无穷大
Best=np.inf
Best_path = None

#得到适应度最高的基因，对应的适应度
foa = GA(num_city=data.shape[0], num_total=30, iteration=75, data=data.copy())
#得到最优的路线和长度
path, path_len = foa.run()
if path_len < Best:
    Best = path_len
    Best_path = path
plt.subplot(2, 2, 3)
# 加上一行，最后一个城市回到第一个城市
Best_path = np.vstack([Best_path, Best_path[0]])
plt.plot(Best_path[:, 0], Best_path[:, 1])
plt.title('result')
plt.show()
