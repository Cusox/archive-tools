# -*- coding: UTF-8 -*-
import os
import jieba

def readfile(path): # 读取文件
	with open(path, "rb") as fp:
		content = fp.read()
	return content

def savefile(path, content): # 保存文件
	with open(path, "wb") as fp:
		fp.write(content)

def corpus_segment(corpus_path, corpus_seg_path):
	catelist = os.listdir(corpus_path) # 获取 corpus_path 下所有子目录
	for cate in catelist:
		cate_path = corpus_path + cate + '/'
		cate_seg_path = corpus_seg_path + cate + '/'
		if not os.path.exists(cate_seg_path): # 不存在分词目录则创建
			os.makedirs(cate_seg_path)
		textlist = os.listdir(cate_path) # 获取一个分类下的所有文本
		for text in textlist:
			text_path = cate_path + text
			content = readfile(text_path)
			content = content.replace('\r\n'.encode('utf-8'), ''.encode('utf-8')).strip() # 删除换行
			content = content.replace(' '.encode('utf-8'), ''.encode('utf-8')).strip() # 删除空行、多余的空格
			content_seg = jieba.cut(content)  # 分词
			savefile(cate_seg_path + text, ' '.join(content_seg).encode('utf-8'))
	print("分词结束")

if __name__ == "__main__":
	# 对训练集进行分词
	corpus_path = "train_corpus/" # 未分词已分类的语料库
	corpus_seg_path = "train_corpus_seg/" # 已分词已分类的语料库
	corpus_segment(corpus_path, corpus_seg_path)
	
	# 对测试集进行分词
	corpus_path = "test_corpus/" # 未分词已分类的语料库
	corpus_seg_path = "test_corpus_seg/" # 已分词已分类的语料库
	corpus_segment(corpus_path, corpus_seg_path)
