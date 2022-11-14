### Excel file example
Formula for calculating the sum is 

`=INDIRECT(ADDRESS(ROW()-1,COLUMN())) + INDIRECT(ADDRESS(ROW(),COLUMN()-1))`.

Note: The first row should have **zero** as sum value. 

Example could be found here: https://docs.google.com/spreadsheets/d/1c-u55jqq0l26oYA130PmEJ-qiKXBP0IBCYQLh7uXbpM/edit?usp=sharing