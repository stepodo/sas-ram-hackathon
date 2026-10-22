# The CineAgent

## Building an AI Agent to Analyze Movies and Craft Stories Across Every Genre



Welcome to the **SAS RAM Hackathon**!

In this challenge, you will build an AI agent with one mission: **understand movies and use that knowledge to help create new ones**.



Your CineAgent will work with different kinds of movie knowledge. It will explore movie plots and stories, learn the principles behind successful films, and work with structured movie data covering attributes such as titles, genres, directors, and financial performance.



Throughout this guide, you will build CineAgent **step by step**. You will start by creating and evaluating its knowledge base using **Retrieval-Augmented Generation (RAG)**. Then, you will extend the agent with **MCP tools**, giving it access to structured movie data and allowing you to explore a richer set of questions and tasks.



Along the way, you will **experiment, evaluate, and improve** different versions of the agent until you are ready to deploy your champion.



By the end of the challenge, CineAgent won't just know about movies. **It will be ready to help you imagine the next one**.



Are you ready? Let's start!

##### 

### SAS Retrieval Agent Manager



In this challenge, you will build **CineAgent using** **SAS Retrieval Agent Manager**.



#### Software Overview

SAS Retrieval Agent Manager provides the environment you will use throughout the challenge to turn movie knowledge into an AI-powered agent. You will progressively build CineAgent, starting with document-based knowledge and then extending the agent with tools that can access structured movie data.



For more information about SAS Retrieval Agent Manager and training courses on this solution, please visit out official web pages:

