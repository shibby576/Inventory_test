import streamlit as st
import pandas as pd

path = 'inventory.csv'
df = pd.read_csv(path)

#Create form to collect inputs
with st.sidebar.form(key='my_form'):
#Customer input variables
	amountdown = int(st.text_input('Amount Down ex 500',500))
	tradevalue = int(st.text_input('Trade Value ex 1000',1000))
	income = int(st.text_input('Enter gross monthly income ex 3000', 3000))
	desiredpayment = int(st.text_input('Desired payment ex 300',300))
	vehicletype = st.text_input('Enter Vehicle type (only SUV, SEDAN, TRUCK, COUPE, VERT, VAN, HATCHBACK', 'SUV')
	creditScore = int(st.text_input('Enter credit score', 650))

	submit_button = st.form_submit_button(label='Submit')
### dealer constants
docfee=int(250) #pre tax
tagfee = int(35) #post tax
projbackend = int(1500)
taxrate = float(0.08)
term=int(72)

#FUNCTIONS
#Get APR based on CS
def apr(creditScore):
    apr=.1
    if creditScore >= 0 and creditScore <= 579:
        apr =.2
        return apr
    elif creditScore >= 580 and creditScore <= 669:
        apr =.12
        return apr
    elif creditScore >= 670 and creditScore <= 739:
        apr =.07
        return apr
    elif creditScore >= 740 and creditScore<= 799:
        apr =.05
        return apr
    elif creditScore >= 800 and creditScore<= 850:
        apr =.035
        return apr
    elif creditScore is null:
        apr =.2
        return apr
    else:
        return apr
#Get Max LTV based on CS
def LTVMax(creditScore):
    ltvMax=1.25
    if creditScore >= 0 and creditScore <= 579:
        ltvMax =.85
        return ltvMax
    elif creditScore >= 580 and creditScore <= 669:
        ltvMax =1.05
        return ltvMax
    elif creditScore >= 670 and creditScore <= 739:
        ltvMax =1.15
        return ltvMax
    elif creditScore >= 740 and creditScore<= 799:
        ltvMax =1.25
        return ltvMax
    elif creditScore >= 800 and creditScore<= 850:
        ltvMax =1.25
        return ltvMax
    elif creditScore is null:
        ltvMax = .85
        return ltvMax
    else:
        ltvMax = 1
        return ltvMax

#Get Max PTI based on CS
def PTIMax(creditScore):
    PTIMax=.2
    if creditScore >= 0 and creditScore <= 579:
        PTIMax =.15
        return PTIMax
    elif creditScore >= 580 and creditScore <= 669:
        PTIMax =.15
        return PTIMax
    elif creditScore >= 670 and creditScore <= 739:
        PTIMax =.17
        return PTIMax
    elif creditScore >= 740 and creditScore<= 799:
        PTIMax =.2
        return PTIMax
    elif creditScore >= 800 and creditScore<= 850:
        PTIMax =.2
        return PTIMax
    elif creditScore is null:
        PTIMax =.15
        return PTIMax
    else:
        return PTIMax

#Get Max Price to book based on CS
def P2BMax(creditScore):
    P2BMax=1.1
    if creditScore >= 0 and creditScore <= 579:
        P2BMax =1
        return P2BMax
    elif creditScore >= 580 and creditScore <= 669:
        P2BMax =1
        return P2BMax
    elif creditScore >= 670 and creditScore <= 739:
        P2BMax =1.05
        return P2BMax
    elif creditScore >= 740 and creditScore<= 799:
        P2BMax =1.1
        return P2BMax
    elif creditScore >= 800 and creditScore<= 850:
        P2BMax =1.1
        return P2BMax
    elif creditScore is null:
        P2BMax =1
        return P2BMax
    else:
        return P2BMax

#Loan amount function
def loan_amt(price, docfee, taxrate, tradevalue,amountdown,tagfee):
	loanamt = (((price+docfee)*(1+taxrate)-(tradevalue + amountdown))+tagfee)
	return loanamt

#loan amount, WITH backend
def loan_amtbe(price, docfee, taxrate, tradevalue,amountdown,tagfee,backendspend):
    loanamtbe = (((price+docfee)*(1+taxrate)-(tradevalue + amountdown))+tagfee+backendspend)
    return loanamtbe

#LTV formula
def ltv_calc(loan,value):
	ltv=(loan/value)
	return ltv

#Payment formula
def pmt(apr,loanamt,term):
	pmt=(((apr/12)*(loanamt)))/(1-(1+(apr/12))**-term)
	return pmt

#paymebt to income ratio
def pti(payment,income):
    pti=payment/income
    return pti

#Price to book formula
def p2b(price,book):
    p2b=price/book
    return p2b

