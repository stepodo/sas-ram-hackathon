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

* Official Webpage: https://www.sas.com/en\_us/software/retrieval-agent-manager.html
* SAS Help Center for SAS RAM: https://go.documentation.sas.com/doc/en/ragntmgrcdc/v\_013/ragntmgrug/titlepage.htm?fromDefault=
* SAS Learning Portal: https://learn.sas.com/



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

**Movie Summaries:** This Source contains movie summaries.

**Movie Success Guidelines:** This Source contains guidelines for developing and evaluating a successful movie.



Upload the corresponding file to each Source.



**Why two Sources?** Keeping the documents separate will allow us to build and experiment with two distinct knowledge bases in the next steps.





### The Collections



\[...]





### The Agent



\[...]





### The MCP Server



\[...]



##### MCP tool descriptions

The code defines **25** functions decorated with '@tool'.

Below is a description of each tool, grouped by purpose and based on its actual implementation.



###### 1\. Dataset discovery and movie retrieval

* **get\_dataset\_schema**: Returns an overview of the movie dataset, including its number of rows and columns, column names, data types, missing-value counts and percentages, and number of distinct values. It also provides minimum and maximum values for numeric columns and a sample of the first records. The sample defaults to 5 rows and is capped at 20.
* **search\_movies**: Searches for movies using case-insensitive partial matches on title, genre, director, writer, star, company, country, and content rating. It can also restrict results to an inclusive year range, using 'release\_year' when available and otherwise 'year'. All supplied criteria are combined with AND logic. Returns matching movie records, the total match count, and the applied filters.
* **get\_movie**: Retrieves movie records by title, placing case-insensitive exact matches before partial matches. Records appearing in both sets are deduplicated by their DataFrame index. Returns all available fields for each selected movie, with 10 results by default and a maximum of 50.
* **filter\_movies**: Retrieves movie records using structured filter conditions. Supports equality, inequality, numeric comparisons, inclusive ranges, list membership, case-insensitive substring matching, and missing-value checks. It can select specific output columns, sort the results, and limit the number of returned records. Multiple filters are combined with AND logic.
* **rank\_movies**: Ranks movies by a selected numeric metric, such as revenue, score, budget, profit, or ROI, after applying optional filters. It excludes records whose ranking metric cannot be interpreted as numeric or is missing. Results are sorted from highest to lowest by default; ascending order produces a bottom-ranked list. Returns the movie title, release year, genre, and selected metric where available.



###### 2\. Aggregation and segment comparison

* **aggregate\_movies**: Calculates one or more summary metrics across the full dataset or within groups defined by one or more columns. Supported aggregations are 'count', 'nunique', 'sum', 'mean', 'median', 'min', 'max', and 'std'. Each metric can have a custom output alias. Supports filtering, sorting by an aggregated output column, and limiting the returned groups. Passing an empty 'group\_by' list produces an overall summary.
* **compare\_segments**: Compares categories of a selected dimension, such as genre, country, or company. For each category, returns a movie count and the median and mean of the requested metrics. The default metrics are revenue, profit, ROI, and score. Categories are ranked by movie count—not by financial performance—and the largest categories are returned.
* **analyze\_release\_timing**: Summarizes a selected metric across an existing release-calendar dimension, such as release month, quarter, week, day of week, or the weekend, summer, awards-season, and holiday-season flags. Returns a movie count and the chosen statistic for each group, sorted by the calendar dimension. By default, it calculates median revenue by release month. It uses the dataset’s existing calendar fields rather than deriving them.
* **analyze\_trends**: Aggregates a selected metric by year, release year, release month, or release quarter, optionally adding a second grouping dimension such as genre or country. Returns a movie count and a selected summary statistic, ordered by the time dimension. This is descriptive aggregation rather than forecasting. Grouping only by month or quarter pools those periods across years.



###### 3\. Statistical exploration

* **describe\_metrics**: Returns descriptive statistics for selected columns after optional filtering. Converts values to numeric and reports the non-missing count, mean, standard deviation, minimum, maximum, requested percentiles, and missing-value count. The default percentiles are the 25th, 50th, and 75th percentiles; values that cannot be converted to numeric are counted as missing.
* **correlation\_analysis**: Calculates Pearson, Spearman, or Kendall correlations between selected numeric columns. Without a target, returns the full correlation matrix. With a target, returns the other variables ranked by the absolute magnitude of their correlation with that target, while preserving each coefficient’s sign. It operates on the full dataset and does not accept filters. The output explicitly warns that association is not evidence of causation.
* **detect\_outliers**: Identifies unusually low or high values in a selected numeric column after optional filtering. Supports two methods: iqr that flags observations below \\(Q\_1 - 1.5\\,IQR\\) or above \\(Q\_3 + 1.5\\,IQR\\) and 'zscore' that flags observations with an absolute z-score of at least 3. Returns the thresholds, total outlier count, and selected movie records ranked by an outlier score. For IQR, that score is absolute distance from the median; for z-score, it is the absolute z-score.
* **distribution\_analysis**: Calculates histogram bin boundaries and observation counts for a numeric column, optionally producing a separate histogram for each category of another column. Supports filtering and between 2 and 100 bins. Returns histogram data rather than an image. When grouped, bin boundaries are calculated independently for each category, so they are not necessarily aligned across groups.



