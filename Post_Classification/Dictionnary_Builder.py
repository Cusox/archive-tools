# encoding = utf-8
import sys
import pymysql
import jieba
import jieba.analyse
import numpy as np

np.set_printoptions(threshold = sys.maxsize)
np.set_printoptions(suppress = True) # 不使用科学计数法
mysql = pymysql.connect(host="host", port=port, user="user", passwd="password", db="database", charset = "utf8") # 连接数据库
cur = mysql.cursor() # 生成游标
word_num = 0


def Dictionary_Builder(posts):
	merged_words = [] # 用来存放所有词的 list
	post_words = [] # post_words 是把每一条数据的 id 和生成的分词情况保存下来的list
	for index in range(len(posts)): # 遍历每一篇文章
		words = jieba.analyse.extract_tags(posts[index][1], withWeight = True, allowPOS = 'n', topK = 5) # 为每一篇文章分词(allowPOS = 'n'代表分为名词词性)，为每个词打上权重，取权重最大的前5个词语
		words_weight = {tag: weight for tag, weight in words} # 分开词和权重并存入 words_weight 中
		merged_words = set(words_weight.keys()) | set(merged_words) # 将词放入 set 中进行去重并整合成一个大的 list
		post_words.append((posts[index][0], words_weight)) # 把该条数据的 id 和所分的词加入到 post_words 中
	dictionary = ','.join(merged_words) # 通过逗号分隔所有词，构成词库
	word_num = len(merged_words) # 记录词的总数, 后面作为维数使用
	sql = "insert into article_dictionary values(null, '{dictionary}')".format(dictionary = dictionary) # 把词库插入数据库表 article_dictionary
	cur.execute(sql)
	mysql.commit()
	print('词库写入完毕')
	print('正在生成已分类文章的向量')
	for post_word in post_words: # post_word 是 (id, (tag, weight)) 的形式
		vector = [] # 清空 vector 集合
		for merged_word in merged_words: # 在词库中遍历每个词
			if merged_word in post_word[1].keys(): # 如果文章中存在词库中的遍历到的这个词
				vector.append(post_word[1][merged_word]) # 把权重放入对应词的位置
			else: 
				vector.append(0) # 否则为0
		sql = "update article_category_data set weight = '{vector}' where id = {post_id}".format(vector = vector, post_id = post_word[0]) # 把每条数据的权重值集合插入表中
		cur.execute(sql)
		mysql.commit()
		# print('-----------------提交成功------------------------')

def Ave_Vector_Builder(index, category): # 计算每一类文章的平均向量
	sql = "select id, weight from article_category_data where category='{category}'".format(category = category)
	cur.execute(sql)
	cated_posts = cur.fetchall()  # 所有的这一类的文章的 id, 权重 集合
	null_vector = np.zeros(word_num) # 创造一个一维，长度为 word_num 的零向量
	print('一维零向量生成完毕')
	for i in range(len(cated_posts)): # 遍历每一条数据
		dat = cated_posts[i][1][1:-1].split(',') # 取出对应的数据
		dat_vector = list(map(float, dat)) # 把取出来的字符串转为 float 类型并放入集合中
		temp_vector = np.array(dat_vector) # 生成向量
		null_vector += temp_vector # 与零向量相加
	print('遍历完毕')
	ave_vector = (null_vector / len(cated_posts)).tolist() # 获得平均向量
	result = '['+','.join([str('{:.10f}'.format(item) if item != 0.0 else item) for item in ave_vector])+']' # 固定生成的字符串格式，如果不为零保留十位小数，为零不改变
	print('字符串格式固定完毕')
	sql = "insert into article_category_weight values({index}, '{category}', '{result}')".format(index = index, category = category, result = result) # 把 id, 分类, 该分类的平均向量插入 article_category_weight 中
	cur.execute(sql)
	mysql.commit()
	print('提交完毕')

if __name__ == '__main__':
	sql = 'select id, category, content from article_category_data where content is not null' # 在数据库表 article_category_data 中查询内容不为空的文章数据
	cur.execute(sql) # 执行sql
	datas = cur.fetchall()   # 每一行的数据的集合
	posts = [] # 存储文章的列表
	print('拉取数据')
	for index in range(len(datas)):
		posts.append((datas[index][0], datas[index][2])) # 把 id 和 content 作为一个值构建一个 posts 集合
	print('数据拉取并且遍历完毕')
	Dictionary_Builder(posts) # 运行
	print(' Dictionary_Builder 运行结束, 词库已生成')
	cate =['文化', '娱乐', '体育', '财经', '科技', '游戏'] # 类别
	for index in range(len(cate)): # 对每一类文章进行枚举
		Ave_Vector_Builder(index + 1, cate[index]) # id 从 1 开始
	mysql.close()
