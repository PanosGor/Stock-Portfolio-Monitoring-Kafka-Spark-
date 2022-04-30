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


## Part 2: Evaluation of portfolios

Consumers read from the Kafka topic continuously, but the goal was to make the consumer read from the Stock Exchange topic in 20 second intervals and do an evaluation of all portfolios of all investors.
In order to make the consumer behave this way.poll() command was used which fetches data from the assigned topics/partitions in batches. 
When poll() is called the consumer will use the last value’s timestamp that it consumed as a starting offset and will fetch information from that point on.  
Next time.sleep() is used so that poll is called every 20 seconds.
In the consumer configuration was set auto_offset_reset equal to earliest. 
The way it works is that the first time each consumer runs it reads every message from the beginning of the topic firstly so that it will not lose the first message of the server that gives all the stocks.

*Figure 4 – The way the consumer read the Kafka Topic*

![image](https://user-images.githubusercontent.com/82097084/166109370-55c1a665-8b07-4919-9494-975ee7d09090.png)

For every interval the consumer needs to evaluate his portfolios using only the most up to date price of the stock. 
Since the poll() command brings all the values from the last time it got invoked a dictionary called Stock_per_interval was used. 
The dictionary saves the latest price for each stock, as every new price for the same stock will overwrite the last price in the dictionary.
If a new stock appears then automatically is being saved in the dictionary. 
This is a very simple way to keep track of all the changes with regards to the stock prices.

*Figure 5 – The last updated values*

![image](https://user-images.githubusercontent.com/82097084/166109426-3b0972f4-1cc0-4e03-89e8-aaf0ada0cdd2.png)

The Investor’s portfolios are saved in 2 separate dictionaries called P1 and P2. 
These 2 portfolios have the number of stocks for each stock in the portfolio for example ‘FB’: 1000 indicates 1000 stocks for Facebook. 
To evaluate the whole portfolio, the total sum of all the combinations of prices multiplied by the number of stocks in the portfolio needed to be calculated. 
For example, if portfolio P has only 500 stocks for AAPL and 500 stocks for AMZN then the evaluation of the portfolio P will be 500 * FP_Price + 500 * AMZN_Price.
To achieve this the application iterates through the keys of each portfolio and by using dictionary Stock_per_interval it looks for the same key (The keys of each portfolio are subsets of the keys for dictionary Stock_per_interval). 
For each stock it calculates the NAV = Stock Price * Number of Stocks. 
It adds this calculation to variable eval_n_sum (which is created at the top of the script and is equal to 0). 
This eval_n_sum holds the current evaluation for the whole portfolio for each portfolio. 
At the end of all calculations the eval_n_sum is set to 0 so that it will be 0 for the calculations of the next 20 seconds interval.
In order to calculate the difference from the previous evaluation every time the application calculates the current portfolio evaluation it stores it to the list eval_list_n. 
If the list is empty, it means that this is the first time that the application evaluates this portfolio. 
Which means that the there is no previous value for the portfolio evaluation and the difference as well as the percentage change of the evaluation from the previous evaluation is 0. 
If the list is not empty the in order to calculate the NAV_Difference it uses the last element of the list  eval_list_n which is basically the NAV value from the previous portfolio evaluation and stores to variable eval_diff_n. 
The NAV change is given by the following formula

**NAV_Change= CurrentEvaluation- PreviousEvaluation**

Similarly, to calculate the percentage change the application uses the last value of the list eval_list_n the calculation is based on the formula:

**NAV_Change_%=((CurrentEvaluation- PreviousEvaluation))/( PreviousEvaluation)x100**

The timestamp is also being calculated by using the datetime module in Python. 
Ntime stores current timestamp by using datetime.now() . 
The results are being stored as a string following the following format “YY-MM-DD HH:MM”.
All the above calculations are being made for all the stocks that the consumer has seen in the 20 seconds interval. 
After finishing all the calculations, it stores the results in 2 separate dictionaries called portfolio_eval_n one dictionary for each portfolio. 
Each dictionary has the following format:

-	‘PORTFOLIO’: Is a string with 2 numbers separated by a (.) the first number indicates the investor and the second one indicates he portfolio for example Investor 3 portfolio 2 = 3.2
-	‘TIMESTAMP’: the calculated timestamp that was explained above
-	‘NAV’: Current evaluation of the portfolio
-	‘NAV_Change’: Difference for the previous evaluation
-	‘NAV_Change_%’: Percentage difference from previous evaluation

After that the application prints the results for the user to see and uses the results are shown in the screenshot below.

*Figure 6 – Metrics of every Investor consumer*

![image](https://user-images.githubusercontent.com/82097084/166109547-ef7bf7ed-b68b-42f0-81b5-f08f5762f4ea.png)

The Kafka Producer sends the results to a specified Kafka topic in this case Kafka topic is ‘portfolios’. 
The producer uses value serializer in order to dump the string to the topic in a json format.
At the end the evaluation for each portfolio is set to 0 and the application sleeps for 20 seconds. 
After that it will read the next 20 seconds interval from the consumer, and it will perform the same calculations again. 
The same application can work for every investor by changing the investor variable at the beginning and the portfolios.

## Part 3: An application that monitors the topic ‘portfolios’

For the creation of the csv files app1 monitors Kafka topic Portfolios. 
More specifically a kafka consumer was created. auto_offset_reset was set to ‘earliest’ for the consumer to read the data starting from the oldest available message, group_id = “my-group”. 
A group_id name that hadn’t been used was chosen for the consumer even though it wouldn’t make any difference as there are no other consumers reading data from this Kafka topic. 
After that the application prints the results for the user to see and uses the results are shown in the screenshot below.

*Figure 7 -  Consumer of Portfolios*

![image](https://user-images.githubusercontent.com/82097084/166109589-4eb94eb3-e3d0-4849-a13d-c89041e64ba1.png)

The value deserializer uses a lambda function in order to load the strings received from the topic in a json format. 
In order for that to be achieved loads function from json module is being used.

The data received from the topic have the following format:
-	‘PORTFOLIO’: Is a string with 2 numbers separated by a (.) the first number indicates the investor and the second one indicates he portfolio for example Investor 3 portfolio 2 = 3.2
-	‘TIMESTAMP’: the calculated timestamp that was explained above
-	‘NAV’: Current evaluation of the portfolio
-	‘NAV_Change’: Difference for the previous evaluation
-	‘NAV_Change_%’: Percentage difference from previous evaluation

The value of the key PORTFOLIO is split to the (.) to separate the investor and the portfolio into two different variables named investor and portfolio. 
By using os.path.isfile() function from the module os the application checks if the a file named after the given investor and portfolio exists in the local directory.
If a file does not exist, then it creates a csv file named after the given investor and the given portfolio. 
A csv writer() object will be created for the new csv file created (note that a new csv writer() will be created every time the consumer reads new data) the writer()
append at the end of the file (In this case because the file is completely empty the end is the beginning) the header from column cols the header will have the same
format as the json object meaning:

-	‘PORTFOLIO’
-	‘TIMESTAMP’
-	‘NAV’
-	‘NAV_Change’
-	‘NAV_Change_%’

After that the new data that the consumer read will be appended at the end of the csv file this process will be done every time for every unique combination of 
Investors and portfolios meaning that there is no limit to how many combinations of Investors and portfolios we can have.
If the file already exists in the directory the file will be opened without being replaced. Again a new writer() object will be created for the given csv file and the
data will be appended at the end of the file. By doing this the application makes sure not to lose any information received from the consumer. 
This is a dynamic way to create csv files for a non-specified number of Investors and Portfolios. Meaning that if there were 1000 Investor and each investor has 1000
portfolios to evaluate 1 million csv files will be created for all possible combinations between Investors and portfolios with each csv file containing only information for its equivalent Investor_n_Portfolio_n. 
The application will keep updating the csv files as long as it reads data from the Kafka topic

Example screenshot of the produced csv file for Investor 1 Portfolio 2:

*Figure 8 – csv layout*

![image](https://user-images.githubusercontent.com/82097084/166109690-695a25a2-c929-447b-8fc3-2e2d5a78357a.png)

## Part 4 – Spark Application

A spark application was made that it reads all csv files in the directory that the above application creates and when it is run it asks for which investor and 
portfolio we want information about and in what timeframe. 
It uses spark SQL to query the csv files and fetch all the information about the specific portfolio we have and also gives us information about the average evaluation,
standard deviation and highest spread of each portfolio in the same time frame.

*Figure 9 – Metrics that the Spark app2 gives us*

![image](https://user-images.githubusercontent.com/82097084/166109709-4bd69e03-a3e0-4221-a888-0293d6eb0ee3.png)










