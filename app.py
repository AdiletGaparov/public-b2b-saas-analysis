from altair.vegalite.v4.schema import channels
from pandas.core.tools.datetimes import Scalar
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from altair import datum

st.title('What should B2B SaaS startup do to grow the business?')

def load_data():
    data = pd.read_csv('B2B_SaaS_data.csv')

    data.rename(columns={
        'employees_sales_dec_2021': 'sales employees (dec 2021)', 
        'employees_sales_dec_2020': 'sales employees (dec 2020)',
        'employees_sales_growth_1y': 'YoY sales employees (%, dec)',
        'employees_engineering_dec_2021': 'engineering employees (dec 2021)', 
        'employees_engineering_dec_2020': 'engineering employees (dec 2020)',
        'employees_engineering_growth_1y': 'YoY engineering employees (%, dec)',
        'employees_total_dec_2021': 'employees (dec 2021)',
        'employees_total_dec_2020': 'employees (dec 2020)',
        'employees_bd_dec_2021': 'business dev employees (dec 2021)',
        'employees_bd_dec_2020': 'business dev employees (dec 2020)',
        'employees_bd_growth_1y': 'YoY business dev employees (%, dec)',
        'employees_support_dec_2021': 'support employees (dec 2021)',
        'employees_support_dec_2020': 'support employees (dec 2020)',
        'employees_support_growth_1y': 'YoY support employees (%, dec)',
        'linkedin_followers': 'LinkedIn followers (dec 2021)',
        'page_visits_nov_2021_thousands': 'website visits (nov 2021)',
        'bounce_rate': 'bounce rate (%, nov 2021)',
        'channel_direct': 'direct traffic (%, nov 2021)',
        'channel_search': 'search traffic (%, nov 2021)',
        'channel_social': 'social traffic (%, nov 2021)',
        'search_paid': 'paid search (%, nov 2021)',
        'social_linkedin': 'traffic from LinkedIn (%, nov 2021)'
    }, inplace=True)

    cols_to_keep = [
        'company',
        'ticker',
        'sales employees (dec 2021)', 
        'sales employees (dec 2020)',
        'YoY sales employees (%, dec)',
        'engineering employees (dec 2021)', 
        'engineering employees (dec 2020)',
        'YoY engineering employees (%, dec)',
        'employees (dec 2021)',
        'employees (dec 2020)',
        'business dev employees (dec 2021)',
        'business dev employees (dec 2020)',
        'YoY business dev employees (%, dec)',
        'support employees (dec 2021)',
        'support employees (dec 2020)',
        'YoY support employees (%, dec)',
        'LinkedIn followers (dec 2021)',
        'website visits (nov 2021)',
        'bounce rate (%, nov 2021)',
        'direct traffic (%, nov 2021)',
        'search traffic (%, nov 2021)',
        'social traffic (%, nov 2021)',
        'paid search (%, nov 2021)',
        'traffic from LinkedIn (%, nov 2021)'
    ]

    data['website visits (nov 2021)'] = data['website visits (nov 2021)'] * 1000
    data['MRR ($1M, nov 2021)'] = round(data['MRR_1K_USD_nov_2021'] / 1000)
    data['MRR ($1M, nov 2020)'] = round(data['MRR_1K_USD_nov_2020'] / 1000)
    data['YoY MRR (%, nov)'] = (data['MRR ($1M, nov 2021)'] - data['MRR ($1M, nov 2020)'])/data['MRR ($1M, nov 2020)']
    cols_to_keep.extend(['MRR ($1M, nov 2021)', 'MRR ($1M, nov 2020)', 'YoY MRR (%, nov)'])

    # get last year number of employees from growth
    for type in ['sales', 'business dev', 'support', 'engineering']:
        col_dec_2020 = f'{type} employees (dec 2020)'
        col_dec_2021 = f'{type} employees (dec 2021)'
        col_growth = f'YoY {type} employees (%, dec)'

        data[col_dec_2020] = data[col_dec_2021] / (1 + data[col_growth])
        data[col_dec_2020] = data[col_dec_2020].round()

    # customer success and related ratios
    for year in ['2020', '2021']:
        data[f'customer success employees (dec {year})'] = data[f'business dev employees (dec {year})'] + data[f'support employees (dec {year})']
        cols_to_keep.append(f'customer success employees (dec {year})')

        data[f'customer success:sales employees (dec {year})'] = data[f'customer success employees (dec {year})'] / data[f'sales employees (dec {year})']
        cols_to_keep.append(f'customer success:sales employees (dec {year})')

        data[f'sales:engineering employees (dec {year})'] =data[f'sales employees (dec {year})'] / data[f'engineering employees (dec {year})']
        cols_to_keep.append(f'sales:engineering employees (dec {year})')

        data[f'customer success:engineering employees (dec {year})'] =data[f'customer success employees (dec {year})'] / data[f'engineering employees (dec {year})']
        cols_to_keep.append(f'customer success:engineering employees (dec {year})')

    # YoY growth in customer success and ratios
    data['YoY customer success employees (%, dec)'] = (data['customer success employees (dec 2021)'] - data['customer success employees (dec 2020)']) / data['customer success employees (dec 2020)']
    cols_to_keep.extend(['YoY customer success employees (%, dec)'])
    
    # marketing
    data['paid search visits (nov 2021)'] = data['website visits (nov 2021)'] * data['search traffic (%, nov 2021)'] * data['paid search (%, nov 2021)']
    data['visits from LinkedIn (nov 2021)'] = data['website visits (nov 2021)'] * data['social traffic (%, nov 2021)'] * data['traffic from LinkedIn (%, nov 2021)']
    data['direct visits (nov 2021)'] = data['website visits (nov 2021)'] * data['direct traffic (%, nov 2021)']
    data['unbounced website visits (nov 2021)'] = data['website visits (nov 2021)'] * (1-data['bounce rate (%, nov 2021)'])
    data['organic visits (nov 2021)'] = data['direct visits (nov 2021)'] + data['website visits (nov 2021)'] * data['search traffic (%, nov 2021)'] * (1-data['paid search (%, nov 2021)'])
    cols_to_keep.extend([
        'paid search visits (nov 2021)', 
        'visits from LinkedIn (nov 2021)', 
        'organic visits (nov 2021)', 
        'unbounced website visits (nov 2021)', 
        'direct visits (nov 2021)'
    ])
    
    # additional filters
    data['growth source'] = np.where(data['sales:engineering employees (dec 2020)'] < 0.6, 'product-led growth?', 'sales-led growth?')
    data['run-rate (estimate)'] = np.where(data['MRR ($1M, nov 2021)'] > 70, '$1B+', '<$1B')
    cols_to_keep.extend(['growth source', 'run-rate (estimate)'])
    return data.loc[data['MRR ($1M, nov 2021)'] < 160, cols_to_keep] 

