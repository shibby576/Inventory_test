import streamlit as st
import pandas as pd

path = 'inventory.csv'
df = pd.read_csv(path)

#Create form to collect inputs
with st.sidebar.form(key='my_form'):
#Customer input variables
	amountdown = int(st.text_input('Amount Down ex 500',500))
	tradevalue = int(st.text_input('Trade Value ex 1000',1000))
	taxrate = float(st.text_input('Tax rate ex 0.07',0.07))
#Creditscore = 0
	interestrate = float(st.text_input('Enter APR ex 0.12',0.12))
	income = int(st.text_input('Enter gross monthly income ex 3000', 3000))
	desiredpayment = int(st.text_input('Desired payment ex 300',300))
	vehicletype = st.text_input('Enter Vehicle type (only SUV, SEDAN, TRUCK, COUPE, VERT, VAN, HATCHBACK', 'SUV')
	term=int(st.text_input('Enter term ex 72',72))

#Dealer input veriables
	docfee=int(st.text_input('Enter Doc Fee ex 250',250)) #pre tax
	tagfee = int(st.text_input('Enter Tag fee ex 35',35)) #post tax
	ptiMax = float(st.text_input('Enter max pmt to income ex 0.3', 0.3))
	p2bMax = float(st.text_input('Enter price to book max ex 1.05', 1.05))
	LTVMax = float(st.text_input('Enter LTV Max ex 1.05',1.1))
#	grossMin = int(st.text_input('Enter Gross min ex 500',500))
#	desiredGross = int(st.text_input('Enter desired gross ex 2500',2500))
#	desiredLTV = float(st.text_input('Desired LTV ex 1.05',1.05))
	pmtVar = float(st.text_input('Enter payment variance ex 0.25',0.25))
	projbackend = int(st.text_input('Enter projected backend ex 1000',1000))
	projintspread = float(st.text_input('Enter projected int spread ex 0.02',.02))
	projbankfee = int(st.text_input('Enter bank fee ex -500',-500))

	submit_button = st.form_submit_button(label='Submit')

#FUNCTIONS
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

#gross function
def gross(price,cost,projbackend,projbankfee,loan_amt,projintspread):
	gross = (price-cost)+projbackend+projbankfee+(loan_amt*projintspread)
	return gross

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


#SCORING
#customer scoring
pmtWeight = 5
typeMatchWeight = 2


#class match score
def classmatch(body,vehicletype):
	typeMatchscore_yes = 1
	typeMatchscore_no = .5
	if body==vehicletype:
		class_match=typeMatchscore_yes
	else:
		class_match=typeMatchscore_no
		
	return class_match

#Customer score
def cust_score(desiredpayment,pmt,pmtWeight,typeMatchWeight,classmatch):
	cust_score = (((desiredpayment/pmt)*pmtWeight)+(typeMatchWeight*classmatch))/(pmtWeight+typeMatchWeight)
	return cust_score

st.title('Inventory search')
st.subheader('Instructions')
st.markdown('Adjust the values on the left then select Submit at the bottom to search for vehicles matches. The results are sorted by the customer score, which is a function of whether the vehicle type matches what as input and how far the payment is from their desired payment. Results are filtered by: - Max LTV (set on the left) - Max price to book (set on the left) - Max payment to income ratio (set on the left) - Desired customer payment, including backend and padding (set on the left) - Results are sorted by the customer score')
#st.subheader('Formulas')
#st.write('Customer score formula: ',' = (((desiredpayment/pmt)*pmtWeight)+(typeMatchWeight*classmatch))/(pmtWeight+typeMatchWeight)')
#st.write('Customer score weights: pmtWeight = 5 typeMatchWeight = 2')
#st.write('Loan amount: ', '(((price+docfee)*(1+taxrate)-(tradevalue + amountdown))+tagfee)')
#st.write('Payment: ','(((apr/12)*(loanamt)))/(1-(1+(apr/12))**-term)')

#Form Output
if submit_button:
	#add loan amounts to dataframe
	df['loan amount'] = df.apply(lambda x: loan_amt(x['price'], docfee, taxrate, tradevalue, amountdown, tagfee), axis=1)
	#add loan amount WITH BE to dataframe
	df['loan amount BE'] = df.apply(lambda x: loan_amtbe(x['price'], docfee, taxrate, tradevalue, amountdown, tagfee,projbackend), axis=1)

#add LTV
	df['LTV'] = df.apply(lambda x: ltv_calc(x['loan amount'], x['priceGuide']), axis=1)
#add pmt
	df['Payment'] = df.apply(lambda x: pmt(interestrate, x['loan amount'],term), axis=1)
	#add pmt WITH BE
	df['Payment+BE'] = df.apply(lambda x: pmt(interestrate, x['loan amount BE'],term), axis=1)
	#add PTI
	df['PTI'] = df.apply(lambda x: pti(x['Payment'],income), axis=1)
#add gross
	df['Gross'] = df.apply(lambda x: gross(x['price'], x['cost'],projbackend,projbankfee,x['loan amount'],projintspread), axis=1)
#add classmatch
	df['Class'] = df.apply(lambda x: classdef(x['body']),axis=1)
#Add class match score to df
	df['Class Match'] = df.apply(lambda x: classmatch(x['Class'],vehicletype),axis=1)
#Add customer score to df
	df['Cust score'] = df.apply(lambda x: cust_score(desiredpayment,x['Payment'],pmtWeight,typeMatchWeight,x['Class Match']),axis=1)
#Add price to book to df
	df['price2book'] = df.apply(lambda x: p2b(x['price'],x['priceGuide']),axis=1)

	final_df=df.loc[(df['LTV'] <=LTVMax) & (df['price2book'] <= p2bMax) &(df['PTI']<= ptiMax) & (df['Payment+BE']<=(desiredpayment*(1+pmtVar)))].sort_values(by='Cust score', ascending=False)

	col1, col2= st.columns(2)
	with col1:
		st.subheader('Overall stats')
#		st.subheader('Number of vehicle options:')
#		st.text(len(final_df.index))
		st.write('Number of vehicle options: ',len(final_df.index))
		st.write('Percent of desired type: ',(len(final_df[(final_df['Class Match']>.5)])/len(final_df.index)))
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
	st.table(final_df[['year','stockNumber', 'make', 'model','odometer','Payment','Payment+BE','price2book','PTI','price', 'vin','body','priceGuide', 'cost', 'loan amount','loan amount BE','LTV', 'Gross','Class','Class Match', 'Cust score',]])

