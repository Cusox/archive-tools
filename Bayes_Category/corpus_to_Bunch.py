# -*- coding: UTF-8 -*-  
import os
import pickle
from sklearn.datasets._base import Bunch

def readfile(path): # 读取文件
	with open(path, "rb") as fp:
		content = fp.read()
	return content

def corpus2Bunch(wordbag_path, seg_path):
	catelist = os.listdir(seg_path) # 获取分类信息
	bunch = Bunch(target_name = [], label = [], filenames = [], contents = [])
	bunch.target_name.extend(catelist) # 填充 bunch 中的 tatget_name list
	for cate in catelist:
		cate_path = seg_path + cate + '/'
		textlist = os.listdir(cate_path)
		for text in textlist:
			text_path = cate_path + text
			bunch.label.append(cate)
			bunch.filenames.append(text_path)
			bunch.contents.append(readfile(text_path))
	with open(wordbag_path, "wb") as fp:
		pickle.dump(bunch, fp)
	print("构建文本对象结束")

if __name__ == "__main__":
	# 对训练集进行Bunch化操作
	wordbag_path = "train_word_bag/train_set.dat" # Bunch 存储路径
	seg_path = "train_corpus_seg/" # 已分词已分类的语料库
	corpus2Bunch(wordbag_path, seg_path)
	
	# 对测试集进行Bunch化操作
	wordbag_path = "test_word_bag/test_set.dat" # Bunch 存储路径
	seg_path = "test_corpus_seg/" # 已分词已分类的语料库
	corpus2Bunch(wordbag_path, seg_path)
