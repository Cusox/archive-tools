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

def text_keywords(article_id, article):
	keywords = jieba.analyse.extract_tags(article, topK=5, withWeight=True, allowPOS=('n'))
	words_weight = {keyword: weight * 100 for keyword, weight in keywords}
	str_keywords = json.dumps(words_weight, ensure_ascii = False)
	sql = "update article set keywords = '{str_keywords}' where id = {article_id}".format(str_keywords = str_keywords, article_id = article_id)
	cur.execute(sql)
	mysql.commit()
	# print("Complete")
		
if __name__ == '__main__':
	sql = "select id, content from article where keywords is null"
	cur.execute(sql)
	results = cur.fetchall()
	for result in results:
		text_keywords(result[0], result[1])
