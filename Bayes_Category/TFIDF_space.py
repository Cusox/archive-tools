import pickle
from sklearn.datasets._base import Bunch
from sklearn.feature_extraction.text import TfidfVectorizer

def readfile(path): # 读取文件
	with open(path, "rb") as fp:
		content = fp.read()
	return content

def readbunchobj(path):
	with open(path, "rb") as fp:
		bunch = pickle.load(fp)
	return bunch

def writebunchobj(path, bunchobj):
	with open(path, "wb") as fp:
		pickle.dump(bunchobj, fp)

def vector_space(stopword_path, bunch_path, space_path, train_tfidf_path = None):
	stopwordlist = readfile(stopword_path).splitlines()
	bunch = readbunchobj(bunch_path)
	tfidfspace = Bunch(target_name = bunch.target_name, label = bunch.label, filenames = bunch.filenames, tdm = [], vocabulary = {})
	'''
	tdm	TF-IDF矩阵
	vocabulary 词典索引
	'''
	if train_tfidf_path is not None:
		trainbunch = readbunchobj(train_tfidf_path)
		tfidfspace.vocabulary = trainbunch.vocabulary
		vectorizer = TfidfVectorizer(stop_words = stopwordlist, sublinear_tf = True, max_df = 0.5, vocabulary = trainbunch.vocabulary)
		'''
		sublinear_tf 计算tf值采用亚线性策略
		max_df 设置阙值，达到直接加入临时停用词
		'''
		tfidfspace.tdm = vectorizer.fit_transform(bunch.contents)
	else:
		vectorizer = TfidfVectorizer(stop_words = stopwordlist, sublinear_tf = True, max_df = 0.5)
		tfidfspace.tdm = vectorizer.fit_transform(bunch.contents)
		tfidfspace.vocabulary = vectorizer.vocabulary_ # vocabulary_ 向量空间坐标轴信息
	writebunchobj(space_path, tfidfspace)
	print("tf-idf词向量空间实例创建成功！！！")

if __name__ == "__main__":
	stopword_path = "train_word_bag/stopwords.txt"
	bunch_path = "train_word_bag/train_set.dat"
	space_path = "train_word_bag/tfidfspace.dat"
	vector_space(stopword_path, bunch_path, space_path)
	
	bunch_path = "test_word_bag/test_set.dat"
	space_path = "test_word_bag/testspace.dat"
	train_tfidf_path = "train_word_bag/tfidfspace.dat"
	vector_space(stopword_path, bunch_path, space_path, train_tfidf_path)
