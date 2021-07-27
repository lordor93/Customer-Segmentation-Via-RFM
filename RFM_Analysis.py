
###############################################
# RFM ANALYZE PROJECT
###############################################
import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)


def retail_data_prep(dataframe):
    dataframe.dropna(inplace=True)
    # Omitting Repayments containing negative values in UnitPrice
    dataframe = dataframe[~dataframe["Invoice"].str.contains("C", na=False)]
    dataframe = dataframe[dataframe["Quantity"] > 0]
    dataframe = dataframe[dataframe["Price"] > 0]
    return dataframe

#df_ = pd.read_excel("Week3/online_retail_II", sheet_name = "Year 2010-2011")
#df_.to_pickle("online_retail_II_2010-2011.pkl")
df =  pd.read_pickle("online_retail_II_2010-2011.pkl")
df.head()

df.shape
df.describe().T


# Data Preprocessing

df = retail_data_prep(df)
df.groupby("StockCode").agg({"Quantity":"sum"}).sort_values("Quantity",ascending= False).head()

# Total Price requires for Monetary value
df["TotalPrice"] = df["Quantity"] * df["Price"]
df.head()

# Creation of RFM Metrics

# Recency (yenilik): Müşterinin son satın almasından bugüne kadar geçen süre
# Frequency (Sıklık): Toplam satın alma sayısı.
# Monetary (Parasal Değer): Müşterinin yaptığı toplam harcama.
df.head()
df["InvoiceDate"].max()
today_date = dt.datetime(2011,12,11)
rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda date: (today_date - date.max()).days,
                                    "Invoice": lambda num: num.nunique(),
                                    "TotalPrice": lambda TotalPrice: TotalPrice.sum()})
rfm.head()

rfm.columns = ["Recency","Frequency","Monetary"]
rfm.describe().T
rfm = rfm[rfm["Monetary"] > 0]
rfm.describe().T

# RFM Scores
rfm["recency_score"] = pd.qcut(rfm["Recency"],5, labels=[5, 4, 3, 2, 1])

rfm["frequency_score"] = pd.qcut(rfm['Frequency'].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])

rfm["monetary_score"] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5])

rfm["RFM_SCORE"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str))

rfm.head()



# RFM Segmentations(Clusters)
seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

rfm['segment'] = rfm['RFM_SCORE'].replace(seg_map, regex=True)
rfm.head()



rfm[["segment", "Recency", "Frequency", "Monetary"]].groupby("segment").agg(["mean", "count"])
#rfm.to_csv("RFM.csv")

# Actions
####  Can't Loose Them Segmenti ####
'''
* Recency degerleri ortalama 133 gündür ve 63 kisi vardır.
*  Ortalama frequency degerleri  8 dir.  Ortalama Monetary degerleri yaklasık 2796 birim paradır. Bu yüksek bir değerdir. 
* Bu kisilerin riskli gruba düsmelerini engellemek icin Sms yada e-mail kampanyalar bu kişilere gönderilebilinir.

'''

####  At Risk Segmenti ####
'''
* Bu grub riskli müsterileri icermektedir. Islem yapılmazsa bunlar churn olabilirler.
* Ortalama recency degerleri yaklasık 154 gündür. 
* Ortalama Frequency degerleridee yaklasık 3tür. Ortalama monetary de 1085 birimdir.
* Bunlari geri kazanmak icin tesvik edici kampanyalar yapılabilinir.
* Yada kendimizi hatirlaticak, bizi unuttun mu yada özlendin tarzi e-mailler gönderilebilinir.

'''
####  Loyal Customers  Segmenti ####
'''
* Sadık müsterilerdir. Recency ortalamaları yaklasık 34 gündür. Ortalama Monetary degerleri yaklasık  2864 birimdir.
* Ortalama frequency degerleri yaklasık 6.5 dur.
* Sadık müsterileri ödüllendirmemiz gerekebilir. Bu müsterilere özel indirim kuponları verilebilniir. Örnegin 200tl harcamada da 40 tl indirim gibi.

'''
rfm = pd.read_csv("RFM.csv")




# LoyalCustomers segmentindeki müsterilerin csv file a yazılması
dff = pd.DataFrame()
dff["LoyalCustomers"] = rfm[rfm["segment"] == "loyal_customers"].index
dff.head()

dff.to_csv("LoyalCustomers.csv")
