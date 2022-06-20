import pymongo

myclient = pymongo.MongoClient('mongodb://localhost:27017/')


def createdatabase(key):
    mydb = myclient[key]


def uploaddata(key1, duplicates, keyword, words, query, retries, elapsed):
    mydb = myclient[keyword]
    mycol = mydb[str(keyword)]
    x = mycol.insert_one(
        {"keyword_title": key1, "Query string": query, "Duplicates": duplicates, 'Words': words, 'retries': retries,
         'Request Time': elapsed})
    print(x.inserted_id)


def uploadunique(key, uniquewords):
    mydb = myclient[key]
    mycol = mydb["unique_words"]
    x = mycol.insert_one({"Unique_words": uniquewords})
    print(x.inserted_id)
