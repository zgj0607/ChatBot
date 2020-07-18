#!/usr/bin/python                                                                                                                                                                                                                    
# coding=utf-8

# File Name: test.py
# Author   : john
# Mail     : john.y.ke@mail.foxconn.com
# Created Time: Sat 01 Sep 2018 05:38:56 PM CST

import jieba
import pandas as pd
from numpy import *


def loadDataSet():
    postingList = [['落叶', '帅'],
                   ['傻逼'],
                   ['皮蛋', '瘦肉粥', '美味'],
                   ['智障'],
                   ['生活', '潇洒'],
                   ['白痴']]
    classVec = [0, 1, 0, 1, 0, 1]  # 1 侮辱言论   0正常言论

    return postingList, classVec


def createVocabList(dataSet):
    """
    获取所有单词的集合
    :param dataSet: 数据集
    :return: 所有单词的集合(即不含重复元素的单词列表)
    """
    vocabSet = set([])
    for document in dataSet:
        vocabSet = vocabSet | set(document)  # union of the two sets

    return list(vocabSet)


def setOfWords2Vec(vocabList, inputSet):
    """
    遍历查看该单词是否出现，出现该单词则将该单词置1
    :param vocabList: 所有单词集合列表
    :param inputSet: 输入数据集
    :return: 匹配列表[0,1,0,1...]，其中 1与0 表示词汇表中的单词是否出现在输入的数据集中
    """
    returnVec = [0] * len(vocabList)  # 创建一个和词汇表等长的向量，并将其元素都设置为0
    for word in inputSet:  # 遍历文档中的所有单词，如果出现了词汇表中的单词，则将输出的文档向量中的对应值设为1
        if word in vocabList:
            returnVec[vocabList.index(word)] = 1
        else:
            print("the word: %s is not in my Vocabulary!" % word)
    return returnVec


def trainNB0(trainMatrix, trainCategory):
    """
    训练数据优化版本
    :param trainMatrix: 文件单词矩阵
    :param trainCategory: 文件对应的类别
    :return:
    """
    # 总文件数
    numTrainDocs = len(trainMatrix)
    print("总文件数： ", numTrainDocs)
    # 总单词数
    numWords = len(trainMatrix[0])
    print("总单词数： ", numWords)
    # 侮辱性文件的出现概率
    pAbusive = sum(trainCategory) / float(numTrainDocs)
    # 构造单词出现次数列表
    # p0Num 正常的统计
    # p1Num 侮辱的统计
    p0Num = ones(numWords)  # [0,0......]->[1,1,1,1,1.....]
    p1Num = ones(numWords)

    # 整个数据集单词出现总数，2.0根据样本/实际调查结果调整分母的值（2主要是避免分母为0，当然值可以调整）
    # p0Denom 正常的统计
    # p1Denom 侮辱的统计
    p0Denom = 2.0
    p1Denom = 2.0
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            # 累加辱骂词的频次
            p1Num += trainMatrix[i]
            # 对每篇文章的辱骂的频次 进行统计汇总
            p1Denom += sum(trainMatrix[i])
        else:
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    # 类别1，即侮辱性文档的[log(P(F1|C1)),log(P(F2|C1)),log(P(F3|C1)),log(P(F4|C1)),log(P(F5|C1))....]列表
    p1Vect = log(p1Num / p1Denom)
    # 类别0，即正常文档的[log(P(F1|C0)),log(P(F2|C0)),log(P(F3|C0)),log(P(F4|C0)),log(P(F5|C0))....]列表
    p0Vect = log(p0Num / p0Denom)
    return p0Vect, p1Vect, pAbusive


