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

def get_category(article_id):
	sql = "select category from article where id = {}".format(article_id)
	cur.execute(sql)
	result = cur.fetchone()
	return result[0]

def user_dictionary_generator(user_result):
	histories = tuple(user_result[1].split(','))
	if (user_result[2] == None):
		dictionary = {}
	else:
		dictionary = json.loads(user_result[2])
	for history in histories:
		sql = "select keywords from article where id = {}".format(history)
		cur.execute(sql)
		result = cur.fetchone()
		dic_result = json.loads(result[0])
		print(type(dic_result))
		for key, value in dic_result.items():
			if key in dictionary.keys():
				dictionary[key] += value
			else:
				dictionary[key] = value
	print(dictionary)
	sql = "update user set user_dictionary = '{dictionary}' where id = {user_id}".format(dictionary = json.dumps(dictionary, ensure_ascii = False), user_id = user_result[0])
	cur.execute(sql)
	mysql.commit()
	# print("commit")
		

if __name__ == '__main__':
	sql = "select id, user_history, user_dictionary from user where updated = 'true'"
	cur.execute(sql)
	results = cur.fetchall()
	for result in results:
		user_dictionary_generator(result)
