# CineAgent

## Building an AI Agent to Analyze Movies and Create New Movie Stories





Welcome to the **SAS Retrieval Agent Manager Hackathon**!

In this challenge, you will build an AI agent with one mission: **understand movies and use that knowledge to help create new ones**.



Your CineAgent will work with different kinds of movie knowledge. It will explore movie plots and stories, learn the principles behind successful films, and work with structured movie data covering attributes such as titles, genres, directors, and financial performance.



Throughout this guide, you will build CineAgent **step by step**. You will start by creating and evaluating its document-based knowledge base using **Retrieval-Augmented Generation (RAG)**. Then, you will extend the agent capabilities with **MCP tools**, giving it access to structured movie data and allowing you to explore a richer set of questions and tasks.



Along the way, you will **experiment, evaluate, and improve** different versions of the agent until you are ready to select your champion.



By the end of the challenge, CineAgent will not just know about movies. **It will be ready to help you imagine the next one**.



Are you ready? Let's start!





### 1. SAS Retrieval Agent Manager



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

|**Configuration**|**Chunk size**|**Chunk overlap**|
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



**Important**: The system prompt template must include the '{context}' variable. SAS Retrieval Agent Manager replaces this variable with the content retrieved from the Collection.



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



**Tip**: You can use the same LLM for both Collections. Using the same model makes it easier to compare the effect of different Collection configurations without introducing an additional model variable.



#### 6.3 Expected result

You should now have:

* A 'Movie Guidelines Retrieval Setting' containing the custom prompt for the movie success guidelines
* A 'Movie Summaries Retrieval Setting' containing the custom prompt for the movie summaries
* An LLM configured for each Collection
* The correct custom retrieval setting assigned to the LLM in each Collection
* An Eval LLM selected for user evaluations



You are now ready to create the user evaluation tests that will be used to compare the Collection configurations.





### 7\. Evaluate the Collection configurations



The next step is to evaluate the retrieval performance of the configurations created for each Collection. You will use questions with known answers to determine which configuration produces the most accurate responses. The evaluation results will help you select a champion configuration for each Collection.



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



**Important**: Preserve the order and spelling of the expected values in the spreadsheet. Do not translate or rewrite them.



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



**Important**: Each Collection must have a champion configuration before it can be used by CineAgent.



##### 7.9.3 Expected result

You should now have:

* Two reusable User Eval Tests;
* One completed evaluation for the configurations in each Collection;
* Detailed results showing which prompts and assertions passed or failed;
* One champion configuration in 'Movie Success Guidelines Knowledge';
* One champion configuration in 'Movie Summaries Knowledge'.



The document-based RAG implementation is now ready for an initial test in the Chat view.





### 8\. Test the Collections in Chat



The document-based RAG implementation is now ready.

Before creating CineAgent, use the Chat interface to test the champion configuration of each Collection. This allows you to verify how the RAG pipeline retrieves information and generates answers from one document-based knowledge source at a time.



#### 8.1 Test the Movie Success Guidelines Collection

1. In the navigation pane, select **Chat**.
2. Select the **Collection** tab.
3. Select the 'Movie Success Guidelines Knowledge' Collection.
4. Select its champion configuration.
5. Verify that the correct LLM and 'Movie Guidelines Retrieval Setting' are selected.
6. Enter a question in the chat.



For example: *Ciao, quali sono i principali fattori che contribuiscono al successo di un film?*

Review the response and verify  that it is supported by the movie success guidelines.



#### 8.2 Test the Movie Summaries Collection

1. Remain on the **Collection** tab.
2. Select the 'Movie Summaries Knowledge' Collection.
3. Select its champion configuration.
4. Verify that the correct LLM and 'Movie Summaries Retrieval Setting' are selected.
5. Enter a question about a movie included in the Collection.



For example: *Ciao, cosa sai del film 8 Mile?*

Review the response and verify that it is based on the retrieved movie summary.



**Note**: These example questions are intentionally written in Italian. They can help you test the multilingual capabilities of the selected embedding model and LLM.



#### 8.3 Inspect the response details

