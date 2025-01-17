# Prague Real Estate Data Scraping project

This project is a collection of scrapers that scrape real estate data from different websites.
The data is then stored in a database and used for notifying users about new listings based on their preferences.

## Data sources that are scraped

- sreality.cz
- bezrealitky.cz 
- reality.idnes.cz 

### Data sources that are planned to be scraped
- Svoboda-Williams.com
- realitymix.cz
- archer-reality.cz
- reality.bazos.cz
- reality.cz
- eurobydleni.cz
- https://www.maxima.cz/nabidka-nemovitosti/?at=1&kraj=praha
- Remax-czech.cz
- www.mmreality.cz
- https://www.engelvoelkers.com/

# Building the image for Prefect pipelines

All the pipelines are run in the same docker container, to build the image and publish it to
Docker Hub run the following commands:

```bash
docker buildx build --platform linux/amd64 -t bakoad/real-estate-pipelines:latest .
docker push bakoad/real-estate-pipelines:latest

```

# Automations

To generate a new scraper run the following command in from the data_infrastructure directory:

```bash
python automations/generate_new_scraper.py
```