data = load_data()

"""
Through analysis of public **B2B SaaS companies**, I am aiming to answer the following question. 

>**What should B2B SaaS startup do to grow the business?**
> - [ ]  Hire more engineers to build new features?
> - [ ]  Spend more on marketing?
> - [ ]  Hire more salespeople?
> - [ ]  Hire more support and customer success managers to take care of existing customers?

**My hypothesis is that correct mix of employees (customer success, sales, engineering) may fuel mid-term and long-term growth of B2B SaaS startup.** 
If this hypothesis is true, then the information about current mix of employees may enhance other financial and non-financial information (`not available to general public, incl. me`) 
to make a better prediction of future revenues and help a startup to make better hiring decisions. 

---------------

##### Why do I believe this hypothesis might be true? 

This hypothesis is developed after reflecting upon my past work experience.

Before becoming **Data Scientist**, I worked 2.5 years at **Microsoft** as a Sales Engineer / Customer Success Manager, 
driving new revenue and consumption of **SaaS** products in the region of 9 countries. 

During my time there (2016-2018) MSFT stock grew from $50 to $110, 
which was driven by successful transformation into cloud leader and switch towards **subscription business model**.
Due to small size of the subsidiary, in addition to being responsible for driving usage of Office 365 cloud services and Windows 10 deployment,
I ended up helping to drive new revenue and usage of almost all subscription products in the enterprise segment. 

As a result, I learned few things about **B2B SaaS** business and how correct hiring decisions and right focus may impact the growth:

1. If you have few customers, you need to add more (quite obvious, I know).
2. If you forget about existing customers, you will limit the mid-term and long-term growth (renewal will be a challenge, upsell/cross-sell is impossible).
3. It is easier to upsell/cross-sell than to add new customer.
4. When you sell to companies, you sell to specific people inside the company. These people switch jobs and if they use and like your product and company, 
they will try to bring your product at their new job and will recommend to friends and colleagues (organic growth!).

With above and other learnings in mind and without access to confidential information (financials, product usage, customers, etc),
I believe just by looking at who work in the company, we can get few insights (more relevant to companies with **high-touch B2B SaaS model**).

--------------
##### Product-led growth vs sales-led growth? Less than $1B run-rate vs more than $1B run-rate?
"""
col_strategy_size_text, col_strategy_size_charts = st.columns(2)