After receiving a response, open the **Details** view (the button is placed at the end of the answer). Use the activity log to inspect:

* The Collection and configuration queried
* The retrieval prompt
* The documents retrieved
* The number of chunks returned
* The content and original position of each retrieved chunk
* The LLM call used to generate the final response
* The response duration and cost



Reviewing these details helps you understand how the selected configuration retrieved the information used in the answer.



##### 8.3.1 What should you check?

For each response, consider the following questions:

* Did the system retrieve information from the correct document?
* Are the retrieved chunks relevant to the question?
* Does the answer accurately reflect the retrieved content?
* Is important context missing from the answer?
* Does the system avoid providing unsupported information?
* Is the response clear and useful?



If the results are not satisfactory, return to the Collection and compare the response with another configuration. You can also review the chunk size, chunk overlap, retrieval setting, and evaluation results.



**Collection chat versus an agent**: At this stage, you are interacting directly with the RAG pipeline of a Collection. The system retrieves relevant chunks from the selected Collection and provides them to the LLM, which generates the response. It does not yet have the broader instructions, multiple knowledge sources, or tools that will be assigned to CineAgent. In the next section, you will create the first CineAgent experiment and give it access to both champion Collections.



#### 8.4 Expected result

You should now have:

* Tested the champion configuration of both Collections.
* Received answers grounded in the corresponding documents.
* Inspected the retrieval activity and retrieved chunks.
* Confirmed that both Collections are ready to be used by CineAgent.





### 9\. Create CineAgent and Experiment 1



The document-based knowledge sources are now ready to be used by an agent.



In this section, you will create 'CineAgent', an agent specialized in movies of different eras and genres. You will then configure the first agent experiment.



Experiment 1 represents the RAG-only baseline. It can retrieve information from the two Knowledge Collections but does not have access to the movie database or any MCP tools.



This baseline will make it possible to evaluate what the agent can answer using only unstructured documents.



#### 9.1 Create CineAgent

1. In the navigation pane, select **Agents**.
2. Click **Create an Agent**.
3. Enter the following information: **Name**: 'CineAgent', **Description**: 'An AI agent specialized in movies of different eras and genres. It uses movie summaries and movie success guidelines to answer questions about films and filmmaking.'
4. Leave the agent-level **System prompt** empty. The system prompt will be defined at the experiment level so that different prompts and configurations can be evaluated independently.
5. Leave the **Chat initializer command** empty.
6. Click **Create**.



The new agent is added to the **Agents** view.

**Note**: The initial status of the agent is 'No Champion'. This is expected because no experiment has been evaluated and selected as the champion yet.



#### 9.2 Create Experiment 1

1. In the **Agents** view, open 'CineAgent'.
2. Select the **Summary** tab.
3. Click **Add Agent Experiment**.
4. On the **Details** tab, enter the following information: **Name**: 'CineAgent Experiment 1 - Collections Only', **Experiment type**: 'Tools-based experiment'
5. In the **System prompt** field, enter the content of the file 'cineagent\_experiment\_1.txt' stored in the folder retrieval\_settings in the GitHub repository.
6. Configure the virtual CPU and RAM values required by your SAS Retrieval Agent Manager environment. 



**Recommendation**: Record the selected CPU and RAM values and use the same values for Experiment 2. This helps ensure that the comparison focuses on the available information sources rather than differences in computing resources.



##### 9.2.1 Configure the LLM

1. Select the **LLMs** tab.
2. Select the LLM that CineAgent should use.
3. Select the retrieval setting to associate with the LLM.
4. Add the LLM configuration to the experiment. 



**Recommendation**: Use the same LLM, model parameters, and retrieval setting in Experiment 1 and Experiment 2. The main difference between the experiments should be the availability of the MCP tools.



##### 9.2.2 Leave the Tools configuration empty

1. Select the **Tools** tab.
2. Verify that no tools are selected.
3. Do not add any MCP tools to the experiment.



This is an important constraint of Experiment 1. CineAgent must answer questions using only information retrieved from the document-based Knowledge Collections. The agent will therefore not be able to query the structured movie database during this experiment.



