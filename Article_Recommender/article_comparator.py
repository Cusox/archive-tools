# coding = utf-8
import sys
import pymysql
import json
import jieba
import jieba.analyse
import numpy as np

np.set_printoptions(threshold = sys.maxsize)
np.set_printoptions(suppress = True) # 不使用科学计数法
mysql = pymysql.connect(host="bj-cynosdbmysql-grp-2r0nnbpu.sql.tencentcdb.com", port=22241, user="tmp", passwd="Aa1@0000", db="lsilencej_test_post", charset = "utf8") # 连接数据库
cur = mysql.cursor() # 生成游标

def user_recommend(user):
	dictionary = json.loads(user[2])
	histories = tuple(user[1].split(','))
	sql = "select id, keywords, content from article where id not in {}".format(tuple(histories))
	cur.execute(sql)
	results = cur.fetchall()
	topK = []
	rel = ()
	for result in results:
		keywords = json.loads(result[1])
		article_sum = 0
		for key, value in keywords.items():
			if key in dictionary.keys():
				article_sum += value * dictionary[key]
		rel = (article_sum, result[0], result[2])
		topK.append(rel)
	topK.sort(reverse = True) # 从大到小排序, article_sum为文章与用户字典的相关度, result[0]为推荐的文章id, result[2]为推荐的文章内容
	recommend = []
	# print(user[0], ':') # 这段打印的已经测试过了, 转字符串的程序还没测试
	for index in range(15):
		# print(topK[index])
		recommend.append(topK[index][1])
	str_recommend = ','.join([str(r) for r in recommend])
	sql = "update user set user_recommend = '{str_recommend}'".format(str_recommend = str_recommend)
	cur.execute(sql)
	mysql.commit()

if __name__ == '__main__':
	sql = "select id, user_history, user_dictionary from user where recommend is null"
	cur.execute(sql)
	results = cur.fetchall()
	for result in results:
		user_recommend(result)
