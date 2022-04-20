from pyspark.sql import SparkSession

start_date=str("2022-3-20 15:38")
end_date=str("2022-3-20 15:43")
investor=1
portfolio=1

spark=SparkSession.builder.master('local[1]').appName('6107app').getOrCreate()

def main1(investor,portfolio,start_date,end_date):
    

    df1 = spark.read.option("delimiter", ",").option("header", True)\
                   .csv('INVESTOR_{}_PORTFOLIO_{}.csv'.format(investor,portfolio))\
                   .toDF('portfolio','timestamp','nav',"nav_change",'nav_change_percent')
    
    df1.registerTempTable('table1')

    print("\n",f"Info about\n\n investor: {investor}\n portfolio: {portfolio}\n between {start_date} and {end_date}","\n")

    spark.sql('select *\
                from table1\
                where timestamp between "{}" AND "{}"'.format(start_date,end_date)).show()


def main2(start_date,end_date):

    df = spark.read.option("delimiter", ",").option("header", True)\
                    .csv('*.csv')\
                    .toDF('portfolio','timestamp','nav',"nav_change",'nav_change_percent')

    df.registerTempTable('All_Files')

    #spark.sql('select * from All_Files').show(200)

    spark.sql('select portfolio, round(avg(nav),2) as Average_Valuation\
                        from All_Files\
                        where timestamp between "{}" AND "{}"\
                        group by portfolio\
                        order by portfolio ASC'.format(start_date,end_date)).show()

    spark.sql('select portfolio, round(stddev(nav),2) as Std_Dev\
                        from All_Files where \
                        timestamp between "{}" AND "{}" \
                        group by portfolio\
                        order by portfolio ASC'.format(start_date,end_date)).show()

    spark.sql('select portfolio, round((max(nav)-min(nav))/avg(nav),2) as Biggest_Spread\
                        from All_Files \
                        where timestamp between "{}" AND "{}" \
                        group by portfolio\
                        order by portfolio ASC'.format(start_date,end_date)).show()

main1(investor,portfolio,start_date,end_date)

main2(start_date,end_date)