###### 4\. Financial performance

* **analyze\_profitability**: Summarizes financial performance for the selected movies, either overall or by category. Returns movie count, median budget, median revenue, median profit, the median of a selected metric—ROI by default—and the percentage of movies  with positive profit. Supports structured filters and additional minimum-budget and minimum-vote thresholds. The profitable percentage uses only records with a non-missing numeric profit value.
* **find\_sleeper\_hits**: Finds movies meeting caller-defined budget, ROI, revenue, and vote thresholds, then ranks them by ROI in descending order. Always requires a positive budget and a non-missing ROI. Returns identifying information and financial metrics. Despite its name, it does not impose a low-budget or high-ROI threshold unless the caller supplies one.
* **find\_box\_office\_bombs**: Finds movies with a positive budget and an ROI at or below a selected threshold, which defaults to zero. An optional minimum budget can restrict the search to larger productions. Results are sorted by profit in ascending order, placing the lowest-profit records first. Returns identifying information, budget, revenue, profit, and ROI.



###### 5\. Talent, company, genre, and country analysis

The following tools share a common aggregation routine. Their standard output includes movie count, the median and mean of the selected metric, total revenue, median ROI, and median score. Entities are ranked by the median of the selected metric.

* **analyze\_talent**: Summarizes movie-level performance by director, writer, or star. Can search for a specific person using a case-insensitive partial name match, apply filters, and require a minimum number of movies. Defaults to ranking people by median revenue with at least 3 movies. These are aggregates of associated movie records, not estimates of an individual’s causal contribution.
* **analyze\_companies**: Summarizes movie-level performance by company after optional filtering. Excludes companies below a specified minimum movie count and ranks the remaining companies by the median of the selected metric. Defaults to revenue, at least 5 movies per company, and the top 20 companies.
* **analyze\_genres**: Compares genres using the shared entity-level summary metrics. Supports inclusive release-year bounds and a minimum movie count per genre. Defaults to ranking genres by median ROI, requiring at least 10 movies per genre, and returning up to 100 genres.
* **analyze\_countries**: Compares countries using the shared entity-level summary metrics. Defaults to ranking countries by median revenue, requiring at least 10 movies per country, and returning the top 20. Unlike the talent and company tools, it does not expose a general filtering parameter.



###### 6\. Data quality and missing values

* **data\_quality\_report**: Audits the dataset for missing values, fully duplicated rows, repeated movie names, non-numeric values in expected numeric columns, zero or negative budgets and revenues, and disagreements between 'year' and 'release\_year'. Returns counts and missing-value percentages without modifying the data. The repeated-name check counts every row belonging to a duplicated title, not just the extra occurrences.
* **missing\_data\_analysis**: Reports missing-value counts and percentages for selected columns, either across the full dataset or separately by a grouping column. If no columns are specified, analyzes all columns. It measures missingness without replacing or imputing missing values and does not treat missing financial values as zero.



###### 7\. Visualization and question routing

* **create\_chart**: Creates a bar chart, line chart, scatter plot, histogram, box plot, or correlation heatmap. Supports structured filters, optional grouping through color, and optional aggregation before plotting. Returns the chart as a Base64-encoded PNG, the number of rows used, and up to 200 rows of the data supplied to the plotting code. When 'top\_n' is provided, it sorts and limits the data before plotting. Otherwise, datasets larger than 5,000 rows are reproducibly sampled down to 5,000 rows. The heatmap displays correlations between the numeric columns supplied through 'x', 'y', and 'color'; it is not a general pivot-table heatmap.
* **answer\_movie\_analysis**: Suggests analytical tools for a natural-language question using simple, case-insensitive English keyword matching. It can recommend search, ranking, comparison, trend, correlation, release-timing, or profitability tools. If no keywords match, it recommends schema discovery, filtering, and aggregation. It returns only a routing recommendation: it does not execute the suggested tools, extract their arguments, or answer the analytical question itself.

