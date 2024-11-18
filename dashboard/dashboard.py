import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')
from babel.numbers import format_currency
import plotly.graph_objects as go

sns.set(style='dark')
st.set_page_config(page_title="Dashboard Ecommerce", page_icon=":bar_chart:", layout="wide")
st.title("Dashboard Data Ecommerce Public Dataset :bar_chart:")

# Load cleaned data
new = pd.read_csv("ecommerce.csv")
new.sort_values(by="order_purchase_timestamp", inplace=True)
new.reset_index(inplace=True)

new["order_purchase_timestamp"] = pd.to_datetime(new["order_purchase_timestamp"])
min_date = new["order_purchase_timestamp"].min()
max_date = new["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("logo.png")
    
    selected = option_menu(
        menu_title="Dashboard Ecommerce",
        options=["Home","Penjualan per Bulan","Demografi Customer by State","Rating Product"],
    )

if selected =="Home":
    col1, col2, col3=st.columns([1,2,1])
    with col2:
        st.image("data-analysis.png")
    st.write("Dashboard ecommerce ini dibuat sebagai proyek analisis data dalam course online Dicoding Belajar Analisis Data dengan Python. Pada Dashboard ini ditampilkan Penjualan pada tiap bulan dan tiap harinya. Selain itu juga menampilkan demografi pembeli berdasarakn negaranya, dan penilaian pada kategori produk.")
    st.divider()
    st.markdown(
    """
    <p style="text-align: left; color: gray; font-size: 13px;">
        Rahma Almira
    </p>
    """,
    unsafe_allow_html=True
)

if selected == "Penjualan per Bulan":
    st.subheader(':scroll: Monthly Orders')
    month=pd.read_csv("month.csv")
    month["order_purchase_timestamp"] = pd.to_datetime(month["order_purchase_timestamp"])
    month['date'] = month['order_purchase_timestamp'].dt.to_period('M').astype(str)
    df = month.groupby('date').agg({
        'payment_value':'sum',
        'order_id':'nunique'}).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        #membuat plot
        fig=go.Figure()
        # Menambahkan line untuk total pendapatan
        fig.add_trace(go.Scatter(x=df["date"], y=df['payment_value'], mode='lines+markers', name='Total Pendapatan', line=dict(color='#AE445A')))
        # Menambahkan judul dan label sumbu
        fig.update_layout(title='Trend Total Pendapatan',
                        xaxis_title='Bulan',
                        yaxis_title='Jumlah',
                        legend_title='Variabel')
        st.plotly_chart(fig)
    with col2:
        #membuat plot
        fig1=go.Figure()
        # Menambahkan line untuk total pendapatan
        fig1.add_trace(go.Scatter(x=df["date"], y=df['order_id'], mode='lines+markers', name='Total Penjualan'))
        # Menambahkan judul dan label sumbu
        fig1.update_layout(title='Trend Total Penjualan',
                        xaxis_title='Bulan',
                        yaxis_title='Jumlah',
                        legend_title='Variabel')
        st.plotly_chart(fig1)

    st.divider()

    st.subheader(":scroll: Daily Order")  
    # Mengambil start_date & end_date dari date_input
    startdate, enddate = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    filtered_df = new[(new["order_purchase_timestamp"] >= str(startdate)) & 
                    (new["order_purchase_timestamp"] <= str(enddate))]

    def create_daily_orders_df(df):
        daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
            "order_id": "nunique",
            "payment_value": "sum"
        })
        daily_orders_df = daily_orders_df.reset_index()
        daily_orders_df.rename(columns={
            "order_id": "order_count",
            "payment_value": "revenue"
        }, inplace=True)
        
        return daily_orders_df 
    daily_orders_df = create_daily_orders_df(filtered_df)
    col1, col2 = st.columns(2)
    
    with col1:
        total_orders = daily_orders_df.order_count.sum()
        st.metric("Total orders", value=total_orders)
    
    with col2:
        total_revenue = format_currency(daily_orders_df.revenue.sum(), "AUD", locale='es_CO') 
        st.metric("Total Revenue", value=total_revenue)
    
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.plot(
        daily_orders_df["order_purchase_timestamp"],
        daily_orders_df["revenue"],
        marker="o",
        markersize=3,
        color="#4B4376"
    )
    ax.tick_params(axis='y', labelsize=10)
    ax.tick_params(axis='x', labelsize=8)
    
    st.pyplot(fig) 

    st.divider()
    st.markdown(
    """
    <p style="text-align: left; color: gray; font-size: 13px;">
        Rahma Almira
    </p>
    """,
    unsafe_allow_html=True
)

