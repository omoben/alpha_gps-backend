import pandas as pd
import plotly.express as px

# Create a simple DataFrame
df = pd.DataFrame({
    "Fruit": ["Apple", "Banana", "Cherry", "Date"],
    "Quantity": [10, 20, 30, 40]
})

# Create a simple bar chart
fig = px.bar(df, x="Fruit", y="Quantity", title="Fruit Quantity")

# Show the plot
fig.show()

