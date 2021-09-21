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
	income = 0
	desiredpayment = int(st.text_input('Desired payment ex 300',300))
	vehicletype = st.text_input('Enter Vehicle type (only SUV, SEDAN, TRUCK, COUPE, VERT, VAN, HATCHBACK', 'SUV')
	term=int(st.text_input('Enter term ex 72',72))

#Dealer input veriables
	docfee=int(st.text_input('Enter Doc Fee',250)) #pre tax
	tagfee = int(st.text_input('Enter Tag fee',35)) #post tax
	projbackend = int(st.text_input('Enter projected backend',1000))
	projintspread = float(st.text_input('Enter projected int spread',.02))
	projbankfee = int(st.text_input('Enter bank fee',-500))
	LTVMax = float(st.text_input('Enter LTV Max',1.1))
	grossMin = int(st.text_input('Enter Gross min',0))
	desiredGross = int(st.text_input('Enter desired gross',2500))
	desiredLTV = float(st.text_input('Desired LTV',1.05))
	pmtVar = float(st.text_input('Enter payment variance',0.25))

	submit_button = st.form_submit_button(label='Submit')

#FUNCTIONS
#Loan amount function
def loan_amt(price, docfee, taxrate, tradevalue,amountdown,tagfee):
	loanamt = (((price+docfee)*(1+taxrate)-(tradevalue + amountdown))+tagfee)
	return loanamt

#LTV formula
def ltv_calc(loan,value):
	ltv=(loan/value)
	return ltv

#Payment formula
def pmt(apr,loanamt,term):
	pmt=(((apr/12)*(loanamt)))/(1-(1+(apr/12))**-term)
	return pmt

#gross function
def gross(price,cost,projbackend,projbankfee,loan_amt,projintspread):
	gross = (price-cost)+projbackend+projbankfee+(loan_amt*projintspread)
	return gross

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

#dealer scoring
grossWeight = 1
LTVweight = .5

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

#Gross score
def gross_score(gross,desiredGross):
	gross_score = gross/desiredGross
	return gross_score

#LTV score
def ltv_score(LTVMax,ltv):
	score = LTVMax/ltv
	return score

# dealer score
def dealer_score(grossScore,grossWeight,LTVweight,LTVscore):
	score = (((grossScore*grossWeight)+(LTVweight*LTVscore))/grossWeight+LTVscore)
	return score

#total score
def total_score(desiredpayment,payment,pmtWeight,typeMatchWeight,Classmatch,GrossScore,grossWeight,LTVweight,LTVscore):
	score = (((desiredpayment/payment)*pmtWeight)+(typeMatchWeight*Classmatch)+(GrossScore*grossWeight)+(LTVweight*LTVscore))/((pmtWeight+typeMatchWeight)+(grossWeight+LTVweight))
	return score

#Form Output
if submit_button:
	#add loan amounts to dataframe
	df['loan amount'] = df.apply(lambda x: loan_amt(x['price'], docfee, taxrate, tradevalue, amountdown, tagfee), axis=1)
#add LTV
	df['LTV'] = df.apply(lambda x: ltv_calc(x['loan amount'], x['priceGuide']), axis=1)
#add pmt
	df['Payment'] = df.apply(lambda x: pmt(interestrate, x['loan amount'],term), axis=1)
#add gross
	df['Gross'] = df.apply(lambda x: gross(x['price'], x['cost'],projbackend,projbankfee,x['loan amount'],projintspread), axis=1)
#add classmatch
	df['Class'] = df.apply(lambda x: classdef(x['body']),axis=1)
#Add class match score to df
	df['Class Match'] = df.apply(lambda x: classmatch(x['Class'],vehicletype),axis=1)
#Add customer score to df
	df['Cust score'] = df.apply(lambda x: cust_score(desiredpayment,x['Payment'],pmtWeight,typeMatchWeight,x['Class Match']),axis=1)
#Add gross score
	df['Gross score'] = df.apply(lambda x: gross_score(x['Gross'],desiredGross),axis=1)
#Add LTV score
	df['LTV score'] = df.apply(lambda x: ltv_score(LTVMax,x['LTV']),axis=1)
#Add dealer score
	df['Dealer score'] = df.apply(lambda x: dealer_score(x['Gross score'],grossWeight,LTVweight,x['LTV score']),axis=1)
#Add total score
	df['Total score'] = df.apply(lambda x: total_score(desiredpayment,x['Payment'],pmtWeight,typeMatchWeight,x['Class Match'],x['Gross score'],grossWeight,LTVweight,x['LTV score']),axis=1)
	final_df=df.loc[(df['Payment'] <=(desiredpayment*(1+pmtVar))) & (df['Gross'] >= grossMin) & (df['LTV'] < LTVMax)].sort_values(by='Cust score', ascending=False)
    
    st.title('Inventory search')
    col1, col2 = st.columns(2)
    with col1:
		st.subheader('Number of vehicle options:')
		st.text(len(final_df.index))
	with col2:
		st.subheader('column 2')
	st.subheader('Vehicle search results')
	st.table(final_df[['year', 'make', 'model', 'vin','body','price','priceGuide', 'cost', 'loan amount','LTV', 'Payment','Gross','Class','Class Match', 'Cust score','Gross score','LTV score','Dealer score', 'Total score']])