##### 9.2.3 Add the Knowledge Collections

1. Select the **Collections** tab.
2. Leave **Agentic retrieval** disabled.
3. Select the following Collections: 'Movie Success Guidelines Knowledge' and 'Movie Summaries Knowledge'
4. Add both Collections to the experiment.



With agentic retrieval disabled, the experiment searches all the Collections assigned to the selected LLM. This creates a simple and consistent baseline for the first evaluation.



**Important**: Both Collections must have a champion configuration. The agent uses the champion configurations when retrieving information from the Collections.



The new experiment appears on the **Summary** tab of 'CineAgent'.

Open 'CineAgent Experiment 1 - Collections Only' and verify the following configuration:



|**Configuration area**|**Expected value**|
|-|-|
|Agent|CineAgent|
|Experiment|CineAgent Experiment 1 - Collections Only|
|Experiment type|Tools-based experiment|
|System prompt|CineAgent Experiment 1 instructions|
|LLM|The LLM you prefer|
|Retrieval setting|NA|
|Tools|No tools assigned|
|Collections|Movie Success Guidelines Knowledge and Movie Summaries Knowledge|
|Agentic retrieval|Disabled|
|Agent status|No Champion. Do not select the experiment as the champion yet.|



The experiment must first be evaluated using a predefined set of questions. After reviewing the evaluation results, you will select the appropriate experiment as the champion and start the agent.



##### 9.2.4 What Experiment 1 can answer

Experiment 1 can answer questions whose information is available in: the movie summaries, the movie success guidelines and both document-based knowledge sources.



For example, it should be able to answer questions such as:

* *Cosa sai del film 8 Mile?*
* *Quali sono i principali fattori che contribuiscono al successo di un film?*
* *In base alle linee guida disponibili, quali caratteristiche potrebbero rendere efficace la storia di un film?*



##### 9.2.5 What Experiment 1 cannot reliably answer

Experiment 1 does not have access to the structured movie database. It might therefore be unable to answer questions that require structured fields, numerical filtering, aggregation, ranking, or comparisons across the complete movie dataset.



For example:

* *Quali sono i cinque film con il ROI più alto?*
* *Qual è il ROI medio dei film diretti da Christopher Nolan?*
* *Quanti film horror sono presenti nel database?*
* *Quale regista ha diretto il maggior numero di film?*



If CineAgent cannot find the required information in the assigned Collections, it should clearly explain that the available knowledge is insufficient instead of inventing an answer. These questions will become especially important when comparing Experiment 1 with Experiment 2, which will also have access to the movie database through MCP tools.



#### 9.3 Expected result

You should now have:

* One agent named 'CineAgent'
* One experiment named 'CineAgent Experiment 1 - Collections Only'
* A generic CineAgent system prompt configured at the experiment level
* One LLM and retrieval setting assigned
* The two champion Knowledge Collections assigned
* No MCP tools assigned
* Agentic retrieval disabled
* An agent whose current status is 'No Champion'



CineAgent Experiment 1 is now ready for evaluation.





### 10\. Evaluate CineAgent Experiment 1



The next step is to evaluate the responses generated by 'CineAgent Experiment 1 - Collections Only'. The process is the same as the Collection evaluation described earlier: create a reusable User Eval Test from the evaluation spreadsheet, add one test prompt for each row, and reproduce all the specified assertions without changing their values.



#### 10.1 Create the CineAgent User Eval Test

1. In the navigation pane, select **User Eval Tests**.
2. Click **New**.
3. Enter the following information: **Name**: 'CineAgent Evaluation', **Description**: Evaluates CineAgent responses across document-based and structured movie questions, **Passing Threshold**: 100
4. Click **OK**.
5. Add the questions and assertions from the CineAgent evaluation spreadsheet, following the same procedure used for the Collection evaluation tests (file name is: 'cineagent\_evaluation.xlsx').



**Important**: Preserve the spelling, order, metrics, and expected values provided in the spreadsheet.



The evaluation set should include: (1) questions that can be answered using the movie summaries, (2) questions that can be answered using the movie success guidelines and (3) questions that require structured movie data, such as filtering, ranking, counting, or aggregation. The third category is expected to expose the limitations of Experiment 1 because this experiment does not have access to the movie database or MCP tools.