with col_strategy_size_text:
    st.write(
    """
My choice fell on public B2B SaaS companies mostly because their financial performance (**MRR**) is available. 
The drawback of that choice is that their run-rate is likely higher than run-rate of a B2B SaaS startup that would be interested in **raising more money from VCs or through alternative funding**.

There are **26** B2B SaaS public companies in my dataset. Besides estimate of MRR (quarterly revenue divided by 3) in November 2021 and November 2020, I collected from **LinkedIn** information such as 
number of employees, what they do (in general terms according to **LinkedIn**), YoY change in employees count, and number of followers on **LinkedIn** (main social network for B2B sales).

With the information above, I can segment my dataset further that will help in understanding employee mix better. 

First, from the ratio of number of salespeople to engineers (`sales:engineering employees`) we can guess if the company pursues product-led growth or sales-led growth strategy (or it is just slow in hiring sales).

Second, although all these companies are public, we still can divide them by run-rate: those with run-rate of roughly $1B+ and those who didn't achieve this milestone yet. 
The bigger company will have different challenges in growing. 
    """
    )

growth_source = alt.Chart(data).mark_circle().encode(
    x=alt.X('sales:engineering employees (dec 2021)'),
    y=alt.Y('YoY MRR (%, nov)'),
    color=alt.Color('growth source', legend=alt.Legend(orient='top'), scale=alt.Scale(scheme='set1')),
    tooltip=['company', 'ticker'],
    size='MRR ($1M, nov 2021)'
)

small_big_split = alt.Chart(data).mark_circle().encode(
    x=alt.X('MRR ($1M, nov 2021)',),
    y=alt.Y('YoY MRR (%, nov)'),
    color=alt.Color('run-rate (estimate)',legend=alt.Legend(orient='top'), scale=alt.Scale(scheme='set2')),
    tooltip=['company', 'ticker'],
    size='employees (dec 2021)'
)

with col_strategy_size_charts:
    st.altair_chart(growth_source, use_container_width=True)
    st.altair_chart(small_big_split, use_container_width=True)

"""
-------------------------------------------------
##### How does revenue growth correlate with employee count growth?

For bigger companies (with $1B+ run-rate) we can see the **positive correlation between MRR growth rate and 
growth of hiring salespeople, customer success managers, and engineers.** 
There is one company in this category that seems to pursue product-led growth strategy as discussed before, 
but since this company is Cloudera (enterprise data cloud), sales-led growth strategy would fit better in my opinion.

For smaller companies, however, the picture is different.
"""

col_hiring_in_small, col_hiring_in_big = st.columns(2)

engineering_hiring_in_small = alt.Chart(data[data['run-rate (estimate)']!='$1B+']).mark_circle().encode(
    x=alt.X('YoY engineering employees (%, dec)'),
    y=alt.Y('YoY MRR (%, nov)'),
    color=alt.Color('growth source', legend=alt.Legend(orient='right'), scale=alt.Scale(scheme='set1')),
    tooltip=['company', 'ticker'],
    size=alt.Size('engineering employees (dec 2020)', legend=alt.Legend(orient='top', title='employees in engineering'))
).properties(
    height=250,
)

sales_hiring_in_small = alt.Chart(data[data['run-rate (estimate)']!='$1B+']).mark_circle().encode(
    x=alt.X('YoY sales employees (%, dec)'),
    y=alt.Y('YoY MRR (%, nov)'),
    color=alt.Color('growth source', legend=alt.Legend(orient='right'), scale=alt.Scale(scheme='set1')),
    tooltip=['company', 'ticker'],
    size=alt.Size('sales employees (dec 2020)', legend=alt.Legend(orient='top', title='employees in sales'))
).properties(
    height=250,
)
support_hiring_in_small = alt.Chart(data[data['run-rate (estimate)']!='$1B+']).mark_circle().encode(
    x=alt.X('YoY customer success employees (%, dec)'),
    y=alt.Y('YoY MRR (%, nov)'),
    color=alt.Color('growth source', legend=alt.Legend(orient='right'), scale=alt.Scale(scheme='set1')),
    tooltip=['company', 'ticker'],
    size=alt.Size('customer success employees (dec 2020)', legend=alt.Legend(orient='top', title='employees in cust success'))
).properties(
    height=250,
)

