# encoding = utf-8
import pymysql
import jieba
import jieba.analyse

mysql = pymysql.connect(host="host", port=port, user="user", passwd="password", db="database", charset = "utf8") # 连接数据库
cur = mysql.cursor() # 生成游标

def Vector_Reader(): # 读取所有文章类型的平均向量
	sql = "select category, category_weight from article_category_weight" # 在 article_category_weight 中读取文章种类和该种类的平均向量
	cur.execute(sql)
	categories_weight = cur.fetchall()  # 每一行的数据
	vectors = []
	for index in range(len(categories_weight)):
		vectors.append((categories_weight[index][0], categories_weight[index][1]))
	return vectors
	
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
 

def Cos_Comparer(result, vectors, dictionary): # 通过比较两个向量的cos值来判断相似度,传入的参数分别是未分类的文章,多个类型的平均向量,字典
    post_id = result[0] # 获取当前数据的id
    post = result[1] # 获取当前数据的文本内容
    words = jieba.analyse.extract_tags(post, withWeight = True, allowPOS = 'n', topK = 20)
    words_weight = {tag: weight for tag, weight in words}
    # print('words_weight : ', words_weight)
    # print("============")
    dictionary_list = ','.join(dictionary).split(',') # 字符串变成列表
    vector = [] # 未分类的文章的文章向量
    for index_word in dictionary_list: # 枚举词库中的每个词
        if index_word in words_weight: # 如果新文章中存在这个词
            vector.append(words_weight[index_word]) # 把权重加入 vector 列表中
        else:
            vector.append(0) # 否则为0
    # print(vector) # 新输入的文章向量
    topK = [] # 将该文章的向量和所有文章类别的平均向量比较，获取相关度为前三的类别
    cos = ()
    for v in vectors:
        temp_v = v[1][1:-1].split(',') # 取每类文章的平均向量
        temp_f_v = list(map(float, temp_v)) # 字符串转数的集合
        num_cos = cosine_similarity(vector, temp_f_v) # 计算未分类文章和每类文章的平均向量的相关度
        cos = (v[0], num_cos) # 格式 ('科技', 9.8)
        if (len(topK) < 3): # 只保留前三个数据, 此时集合中少于三个元素
            topK.append(cos) # 加入 topK 当中
            topK.sort(reverse = True) # 从大到小排序
        else: # 集合中多于三个元素
            if (cos[1] > topK[0][1]): # 如果现在这个余弦夹角比 topK 中的最大值还大，即更加相关，则插入到头部
                tmp = topK[1]
                topK[1] = topK[0]
                topK[0] = cos
                topK[2] = tmp
 
    print('post', post_id, ':', topK)
    sql = "update article set category = '{top}' where id = {post_id}".format(top = topK[0][0], post_id = post_id)
    # print(sql)
    cur.execute(sql)
    mysql.commit()


vectors = Vector_Reader() # 获得所有类型的平均向量
print('已获得向量')
sql = "select dictionary from article_dictionary" # 在 article_dictionary 中读取词库
cur.execute(sql)
dictionary = cur.fetchone() # 只有一行数据
print('已查询到字典')
sql = "select id, content from article where category is null" # 在 article 中读取未分类的文章
cur.execute(sql)
results = cur.fetchall()
print('拉取到数据')
for result in results:
	Cos_Comparer(result, vectors, dictionary)
mysql.close()
