# CineAgent

## Build an AI Agent to Analyze Movies and Create New Stories

Welcome to the **SAS Retrieval Agent Manager Hackathon**!

In this challenge, you will build **CineAgent**, an AI agent that understands movies and helps create new ones. CineAgent will work with:

- **Unstructured knowledge**: movie plots, summaries, and filmmaking guidelines.
- **Structured data**: titles, genres, directors, budgets, revenue, and other movie attributes.
- **MCP tools**: search, filtering, aggregation, statistical analysis, and visualization.

You will build CineAgent step by step:

1. Create and evaluate a document-based knowledge base using **RAG**.
2. Extend the agent with **MCP tools** for structured movie data.
3. Experiment, evaluate, and improve different agent versions.
4. Select your champion experiment.

By the end, CineAgent will not only know about movies — it will help you imagine the next one.

---

## 1. SAS Retrieval Agent Manager

You will build CineAgent using **SAS Retrieval Agent Manager**.

SAS Retrieval Agent Manager provides the environment to:

- Create **Sources** and **RAG Collections**.
- Configure and run vectorization jobs.
- Create retrieval settings and user evaluations.
- Build and compare agent experiments.
- Integrate MCP tools.

### Useful resources

- [SAS Retrieval Agent Manager](https://www.sas.com/en_us/software/retrieval-agent-manager.html)
- [SAS Help Center](https://go.documentation.sas.com/doc/en/ragntmgrcdc/v_013/ragntmgrug/titlepage.htm?fromDefault=)
- [SAS Learning Portal](https://learn.sas.com/)

---

## 2. Create the Sources

A **Source** contains the raw documents that will later be processed and indexed by the RAG pipeline.

In the repository’s `documents` folder, download:

| File | Content |
|---|---|
| `movies_summary.pdf` | Movie IDs, titles, and plot summaries |
| `movies_success_guidelines.txt` | Guidelines on storytelling, audience, production, economics, marketing, and distribution |

Create **two separate Sources**:

### Movie Summaries

1. Go to **Sources** → **Local Files**.
2. Enter:
   - **Name**: `Movie Summaries`
   - **Description**: `Movie plot summaries used to answer questions about movie stories, characters, and themes.`
3. Upload `movies_summary.pdf`.
4. Select **Save**.

### Movie Success Guidelines

1. Go to **Sources** → **Local Files**.
2. Enter:
   - **Name**: `Movie Success Guidelines`
   - **Description**: `Guidelines for developing and evaluating a successful movie, including storytelling, audience, production, financial considerations, marketing, and distribution.`
3. Upload `movies_success_guidelines.txt`.
4. Select **Save**.

> **Why two Sources?**  
> Separate Sources let you create, configure, and evaluate independent RAG Collections. This makes it easier to test different chunking and retrieval strategies for each type of content.

### Checklist

- [ ] `Movie Summaries` contains `movies_summary.pdf`
- [ ] `Movie Success Guidelines` contains `movies_success_guidelines.txt`

---

## 3. Create the Collections

A **Collection** connects one or more Sources to configurations that define chunking, embedding, storage, and retrieval.

Create the following Collections:

| Collection | Source |
|---|---|
| `Movie Summaries Knowledge` | `Movie Summaries` |
| `Movie Success Guidelines Knowledge` | `Movie Success Guidelines` |

### Movie Summaries Knowledge

1. Go to **Collections** → **New Collection**.
2. Enter:
   - **Name**: `Movie Summaries Knowledge`
   - **Description**: `A RAG Collection containing movie titles and plot summaries. Each movie entry includes a movie ID, title, and summary.`
3. Select the `Movie Summaries` Source.
4. Select **Save**.

### Movie Success Guidelines Knowledge

1. Go to **Collections** → **New Collection**.
2. Enter:
   - **Name**: `Movie Success Guidelines Knowledge`
   - **Description**: `A RAG Collection containing guidelines for developing and evaluating a successful movie.`
3. Select the `Movie Success Guidelines` Source.
4. Select **Save**.

### Checklist

- [ ] Both Collections are created
- [ ] Each Collection is linked to the correct Source

---

## 4. Configure and Vectorize the Collections

A **configuration** defines how documents are chunked, embedded, stored, and retrieved.

> **Important**  
> You cannot edit a configuration after saving it. To test different values, create a new configuration or copy an existing one.

### Create configurations

For each Collection, create **at least three configurations** with different chunking parameters.

Example for `Movie Summaries Knowledge`:

| Configuration | Chunk size | Chunk overlap |
|---|---:|---:|
| `summaries-config-01` | 256 | 36 |
| `summaries-config-02` | 512 | 64 |
| `summaries-config-03` | 128 | 0 |

Use descriptive names for the guidelines configurations, for example:

- `guidelines-config-01`
- `guidelines-config-02`
- `guidelines-config-03`

For every configuration:

1. Open the Collection.
2. On the **Summary** tab, select **Create a new configuration**.
3. In **Basics**, configure:
   - **Name**: a unique, descriptive name.
   - **Description**: the purpose or parameters of the configuration.
   - **Embedding model**: select an embedding model. Use a multilingual model if you plan to query in multiple languages.
   - **Destination**: select the PostgreSQL vector database provided for the hackathon.
   - **Configuration update strategy**: `Append and sync`.
4. In **Settings**, set the desired **Chunk size** and **Chunk overlap**.
5. Leave other settings at their default values unless instructed otherwise.
6. Select **Save**.

### Run vectorization

For every configuration:

1. Select it on the **Summary** tab.
2. Review the execution settings.
3. Select **Submit**.
4. Monitor **Vectorization Status** until it is `Completed`.

> If the status is `Error`, open the job log, review the error details, and contact a hackathon organizer if needed.

### Checklist

- [ ] At least three configurations per Collection
- [ ] Different chunk size and overlap values across configurations
- [ ] Every vectorization job completed successfully

---

## 5. Create Retrieval Settings

A **retrieval setting** controls how retrieved context is provided to the LLM.

Create two custom retrieval settings:

| Retrieval setting | Prompt file |
|---|---|
| `Movie Guidelines Retrieval Setting` | `retrieval_settings/movie_guideline_collection.txt` |
| `Movie Summaries Retrieval Setting` | `retrieval_settings/movie_summary_collection.txt` |

> **Important**  
> The system prompt template must include the `{context}` variable. SAS Retrieval Agent Manager replaces it with the content retrieved from the Collection.

### Movie Guidelines Retrieval Setting

1. Go to **Retrieval Settings** → **New**.
2. Enter **Name**: `Movie Guidelines Retrieval Setting`.
3. Open `retrieval_settings/movie_guideline_collection.txt`.
4. Copy its full content into **System prompt template**.
5. Verify that `{context}` is present.
6. Leave other parameters unchanged.
7. Select **OK**.

### Movie Summaries Retrieval Setting

1. Go to **Retrieval Settings** → **New**.
2. Enter **Name**: `Movie Summaries Retrieval Setting`.
3. Open `retrieval_settings/movie_summary_collection.txt`.
4. Copy its full content into **System prompt template**.
5. Verify that `{context}` is present.
6. Leave other parameters unchanged.
7. Select **OK**.

---

## 6. Assign Retrieval Settings to Collections

Creating a retrieval setting does not automatically associate it with a Collection. You must assign it to an LLM in each Collection.

### Movie Success Guidelines Knowledge

1. Go to **Collections** and open `Movie Success Guidelines Knowledge`.
2. Open the **LLMs** tab.
3. Add the LLM you want to use.
4. Assign `Movie Guidelines Retrieval Setting`.
5. In **User Eval**, select the **Eval LLM**.
6. Select **Save**.

### Movie Summaries Knowledge

1. Go to **Collections** and open `Movie Summaries Knowledge`.
2. Open the **LLMs** tab.
3. Add the LLM you want to use.
4. Assign `Movie Summaries Retrieval Setting`.
5. In **User Eval**, select the **Eval LLM**.
6. Select **Save**.

> **Tip**  
> Use the same LLM for both Collections. This makes it easier to compare configurations without introducing an additional model variable.

### Checklist

- [ ] Each Collection has at least one configured LLM
- [ ] The correct retrieval setting is assigned to each LLM
- [ ] An Eval LLM is selected for both Collections

---

## 7. Evaluate Collection Configurations

Use evaluation questions with known answers to compare retrieval configurations and select a champion for each Collection.

The repository provides:

| Evaluation file | Collection |
|---|---|
| `evaluation_tests/movie_guidelines_evaluation.xlsx` | `Movie Success Guidelines Knowledge` |
| `evaluation_tests/movie_summary_evaluation.xlsx` | `Movie Summaries Knowledge` |

Each spreadsheet row contains:

- A question.
- One or more evaluation metrics.
- Expected values or conditions.

### Create User Eval Tests

Create two tests:

| Test | Description | Passing threshold |
|---|---|---:|
| `Movie Guidelines Evaluation` | Evaluates responses from the Movie Success Guidelines Knowledge Collection | 100 |
| `Movie Summaries Evaluation` | Evaluates responses from the Movie Summaries Knowledge Collection | 100 |

For each spreadsheet row:

1. Copy `Question` into **Prompt**.
2. Set **Passing threshold (%)** to `100`.
3. Under **Assertions**:
   - Select the metric from `Metric`.
   - Enter the expected value from `Condition`.
4. For additional `Metric n` / `Condition n` pairs, select **New assertion** and repeat.
5. Save the test prompt.

> **Important**  
> Preserve the order, spelling, metrics, and expected values exactly as provided. Do not translate or rewrite them.

### Run evaluations

For each Collection:

1. Open the Collection.
2. Go to **User Eval**.
3. Create a new evaluation.
4. In **Configurations**, select all configurations to compare.
5. In **Tests**, select the corresponding evaluation test.
6. Select **OK**.
7. Wait for the evaluation to complete.
8. Review prompt responses, assertion results, and overall scores.

### Select champion configurations

For each Collection:

1. Open the Collection.
2. Go to **Summary**.
3. Compare the **Last User Eval** scores.
4. Inspect detailed results if scores are close.
5. Set the best configuration’s **Configuration Status** to `Champion`.

Configuration statuses:

| Status | Meaning |
|---|---|
| `Under Evaluation` | New configuration not yet selected for production use |
| `Challenger` | Configuration being tested as an alternative |
| `Champion` | Primary configuration used by agents and end users |

> **Important**  
> Each Collection must have a champion configuration before CineAgent can use it.

### Checklist

- [ ] Two reusable User Eval Tests created
- [ ] Evaluations completed for both Collections
- [ ] One champion configuration selected per Collection

---

## 8. Test the Collections in Chat

Before creating CineAgent, test each Collection’s champion configuration in the **Chat** view.

### Test Movie Success Guidelines

1. Go to **Chat** → **Collection**.
2. Select `Movie Success Guidelines Knowledge`.
3. Select its champion configuration.
4. Verify the LLM and `Movie Guidelines Retrieval Setting`.
5. Ask, for example:

   > Ciao, quali sono i principali fattori che contribuiscono al successo di un film?

### Test Movie Summaries

1. Select `Movie Summaries Knowledge`.
2. Select its champion configuration.
3. Verify the LLM and `Movie Summaries Retrieval Setting`.
4. Ask, for example:

   > Ciao, cosa sai del film 8 Mile?

> **Note**  
> The example questions are in Italian to help test multilingual retrieval and generation.

### Inspect responses

Open **Details** at the end of an answer and check:

- The Collection and configuration queried.
- The retrieval prompt.
- Retrieved documents and chunks.
- The number of chunks returned.
- The LLM call and response duration/cost.

Ask yourself:

- Did the system retrieve from the correct document?
- Are the retrieved chunks relevant?
- Is the answer supported by the retrieved context?
- Is important context missing?
- Does the system avoid unsupported information?

> **Collection chat vs. agent**  
> At this stage, you are testing a single RAG Collection directly. CineAgent will later combine both Collections, agent instructions, and MCP tools.

---

## 9. Create CineAgent and Experiment 1

Experiment 1 is the **RAG-only baseline**: CineAgent can use both Knowledge Collections but has no access to the structured movie database or MCP tools.

### Create CineAgent

1. Go to **Agents** → **Create an Agent**.
2. Enter:
   - **Name**: `CineAgent`
   - **Description**: `An AI agent specialized in movies of different eras and genres. It uses movie summaries and movie success guidelines to answer questions about films and filmmaking.`
3. Leave **System prompt** and **Chat initializer command** empty.
4. Select **Create**.

> The initial agent status is `No Champion`. This is expected until an experiment is evaluated and promoted.

### Create Experiment 1

1. Open `CineAgent`.
2. Go to **Summary** → **Add Agent Experiment**.
3. In **Details**, enter:
   - **Name**: `CineAgent Experiment 1 - Collections Only`
   - **Experiment type**: `Tools-based experiment`
   - **System prompt**: copy the content of `retrieval_settings/cineagent_experiment_1.txt`
4. Configure the CPU and RAM required by your environment.

> **Recommendation**  
> Use the same CPU and RAM values for Experiment 2 so that performance differences reflect available information sources, not compute resources.

### Configure the LLM

1. Open the **LLMs** tab.
2. Select the LLM for CineAgent.
3. Select the retrieval setting.
4. Add the LLM configuration to the experiment.

Use the same LLM, model parameters, and retrieval setting in Experiments 1 and 2.

### Leave Tools empty

1. Open the **Tools** tab.
2. Verify that no tools are selected.
3. Do **not** add MCP tools.

### Add Knowledge Collections

1. Open the **Collections** tab.
2. Leave **Agentic retrieval** disabled.
3. Add:
   - `Movie Success Guidelines Knowledge`
   - `Movie Summaries Knowledge`

With agentic retrieval disabled, the experiment searches all Collections assigned to the selected LLM.

### Expected configuration

| Area | Expected value |
|---|---|
| Agent | `CineAgent` |
| Experiment | `CineAgent Experiment 1 - Collections Only` |
| Experiment type | `Tools-based experiment` |
| System prompt | Experiment 1 instructions |
| LLM | Your selected LLM |
| Tools | None |
| Collections | Both Knowledge Collections |
| Agentic retrieval | Disabled |
| Agent status | `No Champion` |

### What Experiment 1 can answer

It can answer questions supported by the movie summaries, the success guidelines, or both. For example:

- *Cosa sai del film 8 Mile?*
- *Quali sono i principali fattori che contribuiscono al successo di un film?*
- *In base alle linee guida disponibili, quali caratteristiche potrebbero rendere efficace la storia di un film?*

### What Experiment 1 cannot reliably answer

It does not have access to the structured movie database, so it may struggle with filtering, ranking, counting, aggregation, or comparisons. For example:

- *Quali sono i cinque film con il ROI più alto?*
- *Qual è il ROI medio dei film diretti da Christopher Nolan?*
- *Quanti film horror sono presenti nel database?*
- *Quale regista ha diretto il maggior numero di film?*

If the required information is unavailable, CineAgent should clearly state that its knowledge is insufficient rather than inventing an answer.

---

## 10. Evaluate Experiment 1

Create a reusable evaluation for CineAgent using `evaluation_tests/cineagent_evaluation.xlsx`.

### Create the evaluation

1. Go to **User Eval Tests** → **New**.
2. Enter:
   - **Name**: `CineAgent Evaluation`
   - **Description**: `Evaluates CineAgent responses across document-based and structured movie questions`
   - **Passing Threshold**: `100`
3. Add one prompt and its assertions for every spreadsheet row.
4. Preserve spelling, order, metrics, and expected values.

The evaluation should include:

1. Questions answerable from movie summaries.
2. Questions answerable from success guidelines.
3. Questions requiring structured movie data.

The third category should expose the limitations of Experiment 1.

### Run the evaluation

1. Go to **Agents** and open `CineAgent`.
2. Open **User Evaluation**.
3. Create a new evaluation.
4. In **Experiments**, select `CineAgent Experiment 1 - Collections Only`.
5. In **Tests**, select `CineAgent Evaluation`.
6. Select **OK**.
7. Wait for the evaluation to complete.

Review:

- Overall score.
- Prompts and responses.
- Passed and failed prompts.
- Response cost.
- Incorrect or unsupported answers.

> **Note**  
> Do not select Experiment 1 as champion yet. Compare it with Experiment 2 after deploying the MCP tools.

---

## 11. Deploy the Movie Database MCP Server

The Movie Database MCP Server provides **25 tools** for searching, filtering, aggregating, ranking, analyzing, and visualizing structured movie data.

### Create the MCP template

1. In the repository, open `code_templates/code_mcp_server`.
2. Download:
   - `run.py`
   - `requirements.txt`
   - `README.md`
3. In SAS Retrieval Agent Manager, go to **Code Templates** → **Code MCP Server**.
4. Enter:
   - **Name**: `Movie Database MCP Template`
   - **Description**: `Provides tools for searching and analyzing the structured movie database.`
5. In **Code**, upload the three files.
6. Select **OK**.

> **Important**  
> Copy the code, dependencies, and environment-variable names exactly as provided. Do not rename the MCP tools: their names and descriptions help CineAgent choose the right operation.

### Create and start the server

1. Go to **MCP Tools**.
2. Create a new tool server.
3. Enter:
   - **Name**: `Movie Database MCP Server`
   - **Description**: `Provides structured search, filtering, aggregation, statistical analysis, and visualization tools for the movie database.`
4. Select **Custom**.
5. Select `Movie Database MCP Template` and its latest version.
6. Configure authentication and environment variables if required.
7. Select **Finish**.
8. Start the server.
9. Wait until it is running and reachable.

> **Important**  
> The MCP server must remain running while CineAgent uses its tools.

### Available tool capabilities

| Capability | Example tools | Purpose |
|---|---|---|
| Dataset discovery and retrieval | `get_dataset_schema`, `search_movies`, `get_movie`, `filter_movies`, `rank_movies` | Explore the database and retrieve movie records |
| Aggregation and comparison | `aggregate_movies`, `compare_segments`, `analyze_release_timing`, `analyze_trends` | Calculate metrics and compare categories or periods |
| Statistical exploration | `describe_metrics`, `correlation_analysis`, `detect_outliers`, `distribution_analysis` | Analyze distributions, correlations, and outliers |
| Financial performance | `analyze_profitability`, `find_sleeper_hits`, `find_box_office_bombs` | Analyze budgets, revenue, profit, ROI, and outcomes |
| Talent and market analysis | `analyze_talent`, `analyze_companies`, `analyze_genres`, `analyze_countries` | Compare directors, writers, stars, companies, genres, and countries |
| Data quality | `data_quality_report`, `missing_data_analysis` | Identify missing values, duplicates, and invalid numeric values |
| Visualization and routing | `create_chart`, `answer_movie_analysis` | Produce chart data or select an appropriate analytical tool |

### When to use Collections vs. MCP tools

| Question type | Best source |
|---|---|
| Plot, characters, narrative details | Knowledge Collections |
| Filmmaking and success guidelines | Knowledge Collections |
| Filters, sorting, counts, rankings | MCP tools |
| Financial metrics and statistical comparisons | MCP tools |
| Trends and charts | MCP tools |

---

## 12. Create Experiment 2

`CineAgent Experiment 2 - Collections and MCP Tools` extends Experiment 1 with access to the structured movie database.

1. Open `CineAgent`.
2. Add a new agent experiment.
3. Enter:
   - **Name**: `CineAgent Experiment 2 - Collections and MCP Tools`
   - **Experiment type**: `Tools-based experiment`
   - **System prompt**: copy `retrieval_settings/cineagent_experiment_2.txt`
4. Use the same LLM as Experiment 1.
5. Add all tools from `Movie Database MCP Server`.
6. Add both Knowledge Collections.
7. Use the same CPU and RAM values as Experiment 1.
8. Select **Create**.

### Evaluate Experiment 2

Run `CineAgent Evaluation` against Experiment 2 and compare it with Experiment 1. Focus on questions involving:

- Filtering and ranking.
- Counting and aggregation.
- Financial metrics.
- Statistical analysis.

Example questions:

- *Quali sono i cinque film con il ROI più alto?*
- *Qual è il budget medio dei film diretti da Christopher Nolan?*

Open response details to inspect which MCP tools were called, along with their inputs and outputs.

### Test chart generation

Submit:

> Visualizza in un grafico la relazione tra il logaritmo del budget e il logaritmo delle revenue.

Experiment 2 can generate chart data and images through MCP tools, but its standard tools-based workflow does not render the image directly in chat. Use a template-based experiment for that.

### Create the visual-output template

1. In the repository, open `code_templates/code_agent`.
2. Download `run.py`.
3. Go to **Code Templates** → **Code Agent**.
4. Enter:
   - **Name**: `CineAgent Visual Output Agent Template`
   - **Description**: `Template that enables CineAgent to display generated charts in its responses.`
5. Upload `run.py`.
6. Configure aliases and environment variables as required.
7. Select **Save**.
8. Publish the template.

---

## 13. Create Experiment 3

`CineAgent Experiment 3 - Template-Based Visual Output` extends Experiment 2 by rendering generated charts directly in the chat response.

1. Open `CineAgent`.
2. Add a new agent experiment.
3. Enter:
   - **Name**: `CineAgent Experiment 3 - Template-Based Visual Output`
   - **Experiment type**: `Template-based experiment`
4. Select `CineAgent Visual Output Agent Template` and its published version.
5. Use the same system prompt, LLM, Collections, and MCP tools as Experiment 2.
6. Configure aliases and environment variables.
7. Select **Create**.

### Test visual output

Use the **Development Server** and submit:

> Visualizza in un grafico la relazione tra il logaritmo del budget e il logaritmo delle revenue.

Verify that the experiment:

- Calls the appropriate MCP tool.
- Receives the generated chart.
- Displays the image in the chat response.

---

## 14. Compare the Experiments

| Experiment | Knowledge Collections | MCP tools | Images in chat |
|---|:---:|:---:|:---:|
| Experiment 1 — Collections Only | Yes | No | No |
| Experiment 2 — Collections and MCP Tools | Yes | Yes | No |
| Experiment 3 — Template-Based Visual Output | Yes | Yes | Yes |

Run `CineAgent Evaluation` against Experiments 2 and 3, then compare the results with the Experiment 1 baseline.

After reviewing scores and manual tests:

1. Select the best-performing experiment.
2. Set its **Status** to `Champion`.
3. Start `CineAgent`.

You can then use the running champion from the **Agent** tab in Chat.

---

## 15. Congratulations!

You have completed the CineAgent challenge.

You created and evaluated document-based Knowledge Collections, built a reusable evaluation framework, deployed a Movie Database MCP Server, and progressively enhanced CineAgent through three experiments:

- `CineAgent Experiment 1 - Collections Only`
- `CineAgent Experiment 2 - Collections and MCP Tools`
- `CineAgent Experiment 3 - Template-Based Visual Output`

You now have an agent that combines unstructured movie knowledge, structured data analysis, MCP tools, and richer visual responses.

**Well done, and have fun experimenting with your agent!**