engineering_hiring_in_big = alt.Chart(data[data['run-rate (estimate)']=='$1B+']).mark_circle().encode(
    x=alt.X('YoY engineering employees (%, dec)'),
    y=alt.Y('YoY MRR (%, nov)'),
    color=alt.Color('growth source', legend=alt.Legend(orient='right'), scale=alt.Scale(scheme='set1')),
    tooltip=['company', 'ticker'],
    size=alt.Size('engineering employees (dec 2020)', legend=alt.Legend(orient='top', title='employees in engineering'))
).properties(
    height=250,
)

sales_hiring_in_big = alt.Chart(data[data['run-rate (estimate)']=='$1B+']).mark_circle().encode(
    x=alt.X('YoY sales employees (%, dec)'),
    y=alt.Y('YoY MRR (%, nov)'),
    color=alt.Color('growth source', legend=alt.Legend(orient='right'), scale=alt.Scale(scheme='set1')),
    tooltip=['company', 'ticker'],
    size=alt.Size('sales employees (dec 2020)', legend=alt.Legend(orient='top', title='employees in sales'))
).properties(
    height=250,
)

support_hiring_in_big = alt.Chart(data[data['run-rate (estimate)']=='$1B+']).mark_circle().encode(
    x=alt.X('YoY customer success employees (%, dec)'),
    y=alt.Y('YoY MRR (%, nov)'),
    color=alt.Color('growth source', legend=alt.Legend(orient='right'), scale=alt.Scale(scheme='set1')),
    tooltip=['company', 'ticker'],
    size=alt.Size('customer success employees (dec 2020)', legend=alt.Legend(orient='top', title='employees in cust success'))
).properties(
    height=250,
)

with col_hiring_in_small: 
    st.caption('Companies with less than $1B run-rate')
    st.altair_chart(engineering_hiring_in_small, use_container_width=True)
    st.caption('Companies with less than $1B run-rate')
    st.altair_chart(sales_hiring_in_small, use_container_width=True)
    st.caption('Companies with less than $1B run-rate')
    st.altair_chart(support_hiring_in_small, use_container_width=True)

with col_hiring_in_big:
    st.caption('Companies with roughly $1B+ run-rate')
    st.altair_chart(engineering_hiring_in_big, use_container_width=True)
    st.caption('Companies with roughly $1B+ run-rate')
    st.altair_chart(sales_hiring_in_big, use_container_width=True)
    st.caption('Companies with roughly $1B+ run-rate')
    st.altair_chart(support_hiring_in_big, use_container_width=True)


"""
---------------------------------
##### How does revenue growth correlate with ratio of customer success managers to salespeople?

"""

col_cust_sales_ratio_text, col_cust_sales_ratio_chart = st.columns(2)

cust_sales_ratio_in_small = alt.Chart(data[data['run-rate (estimate)']!='$1B+']).mark_circle().encode(
    x=alt.X('customer success:sales employees (dec 2020)'),
    y=alt.Y('YoY MRR (%, nov)'),
    color=alt.Color('growth source', legend=alt.Legend(orient='right'), scale=alt.Scale(scheme='set1')),
    tooltip=['company', 'ticker'],
    size='sales employees (dec 2020)',
)

with col_cust_sales_ratio_text: 
    st.write(
    """
We saw previously that simply hiring more salespeople, engineers or customer success managers/support doesn't positively correlate with MRR growth for smaller companies as opposed to those who reached mileston of $1B run-rate. 

However, what seems to be relevant at this stage of growth is the ratio of customer success managers/support to salespeople. In other words, **for each account executive who will work on bringing new customers,
a startup with high-touch SaaS model needs to have 1-2 employees who will support existing customers with deployment and usage.** 
    """
    )

with col_cust_sales_ratio_chart:
    st.caption('Companies with less than $1B run-rate')
    st.altair_chart(cust_sales_ratio_in_small, use_container_width=True)  


"""
---------------------------------------------

"""