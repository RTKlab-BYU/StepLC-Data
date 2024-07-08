import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# BASELINE_TOLERANCE = 0 # 20 min
# BASELINE_TOLERANCE = 0.5 # 10 min
BASELINE_TOLERANCE = 3 #30 min
MIN_Gradient_SIZE = 75
CONCENTRATIONS = [0,2,5,15,25,80]
# ABSORBANCES = [-1.11,2.61,3.5,7.67,19.07,54.5] # 20 min
# ABSORBANCES = [-0.05,0.9,2.76,11.2,20.2,56.5] # 30 min
ABSORBANCES = [0.5,1.2,2.2,11.7,16.4,50]
# ABSORBANCES = [-0.22,1.11,3.33,8.64,20.04,55.44] # 10 min

# DATA_FILE = "20min_pub.txt" #20 min
# OUTPUT_FILENAME = "20min" #20 min

# DATA_FILE = "10min_pub.txt" # 10 min
# OUTPUT_FILENAME = "10min" # 10 min

# DATA_FILE = "first2_days.txt" # 30 min
# OUTPUT_FILENAME = "25nLmin_20rep" # 30 min

DATA_FILE = "final_25nLmin.txt" # 30 min
OUTPUT_FILENAME = "25nLmin_45rep" # 30 min

# DATA_FILE = "final_25nLmin.txt" # 30 min
# OUTPUT_FILENAME = "25nLmin_10rep" # 30 min

# FIRST_Gradient_TO_INCLUDE = 18 #20 min
# LAST_Gradient_TO_INCLUDE = 27 #20min

# FIRST_Gradient_TO_INCLUDE = 7 #30 min
# LAST_Gradient_TO_INCLUDE = 26 #30 min

FIRST_Gradient_TO_INCLUDE = 7 #30 min
LAST_Gradient_TO_INCLUDE = 51 #30 min

# FIRST_Gradient_TO_INCLUDE = 7 #30 min
# LAST_Gradient_TO_INCLUDE = 16 #30 min

# FIRST_Gradient_TO_INCLUDE = 19 #10 min
# LAST_Gradient_TO_INCLUDE = 28 #10min

# TIME_ADJUST = 15.5 #20min
# TIME_ADJUST = 11 #10min
TIME_ADJUST = 70 #30min

#print statements
BREAKS = [1,2,5,8,15,20,25,45,75,77]
FIRST_BREAK_MIN_TIME = 0.5

# Desired Separation
# %B start duration
# 1     1
# 2     5
# 8     7.5
# 15    4.5
# 20    3
# 25    10
# 45    5
# 80    5
# 90    5
# 1     25
# 1     done


def convert_to_concentration(signal):
    i = 1
    while i < len(CONCENTRATIONS):
        x1 = ABSORBANCES[i-1]
        x2 = ABSORBANCES[i]

        y1 = CONCENTRATIONS[i-1]
        y2 = CONCENTRATIONS[i]

        if signal < x2 or i == len(CONCENTRATIONS) -1:
            m = (y2-y1)/(x2-x1)
            b = y2 - m*x2
            new = m * signal + b
            return new
            
        i = i + 1
    return None

def check_for_break(pB, break_index, time):
    if break_index < len(BREAKS):
        if pB > BREAKS[break_index] and time > FIRST_BREAK_MIN_TIME:
            print(str(pB) +"%:\t"+str(time)+" min")
            return True
    return False

df = pd.read_csv(DATA_FILE,sep=";",skiprows=18)

fig = go.Figure()
fig.update_layout(template = "simple_white")

