import pandas as pd
import arcpy

def GetSum(df,Col,ColList):
    df[Col] = df[ColList].sum(axis=1)

def GetPer(df,Col,Numerator,Denomenator):
    df.loc[df[Denomenator] == 0, Col] = 0
    df.loc[df[Denomenator] > 0, Col] = df[Numerator]/df[Denomenator]

def GetMean(df,Col):
    return df[Col].mean()

def GetStatus(df,EvalCol,OutCol,Val):
    df.loc[df[EvalCol] < Val, OutCol] = 0
    df.loc[df[EvalCol] >= Val, OutCol] = 1
    df[OutCol] = df[OutCol].astype(int)

def writeCSV(df,outName):
    df.to_csv(outName,index=True)



if __name__ == "__main__":
    #Input/Output Variables. Change as needed
    CensusTracts = r'.\TitleVI_2013_2017.gdb\CensusTractsMajorWater'
    OutGDB = r'.\Output.gdb'

    LEP_csv = r'.\ACS_17_5YR_C16001_LEP\ACS_17_5YR_C16001_with_ann.csv'
    LEP_Output = "LEPProcessed.csv"

    LowInc_csv = r'.\ACS_17_5YR_C17002_LowIncome\ACS_17_5YR_C17002_with_ann.csv'
    LowInc_Output = "LowIncProcessed.csv"

    Minority_csv = r'.\ACS_17_5YR_B03002_Minority\ACS_17_5YR_B03002_with_ann.csv'
    Minority_Output = "MinorityProcessed.csv"

    #Variables that are the same for each analysis
    TotalPop = 'HD01_VD01'

    #LEP Variables
    LEPPopCols = ['HD01_VD05','HD01_VD08','HD01_VD11','HD01_VD14','HD01_VD17','HD01_VD20','HD01_VD23','HD01_VD26','HD01_VD29','HD01_VD32','HD01_VD35','HD01_VD38']
        #Enter columns to calculate "OtherLangSpEngLessVWellPop" Column
    OtherLangCols = ['HD01_VD17','HD01_VD32','HD01_VD38']
        #Enter the values for the columns related to each variable
    LEPSpanish = 'HD01_VD05'
    TotalSpanish = 'HD01_VD03'
    LEPChinese = 'HD01_VD23'
    TotalChinese ='HD01_VD21'
    LEPVietnamese = 'HD01_VD26'
    TotalVietnamese ='HD01_VD24'
    LEPTagalog = 'HD01_VD29'
    TotalTagalog = 'HD01_VD27'
    LEPKorean = 'HD01_VD20'
    TotalKorean ='HD01_VD18'
    LEPRussian = 'HD01_VD14'
    TotalRussian = 'HD01_VD12'

        #OutputField Names - Change as Desired
    LEPPop = "LEPPop"
    LEPPer = "LEPPer"
    LEPStatus = "LEP_STATUS"
    OtherLang = "OtherLangSpEngLessVWellPop"

        #Corresponds to values above should not need to modify unless add new language
    langDict = {"LEPSpanish": {"numerator": LEPSpanish,"denomenator": TotalSpanish}, 
    'LEPChinese':{"numerator": LEPChinese,"denomenator": TotalChinese},
    'LEPVietnamese':{"numerator": LEPVietnamese,"denomenator": TotalVietnamese},
    'LEPTagalog':{"numerator": LEPTagalog,"denomenator": TotalTagalog},
    'LEPKorean':{"numerator":LEPKorean, "denomenator":TotalKorean},
    'LEPRussian':{"numerator": LEPRussian,"denomenator": TotalRussian}
    }


    #Low Income Variables
    LowIncPopCols = ['HD01_VD02','HD01_VD03','HD01_VD04','HD01_VD05','HD01_VD06','HD01_VD07']
        #Output columns change as needed
    LowIncPop = "LowIncomePop"
    LowIncPer = "LowIncomePer"
    LowIncStatus = "LowIncome_Status"


    #Minority Variables
        #TotalSum Cols
    MinorityPopCols = ['HD01_VD04','HD01_VD05','HD01_VD06','HD01_VD07','HD01_VD08','HD01_VD09','HD01_VD12']
        #Enter columns that represent Asian Pac Island Populations
    APIPopCols = ['HD01_VD06','HD01_VD07']
        #Output columns change as needed
    APIPop = "API"
    MinorityPop = "MINORITY"
    MinorityPer = "MIN_PER"
    MinorityStatus = "MIN_STATUS"







    #Minority Process
    data = pd.read_csv(Minority_csv)
    #sum Minority cols to get total Minority pop
    GetSum(data,MinorityPop,MinorityPopCols)
    #sum API cols to get total API pop
    GetSum(data,APIPop,APIPopCols)

    #if total pop is 0, will get error when calculating Low income percentage so use conditional
    GetPer(data,MinorityPer,MinorityPop,TotalPop)

    #Threshold is the average percentage of LEP population in the study area
    Threshold = float(data[MinorityPop].sum())/float(data[TotalPop].sum())
    print "Minority Threshold is %f" % (Threshold)

    #Calculate MinorityStatus
    GetStatus(data,MinorityPer,MinorityStatus,Threshold)

    #write data frame to new CSV
    writeCSV(data,Minority_Output)

    #LEP Process
    data = pd.read_csv(LEP_csv)

    #Get total LEP pop column
    GetSum(data,LEPPop,LEPPopCols)
    #Get OtherLang column
    GetSum(data,OtherLang,OtherLangCols)

    #parse through lang dict and create new column based on LEP population
    for language in langDict:
        langField = langDict[language]
        LEPLang = langDict[language]['numerator']
        TotalLang = langDict[language]['denomenator']
        #if total pop is 0, will get error when calculating language field so use conditional
        GetPer(data,language,LEPLang,TotalLang)

    #if total pop is 0, will get error when calculating LEPPer so use conditional
    GetPer(data,LEPPer,LEPPop,TotalPop)

    #Threshold is the average percentage of LEP population in the study area
    # Threshold = GetMean(data,LEPPop)/GetMean(data,TotalPop)
    # print  "LEP Threshold is %d" % (Threshold) 
    Threshold = float(data[LEPPop].sum())/float(data[TotalPop].sum())
    print "LEP Threshold is %f" % (Threshold)

    #Calculate LEPStatus
    GetStatus(data,LEPPer,LEPStatus,Threshold)

    writeCSV(data, LEP_Output)



    #Low Income Process
    data = pd.read_csv(LowInc_csv)
    #sum low income cols to get total low inc pop
    GetSum(data,LowIncPop,LowIncPopCols)


    #if total pop is 0, will get error when calculating Low income percentage so use conditional
    GetPer(data,LowIncPer,LowIncPop,TotalPop)

    #Threshold is the average percentage of LEP population in the study area
    Threshold = float(data[LowIncPop].sum())/float(data[TotalPop].sum())
    print "LowIncome Threshold is %f" % (Threshold)

    #Calculate LowIncomeStatus
    GetStatus(data,LowIncPer,LowIncStatus,Threshold)

    #write data frame to new CSV
    writeCSV(data,LowInc_Output)



    #Create GIS
    arcpy.env.workspace = OutGDB
    arcpy.env.overwriteOutput = True
    #disable qualified field names otherwise join will create long names
    arcpy.env.qualifiedFieldNames = False
    ds_List = {"Minority": Minority_Output, "LowInc": LowInc_Output, "LEP": LEP_Output}

    for ds in ds_List:
        print "working on %s" % (ds)
        tableOut = ds + "processed"
        featureLayer = ds + "fl"
        arcpy.TableToTable_conversion(ds_List[ds],OutGDB,tableOut)
        arcpy.MakeFeatureLayer_management(CensusTracts,featureLayer)
        arcpy.AddJoin_management(featureLayer,"GeoID2",tableOut,"id2","KEEP_COMMON")
        arcpy.CopyFeatures_management(featureLayer,ds)




