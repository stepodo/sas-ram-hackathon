# CineAgent

## Building an AI Agent to Analyze Movies and Create New Movie Stories





### Index

\[...]





Welcome to the **SAS Retrieval Agent Manager Hackathon**!

In this challenge, you will build an AI agent with one mission: **understand movies and use that knowledge to help create new ones**.



Your CineAgent will work with different kinds of movie knowledge. It will explore movie plots and stories, learn the principles behind successful films, and work with structured movie data covering attributes such as titles, genres, directors, and financial performance.



Throughout this guide, you will build CineAgent **step by step**. You will start by creating and evaluating its document-based knowledge base using **Retrieval-Augmented Generation (RAG)**. Then, you will extend the agent capabilities with **MCP tools**, giving it access to structured movie data and allowing you to explore a richer set of questions and tasks.



Along the way, you will **experiment, evaluate, and improve** different versions of the agent until you are ready to select your champion.



By the end of the challenge, CineAgent will not just know about movies. **It will be ready to help you imagine the next one**.



Are you ready? Let's start!





1. ### SAS Retrieval Agent Manager



In this challenge, you will build **CineAgent using** **SAS Retrieval Agent Manager**.



#### 1.1 Software overview



SAS Retrieval Agent Manager provides the environment used throughout this challenge to create Sources, configure RAG Collections, run user evaluations, build agent experiments, and integrate MCP tools.



You will start with document-based knowledge. You will then extend CineAgent with an MCP tool server that provides access to structured movie data.



For more information about SAS Retrieval Agent Manager and the available training resources, visit:

