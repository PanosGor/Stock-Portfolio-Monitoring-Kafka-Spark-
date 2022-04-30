# Stock Portfolio Monitoring Kafka Spark 
This is a Kafka Ecosystem This is a Kafka Ecosystem. 2 Servers imitate the stock trades and publish stock prices to a Kafka topic. 
3 investors monitor the Kafka topic "Stock_Exachange" and update their respective portfolios every 20 seconds. 
The evaluation of each investor's portfolio is then published to a second Kafka topic "Portfolios". Another application "App1" monitors Kafka topic "Portfolios" and saves the data to separate csv files. 
"App2" then queries the csv fiels created locally and provides some metrics with regards to the portfolios.


## Process Flow

![image](https://user-images.githubusercontent.com/82097084/166108976-85d16c0c-4189-4440-93d8-4879e06400c9.png)

As can be seen from the above flowchart we have a Kafka Cluster which consists of 2 Kafka topics. 
The first topic named StockExchange consists of a single partition, the second Kafka topic named Portfolios consists of a single partition as well. 
Starting with the kafka topic StockExchange, there are two different producers that send data to the StockExchange kafka topic. 
The first producer se_1_server sends data that simulate the financial stock exchange trades. 
These hypothetical trades are affecting only 12 stocks and take place every 2-5 seconds the seconds producer named se_2_server sends data to the same kafka topic and again simulates stock trades for 12 different stocks from se_1_server. 
In total, StockExchange receives data from two different producers with regards to 24 stocks in total.
There are 3 different applications that monitor the kafka topic StockExchange Investor 1, Investor 2, Investor 3. 
Each application has a single consumer that reads the data from the StockExchange each consumer belongs to a different consumer group so that no consumer will remain idle as all consumers read from the same topic.


Each application evaluates two separate portfolios, also it calculates the difference between the current and the previous evaluations. 
Additionally, it calculates the percentage difference between the current and the previous evaluations.
Each Investor application also has a producer that sends the data to the kafka topic named Portfolios. 
A fourth application named App1 monitors the kafka topic Portfolios. 
This application has a single consumer that belongs to a different consumer group than the other three consumers mentioned above. 
The consumer reads the data from the topic and then the application saves the data in csv files. 
App1 creates a separate csv file for each unique combination of Investor and portfolio (as each Investor manages more than one portfolios).

A fifth application named App2 queries all the csv files created by App1 and provides information with regards to:
-	The values of a given portfolio in a given time interval
-	The average evaluation of each portfolio along with the name of its investor within a given time interval
-	The standard deviation of each portfolio along with the name of its investor within a given time interval
-	The highest spread ((max_eval – min_eval) / avg_eval) of each portfolio along with the name of its investor within a given time interval

## Part 1: servers 

The first steps towards setting up the network of financial and investment services of stock exchanges and investors is to create a Kafka Topic named “StockExchange”. This topic is created through an Ubuntu bash. 
The specifications of the topic are the following: the bootstrap-server is set to 9092, the replication-factor is set to 1 as well as the partitions.
After creating the topic, some changes will take place in the initial given server, in order to fit the problem and serve its role as a Producer in the network. 
The goal of the server is to simulate an environment of stocks and the continuous changes in their price. 
A brief summary of what the server do is the following: The server in its given form, contains a list of TICK – STOCK PRICE pairs named stock. 
This list contains the tickers and stock prices of 24 companies. Then the stock list is iterated and a JSON type message that contains the ticker, the stock price and the timestamp is produced. 
The messages are produced and then encoded before being send. 
Next, there is a never ending while loop in which the server sleeps for a random amount of time between 2 and 5 seconds. 
Then it “chooses” a random number between 1 and the length of the list named stock. 
Then, the tick-stock price pair that corresponds to the list position dictated by the number “chosen” in the previous step is picked. 
As a next step, a random number between 0 and 1 is created then divided by 10 and reduced by 0.5. 
The result of this arithmetic operations produces a number between -0.4 and -0.5. Now, the new price of the stock is produced. 
This happens in the following way: the initial stock value is multiplied with a value between 0.6 and 0.5 and the new stock price in calculated. 
Then, again, a message in JSON format which contains the ticker, the produced stock price and the timestamp is formed and encoded() before being sent. 
This server is waiting an “application” to connect in the port 9999 in order to emit messages through this gate. 

In this project, based on the initial server, two other servers are created. 
Each of them, in the list named stock, contains 12 unique ticker - stock values pairs. 
Those servers should “connect” to the Kafka topic created, named “StockExchange”, and emit their messages to this topic. 
To achieve this, the servers will be modified to become Producers. 
The modification goes as following: a new Kafka producer is initialized with following arguments: bootstrap_servers = [‘localhost: 9092’] and value_serializer = lambda x: dumps(x). encode(‘utf-8’). 
The first argument sets the host and port the producer should contact to bootstrap initial cluster metadata. 
The second argument dictates how the data should be serialized before being sent to the broker. 
In this case the data are converted to a JSON file and encode  to utf-8. 
The Producer is emitting its messages to the Kafka topic “StockExchange”. 
Also, within the for loop and the while loop the messages are sent to a broker with the usage of the send method in which the topic ( “StockExchange”) and the data sent (messages) are  specified (replacing the c.send(sg + ‘\n’).encode() used in the initial server.  
The basic functionality of the server, which is to produce new stock prices for the different tickers assigned to it, remains the same. 
To consolidate, a Kafka topic named “StockExchange” was created and two Producers were initialized who emit messages to the topic. 
Each server prints the data sent to the kafka topic on screen for the user to see.

*Figure 1 – Server 1 output*

![image](https://user-images.githubusercontent.com/82097084/166109168-528458b0-8bb6-4c16-932a-0565ce9b682b.png)

*Figure 2 – Server 2 output*

![image](https://user-images.githubusercontent.com/82097084/166109179-529956bf-9d4b-4a2d-a41c-f8d293d4fda1.png)