#define body types
suv = ['4D Sport Utility', '2D Sport Utility']
sedan = ['4D Sedan']
truck = ['4D Crew Cab', '4D Double Cab', 'Double Cab', '4D SuperCrew','Super Cab','4D Quad Cab','2D Standard Cab', '4D Extended Cab','King Cab','4D Access Cab','4D CrewMax']
hatchback = ['4D Hatchback','4D Wagon','2D Hatchback','5D Hatchback','3D Hatchback']
coupe = ['2D Coupe', '2D Cabriolet']
van = ['4D Passenger Van', '4D Cargo Van']
convertible = ['2D Convertible','2D Cabriolet']

# categorize each row based on body type
def classdef(body):
	style=''
	if body in suv:
		style='SUV'
		return style
	elif body in sedan:
		style='SEDAN'
		return style
	elif body in truck:
		style='TRUCK'
		return style
	elif body in hatchback:
		style='HATCHBACK'
		return style
	elif body in coupe:
		style='COUPE'
		return style
	elif body in van:
		style='VAN'
		return style
	elif body in convertible:
		style='VERT'
		return style
	else:
		style='OTHER'
		return style


st.title('Inventory search')
st.subheader('Instructions')
 #st.markdown('Adjust the values on the left then select Submit at the bottom to search for vehicles matches. The results are sorted by the customer score, which is a function of whether the vehicle type matches what as input and how far the payment is from their desired payment. Results are filtered by: - Max LTV (set on the left) - Max price to book (set on the left) - Max payment to income ratio (set on the left) - Desired customer payment, including backend and padding (set on the left) - Results are sorted by the customer score')
""" 
Adjust the values on the left then select Submit at the bottom to search for vehicles matches. The results are sorted by the payment (including backend),. Results are filtered by: 
- Max LTV (defined by CS table)
- Max price to book (defined by CS table)
- Max payment to income ratio (CS based max pmt to income ratio)
- Desired customer payment, including backend
- Vehicle type
- Results are sorted by payment
"""

#call threshold functions
apr = apr(creditScore)
ltvMax = LTVMax(creditScore)
P2BMax = P2BMax(creditScore)
PTIMax = PTIMax(creditScore)

#Form Output
if submit_button:
	#add loan amounts to dataframe
	df['loan amount'] = df.apply(lambda x: loan_amt(x['price'], docfee, taxrate, tradevalue, amountdown, tagfee), axis=1)
	#add loan amount WITH BE to dataframe
	df['loan amount BE'] = df.apply(lambda x: loan_amtbe(x['price'], docfee, taxrate, tradevalue, amountdown, tagfee,projbackend), axis=1)

#add LTV
	df['LTV'] = df.apply(lambda x: ltv_calc(x['loan amount'], x['priceGuide']), axis=1)
#add pmt
	df['Payment'] = df.apply(lambda x: pmt(apr, x['loan amount'],term), axis=1)
	#add pmt WITH BE
	df['Payment+BE'] = df.apply(lambda x: pmt(apr, x['loan amount BE'],term), axis=1)
	#add PTI
	df['PTI'] = df.apply(lambda x: pti(x['Payment'],income), axis=1)
#add classmatch
	df['Class'] = df.apply(lambda x: classdef(x['body']),axis=1)
#Add price to book to df
	df['price2book'] = df.apply(lambda x: p2b(x['price'],x['priceGuide']),axis=1)

	final_df=df.loc[(df['LTV'] <=ltvMax) & (df['price2book'] <= P2BMax) &(df['PTI']<= PTIMax) & (df['Payment+BE']<=desiredpayment) & (df['Class']<=vehicletype)].sort_values(by='Payment+BE', ascending=True)

	col1, col2= st.columns(2)
	with col1:
		st.subheader('Overall stats')
#		st.subheader('Number of vehicle options:')
#		st.text(len(final_df.index))
        st.write('Number of vehicle options: ',len(final_df.index))
        st.write('APR: ', apr)
        st.write('LTVmax ', ltvMax)
        st.write('PTI max ', PTIMax)
        st.write('P2B max ', P2BMax)
	with col2:
		st.subheader('Option stats')
#		st.text(final_df['Cust score'].mean())
#		st.write('Avg LTV: ', final_df['LTV'].mean())
		st.write('Median LTV: ', final_df['LTV'].median())
#		st.write('Min payment: ',final_df['Payment'].min())
		st.write('Max payment: ',final_df['Payment'].max())
		st.write('Max loan amount: ',final_df['loan amount'].max())
		st.write('Max vehicle price: ',final_df['price'].max())
#		st.write('Avg customer score: ',final_df['Cust score'].mean())
#		st.write('Avg dealer score: ',final_df['Dealer score'].mean())


	st.subheader('Vehicle search results')
	st.table(final_df[['year','stockNumber', 'make', 'model','odometer','Payment','Payment+BE','price2book','PTI','price', 'vin','body','priceGuide', 'cost', 'loan amount','loan amount BE','LTV','Class']])

