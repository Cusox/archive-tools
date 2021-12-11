# coding = utf-8
import re
import jieba
import numpy as np
import networkx as nx
from sklearn.metrics.pairwise import cosine_similarity
import pymysql
import os
import configparser
class TextSummarizer:
	def  __init__(self, article, num): # 初始化
		self.article = article
		self.num = num
		self.word_embeddings = {}
		self.stopwords = None
		self.sentences_vectors = []
		self.similarity_matrix = None
		self.ranked_sentences = None
		self.text_str = ""
	
	def __word_embeddings(self): # 获取词向量
		for i, line in enumerate(open('res/sgns.sogou.char', encoding = 'utf-8').readlines()):
			if i != 0: # 第一行为统计信息，去除
				values = line.split()
				word = values[0] # 第一个为所表示的词
				dimen = np.asarray(values[1:], dtype='float32') # 后面的为维度
				self.word_embeddings[word] = dimen
	
	def __stopwords(self): # 获取停用词
		self.stopwords = [line.strip() for line in open('res/stopwords.txt', encoding='utf-8').readlines()] # for循环放在后面相对于列表来说处理的更快
		
	def __sentences(self, sentences): # 断句
		# 分号、破折号、英文双引号做了忽略
		for sentence in sentences:
			sentence = re.sub('([（），。！？\?])([^”’])', r'\1\n\2', sentence)  # 单字符断句符
			sentence = re.sub('(\.{6})([^”’])', r'\1\n\2', sentence)  # 英文省略号
			sentence = re.sub('(\…{2})([^”’])', r'\1\n\2', sentence)  # 中文省略号
			sentence = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', sentence) # \n放到双引号后
			sentence = sentence.rstrip() # 去掉末尾多余的\n
			sentence.split("\n")
			# print(sentences[:5])
		return sentences
        
	def __remove_stopwords(self, sentence): # 去除停用词
		sentence = [i for i in sentence if i not in self.stopwords]
		return sentence		 
        
	def __sentence_vectors(self, cleaned_sentences): # 获取句向量，将句子中的每个词向量相加取均值
		for i in cleaned_sentences:
			if len(i) != 0:
				ave = sum([self.word_embeddings.get(j.strip(), np.zeros((300,))) for j in i]) / (len(i) + 1e-2) # 预训练的词向量维度为300
				# np.zeros返回来一个给定形状和类型的用0填充的数组；
				# zeros(shape, dtype=float, order='C')
				# shape:形状
				# dtype:数据类型，可选参数，默认numpy.float64
				# order:可选参数，C代表行优先；F代表列优先
			else:
				ave = np.zeros((300,)) # 预训练的词向量维度为300
			self.sentences_vectors.append(ave)
	
	def __similarity_matrix(self): # 基于余弦相似度计算相似度矩阵
		self.similarity_matrix = np.zeros((len(self.sentences_vectors), len(self.sentences_vectors))) # 以句向量列表的长度构建方阵
		for i in range(len(self.sentences_vectors)):
			for j in range(len(self.sentences_vectors)):
				if i != j:
					self.similarity_matrix[i][j] = cosine_similarity(self.sentences_vectors[i].reshape(1, -1), self.sentences_vectors[j].reshape(1, -1)) # 计算两个矩阵的余弦相似度
					# reshape(1, -1)指的是变成一行，-1表示不知道分多少列
       
	def generate_summary(self):
		self.__word_embeddings() # 获取词向量
		self.__stopwords() # 获取停用词
		sentences = self.__sentences(self.article) # 将文章分割成句子
		cutted_sentences = [jieba.lcut(s) for s in sentences] # 对每个句子分词
		cleaned_sentences = [self.__remove_stopwords(sentence) for sentence in cutted_sentences] # 去除停用词
		self.__sentence_vectors(cleaned_sentences) # 获取句向量
		self.__similarity_matrix() # 获取相似度矩阵
		nx_graph = nx.from_numpy_array(self.similarity_matrix) # 将相似度矩阵转换为图的结构
		scores = nx.pagerank(nx_graph) # 获得句子间的相关度分数
		self.ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse = True) # 根据得分进行降序排序
		for i in range(self.num): # 获取得分前几的句子
			self.text_str += self.ranked_sentences[i][1]
			# print(self.ranked_sentences[i][1])
		# print(self.text_str)
		return self.text_str

class ReadConfig:
	def __init__(self):
		mysql_config_path = os.path.join('', 'mysql_config.ini')
		self.cf = configparser.ConfigParser()
		self.cf.read(mysql_config_path, encoding = 'utf-8')
		
	def __mysql_read(self, param):
		val = self.cf.get('mysql', param)
		return val
		
	def mysql_config(self):
		mysql = pymysql.connect( # 连接数据库
			host = self.__mysql_read('host'), 
			port = int(self.__mysql_read('port')), 
			user = self.__mysql_read('user'), 
			passwd = self.__mysql_read('password'), 
			db = self.__mysql_read('datebase'), 
			charset = self.__mysql_read('charset'))
		cur = mysql.cursor() # 创建游标
		try:
			sql = 'select id, content from article where summary is null' # 编写sql
			cur.execute(sql) # 执行sql
			D = cur.fetchall() # 查看结果
			print(D)
			for d in D:
				# print(d[1])
				summary = TextSummarizer(d[1].split("\n"), 3).generate_summary()
				# print(summary + "\n")
				sql = 'update article set summary = %s where id = %s'
				cur.execute(sql, (summary, d[0]))
			mysql.commit()
			mysql.close()
		except IOError as msg:
			print("ERROR ! ! !")
			print(str(msg))
			mysql.rollback()
			mysql.close()
		
ReadConfig().mysql_config()
