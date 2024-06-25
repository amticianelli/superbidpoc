# Points of improvement
* Add parallellism using asyncio/httpx instead of requests
* Add AAD authentication if available
* Add metrics comparison
 
# Main differences
## Anthropic
### Perks
* Easiest to use
* Don't need to inform a region (the API Gateway takes care of the request)

### Disadvantages
* Only 2 SDKs (Python and Typescript)
* Lacking topic discussions on the Internet

## Google Gemini
### Perks
* Easy to use
* They manufactur their own chips (easier to scale) up

### Disadvantages
* Lacking topic discussions on the Internet
* System instruction not supported for vision (???)


## Microsoft Open AI
### Perks
* More material on the internet (StackOverflow, Medium and other sources)
* Have integrated options like "Add you own data"
* CSS of Microsoft is the best on the planet
* Extra layer of security among API for the rest of the environment
* Pioneer in the LLM area (together with Open AI)

### Disadvantages
* More complex to use

# PoC Results

## Data quality

| Invoice | GPT4Vision | GPT4o | Gemini | Claude |
|:-------:|:---------:|:-----:|:------:|:------:|
| 1       |  `2nd`    | `2nd` | `4th`  | `1st`  |
| 2       |  `2nd`    | `2nd` | `4th`  | `1st`  |
| 3       |  `2nd`    | `2nd` | `1st`  | `2nd`  |
| 4       |  `3rd`    | `1st` |        | `1st`  |
| 5       |           | `1st` |        | `1st`  |
| 6       |  `2nd`    | `1st` | `2nd`  | `1st`  |

## Time to process all invoices
|            |       |
|------------|-------|
| GPT4Vision | `2:12`|
|  GPT4o     | `1:49`|
|  Gemini    | `1:04`|
|  Claude    | `1:11`|


## Podium
|     | Model      |
|-----|------------|
| 1st | claude     |
| 2nd | gpt4o      |
| 3rd | gpt4vision |
| 4th | gemini     |