* [Official Webpage](https://www.sas.com/en_us/software/retrieval-agent-manager.html)
* [SAS Help Center for SAS RAM](https://go.documentation.sas.com/doc/en/ragntmgrcdc/v_013/ragntmgrug/titlepage.htm?fromDefault=)
* [SAS Learning Portal](https://learn.sas.com/)



#### 1.2 How to access

\[...]





### 2\. Sources



The first step is to add the movie documents to **SAS Retrieval Agent Manager**.

A Source contains the raw documents that will later be processed and indexed as part of the RAG pipeline.



In the **documents** folder of the GitHub repository, you will find two files:

* 'movies\_success\_guidelines.txt' contains guidelines for developing and evaluating a successful movie. It covers areas such as storytelling, audience, production, economics, marketing, and distribution.
* 'movies\_summary.pdf' contains movie titles and their corresponding plot summaries. Each movie entry includes a movie ID, title, and summary.



Download both files to your computer. You will use them to create **two separate Sources** in SAS Retrieval Agent Manager.



#### 2.1 Create the two Sources

A Source is where we will store the documents that provide knowledge to CineAgent.

For this challenge, we will keep the two types of knowledge separate by creating **two Sources**:

* One for movie summaries
* One for movies success guidelines



1. In the navigation pane, select **Sources**.
2. Select **Local Files**.
3. Enter the following name and description:

   1. **Name** 'Movie Summaries'
   2. **Description** 'Movie plot summaries used to answer questions about movie stories, characters, and themes.'
4. Select **Browse files** and load the 'movies\_summary.pdf' file
5. Select **Save**
6. Create another source by selecting **Local Files**
7. Enter the following name and description:

   1. **Name** 'Movie Success Guidelines'
   2. **Description** 'Guidelines for developing and evaluating a successful movie, including storytelling, audience, production, financial considerations, marketing, and distribution.'
8. Select **Browse files** and load the 'movies\_success\_guidelines.txt' file
9. Select **Save**



#### 2.2 Why two Sources?

Keeping the documents separate allows you to create, configure, and evaluate two independent RAG Collections: one for movie summaries and one for movie success guidelines.



This makes it easier to test different chunking and retrieval strategies for each type of content.



#### 2.3 Expected result

The **Sources** view should now contain:

* 'Movie Summaries', with 'movies\_summary.pdf'.
* 'Movie Success Guidelines', with 'movies\_success\_guidelines.txt'.



You are now ready to create a separate Collection for each Source.





### 3\. Collections



Now that the two Sources are available, you can create the Collections used by the RAG pipeline.



A Collection connects one or more Sources to a set of configurations. Each configuration defines how the source documents are divided into chunks, converted into vector embeddings, stored, and retrieved.



In this challenge, you will create two Collections:

* Movie Summaries Knowledge
* Movie Success Guidelines Knowledge



Each Collection will use one of the Sources created in the previous section.



#### 3.1 Create the Movie Summaries Knowledge Collection

1. In the navigation pane, select **Collections**.
2. Click **New Collection**.
3. Enter the following information:

   1. **Name**: 'Movie Summaries Knowledge'
   2. **Description**: 'A RAG Collection containing movie titles and plot summaries. Each movie entry includes a movie ID, title, and summary.'
4. Select the 'Movie Summaries' Source.
5. Click **Save**.



#### 3.2 Create the Movie Success Guidelines Knowledge Collection

1. Return to the Collections view.
2. Click **New Collection**.
3. Enter the following information:

   1. **Name**: 'Movie Success Guidelines Knowledge'
   2. **Description**: 'A RAG Collection containing guidelines for developing and evaluating a successful movie.'
4. Select the 'Movie Success Guidelines' Source.
5. Click **Save**.



#### 3.3 Expected result

The **Collections** view should now contain:

* 'Movie Summaries Knowledge', associated with the 'Movie Summaries' Source;
* 'Movie Success Guidelines Knowledge', associated with the 'Movie Success Guidelines' Source.



The Collections do not contain vector embeddings yet. In the next steps, you will create and run multiple configurations for each Collection.





### 4\. Collection configurations

A configuration defines how the documents in a Collection are processed and indexed.



You will create multiple configurations with different chunk size and chunk overlap values. You will then evaluate their retrieval performance and select the best configuration as the champion.



> \*\*Important\*\*: You cannot edit a configuration after saving it. To test different values, create a new configuration or copy an existing one.



#### 4.1 Create the first Movie Summaries configuration

1. Open the 'Movie Summaries Knowledge' Collection.
2. On the **Summary** tab, click **Create a new configuration**.



###### Basics

On the **Basics** tab, enter or select the following values:

* **Name**: Enter a descriptive and unique name, such as 'summaries-config-01'.
* **Description**: Describe the parameters or purpose of the configuration, such as 'Initial benchmark configuration for movie summaries'.
* **Embedding model**: Select an embedding model.
* **Destination**: Select the PostgreSQL vector database destination provided for the hackathon.
* **Configuration update strategy**: Select 'Append and sync'.



> If you plan to submit queries in multiple languages, select a multilingual embedding model.



###### Settings

On the **Settings** tab, configure the chunking parameters:

* **Chunk size**: 256
* **Chunk overlap**: 36



Leave the other settings at their default values unless instructed otherwise.



3\. Click **Save**.



##### 4.1.1 Run the vectorization job

After saving the configuration:

1. Select the configuration on the **Summary** tab.
2. Review the default execution settings.
3. Click **Submit**.
4. Monitor the job in the **Vectorization Status** column.



Wait until the status is 'Completed' before using or evaluating the configuration.

If the status is 'Error', open the job log, review the error details, and contact a hackathon organizer if you cannot resolve the issue.



##### 4.1.2 Create additional configurations

Create at least two configurations for the 'Movie Summaries Knowledge' Collection.

Use a different combination of **Chunk size** and **Chunk overlap** for each configuration. For example:

|Configuration|Chunk size|Chunk overlap|
|-|-|-|
|summaries-config-01|256|36|
|summaries-config-02|512|64|
|summaries-config-03|128|0|



You can create a new configuration while another vectorization job is running.

Run a vectorization job for every configuration and wait until each **Vectorization Status** is 'Completed'.



#### 4.2 Configure the Movie Success Guidelines Collection

Repeat the same process for the 'Movie Success Guidelines Knowledge' Collection.

1. Open the 'Movie Success Guidelines Knowledge' Collection.
2. Create at least three configurations.
3. Use different chunk size and chunk overlap values for each configuration.
4. Select the embedding model and PostgreSQL destination.
5. Select 'Append and sync' as the configuration update strategy.
6. Save each configuration.
7. Run a vectorization job for every configuration.
8. Wait until every **Vectorization Status** is 'Completed'.



Use descriptive configuration names, such as:

* 'guidelines-config-01'
* 'guidelines-config-02'
* 'guidelines-config-03'



#### 4.3 Expected result

You should now have:

* two Collections, each associated with the correct Source;
* At least two configurations in each Collection;
* Different chunking parameters across the configurations;
* A completed vectorization job for every configuration.



All configurations initially have the 'Under Evaluation' status. Later in the challenge, you will evaluate their retrieval performance and select the best configuration in each Collection as the 'Champion'.





### 5\. Retrieval Settings



Now that the documents have been vectorized, you need to define how the retrieved content will be provided to the large language model.



A retrieval setting controls how SAS Retrieval Agent Manager retrieves context from a Collection and how the LLM uses that context to answer a query.



SAS provides six standard retrieval settings: **Concise**, **Context**, **Default**, **Detailed** and **Summary**.



In this challenge, you will create two custom retrieval settings:

* 'Movie Guidelines Retrieval Setting'
* 'Movie Summaries Retrieval Setting'



Each custom retrieval setting uses a system prompt template designed for the corresponding type of movie knowledge.



> \*\*Important\*\*: The system prompt template must include the '{context}' variable. SAS Retrieval Agent Manager replaces this variable with the content retrieved from the Collection.



#### 5.1 Create the Movie Guidelines Retrieval Setting

1. In the navigation pane, select **Retrieval Settings**.
2. Click **New**.
3. In the **Name** field, enter: 'Movie Guidelines Retrieval Setting'
4. In the GitHub repository, open the 'retrieval\_settings' folder.
5. Open 'movie\_guideline\_collection.txt'.
6. Copy the complete content of the file.
7. Replace the default content in the **System prompt template** field with the copied text.
8. Verify that the template includes the '{context}' variable.
9. Leave the other retrieval parameters at their default values.
10. Click **OK** to save the retrieval setting.



#### 5.2 Create the Movie Summaries Retrieval Setting

1. In the **Retrieval Settings** view, click **New**.
2. In the **Name** field, enter: 'Movie Summaries Retrieval Setting'
3. In the GitHub repository, open the 'retrieval\_settings' folder.
4. Open 'movie\_summary\_collection.txt'.
5. Copy the complete content of the file.
6. Replace the default content in the **System prompt template** field with the copied text.
7. Verify that the template includes the '{context}' variable.
8. Leave the other retrieval parameters at their default values.
9. Click **OK** to save the retrieval setting.





### 6\. Assign the Retrieval Settings to the Collections



Creating a retrieval setting does not automatically associate it with a Collection. You must assign each retrieval setting to an LLM in the corresponding Collection.



#### 6.1 Configure the Movie Success Guidelines Knowledge Collection

1. In the navigation pane, select **Collections**.
2. Open the 'Movie Success Guidelines Knowledge' Collection.
3. Select the **LLMs** tab.
4. From the list of available LLMs, add the model that you want to use with the Collection.
5. For the configured LLM, select: 'Movie Guidelines Retrieval Setting'
6. In the **User Eval** section, select the LLM that will be used as the **Eval LLM**.
7. Click **Save**.



#### 6.2 Configure the Movie Summaries Knowledge Collection

1\. Return to the **Collections** view.

2\. Open the 'Movie Summaries Knowledge' Collection.

3\. Select the **LLMs** tab.

4\. From the list of available LLMs, add the model that you want to use with the Collection.

5\. For the configured LLM, select: 'Movie Summaries Retrieval Setting'

6\. In the **User Eval** section, select the LLM that will be used as the **Eval LLM**.

7\. Click **Save**.



> **Tip**: You can use the same LLM for both Collections. Using the same model makes it easier to compare the effect of different Collection configurations without introducing an additional model variable.



#### 6.3 Expected result

You should now have:

* A 'Movie Guidelines Retrieval Setting' containing the custom prompt for the movie success guidelines
* A 'Movie Summaries Retrieval Setting' containing the custom prompt for the movie summaries
* An LLM configured for each Collection
* The correct custom retrieval setting assigned to the LLM in each Collection
* An Eval LLM selected for user evaluations



You are now ready to create the user evaluation tests that will be used to compare the Collection configurations.





### 7\. Evaluate the Collection configurations



The next step is to evaluate the retrieval performance of the configurations created for each Collection.



You will use questions with known answers to determine which configuration produces the most accurate responses. The evaluation results will help you select a champion configuration for each Collection.



The GitHub repository contains two evaluation files:

* 'movie\_guidelines\_evaluation.xlsx'
* 'movie\_summary\_evaluation.xlsx'



Each row in these files contains:

* A question to submit to the RAG pipeline;
* One or more evaluation metrics;
* The expected values or conditions used to evaluate the response.



In SAS Retrieval Agent Manager, these questions and expected results are implemented as reusable **User Eval Tests**.



#### 7.1 Create the Movie Guidelines User Eval Test

1. In the navigation pane, select **User Eval Tests**.
2. Click **New**.
3. Enter the following information:

   1. **Name**: 'Movie Guidelines Evaluation'
   2. **Description**: 'Evaluates responses generated from the Movie Success Guidelines Knowledge Collection.'
   3. **Passing Threshold**: '100'
4. Click **OK** to create the test.



##### 7.1.1 Add the test prompts

1. In the GitHub repository, open the 'evaluation\_tests' folder.
2. Download and open 'movie\_guidelines\_evaluation.xlsx'.
3. In SAS Retrieval Agent Manager, open 'Movie Guidelines Evaluation'.
4. Click **Create one** to add the first test prompt.
5. Copy the value from the 'Question' column of the spreadsheet into the **Prompt** field.
6. Set the **Passing threshold (%)** to '100'.
7. Under **Assertions**:

   1. Select the metric specified in the 'Metric' column;
   2. Enter the corresponding expected value from the 'Condition' column in the **Value** field.
8. If the spreadsheet row contains additional 'Metric n' and 'Condition n' pairs:

   1. click **New assertion**;
   2. select the additional metric;
   3. enter the corresponding expected value;
   4. repeat this step for every additional assertion in the row.
9. Save the test prompt.
10. 10\. Repeat these steps for every row in 'movie\_guidelines\_evaluation.xlsx'.



> \*\*Important\*\*: Preserve the order and spelling of the expected values in the spreadsheet. Do not translate or rewrite them.



#### 7.2 Create the Movie Summaries User Eval Test

1. Return to the **User Eval Tests** view.
2. Click **New**.
3. Enter the following information:

   1. **Name**: 'Movie Summaries Evaluation'
   2. **Description**: 'Evaluates responses generated from the Movie Summaries Knowledge Collection.'
   3. **Passing Threshold**: '100'
4. Click **OK** to create the test.
5. In the GitHub repository, open the 'evaluation\_tests' folder.
6. Download and open 'movie\_summary\_evaluation.xlsx'.
7. Add one test prompt for each row in the spreadsheet:

   1. copy 'Question' into the **Prompt** field;
   2. set **Passing threshold (%)** to '100';
   3. select the metric specified in 'Metric';
   4. copy the corresponding 'Condition' into the **Value** field;
   5. use **New assertion** for every additional 'Metric n' and 'Condition n' pair.
8. 8\. Save every test prompt.



#### 7.3 Expected result

The **User Eval Tests** view should now contain: 'Movie Guidelines Evaluation' and 'Movie Summaries Evaluation'.

Each test should contain all the questions and assertions provided in the corresponding spreadsheet.



#### 7.4 Prepare the Collections for evaluation

Before running the evaluations, verify that each Collection has:

* At least two vectorized configurations
* A 'Completed' **Vectorization Status** for every configuration
* At least one configured LLM
* The correct custom retrieval setting assigned to that LLM
* An **Eval LLM** selected in the **User Eval** section



#### 7.5 Verify the Movie Success Guidelines Knowledge Collection

1. In the navigation pane, select **Collections**.
2. Open 'Movie Success Guidelines Knowledge'.
3. Select the **LLMs** tab.
4. Verify that the LLM you want to evaluate appears in the list of configured LLMs.
5. Verify that 'Movie Guidelines Retrieval Setting' is assigned to the configured LLM.
6. In the **User Eval** section, select an **Eval LLM**.
7. Click **Save**.



#### 7.6 Verify the Movie Summaries Knowledge Collection

1. Return to the **Collections** view.
2. Open 'Movie Summaries Knowledge'.
3. Select the **LLMs** tab.
4. Verify that the LLM you want to evaluate appears in the list of configured LLMs.
5. Verify that 'Movie Summaries Retrieval Setting' is assigned to the configured LLM.
6. In the **User Eval** section, select an **Eval LLM**.
7. Click **Save**.



#### 7.7 Evaluate the Movie Success Guidelines configurations

1. Open the 'Movie Success Guidelines Knowledge' Collection.
2. Select the **User Eval** tab.
3. Click the button to create a new evaluation.
4. On the **Configurations** tab, select all the configurations that you want to compare.
5. Add the selected configurations to the right pane.
6. On the **Tests** tab, select 'Movie Guidelines Evaluation'.
7. Click **OK** to start the evaluation.
8. Monitor the evaluation status until the job is complete.



When the evaluation is complete, select the job in the **User Eval** tab to review:

* The prompt submitted to each configuration;
* The response generated by the LLM;
* The assertions applied to the response;
* Which assertions passed or failed;
* The overall evaluation score.



#### 7.8 Evaluate the Movie Summaries configurations

1. Open the 'Movie Summaries Knowledge' Collection.
2. Select the **User Eval** tab.
3. Start a new evaluation.
4. On the **Configurations** tab, select all the configurations that you want to compare.
5. On the **Tests** tab, select 'Movie Summaries Evaluation'.
6. Click **OK** to start the evaluation.
7. Monitor the evaluation status until the job is complete.
8. Review the results and compare the scores of the selected configurations.



#### 7.9 Select the champion configurations

After reviewing the evaluation results, select the best-performing configuration in each Collection as the champion.



##### 7.9.1 Select the Movie Success Guidelines champion

1. Open the 'Movie Success Guidelines Knowledge' Collection.
2. Select the **Summary** tab.
3. Compare the values in the Last **User Eval** column.
4. Review the detailed evaluation results if two or more configurations have similar scores.
5. In the **Configuration Status** column, set the best-performing configuration to 'Champion'.



##### 7.9.2  Select the Movie Summaries champion

1. Open the 'Movie Summaries Knowledge' Collection.
2. Select the **Summary** tab.
3. Compare the values in the **Last User Eval** column.
4. Review the detailed evaluation results if necessary.
5. In the **Configuration Status** column, set the best-performing configuration to 'Champion'.



A configuration can have one of the following statuses:

* 'Under Evaluation': a new configuration that has not yet been selected for production use;
* 'Challenger': a configuration being tested as a possible alternative;
* 'Champion': the primary configuration used for queries by agents and end users.



> **Important**: Each Collection must have a champion configuration before it can be used by CineAgent.



##### 7.9.3 Expected result

You should now have:

* Two reusable User Eval Tests;
* One completed evaluation for the configurations in each Collection;
* Detailed results showing which prompts and assertions passed or failed;
* One champion configuration in 'Movie Success Guidelines Knowledge';
* One champion configuration in 'Movie Summaries Knowledge'.



The document-based RAG implementation is now ready for an initial test in the Chat view.









\_\_\_



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



Let's try something different.

Ask the agent to *Visualizza in un grafico la relazione tra il logaritmo del budget ed il logaritmo delle revenue*.

Satisfy with the result? To manage more complicated interaction, you need to build a more advanced agent.



### The Agent (Experiment 3)



Download the run.py file stored in the code\_templates/code\_agent



In the left panel click Code Templates

* Click **Code Agent**
* Provide a name: experiment\_3\_cineagent\_code and a description: Cineagent advanced deployment code
* In the Code tab, click the **Browse button** and import the run.py file downloaded. Remember to publish the code



In the left panel click Agents

* Create a new agent experiment named Experiment 3
* This time, the Experiment Type must be settled to Template-based experiment, select the experiment\_3\_cineagent\_code code and the right version (you should have only one version of the agent).
* You can set System Prompt, Tools and Collections as the Experiment 3



Use the Development Server to test the execution of the MCP tools that can plot a graph. Something has changed?



**Congratulation! You have completed the SAS RAM Hackathon Challenge!**

**Please, if you want, feel free to continue to test different Collections, Agents and MCP tools configuration!**





&#x20;

