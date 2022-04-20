# Stock-Portfolio-Monitoring-Kafka-Spark-
This is a Kafka Ecosystem
This is a Kafka Ecosystem. 2 Servers imitate the stock trades and publish stock prices to a Kafka topic. 
3 investors monitor the Kafka topic "Stock_Exachange" and update their respective portfolios every 20 seconds. 
The evaluation of each investor's portfolio is then published to a second Kafka topic "Portfolios". 
Another application "App1" monitors Kafka topic "Portfolios" and saves the data to separate csv files. 
"App2" then queries the csv fiels created locally and provides some metrics with regards to the portfolios
