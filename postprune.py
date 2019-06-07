# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 17:42:09 2019

@author: WENDY
"""

import os
import shutil
import numpy as np
import scipy.sparse as sp


# 准备工作
def init(data_path):
    if not os.path.exists(data_path):
        raise Exception("找不到原始结果保存文件夹")
    visual_path = data_path + "-result"
    if not os.path.exists(visual_path):
        raise Exception("找不到完整结果保存文件夹")
    visual_path_data = os.path.join(visual_path, 'data')
    if not os.path.exists(visual_path_data):
        raise Exception("找不到完整结果数据文件夹")

    # 创建保存剪枝后结果文件夹
    visual_path_datacut = os.path.join(visual_path, 'dataPrune')
    if os.path.exists(visual_path_datacut):
        shutil.rmtree(visual_path_datacut)
    shutil.copytree(visual_path_data, visual_path_datacut)

    return visual_path_datacut


# 获得所有文件夹目录
def Getdirnext(dirname_list, f=0):
    dirnext = []
    for name in dirname_list:
        for i in range(5):
            if name != []:
                newdir = name + os.path.sep + '%d' % i
                #                print(newdir)
                if os.path.exists(newdir):
                    f = 1
                    dirnext.append(newdir)
                else:
                    dirnext.append([])
    return dirnext, f


# 归一化
def Getnorm(data):
    m = sum(data)
    m_list = [i / m for i in data]
    return m_list


def normalize(data):
    for i in range(len(data)):
        m = np.sum(data[i])
        data[i] /= m
    return data


# 求矩阵的熵（每一个向量距离质心的离散程度）
def Getmatrix_dis(ma):
    """
    :param ma: sp.csr_matrix
    :return:
    """
    #    print('ma', ma.shape)
    # 计算质心
    ma_mean = sp.csr_matrix.mean(ma, axis=0)

    # 不需要逐行计算
    maT = ma.T

    # 计算交叉项
    vecProd = ma_mean * maT

    # 先求 (ma_mean)^2
    Sq_ma_mean = np.power(ma_mean, 2)
    sum_Sq_ma_mean_i = np.sum(Sq_ma_mean, axis=1)

    # 建立
    sum_Sq_ma_mean = np.tile(sum_Sq_ma_mean_i, (1, vecProd.shape[1]))

    # 计算 (maT)^2
    Sq_ma = sp.csr_matrix.power(ma, 2)
    sum_Sq_ma = sp.csr_matrix.sum(Sq_ma, axis=1)

    # 求和
    SqED = sum_Sq_ma.T + sum_Sq_ma_mean - 2 * vecProd

    # 开方得到欧式距离
    ma_dis = np.sqrt(SqED)
    #    print('ma_mean', ma_mean.shape)
    #    print('vecProd', vecProd.shape)
    #    print('Sq_ma_mean', Sq_ma_mean.shape)
    #    print('sum_Sq_ma_mean_i', sum_Sq_ma_mean_i)
    #    print('sum_Sq_ma_mean', sum_Sq_ma_mean.shape)
    #    print('sum_Sq_ma', sum_Sq_ma.shape)
    #    print('SqED', SqED.shape)
    #    print('ma_dis', ma_dis.shape)

    return ma_dis, ma.shape


# 得到 sub_list
def Getlist(data, k, U):
    sub_list = []

    # 生成这个节点聚类结果sub_list
    for i in range(k):
        # 将这层的景点聚类结果写进这层的result文件夹中
        matrix = U.toarray()
        matrix = normalize(matrix)

        # 顺序输出POI所属的类别
        class_POI = matrix.argmax(axis=1)

        # 输出属于这一类的景点的列表索引值
        index = np.where(class_POI == i)
        index_list = index[0].tolist()
        sub_list.append(index_list)

    return sub_list


def GetSE(X, U, level, alpha=0.1, beta=0.1):
    # 获得全部的距离
    X_dis, X_shape = Getmatrix_dis(X)
    X_dis_list = X_dis.tolist()[0]
    X_all = X_shape[0]

    #    X_dis_list = Getnorm(X_dis_list)

    X_dis_mean = sum(X_dis_list) / len(X_dis_list)
    X_SE = [(i - X_dis_mean) ** 2 for i in X_dis_list]
    X_SE_mean = sum(X_SE) / len(X_SE)

    # 获得子矩阵索引
    sub_list = Getlist(X, 5, U)

    sub_SE = []
    for sub_list_ in sub_list:
        sub_data = X[sub_list_[0]]
        for i in sub_list_[1:]:
            sub_data = sp.vstack((sub_data, X[i]))
        #            print(sub_data.shape)

        # 获得子矩阵的全部的距离
        sub_dis, sub_shape = Getmatrix_dis(sub_data)
        sub_dis_list = sub_dis.tolist()[0]
        sub_all = sub_shape[0]
        #        sub_dis_list = Getnorm(sub_dis_list)

        # 平均距离
        sub_dis_mean = sum(sub_dis_list) / len(sub_dis_list)
        #        print('平均距离： ', sub_dis_mean)

        # 距离的离散程度
        sub_dis_SE = [(i - sub_dis_mean) ** 2 for i in sub_dis_list]
        sub_dis_SE_mean = sum(sub_dis_SE) / len(sub_dis_SE)
        sub_SE.append((sub_all / X_all) * sub_dis_SE_mean)
    #        print('sub shape: ', sub_shape)
    #        print('距离的离散程度： ', sub_dis_SE_mean)

    sub_SSE = sum(sub_SE)

    loss = alpha * (X_SE_mean - sub_SSE) - beta * level

    if loss < 0:
        result = False
    else:
        result = True

    return X_SE_mean, sub_SSE, loss, result, X_SE_mean - sub_SSE


def postPrune(data_path):
    # 设置要保存的文件夹路径
    path_datacut = init(data_path)
    print("[PostPrune] 待进行后剪枝的结果: {}".format(data_path))
    print("[PostPrune] 后剪枝后结果的保存文件夹: {} ".format(path_datacut))

    U_name = '\\model\\501_U_sp.npz'
    X_name = '\\data\\buchai_POI_matrix.npz'

    dirnext = [data_path]
    dir_all = []

    f = 1
    while f:
        dir_all.append(dirnext)
        #    print(dirnext)
        dirnext, f = Getdirnext(dirnext)

    name_seq = [0, 1, 2, 3, 4]

    # 得到所有的文件夹目录
    data_path_text = data_path.split('\\')

    get_dir = []
    for sub_dir in dir_all:
        get_dir_sub = []
        for sub_dir_ in sub_dir:
            if sub_dir_ != []:
                sub_dir_text = sub_dir_.split('\\')
                get_dir_sub.append([i for i in sub_dir_text if i not in data_path_text])
        get_dir.append(get_dir_sub)

    CZ = []
    LOSS = []
    shang = []
    SSE_all = []
    SSE_result = []
    for i in range(len(dir_all)):
        SSE_alli = []
        SSE_resulti = []
        CZi = []
        LOSSi = []
        shangi = []
        xiai = []
        dir_ = dir_all[i]
        for file in dir_:
            if file != []:
                U_file = file + U_name
                X_file = file + X_name
                U = sp.load_npz(U_file)
                X = sp.load_npz(X_file)
                X_SE_mean, sub_SSE, loss, result, chazhi = GetSE(X, U, i, alpha=0.1, beta=0.15)
                SSE_alli.append(['X_SE_mean:', X_SE_mean, 'sub_SSE:',
                                 sub_SSE, 'loss', loss, 'result', result])
                CZi.append(chazhi)
                LOSSi.append(loss)
                SSE_resulti.append(result)
                shangi.append((X_SE_mean, sub_SSE))

        CZ.append(CZi)
        LOSS.append(LOSSi)
        shang.append(shangi)
        SSE_all.append(SSE_alli)
        SSE_result.append(SSE_resulti)

    for i in range(len(SSE_result)):
        result = SSE_result[i]
        for j in range(len(result)):
            get_filename = get_dir[i][j]
            if get_filename == []:
                sub_file = ''
            else:
                sub_file = ''.join(get_filename)
            resulti = result[j]
            if resulti != True:
                for n in range(5):
                    filename = path_datacut + os.path.sep + sub_file + str(n)
                    os.remove(filename + '-feature.csv')
                    os.remove(filename + '-word.csv')
                    os.remove(filename + '-poi.csv')


if __name__ == '__main__':
    # 设置要可视化的源文件夹
    data_path = "2019-06-02-18-32-08"

    postPrune(data_path)
