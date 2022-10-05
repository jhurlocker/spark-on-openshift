import sys, string
import os
import socket
from pyspark.sql import SparkSession
from datetime import datetime

if __name__ == "__main__":

    spark = SparkSession\
        .builder\
        .appName("PythonWordCount")\
        .getOrCreate()

    s3_endpoint_url = 'minio-ml-workshop-opendatahub.apps-crc.testing'
    s3_access_key_id = 'minio'
    s3_secret_access_key = 'minio123'
    s3_bucket = 'spark-demo'

    hadoopConf = spark.sparkContext._jsc.hadoopConfiguration()
    hadoopConf.set("fs.s3a.endpoint", s3_endpoint_url)
    hadoopConf.set("fs.s3a.access.key", s3_access_key_id)
    hadoopConf.set("fs.s3a.secret.key", s3_secret_access_key)
    hadoopConf.set("fs.s3a.path.style.access", "true")
    hadoopConf.set("fs.s3a.connection.ssl.enabled", "false")

    text_file = spark.sparkContext.textFile("s3a://" + s3_bucket + "/shakespeare.txt") \
                .flatMap(lambda line: line.split(" ")) \
                .map( lambda x: x.replace(',',' ').replace('.',' ').replace('-',' ').lower())

    sorted_counts = text_file.flatMap(lambda line: line.split(" ")) \
            .map(lambda word: (word, 1)) \
            .reduceByKey(lambda a, b: a + b) \
            .sortBy(lambda wordCounts: wordCounts[1], ascending=False)
            
    i = 0
    for word, count in sorted_counts.collect()[0:500]:
        print("{} : {} : {} ".format(i, word, count))
        i += 1
    
    now = datetime.now() # current date and time
    date_time = now.strftime("%d-%m-%Y_%H:%M:%S")

    sorted_counts.saveAsTextFile("s3a://" + s3_bucket + "/sorted_counts_" + date_time)

    spark.stop()
