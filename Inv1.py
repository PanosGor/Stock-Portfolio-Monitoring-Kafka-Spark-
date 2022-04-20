from json import loads,dumps
from kafka import KafkaConsumer,KafkaProducer
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from kafka import TopicPartition
import time

#Here the user can specify the Investor he wants to read for and the Kafkatopic
investor = 1
KAfkaTopic = 'Test1'
Producer_Kafka_Topic = 'portfolios2'


stocks_per_interval = {}
time_check = []
start = datetime.now()
eval_list_1 = []
eval_list_2 = []
eval_1_sum = 0
eval_2_sum = 0


#P1 and P2 holds the number of stocks for portfolios 1 and 2
#So that the evaluation of the portfolio could be calculated
#he investor variable the KafkaTopic and the P1 and P2 could be changed for different topics
#or investors or portfolios
p1 = {'IBM':1000,'AAPL':1200,'FB':900,'AMZN':2300,'GOOG':1400,'TWTR':400}

p2 = {'LNKD':900,'INTC':600,'AMD':1100,'MSFT':1200,'DELL':700,'ORKL':1200}

#We instantiate the producer and the consumer
#For the consumer  group_id changes with regards to the investor
#KAfKAtopic can also be changed to read from another topic
dezer = lambda x: loads(x.decode('utf-8'))
serzer = lambda x: dumps(x).encode('utf-8')

consumer = KafkaConsumer(KAfkaTopic,
                         bootstrap_servers=['localhost:9092'],
                         auto_offset_reset='earliest',
                         enable_auto_commit=True,
                         group_id=f'my-group{investor}',
                         value_deserializer=dezer, )

producer = KafkaProducer(bootstrap_servers=['localhost:9092'], value_serializer=serzer)

#poll_var is used to specify the number of miliseconds for the consumer.poll() function
#We 20000 miliseconds equal to 20 seconds
poll_var = 20000

while True:
    
    
    records = consumer.poll(poll_var)
    print()
    x=records.values()
    for i in x:
        for j in i:
            nuke=j.value
            print(nuke)
            stock_info = loads(nuke)
            
            #stocks per intervcal starts as an empty dictionary at the beginning of this file
            #every time a new stock appears it creates a key with the stocks TICK
            #And stores as a value the Stock's PRICE
            #Every time a stock appears again its price is being overwritten by the new price
            #So that at every time we have the most up to date price for each stock
            stocks_per_interval[stock_info["TICK"]]=float(stock_info["PRICE"])
            
    print("20 seconds interval end")
    
    print(stocks_per_interval)
    for i in p1.keys():
        #the eval_1_sum in the beggining is equal to 0
        #for every stock in the P1 portfolio we mutliply the price of the stock with the number of stocks
        #eval_1_sum keeps the sum of all stock_price * stock_number
        eval_1_sum += p1[i]*stocks_per_interval[i]
    for i in p2.keys():
        #SAme as above for eval_2_sum
        eval_2_sum += p2[i]*stocks_per_interval[i]
    ntime = datetime.now()
    #timestamp used datetime to calculate the timestamp and then stores everything up to a minute 
    #within a string
    timestamp = f"{ntime.year}-{ntime.month}-{ntime.day} {ntime.hour}:{ntime.minute}"
    print(timestamp)   
    print(f"EValuation of Portfolio {investor}.1 {eval_1_sum} $")
    print(f"EValuation of Portfolio {investor}.2 {eval_2_sum} $")
    #eval_list_1 is a list where we save the current evaluation of portfolio 1
    #in order to calculate the evaluation difference from the previous portfolio
    #we use the current evaluation eval_1_sum - eval_list_1[-1] where eval_list_1[-1]
    #is the last element in the list eval_list_1 that indicates the previous evaluation
    #similarly we do the calculation for the percentage change
    #len(eval_list_1)==0 that means that this is the first time that we evaluate the portfolio
    if len(eval_list_1)==0:
        eval_diff_1 = 0
        perc_eval_diff_1 = 0
        print("Difference from previous evaluation for Portfolio {investor}.1: 0 $")
        print("Percentage Difference from previous evaluation for portfolio {investor}.1 0 %")
        eval_list_1.append(eval_1_sum)
    else:
        eval_diff_1 = eval_1_sum - eval_list_1[-1]
        perc_eval_diff_1 = (eval_diff_1/eval_list_1[-1])*100
        print(f"Difference from previous evaluation for Portfolio {investor}.1: {eval_diff_1} $")
        print(f"Percentage Difference from previous evaluation for portfolio {investor}.1: {round(perc_eval_diff_1,2)} %")
        eval_list_1.append(eval_1_sum)
    #similarly as above for portfolio 2
    if len(eval_list_2)==0:
        eval_diff_2 = 0
        perc_eval_diff_2 = 0
        print("Difference from previous evaluation for Portfolio {investor}.2: 0 $")
        print("Percentage Difference from previous evaluation for portfolio {investor}.2: 0%")
        eval_list_2.append(eval_2_sum)
    else:
        eval_diff_2 = eval_2_sum - eval_list_2[-1]
        perc_eval_diff_2 = (eval_diff_2/eval_list_2[-1])*100
        print(f"Difference from previous evaluation for Portfolio {investor}.2 :{eval_diff_2} $")
        print(f"Percentage Difference from previous evaluation for portfolio {investor}.2: {round(perc_eval_diff_2,2)} %")
        eval_list_2.append(eval_2_sum)
        
    #we create 2 dictionaries were we save our results for each portfolio
    portfolio_eval_1 = {'PORTFOLIO':f'{investor}.1','TIMESTAMP':timestamp,'NAV':eval_1_sum,'NAV_Change':eval_diff_1,'NAV_Change_%':round(perc_eval_diff_1,2)}   
    portfolio_eval_2 = {'PORTFOLIO':f'{investor}.2','TIMESTAMP':timestamp,'NAV':eval_2_sum,'NAV_Change':eval_diff_2,'NAV_Change_%':round(perc_eval_diff_2,2)}

    print(portfolio_eval_1)
    print(portfolio_eval_2)
    
    #we seend the results to the Producer_Kafka_Topic (Producer_Kafka_Topic is a variable that can be changed at the beggining of the top this script)
    producer.send(Producer_Kafka_Topic, value=portfolio_eval_1)
    producer.send(Producer_Kafka_Topic, value=portfolio_eval_2)
    
    #we set the evaluations for both portfolios to zero at the end of the 20 sec interval
    eval_1_sum = 0 
    eval_2_sum = 0
    time.sleep(20)