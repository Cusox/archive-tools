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

def update_dictionary(user_id, history):
	sql = "select id, weight from article_category_data where id in {}".format(tuple(history))
	cur.execute(sql)
	weights = cur.fetchall()
	null_vector = np.zeros(word_num) # 创造一个一维，长度为 word_num 的零向量
	print('一维零向量生成完毕')
	for index in range(len(weights)):
		# print(weights[index][0])
		dat = weights[index][1][1:-1].split(',')
		dat_vector = list(map(float, dat)) # 把取出来的字符串转为 float 类型并放入集合中
		temp_vector = np.array(dat_vector) # 生成向量
		null_vector += temp_vector # 与零向量相加
	print('遍历完毕')
	user_vector = (null_vector / len(weights)).tolist() # 获得平均向量作为用户向量
	result = '['+','.join([str('{:.10f}'.format(item) if item != 0.0 else item) for item in user_vector])+']' # 固定生成的字符串格式，如果不为零保留十位小数，为零不改变
	print('字符串格式固定完毕')
	sql = "update user set user_dictionary = '{result}', updated = 'true' where id = {user_id}".format(result = result, user_id = user_id) # 把用户向量插入 user 中
	cur.execute(sql)
	mysql.commit()
	print('提交完毕')

def cosine_similarity(vector1, vector2): # 求两向量之间的夹角
    molecule = 0.0 # 初始化
    denominatorA = 0.0
    denominatorB = 0.0
    for a, b in zip(vector1, vector2):
        if(a != 0 or b != 0):
            molecule += a * b # 计算分子
            denominatorA += a ** 2 # 计算分母
            denominatorB += b ** 2
    if denominatorB == 0.0 or denominatorB == 0.0: # 分母不为0
        return 0
    else: # 计算两个向量的夹角
        return round(molecule / ((denominatorA ** 0.5) * (denominatorB ** 0.5)) * 100, 2) # 乘以 100 防止数据过小

def recommend_posts(user_dictionary):
	print("开始生成向量")
	dat = user_dictionary[2][1:-1].split(',') # 取出对应的数据
	dat_vector = list(map(float, dat)) # 把取出来的字符串转为 float 类型并放入集合中
	user_vector = np.array(dat_vector) # 生成向量
	print("生成向量成功")
	print(user_dictionary[1])
	sql = "select id, weight from article_category_data where id not in {} limit 5000".format(tuple(user_dictionary[1].split(','))) # limit限制数量
	cur.execute(sql)
	posts = cur.fetchall()
	print("查找文章成功")
	topK = []
	cos = ()
	for post in posts:
		data = post[1][1:-1].split(',') # 取出对应的数据
		data_vector = list(map(float, data)) # 把取出来的字符串转为 float 类型并放入集合中
		post_vector = np.array(data_vector) # 生成向量
		num_cos = cosine_similarity(user_vector, post_vector)
		cos = (num_cos, post[0])
		if (len(topK) < 10):
			topK.append(cos) # 加入 topK 当中
			topK.sort(reverse = True) # 从大到小排序
		else:
			if (cos[0] > topK[0][0]): # 如果现在这个余弦夹角比 topK 中的最大值还大，即更加相关，则插入到头部
				topK[9] = topK[8]
				topK[8] = topK[7]
				topK[7] = topK[6]
				topK[6] = topK[5]
				topK[5] = topK[4]
				topK[4] = topK[3]
				topK[3] = topK[2]
				topK[2] = topK[1]
				topK[1] = topK[0]
				topK[0] = cos
		# print("okkkkkkkkkkkkkkkkkkkkkkk")
	print("user", user_dictionary[0], ':', topK)
	top = []
	for index in range(len(topK)):
		top.append(topK[index][1])
	top_str = ','.join(str(x) for x in top)
	# print(','.join(str(x) for x in top))
	sql = "update user set recommend = '{top_str}' where id = {user_id}".format(top_str = top_str, user_id = user_dictionary[0])
	cur.execute(sql)
	mysql.commit()
	
if __name__ == '__main__':
	sql = "select dictionary from article_dictionary" # 在 article_dictionary 中读取词库
	cur.execute(sql)
	dictionary = cur.fetchone() # 只有一行数据
	print('已查询到字典')
	dictionary_list = ','.join(dictionary).split(',')
	word_num = len(dictionary_list)
	sql = "select id, user_history from user where updated = 'false'" # 在 user 中读取 user_history
	cur.execute(sql)
	results = cur.fetchall()
	print(results)
	for result in results:
		# print(result[0])
		history = ''.join(result[1]).split(',')
		# print(history)
		update_dictionary(result[0], history)
	sql = "select id, user_history, user_dictionary from user where user_dictionary is not null and recommend is null"
	cur.execute(sql)
	re_results = cur.fetchall()
	for re_result in re_results:
		# print(re_result)
		recommend_posts(re_result)
