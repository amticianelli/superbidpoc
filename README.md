# Points of improvement
* Add parallellism using httpx instead requests
* Add AAD authentication
* Add metrics comparison
 
# Main differences
## Anthropic

* Easiest to use
* Don't need to infom a region (the API Gateway takes care of the request)

* Only 2 SDKs (Python and Typescript)
* Lacking topic discussions on the Internet

## Google Gemini

* Easy to use
* They manufactur their own chips (easier to scale) up

* Lacking topic discussions on the Internet
* System instruction not supported for vision (???)


## Microsoft Open AI

* More complex to use
* Have integrated options like "Add you own data"
* CSS of Microsoft is the best on the planet
* Extra layer of security among API the rest of environment
* Pioneer in the LLM area (together with Open AI)

# PoC Results

| Invoice | GPTVision | GPT4o | Gemini | Claude |
|:-------:|:---------:|:-----:|:------:|:------:|
| 1       |  `2nd`    | `2nd` | `4th`  | `1st`  |
| 2       |  `2nd`    | `2nd` | `4th`  | `1st`  |
| 3       |  `2nd`    | `2nd` | `1st`  | `2nd`  |
| 4       |  `3rd`    | `1st` |        | `1st`  |
| 5       |           | `1st` |        | `1st`  |
| 6       |  `2nd`    | `1st` | `2nd`  | `1st`  |


## Podium
|     | Model      |
|-----|------------|
| 1st | claude     |
| 2nd | gpt4o      |
| 3rd | gpt4vision |
| 4th | gemini     |