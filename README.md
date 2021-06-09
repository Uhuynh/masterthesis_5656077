# MASTER THESIS
# ESG Ratings and Credit Ratings: Is there an Informational Overlap?

**Submitted to:**

Prof. Loriana Pelizzon, Ph.D.  
Goethe University Frankfurt  
Chair of Law and Finance  
Frankfurt am Main

**by:**

Uyen Huynh  
s4584479@stud.uni-frankfurt.de  
M.Sc. International Management  
Summer Term 2021  

## 1. Data
Data used in the thesis (2006 - 2020) is collected from three sources:  
* Bloomberg Terminal
* Eikon DataStream (Refinitiv)
* data provided by my supervisors (Ms. Zorka and Mr. Carmelo)
### 1.1. Bloomberg Terminal
Following data is retrieved and saved under ```data/raw_data/bloomberg_raw.xlsx```:
* ESG percentile ranks from Sustainalytics and S&P Global (formerly RobecoSAM)
* S&P credit rating changes
* yearly accounting data  
### 1.2. Refinitiv
Following data is retrieved and saved under ```data/raw_data/refinitiv_raw.xlsx```:
* ESG scores from Refinitiv
### 1.3. From supervisors
Following data is received and saved under ```data/raw_data/credit_rating_supervisors.xlsx```:
* S&P credit ratings from 1980 to 2015





lib directory: contains main code snippet to clean and prepare data for running regressions

data directory: contains raw data downloaded from Bloomberg Terminal and Refinitiv Eikon Datastream
- cleaned data are under: data/cleaned_data/cleaned_data.xlsx
- regression data are under: data/cleaned_data/regression_data.xlsx