#### 10.2 Run the evaluation

1. In the navigation pane, select **Agents**.
2. Open 'CineAgent'.
3. Select the **User Evaluation** tab.
4. Create a new evaluation.
5. On the **Experiments** tab, select 'CineAgent Experiment 1 - Collections Only'.
6. On the **Tests** tab, select 'CineAgent Evaluation'.
7. Click **OK** to start the evaluation.
8. Wait until the evaluation status is 'Complete'.



When the evaluation is complete, review:

* The overall score.
* The prompts submitted to the experiment.
* The responses generated by CineAgent.
* The prompts that passed or failed.
* The response cost.
* Any incorrect or unsupported answers.



**Note**: Do not select Experiment 1 as the champion yet. Its results will be compared with Experiment 2 after the MCP tools have been deployed and assigned to CineAgent.



#### 10.3 Expected result

You should now have:

* One reusable User Eval Test named 'CineAgent Evaluation';
* One completed evaluation for 'CineAgent Experiment 1 - Collections Only';
* A baseline score showing how CineAgent performs using only the two Knowledge Collections;
* Identified questions that require access to the structured movie database.





### 11\. Deploy the Movie Database MCP Server



Experiment 1 demonstrated what CineAgent can answer using only the two document-based Knowledge Collections.



The next step is to make the structured movie database available through a Model Context Protocol (MCP) tool server. The server provides 25 tools that CineAgent can use to search, filter, aggregate, rank, analyze, and visualize the movie data.



The deployment consists of two steps: (1) create an MCP tool server template from the code provided in the GitHub repository and (2) create and start an MCP tool server based on that template.



#### 11.1 Create the MCP tool server template

1. In the GitHub repository, open the folder containing the Movie Database MCP server files (code\_templates/code\_mcp\_server). Download from the GitHub repository the three files run.py, requirements.txt and README.md
2. In SAS Retrieval Agent Manager, navigate to **Code Templates**.
3. Click **Code MCP Server**.
4. Enter the following information: **Name**: 'Movie Database MCP Template', **Description**: 'Provides tools for searching and analyzing the structured movie database.'
5. Select the **Code** tab.
6. Click Browse and upload the three files
7. Click **OK** to save the template.



**Important**: Copy the code, dependencies, and environment-variable names exactly as provided. Do not rename the MCP tools because their names and descriptions help CineAgent select the appropriate operation.



#### 11.2 Create the Movie Database MCP server

1. In the navigation pane, select **MCP Tools**.
2. Click the button to create a new tool server.
3. Enter the following information: **Name**: 'Movie Database MCP Server', **Description**: 'Provides structured search, filtering, aggregation, statistical analysis, and visualization tools for the movie database.'
4. Select **Custom**.
5. Select 'Movie Database MCP Template'.
6. Select the latest available template version.
7. Click **Select Template**.
8. If required, configure the authentication and environment-variable values.
9. Click **Finish**.



The new server is added to the **MCP Tool Servers** table.



#### 11.3 Start the MCP server

1. Select 'Movie Database MCP Server'.
2. Check its current value in the **Server Status** column.
3. Click the start button.
4. Wait until the server is running.
5. Verify that the ping status indicates that the server is reachable.



Starting the server makes its tools available for assignment to agent experiments.



**Important**: The MCP server must remain running while CineAgent uses its tools. If the server is stopped, its tools become unavailable to the agent.



#### 11.4 Verify the available tools

Select 'Movie Database MCP Server' in the **MCP Tool Servers** table.

When the server is running, the details pane should display **25 tools**. The tools are organized around the following capabilities:



|**Capability**|**Example tools**|**Purpose**|
|-|-|-|
|Dataset discovery and retrieval|'get\_dataset\_schema', 'search\_movies', 'get\_movie', 'filter\_movies', 'rank\_movies'|Explore the database and retrieve movie records using textual or structured conditions.|
|Aggregation and comparison|'aggregate\_movies', 'compare\_segments', 'analyze\_release\_timing', 'analyze\_trends'|Calculate summary metrics and compare movies across categories or periods.|
|Statistical exploration|'describe\_metrics', 'correlation\_analysis', 'detect\_outliers', 'distribution\_analysis'|Examine distributions, correlations, descriptive statistics, and unusual observations.|
|Financial performance|'analyze\_profitability', 'find\_sleeper\_hits', 'find\_box\_office\_bombs'|Analyze budgets, revenue, profit, ROI, and financial outcomes.|
|Talent and market analysis|'analyze\_talent', 'analyze\_companies', 'analyze\_genres', 'analyze\_countries'|Compare directors, writers, stars, companies, genres, and countries.|
|Data quality|'data\_quality\_report', 'missing\_data\_analysis'|Identify missing values, duplicates, invalid numeric values, and other data-quality issues.|
|Visualization and routing|'create\_chart', 'answer\_movie\_analysis'|Produce chart data or suggest which analytical tool is appropriate for a question.|





The descriptions are particularly important because they allow the LLM to determine which tool is suitable for the user's request.



#### 11.5 Understand the MCP capabilities

The tools enable CineAgent to answer questions that Experiment 1 could not reliably handle, including:

* *Quali sono i cinque film con il ROI più alto?*
* *Qual è il budget medio dei film diretti da Christopher Nolan?*
* *Quanti film horror sono presenti nel database?*
* *Quali generi hanno il ROI mediano più elevato?*
* *Quali film possono essere considerati sleeper hits?*
* *Esiste una correlazione tra budget e revenue?*
* *Crea un grafico dei ricavi medi per genere.*



The MCP server does not replace the Knowledge Collections. Instead, it adds access to structured movie records and analytical operations.



The Collections remain better suited to questions about:

* Movie plots and narrative details;
* The content of individual movie summaries;
* Qualitative guidelines for producing a successful film.



The MCP tools are better suited to questions involving: precise field values, filters and sorting, counts and aggregations, rankings, financial metrics, statistical comparisons, trends and charts.



Experiment 2 will combine both approaches, allowing CineAgent to retrieve unstructured information from the Collections and analyze structured information through the MCP tools.



#### 11.6 Expected result

You should now have:

* One code template named 'Movie Database MCP Template'.
* One tool server named 'Movie Database MCP Server'.
* A running and reachable MCP server.
* 25 available movie-analysis tools.
* Tool descriptions and parameters visible in the server details.
* The structured movie database ready to be assigned to 'CineAgent Experiment 2'.





### 12\. Create CineAgent Experiment 2



'CineAgent Experiment 2 - Collections and MCP Tools' extends Experiment 1 by giving CineAgent access to the structured movie database through the MCP tools.



Follow the same procedure used for 'CineAgent Experiment 1 - Collections Only', with the following differences:

1. Create a new agent experiment named 'CineAgent Experiment 2 - Collections and MCP Tools'.
2. Select **Tools-based experiment**.
3. Copy the system prompt from 'cineagent\_experiment\_2.txt', located in the 'retrieval\_settings' folder of the GitHub repository.
4. On the **LLMs** tab, select the same LLM used for Experiment 1.
5. On the **Tools** tab, add all the tools provided by 'Movie Database MCP Server'.
6. On the **Collections** tab, add: 'Movie Success Guidelines Knowledge' and 'Movie Summaries Knowledge'.
7. Use the same CPU and RAM values as Experiment 1.
8. Click **Create**.



Experiment 2 can now combine document retrieval with structured movie-data analysis.



#### 12.1 Evaluate CineAgent Experiment 2

Run 'CineAgent Evaluation' against 'CineAgent Experiment 2 - Collections and MCP Tools'. Compare its score and responses with 'CineAgent Experiment 1 - Collections Only', paying particular attention to questions that require filtering, ranking, counting, aggregation, financial metrics, or statistical analysis.



You can also repeat the questions tested manually during Experiment 1. Open the response details to verify which MCP tools were called and inspect their inputs and outputs.

For example:

* *Quali sono i cinque film con il ROI più alto?*
* *Qual è il budget medio dei film diretti da Christopher Nolan?*



