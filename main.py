import math
import streamlit as st
import pandas as pd
import plotly.express as px
from scipy.optimize import curve_fit
import plotly.graph_objects as go

#We define a function to obtain the m and b values of a linear function
def coefbringer(plot):
    results = px.get_trendline_results(plot)
    coef = results.iloc[0]["px_fit_results"].params
    print(f"Coef: {coef}")
    results = results.iloc[0]["px_fit_results"].summary()
    st.caption(f"Trendline:")
    st.latex(f" y= {coef[1]}*x + {coef[0]} ")
    return coef


#We calculate the trendline intersection with the y-axis
def ogipcalc(coeff) -> float:
    ogipc = -coeff[0] / coeff[1]
    st.subheader(f"OGIP is: {ogipc}")
    return ogipc



#We calculate the x value when Xsamaniego=1
def ogipcalcpower(coeff)-> float:
    # y = a * x ** b
    ogippower = 10**((math.log10(1)-math.log10(coeff[0]))/(coeff[1]))
    st.subheader(f"OGIP is: {ogippower}")
    return ogippower

#error calculation between OGIP given and calculated
def errcalc(ogipgiven, ogipcalculated):
    error = (ogipcalculated - ogipgiven) / ogipgiven * 100
    st.markdown(f"The difference between the OGIP given and the calculated is **:red[{error}]** %")

#P/Z Calculation and graph
def pzmethod(df):
    st.write('Remember, in this method its assumed We=0', )
    df["P/Z"] = df["Presion"] / df["Z"]
    st.table(df)
    normalgraph = px.scatter(df, x=df["Gp (x109 cf)"], y=df["P/Z"], trendline="ols",
                         trendline_color_override="aquamarine")
    st.plotly_chart(normalgraph)
    return normalgraph
#P/Z and X samaniego calculation.
def samaniegomethod(df):
    st.write('Remember, in this method its assumed We=0', )
    df["P/Z"] = df["Presion"] / df["Z"]
    df["X samaniego"] = 1-df["P/Z"]/df["P/Z"][0]

    x = df["Gp (x109 cf)"]
    y = df["X samaniego"]
    #Creation of a power trendlinw
    popt,pcov = curve_fit(lambda fx, a, b: a * fx ** b, x, y)
    df["trendpower"] = popt[0] * x ** popt[1]

    st.table(df)
    # Group data together
    graph = px.scatter(df, x=df["Gp (x109 cf)"], y=df["X samaniego"], log_x=True, log_y=True)
    trendpower= px.line(df, x=df["Gp (x109 cf)"], y=df["trendpower"], log_x=True, log_y=True, color_discrete_sequence=["red"])
    #Plotting the scatter graph and trendline
    graph2=go.Figure(data=graph.data + trendpower.data)
    st.plotly_chart(graph2)
    st.caption(f"Trendline:")
    st.latex(" y= "+str(popt[0])+"*x^{"+str(popt[1])+"}")
    return popt[0], popt[1]

def havlenaodehmethod(df):
    st.text("This program is made for Wp=0 for now")
    df["P/Z"] = df["Presion"] / df["Z"]
    df["F/Eg"] = df["Gp (x109 cf)"]/(1 - df["P/Z"] / df["P/Z"][0])
    st.table(df)
    # Group data together
    graph = px.scatter(df, x=df["Gp (x109 cf)"][1:], y=df["F/Eg"][1:])
    trend=px.scatter(df, x=df["Gp (x109 cf)"][1:4], y=df["F/Eg"][1:4], trendline="ols",
                         trendline_color_override="aqua")
    graph2 = go.Figure(data=graph.data + trend.data)
    st.plotly_chart(graph2)
    coefhyo=coefbringer(trend)
    return coefhyo

st.title("Dry Gas")

df = pd.read_csv("data/dry_gas.csv", sep=";")
print(df)

# First, we create a select box in which we will be able to select different datasets
st.text("The units of the dataframe should be psi for pressure and cf for Gp")
option = st.selectbox(
    'Which data set would ypu like to choose?',
    ('tp1', 'Upload data'))
tp1 = df
st.write('You selected:', option)
if option == "tp1":
    st.table(tp1)
    tp1["Z"].astype(float)
    tp1["Gp (x109 cf)"].astype(float)

if option == "Upload data":
    st.text("The units of the dataframe should be psi for pressure and cf for Gp")
    # Button to select a separator
    st.write("Write the separator used in your file:")
    separator = st.text_input("Write the separator used in your file:")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        # read csv
        df1 = pd.read_csv(uploaded_file, sep=separator)

st.header("OOIP, OGIP and Water entry determination")
opt2 = st.selectbox(
    'Which method would you like to use??',
    ('P/Z', 'Samaniego', "Havlena and Odeh"))

st.write('You selected:', option)
# P/Z calculation and graph
if opt2 == "P/Z":
    graphpz=pzmethod(tp1)
    coeff = coefbringer(graphpz)
    ogipc = ogipcalc(coeff)
    ogip: float = st.number_input('Select volumetric OGIP', value=823)
    errcalc(ogip, ogipc)
    linear=st.checkbox('Linear function')
    error=st.checkbox("Error<5%")
    if linear and error:
        st.write("It looks like there is no water entry, please check with Havlena and Odeh method.")
    else:
        if error:
            st.write("If not a linear function shown in the graph, then a water entry might be present")
        if linear:
            st.write('The error is too big, check Havlena and Odeh')

if opt2 == "Samaniego":
    coef=samaniegomethod(tp1)
    ogipcpower = ogipcalcpower(coef)
    ogip: float = st.number_input('Select volumetric OGIP', value=823)
    errcalc(ogip, ogipcpower)
    linear=st.checkbox('Linear function')
    error=st.checkbox("Error<5%")
    if linear and error:
        st.write("It looks like there is no water entry, please check with Havlena and Odeh method.")
    else:
        if error:
            st.write("If not a linear function shown in the graph, then a water entry might be present")
        if linear:
            st.write('The error is too big, check Havlena and Odeh')

if opt2 == "Havlena and Odeh":
    hyo=havlenaodehmethod(tp1)
    ogipc = hyo[0]
    st.subheader(f"OGIP is: {ogipc}")
    ogip: float = st.number_input('Select volumetric OGIP', value=823)
    errcalc(ogip, ogipc)
    constant=st.checkbox('constant function')
    error=st.checkbox("Error<5%")
    if constant and error:
        st.write("**It looks like there is no water entry!**")
    else:
        if error:
            st.write("If not a constant function shown in the graph, then a water entry is present")
        if constant:
            st.write('The error is too big, there must be We')


