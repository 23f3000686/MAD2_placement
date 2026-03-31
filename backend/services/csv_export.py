import pandas as pd


def export_csv(data):

    df = pd.DataFrame(data)

    df.to_csv("applications.csv")