current = pd.DataFrame()
Gradient_found = False
Gradient_start = TIME_ADJUST
break_number = 0
i = 1
j = 1
for index, row in df.iterrows():
    current_time = row["Time [min]"] 
    time_elapsed = current_time - Gradient_start
    signal = row["Absorbance [mAU]"]
    if signal <= BASELINE_TOLERANCE and not Gradient_found:
        #Gradient too low to be started
        current = pd.concat([current,pd.DataFrame(data={"Time (min)":[time_elapsed],"% Organic":[convert_to_concentration(signal)]})])
        percent = convert_to_concentration(signal)
        if check_for_break(percent, break_number, time_elapsed):
            break_number = break_number + 1
    elif signal > BASELINE_TOLERANCE and not Gradient_found:
        #Gradient found
        current = pd.concat([current,pd.DataFrame(data={"Time (min)":[time_elapsed],"% Organic":[convert_to_concentration(signal)]})])
        Gradient_found = True
        percent = convert_to_concentration(signal)
        print(str(i) + " Gradient_found")
        print(row)
        if check_for_break(percent, break_number, time_elapsed):
            break_number = break_number + 1
    elif Gradient_found and time_elapsed < MIN_Gradient_SIZE:
        #Gradient to thin to be done
        percent = convert_to_concentration(signal)
        current = pd.concat([current,pd.DataFrame(data={"Time (min)":[time_elapsed],"% Organic":[percent]})])
        if check_for_break(percent, break_number, time_elapsed):
            break_number = break_number + 1
    elif Gradient_found and time_elapsed >= MIN_Gradient_SIZE and signal > BASELINE_TOLERANCE:
        #Gradient too high to be done
        percent = convert_to_concentration(signal)
        current = pd.concat([current,pd.DataFrame(data={"Time (min)":[time_elapsed],
                                                        "% Organic":[percent]})])
        if check_for_break(percent, break_number, time_elapsed):
            break_number = break_number + 1
    elif Gradient_found and time_elapsed >= MIN_Gradient_SIZE and signal < BASELINE_TOLERANCE:
        #Gradient finished
        current = pd.concat([current,pd.DataFrame(data={"Time (min)":[time_elapsed],
                                                        "% Organic":[convert_to_concentration(signal)]})])
        # fig = px.scatter(current, x="Time (min)",y="% Organic")
        # fig.show()
        
        if i == FIRST_Gradient_TO_INCLUDE:
            current = current.rename(columns={"% Organic": "Gradient "+str(j)})
            # all = current
            include = True
        elif i >= FIRST_Gradient_TO_INCLUDE and i <= LAST_Gradient_TO_INCLUDE:
            current = current.rename(columns={"% Organic": "Gradient "+str(j)})
            # all = pd.merge(all,current,how="outer")
            # print(all)
            include = True
        elif i > LAST_Gradient_TO_INCLUDE:
            include = False
            break
        else: 
            include = False
        if include:
            # red = 194-j*1 #10min
            green = 194-j*1
            # blue = 255-j*1 #20min
            # green = j*1/2
            blue = 10 + j*1 #10min
            red = 10 + j*1 #10min
            fig.add_trace(go.Scatter(x=current["Time (min)"], y=current["Gradient "+str(j)],
                    mode='lines',
                    line=dict(
                        color=f'rgba({red}, {green}, {blue}, 0.75)'),
                    name="Gradient"+str(j)))
            j = j + 1
            axis_max = max(current["Time (min)"])
            fig.update_xaxes(range = [0,axis_max])
            fig.show()
        
        Gradient_found = False
        current = pd.DataFrame()
        Gradient_start = current_time + TIME_ADJUST
        break_number = 0
        i = i + 1
        
    else:
        print("ERROR")
        print(row)
if i == FIRST_Gradient_TO_INCLUDE:
    current = current.rename(columns={"% Organic": "Gradient "+str(j)})
    # all = current
    j = 1
    include = True
elif i >= FIRST_Gradient_TO_INCLUDE and i <= LAST_Gradient_TO_INCLUDE:
    current = current.rename(columns={"% Organic": "Gradient "+str(j)})
    # all = pd.merge(all,current,how="outer")
    # print(all)
    include = True
elif i > LAST_Gradient_TO_INCLUDE:
    include = False
    pass
else: 
    include = False
if include:
    # red = 194-j*1 #10min
    green = 194-j*1
    # blue = 255-j*1 #20min
    # green = j*1/2
    blue = 10 + j*1 #10min
    red = 10 + j*1 #10min
    fig.add_trace(go.Scatter(x=current["Time (min)"], y=current["Gradient "+str(j)],
            mode='lines',
            line=dict(
                color=f'rgba({red}, {green}, {blue}, 0.75)'),
            name="Gradient "+str(j)))
    axis_max = max(current["Time (min)"])
    fig.update_xaxes(range = [0,axis_max])
    fig.show()
fig.update_layout(template = "simple_white", font=dict(family="Arial Black",size=32),showlegend=False,
                  xaxis_title=dict(text='Time (min)'),
                  yaxis_title=dict(text='%B'),
                  yaxis=dict(showline=True, linewidth=3, linecolor='black'),
                  xaxis=dict(showline=True, linewidth=3, linecolor='black'))
fig.update_xaxes(range = [0,axis_max])

fig.write_image("images/"+OUTPUT_FILENAME+".png",format="png",
 scale=10, width = 1000, height=800,
                 engine = "kaleido") 
fig.show()

# all.to_excel(OUTPUT_FILENAME+".xlsx")
