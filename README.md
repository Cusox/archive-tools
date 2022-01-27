# ArchiveTools

一些以前写过的可能有用的功能

## Text_Summarizer_cn

中文文章自动摘要：

- 预训练的词向量文件来自 https://github.com/Embedding/Chinese-Word-Vectors
- 停用词可使用 res 文件夹下的，也可使用 https://github.com/goto456/stopwords

## TF-IDF 文章分类系统

目录文件：

- **Dictionnary_Builder.py**

  构建词库和各类文章的平均向量

- **Post_Classify.py**

  将未分类的文章和各类文章的平均向量进行比对

### 数据库表

- **article**

  未分类的文章，字段最低需求：

  - id int 非空 键
  - category varchar 可空
  - content longtext 非空

- **article_category_data**

  已分类的文章，字段最低需求：

  - id int 非空 键

  - category varchar 非空

  - content longtext 非空

  - weight longtext 可空


- **article_category_weight**

  各类文章的平均向量，字段最低需求：

  - id int 非空 键


  - category varchar 非空

  - category_weight longtext 非空

- **article_dictionary**

  词库，字段最低需求：

  - id int 非空 键

  - dictionary longtext 非空


**Tips：**

- **由于大部分代码和 id 绑定在一起，如果原数据库表有数据可能会有bug存在**
- **代码中的分类可调，相应的已分类的文章需要提供**

## TF-IDF 简易文章推荐系统

### 数据库表

- **article_dictionary**

  数据量尽量大，不然有些文章生成向量为空（找不到分词的话会变成零向量）：

  - id int 非空 键
  - dictionary longtext 可空

- **user**

  存放用户数据的表：

  - id int 非空 键
  - user_history longtext 可空
  - user_dictionary longtext 可空
  - updated varchar 30 非空，只有两个值：true false
  - recommend longtext 可空

- **article（代码中是article_category_data，用了测试时的数据）**

  存放文章基本信息的表：

  - id int 非空 键
  - weight longtext 可空

- **Tips：**

  - **sql = "select id, weight from article_category_data where id not in {} limit 5000".format(tuple(user_dictionary[1].split(','))) 的 limit 5000 是用来限制文章数量的，可以修改成通过时间进行限制**
  - **dictionary 的数据量一定要够大，如果一篇文章的关键字都在 dictionary 中找不到的话则会变成零向量，可以和分类系统中通过构建得到词库的 dictionary 是同一张表**
  - **article 中的 weight 最好在爬取文章的时候就算出来**

## Bayes_Category

按照顺序运行

- **corpus_segment.py**
- **corpus_to_Bunch.py** 请自觉创建目录 **train_word_bag** 和 **test_word_bag**
- **TFIDF_space.py**
- **NBayes_Predict.py**

**stopwords.txt** 为停用词表

本仓库是博客文章《[利用朴素贝叶斯模型进行的中文文本类别预测 ](https://lsilencej.top/2021/10/24/category_nbayes)》的源代码

## Article_Recommender

文章推荐系统（思路优化版）

目录文件：

- **article_keywords.py** 文章关键词提取
- **user_article.py** 用户关键词列表生成
- **article_comparator.py** 文章用户兴趣拟合度比较

本仓库是博客文章《[文章推荐系统（思路优化版） ](https://lsilencej.top/2021/10/26/article_recommender/)》的源代码，思路仅供参考