def classifyNB(vec2Classify, p0Vec, p1Vec, pClass1):
    """
    使用算法：
        # 将乘法转换为加法
        乘法：P(C|F1F2...Fn) = P(F1F2...Fn|C)P(C)/P(F1F2...Fn)
        加法：P(F1|C)*P(F2|C)....P(Fn|C)P(C) -> log(P(F1|C))+log(P(F2|C))+....+log(P(Fn|C))+log(P(C))
    :param vec2Classify: 待测数据[0,1,1,1,1...]，即要分类的向量
    :param p0Vec: 类别0，即正常文档的[log(P(F1|C0)),log(P(F2|C0)),log(P(F3|C0)),log(P(F4|C0)),log(P(F5|C0))....]列表
    :param p1Vec: 类别1，即侮辱性文档的[log(P(F1|C1)),log(P(F2|C1)),log(P(F3|C1)),log(P(F4|C1)),log(P(F5|C1))....]列表
    :param pClass1: 类别1，侮辱性文件的出现概率
    :return: 类别1 or 0
    """
    # 计算公式  log(P(F1|C))+log(P(F2|C))+....+log(P(Fn|C))+log(P(C))
    # 大家可能会发现，上面的计算公式，没有除以贝叶斯准则的公式的分母，也就是 P(w) （P(w) 指的是此文档在所有的文档中出现的概率）就进行概率大小的比较了，
    # 因为 P(w) 针对的是包含侮辱和非侮辱的全部文档，所以 P(w) 是相同的。
    # 使用 NumPy 数组来计算两个向量相乘的结果，这里的相乘是指对应元素相乘，即先将两个向量中的第一个元素相乘，然后将第2个元素相乘，以此类推。
    # 我的理解是：这里的 vec2Classify * p1Vec 的意思就是将每个词与其对应的概率相关联起来
    p1 = sum(vec2Classify * p1Vec) + log(pClass1)  # P(w|c1) * P(c1) ，即贝叶斯准则的分子
    p0 = sum(vec2Classify * p0Vec) + log(1.0 - pClass1)  # P(w|c0) * P(c0) ，即贝叶斯准则的分子·
    if p1 > p0:
        return 1
    else:
        return 0


# 创建停用词list
def stopwordslist(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r', encoding='utf-8').readlines()]
    return stopwords


# 对句子进行分词
def wordCut(sentence):
    words = jieba.cut(sentence.strip())
    stopwords = stopwordslist(
        '/chatbot/corpus/vocabulary/StopWords.txt')  # 这里加载停用词的路径
    outstr = []
    for word in words:
        if word not in stopwords:
            if word != '\t':
                outstr.append(word)
    return outstr


def DataHandle(filename, flag):
    out = []
    lines = pd.read_table(filename, header=None, encoding='utf-8', names=['评论'])
    for line in lines['评论']:
        line = str(line)
        outStr = wordCut(line)  # 这里的返回值是字符串
        out.append(outStr)

    if flag:
        Vec = [1] * lines.shape[0]
    else:
        Vec = [0] * lines.shape[0]

    return Vec, out


if __name__ == '__main__':
    googDataPath = '/Users/zhou/Documents/PycharmProject/ChatBot/chatbot/corpus/classify/good.txt'
    badDataPath = '/Users/zhou/Documents/PycharmProject/ChatBot/chatbot/corpus/classify/bad.txt'

    # 1 好评     0 差评
    goodVec, goodList = DataHandle(googDataPath, 1)
    badVec, badList = DataHandle(badDataPath, 0)

    listClasses = goodVec + badVec
    listOPosts = goodList + badList
    print(listClasses)
    print(listOPosts)

    myVocabList = createVocabList(listOPosts)
    print(myVocabList)
    # 3. 计算单词是否出现并创建数据矩阵
    trainMat = []
    for postinDoc in listOPosts:
        trainMat.append(setOfWords2Vec(myVocabList, postinDoc))
    # 4. 训练数据
    p0V, p1V, pAb = trainNB0(array(trainMat), array(listClasses))
    # 5. 测试数据
    while True:
        inputS = input(u'请输入您对本商品的评价：')

        testEntry = wordCut(inputS)
        thisDoc = array(setOfWords2Vec(myVocabList, testEntry))
        print('评价: ', classifyNB(thisDoc, p0V, p1V, pAb))