if selected =="Demografi Customer by State":
    st.subheader(':earth_americas: Customers demographic by state')
    state=st.multiselect("Pick the State",new["customer_state"].unique())
    cs=new.groupby(by="customer_state")["order_id"].count().reset_index()
    state_df=cs[cs["customer_state"].isin(state)]

    fig = px.pie(state_df, values = 'order_id', names = 'customer_state', hole = 0.5)
    fig.update_traces(text = state_df["customer_state"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

    with st.expander("View Data Customer by State"):
            state = state_df.groupby(by = "customer_state", as_index = False)["order_id"].sum().sort_values(by="order_id",ascending=False).rename(columns={"customer_state": "State", "order_id": "Total Customers"})
            st.write(state.style.background_gradient(cmap="Oranges"))
            csv = state.to_csv(index = False).encode('utf-8')
            st.download_button("Download Data", data = csv, file_name = "State.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')
    
    st.divider()
    st.markdown(
    """
    <p style="text-align: left; color: gray; font-size: 13px;">
        Rahma Almira
    </p>
    """,
    unsafe_allow_html=True
)

if selected =="Rating Product":
    st.subheader(":star: Review score for Product Category")
    product=st.multiselect("Pick the Product",new["product_category_name_english"].unique())
    pr=new.groupby(by="product_category_name_english")["review_score"].mean().reset_index()
    product_df=pr[pr["product_category_name_english"].isin(product)]

    fig1 = px.bar(product_df, x = "product_category_name_english", y = "review_score", text = ['${:,.2f}'.format(x) for x in product_df["review_score"]],color_discrete_sequence=["#FF9C73"],
                    template = "seaborn")
    fig1.update_traces(text = product_df["review_score"], textposition = "outside")
    fig1.update_layout(
            xaxis_title="Product Category",
            yaxis_title="Average Rating")
    fig1.update_layout(coloraxis_colorbar_title="Rating Scale")
    st.plotly_chart(fig1,use_container_width=True)

    with st.expander("View Data Product Rating"):
            product = product_df.groupby(by = "product_category_name_english", as_index = False)["review_score"].mean().sort_values(by="review_score",ascending=False).rename(columns={"product_category_name_english": "Category", "review_score": "Average Review Score"})
            st.write(product.style.background_gradient(cmap="Oranges"))
            csv = product.to_csv(index = False).encode('utf-8')
            st.download_button("Download Data", data = csv, file_name = "Rating.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(":star: Top 5 Produk dengan Rating Terbaik")
        top_5_products = pr.nlargest(5, 'review_score')
        fig1 = px.bar(top_5_products, x = "product_category_name_english", y = "review_score", text = ['${:,.2f}'.format(x) for x in top_5_products["review_score"]],
                    color="review_score",
                    color_continuous_scale="Teal",
                    template="plotly")
        fig1.update_traces(text = top_5_products["review_score"], textposition = "outside")
        fig1.update_layout(
            xaxis_title="Product Category",
            yaxis_title="Average Rating")
        fig1.update_layout(coloraxis_colorbar_title="Rating Scale")
        st.plotly_chart(fig1,use_container_width=True)
    with col2:
        st.subheader(":star: Top 5 Produk dengan Rating Terbruk")
        bot_5_products = pr.nsmallest(5, 'review_score')
        fig2 = px.bar(bot_5_products, x = "product_category_name_english", y = "review_score", text = ['${:,.2f}'.format(x) for x in bot_5_products["review_score"]],
                    color="review_score",
                    color_continuous_scale="Greens",
                    template="plotly")
        fig2.update_traces(text = bot_5_products["review_score"], textposition = "outside")
        fig2.update_layout(
            xaxis_title="Product Category",
            yaxis_title="Average Rating")
        fig2.update_layout(coloraxis_colorbar_title="Rating Scale")
        st.plotly_chart(fig2,use_container_width=True)    
    st.divider()
    st.markdown(
    """
    <p style="text-align: left; color: gray; font-size: 13px;">
        Rahma Almira
    </p>
    """,
    unsafe_allow_html=True
)