* [Official Webpage](https://www.sas.com/en_us/software/retrieval-agent-manager.html)
* [SAS Help Center for SAS RAM](https://go.documentation.sas.com/doc/en/ragntmgrcdc/v_013/ragntmgrug/titlepage.htm?fromDefault=)
* [SAS Learning Portal](https://learn.sas.com/) 



#### How to access

\[...]





### The Sources



The first step is to make our movie knowledge available in **SAS Retrieval Agent Manager (RAM)**.



In the **documents** folder of this repository, you will find two files:

* movies\_success\_guidelines.txt: contains guidelines and key principles for developing and evaluating a successful movie, covering areas such as story, audience, production, economics, marketing, and distribution.
* movies\_summary.pdf: contains movie titles and their corresponding plot summaries.



Download both files. We will use them to create **two separate Sources** in SAS Retrieval Agent Manager.



#### Create your first Source

In SAS Retrieval Agent Manager, click **Sources**, then select **Local Files**.



A Source is where we will store the documents that provide knowledge to CineAgent. For this challenge, we will keep the two types of knowledge separate by creating **two Sources**:

* One for movies\_summary
* One for movies\_success\_guidelines



For each Source, provide a **Name** and a **Description**. Feel free to choose your own, or use the following examples:

* **Movie Summaries:** This Source contains movie summaries.
* **Movie Success Guidelines:** This Source contains guidelines for developing and evaluating a successful movie.



Upload the corresponding file to each Source.



**Why two Sources?** Keeping the documents separate will allow us to build and experiment with two distinct knowledge bases in the next steps.





### The Collections



Once the two sources were created, we need to create the vectorized tables that will be used by the RAG system.



In the left panel, click **Collections** and then click **Create a Collection**. You are going to create two collections, one per each Sources we created before.

* **Movie Summaries Knowledge**: This collection contains a document that has one paragraph per each movie. The paragraph as a three level structure: MOVIE\_ID, TITLE, SUMMARY.
* **Movie Success Guidelines Knowledge**: This collection contains a document that has suggestions and guidelines to follow to write a successful movie.



Once the two collections are ready, click the **Movie Summaries Knowledge**; the collection is empty, you are going to deploy your first RAG configuration.



#### Setup a Collection Configuration

Click **Create a new configuration**.



In the Basics tab:

* Specify a Name and a Description (for instance: test 1.0, RAG benchmark) for your configuration.
* Specify the **Embedding model** (please, specify a multilingual model if you are planning to ask the agent questions in multiple languages).
* Select **PostgreSQL** as the **Destination**.
* In **Configuration update strategy** select **Append and sync**



In the Settings tab:

* Specify a **Chunk size** \[xxx]
* Specify the **Chunk overlap** \[xxx]



Click **Save**.



Click the **Play button** a the right of the screen to initialize the execution of the RAG process.



Feel free to prepare multiple configurations for your collection by changing the Chunk size and the Chunk overlap. You can setup a new configuration during the initialization process of another one.



Repeat the process, following the same logics, for the **Movie Success Guidelines Knowledge** collection.

Create at least two or three configurations per each collection.



#### Retrieval Settings

Once all configurations have completed the Vectorization Status, you need to evaluate the RAG performance of each of them in order to select the champion model.

To do this we need to:

1. Provide the RAG system a description of the future purpose of our use case
2. Sample questions with a known answer we can use to evaluate model performance



In the left panel, click **Retrieval Settings**.

SAS provides six standard retrieval settings: **Concise**, **Context**, **Default**, **Detailed** and **Summary**. However, you are going to build dedicated ones.

* Click the **New** button a the top right of the window
* Provide a N**ame** to your custom retrieval setting: write **Movie Guidelines Prompt**
* In the GitHub repository, navigate the content of the *retrieval\_settings* folder and copy the content of **movie\_guideline\_collection.txt**
* Paste the content in the **System prompt template** replacing the default prompt
* Leave all other settings as default
* Click **Save**



Repeat the same process for the Movie Summary Knowledge collection by coping and pasting the content of the **movie\_summary\_collection.txt** file. Name the custom retrieval setting as **Movie Summary Prompt**.



#### Evaluation Tests (collections)

In the left panel, click **Evaluation Tests**. Now you are going to implement a series of questions with known answers to evaluate the RAG system

* Click **Create an evaluation test**
* Provide a **Name** (for instance Movie Guideline Test) and a Description.
* Leave Passing threshold to 100%
* In the GitHub repository navigate the content of the *evaluation\_tests* folder and download the **movie\_guidelines\_evaluation.xlsx** file. Use the columns Question, Metric and Condition to build the question inside the SAS RAM
* Click **Create test case**
* Paste the content of the column Question in the **Prompt**, check **Metric** match and paste the corresponding **Value**.
* When multiple assertions are required, click the **New Assertion button** and follow the order in the Metric and Condition "n" columns in the Excel file.



Repeat the process with the content of the **movie\_summary\_evaluation.xlsx** file.



Go back to the Collections window:

* Click one of the two collection you built
* Click the **LLMs** tab
* Move the LLM model you prefer on the right panel (click the **arrow button**).
* Once the model is listed on the right, please remember to specify in Retrieval Settings the right custom retrieval setting you created.
* Specify the model as the Eval LLM model (menu at the bottom of the right panel).
* Remember to click the **Save button** a the top right of the window.



Now you are ready to run the evaluation tests:

* Click the **User Eval** tab
* Select all configurations you built in this collection
* Select the right test in the **Test** tab.
* Click **Ok**



Once the execution is completed, you can display the results in the **Summary** tab. Select the best model as the champion model of your collection using the **Configuration Status** menu.



Repeat this process for the other collection you built.





### Chat



The RAG implementation is completed! 

In the left panel, click **Chat**, then keep the selection to the **Collection** tab.

Select the champion configuration in the Movie Success Guidelines Knowledge collection and query the RAG system (for instance: C*iao, quali sono i segreti per un film di successo?*)

You can repeat the same test with the champion configuration from the Movie Summaries Knowledge (for instance: *Ciao, cosa sai del film di Eminem 8 Mile?*)



Technically speaking, this is not an agent, but just the RAG at works!



Now is time to build your CineAgent!





### The Agent (Experiment 1)



To deploy the first experiment of the CineAgent, you need:

1. An appropriate System Prompt
2. Give the agent the possibility to explore the content of the two RAG systems you built



In the left panel, click **Agents**

* Click Create an Agent
* Specify CineAgent as the agent Name, write a description. Leave System Prompt and Chat initializer command empty (the default)
* Click Add Agent Experiment



In Details tab:

* As experiment Name write Experiment 1
* In System Prompt paste the content of the file cineagent\_experiment\_1.txt file stored in the GitHub repository under the folder retrieval\_settings



In LLMs tab:

* Specify the model you prefer



In Collections tab:

* Move the two collections you built on the right panel
* Click **Save**



You can start the Development Server to test your Experiment 1 (please note you need to click on **Open Chat**). For instance, try ask something like *Ciao, vorrei sviluppare un nuovo film western. Suggeriscimi una trama e analizza quali tematiche e quale periodo di uscita potrebbero contribuire a massimizzarne il ROI.* 



Once you have obtained the answer, click on the **Detail view** button to access the behind the scenes operations. You can see the original position of the chunks the agent retrieved from the RAG systems.



#### Evaluation Tests (agent)

Now it is time to evaluate the performance of the agent.

Following the same strategy adopted for the collections, you are going to create a test in the **Evaluation Tests** window. 

Test questions are listed in the Excel file named **cineagent\_evaluation.xlsx** available in the *evaluation\_tests* folder inside the GitHub repository.



### The Model Context Protocol (MCP) Server



The Experiment 1 works, but you are not leveraging all the information you have access to. Indeed, you have access to structured cinematic data (a table in a database) that contains useful information. 

The table (available as CSV file in the GitHub repository) has:

* Number of columns:
* Number of rows:



To provide access to this structure source of information, you are going to build a custom MCP Server inside SAS RAM.



In the GitHub Repository:

* Download the **run.py**, the **README.md** file and the **requirements.txt** file inside code\_templates/code\_mcp\_server folder.



In SAS RAM:

* In the left panel, click on **Code Templates**
* Click on **Code MCP Server**
* As **Name**, write cineagent\_mcp\_tools. **Description**: List of custom MCP tools for the CineAgent project.
* In the code tab, click Browse, than load the three files you downloaded from GitHub. The file run.py contains the Python code behind the custom MCP server. Multiple MCP servers are also available out-of-the-box and they do not require such a complicated development.
* Click **Ok**
* Click the Publish button at the top right corner of the screen. Click Ok. Your code is now ready to be embedded in a MCP server!
* In the left panel, click on **MCP Tools**
* Click the New button
* As Name specify CineAgent MCP Server, description: MCP server for the CineAgent Project
* Select Custom as Tool server type
* Select cineagent\_mcp\_tools, then select the version (blue button) in the right panel. You should have just one version published.
* Click Finish
* By default the MCP server is stopped, click the MCP server then click the play button to execute it
* Check if Server Status is Running and Ping Status is Connected. If so, the MCP server deployment is completed.



Now you are ready to build a more complicated agent that has also access to the data via the MCP tools you just deployed!



### The Agent (Experiment 2)



Follow the same process reported in the section The Agent (Experiment 1). However:

* The Name of the Agent Experiment this time is Experiment 2
* This agent has its dedicated System Prompt, paste it from the file **cineagent\_experiment\_2.txt** stored in the folder *retrieval\_settings* in the GitHub repository.
* In the tool tab, move all the MCP tools you just built on the right panel, so the agent can access them.



You can test the Experiment 2 performance using the same set of questions implemented before.



Post the same question you tried for the Experiment 1, now you should see the agent answering some of your requests using the MCP tools you built.



Once you are confident with agent performance, you can select the champion agent experiment by selection Champion in the Status column and start the Agent Server. Now the agent can be used in the Chat window (left panel) or deployed in a custom infrastructure using the SAS RAM API.



**Congratulation! You have completed the SAS RAM Hackathon Challenge!**

**Please, if you want, feel free to continue to test different Collections, Agents and MCP tools configuration!**





&#x20;