#### 12.2 Test chart generation

Submit the following request: *Visualizza in un grafico la relazione tra il logaritmo del budget e il logaritmo delle revenue.*

Experiment 2 can use the MCP tools to generate the chart data and image. However, its standard tools-based workflow does not render the generated image directly in the chat output. To support this richer interaction, you will create a template-based experiment.



#### 12.3 Create the CineAgent visual-output template

1. In the GitHub repository, open 'code\_templates/code\_agent'.
2. Download the run.py file containing the agent template files.
3. In SAS Retrieval Agent Manager, select **Code Templates**.
4. Click **Code Agent**.
5. Enter **Name**: 'CineAgent Visual Output Agent Template', **Description**: 'Template that enables CineAgent to display generated charts in its responses.'
6. On the **Code** tab, click **Browse** and upload the run.py file.
7. Configure any aliases or environment variables required by the template.
8. Click **Save**.
9. Select 'CineAgent Visual Output Agent Template' and publish it. Publishing the template makes it available when creating a template-based agent experiment.



### 13\. Create CineAgent Experiment 3



'CineAgent Experiment 3 - Template-Based Visual Output' extends Experiment 2 with a custom agent template that can display generated charts directly in the response. 



**Note**: A template-based approach provides greater flexibility and control by allowing developers to customize the agent’s execution logic, process tool outputs, support richer response formats such as images, and reuse the same implementation across multiple agent experiments.



1. Open 'CineAgent'.
2. Select the **Summary** tab.
3. Add a new agent experiment.
4. Enter: **Name**: 'CineAgent Experiment 3 - Template-Based Visual Output', **Experiment type**: 'Template-based experiment'
5. Select 'CineAgent Visual Output Agent Template'.
6. Select the published template version.
7. Configure the same system prompt used for Experiment 2.
8. Assign the same LLM, Collections, and MCP tools used for Experiment 2.
9. Configure the aliases and environment variables required by the template.
10. Click **Create**.



#### 13.1 Test CineAgent Experiment 3

Use the **Development Server** to test 'CineAgent Experiment 3 - Template-Based Visual Output'. 

Submit the chart request again: *Visualizza in un grafico la relazione tra il logaritmo del budget e il logaritmo delle revenue*.



Verify that the experiment:

* Calls the appropriate MCP tool;
* Receives the chart generated by the tool;
* Displays the resulting image in the chat output.



The analytical result should be consistent with Experiment 2. The difference is that Experiment 3 processes the tool output through the custom agent template and renders the chart in the response.



### 14\. Compare the CineAgent experiments



|**Agent experiment**|**Knowledge Collections**|**MCP tools**|**Images in chat**|
|-|-|-|-|
|CineAgent Experiment 1 - Collections Only|Yes|No|No|
|CineAgent Experiment 2 - Collections and MCP Tools|Yes|Yes|No|
|CineAgent Experiment 3 - Template-Based Visual Output|Yes|Yes|Yes|





Run 'CineAgent Evaluation' against Experiments 2 and 3 and compare their results with the Experiment 1 baseline.



After reviewing the scores and manual tests:

1. Select the best-performing experiment;
2. Set its **Status** to 'Champion';
3. Start 'CineAgent'.



The running champion experiment can then be used from the **Agent** tab in the Chat interface.





### Congratulations!

#### Congratulations! You have successfully completed the CineAgent challenge.



You created and evaluated document-based Knowledge Collections, built a reusable evaluation framework, deployed a Movie Database MCP Server, and progressively enhanced CineAgent through three experiments:

* 'CineAgent Experiment 1 - Collections Only'
* 'CineAgent Experiment 2 - Collections and MCP Tools'
* 'CineAgent Experiment 3 - Template-Based Visual Output'



You now have an agent that can combine unstructured movie knowledge, structured data analysis, MCP tools, and richer visual responses.



Thank you for taking part in this challenge. We hope you enjoyed building CineAgent and exploring the capabilities of SAS Retrieval Agent Manager.



**Well done, and have fun experimenting with your agent!**



&#x20;

